#!/usr/bin/env python3
"""AmazingHand 串口测试工具 — 自动计算校验和，支持按舵机ID单独控制"""

import serial
import time
import sys

# ============================================================
# 协议常量
# ============================================================
FRAME_HEADER = 0xAA
RESP_HEADER = 0xBB

CMD = {
    "nop":        0x00,
    "rock":       0x01,
    "scissors":   0x02,
    "paper":      0x03,
    "thumbs_up":  0x04,
    "taunt1":     0x05,
    "taunt2":     0x06,
    "open":       0x07,
    "close":      0x08,
    "ok":         0x09,
    "pinch":      0x0A,
    "index":      0x0C,
    "direct":     0xF0,
    "set_side":   0xF1,
    "repeat":     0xFE,
    "stop":       0xFF,
}

STATUS_NAMES = {0x00: "OK", 0x01: "无效命令", 0x02: "参数错误",
                 0x03: "忙",  0x10: "完成"}


# ============================================================
# 校验和
# ============================================================
def checksum(cmd_id, data=b""):
    cs = cmd_id ^ len(data)
    for b in data:
        cs ^= b
    return cs & 0xFF


# ============================================================
# 帧构建与解析
# ============================================================
def build_frame(cmd_id, data=b""):
    """构建命令帧，返回 bytes"""
    return bytes([FRAME_HEADER, cmd_id, len(data)]) + data + bytes([checksum(cmd_id, data)])


def read_response(ser, timeout=1.0):
    """读取一个响应帧，返回 (cmd_id, status) 或 None"""
    ser.timeout = timeout
    while True:
        b = ser.read(1)
        if not b:
            return None
        if b[0] == RESP_HEADER:
            rest = ser.read(3)
            if len(rest) != 3:
                return None
            cmd, status, ck = rest
            if (cmd ^ status) != ck:
                print(f"  [警告] 响应校验和不匹配: cmd={cmd:02X} status={status:02X} ck={ck:02X} expected={cmd ^ status:02X}")
                return None
            return (cmd, status)


# ============================================================
# 命令发送
# ============================================================
def send_cmd(ser, cmd_id, data=b"", label=""):
    """发送命令，等待 ACK + 完成，打印结果"""
    frame = build_frame(cmd_id, data)
    hex_str = " ".join(f"{b:02X}" for b in frame)
    print(f"发送 [{label}]: {hex_str}")
    ser.write(frame)

    ack = read_response(ser, timeout=1.0)
    if not ack:
        print("  [错误] 无 ACK 响应")
        return False
    print(f"  ACK:  cmd={ack[0]:02X} status={ack[1]:02X} ({STATUS_NAMES.get(ack[1], '?')})")
    if ack[1] != 0x00:
        return False

    done = read_response(ser, timeout=5.0)
    if done:
        print(f"  DONE: cmd={done[0]:02X} status={done[1]:02X} ({STATUS_NAMES.get(done[1], '?')})")
    else:
        print("  (无完成响应，可能不需要)")
    return True


# ============================================================
# 高层命令
# ============================================================
def servo_move(ser, servo_id, angle):
    """单独控制一个舵机：servo_id 1-8, angle 0-180"""
    angles = [90] * 8
    angles[servo_id - 1] = angle
    return send_cmd(ser, CMD["direct"], bytes(angles),
                    f"舵机{servo_id} → {angle}°")

def servo_all(ser, angles):
    """控制全部 8 舵机"""
    label = " ".join(f"{i+1}={angles[i]}°" for i in range(8) if angles[i] != 90)
    if not label:
        label = "全部归中"
    return send_cmd(ser, CMD["direct"], bytes(angles), label)

def gesture(ser, name):
    """发送手势命令"""
    return send_cmd(ser, CMD[name], label=name.upper())

def set_hand(ser, side):
    """设置左右手: 'R'/'L' 或 1/2"""
    val = 0x01 if side in ("R", "r", 1) else 0x02
    return send_cmd(ser, CMD["set_side"], bytes([val]),
                    f"设{'右手' if val==1 else '左手'}")

def nop_test(ser):
    return send_cmd(ser, CMD["nop"], label="NOP")


# ============================================================
# CLI
# ============================================================
def print_help():
    print("""
用法:
  python serial_test.py COM端口 [命令]

命令:
  nop                            链路测试
  servo <ID> <角度>              单独控制舵机 (ID=1-8, 角度=0-180)
  all <a1> <a2> ... <a8>         控制全部 8 舵机
  mid                            全部归中 (90°)
  open / close                   张开/握拳
  rock / scissors / paper        石头/剪刀/布
  thumbs_up / ok / pinch         真棒/OK/捏合
  taunt1 / taunt2                嘲讽1/2
  index                          指向 (食指伸出)
  hand <R|L>                     设右手/左手
  repeat                         重复上一条
  stop                           停止
  wave                           扫频测试 (舵机1 0→180→0)
  sweep <ID>                     单个舵机扫频 (0→180→0)
  test                           全部 8 舵机逐个归中测试

示例:
  python serial_test.py COM3 nop
  python serial_test.py COM3 servo 1 90
  python serial_test.py COM3 servo 3 180
  python serial_test.py COM3 sweep 1
  python serial_test.py COM3 rock
  python serial_test.py COM3 hand L
  python serial_test.py COM3 mid
  python serial_test.py COM3 test
""")

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    port = sys.argv[1]

    # 只有端口号，打开交互模式
    if len(sys.argv) == 2:
        interactive(port)
        return

    # 单条命令模式
    cmd = sys.argv[2].lower()
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(0.5)  # 等 ESP32 复位

        if cmd == "nop":
            nop_test(ser)
        elif cmd == "servo":
            sid = int(sys.argv[3])
            ang = int(sys.argv[4])
            servo_move(ser, sid, ang)
        elif cmd == "all":
            angs = [int(a) for a in sys.argv[3:11]]
            servo_all(ser, angs)
        elif cmd == "mid":
            servo_all(ser, [90]*8)
        elif cmd == "test":
            # 逐舵机归中测试
            ser.write(build_frame(CMD["nop"]))
            resp = read_response(ser)
            if not resp:
                print("链路不通！检查串口连接和波特率。")
                ser.close()
                return
            print("链路 OK，开始逐舵机测试...\n")
            for sid in range(1, 9):
                print(f"--- 舵机 {sid} ---")
                for ang in [90, 0, 180, 90]:
                    servo_move(ser, sid, ang)
                    time.sleep(0.8)
                print()

        elif cmd == "sweep":
            sid = int(sys.argv[3])
            print(f"舵机 {sid} 扫频: 0° → 180° → 0° (步长 10°)")
            for ang in range(0, 181, 10):
                servo_move(ser, sid, ang)
                time.sleep(0.3)
            for ang in range(170, -1, -10):
                servo_move(ser, sid, ang)
                time.sleep(0.3)

        elif cmd == "wave":
            print("舵机1 扫频: 0° → 180° → 0° (步长 10°)")
            for ang in range(0, 181, 10):
                servo_move(ser, 1, ang)
                time.sleep(0.3)
            for ang in range(170, -1, -10):
                servo_move(ser, 1, ang)
                time.sleep(0.3)

        elif cmd in ("open", "close", "rock", "scissors", "paper",
                      "thumbs_up", "ok", "pinch", "taunt1", "taunt2",
                      "index"):
            gesture(ser, cmd)

        elif cmd == "hand":
            set_hand(ser, sys.argv[3])

        elif cmd == "repeat":
            send_cmd(ser, CMD["repeat"], label="REPEAT")

        elif cmd == "stop":
            send_cmd(ser, CMD["stop"], label="STOP")

        else:
            print(f"未知命令: {cmd}")
            print_help()

        ser.close()
    except serial.SerialException as e:
        print(f"串口错误: {e}")
        print(f"  端口: {port}")
        print(f"  可用端口: {list_ports()}")
    except IndexError:
        print(f"参数不足，见下方帮助:")
        print_help()
    except ValueError as e:
        print(f"参数格式错误: {e}")


def list_ports():
    try:
        from serial.tools import list_ports as lp
        return [p.device for p in lp.comports()]
    except ImportError:
        return ["(无法列举，请安装 pyserial)"]


def interactive(port):
    """交互模式"""
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(0.5)
    except serial.SerialException as e:
        print(f"无法打开 {port}: {e}")
        return

    print(f"AmazingHand 交互测试 — {port}")
    print("输入命令 (help 查看帮助, quit 退出)\n")

    last_angles = [90]*8

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()

        if cmd == "quit" or cmd == "exit":
            break
        elif cmd == "help":
            print("""
  nop                   链路测试
  s <ID> <角度>          控制单个舵机 (1-8) (0-180)
  m <ID> <角度>          同上 (简写)
  all <a1>..<a8>         控制全部
  mid                    全部归中
  rock/scissors/paper    手势
  open/close             张开/握拳
  ok/thumbs_up/pinch     手势
  taunt1/taunt2          手势
  hand R/L               左右手
  repeat/stop            控制
  test                   逐个测试
  wave/sweep <ID>        扫频
  quit                   退出
""")
        elif cmd == "nop":
            nop_test(ser)
        elif cmd in ("s", "m", "servo"):
            sid, ang = int(parts[1]), int(parts[2])
            servo_move(ser, sid, ang)
            last_angles[sid-1] = ang
        elif cmd == "all":
            angs = [int(a) for a in parts[1:9]]
            servo_all(ser, angs)
            last_angles = angs
        elif cmd == "mid":
            servo_all(ser, [90]*8)
            last_angles = [90]*8
        elif cmd in ("open", "close", "rock", "scissors", "paper",
                      "thumbs_up", "ok", "pinch", "taunt1", "taunt2",
                      "index"):
            gesture(ser, cmd)
        elif cmd == "hand":
            set_hand(ser, parts[1])
        elif cmd in ("repeat", "stop"):
            send_cmd(ser, CMD[cmd], label=cmd.upper())
        elif cmd == "test":
            ser.write(build_frame(CMD["nop"]))
            if not read_response(ser):
                print("链路不通！")
                continue
            print("链路OK，逐舵机测试:")
            for sid in range(1, 9):
                print(f"  舵机 {sid}: 90° → 0° → 180° → 90°")
                for ang in [90, 0, 180, 90]:
                    servo_move(ser, sid, ang)
                    time.sleep(0.5)
            print("测试完成")
        elif cmd == "sweep":
            sid = int(parts[1])
            for ang in list(range(0, 181, 10)) + list(range(170, -1, -10)):
                servo_move(ser, sid, ang)
                time.sleep(0.2)
        elif cmd == "wave":
            for ang in list(range(0, 181, 10)) + list(range(170, -1, -10)):
                servo_move(ser, 1, ang)
                time.sleep(0.2)
        else:
            print(f"未知命令: {cmd}")

    ser.close()
    print("已断开")


if __name__ == "__main__":
    main()
