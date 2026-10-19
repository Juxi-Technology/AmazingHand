/* AmazingHand 网页控制 —— 前端主逻辑（Web Serial / 纯静态版）
 *
 * 后端由 io.js 在页面内实现（Web Serial 直连串口），消息格式与 WebSocket 版一致：
 *   发: {cmd:"pose"|"set"|"middle"|"torque"|"stop"|"target", target, ...}
 *   收: {type:"state"|"positions"|"torque"|"stopped"|"target", ...}
 *
 * target 取值：left / right
 * 姿态数组 8 个值，顺序由后端下发的 fingers 决定（无名指/中指/食指/拇指）。
 */

const el = (id) => document.getElementById(id);

/* 文案统一走 i18n.js。config.json 来的名字（手/手指/姿态）用稳定 key 现翻，
 * 词典里没有就退回 config 自己的 label。 */
const t = (key, vars) => window.I18N.t(key, vars);
const handName = (k, h) => window.I18N.pick("hand", k, h && h.label);
const fingerName = (f) => window.I18N.pick("finger", f.key, f.name);

const state = {
  target: "right",          // left / right
  hands: {},
  enabled: [],
  poses: {},
  middle: { positions: [] },
  positions: {},            // { right: [8], left: [8] }
  limits: { pose_min_deg: -120, pose_max_deg: 120 },
  connected: false,
  port: null,               // 最近一次串口状态，切换语言时重渲染用
};

/* ------------------------------------------------------------ 连接 */

function connect() {
  AHIO.init({ onMessage: handle });
}

function setConn(ok) {
  const b = el("conn");
  b.textContent = t(ok ? "conn.on" : "conn.off");
  b.className = "badge " + (ok ? "ok" : "bad");
}

function send(obj) {
  return AHIO.send(obj);
}

/* ------------------------------------------------------------ 收消息 */

function handle(m) {
  if (m.type === "state") {
    state.hands = m.hands;
    state.enabled = m.enabled;
    state.poses = m.poses;
    state.middle = m.middle;
    state.positions = m.positions;
    state.limits = m.limits;
    state.axes = m.axes || null;
    // 摄像头的两根轴目标值也要存下来，否则 tracking.js 的 camCfg() 永远走
    // DEFAULT_CAMERA 兜底 —— config.json 的 camera 段就白改了
    state.camera = m.camera || null;
    state.target = (m.target && m.enabled.includes(m.target)) ? m.target : m.enabled[0];
    if (m.port) {
      state.connected = !!m.port.connected;
      setConn(state.connected);
      renderPorts(m.port);
    }
    setupTargets();
    renderPoses();
    renderFingers();
    updateMeta();
    return;
  }
  if (m.type === "ports" || m.type === "connected" || m.type === "disconnected") {
    state.connected = !!m.connected;
    setConn(state.connected);
    renderPorts(m);
    if (m.positions) { state.positions = m.positions; syncSliders(); }
    return;
  }
  if (m.type === "error") {
    // 后端直接给的中文错误原文先用着 —— 服务端不做 i18n
    setPortState(m.msg || t("port.error"), true);
    return;
  }
  if (m.type === "target") {
    state.target = m.target;
    renderFingers();
    updateMeta();
    return;
  }
  if (m.type === "positions") {
    state.positions = m.positions;
    syncSliders();
    return;
  }
  if (m.type === "torque") {
    if (m.hands) for (const [k, v] of Object.entries(m.hands)) {
      if (state.hands[k]) state.hands[k].torque = v;
    } else if (state.hands[m.target]) {
      state.hands[m.target].torque = m.on;
    }
    updateTorqueBtn();
    return;
  }
  if (m.type === "stopped") {
    for (const k of Object.keys(state.hands)) state.hands[k].torque = false;
    updateTorqueBtn();
    return;
  }
}

/* ------------------------------------------------------------ 取数 */

/** 当前控制哪只手 */
function displayHand() {
  return state.target;
}

function currentPositions() {
  return state.positions[displayHand()] || state.middle.positions || [];
}

/* ------------------------------------------------------------ 渲染 */

function setupTargets() {
  const box = el("targets");
  box.innerHTML = "";
  for (const k of ["right", "left"]) {
    if (!state.enabled.includes(k)) continue;
    const b = document.createElement("button");
    b.className = "target" + (state.target === k ? " active" : "");
    b.dataset.target = k;
    b.textContent = handName(k, state.hands[k]);
    b.onclick = () => {
      state.target = k;
      document.querySelectorAll(".target").forEach(x =>
        x.classList.toggle("active", x.dataset.target === k));
      send({ cmd: "target", target: k });
      renderFingers();
      updateMeta();
      updateTorqueBtn();
    };
    box.appendChild(b);
  }
}

function renderFingers() {
  const h = state.hands[displayHand()];
  const box = el("fingers");
  if (!h) { box.innerHTML = ""; return; }

  const pos = currentPositions();
  // 范围仍然读 config 的 axes，只有标签走词典
  const ax = state.axes?.flexion
    ? state.axes
    : { flexion: { min: -50, max: 90 }, spread: { min: -45, max: 45 } };

  box.innerHTML = "";
  h.fingers.forEach((f, fi) => {
    const { base, side } = toAxes(pos[fi * 2], pos[fi * 2 + 1]);
    const wrap = document.createElement("div");
    wrap.className = "finger";
    wrap.innerHTML = `
      <h3>${fingerName(f)}<span class="ids">ID ${f.ids.join(" / ")}</span></h3>
      <div class="joint">
        <label>${t("axis.flexion")}<b data-readout="${f.key}-0">${Math.round(base)}</b></label>
        <input type="range" data-finger="${f.key}" data-axis="0" data-fi="${fi}"
               min="${ax.flexion.min}" max="${ax.flexion.max}" step="1" value="${Math.round(base)}">
        <label class="muted">${t("axis.flexionHint")}</label>
      </div>
      <div class="joint">
        <label>${t("axis.spread")}<b data-readout="${f.key}-1">${Math.round(side)}</b></label>
        <input type="range" data-finger="${f.key}" data-axis="1" data-fi="${fi}"
               min="${ax.spread.min}" max="${ax.spread.max}" step="1" value="${Math.round(side)}">
        <label class="muted">${t("axis.spreadHint")}</label>
      </div>`;
    box.appendChild(wrap);
  });

  box.querySelectorAll("input[type=range]").forEach(inp => {
    inp.addEventListener("input", onSlider);
  });
  syncSliders();
}

/* 官方约定：每根手指两个舵机是「屈伸轴 + 侧摆轴」的合成。
 *   servo1 = 屈伸 + 侧摆        base = (s1 + s2) / 2
 *   servo2 = 屈伸 − 侧摆        side = (s1 − s2) / 2
 * 剪刀手那种「两根手指分开」就是靠 side 一正一负。
 */
function toAxes(s1, s2) {
  return { base: (s1 + s2) / 2, side: (s1 - s2) / 2 };
}
function toServo(base, side) {
  return [base + side, base - side];
}

function onSlider(ev) {
  const t = ev.target;
  const fi = Number(t.dataset.fi);
  const axis = Number(t.dataset.axis);
  const v = Number(t.value);

  const h = state.hands[displayHand()];
  const f = h.fingers[fi];
  const pos = currentPositions().slice();
  const cur = toAxes(pos[fi * 2], pos[fi * 2 + 1]);
  if (axis === 0) cur.base = v; else cur.side = v;

  const [s1, s2] = toServo(cur.base, cur.side);
  pos[fi * 2] = s1;
  pos[fi * 2 + 1] = s2;

  // 乐观更新本地，滑块跟手
  state.positions[displayHand()] = pos;
  updateReadout(f.key, 0, cur.base);
  updateReadout(f.key, 1, cur.side);

  send({ cmd: "set", target: state.target, angles: { [f.key]: [s1, s2] } });
}

function updateReadout(key, idx, val) {
  const n = document.querySelector(`[data-readout="${key}-${idx}"]`);
  if (n) n.textContent = Math.round(val);
}

function syncSliders() {
  const pos = currentPositions();
  document.querySelectorAll("input[type=range]").forEach(inp => {
    const fi = Number(inp.dataset.fi);
    const axis = Number(inp.dataset.axis);
    const a = toAxes(pos[fi * 2] ?? 0, pos[fi * 2 + 1] ?? 0);
    const v = axis === 0 ? a.base : a.side;
    inp.value = Math.round(v);
    updateReadout(inp.dataset.finger, axis, v);
  });
}

function renderPoses() {
  const box = el("gestures");
  box.innerHTML = "";
  for (const [name, p] of Object.entries(state.poses)) {
    const b = document.createElement("button");
    b.textContent = window.I18N.pick("pose", name, p.label || name);
    b.title = name;
    b.onclick = () => send({ cmd: "pose", target: state.target, name });
    box.appendChild(b);
  }
}

/* ------------------------------------------------------------ 串口 */

function setPortState(text, isError) {
  const n = el("port-state");
  n.textContent = text || "";
  n.style.color = isError ? "var(--danger)" : "var(--muted)";
}

function renderPorts(p) {
  state.port = p;                       // 存下来，切换语言时重渲染要用
  const sel = el("port-select");
  const prev = sel.value;
  // state 下发的是 port.available；ports/connected/disconnected 回复历史上用过 ports 键，两个都认
  const ports = p.available || p.ports || [];
  const cur = p.current || "";
  const connected = !!p.connected;

  sel.innerHTML = "";
  if (p.dry_run) {
    const o = document.createElement("option");
    o.value = ""; o.textContent = t("port.dryRun");
    sel.appendChild(o);
    sel.disabled = true;
  } else if (!ports.length) {
    // 提示项的 value 必须为空 —— 否则点「连接」会把提示文字当成串口名发出去
    const o = document.createElement("option");
    o.value = ""; o.textContent = t("port.none");
    sel.appendChild(o);
    sel.disabled = true;
  } else {
    sel.disabled = false;
    for (const q of ports) {
      const o = document.createElement("option");
      o.value = q.device;
      o.textContent = q.likely ? `${q.device}  ★  ${q.description}` : `${q.device}  ${q.description}`;
      sel.appendChild(o);
    }
  }

  // 优先保持用户的选择，其次跟当前已连接的端口
  const want = cur || prev;
  if (want && [...sel.options].some(o => o.value === want)) sel.value = want;

  el("btn-port-connect").disabled = !!p.dry_run || !ports.length;
  el("btn-port-connect").textContent = t(connected ? "port.reconnect" : "port.connect");
  el("btn-port-disconnect").disabled = !connected;

  if (p.dry_run) setPortState(t("port.dryRunHint"));
  else if (connected) setPortState(t("port.connected", { port: cur }));
  else if (ports.length) setPortState(t("port.pick"));
  else setPortState(t("port.plugIn"));
}

function bindPort() {
  el("btn-port-refresh").onclick = () => {
    setPortState(t("port.scanning"));
    // Web Serial 不能静默枚举：点一下由浏览器弹窗让你选设备（只会记住授权过的）
    send({ cmd: "ports", request: true });
  };
  el("btn-port-connect").onclick = () => {
    const port = el("port-select").value;
    if (!port) return;
    setPortState(t("port.connecting", { port }));
    send({ cmd: "connect", port });
  };
  el("btn-port-disconnect").onclick = () => {
    setPortState(t("port.disconnecting"));
    send({ cmd: "disconnect" });
  };
}

/* ------------------------------------------------------------ 渲染 */

function updateMeta() {
  const h = state.hands[state.target];
  if (!h) return;
  el("hand-meta").textContent = `${handName(state.target, h)} · ID ${h.servo_ids.join(", ")}`;
}

function updateTorqueBtn() {
  const on = !!state.hands[state.target]?.torque;
  el("btn-torque").textContent = t(on ? "btn.torqueRelease" : "btn.torqueEnable");
}

/* ------------------------------------------------------------ 交互 */

function bind() {
  bindPort();

  el("btn-middle").onclick = () => send({ cmd: "middle", target: state.target });

  el("btn-torque").onclick = () => {
    const on = !!state.hands[state.target]?.torque;
    send({ cmd: "torque", target: state.target, on: !on });
  };

  el("btn-stop").onclick = () => send({ cmd: "stop" });

  el("tab-manual").onclick = () => switchTab("manual");
  el("tab-camera").onclick = () => switchTab("camera");
}

function switchTab(which) {
  const manual = which === "manual";
  el("tab-manual").classList.toggle("active", manual);
  el("tab-camera").classList.toggle("active", !manual);
  el("panel-manual").classList.toggle("hidden", !manual);
  el("panel-camera").classList.toggle("hidden", manual);
}

/* ------------------------------------------------------------ 对外 */

window.AH = {
  target: () => state.target,
  /** 让机械手回到中位（摄像头启动前先调一次，避免上手就是随机姿势） */
  middle() { return send({ cmd: "middle", target: state.target }); },
  sendAngles(angles) {
    return send({ cmd: "set", target: state.target, angles });
  },
  connected: () => state.connected,
  fingerOrder() {
    const h = state.hands[displayHand()];
    return h ? h.fingers.map(f => f.key) : ["ring", "middle", "pointer", "thumb"];
  },
};

/* 切换语言后把动态生成的文案重刷一遍（静态那些由 I18N.apply() 负责） */
window.I18N.onChange(() => {
  setConn(state.connected);
  setupTargets();
  renderPoses();
  renderFingers();
  updateMeta();
  updateTorqueBtn();
  if (state.port) renderPorts(state.port);
});

bind();
connect();
