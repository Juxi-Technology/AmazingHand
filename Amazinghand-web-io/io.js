/* Amazinghand-web-io —— 浏览器内的“后端”
 *
 * 取代 Amazinghand-web/server.py：命令与消息协议完全一致（app.js 不用改逻辑），
 * 但串口改走 Web Serial API，所以整个站点可以当纯静态页面托管（GitHub Pages）。
 *
 * 只支持 Chromium 系浏览器（Chrome / Edge）：Web Serial 是 Chromium 专有 API，
 * 且要求安全上下文（https 或 localhost）。没有该 API 时自动进入 dry 模式：
 * 界面可用、摄像头可用，但不下发任何串口数据。
 */
(function () {
  "use strict";

  /* ---------------- SCS0009 协议常量 ----------------
   * 与 rustypot 的 servo/feetech/scs0009.rs 一致：
   *   1024 步 / 300°，中位 511，多字节寄存器大端。
   * 幂寄存器地址：torque_enable=40, goal_position=42, goal_speed=46。
   */
  const SCS = {
    steps: 1024,
    center: 511,
    spanRad: (300 * Math.PI) / 180,
    baudRate: 1000000,
  };
  const INST_SYNC_WRITE = 0x83;
  const BROADCAST_ID = 0xfe;
  const ADDR = { torqueEnable: 40, goalPosition: 42, goalSpeed: 46 };

  const POSE_EPSILON_DEG = 0.5;   // 与 server.py 一致：变化小于此值不下发
  const MIN_WRITE_INTERVAL_MS = 20;

  /* ---------------- 状态 ---------------- */
  let cfg = null;                 // 去掉 "//" 注释键后的 config
  let hands = {};                 // { right: {...,fingers,servo_ids}, left: {...} }
  let enabled = [];               // ["right","left"]
  let current = {};               // { right: [8 个姿态值], left: [...] }
  let target = "right";
  let torqueOn = {};              // { right: false, left: false }
  let lastGoal = {};              // { 舵机ID: 目标角度 }
  let lastWriteAt = 0;

  let serialPort = null;          // SerialPort 实例
  let writer = null;
  let portName = "";              // 当前串口的显示名
  const knownPorts = new Map();   // 显示名 -> { port, label, likely }

  let dryRun = false;             // 无 Web Serial 时的降级模式
  let emit = () => {};            // 向 app.js 发消息

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const clampPose = (v) =>
    Math.max(cfg.limits.pose_min_deg, Math.min(cfg.limits.pose_max_deg, Number(v)));

  /* ---------------- 配置 ---------------- */

  function stripComments(node) {
    if (Array.isArray(node)) return node.map(stripComments);
    if (node && typeof node === "object") {
      const out = {};
      for (const [k, v] of Object.entries(node)) {
        if (!k.startsWith("//")) out[k] = stripComments(v);
      }
      return out;
    }
    return node;
  }

  async function loadConfig() {
    const res = await fetch("./config.json", { cache: "no-cache" });
    if (!res.ok) throw new Error(`config.json HTTP ${res.status}`);
    cfg = stripComments(await res.json());

    hands = {};
    for (const [k, h] of Object.entries(cfg.hands)) {
      if (k !== "left" && k !== "right") continue;
      const servoIds = h.fingers.flatMap((f) => f.ids);
      hands[k] = { ...h, key: k, servo_ids: servoIds, torque: false };
    }
    enabled = Object.keys(hands);
    target = enabled[0];

    current = {};
    for (const k of enabled) current[k] = [...cfg.middle.positions];
    torqueOn = {};
    for (const k of enabled) torqueOn[k] = false;
  }

  /* ---------------- 换算（对齐 server.py / AmazingHandControl） ----------------
   * 1) mirror_pose 为真时，先交换每根手指两个舵机的值
   * 2) servo_deg = (ID 奇数 ? +1 : -1) × (姿态值 − angle_offset_deg)
   */
  function poseToServoGoals(hand, positions) {
    const pos = positions.map(Number);
    if (hand.mirror_pose) {
      for (let i = 0; i < hand.fingers.length; i++) {
        const a = i * 2;
        [pos[a], pos[a + 1]] = [pos[a + 1], pos[a]];
      }
    }
    const goals = [];
    hand.fingers.forEach((finger, i) => {
      finger.ids.forEach((id, j) => {
        const v = pos[i * 2 + j] - hand.angle_offset_deg;
        goals.push([id, id % 2 === 0 ? -v : v]);
      });
    });
    return goals;
  }

  /* 角度(弧度) → SCS0009 寄存器值；与 rustypot 的 AnglePosition::to_raw 同式 */
  function angleToRaw(rad) {
    const raw = Math.trunc((SCS.steps * rad) / SCS.spanRad + SCS.center);
    return Math.max(0, Math.min(SCS.steps - 1, raw));
  }

  /* 速度(rad/s) → 寄存器值；与 rustypot 的 Velocity::to_raw 同式 */
  function speedToRaw(radPerSec) {
    const raw = Math.trunc(radPerSec / (SCS.spanRad / SCS.steps));
    return Math.max(0, Math.min(SCS.steps - 1, raw));
  }

  /* ---------------- 协议帧 ----------------
   * Feetech SCS（protocol v1 帧）：
   *   FF FF ID LEN INST PARAM... CHECKSUM
   *   LEN      = 参数长度 + 2（指令 + 校验各占 1 字节）
   *   CHECKSUM = ~(ID + LEN + INST + ΣPARAM) & 0xFF
   * Sync Write 的参数：ADDR、每 ID 数据长度、(ID, DATA…) × N
   */
  function checksum(bytes) {
    let sum = 0;
    for (const b of bytes) sum += b;
    return ~sum & 0xff;
  }

  function syncWritePacket(addr, entries) {
    const dataLen = entries[0].data.length;
    const params = [addr, dataLen];
    for (const e of entries) {
      params.push(e.id);
      for (const b of e.data) params.push(b);
    }
    const body = [BROADCAST_ID, params.length + 2, INST_SYNC_WRITE, ...params];
    return Uint8Array.from([0xff, 0xff, ...body, checksum(body)]);
  }

  const be16 = (v) => [(v >> 8) & 0xff, v & 0xff];

  async function syncWrite(addr, entries) {
    if (!writer || !entries.length) return;
    try {
      await writer.write(syncWritePacket(addr, entries));
    } catch (e) {
      console.warn("串口写入失败：", e);
      emit({ type: "error", msg: `串口写入失败：${e.message || e}` });
    }
  }

  /* ---------------- 驱动 ---------------- */

  function setTorque(keys, on) {
    for (const k of keys) {
      const h = hands[k];
      if (!h) continue;
      syncWrite(
        ADDR.torqueEnable,
        h.servo_ids.map((id) => ({ id, data: [on ? 1 : 0] }))
      );
      torqueOn[k] = on;
      h.torque = on;
    }
  }

  function sendPose(keys, positions, speed, force) {
    const safe = positions.map(clampPose);
    for (const k of keys) {
      const h = hands[k];
      if (!h) continue;
      let goals = poseToServoGoals(h, safe);

      if (!force) {
        goals = goals.filter(([id, g]) => Math.abs((lastGoal[id] ?? 1e9) - g) >= POSE_EPSILON_DEG);
        if (!goals.length) continue;
      }
      const now = Date.now();
      if (!force && now - lastWriteAt < MIN_WRITE_INTERVAL_MS) continue;
      lastWriteAt = now;

      for (const [id, g] of goals) lastGoal[id] = g;

      const spd = speed === undefined || speed === null ? cfg.limits.speed : speed;
      syncWrite(ADDR.goalSpeed, goals.map(([id]) => ({ id, data: be16(speedToRaw(spd)) })));
      syncWrite(
        ADDR.goalPosition,
        goals.map(([id, g]) => ({ id, data: be16(angleToRaw((g * Math.PI) / 180)) }))
      );
    }
  }

  function goMiddle(keys) {
    sendPose(keys, cfg.middle.positions, undefined, true);
  }

  function releaseAll() {
    for (const k of enabled) setTorque([k], false);
  }

  /* ---------------- 串口 ---------------- */

  const LIKELY_VIDS = new Set([0x1a86, 0x10c4, 0x0403, 0x067b, 0x2341, 0x2e8a]);

  function describePort(port, index) {
    const info = port.getInfo ? port.getInfo() : {};
    const vid = info.usbVendorId;
    const pid = info.usbProductId;
    const hex = (n) => (n === undefined ? "????" : n.toString(16).padStart(4, "0"));
    const name = `USB ${hex(vid)}:${hex(pid)} #${index + 1}`;
    const likely = vid !== undefined && LIKELY_VIDS.has(vid);
    return { name, label: likely ? `${name} ★` : name, likely };
  }

  async function refreshPorts() {
    if (!navigator.serial) return [];
    const ports = await navigator.serial.getPorts();
    knownPorts.clear();
    ports.forEach((p, i) => {
      const d = describePort(p, i);
      knownPorts.set(d.name, { port: p, label: d.label, likely: d.likely });
    });
    return [...knownPorts.entries()].map(([name, r]) => ({
      device: name,
      description: r.label,
      likely: r.likely,
    }));
  }

  async function openPort(port, name) {
    await port.open({
      baudRate: SCS.baudRate,
      dataBits: 8,
      stopBits: 1,
      parity: "none",
      flowControl: "none",
      bufferSize: 4096,
    });
    serialPort = port;
    portName = name;
    writer = port.writable.getWriter();
  }

  async function closePort() {
    try {
      releaseAll();
    } catch (e) {
      /* 断开时松力矩失败不值得打断流程 */
    }
    try {
      if (writer) {
        writer.releaseLock();
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
    lastGoal = {};
  }

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

  /* ---------------- 会话（与 server.py 的 Session 对齐） ---------------- */

  function stateMessage() {
    return {
      type: "state",
      hands: Object.fromEntries(
        enabled.map((k) => [
          k,
          {
            label: hands[k].label,
            angle_offset_deg: hands[k].angle_offset_deg,
            mirror_pose: hands[k].mirror_pose,
            fingers: hands[k].fingers.map((f) => ({ key: f.key, name: f.name, ids: f.ids })),
            servo_ids: hands[k].servo_ids,
            torque: !!torqueOn[k],
          },
        ])
      ),
      enabled,
      poses: cfg.poses,
      middle: cfg.middle,
      sequences: cfg.sequences || {},
      limits: cfg.limits,
      axes: cfg.axes || {},
      camera: cfg.camera || {},
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

  function posePositions(pose, hand) {
    return pose[hand] || pose.positions;
  }

  function setPositions(hand, positions) {
    current[hand] = positions.map(Number);
  }

  function mergeAngles(hand, angles) {
    const out = [...current[hand]];
    hands[hand].fingers.forEach((f, fi) => {
      const v = angles[f.key];
      if (Array.isArray(v) && v.length === 2) {
        out[fi * 2] = Number(v[0]);
        out[fi * 2 + 1] = Number(v[1]);
      }
    });
    current[hand] = out;
    return out;
  }

  async function ensureTorque(hand) {
    if (torqueOn[hand]) return;
    setTorque([hand], true);
    await sleep(300);
  }

  async function onCommand(msg) {
    const cmd = msg.cmd;

    if (cmd === "hello") return emit(stateMessage());

    if (cmd === "ports") {
      if (msg.request && navigator.serial) {
        // 必须在用户手势里同步调用（本分支第一个 await 之前），否则浏览器拒绝
        try {
          await navigator.serial.requestPort();
        } catch (e) {
          /* 用户取消选择，保持现有列表 */
        }
        await refreshPorts();
      }
      return emit({ type: "ports", ...portInfo() });
    }

    if (cmd === "connect") {
      if (!navigator.serial) {
        return emit({
          type: "error",
          msg: "这个浏览器不支持 Web Serial，请改用 Chrome 或 Edge。",
        });
      }
      let port = null;
      const picked = msg.port ? knownPorts.get(msg.port) : null;
      if (picked) {
        port = picked.port;
      } else {
        // 必须在用户手势里同步调用 requestPort()，否则浏览器会拒绝
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
      } catch (e) {
        return emit({ type: "error", msg: `连接 ${msg.port} 失败：${e.message || e}` });
      }

      // 接上先开力矩再回中位，避免上电残留姿态
      setTorque(enabled, true);
      await sleep(400);
      goMiddle(enabled);
      for (const k of enabled) setPositions(k, cfg.middle.positions);

      return emit({
        type: "connected",
        ...portInfo(),
        positions: current,
      });
    }

    if (cmd === "disconnect") {
      await closePort();
      return emit({ type: "disconnected", ...portInfo() });
    }

    if (cmd === "target") {
      target = pickTarget(msg);
      return emit({ type: "target", target });
    }

    if (cmd === "pose") {
      const t = pickTarget(msg);
      const pose = cfg.poses[msg.name] || cfg.middle;
      const pos = posePositions(pose, t);
      setPositions(t, pos);
      await ensureTorque(t);
      sendPose([t], pos, msg.speed ?? cfg.limits.speed);
      return emit({ type: "positions", target: t, positions: current });
    }

    if (cmd === "set") {
      const t = pickTarget(msg);
      const merged = mergeAngles(t, msg.angles || {});
      await ensureTorque(t);
      sendPose([t], merged, msg.speed);
      return;
    }

    if (cmd === "middle") {
      const t = pickTarget(msg);
      setPositions(t, cfg.middle.positions);
      await ensureTorque(t);
      goMiddle([t]);
      return emit({ type: "positions", target: t, positions: current });
    }

    if (cmd === "torque") {
      const t = pickTarget(msg);
      setTorque([t], !!msg.on);
      return emit({
        type: "torque",
        target: t,
        on: !!msg.on,
        hands: { ...torqueOn },
      });
    }

    if (cmd === "stop") {
      releaseAll();
      return emit({ type: "stopped", hands: Object.fromEntries(enabled.map((k) => [k, false])) });
    }
  }

  /* ---------------- 初始化 ---------------- */

  async function init(opts) {
    emit = (opts && opts.onMessage) || (() => {});
    dryRun = !navigator.serial;
    try {
      await loadConfig();
    } catch (e) {
      emit({ type: "error", msg: `读取 config.json 失败：${e.message || e}` });
      return;
    }
    if (!dryRun) {
      try {
        await refreshPorts();
        navigator.serial.addEventListener("disconnect", async (ev) => {
          if (serialPort && ev.target === serialPort) {
            await closePort();
            emit({ type: "disconnected", ...portInfo() });
          }
        });
      } catch (e) {
        console.warn("枚举串口失败：", e);
      }
    }
    emit(stateMessage());
  }

  window.AHIO = {
    init,
    send: (msg) => {
      Promise.resolve(onCommand(msg)).catch((e) =>
        emit({ type: "error", msg: e.message || String(e) })
      );
      return true;
    },
    isConnected: () => !!serialPort,
    isDryRun: () => dryRun,
    supportsSerial: () => !!navigator.serial,
    // 供调试/单测使用
    _protocol: { checksum, syncWritePacket, angleToRaw, speedToRaw, poseToServoGoals, ADDR },
  };
})();
