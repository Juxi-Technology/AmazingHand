/* AmazingHand 网页控制 —— 摄像头互动遥控
 *
 * 在浏览器本地跑 MediaPipe，画面不离开本机。
 * 识别到的手部关键点换算成 4 根手指的姿态值，通过 window.AH.sendAngles() 下发。
 *
 * MediaPipe 资源放在 ./mediapipe/（离线可用，不依赖外网 CDN）：
 *   vision_bundle.mjs / wasm/* / hand_landmarker.task
 *
 * 加载顺序：**先开摄像头，再加载模型**。
 * 反过来的话，模型一旦加载失败摄像头就永远开不了 —— 表现是「点了没画面」。
 */

/* MediaPipe 资源按顺序探测：本地 ./mediapipe/ 优先，其次是同级目录
 * ../Amazinghand-web/web/mediapipe/ —— 这样不必在网络仓库里再存一份 42MB 资源。
 * 部署到 GitHub Pages 时只要两个目录都在站点里即可。 */
let HandLandmarker = null, FilesetResolver = null, DrawingUtils = null;
let MP_BASE = null;

async function loadMediapipe() {
  const bases = [
    window.AH_MEDIAPIPE_BASE,
    "./mediapipe",
    "../Amazinghand-web/web/mediapipe",
  ].filter(Boolean);
  let lastErr = null;
  for (const base of bases) {
    try {
      const mod = await import(`${base}/vision_bundle.mjs`);
      MP_BASE = base;
      HandLandmarker = mod.HandLandmarker;
      FilesetResolver = mod.FilesetResolver;
      DrawingUtils = mod.DrawingUtils;
      buildBoneGroups();
      return;
    } catch (e) {
      lastErr = e;
      console.warn("MediaPipe 资源不可用：", base, e);
    }
  }
  throw lastErr || new Error("MediaPipe 资源加载失败");
}

/* 文案统一走 i18n.js（i18n.js 是普通脚本，在 app.js 之前加载） */
const t = (key, vars) => window.I18N.t(key, vars);
const fingerLabel = (k) => window.I18N.pick("finger", k, k);

/* 两根轴的目标值都在 config.json 的 camera 段（见下面的 camCfg / DEFAULT_CAMERA），
 * 不再写死在这里。采集只负责记录"你的手做这些动作时摄像头测到什么"，
 * 目标值由配置决定。 */
const SMOOTH = 0.35;            // 指数平滑，越大越平滑但越迟钝

let landmarker = null;
let stream = null;
let rafId = null;
let lastCount = 0;
let fpsT = 0, fpsN = 0;

const smooth = {};              // fingerKey -> 平滑后的 {b, s}

const el = (id) => document.getElementById(id);

/* ------------------------------------------------------- 状态显示 */

function setState(text, cls) {
  const n = el("cam-state");
  if (!n) return;
  n.textContent = text;
  n.style.color = cls === "err" ? "var(--danger)"
                : cls === "ok" ? "var(--ok)" : "var(--muted)";
}
const setRes = (t) => { const n = el("cam-res"); if (n) n.textContent = t; };
const setDetect = (t) => { const n = el("cam-detect"); if (n) n.textContent = t; };
const setSend = (t) => { const n = el("cam-send"); if (n) n.textContent = t; };
const say = (t) => { const n = el("track-out"); if (n) n.textContent = t || ""; };

function setStageIdle(idle) {
  const w = document.querySelector(".video-wrap");
  if (w) w.classList.toggle("idle", idle);
}

/* ------------------------------------------------------- 关键点数学 */

const LM = {
  WRIST: 0,
  // 拇指四个关节：CMC(1) → MCP(2) → IP(3) → TIP(4)。
  // 之前误把 IP 传了两次，三点退化导致拇指弯曲度恒为 0、完全不动。
  THUMB_CMC: 1, THUMB_MCP: 2, THUMB_IP: 3, THUMB_TIP: 4,
  INDEX_MCP: 5, INDEX_PIP: 6, INDEX_DIP: 7, INDEX_TIP: 8,
  MIDDLE_MCP: 9, MIDDLE_PIP: 10, MIDDLE_DIP: 11, MIDDLE_TIP: 12,
  RING_MCP: 13, RING_PIP: 14, RING_DIP: 15, RING_TIP: 16,
  PINKY_MCP: 17, PINKY_PIP: 18, PINKY_DIP: 19, PINKY_TIP: 20,
};

/* 骨骼按手指上色，一眼就能看出是哪根在乱跑。
 * 小拇指不参与手势映射（只用 无名/中/食/拇），但根部 MCP(17) 用来定右手的手掌坐标系，
 * 所以照样画，只是压暗。掌骨（0–1、5–9 这些）用中性灰。 */
const FINGER_BONES = {
  thumb:   { ids: [1, 2, 3, 4],     color: "#f97316" },   // 橙
  pointer: { ids: [5, 6, 7, 8],     color: "#ef4444" },   // 红
  middle:  { ids: [9, 10, 11, 12],  color: "#3b82f6" },   // 蓝
  ring:    { ids: [13, 14, 15, 16], color: "#eab308" },   // 黄
  pinky:   { ids: [17, 18, 19, 20], color: "#5b6b7d" },   // 暗
};
const PALM_COLOR = "#94a3b8";

/** 一根线段归谁：两端都落在某根手指的号段里就是那根手指的骨头；
 *  只要有一端落在小指上就算小指（含 13–17、0–17 这两根掌骨 ——
 *  小指被放歪时最先就体现在它们身上）；其余是掌骨，返回 null。 */
function edgeOwner(c) {
  if (FINGER_BONES.pinky.ids.includes(c.start) ||
      FINGER_BONES.pinky.ids.includes(c.end)) return "pinky";
  for (const k of ["thumb", "pointer", "middle", "ring"]) {
    const ids = FINGER_BONES[k].ids;
    if (ids.includes(c.start) && ids.includes(c.end)) return k;
  }
  return null;
}

/* 分组只算一次 —— HAND_CONNECTIONS 是静态的。
 * MediaPipe 模块改成动态加载了，所以要等它加载完再算（见 buildBoneGroups）。 */
let BONE_GROUPS = null;
function buildBoneGroups() {
  const g = { thumb: [], pointer: [], middle: [], ring: [], pinky: [], palm: [] };
  for (const c of HandLandmarker.HAND_CONNECTIONS) g[edgeOwner(c) ?? "palm"].push(c);
  BONE_GROUPS = g;
}

/* ---- 向量小工具（landmark 是 {x,y,z}）---- */
const sub   = (a, b) => ({ x: a.x - b.x, y: a.y - b.y, z: (a.z || 0) - (b.z || 0) });
const dot   = (a, b) => a.x * b.x + a.y * b.y + a.z * b.z;
const len3  = (a) => Math.hypot(a.x, a.y, a.z);
const scale = (a, k) => ({ x: a.x * k, y: a.y * k, z: a.z * k });
const cross = (a, b) => ({
  x: a.y * b.z - a.z * b.y,
  y: a.z * b.x - a.x * b.z,
  z: a.x * b.y - a.y * b.x,
});
function norm(a) { const l = len3(a); return l < 1e-9 ? { x: 0, y: 0, z: 0 } : scale(a, 1 / l); }

function angleAt(a, b, c) {
  const v1 = sub(a, b), v2 = sub(c, b);
  const m1 = len3(v1), m2 = len3(v2);
  if (m1 < 1e-6 || m2 < 1e-6) return Math.PI;
  return Math.acos(Math.max(-1, Math.min(1, dot(v1, v2) / (m1 * m2))));
}

/** 返回 0(完全伸直) ~ 1(完全弯曲) */
function flexionAt(lm, a, b, c, d) {
  const f1 = (Math.PI - angleAt(lm[a], lm[b], lm[c])) / Math.PI;
  const f2 = (Math.PI - angleAt(lm[b], lm[c], lm[d])) / Math.PI;
  return Math.max(0, Math.min(1, (f1 + f2) / 2));
}

/* ---- 手掌坐标系：用来算「手指张开程度」----
 *
 * 照搬官方 HandTracking/main.py 的建系方式，两个要点：
 *
 *  1) **用 worldLandmarks（米制、以手为中心），不是归一化图像坐标。**
 *     归一化坐标有透视畸变 —— 手掌相对镜头转个角度，比例就变，
 *     算出来的张开角会跟着漂。米制坐标没有这个问题。
 *
 *  2) **横轴的取法按左右手分开**：
 *       右手：小指根 − 手腕
 *       左手：食指根 − 手腕
 *     两只手这样取出来的是互为镜像的坐标系，所以同一套公式对左右手都成立，
 *     不用再额外做左右手镜像判断。
 *
 * 坐标轴：
 *   pz = 腕 → 中指根   沿手掌中轴（指尖方向）
 *   px = 掌心法线       垂直掌面（弯曲绕它……不，弯曲的转轴是 py）
 *   py = 手掌横轴       张开/并拢绕它转
 */
function handFrame(wlm, label) {
  const W = wlm[LM.WRIST];
  const pz = norm(sub(wlm[LM.MIDDLE_MCP], W));
  const vy = (label === "Left") ? sub(wlm[LM.INDEX_MCP], W)
                                : sub(wlm[LM.PINKY_MCP], W);
  const px = norm(cross(vy, pz));
  // py 的指向决定张开角的符号。实测「并拢」测出来是正的、「张开」是负的，
  // 所以取 cross(px, pz) —— 让「张开」为正，跟目标值 side_spread 同向。
  const py = cross(px, pz);
  return { pz, py, px };
}

const RAD2DEG = 180 / Math.PI;

/** 手指的张开角（度）。
 *
 * 直接取方向向量在手掌横轴 py 上的分量做 asin 反解，而不是
 * atan2(横向, 纵向)。原因：手指弯曲是绕「横轴」转的，
 * 转的时候横向分量不变、纵向分量变小 —— 用 atan2 的话纵向一变，
 * 算出来的角度就跟着变，表现为「一握拳手指就往一侧摆」。
 * 只用横向分量就完全不受弯曲影响。
 *
 * 正 = 偏向食指侧，负 = 偏小指侧。
 */
function splayDeg(lm, mcp, prox, frame) {
  const d = norm(sub(lm[prox], lm[mcp]));
  return Math.asin(Math.max(-1, Math.min(1, dot(d, frame.py)))) * RAD2DEG;
}

const lerp = (a, b, t) => a + (b - a) * t;
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

/* 摄像头互动遥控的两根轴。下面是**目标值**，端点由三个采集姿势实测（见 STAGES）。
 *
 * **屈伸轴**：伸直 → 握拳（四指都走这根）
 *     伸直 flex_straight = −50
 *     握拳 flex_fist     = 无名 90 / 中 90 / 食 90 / 拇 18
 *
 * **侧摆轴**：合拢 → 张开（**只有三指**）
 *                   无名指   中指   食指
 *     合拢            +45      0     −45
 *     张开            −45      0     +45
 *
 *   食指和无名指分处中轴两侧，所以一正一负；中指不动。
 *   拇指**不参与侧摆** —— 见 STAGES 上面的说明。
 *
 * 两根轴都靠**两点实测**映射：采集到的两个姿势直接定下一条直线，
 * 所以各手指测量值的正负方向由采集自动吸收，不需要再手动勾「反向」。
 *
 * 这些目标值放在 config.json 的 camera 段，可以在那儿改。
 */
const FINGER_ORDER = ["ring", "middle", "pointer", "thumb"];

const DEFAULT_CAMERA = {
  flex_straight: -50,
  flex_fist:     { ring: 90, middle: 90, pointer: 90, thumb: 18 },
  side_spread:   { ring: -45, middle: 0, pointer: 45, thumb: -45 },
  side_together: { ring: 45, middle: 0, pointer: -45, thumb: 0 },
};

function camCfg() {
  const c = state.camera || {};
  // 侧摆方向按「控制对象」分：左右手方向相反时，config 的 side_sign 里给出 ±1。
  // 取反时把两个端点都乘上 sign，等价于整根侧摆轴取反，屈伸不受影响。
  const hand = (window.AH && window.AH.target) ? window.AH.target() : "right";
  const sign = (c.side_sign && c.side_sign[hand]) || 1;
  const scaled = (o) => {
    if (!o || sign === 1) return o;
    const r = {};
    for (const k of Object.keys(o)) r[k] = o[k] * sign;
    return r;
  };
  return {
    flex_straight: c.flex_straight ?? DEFAULT_CAMERA.flex_straight,
    flex_fist:     c.flex_fist     || DEFAULT_CAMERA.flex_fist,
    side_spread:   scaled(c.side_spread   || DEFAULT_CAMERA.side_spread),
    side_together: scaled(c.side_together || DEFAULT_CAMERA.side_together),
  };
}

/* ---- 三个姿势，分开采 ----
 *
 * 不做自动推进：摆好一个姿势，点对应的按钮采一次（约 1 秒取平均）。
 * 顺序随意，采错了点同一个按钮重采。
 *
 *   ① 手指伸直张开，大拇指向外     → 屈伸的「伸直」端 + 侧摆的「张开」端
 *                                    也充当拇指的「指外」
 *   ② 手指伸直合拢，大拇指贴合食指 → 侧摆的「合拢」端
 *   ③ 握拳，大拇指贴近掌心         → 屈伸的「握拳」端
 *                                    也充当拇指的「指向掌心」
 *
 * 两根轴各要两个端点才能定一条直线，三个姿势刚好：
 * ① 一下子给出屈伸的下端和侧摆的一端，② 补上侧摆的另一端，③ 补上屈伸的上端。
 *
 * **拇指只做屈伸，不参与侧摆。** 它的 CMC 是对掌关节，弯曲和左右摆耦合得很厉害，
 * 硬拆成两根轴的结果是两根都不准。所以：
 *   屈伸 —— 取 ①「指外」和 ③「指向掌心」两点，就是它需要的两种姿势；
 *   侧摆 —— 恒为 0，两个舵机同值。
 * 拇指的「伸直」之所以取 ① 而不是 ②（贴合食指）：贴合时拇指已经在侧摆位上了，
 * 那一刻量到的屈伸零点是被污染的，拿它当零点整根轴都会偏。
 */
const CAP_FRAMES = 24;                     // 20Hz 下约 1.2 秒

const STAGES = [
  { id: "spread" },
  { id: "together" },
  { id: "fist" },
];

let capTarget = null;     // 正在采哪个姿势；null = 空闲
let capAcc = null;        // 本次采集的累加
let capN = 0;
let collected = {};       // { spread: {splay,flex}, together: {...}, fist: {...} }
let cal = null;           // 三个姿势都采完才非 null

function resetCal() {
  capTarget = null; capAcc = null; capN = 0; collected = {}; cal = null;
  renderCal();
}

/** 点按钮开始采某个姿势。正在采的时候不打断。 */
function startCapture(id) {
  if (capTarget) return;
  if (!stream) { say(t("cam.say.startFirst")); return; }
  capTarget = id;
  capAcc = { splay: {}, flex: {} };
  capN = 0;
  cal = null;                // 重采任何一个，整体都回到未就绪
  renderCal();
}

/** 每帧喂一次。攒够 CAP_FRAMES 帧就存下这个姿势的平均值。 */
function stepCapture(splay, flex) {
  for (const k of FINGER_ORDER) {
    capAcc.splay[k] = (capAcc.splay[k] || 0) + splay[k];
    capAcc.flex[k]  = (capAcc.flex[k]  || 0) + flex[k];
  }
  capN++;
  renderCal();
  if (capN < CAP_FRAMES) return;

  const avg = { splay: {}, flex: {} };
  for (const k of FINGER_ORDER) {
    avg.splay[k] = capAcc.splay[k] / capN;
    avg.flex[k]  = capAcc.flex[k]  / capN;
  }
  collected[capTarget] = avg;

  capTarget = null;
  capAcc = null;
  capN = 0;
  if (STAGES.every(s => collected[s.id])) cal = finishCal();
  renderCal();
}

/* 把三个姿势拼成两根轴各自的端点对。 */
function finishCal() {
  const a = collected.spread;
  const b = collected.together;
  const c = collected.fist;
  if (!a || !b || !c) return null;
  return {
    flexLo:  { ...a.flex },      // ① 伸直（拇指取"向外伸直"那个姿态）
    flexHi:  { ...c.flex },      // ③ 握拳
    splayLo: { ...b.splay },     // ② 合拢
    splayHi: { ...a.splay },     // ① 张开
  };
}

/* 没有「反向」开关：两根轴都是两点实测映射，方向已被采集吸收 ——
 * 测量值的正负在 (值 − 端点A) / (端点B − 端点A) 里自动约掉。 */

function toAngles(lm, wlm, label) {
  // 侧摆用手掌坐标系 + 米制关键点；屈伸仍用归一化关键点的关节夹角（已验证可用）
  const frame = handFrame(wlm, label);
  const CAM = camCfg();

  // 弯曲度 0~1
  const flex = {
    ring:    flexionAt(lm, LM.RING_MCP,   LM.RING_PIP,   LM.RING_DIP,   LM.RING_TIP),
    middle:  flexionAt(lm, LM.MIDDLE_MCP, LM.MIDDLE_PIP, LM.MIDDLE_DIP, LM.MIDDLE_TIP),
    pointer: flexionAt(lm, LM.INDEX_MCP,  LM.INDEX_PIP,  LM.INDEX_DIP,  LM.INDEX_TIP),
    thumb:   flexionAt(lm, LM.THUMB_CMC,  LM.THUMB_MCP,  LM.THUMB_IP,   LM.THUMB_TIP),
  };

  // 外张角（度）
  //
  // 用 splayDeg = asin(第一节指骨方向 · 手掌横轴)：
  //   · asin(d·py) 只看横向分量。弯曲是绕 py 转的，不改变横向分量，
  //     所以张开轴和弯曲轴天然解耦（之前用 atan2(横,纵) 就会耦合）。
  //   · 取 MCP→PIP（第一节指骨）而不是到指尖，避开 PIP/DIP 弯曲的干扰。
  const splay = {};
  for (const k of ["ring", "middle", "pointer", "thumb"]) {
    const mcp  = { ring: LM.RING_MCP,   middle: LM.MIDDLE_MCP, pointer: LM.INDEX_MCP,  thumb: LM.THUMB_MCP }[k];
    const prox = { ring: LM.RING_PIP,   middle: LM.MIDDLE_PIP, pointer: LM.INDEX_PIP,  thumb: LM.THUMB_IP  }[k];
    const v = splayDeg(wlm, mcp, prox, frame);
    splay[k] = v;
  }
  // 采集中或还没采完：不下发，手保持在中位 —— 免得被拽向"伸直"姿势
  if (!cal) {
    if (capTarget) stepCapture(splay, flex);
    return null;
  }
  const R = cal;

  const out = {};
  for (const key of Object.keys(flex)) {
    // ---- 屈伸轴：① 伸直 → ③ 握拳，两点实测 ----
    let base = CAM.flex_straight;
    let curl = 0;                       // 0 = 伸直，1 = 握紧
    {
      const lo = R.flexLo[key];
      const hi = R.flexHi[key];
      if (hi - lo > 0.05) {
        curl = clamp((flex[key] - lo) / (hi - lo), 0, 1);
        base = lerp(CAM.flex_straight, CAM.flex_fist[key], curl);
      }
    }
    const pb = smooth[key]?.b ?? base;
    base = pb + (base - pb) * SMOOTH;

    // ---- 侧摆轴：② 合拢 → ① 张开，两点实测。拇指不参与，恒为 0 ----
    //
    // 再按 (1 − 弯曲度) 衰减，握紧时归 0。
    // 原因：splayDeg 取的是 MCP→PIP 方向在掌面横轴上的分量，而手指弯曲正是绕这根轴
    // 转的 —— 弯到一定程度这个分量会翻向，"张开度"突然甩到另一头。表现出来就是侧摆
    // 猛跳，并把同组那个**偶数 ID** 舵机带着掉头（偶数 ID 拿到的是 base − side：
    // base 在涨、side 一翻它就反向）。奇数 ID 拿到 base + side，只是变快，看不出来。
    // 何况握拳本来就该是并拢的，所以让侧摆随弯曲线性收到 0。
    let side = 0;
    if (key !== "thumb") {
      const s0 = R.splayLo[key];
      const span = R.splayHi[key] - s0;
      side = CAM.side_together[key];
      if (Math.abs(span) > 1e-6) {
        const t = clamp((splay[key] - s0) / span, 0, 1);
        side = lerp(CAM.side_together[key], CAM.side_spread[key], t);
      }
      side *= (1 - curl);
    }
    const ps = smooth[key]?.s ?? side;
    side = ps + (side - ps) * SMOOTH;

    smooth[key] = { b: base, s: side };
    // 合成下发：servo1 = 屈伸 + 侧摆，servo2 = 屈伸 − 侧摆
    out[key] = [Math.round(base + side), Math.round(base - side)];
  }
  return out;
}


/* ------------------------------------------------------- 摄像头设备 */

async function listCameras() {
  if (!navigator.mediaDevices?.enumerateDevices) return [];
  try {
    const all = await navigator.mediaDevices.enumerateDevices();
    return all.filter(d => d.kind === "videoinput");
  } catch (e) {
    return [];
  }
}

async function refreshCameras() {
  const sel = el("cam-device");
  if (!sel) return 0;
  const prev = sel.value;
  const cams = await listCameras();
  sel.innerHTML = '<option value="">默认设备</option>';
  cams.forEach((c, i) => {
    const o = document.createElement("option");
    o.value = c.deviceId;
    // 未授权时 label 是空的，只能按序号叫
    o.textContent = c.label || t("cam.deviceN", { n: i + 1 });
    sel.appendChild(o);
  });
  if (prev && [...sel.options].some(o => o.value === prev)) sel.value = prev;
  return cams.length;
}

/* ------------------------------------------------------- MediaPipe */

async function ensureLandmarker() {
  if (landmarker) return landmarker;
  setState(t("cam.st.loading"));
  await loadMediapipe();
  const vision = await FilesetResolver.forVisionTasks(`${MP_BASE}/wasm`);
  const base = { modelAssetPath: `${MP_BASE}/hand_landmarker.task` };
  const opts = (delegate) => ({
    baseOptions: { ...base, delegate },
    runningMode: "VIDEO",
    numHands: 1,
  });
  try {
    landmarker = await HandLandmarker.createFromOptions(vision, opts("GPU"));
  } catch (e) {
    console.warn("MediaPipe GPU delegate 不可用，改用 CPU：", e);
    setState(t("cam.st.loadingCpu"));
    landmarker = await HandLandmarker.createFromOptions(vision, opts("CPU"));
  }
  return landmarker;
}

/* ------------------------------------------------------- 启动 / 停止 */

async function start() {
  // ---------- 0) 先把机械手恢复到中位 ----------
  // 摄像头一开就会开始下发，如果手还停在刚才的姿势上会被猛地拽走。
  // 先回中位，让手和画面都从同一个已知状态开始。
  if (window.AH?.connected()) {
    setState(t("cam.st.home"));
    say(t("cam.say.home"));
    window.AH.middle();
    await new Promise(r => setTimeout(r, 900));
    say("");
  }

  // ---------- 1) 再开摄像头 ----------
  if (!stream) {
    if (!navigator.mediaDevices?.getUserMedia) {
      setState(t("cam.st.unsupported"), "err");
      say(t("cam.say.noApi") + window.isSecureContext);
      return;
    }

    setState(t("cam.st.asking"));
    say(t("cam.say.asking"));
    const devId = el("cam-device")?.value || "";
    const constraints = {
      video: devId
        ? { deviceId: { exact: devId }, width: { ideal: 640 }, height: { ideal: 480 } }
        : { width: { ideal: 640 }, height: { ideal: 480 } },
      audio: false,
    };

    try {
      stream = await navigator.mediaDevices.getUserMedia(constraints);
    } catch (e) {
      setState(t("cam.st.failed"), "err");
      const hint = {
        NotAllowedError: t("cam.say.denied"),
        PermissionDeniedError: t("cam.say.denied"),
        NotFoundError: t("cam.say.unplugged"),
        NotReadableError: t("cam.say.busy"),
        OverconstrainedError: t("cam.say.overconstrained"),
        SecurityError: t("cam.say.insecure"),
      }[e.name] || t("cam.say.unknownReason");
      say(t("cam.say.openFailed", { name: e.name, message: e.message, hint }));
      return;
    }

    const v = el("video");
    v.srcObject = stream;
    try { await v.play(); } catch (e) { /* autoplay 兜底 */ }
    setStageIdle(false);
    resetCal();              // 重开摄像头就重新采

    // 拿到权限后 label 才可读，重列一次
    await refreshCameras();
    const track = stream.getVideoTracks()[0];
    const st = track.getSettings ? track.getSettings() : {};
    setRes(`${st.width || v.videoWidth || "?"}×${st.height || v.videoHeight || "?"}`);
    setState(t("cam.st.ready"));
  }

  el("btn-cam-start").disabled = true;
  el("btn-cam-stop").disabled = false;

  // ---------- 2) 再加载模型 ----------
  if (!landmarker) {
    say(t("cam.say.loadingModel"));
    try {
      await ensureLandmarker();
    } catch (e) {
      setState(t("cam.st.modelFailed"), "err");
      say(t("cam.say.modelFailed", { err: e.message || e }));
      return;
    }
  }

  // ---------- 3) 识别循环 ----------
  setState(t("cam.st.tracking"), "ok");
  say(t("cam.say.tracking"));

  const video = el("video");
  const canvas = el("overlay");
  const ctx = canvas.getContext("2d");
  const drawer = new DrawingUtils(ctx);

  const loop = () => {
    if (!stream) return;                       // 已停止
    if (video.readyState >= 2) {
      if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
      }
      let res;
      try {
        res = landmarker.detectForVideo(video, performance.now());
      } catch (e) {
        setState(t("cam.st.trackError"), "err");
        say(t("cam.say.trackError", { err: e.message || e }));
        return;
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const hands = res.landmarks || [];
      // worldLandmarks 是米制、以手为中心的 3D 坐标，侧摆要用它（见 handFrame 的说明）。
      // 有些版本字段叫 handedness，有些叫 handednesses，两个都认。
      const worldHands = res.worldLandmarks || [];
      const handed = (res.handedness || res.handednesses || [])[0];
      const handLabel = handed?.[0]?.categoryName || handed?.[0]?.displayName || "Right";
      lastCount = hands.length;

      if (hands.length && el("cam-draw").checked !== false) {
        for (const lm of hands) {
          for (const [k, seg] of Object.entries(BONE_GROUPS)) {
            if (!seg.length) continue;
            const thin = (k === "pinky" || k === "palm");
            drawer.drawConnectors(lm, seg, {
              color: k === "palm" ? PALM_COLOR : FINGER_BONES[k].color,
              lineWidth: thin ? 2 : 3,
            });
          }
          drawer.drawLandmarks(lm, { color: "#22c55e", radius: 3 });
        }
      }

      // 简单 FPS
      const now = performance.now();
      fpsN++;
      if (now - fpsT > 1000) {
        const who = lastCount
          ? " · " + t(handLabel === "Left" ? "hand.left" : "hand.right")
          : "";
        setDetect(`${t("cam.say.handCount", { n: lastCount })} · ` +
                  `${Math.round(fpsN * 1000 / (now - fpsT))} fps${who}`);
        fpsT = now; fpsN = 0;
      }
      if (!fpsT) fpsT = now;

      if (hands.length) {
        const angles = toAngles(hands[0], worldHands[0] || hands[0], handLabel);
        if (!angles) {
          // 采集期间 toAngles 返回 null —— 不下发，手保持在中位不动
          setSend(t("cam.send.captureIncomplete"));
          say(t("cam.say.capturing"));
        } else {
          const sent = window.AH ? window.AH.sendAngles(angles) : false;
          const who = t(window.AH?.target() === "left" ? "hand.left" : "hand.right");
          setSend(sent ? t("cam.send.connected", { hand: who }) : t("cam.send.disconnected"));
          say(Object.entries(angles)
            .map(([k, v]) => {
              const base = (v[0] + v[1]) / 2, side = (v[0] - v[1]) / 2;
              return `  ${fingerLabel(k).padEnd(8)} ${t("axis.flexion")} ` +
                     `${String(Math.round(base)).padStart(4)}   ` +
                     `${t("axis.spread")} ${String(Math.round(side)).padStart(4)}`;
            }).join("\n"));
        }
      } else {
        setSend("—");
        say(t("cam.noHand"));
      }
    }
    rafId = requestAnimationFrame(loop);
  };
  loop();
}

function stop() {
  if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
  const v = el("video");
  if (v) v.srcObject = null;
  const c = el("overlay");
  if (c) c.getContext("2d").clearRect(0, 0, c.width, c.height);
  setStageIdle(true);
  setState(t("cam.st.idle"));
  setRes("—"); setDetect("—"); setSend("—");
  say("");
  el("btn-cam-start").disabled = false;
  el("btn-cam-stop").disabled = true;
}

/* ------------------------------------------------------- 绑定 */

el("btn-cam-start").onclick = start;
el("btn-cam-stop").onclick = stop;
el("btn-cam-refresh").onclick = async () => {
  const n = await refreshCameras();
  say(n ? t("cam.say.foundCams", { n }) : t("cam.say.noCams"));
};

/* 切换语言后重刷动态文案：采集行、状态行、下拉框里的默认项 */
window.I18N.onChange(() => {
  renderCal();
  setState(t("cam.st.idle"));
  refreshCameras().catch(() => {});
});

function renderCal() {
  const box = el("cal-buttons");
  const stepEl = el("cal-step");
  const barEl = el("cal-bar-fill");
  const stateEl = el("cal-state");
  if (!stateEl) return;

  if (box) {
    box.innerHTML = "";
    for (const st of STAGES) {
      const done = !!collected[st.id];
      const busy = capTarget === st.id;
      const b = document.createElement("button");
      b.textContent = (done ? "✓ " : "") + t("cal.btn." + st.id);
      b.title = t("cal.stage." + st.id);
      b.className = busy ? "busy" : (done ? "done" : "");
      b.disabled = !!capTarget;
      b.onclick = () => startCapture(st.id);
      box.appendChild(b);
    }
  }

  const n = Object.keys(collected).length;
  if (barEl) {
    const partial = capTarget ? capN / CAP_FRAMES : 0;
    barEl.style.width = `${Math.round((n + partial) / STAGES.length * 100)}%`;
  }

  // 提示正在采的、否则提示下一个还没采的
  const next = capTarget ? STAGES.find(s => s.id === capTarget)
                         : STAGES.find(s => !collected[s.id]);
  if (stepEl) stepEl.textContent = next ? t("cal.stage." + next.id) : t("cal.allDone");

  if (cal) {
    stateEl.textContent = t("cal.ready");
    stateEl.style.color = "var(--ok)";
  } else if (capTarget) {
    stateEl.textContent = t("cal.capturing");
    stateEl.style.color = "var(--warn)";
  } else {
    stateEl.textContent = t("cal.pending", { n, total: STAGES.length });
    stateEl.style.color = "var(--warn)";
  }
}

setStageIdle(true);
setState(t("cam.st.idle"));
renderCal();
refreshCameras().catch(() => {});
