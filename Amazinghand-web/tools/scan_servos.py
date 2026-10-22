#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描总线上有哪些 SCS0009 舵机，并核对配置里的 ID。

用途：接线完成后先跑一遍，确认每只手 8 个舵机都在、ID 与 config.json 一致。
反过来，如果某条手指不动，也能立刻看出是 ID 写错了还是舵机没响应。

用法：
    python tools/scan_servos.py --port COM5
    python tools/scan_servos.py                 # 自动探测串口
    python tools/scan_servos.py --range 1 20    # 指定扫描范围
"""

import argparse
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT.parent / "Amazinghand-web-io" / "config.json"   # 与前端共用同一份配置


def detect_port():
    try:
        from serial.tools import list_ports
    except Exception:
        return ""
    ports = list(list_ports.comports())
    if not ports:
        return ""
    for p in ports:
        d = ((p.description or "") + " " + (p.hwid or "")).lower()
        if any(k in d for k in ("ch340", "ch341", "cp210", "ft232", "acm", "usb serial")):
            return p.device
    return ports[0].device


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", "-p", default="")
    ap.add_argument("--baudrate", type=int, default=1000000)
    ap.add_argument("--range", nargs=2, type=int, default=[1, 20],
                    metavar=("MIN", "MAX"))
    ap.add_argument("--torque-off", action="store_true",
                    help="扫完把所有舵机力矩关掉")
    args = ap.parse_args()

    try:
        from rustypot import Scs0009PyController
    except ImportError:
        print("缺少 rustypot，请先 pip install -r requirements.txt")
        return 1

    port = args.port or detect_port()
    if not port:
        print("没找到串口，请用 --port 指定")
        return 1

    lo, hi = args.range
    print(f"扫描 {port} 上的 SCS0009，ID {lo}~{hi} …\n")

    ctrl = Scs0009PyController(
        serial_port=port, baudrate=args.baudrate, timeout=0.2)

    found = []
    for sid in range(lo, hi + 1):
        try:
            pos = ctrl.read_present_position(sid)
            found.append(sid)
            print(f"  ✅ ID {sid:>3}  当前位置 {pos:+.4f} rad")
        except Exception:
            pass

    print()
    if not found:
        print("一个都没扫到。检查：供电、波特率 1000000、A/B 线是否接反。")
        return 1

    # 与配置核对
    with io.open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)

    print("与 config.json 核对：")
    ok = True
    for hkey, h in cfg["hands"].items():
        want = [j["id"] for fg in h["fingers"] for j in fg["joints"]]
        missing = [i for i in want if i not in found]
        status = "✅ 齐全" if not missing else f"❌ 缺 {missing}"
        if missing:
            ok = False
        print(f"  {h['label']:<4} 需要 {want}")
        print(f"       {status}")

    extra = [i for i in found if i not in
             [j["id"] for h in cfg["hands"].values()
              for fg in h["fingers"] for j in fg["joints"]]]
    if extra:
        print(f"  总线上还有未配置的 ID: {extra}")

    if args.torque_off:
        ctrl.sync_write_torque_enable(found, [0] * len(found))
        print("\n已关闭全部力矩。")

    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
