#!/usr/bin/env python3
"""AmazingHand 上位机 — 手势控制 + 单舵机控制"""

import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time
import queue

# ============================================================
# 协议层
# ============================================================
FRAME_HEADER = 0xAA
RESP_HEADER = 0xBB

CMD = {
    "nop": 0x00, "rock": 0x01, "scissors": 0x02, "paper": 0x03,
    "thumbs_up": 0x04, "taunt1": 0x05, "taunt2": 0x06,
    "open": 0x07, "close": 0x08, "ok": 0x09, "pinch": 0x0A,
    "index": 0x0C, "direct": 0xF0, "set_side": 0xF1,
    "repeat": 0xFE, "stop": 0xFF,
}

STATUS_NAMES = {0x00: "OK", 0x01: "无效命令", 0x02: "参数错误",
                 0x03: "忙", 0x10: "完成"}


def checksum(cmd_id, data=b""):
    cs = cmd_id ^ len(data)
    for b in data:
        cs ^= b
    return cs & 0xFF


def build_frame(cmd_id, data=b""):
    return bytes([FRAME_HEADER, cmd_id, len(data)]) + data + bytes([checksum(cmd_id, data)])


class SerialWorker:
    """后台串口通信线程"""

    def __init__(self, log_callback):
        self.ser = None
        self.running = False
        self.log = log_callback
        self.tx_queue = queue.Queue()
        self.rx_queue = queue.Queue()
        self.thread = None
        self.lock = threading.Lock()

    def connect(self, port):
        self.ser = serial.Serial(port, 115200, timeout=0.1)
        time.sleep(0.3)
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def disconnect(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None

    def send(self, cmd_id, data=b""):
        if self.ser and self.ser.is_open:
            self.tx_queue.put((cmd_id, data))

    def _run(self):
        while self.running:
            # 发送
            try:
                cmd_id, data = self.tx_queue.get(timeout=0.05)
                frame = build_frame(cmd_id, data)
                with self.lock:
                    self.ser.write(frame)
                self.rx_queue.put(("TX", frame))
            except queue.Empty:
                pass

            # 接收: 精确按帧读取, 确保读满 4 字节, 避免半帧错位
            try:
                with self.lock:
                    if self.ser.in_waiting > 0:
                        hdr = self.ser.read(1)
                        if hdr and hdr[0] == RESP_HEADER:
                            # 读满剩余 3 字节 (timeout=0.1 内可能不足, 需循环)
                            rest = bytearray()
                            deadline = time.time() + 0.1
                            while len(rest) < 3 and time.time() < deadline:
                                chunk = self.ser.read(3 - len(rest))
                                if chunk:
                                    rest.extend(chunk)
                            if len(rest) == 3:
                                self.rx_queue.put(("RX", bytes([RESP_HEADER]) + bytes(rest)))
            except Exception:
                pass

            time.sleep(0.01)


# ============================================================
# GUI
# ============================================================
class HandGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AmazingHand 灵巧手控制台")
        self.root.geometry("720x860")
        self.root.resizable(True, True)

        self.worker = SerialWorker(self._log)
        self.servo_vars = [tk.IntVar(value=90) for _ in range(8)]
        self.side_var = tk.StringVar(value="R")
        self.connected = False
        # 差动控制: 每根手指 2 个自由度 (flex=弯曲/伸直, base=左右摆动)
        self.diff_flex_vars = [tk.IntVar(value=0) for _ in range(4)]
        self.diff_base_vars = [tk.IntVar(value=90) for _ in range(4)]
        # 手势追踪: 摄像头 + MediaPipe
        self.tracker = None
        self.tracker_thread = None
        self.tracker_running = False
        self.tracker_queue = queue.Queue()
        self.tracker_sent_angles = None
        self.tracker_last_sent_ts = 0.0
        self.tracker_smooth_angles = None  # EMA 平滑后的角度

        self._build_ui()
        self._poll_rx()

    # ---- 串口栏 ----
    def _build_ui(self):
        # ===== 顶部：串口控制 =====
        top = ttk.Frame(self.root)
        top.pack(fill=tk.X, padx=8, pady=4)

        ttk.Label(top, text="串口:").pack(side=tk.LEFT, padx=(0, 4))
        self.port_var = tk.StringVar()
        self.port_cb = ttk.Combobox(top, textvariable=self.port_var, width=16, state="readonly")
        self.port_cb.pack(side=tk.LEFT, padx=2)
        self._refresh_ports()

        ttk.Button(top, text="刷新", width=5, command=self._refresh_ports).pack(side=tk.LEFT, padx=2)
        self.connect_btn = ttk.Button(top, text="连接", command=self._toggle_connect)
        self.connect_btn.pack(side=tk.LEFT, padx=2)
        self.status_label = ttk.Label(top, text="● 未连接", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=8)

        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=4)

        # ===== 中部：手势 + 舵机 + 追踪 (可滚动) =====
        # 用 Canvas + Scrollbar 包住所有面板, 各面板自然展开不被挤压
        self._canvas = tk.Canvas(self.root, highlightthickness=0)
        self._vscroll = ttk.Scrollbar(self.root, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vscroll.set)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=4)
        self._vscroll.pack(side=tk.RIGHT, fill=tk.Y, pady=4)

        mid = ttk.Frame(self._canvas)
        self._canvas_window_id = self._canvas.create_window((0, 0), window=mid, anchor="nw")
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)
        self._mid = mid

        def _on_configure(event):
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))
            # 让内部 frame 宽度跟随 Canvas, 内容自动换行
            self._canvas.itemconfigure(self._canvas_window_id, width=event.width)
        self._canvas.bind("<Configure>", _on_configure)
        # 鼠标滚轮滚动
        self._canvas.bind_all("<MouseWheel>",
                              lambda e: self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # --- 手势面板 ---
        gesture_frame = ttk.LabelFrame(mid, text="手势命令")
        gesture_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        gestures = [
            ("石头",    "rock"),     ("剪刀",   "scissors"), ("布",     "paper"),
            ("真棒",    "thumbs_up"),("OK",     "ok"),       ("捏合",   "pinch"),
            ("张开",    "open"),     ("握拳",   "close"),    ("指向",   "index"),
            ("嘲讽1",   "taunt1"),   ("嘲讽2",  "taunt2"),
        ]
        for i, (label, cmd) in enumerate(gestures):
            btn = ttk.Button(gesture_frame, text=label, width=8,
                             command=lambda c=cmd: self._gesture(c))
            btn.grid(row=i // 3, column=i % 3, padx=2, pady=2, sticky="ew")

        # 左右手
        side_frame = ttk.Frame(gesture_frame)
        side_frame.grid(row=5, column=0, columnspan=3, pady=(8, 2))
        ttk.Label(side_frame, text="手:").pack(side=tk.LEFT)
        ttk.Radiobutton(side_frame, text="右手", variable=self.side_var, value="R",
                        command=self._set_side).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(side_frame, text="左手", variable=self.side_var, value="L",
                        command=self._set_side).pack(side=tk.LEFT, padx=4)
        ttk.Button(side_frame, text="重复", width=5, command=lambda: self._send(CMD["repeat"])).pack(side=tk.RIGHT, padx=2)
        ttk.Button(side_frame, text="停止", width=5, command=lambda: self._send(CMD["stop"])).pack(side=tk.RIGHT, padx=2)

        # --- 手指差动控制面板 ---
        # 每根手指两个自由度: 弯曲/伸直(flex, 差动) + 左右摆动(base, 同向)
        # 舵机角度: GPIO_a = base + flex, GPIO_b = base - flex
        # 例(食指): 完全伸直 flex=+70; 完全弯曲 flex=-70; 右摆 base=60; 左摆 base=120
        diff_frame = ttk.LabelFrame(mid, text="手指差动控制 (弯曲/伸直 + 左右摆动)")
        diff_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 4), pady=(4, 0))

        diff_fingers = [
            ("食指", 0), ("中指", 1), ("无名指", 2), ("拇指", 3),
        ]
        for fi, (name, fi_idx) in enumerate(diff_fingers):
            fg = ttk.Frame(diff_frame)
            fg.grid(row=fi, column=0, sticky="ew", padx=4, pady=1)
            ttk.Label(fg, text=name, width=5).pack(side=tk.LEFT)

            # 弯曲/伸直 (flex): -70 = 弯曲, +70 = 伸直, 0 = 中立
            ttk.Label(fg, text="弯曲◀▶伸直", width=8).pack(side=tk.LEFT)
            flex_scale = ttk.Scale(fg, from_=-70, to=70,
                                   variable=self.diff_flex_vars[fi_idx],
                                   command=lambda v, i=fi_idx: self._on_diff_flex(i, v))
            flex_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
            flex_label = ttk.Label(fg, text="0", width=3)
            flex_label.pack(side=tk.LEFT, padx=2)

            # 左右摆动 (base): 60 = 右摆, 120 = 左摆, 90 = 中立
            ttk.Label(fg, text="右摆◀▶左摆", width=8).pack(side=tk.LEFT, padx=(8, 0))
            base_scale = ttk.Scale(fg, from_=60, to=120,
                                   variable=self.diff_base_vars[fi_idx],
                                   command=lambda v, i=fi_idx: self._on_diff_base(i, v))
            base_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
            base_label = ttk.Label(fg, text="90", width=3)
            base_label.pack(side=tk.LEFT, padx=2)

            if not hasattr(self, '_diff_flex_labels'):
                self._diff_flex_labels = {}
                self._diff_base_labels = {}
            self._diff_flex_labels[fi_idx] = flex_label
            self._diff_base_labels[fi_idx] = base_label

        ttk.Button(diff_frame, text="全部归中 (90°)",
                   command=self._diff_mid).grid(row=4, column=0, pady=2)

        # --- 手势追踪面板 (MediaPipe) ---
        tracking_frame = ttk.LabelFrame(mid, text="手势追踪 (MediaPipe 摄像头)")
        tracking_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=(0, 4), pady=(4, 0))

        trow = ttk.Frame(tracking_frame)
        trow.pack(fill=tk.X, padx=4, pady=2)
        ttk.Label(trow, text="摄像头:").pack(side=tk.LEFT)
        self.cam_var = tk.StringVar(value="0")
        cam_cb = ttk.Combobox(trow, textvariable=self.cam_var, width=6, state="readonly",
                              values=[str(i) for i in range(4)])
        cam_cb.pack(side=tk.LEFT, padx=2)
        self.track_btn = ttk.Button(trow, text="开始追踪", command=self._toggle_tracking)
        self.track_btn.pack(side=tk.LEFT, padx=4)
        self.track_status = ttk.Label(trow, text="未启动", foreground="red")
        self.track_status.pack(side=tk.LEFT, padx=8)

        # 画面显示区
        self.track_canvas = tk.Label(tracking_frame, text="(开启追踪后显示摄像头画面)",
                                     bg="#222", fg="#aaa")
        self.track_canvas.pack(fill=tk.X, padx=4, pady=(0, 2))

        # 检测结果行
        self.track_result = ttk.Label(tracking_frame, text="未检测到手", foreground="gray")
        self.track_result.pack(fill=tk.X, padx=4, pady=(0, 2))

        # --- 舵机面板 ---
        servo_frame = ttk.LabelFrame(mid, text="舵机直驱")
        servo_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        fingers = [
            ("食指", 0, 1, 4, 5),
            ("中指", 2, 3, 6, 7),
            ("无名指", 4, 5, 15, 16),
            ("拇指", 6, 7, 17, 18),
        ]

        for name, s1, s2, gpio1, gpio2 in fingers:
            fg = ttk.LabelFrame(servo_frame, text=f"{name} (GPIO{gpio1},{gpio2})")
            fg.pack(fill=tk.X, padx=4, pady=2)

            for si, label in [(s1, f"关节1"), (s2, f"关节2")]:
                row = ttk.Frame(fg)
                row.pack(fill=tk.X, pady=1)
                ttk.Label(row, text=label, width=5).pack(side=tk.LEFT)
                scale = ttk.Scale(row, from_=180, to=0, variable=self.servo_vars[si],
                                  command=lambda v, idx=si: self._on_slider(idx, v))
                scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
                val_label = ttk.Label(row, text="90°", width=4)
                val_label.pack(side=tk.RIGHT, padx=2)
                # 保存 label 引用
                if not hasattr(self, '_slider_labels'):
                    self._slider_labels = {}
                self._slider_labels[si] = val_label

        ttk.Button(servo_frame, text="全部归中 (90°)",
                   command=self._all_mid).pack(pady=4)

        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=4)

        # ===== 底部：日志 =====
        bottom = ttk.LabelFrame(self.root, text="通信日志")
        bottom.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))
        self.log_text = tk.Text(bottom, height=6, state=tk.DISABLED, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    # ---- 串口操作 ----
    def _refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_cb["values"] = ports
        if ports:
            self.port_var.set(ports[0])

    def _toggle_connect(self):
        if not self.connected:
            port = self.port_var.get()
            if not port:
                self._log("请选择串口")
                return
            try:
                self.worker.connect(port)
                self.connected = True
                self.connect_btn.config(text="断开")
                self.status_label.config(text=f"● {port}", foreground="green")
                self._log(f"已连接 {port}")
                # NOP 测试
                time.sleep(0.3)
                self._send(CMD["nop"])
            except Exception as e:
                self._log(f"连接失败: {e}")
        else:
            self.worker.disconnect()
            self.connected = False
            self.connect_btn.config(text="连接")
            self.status_label.config(text="● 未连接", foreground="red")
            self._log("已断开")

    # ---- 命令 ----
    def _send(self, cmd_id, data=b""):
        if self.connected:
            self.worker.send(cmd_id, data)
        else:
            self._log("未连接，请先连接串口")

    def _gesture(self, name):
        self._send(CMD[name])

    def _set_side(self):
        val = 0x01 if self.side_var.get() == "R" else 0x02
        self._send(CMD["set_side"], bytes([val]))

    def _on_slider(self, idx, value):
        """滑块拖拽 → 更新标签 + 发送直驱"""
        angle = int(float(value))
        self.servo_vars[idx].set(angle)
        if idx in self._slider_labels:
            self._slider_labels[idx].config(text=f"{angle}°")

        # 组装直驱帧
        angles = bytes([self.servo_vars[i].get() for i in range(8)])
        self._send(CMD["direct"], angles)

    def _all_mid(self):
        for v in self.servo_vars:
            v.set(90)
        for idx in self._slider_labels:
            self._slider_labels[idx].config(text="90°")
        self._send(CMD["direct"], bytes([90] * 8))

    # ---- 差动控制 ----
    # 每根手指两个舵机: 差动(flex)驱动弯曲/伸直, 同向(base)驱动左右摆动
    # 舵机角度: servo_a = base + flex, servo_b = base - flex
    # 手指 fi (0-3) 对应 servo_vars 索引 (2*fi, 2*fi+1)

    def _diff_compute_and_send(self, fi):
        """根据 flex/base 计算两个舵机角度, 更新舵机变量并发送直驱帧"""
        flex = self.diff_flex_vars[fi].get()
        base = self.diff_base_vars[fi].get()
        a = int(base + flex)
        b = int(base - flex)
        # 约束到 0-180
        a = max(0, min(180, a))
        b = max(0, min(180, b))
        self.servo_vars[2 * fi].set(a)
        self.servo_vars[2 * fi + 1].set(b)
        # 更新舵机直驱面板的标签
        for k in (2 * fi, 2 * fi + 1):
            if k in self._slider_labels:
                self._slider_labels[k].config(text=f"{self.servo_vars[k].get()}°")
        # 发送完整 8 路直驱帧
        angles = bytes([self.servo_vars[i].get() for i in range(8)])
        self._send(CMD["direct"], angles)

    def _on_diff_flex(self, fi, value):
        """弯曲/伸直滑块 (差动)"""
        v = int(float(value))
        self.diff_flex_vars[fi].set(v)
        if fi in self._diff_flex_labels:
            self._diff_flex_labels[fi].config(text=f"{v}")
        self._diff_compute_and_send(fi)

    def _on_diff_base(self, fi, value):
        """左右摆动滑块 (同向)"""
        v = int(float(value))
        self.diff_base_vars[fi].set(v)
        if fi in self._diff_base_labels:
            self._diff_base_labels[fi].config(text=f"{v}")
        self._diff_compute_and_send(fi)

    def _diff_mid(self):
        """差动全部归中: flex=0 (中立), base=90 (中立), 舵机全 90°"""
        for v in self.diff_flex_vars:
            v.set(0)
        for v in self.diff_base_vars:
            v.set(90)
        for fi in self._diff_flex_labels:
            self._diff_flex_labels[fi].config(text="0")
        for fi in self._diff_base_labels:
            self._diff_base_labels[fi].config(text="90")
        for v in self.servo_vars:
            v.set(90)
        for idx in self._slider_labels:
            self._slider_labels[idx].config(text="90°")
        self._send(CMD["direct"], bytes([90] * 8))

    # ---- 手势追踪 (MediaPipe) ----
    def _toggle_tracking(self):
        """开始/停止手势追踪。惰性导入 hand_tracking(需 64 位 Python + mediapipe)。"""
        if self.tracker_running:
            self.tracker_running = False
            self.track_btn.config(text="开始追踪")
            self.track_status.config(text="停止中...", foreground="orange")
            if self.tracker:
                try:
                    self.tracker.release()
                except Exception:
                    pass
            self.track_status.config(text="已停止", foreground="red")
            return

        try:
            import hand_tracking
        except ImportError as e:
            self._log(f"手势追踪需要 mediapipe (64 位 Python): {e}")
            self.track_status.config(text="缺少依赖", foreground="red")
            return

        cam = int(self.cam_var.get())
        try:
            self.tracker = hand_tracking.HandTracker(cam=cam)
        except Exception as e:
            self._log(f"摄像头打开失败: {e}")
            self.track_status.config(text="摄像头错误", foreground="red")
            return

        self.tracker_running = True
        self.tracker_queue = queue.Queue()
        self.tracker_sent_angles = None
        self.tracker_last_sent_ts = 0.0
        self.tracker_smooth_angles = None
        self.track_btn.config(text="停止追踪")
        self.track_status.config(text="追踪中...", foreground="green")
        self.track_result.config(text="等待检测...")

        self.tracker_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.tracker_thread.start()
        self.root.after(30, self._tracking_poll)

    def _tracking_loop(self):
        """后台线程: 持续读取摄像头并计算结果, 放入队列。"""
        import hand_tracking
        while self.tracker_running:
            try:
                frame, tips = self.tracker.process()
                self.tracker_queue.put((frame, tips))
            except Exception as e:
                self.tracker_queue.put((None, None))
                self.tracker_running = False
                self._log(f"追踪错误: {e}")
                break

    def _tracking_poll(self):
        """主线程轮询: 刷新画面 + 节流发送舵机角度。"""
        if not self.tracker_running:
            return

        frame = None
        tips = None
        try:
            while True:
                f, t = self.tracker_queue.get_nowait()
                if f is not None:
                    frame, tips = f, t
        except queue.Empty:
            pass

        # 显示画面
        if frame is not None:
            self._show_track_frame(frame)

        # 计算并发送角度 (EMA 平滑消除抖动)
        if tips:
            import hand_tracking
            hands = list(tips.keys())
            self.track_result.config(text=f"检测到手: {hands[0]}", foreground="green")
            hand_tips = tips[hands[0]]  # 默认用第一只检测到的手
            raw_angles = hand_tracking.tips_to_angles(hand_tips)
            # EMA 平滑: alpha 越低越平滑(延迟略大), 0.4 平衡响应与稳定
            if self.tracker_smooth_angles is None:
                self.tracker_smooth_angles = [float(a) for a in raw_angles]
            else:
                alpha = 0.4
                self.tracker_smooth_angles = [
                    prev + alpha * (cur - prev)
                    for prev, cur in zip(self.tracker_smooth_angles, raw_angles)
                ]
            angles = [int(round(a)) for a in self.tracker_smooth_angles]
            self._tracking_send(angles)
        else:
            self.track_result.config(text="未检测到手", foreground="gray")

        self.root.after(30, self._tracking_poll)

    def _show_track_frame(self, frame_bgr):
        """BGR 帧 → PIL ImageTk 显示到 Label。画面为原始视图(不镜像)。"""
        try:
            import cv2
            from PIL import Image, ImageTk
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            # 固定显示尺寸, 完整显示不被挤扁
            img = img.resize((480, 360), Image.LANCZOS)
            self._tk_img = ImageTk.PhotoImage(img)
            self.track_canvas.config(image=self._tk_img, text="")
        except ImportError:
            self.track_canvas.config(text="(需要 Pillow 显示画面)")

    def _tracking_send(self, angles):
        """发送节流: 角度变化 >=1° 且距上次 >=60ms 才发送。"""
        if not self.connected:
            return
        now = time.time() * 1000
        changed = (self.tracker_sent_angles is None) or \
                  max(abs(a - b) for a, b in zip(angles, self.tracker_sent_angles)) >= 1
        if changed and (now - self.tracker_last_sent_ts) >= 60:
            self.tracker_sent_angles = angles
            self.tracker_last_sent_ts = now
            self.worker.send(CMD["direct"], bytes(angles))

    # ---- 日志 ----
    def _log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        ts = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _poll_rx(self):
        """定期检查串口接收队列"""
        try:
            while True:
                typ, data = self.worker.rx_queue.get_nowait()
                if typ == "TX":
                    hex_str = " ".join(f"{b:02X}" for b in data)
                    self._log(f"发送: {hex_str}")
                elif typ == "RX":
                    if len(data) >= 4:
                        cmd, status, ck = data[1], data[2], data[3]
                        expected = cmd ^ status
                        if expected != ck:
                            self._log(f"响应校验错误: {data.hex(' ').upper()}")
                        else:
                            status_name = STATUS_NAMES.get(status, f"0x{status:02X}")
                            self._log(f"响应: cmd=0x{cmd:02X} status={status_name}")
        except queue.Empty:
            pass
        self.root.after(100, self._poll_rx)


if __name__ == "__main__":
    root = tk.Tk()
    app = HandGUI(root)
    root.mainloop()
