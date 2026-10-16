/* AmazingHand 网页控制 —— 中英文切换
 *
 * 用法：
 *   I18N.t("key")                  取当前语言的文案
 *   I18N.t("key", {n: 3})          带占位符，词典里写 {n}
 *   I18N.pick("pose", name, label) 翻译 config.json 来的名字，翻不到就退回原值
 *   <el data-i18n="key">           静态文案，apply() 会自动填 textContent
 *   <el data-i18n-html="key">      带 <strong>/<br> 的，走 innerHTML
 *   <el data-i18n-title="key">     title 属性
 *   I18N.onChange(fn)              语言变了通知重渲染（动态生成的文案要靠它）
 *
 * 这是普通脚本（不是 ES 模块），在 app.js 之前加载，tracking.js 里用 window.I18N 取。
 */
(function () {
  "use strict";

  const LS_KEY = "ah_lang";

  const DICT = {
    zh: {
      "doc.title": "AmazingHand 网页控制",
      "app.title": "AmazingHand 控制台",

      "conn.off": "未连接",
      "conn.on": "已连接",

      "port.label": "串口",
      "port.detecting": "检测中…",
      "port.refresh": "刷新",
      "port.refreshTitle": "重新扫描串口",
      "port.connect": "连接",
      "port.reconnect": "重连",
      "port.disconnect": "断开",
      "port.none": "未检测到串口",
      "port.dryRun": "（--dry-run，未启用串口）",
      "port.scanning": "扫描中…",
      "port.connecting": "正在连接 {port} …",
      "port.disconnecting": "正在断开…",
      "port.connected": "已连接 {port}",
      "port.dryRunHint": "dry-run 模式：界面可用，不下发串口",
      "port.pick": "未连接 —— 选好串口后点「连接」",
      "port.plugIn": "未检测到串口，插好控制板后点「刷新」",
      "port.error": "出错了",

      "target.label": "控制对象",
      "hand.right": "右手",
      "hand.left": "左手",

      "tab.manual": "手动控制",
      "tab.camera": "摄像头互动遥控",

      "finger.ring": "无名指",
      "finger.middle": "中指",
      "finger.pointer": "食指",
      "finger.thumb": "拇指",

      "axis.flexion": "屈伸",
      "axis.spread": "侧摆",
      "axis.flexionHint": "张开 ↔ 握紧",
      "axis.spreadHint": "左 ↔ 右",

      "manual.poses": "预设姿态",
      "manual.actions": "操作",
      "btn.middle": "全部回中位",
      "btn.torqueRelease": "松开力矩",
      "btn.torqueEnable": "开启力矩",
      "btn.stop": "急停（全部松开）",

      "cam.label": "摄像头",
      "cam.defaultDevice": "默认设备",
      "cam.deviceN": "摄像头 {n}",
      "cam.refresh": "刷新",
      "cam.refreshTitle": "重新列出摄像头",
      "cam.start": "启动",
      "cam.stop": "停止",
      "cam.skeleton": "骨骼",
      "legend.title": "骨骼配色：手掌是中性灰，小拇指是暗色",
      "legend.thumb": "拇",
      "legend.index": "食",
      "legend.middle": "中",
      "legend.ring": "无",
      "legend.pinky": "小",

      "cal.label": "采集",
      "cal.pending": "待采集 {n}/{total}",
      "cal.capturing": "采集中…",
      "cal.ready": "已就绪 ✓",
      "cal.allDone": "三个姿势都采完了",
      "cal.btn.spread": "① 伸直张开",
      "cal.btn.together": "② 伸直合拢",
      "cal.btn.fist": "③ 握拳",
      "cal.stage.spread": "手指伸直张开，大拇指向外",
      "cal.stage.together": "手指伸直合拢，大拇指贴合食指",
      "cal.stage.fist": "握拳，大拇指贴近掌心",
      "cal.hintHtml":
        "<strong>用法</strong>：点「启动」→ 机械手先回到中位 → 摄像头打开 →" +
        "<strong>摆好一个姿势，点对应的按钮采一次</strong>（保持约 1 秒）。" +
        "三个都采完状态变绿就能用了，顺序随意；采错了点同一个按钮重采。" +
        "<br>" +
        "<strong>①手指伸直张开，大拇指向外　②手指伸直合拢，大拇指贴合食指　③握拳，大拇指贴近掌心</strong>" +
        "<br>" +
        "<strong>大拇指只做屈伸，不左右摆</strong> —— 它的对掌关节弯曲和侧摆耦合太紧，" +
        "硬拆成两根轴两根都不准。拇指要的两个姿势就是 ①（指外）和 ③（指向掌心）。",

      "cam.placeholder1": "摄像头未启动",
      "cam.placeholder2": "点上面的「启动」，浏览器会询问权限 —— 选「允许」",
      "cam.row.state": "状态",
      "cam.row.res": "分辨率",
      "cam.row.detect": "识别",
      "cam.row.send": "下发",
      "cam.st.idle": "未启动",
      "cam.noHand": "没检测到手 —— 把手掌正对镜头，光线别太暗。",

      "cam.st.loading": "加载模型…",
      "cam.st.loadingCpu": "加载模型（CPU）…",
      "cam.st.home": "回中位…",
      "cam.st.unsupported": "不支持",
      "cam.st.asking": "请求权限…",
      "cam.st.failed": "失败",
      "cam.st.ready": "画面就绪",
      "cam.st.modelFailed": "模型失败",
      "cam.st.tracking": "识别中",
      "cam.st.trackError": "识别出错",
      "cam.st.captureIncomplete": "采集未完成",

      "cam.say.home": "先把机械手恢复到中位，稍等…",
      "cam.say.noApi":
        "这个浏览器不支持摄像头 API。\n" +
        "请用 Chrome / Edge，并且要经 http://localhost 打开（不能用局域网 IP，那种情况浏览器不给摄像头权限）。\n" +
        "secureContext = ",
      "cam.say.asking": "正在向浏览器申请摄像头权限…",
      "cam.say.openFailed": "打不开摄像头：{name}\n{message}\n\n{hint}",
      "cam.say.unknownReason": "未知原因。",
      "cam.say.unplugged": "没找到摄像头设备。检查设备是否插好/启用。",
      "cam.say.busy": "摄像头被别的程序占用了（相机 App、其他浏览器标签、会议软件）。关掉它们再试。",
      "cam.say.overconstrained": "选的这个摄像头用不了，换一个设备试试。",
      "cam.say.insecure": "当前不是安全上下文。必须用 http://localhost 打开。",
      "cam.say.denied": "浏览器拒绝了权限。点地址栏左边的摄像头图标 → 允许，然后刷新页面。",
      "cam.say.loadingModel": "画面已就绪，正在加载识别模型…（第一次约几秒）",
      "cam.say.modelFailed":
        "MediaPipe 加载失败：{err}\n" +
        "请确认 web/mediapipe/ 下有 vision_bundle.mjs、wasm/ 和 hand_landmarker.task。\n" +
        "画面正常，只是不做识别。",
      "cam.say.tracking": "识别中…把手掌正对镜头。",
      "cam.say.trackError": "识别出错：{err}",
      "cam.say.capturing": "正在采集参考姿态，采完自动开始识别。\n按提示摆好当前步骤的姿势，保持约 1 秒。",
      "cam.say.foundCams": "找到 {n} 个摄像头。",
      "cam.say.noCams": "没列出摄像头（可能还没授权，先点「启动」）。",
      "cam.say.startFirst": "先点上面的「启动」打开摄像头，再采集。",
      "cam.say.handCount": "{n} 只手",
      "cam.send.connected": "已连 {hand}",
      "cam.send.disconnected": "未连接",
      "cam.send.captureIncomplete": "采集未完成",
      "cam.scriptFailed": "脚本加载失败：{src}\n请刷新页面重试。",

      "footer.text":
        "舵机映射：右手 无名指 5,6 / 中指 3,4 / 食指 1,2 / 拇指 7,8；左手对应 11,12 / 13,14 / 15,16 / 17,18。<br>" +
        "换算 servo = (ID 奇数 ? +1 : -1) × (姿态值 − 手偏移)。",

      "pose.open": "张开",
      "pose.close": "握拳",
      "pose.ok": "OK",
      "pose.greeting": "打招呼",
      "pose.victory": "剪刀手",
      "pose.two": "二",
      "pose.paper": "布",
      "pose.stone": "石头",
      "pose.scissors": "剪刀",
      "pose.wave1": "挥手",
      "pose.wave_r": "右摆",
      "pose.wave_l": "左摆",
      "pose.ring_close": "仅无名指握",
      "pose.middle_close": "仅中指握",
      "pose.pointer_close": "仅食指握",
      "pose.thumb_close": "仅拇指握",
      "pose.one": "一",
      "pose.three": "三",
      "pose.hifive": "击掌"
    },

    en: {
      "doc.title": "AmazingHand Web Control",
      "app.title": "AmazingHand Console",

      "conn.off": "Disconnected",
      "conn.on": "Connected",

      "port.label": "Port",
      "port.detecting": "Detecting…",
      "port.refresh": "Refresh",
      "port.refreshTitle": "Rescan serial ports",
      "port.connect": "Connect",
      "port.reconnect": "Reconnect",
      "port.disconnect": "Disconnect",
      "port.none": "No serial port found",
      "port.dryRun": "(--dry-run, serial disabled)",
      "port.scanning": "Scanning…",
      "port.connecting": "Connecting to {port} …",
      "port.disconnecting": "Disconnecting…",
      "port.connected": "Connected to {port}",
      "port.dryRunHint": "dry-run mode: UI works, nothing is sent to the serial port",
      "port.pick": "Not connected — pick a port, then click Connect",
      "port.plugIn": "No serial port found. Plug in the board, then click Refresh",
      "port.error": "Error",

      "target.label": "Target",
      "hand.right": "Right hand",
      "hand.left": "Left hand",

      "tab.manual": "Manual",
      "tab.camera": "Camera Teleop",

      "finger.ring": "Ring",
      "finger.middle": "Middle",
      "finger.pointer": "Index",
      "finger.thumb": "Thumb",

      "axis.flexion": "Flex",
      "axis.spread": "Splay",
      "axis.flexionHint": "open ↔ closed",
      "axis.spreadHint": "left ↔ right",

      "manual.poses": "Poses",
      "manual.actions": "Actions",
      "btn.middle": "All to middle",
      "btn.torqueRelease": "Release torque",
      "btn.torqueEnable": "Enable torque",
      "btn.stop": "E-STOP (release all)",

      "cam.label": "Camera",
      "cam.defaultDevice": "Default device",
      "cam.deviceN": "Camera {n}",
      "cam.refresh": "Refresh",
      "cam.refreshTitle": "Re-list cameras",
      "cam.start": "Start",
      "cam.stop": "Stop",
      "cam.skeleton": "Skeleton",
      "legend.title": "Bone colors: palm is neutral grey, pinky is dim",
      "legend.thumb": "T",
      "legend.index": "I",
      "legend.middle": "M",
      "legend.ring": "R",
      "legend.pinky": "P",

      "cal.label": "Capture",
      "cal.pending": "{n}/{total} captured",
      "cal.capturing": "Capturing…",
      "cal.ready": "Ready ✓",
      "cal.allDone": "All three poses captured",
      "cal.btn.spread": "① Spread",
      "cal.btn.together": "② Together",
      "cal.btn.fist": "③ Fist",
      "cal.stage.spread": "Fingers straight and spread, thumb pointing outward",
      "cal.stage.together": "Fingers straight and together, thumb against the index finger",
      "cal.stage.fist": "Make a fist, thumb tucked toward the palm",
      "cal.hintHtml":
        "<strong>How to use</strong>: click Start → the hand returns to middle → the camera opens → " +
        "<strong>pose your hand, then click that pose's capture button</strong> (hold about 1 second). " +
        "All three must be captured before the status turns green. Order doesn't matter; " +
        "click a button again to re-capture that pose." +
        "<br>" +
        "<strong>① fingers straight and spread, thumb outward　② fingers straight and together, thumb against the index finger　③ make a fist, thumb tucked toward the palm</strong>" +
        "<br>" +
        "<strong>The thumb only flexes — it never splays.</strong> Its CMC is a saddle joint, so flexion and " +
        "abduction are too tightly coupled to split into two axes. The thumb needs just two of these poses: " +
        "① (outward) and ③ (toward the palm).",

      "cam.placeholder1": "Camera not started",
      "cam.placeholder2": "Click Start above; the browser will ask for permission — choose Allow",
      "cam.row.state": "State",
      "cam.row.res": "Resolution",
      "cam.row.detect": "Detect",
      "cam.row.send": "Sending",
      "cam.st.idle": "Not started",
      "cam.noHand": "No hand detected — face your palm at the camera, and keep the light reasonable.",

      "cam.st.loading": "Loading model…",
      "cam.st.loadingCpu": "Loading model (CPU)…",
      "cam.st.home": "Returning to middle…",
      "cam.st.unsupported": "Unsupported",
      "cam.st.asking": "Requesting permission…",
      "cam.st.failed": "Failed",
      "cam.st.ready": "Video ready",
      "cam.st.modelFailed": "Model failed",
      "cam.st.tracking": "Tracking",
      "cam.st.trackError": "Tracking error",
      "cam.st.captureIncomplete": "Capture incomplete",

      "cam.say.home": "Returning the hand to middle first, one moment…",
      "cam.say.noApi":
        "This browser has no camera API.\n" +
        "Use Chrome or Edge and open the page over http://localhost (not a LAN IP — browsers withhold " +
        "camera access in that case).\n" +
        "secureContext = ",
      "cam.say.asking": "Asking the browser for camera permission…",
      "cam.say.openFailed": "Could not open the camera: {name}\n{message}\n\n{hint}",
      "cam.say.unknownReason": "Unknown reason.",
      "cam.say.unplugged": "No camera device found. Check that it's plugged in and enabled.",
      "cam.say.busy": "The camera is in use by another program (camera app, another tab, a meeting app). Close them and retry.",
      "cam.say.overconstrained": "The selected camera can't be used. Try another device.",
      "cam.say.insecure": "Not a secure context. The page must be opened over http://localhost.",
      "cam.say.denied": "The browser denied permission. Click the camera icon left of the address bar → Allow, then reload the page.",
      "cam.say.loadingModel": "Video is ready; loading the recognition model… (a few seconds the first time)",
      "cam.say.modelFailed":
        "MediaPipe failed to load: {err}\n" +
        "Check that web/mediapipe/ contains vision_bundle.mjs, wasm/ and hand_landmarker.task.\n" +
        "The video works; only recognition is off.",
      "cam.say.tracking": "Tracking… face your palm at the camera.",
      "cam.say.trackError": "Tracking error: {err}",
      "cam.say.capturing": "Capturing reference poses; recognition starts once they're done.\nHold the pose for the current step for about 1 second.",
      "cam.say.foundCams": "Found {n} camera(s).",
      "cam.say.noCams": "No cameras listed (permission may not be granted yet — click Start first).",
      "cam.say.startFirst": "Click Start above to open the camera before capturing.",
      "cam.say.handCount": "{n} hand(s)",
      "cam.send.connected": "Sending to {hand}",
      "cam.send.disconnected": "Not connected",
      "cam.send.captureIncomplete": "Capture incomplete",
      "cam.scriptFailed": "Script failed to load: {src}\nPlease reload the page.",

      "footer.text":
        "Servo map: right hand ring 5,6 / middle 3,4 / index 1,2 / thumb 7,8; " +
        "left hand 11,12 / 13,14 / 15,16 / 17,18.<br>" +
        "servo = (odd ID ? +1 : -1) × (pose value − hand offset).",

      "pose.open": "Open",
      "pose.close": "Fist",
      "pose.ok": "OK",
      "pose.greeting": "Greeting",
      "pose.victory": "Victory",
      "pose.two": "Two",
      "pose.paper": "Paper",
      "pose.stone": "Rock",
      "pose.scissors": "Scissors",
      "pose.wave1": "Wave",
      "pose.wave_r": "Swipe right",
      "pose.wave_l": "Swipe left",
      "pose.ring_close": "Ring only",
      "pose.middle_close": "Middle only",
      "pose.pointer_close": "Index only",
      "pose.thumb_close": "Thumb only",
      "pose.one": "One",
      "pose.three": "Three",
      "pose.hifive": "High five"
    }
  };

  let lang = localStorage.getItem(LS_KEY);
  if (lang !== "zh" && lang !== "en") lang = "zh";

  const listeners = [];

  /** 取文案。vars 里的键会替换词典里的 {键}。 */
  function t(key, vars) {
    let s = (DICT[lang] && DICT[lang][key]);
    if (s === undefined) s = DICT.zh[key];       // 漏翻就退回中文，至少不是 undefined
    if (s === undefined) return key;             // 两边都没有，返回 key 方便定位
    if (vars) {
      for (const k of Object.keys(vars)) {
        s = s.split("{" + k + "}").join(String(vars[k]));
      }
    }
    return s;
  }

  /** 翻译 config.json 来的名字（姿态/手指/手）。翻不到就退回 config 自己的 label。 */
  function pick(kind, key, fallback) {
    const s = DICT[lang] && DICT[lang][kind + "." + key];
    if (s !== undefined) return s;
    return fallback !== undefined ? fallback : key;
  }

  /** 把 root 子树里所有带 data-i18n 标记的元素刷一遍。 */
  function apply(root) {
    const scope = root || document;
    scope.querySelectorAll("[data-i18n]").forEach((n) => {
      n.textContent = t(n.dataset.i18n);
    });
    scope.querySelectorAll("[data-i18n-html]").forEach((n) => {
      n.innerHTML = t(n.dataset.i18nHtml);
    });
    scope.querySelectorAll("[data-i18n-title]").forEach((n) => {
      n.title = t(n.dataset.i18nTitle);
    });
  }

  function renderSwitch() {
    document.querySelectorAll(".lang-switch button").forEach((b) => {
      b.classList.toggle("active", b.dataset.lang === lang);
    });
  }

  function setLang(next) {
    if (next !== "zh" && next !== "en") return;
    if (next === lang) return;
    lang = next;
    localStorage.setItem(LS_KEY, lang);
    applyMeta();
    apply();
    renderSwitch();
    listeners.forEach((fn) => { try { fn(lang); } catch (e) { console.error(e); } });
  }

  function applyMeta() {
    document.documentElement.lang = lang === "en" ? "en" : "zh-CN";
    document.title = t("doc.title");
  }

  function mount() {
    const box = document.getElementById("lang-switch");
    if (!box) return;
    box.innerHTML = "";
    for (const code of ["zh", "en"]) {
      const b = document.createElement("button");
      b.dataset.lang = code;
      b.textContent = code === "zh" ? "中文" : "EN";
      b.onclick = () => setLang(code);
      box.appendChild(b);
    }
    renderSwitch();
  }

  window.I18N = {
    t, pick, apply, mount,
    lang: () => lang,
    setLang,
    onChange: (fn) => listeners.push(fn),
  };

  applyMeta();
  document.addEventListener("DOMContentLoaded", () => { mount(); apply(); });
  // DOMContentLoaded 已经过了就立刻挂（脚本在 body 末尾，一般不会）
  if (document.readyState !== "loading") { mount(); apply(); }
})();
