#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PWM 协议 / 姿态映射黄金用例（Python，不依赖串口硬件）

运行（从仓库根目录）：

    python Amazinghand-web/tools/verify_pwm_protocol.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import server  # noqa: E402


def check_frame(label, cmd, data, expected_hex):
    got = server.pwm_frame(cmd, data)
    expected = bytes.fromhex(expected_hex)
    assert got == expected, f"{label}: {got.hex(' ').upper()} != {expected_hex}"
    print(f"  OK {label}: {got.hex(' ').upper()}")


def main():
    print("PWM 帧黄金用例：")
    check_frame("NOP", 0x00, b"", "AA 00 00 00")
    check_frame("direct 90°", 0xF0, bytes([0x5A] * 8),
                "AA F0 08 5A 5A 5A 5A 5A 5A 5A 5A F8")
    check_frame("set right", 0xF1, bytes([0x01]), "AA F1 01 01 F1")
    check_frame("set left", 0xF1, bytes([0x02]), "AA F1 01 02 F2")
    check_frame("stop", 0xFF, b"", "AA FF 00 FF")

    cfg, hands, _limits = server.load_config()
    assert cfg.get("driver") in ("scs0009", "pwm")
    assert cfg["pwm"]["channels"]["pointer"] == [1, 2]

    print("PWM 姿态→角度基准：")

    def check_pose(label, hand_key, positions, expected):
        got = server.pose_to_pwm_angles(cfg, hands[hand_key], positions)
        assert got == expected, f"{label}: {got} != {expected}"
        print(f"  OK {label}: {got}")

    check_pose("middle -17.578", "right", cfg["middle"]["positions"],
               [108, 72, 108, 72, 108, 72, 108, 72])
    check_pose("close 75/18", "right", cfg["poses"]["close"]["positions"],
               [15, 165, 15, 165, 15, 165, 72, 108])
    check_pose("open -35", "right", cfg["poses"]["open"]["positions"],
               [125, 55, 125, 55, 125, 55, 125, 55])
    check_pose("left mirror", "left", [10, -20, 10, -20, 10, -20, 10, -20],
               [110, 100, 110, 100, 110, 100, 110, 100])

    print("全部通过。")


if __name__ == "__main__":
    main()
