#!/usr/bin/env node
/* PWM 协议黄金用例（Node，不依赖浏览器）
 *
 * 运行：
 *   node Amazinghand-web-io/tools/pwm_protocol_test.mjs
 *
 * 校验 buildFrame 与固件手册示例逐字节一致，并检查姿态→PWM 角度的基准值。
 */
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";

const here = path.dirname(fileURLToPath(import.meta.url));
const webDir = path.resolve(here, "..");

const ctx = { window: {}, console };
vm.createContext(ctx);
for (const file of ["common.js", "pwm.js"]) {
  vm.runInContext(fs.readFileSync(path.join(webDir, file), "utf8"), ctx, { filename: file });
}

const C = ctx.window.AH_COMMON;
const P = ctx.window.AH_PWM._protocol;
assert.ok(C, "common.js 未导出 AH_COMMON");
assert.ok(P, "pwm.js 未导出 AH_PWM._protocol");

const hex = (u8) => [...u8].map((b) => b.toString(16).padStart(2, "0").toUpperCase()).join(" ");
const eqFrame = (cmd, data, expected) => {
  const got = hex(P.buildFrame(cmd, data));
  assert.equal(got, expected, `frame 0x${cmd.toString(16)}`);
  console.log(`  ✓ ${got}`);
};

console.log("PWM 帧黄金用例：");
eqFrame(0x00, [], "AA 00 00 00");
eqFrame(0xf0, new Array(8).fill(0x5a), "AA F0 08 5A 5A 5A 5A 5A 5A 5A 5A F8");
eqFrame(0xf1, [0x01], "AA F1 01 01 F1");
eqFrame(0xf1, [0x02], "AA F1 01 02 F2");
eqFrame(0xff, [], "AA FF 00 FF");

/* 构造与 config.json 等价的最小配置 */
const fingers = [
  { key: "ring", ids: [5, 6] },
  { key: "middle", ids: [3, 4] },
  { key: "pointer", ids: [1, 2] },
  { key: "thumb", ids: [7, 8] },
];
const cfg = {
  pwm: {
    middle_deg: 90,
    channels: { pointer: [1, 2], middle: [3, 4], ring: [5, 6], thumb: [7, 8] },
    calibration: { right: {}, left: {} },
  },
};
const hand = { key: "right", mirror_pose: true, fingers };
const handL = { key: "left", mirror_pose: true, fingers };

console.log("PWM 姿态→角度基准：");
const check = (label, positions, expected) => {
  const got = Array.from(C.poseToPwmAngles(cfg, hand, positions));
  assert.deepEqual(got, expected, label);
  console.log(`  ✓ ${label}: [${got.join(", ")}]`);
};

check("middle -17.578", new Array(8).fill(-17.578),
      [108, 72, 108, 72, 108, 72, 108, 72]);
check("close 75/18", [75, 75, 75, 75, 75, 75, 18, 18],
      [15, 165, 15, 165, 15, 165, 72, 108]);
check("open -35", new Array(8).fill(-35),
      [125, 55, 125, 55, 125, 55, 125, 55]);

/* 左手 mirror + 非对称姿态：交换每指两个值后再换算 */
const left = Array.from(C.poseToPwmAngles(cfg, handL, [10, -20, 10, -20, 10, -20, 10, -20]));
assert.deepEqual(left, [110, 100, 110, 100, 110, 100, 110, 100], "left mirror");
console.log(`  ✓ left mirror: [${left.join(", ")}]`);

console.log("全部通过。");
