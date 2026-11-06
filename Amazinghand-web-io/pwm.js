/* Amazinghand-web-io —— PWM 舵机（ESP32-S3 直驱）后端
 *
 * 与 io.js（SCS0009 总线）暴露完全相同的接口：
 *   window.AH_PWM = { init({onMessage}), send(msg), isConnected(), supportsSerial(), _protocol }
 *
 * 串口：115200 8N1，协议：
 *   命令帧  AA CMD LEN DATA... CKSUM   （CKSUM = CMD ^ LEN ^ DATA...）
 *   响应帧  BB CMD STATUS CKSUM        （CKSUM = CMD ^ STATUS）
 *
 * 网页只使用 0xF0 直驱（8 字节绝对角度）、0xF1 选左右手、0xFF 停止、0x00 NOP。
 * 固件没有“松开力矩”命令，因此 capabilities.torque = false。
 */
(function () {
  "use strict";

  const C = window.AH_COMMON;

  /* ---------------- 协议常量 ---------------- */
  const PWM = {
    baudRate: 115200,
    header: 0xaa,
    respHeader: 0xbb,
    nop: 0x00,
    direct: 0xf0,
    setSide: 0xf1,
    stop: 0xff,
    minWriteIntervalMs: 30,
    status: {
      0x00: "OK",
      0x01: "无效命令",
      0x02: "参数错误",
      0x03: "忙（手势执行中）",
      0x10: "完成",
    },
  };

  /* ---------------- 状态 ---------------- */
  let cfg = null;
  let hands = {};
  let enabled = [];
  let current = {};
  let target = "right";
  let torqueOn = {};

  let serialPort = null;
  let writer = null;
  let reader = null;
  let readerTask = null;
  let portName = "";
  const knownPorts = new Map();

  let dryRun = false;
  let emit = () => {};

  let rxBuf = [];
  let waiters = [];
  let lastSendAt = 0;
  let pendingAngles = null;
  let sendTimer = null;
  let lastErrorAt = 0;
  let closing = false;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  /* ---------------- 协议帧 ---------------- */

  function checksum(cmd, data) {
    let cs = cmd ^ data.length;
    for (const b of data) cs ^= b;
    return cs & 0xff;
  }

  function buildFrame(cmd, data) {
    const payload = Array.from(data || []);
    return Uint8Array.from([PWM.header, cmd, payload.length, ...payload,
                            checksum(cmd, payload)]);
  }

  function notifyResponse(cmd, status) {
    for (const w of [...waiters]) {
      if (w.cmd === null || w.cmd === cmd) {
        clearTimeout(w.timer);
        waiters = waiters.filter((x) => x !== w);
        w.resolve({ cmd, status });
      }
    }
  }

  function waitResponse(cmd, timeoutMs) {
    return new Promise((resolve, reject) => {
      const w = { cmd, resolve, reject, timer: null };
      w.timer = setTimeout(() => {
        waiters = waiters.filter((x) => x !== w);
        reject(new Error("timeout"));
      }, timeoutMs);
      waiters.push(w);
    });
  }

  function onRxBytes(bytes) {
    for (const b of bytes) rxBuf.push(b);
    // 防止固件启动日志等噪声无限累积
    if (rxBuf.length > 256) rxBuf = rxBuf.slice(-256);

    for (;;) {
      const i = rxBuf.indexOf(PWM.respHeader);
      if (i < 0) {
        // 没有响应头，只保留最后一个字节（可能正好是半个头？0xBB 是单字节，无需保留）
        rxBuf = [];
        break;
      }
      if (rxBuf.length - i < 4) break;      // 等剩余 3 字节
      const frame = rxBuf.slice(i, i + 4);
      rxBuf = rxBuf.slice(i + 4);
      const [, cmd, status, cs] = frame;
      if ((cmd ^ status) !== cs) continue;  // 校验失败，继续找下一个 0xBB
      notifyResponse(cmd, status);
      if (status === 0x01 || status === 0x02 || status === 0x03) {
        const now = Date.now();
        if (now - lastErrorAt > 500) {      // 连续拖动时不要刷屏
          lastErrorAt = now;
          emit({ type: "error", msg: `PWM 舵机：${PWM.status[status] || "错误 0x" + status.toString(16)}` });
        }
      }
    }
  }

  async function readLoop() {
    if (!serialPort || !serialPort.readable) return;
    const rd = serialPort.readable.getReader();
    reader = rd;
    try {
      for (;;) {
        const { value, done } = await rd.read();
        if (done) break;
        if (value && value.length) onRxBytes(value);
      }
    } catch (e) {
      // 主动断开时 read 会抛 AbortError，属于正常流程
      if (!closing && serialPort) emit({ type: "error", msg: `串口读取失败：${e.message || e}` });
    } finally {
      try { rd.releaseLock(); } catch (_) { /* ignore */ }
      if (reader === rd) reader = null;
    }
  }

  async function writeFrame(cmd, data) {
    if (!writer) throw new Error("串口未连接");
    await writer.write(buildFrame(cmd, data));
  }

  /* ---------------- 配置 ---------------- */

  async function loadConfig() {
    cfg = await C.loadConfig();
    hands = C.buildHands(cfg);
    enabled = Object.keys(hands);
    target = enabled[0] || "right";

    current = {};
    torqueOn = {};
    for (const k of enabled) {
      current[k] = [...cfg.middle.positions];
      torqueOn[k] = true;      // PWM 没有力矩寄存器；连接即视为保持
    }
  }

  const pwmChannels = (fingerKey) => (cfg.pwm?.channels || {})[fingerKey] || [];

  /* ---------------- 发送 ---------------- */

  function queueAngles(angles, force) {
    pendingAngles = angles.map(C.clampAngle);
    const now = performance.now();
    const wait = Math.max(0, PWM.minWriteIntervalMs - (now - lastSendAt));
    if (force || wait === 0) {
      flushAngles();
    } else if (!sendTimer) {
      sendTimer = setTimeout(() => {
        sendTimer = null;
        flushAngles();
      }, wait);
    }
  }

  async function flushAngles() {
    if (!pendingAngles) return;
    const angles = pendingAngles;
    pendingAngles = null;
    lastSendAt = performance.now();
    try {
      await writeFrame(PWM.direct, angles);
    } catch (e) {
      emit({ type: "error", msg: `发送失败：${e.message || e}` });
    }
  }

  async function setSide(handKey) {
    try {
      await writeFrame(PWM.setSide, [handKey === "left" ? 0x02 : 0x01]);
    } catch (e) {
      /* 连接断开时忽略 */
    }
  }

  function sendPose(keys, positions, force) {
    for (const k of keys) {
      if (!hands[k]) continue;
      const angles = C.poseToPwmAngles(cfg, hands[k], positions);
      queueAngles(angles, force);
    }
  }

  async function handshake() {
    // 打开串口可能让 ESP32 复位，先等启动日志结束，再反复发 NOP 直到收到响应。
    for (let attempt = 0; attempt < 6; attempt++) {
      if (closing) throw new Error("连接已取消");
      await sleep(300);
      const wait = waitResponse(PWM.nop, 600);
      try {
        await writeFrame(PWM.nop, []);
        await wait;
        return;
      } catch (_) {
        /* 超时，继续重试 */
      }
    }
    throw new Error("ESP32 无响应：请检查波特率 115200、COM 口和 5 V 供电");
  }

  /* ---------------- 串口管理 ---------------- */

  function portInfo() {
    return {
      current: portName,
      connected: !!serialPort,
      dry_run: dryRun,
      available: [...knownPorts.entries()].map(([name, r]) => ({
        device: name,
        description: r.label,
        likely: r.likely,
      })),
    };
  }

  function describePort(port, index) {
    return C.describePort(port, index);
  }

  async function refreshPorts() {
    if (!navigator.serial) return [];
    const ports = await navigator.serial.getPorts();
    knownPorts.clear();
    ports.forEach((p, i) => {
      const d = describePort(p, i);
      knownPorts.set(d.name, { port: p, label: d.label, likely: d.likely });
    });
    return portInfo().available;
  }

  async function openPort(port, name) {
    await port.open({
      baudRate: PWM.baudRate,
      dataBits: 8,
      stopBits: 1,
      parity: "none",
      flowControl: "none",
      bufferSize: 4096,
    });
    serialPort = port;
    portName = name || "";
    writer = port.writable.getWriter();
    readerTask = readLoop();
  }

  async function closePort() {
    closing = true;
    if (sendTimer) {
      clearTimeout(sendTimer);
      sendTimer = null;
    }
    pendingAngles = null;

    try {
      if (reader) {
        try { await reader.cancel(); } catch (_) { /* ignore */ }
      }
      if (readerTask) {
        try { await readerTask; } catch (_) { /* ignore */ }
      }
      readerTask = null;
      if (writer) {
        try { writer.releaseLock(); } catch (_) { /* ignore */ }
        writer = null;
      }
      if (serialPort) {
        await serialPort.close();
      }
    } catch (e) {
      console.warn("关闭串口失败：", e);
    }

    serialPort = null;
    portName = "";
    rxBuf = [];
    waiters.forEach((w) => {
      clearTimeout(w.timer);
      try { w.reject(new Error("串口已断开")); } catch (_) { /* ignore */ }
    });
    waiters = [];
    closing = false;
  }

  /* ---------------- 会话（与 server.py / io.js 对齐） ---------------- */

  function stateMessage() {
    return {
      type: "state",
      driver: "pwm",
      capabilities: { torque: false, speed: false },
      hands: Object.fromEntries(
        enabled.map((k) => {
          const h = hands[k];
          const fingers = h.fingers.map((f) => ({
            key: f.key,
            name: f.name,
            ids: pwmChannels(f.key),
          }));
          return [k, {
            label: h.label,
            angle_offset_deg: h.angle_offset_deg,
            mirror_pose: h.mirror_pose,
            fingers,
            servo_ids: fingers.flatMap((f) => f.ids),
            torque: !!torqueOn[k],
          }];
        })
      ),
      enabled,
      poses: cfg.poses,
      middle: cfg.middle,
      sequences: cfg.sequences || {},
      limits: cfg.limits,
      axes: cfg.axes || {},
      camera: cfg.camera || {},
      pwm: {
        channels: cfg.pwm?.channels || {},
        middle_deg: cfg.pwm?.middle_deg ?? 90,
        baudrate: cfg.pwm?.baudrate ?? PWM.baudRate,
      },
      target,
      positions: current,
      port: portInfo(),
    };
  }

  function pickTarget(msg) {
    const t = msg.target || target;
    if (hands[t] && enabled.includes(t)) return t;
    if (enabled.includes(target)) return target;
    return enabled[0];
  }

  function setPositions(hand, positions) {
    current[hand] = positions.map(Number);
  }

  function mergeAngles(hand, angles) {
    current[hand] = C.mergeAngles(hands, current, hand, angles);
    return current[hand];
  }

  async function onCommand(msg) {
    const cmd = msg.cmd;

    if (cmd === "hello") return emit(stateMessage());

    if (cmd === "ports") {
      if (msg.request && navigator.serial) {
        try {
          await navigator.serial.requestPort();
        } catch (e) {
          /* 用户取消选择 */
        }
        await refreshPorts();
      }
      return emit({ type: "ports", ...portInfo() });
    }

    if (cmd === "connect") {
      if (!navigator.serial) {
        return emit({ type: "error", msg: "这个浏览器不支持 Web Serial，请改用 Chrome 或 Edge。" });
      }
      let port = null;
      if (msg.port && knownPorts.has(msg.port)) {
        port = knownPorts.get(msg.port).port;
      } else {
        try {
          port = await navigator.serial.requestPort();
          const ports = await navigator.serial.getPorts();
          const idx = ports.indexOf(port);
          const d = describePort(port, idx < 0 ? ports.length : idx);
          knownPorts.set(d.name, { port, label: d.label, likely: d.likely });
          msg = { ...msg, port: d.name };
        } catch (e) {
          return emit({ type: "error", msg: `没有选择串口：${e.message || e}` });
        }
      }

      await closePort();
      try {
        await openPort(port, msg.port);
        await handshake();
      } catch (e) {
        await closePort();
        return emit({ type: "error", msg: `连接 ${msg.port} 失败：${e.message || e}` });
      }

      await setSide(target);
      sendPose([target], cfg.middle.positions, true);
      for (const k of enabled) setPositions(k, cfg.middle.positions);
      return emit({ type: "connected", ...portInfo(), positions: current });
    }

    if (cmd === "disconnect") {
      await closePort();
      return emit({ type: "disconnected", ...portInfo() });
    }

    if (cmd === "target") {
      target = pickTarget(msg);
      await setSide(target);
      return emit({ type: "target", target });
    }

    if (cmd === "pose") {
      const t = pickTarget(msg);
      const pose = cfg.poses[msg.name] || cfg.middle;
      const pos = C.posePositions(pose, t);
      setPositions(t, pos);
      sendPose([t], pos);
      return emit({ type: "positions", target: t, positions: current });
    }

    if (cmd === "set") {
      const t = pickTarget(msg);
      const merged = mergeAngles(t, msg.angles || {});
      sendPose([t], merged);
      return;
    }

    if (cmd === "middle") {
      const t = pickTarget(msg);
      setPositions(t, cfg.middle.positions);
      sendPose([t], cfg.middle.positions, true);
      return emit({ type: "positions", target: t, positions: current });
    }

    if (cmd === "torque") {
      const t = pickTarget(msg);
      torqueOn[t] = !!msg.on;
      // 固件没有力矩释放命令，这里只同步 UI 状态，不下发硬件指令。
      return emit({ type: "torque", target: t, on: !!msg.on, hands: { ...torqueOn } });
    }

    if (cmd === "stop") {
      try { await writeFrame(PWM.stop, []); } catch (_) { /* ignore */ }
      for (const k of enabled) torqueOn[k] = true;
      return emit({ type: "stopped", hands: { ...torqueOn } });
    }
  }

  /* ---------------- 对外接口 ---------------- */

  let initDone = false;

  window.AH_PWM = {
    async init(opts) {
      emit = (opts && opts.onMessage) || (() => {});
      dryRun = !navigator.serial;
      if (!initDone) {
        await loadConfig();
        initDone = true;
        if (navigator.serial) {
          navigator.serial.addEventListener("disconnect", async (e) => {
            if (serialPort && e.target === serialPort) {
              await closePort();
              emit({ type: "disconnected", ...portInfo() });
            }
          });
          await refreshPorts();
        }
      }
      emit(stateMessage());
    },
    send(msg) {
      Promise.resolve(onCommand(msg)).catch((e) =>
        emit({ type: "error", msg: e.message || String(e) }));
      return true;
    },
    isConnected: () => !!serialPort,
    isDryRun: () => dryRun,
    supportsSerial: () => !!navigator.serial,
    _protocol: {
      checksum,
      buildFrame,
      poseToPwmAngles: (handKey, positions) =>
        C.poseToPwmAngles(cfg, hands[handKey], positions),
      PWM,
    },
  };
})();
