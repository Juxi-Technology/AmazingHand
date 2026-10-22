#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AmazingHand 网页控制 —— 后端服务

职责：
  1. 打开串口，驱动 SCS0009 舵机（rustypot）
  2. 提供静态文件服务（web/ 目录）
  3. 通过 WebSocket 接收前端下发的姿态值，换算成舵机目标位置并下发

支持两种模式：左手 / 右手。

换算公式与 AmazingHandControl 官方实现一致：

    1) 左手先交换每根手指两个舵机的值     （mirror_pose）
    2) servo_deg = (id 奇数 ? +1 : -1) × (姿态值 - angle_offset_deg)

  angle_offset_deg：右手 0，左手 -35.16（舵机臂错开半格）。

用法：

    python server.py                      # 自动探测串口，左右手都启用
    python server.py --port COM9
    python server.py --hand left          # 只启用左手
    python server.py --dry-run            # 不开串口，只验证前后端
"""

from __future__ import annotations

import argparse
import asyncio
import gc
import io
import json
import math
import sys
import threading
import time
import traceback
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT.parent / "Amazinghand-web-io"      # 前端只有一份，Python 版直接复用
CONFIG_PATH = ROOT / "config.json"
LOG_PATH = ROOT / "server.log"

WS_HOST = "0.0.0.0"
WS_PORT = 8765
HTTP_PORT = 8000

MIN_WRITE_INTERVAL_S = 0.02      # 串口写入最小间隔
POSE_EPSILON_DEG = 0.5           # 变化小于此值不下发


def _log(msg: str) -> None:
    line = "[%s] %s" % (datetime.now().strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    try:
        with io.open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------- 配置

class HandConfig:
    """一只手：4 根手指，每根两个舵机。"""

    def __init__(self, key, raw):
        self.key = key
        self.label = raw.get("label", key)
        self.angle_offset_deg = float(raw.get("angle_offset_deg", 0.0))
        self.mirror_pose = bool(raw.get("mirror_pose", False))
        self.fingers = [
            {"key": f["key"], "name": f["name"], "ids": [int(x) for x in f["ids"]]}
            for f in raw["fingers"]
        ]

    def servo_ids(self):
        return [i for f in self.fingers for i in f["ids"]]

    def finger_keys(self):
        return [f["key"] for f in self.fingers]


def _strip_comments(node):
    """递归去掉 "//" 注释键（JSON 本身不支持注释）。"""
    if isinstance(node, dict):
        return {k: _strip_comments(v) for k, v in node.items()
                if not k.startswith("//")}
    if isinstance(node, list):
        return [_strip_comments(v) for v in node]
    return node


def load_config():
    with io.open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = _strip_comments(json.load(f))
    hands = {}
    for k, v in cfg["hands"].items():
        got = HandConfig(k, v)
        # 容忍在 config.json 里新增的手，只认识这两只
        if k in ("left", "right"):
            hands[k] = got
    return cfg, hands, cfg["limits"]


# ---------------------------------------------------------------- 换算

def pose_to_servo_goals(hand: HandConfig, positions) -> list[tuple[int, float]]:
    """姿态值(8 个，按 无名指/中指/食指/拇指) -> [(舵机ID, 目标角度°)]

    与 AmazingHandControl 的 apply_pose() 等价。
    """
    pos = [float(x) for x in positions]
    if hand.mirror_pose:
        for i in range(len(hand.fingers)):
            a, b = i * 2, i * 2 + 1
            pos[a], pos[b] = pos[b], pos[a]

    goals = []
    for i, finger in enumerate(hand.fingers):
        for j, sid in enumerate(finger["ids"]):
            v = pos[i * 2 + j] - hand.angle_offset_deg
            # 偶数 ID 取负 —— 每个手指第二个舵机是反向安装的
            goals.append((sid, -v if sid % 2 == 0 else v))
    return goals


# ---------------------------------------------------------------- 舵机

class HandDriver:
    def __init__(self, cfg, hands, limits, controller=None, enabled=None):
        self.cfg = cfg
        self.hands = hands
        self.limits = limits
        self.controller = controller
        self.port = None
        self.enabled = enabled or list(hands.keys())
        self.torque_on = {k: False for k in hands}
        self.last_goal = {}
        self.last_write_t = 0.0

    # -- 钳制 ---------------------------------------------------------
    def clamp(self, v: float) -> float:
        return max(float(self.limits["pose_min_deg"]),
                   min(float(self.limits["pose_max_deg"]), v))

    # -- 目标 ---------------------------------------------------------
    def targets(self, keys, positions):
        """keys 是手名列表，如 ["right"]。"""
        out = []
        safe = [self.clamp(x) for x in positions]
        for k in keys:
            if k in self.hands:
                out.append((k, pose_to_servo_goals(self.hands[k], safe)))
        return out

    # -- 下发 ---------------------------------------------------------
    def enable_torque(self, keys, on: bool):
        for k in keys:
            if k not in self.hands:
                continue
            if self.controller is not None:
                ids = self.hands[k].servo_ids()
                self.controller.sync_write_torque_enable(ids, [1 if on else 0] * len(ids))
            self.torque_on[k] = on
            _log("%s 力矩 %s" % (self.hands[k].label, "开启" if on else "关闭"))

    def send_pose(self, keys, positions, speed=None, force=False):
        if speed is None:
            speed = self.limits.get("speed", 3)
        for _k, goals in self.targets(keys, positions):
            self._write(goals, speed=speed, force=force)

    def goto_middle(self, keys):
        self.send_pose(keys, self.cfg["middle"]["positions"], force=True)
        _log("%s 回中位" % "、".join(self.hands[k].label for k in keys if k in self.hands))

    def _write(self, goals, speed=None, force=False):
        if not goals:
            return
        if not force:
            goals = [(i, g) for i, g in goals
                     if abs(self.last_goal.get(i, 1e9) - g) >= POSE_EPSILON_DEG]
            if not goals:
                return
        now = time.monotonic()
        if not force and now - self.last_write_t < MIN_WRITE_INTERVAL_S:
            return
        self.last_write_t = now

        for i, g in goals:
            self.last_goal[i] = g
        if self.controller is None:
            return
        ids = [i for i, _ in goals]
        rad = [math.radians(g) for _, g in goals]
        if speed is not None:
            self.controller.sync_write_goal_speed(ids, [int(speed)] * len(ids))
        self.controller.sync_write_goal_position(ids, rad)

    def release_all(self):
        for k in self.enabled:
            try:
                self.enable_torque([k], False)
            except Exception:
                pass

    # -- 串口热插拔 ---------------------------------------------------
    def attach(self, controller, port):
        """接上新串口。调用方负责先把旧的摘掉。"""
        self.controller = controller
        self.port = port
        self.last_goal.clear()
        self.torque_on = {k: False for k in self.hands}

    def detach(self):
        """断开串口并**真正释放句柄**。

        rustypot 是编译好的 Rust 扩展，没有 close()/disconnect() —— 串口由
        Rust 端持有，只有对象被回收（Drop）时才释放。所以这里必须先把引用
        彻底丢掉再强制 GC，否则重新打开同一串口会报「拒绝访问」。
        """
        if self.controller is not None:
            self.release_all()
            self.controller = None
        gc.collect()
        self.port = None
        self.last_goal.clear()
        self.torque_on = {k: False for k in self.hands}


# ---------------------------------------------------------------- 串口

def detect_port() -> str:
    """按常见顺序找串口；找不到就返回空串。"""
    ports = list_serial_ports()
    for p in ports:
        if p["likely"]:
            return p["device"]
    return ports[0]["device"] if ports else ""


# 常见 USB 转串口芯片特征。CH34x 系列（CH340/341/343/344…）都是 WCH 家的，
# 所以匹配 "ch34" 前缀 + WCH 的厂商号 1a86，比逐个列型号稳。
LIKELY_MARKERS = (
    "ch34",      # WCH CH340 / CH341 / CH343 / CH344 —— AmazingHand 控制板常用
    "1a86",      # WCH 的 USB vendor id
    "cp210",     # Silicon Labs
    "ft232", "ft231",   # FTDI
    "acm",       # Linux CDC-ACM
    "usb serial",
)


def list_serial_ports() -> list[dict]:
    """列出本机所有串口，供前端选择。

    likely 用来标记常见 USB 转串口芯片，前端可以排前面或高亮。
    """
    try:
        from serial.tools import list_ports
    except Exception:
        return []
    out = []
    for p in list_ports.comports():
        desc = (p.description or "").strip()
        hwid = (p.hwid or "").lower()
        blob = (desc + " " + hwid).lower()
        out.append({
            "device": p.device,
            "description": desc or p.device,
            "likely": any(k in blob for k in LIKELY_MARKERS),
        })
    # 常见的排前面，其余按名字
    out.sort(key=lambda x: (not x["likely"], x["device"]))
    return out


def open_controller(cfg, port=None):
    from rustypot import Scs0009PyController
    port = port or cfg["serial"].get("port") or detect_port()
    if not port:
        raise RuntimeError("没有找到串口。请插好控制板，或在上方手动选择。")
    _log("打开串口 %s @ %s" % (port, cfg["serial"]["baudrate"]))
    return Scs0009PyController(
        serial_port=port,
        baudrate=int(cfg["serial"]["baudrate"]),
        timeout=float(cfg["serial"]["timeout_s"]),
    )


# ---------------------------------------------------------------- HTTP

class WebHandler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(WEB_DIR), **kw)

    def end_headers(self):
        # 开发服务器：禁用一切缓存。
        # 不加这个的话，浏览器会按 Last-Modified 做启发式缓存，改了 js/css
        # 刷新页面也还是旧的 —— 排查问题时极容易误判。
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_head(self):
        """index.html 里的 js/css 自动带版本号，并注入后端标记。

        双保险：即使浏览器已经缓存过旧文件，改完代码刷新也会拿到新的。
        版本号取这几个文件里最新的 mtime。
        注入 AH_BACKEND="ws" 让同一份前端改用 WebSocket，而不是页面内的 Web Serial。
        """
        if self.path.split("?")[0] in ("/", "/index.html"):
            try:
                idx = WEB_DIR / "index.html"
                body = idx.read_bytes()
                assets = ("index.html", "app.js", "tracking.js", "style.css",
                          "i18n.js", "io.js", "ws.js")
                ver = str(int(max((WEB_DIR / a).stat().st_mtime for a in assets)))
                body = body.replace(b".js\"", (".js?v=%s\"" % ver).encode())
                body = body.replace(b".css\"", (".css?v=%s\"" % ver).encode())
                body = body.replace(b"<head>",
                                    b'<head>\n<script>window.AH_BACKEND = "ws";</script>', 1)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                return io.BytesIO(body)
            except Exception:
                pass          # 出错就走默认逻辑
        return super().send_head()

    def log_message(self, fmt, *args):
        pass


def start_http(port: int):
    """起静态文件服务。

    必须用 ThreadingHTTPServer —— 单线程的 HTTPServer 只要浏览器保持一个
    连接（keep-alive / 长轮询），其它请求就全被阻塞，表现是页面一直
    「等待服务器」或直接连不上。
    """
    for attempt in range(10):
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", port + attempt), WebHandler)
            srv.daemon_threads = True
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            return port + attempt, srv
        except OSError:
            continue
    raise RuntimeError("HTTP 端口 %d 起不来" % port)


# ---------------------------------------------------------------- WS

class Session:
    def __init__(self, driver: HandDriver, cfg, dry_run=False):
        self.driver = driver
        self.cfg = cfg
        self.dry_run = dry_run
        self.current = {k: list(driver.cfg["middle"]["positions"])
                        for k in driver.hands}
        self.target = driver.enabled[0]        # left / right

    # -- 状态 ---------------------------------------------------------
    def state(self):
        return {
            "type": "state",
            "hands": {
                k: {
                    "label": h.label,
                    "angle_offset_deg": h.angle_offset_deg,
                    "mirror_pose": h.mirror_pose,
                    "fingers": [{"key": f["key"], "name": f["name"], "ids": f["ids"]}
                                for f in h.fingers],
                    "servo_ids": h.servo_ids(),
                    "torque": self.driver.torque_on.get(k, False),
                }
                for k, h in self.driver.hands.items()
            },
            "enabled": self.driver.enabled,
            "poses": self.cfg["poses"],
            "middle": self.cfg["middle"],
            "sequences": self.cfg.get("sequences", {}),
            "limits": self.driver.limits,
            "axes": self.cfg.get("axes", {}),
            "camera": self.cfg.get("camera", {}),
            "target": self.target,
            "positions": self.current,
            "port": {
                "current": self.driver.port,
                "connected": self.driver.controller is not None,
                "dry_run": self.dry_run,
                "available": list_serial_ports(),
            },
        }

    # -- 指令 ---------------------------------------------------------
    async def handle(self, msg):
        cmd = msg.get("cmd")

        if cmd == "hello":
            return self.state()

        if cmd == "ports":
            return self._ports_reply()

        if cmd == "connect":
            port = (msg.get("port") or "").strip()
            if not port:
                return {"type": "error", "msg": "没有指定串口"}
            if self.dry_run:
                return {"type": "error", "msg": "当前是 --dry-run 模式，未启用串口"}

            # 先把旧口彻底释放（丢引用 + GC），否则重开同一串口会「拒绝访问」
            self.driver.detach()
            await asyncio.sleep(0.25)

            ctrl, last = None, None
            for attempt in range(4):
                try:
                    ctrl = open_controller(self.cfg, port)
                    break
                except Exception as e:
                    last = e
                    gc.collect()          # Windows 释放句柄可能慢一拍，重试
                    await asyncio.sleep(0.4)
            if ctrl is None:
                _log("连接 %s 失败: %s" % (port, last))
                return {"type": "error",
                        "msg": "连接 %s 失败：%s" % (port, last)}

            self.driver.attach(ctrl, port)
            # 接上就让舵机回中位，避免上电残留姿态
            self.driver.enable_torque(self._torque_target(), True)
            await asyncio.sleep(0.4)
            self.driver.goto_middle(self._torque_target())
            self.current = {k: list(self.cfg["middle"]["positions"])
                            for k in self.driver.hands}
            _log("已连接 %s" % port)
            r = self._ports_reply()
            r["type"] = "connected"
            r["positions"] = self.current
            return r

        if cmd == "disconnect":
            self.driver.detach()
            _log("已断开串口")
            r = self._ports_reply()
            r["type"] = "disconnected"
            return r

        if cmd == "target":
            t = msg.get("target")
            if t in self.driver.enabled:
                self.target = t
            return {"type": "target", "target": self.target}

        if cmd == "pose":
            name = msg.get("name")
            p = self.cfg["poses"].get(name) or self.cfg["middle"]
            target = self._target(msg)
            pos = self._pose_positions(p, target)
            self._set_positions(target, pos)
            await self._ensure_torque(target)
            self.driver.send_pose([target], pos,
                                  speed=msg.get("speed", self.driver.limits.get("speed")))
            _log("%s 姿态 %s" % (self._label(target), p.get("label", name)))
            return {"type": "positions", "target": target, "positions": self.current}

        if cmd == "set":
            angles = msg.get("angles") or {}
            target = self._target(msg)
            new = self._merge(target, angles)
            await self._ensure_torque(target)
            self.driver.send_pose([target], new, speed=msg.get("speed"))
            return None

        if cmd == "middle":
            target = self._target(msg)
            self._set_positions(target, self.cfg["middle"]["positions"])
            await self._ensure_torque(target)
            self.driver.goto_middle([target])
            return {"type": "positions", "target": target, "positions": self.current}

        if cmd == "torque":
            target = self._target(msg)
            self.driver.enable_torque([target], bool(msg.get("on")))
            return {"type": "torque", "target": target, "on": bool(msg.get("on")),
                    "hands": {k: self.driver.torque_on[k] for k in self.driver.hands}}

        if cmd == "stop":
            _log("急停：全部松开")
            self.driver.release_all()
            return {"type": "stopped",
                    "hands": {k: False for k in self.driver.hands}}

        return None

    # -- 内部 ---------------------------------------------------------
    @staticmethod
    def _pose_positions(p, hand):
        """一条姿态的 8 个值取哪一份。

        `positions` 是两只手共用的；某只手如果在同一条里另有 "right" / "left"
        键，就用那一份覆盖。左右手机械装配有差异的姿态（比如拇指根的角度）
        各自写一套，不用互相迁就。
        """
        return p.get(hand) or p["positions"]

    def _target(self, msg):
        t = msg.get("target") or self.target
        if t in self.driver.hands and t in self.driver.enabled:
            return t
        if self.target in self.driver.enabled:
            return self.target
        return self.driver.enabled[0]

    def _set_positions(self, target, positions):
        self.current[target] = [float(x) for x in positions]

    def _merge(self, target, angles):
        """把 {finger_key: [v1, v2]} 合并进当前姿态值。

        姿态数组顺序由 hand.finger_keys() 决定（无名指/中指/食指/拇指）。
        """
        order = self.driver.hands[target].finger_keys()
        out = list(self.current[target])
        for fi, fk in enumerate(order):
            v = angles.get(fk)
            if isinstance(v, list) and len(v) == 2:
                out[fi * 2] = float(v[0])
                out[fi * 2 + 1] = float(v[1])
        self.current[target] = out
        return out

    async def _ensure_torque(self, target):
        if self.driver.torque_on.get(target):
            return
        self.driver.enable_torque([target], True)
        await asyncio.sleep(0.3)

    def _label(self, target):
        return self.driver.hands[target].label

    # -- 串口 ---------------------------------------------------------
    def _torque_target(self):
        """连接时要初始化的手 —— 已启用的一起回中位，免得残留姿态。"""
        return list(self.driver.enabled)

    @staticmethod
    def _close_quietly(ctrl):
        """兼容旧调用：rustypot 没有 close()，只能丢引用 + GC。"""
        ctrl = None
        gc.collect()

    def _ports_reply(self):
        ports = list_serial_ports()
        cur = self.driver.port
        for p in ports:
            p["current"] = (p["device"] == cur)
        # 键名必须与 state() 里的 port 块一致（available），否则前端刷新后会拿到空列表
        return {
            "type": "ports",
            "available": ports,
            "ports": ports,          # 旧键名，保留兼容
            "current": cur,
            "connected": self.driver.controller is not None,
            "dry_run": self.dry_run,
        }


async def ws_main(driver, cfg, dry_run=False):
    import websockets
    session = Session(driver, cfg, dry_run=dry_run)

    async def handler(ws):
        _log("前端已连接 %s" % (getattr(ws, "remote_address", None),))
        try:
            await ws.send(json.dumps(session.state(), ensure_ascii=False))
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except Exception:
                    continue
                reply = await session.handle(msg)
                if reply:
                    await ws.send(json.dumps(reply, ensure_ascii=False))
        except Exception as e:
            _log("连接异常: %s" % e)
        finally:
            _log("前端断开")

    async with websockets.serve(handler, WS_HOST, WS_PORT):
        await asyncio.Future()


# ---------------------------------------------------------------- main

def parse_args():
    p = argparse.ArgumentParser(description="AmazingHand 网页控制后端")
    p.add_argument("--port", "-p", default=None, help="串口名，如 COM9 或 /dev/ttyACM0")
    p.add_argument("--hand", choices=["left", "right", "both"], default="both",
                   help="启用哪些手（默认 both）")
    p.add_argument("--speed", type=int, default=None, help="覆盖默认速度 1-6")
    p.add_argument("--dry-run", action="store_true", help="不开串口")
    p.add_argument("--no-connect", action="store_true",
                   help="启动时不开串口，串口全部交给网页里手选（不会动舵机）")
    p.add_argument("--http-port", type=int, default=HTTP_PORT)
    return p.parse_args()


def main():
    args = parse_args()
    cfg, hands, limits = load_config()
    if args.port:
        cfg["serial"]["port"] = args.port
    if args.speed:
        limits["speed"] = args.speed

    enabled = list(hands) if args.hand == "both" else [args.hand]

    controller = None
    port = None
    if args.no_connect:
        _log("--no-connect：启动时不打开串口，请在网页顶部选择串口后点「连接」。")
    elif not args.dry_run:
        try:
            port = cfg["serial"].get("port") or detect_port()
            if port:
                controller = open_controller(cfg, port)
            else:
                # 找不到串口也照常启动，让用户在网页里手动选
                _log("未自动探测到串口 —— 服务照常启动，请在网页顶部选择串口后点「连接」。")
        except Exception as e:
            _log("打开串口失败: %s" % e)
            _log("服务照常启动，请在网页顶部选择串口后点「连接」。")

    driver = HandDriver(cfg, hands, limits, controller=controller, enabled=enabled)
    if controller is not None:
        driver.port = port

    if controller is not None:
        # 上电：先开力矩，再让所有舵机回到中位
        tgt = list(enabled)
        driver.enable_torque(tgt, True)
        time.sleep(0.5)
        driver.goto_middle(tgt)

    http_port, http_srv = start_http(args.http_port)
    _log("WebSocket  ws://localhost:%d" % WS_PORT)
    _log("控制台     http://localhost:%d" % http_port)
    _log("已启用：%s" % ", ".join(hands[k].label for k in enabled))

    try:
        asyncio.run(ws_main(driver, cfg, dry_run=args.dry_run))
    except KeyboardInterrupt:
        _log("收到 Ctrl+C")
    finally:
        driver.detach()          # 丢引用 + GC，真正释放串口
        http_srv.shutdown()
        _log("已退出")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        _log("未捕获异常:\n" + traceback.format_exc())
        sys.exit(1)
