/* AmazingHand 网页控制 —— 前后端共用逻辑（SCS0009 / PWM 两种驱动）
 *
 * 这个文件只放纯函数：配置加载、姿态换算、角度合并、串口描述。
 * io.js（SCS0009）和 pwm.js（ESP32 直驱）都从这里取，保证“换算公式只有一份实现”。
 *
 * 加载顺序：common.js → io.js → pwm.js → app.js
 */
(function () {
  "use strict";

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

  async function loadConfig(url) {
    const res = await fetch(url || "./config.json", { cache: "no-cache" });
    if (!res.ok) throw new Error(`config.json HTTP ${res.status}`);
    return stripComments(await res.json());
  }

  /** 从 config 构建 left/right 手对象（附带 key / servo_ids / torque）。 */
  function buildHands(cfg) {
    const hands = {};
    for (const [k, h] of Object.entries(cfg.hands || {})) {
      if (k !== "left" && k !== "right") continue;
      const servoIds = h.fingers.flatMap((f) => f.ids);
      hands[k] = { ...h, key: k, servo_ids: servoIds, torque: false };
    }
    return hands;
  }

  /* ---------------- 姿态 ---------------- */

  const clampPose = (limits, v) =>
    Math.max(limits.pose_min_deg, Math.min(limits.pose_max_deg, Number(v)));

  /** 姿态可能按手给了不同数组（pose.right / pose.left），否则用 positions。 */
  function posePositions(pose, hand) {
    return pose[hand] || pose.positions;
  }

  /** 把 {fingerKey:[v1,v2]} 合并进当前 8 值姿态数组，返回新数组。 */
  function mergeAngles(hands, current, hand, angles) {
    const out = [...current[hand]];
    hands[hand].fingers.forEach((f, fi) => {
      const v = angles[f.key];
      if (Array.isArray(v) && v.length === 2) {
        out[fi * 2] = Number(v[0]);
        out[fi * 2 + 1] = Number(v[1]);
      }
    });
    return out;
  }

  /* ---------------- SCS0009 换算 ----------------
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

  /* ---------------- PWM 换算 ----------------
   * 固件差动约定：move_finger(pos1,pos2) → (90−pos1, 90−pos2)。
   * 因此每根手指第一个通道取 −，第二个通道取 +：
   *   angle = middle_deg + dir × scale × pose + offset_deg
   * 默认 middle=90 / scale=1 / offset=0，即直接镜像舵机轴角度。
   * mirror_pose 为真时先交换每指两个姿态值（左手）。
   *
   * 通道分配来自 config.pwm.channels，按手指 key 对应：
   *   pointer→[1,2], middle→[3,4], ring→[5,6], thumb→[7,8]
   */
  function clampAngle(v) {
    return Math.max(0, Math.min(180, Math.round(v)));
  }

  function poseToPwmAngles(cfg, hand, positions) {
    const pwm = cfg.pwm || {};
    const middle = Number(pwm.middle_deg ?? 90);
    const channels = pwm.channels || {
      pointer: [1, 2], middle: [3, 4], ring: [5, 6], thumb: [7, 8],
    };
    const calibration = (pwm.calibration || {})[hand.key] || {};

    const pos = positions.map(Number);
    if (hand.mirror_pose) {
      for (let i = 0; i < hand.fingers.length; i++) {
        const a = i * 2;
        [pos[a], pos[a + 1]] = [pos[a + 1], pos[a]];
      }
    }

    const angles = new Array(8).fill(clampAngle(middle));
    hand.fingers.forEach((finger, i) => {
      const ch = channels[finger.key];
      if (!ch || ch.length !== 2) return;
      const cal = calibration[finger.key] || {};
      const scale = Number(cal.scale ?? 1);
      const off = cal.offset_deg || [0, 0];
      const v0 = pos[i * 2], v1 = pos[i * 2 + 1];
      angles[ch[0] - 1] = clampAngle(middle - scale * v0 + Number(off[0] || 0));
      angles[ch[1] - 1] = clampAngle(middle + scale * v1 + Number(off[1] || 0));
    });
    return angles;
  }

  /* ---------------- 串口描述 ---------------- */

  const LIKELY_VIDS = new Set([0x1a86, 0x10c4, 0x0403, 0x067b, 0x2341, 0x2e8a]);

  /** Web Serial 的端口没有系统名，用 VID:PID + 序号生成稳定显示名。 */
  function describePort(port, index) {
    const info = port.getInfo ? port.getInfo() : {};
    const vid = info.usbVendorId;
    const pid = info.usbProductId;
    const hex = (n) => (n === undefined ? "????" : n.toString(16).padStart(4, "0"));
    const name = `USB ${hex(vid)}:${hex(pid)} #${index + 1}`;
    const likely = vid !== undefined && LIKELY_VIDS.has(vid);
    return { name, label: likely ? `${name} ★` : name, likely };
  }

  window.AH_COMMON = {
    stripComments,
    loadConfig,
    buildHands,
    clampPose,
    posePositions,
    mergeAngles,
    poseToServoGoals,
    poseToPwmAngles,
    clampAngle,
    describePort,
    LIKELY_VIDS,
  };
})();
