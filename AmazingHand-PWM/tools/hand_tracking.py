#!/usr/bin/env python3
"""AmazingHand 手势追踪 — 轻量移植官方 AmazingHand 算法

基于官方 Demo/HandTracking/HandTracking/main.py 的核心算法:
  - mediapipe 0.10.14 旧版 mp.solutions.hands(仅旧版有 3D world landmarks)
  - 用 WRIST/MIDDLE_MCP/INDEX_MCP/PINKY_MCP 构建手部局部坐标系
  - 4 指指尖相对 MCP 的 3D 向量, 左乘旋转矩阵 R 变换到手部坐标系

去掉 dora-rs / pyarrow 依赖, 直接返回每指的 3D tip 向量。
并映射到本项目的差动舵机模型 (flex/base)。

依赖: mediapipe==0.10.14, numpy<2, scipy, opencv-python
注意: mediapipe 0.10.14 仅支持 64 位 Python (win_amd64 wheel)
"""

import numpy as np
import cv2

import mediapipe as mp
from mediapipe import solutions

mp_drawing = solutions.drawing_utils
mp_drawing_styles = solutions.drawing_styles
mp_hands = solutions.hands


def _unit(v):
    n = np.linalg.norm(v)
    if n > 0:
        return v / n
    return np.array([0.0, 0.0, 1.0])


class HandTracker:
    """摄像头手部追踪器: 输出每只手的 4 指 3D tip 向量(手部坐标系)"""

    def __init__(self, cam=0, max_hands=2, min_detection=0.3, min_tracking=0.3,
                 model_complexity=0):
        self.cap = cv2.VideoCapture(cam)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        self.hands = mp_hands.Hands(
            model_complexity=model_complexity,
            min_detection_confidence=min_detection,
            min_tracking_confidence=min_tracking,
            max_num_hands=max_hands,
        )
        self.frame_count = 0
        self.last_tips = None   # 缓存最近一帧结果

    def process(self):
        """处理一帧。返回 (frame_bgr, tips_by_hand) 或 (frame_bgr, None)。

        tips_by_hand: {"Right": [tip1..4], "Left": [tip1..4]}
        每指 tip 是手部坐标系下的 3D numpy 数组 (x, y, z)。

        使用镜像视图(自拍): 这是官方算法正确构建手部坐标系的前提。
        镜像后, 你伸右手在画面里呈"左手像" → MediaPipe 报 "Left" 是正常的。

        每帧都检测并画骨架, 保证画面稳定不闪烁。
        """
        ok, frame = self.cap.read()
        if not ok:
            return frame, None

        # 统一镜像(自拍视角)
        frame = cv2.flip(frame, 1)

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.hands.process(image)
        image.flags.writeable = True

        # 画骨架线条到画面 (每帧都画, 消除闪烁)
        if results.multi_hand_landmarks:
            self._last_landmarks = results.multi_hand_landmarks
        if getattr(self, '_last_landmarks', None):
            for hand_landmarks in self._last_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

        tips = self._extract_tips(results)
        if tips is not None:
            self.last_tips = tips
        return frame, self.last_tips

    @staticmethod
    def _extract_tips(results):
        """从 mediapipe 结果提取每手 4 指 tip 向量(手部坐标系)。"""
        if not results.multi_hand_landmarks:
            return None

        tips_by_hand = {}
        for index, handedness in enumerate(results.multi_handedness):
            cls = handedness.classification[0]
            if cls.score < 0.8:
                continue
            label = cls.label  # "Right" / "Left"

            world = results.multi_hand_world_landmarks[index]
            norm = results.multi_hand_landmarks[index]

            # 每指 tip 相对 MCP 的 3D 世界坐标向量
            tip_vecs = []
            for tip, mcp in ((mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP),
                             (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP),
                             (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_MCP),
                             (mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.THUMB_MCP)):
                t = world.landmark[tip]
                m = world.landmark[mcp]
                tip_vecs.append(np.array([t.x - m.x, t.y - m.y, t.z - m.z]))

            # 构建手部局部坐标系
            origin = np.array([norm.landmark[mp_hands.HandLandmark.WRIST].x,
                               norm.landmark[mp_hands.HandLandmark.WRIST].y,
                               norm.landmark[mp_hands.HandLandmark.WRIST].z])
            mid_mcp = np.array([norm.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x,
                                norm.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y,
                                norm.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].z])
            unit_z = _unit(mid_mcp - origin)

            pinky_mcp = np.array([norm.landmark[mp_hands.HandLandmark.PINKY_MCP].x,
                                  norm.landmark[mp_hands.HandLandmark.PINKY_MCP].y,
                                  norm.landmark[mp_hands.HandLandmark.PINKY_MCP].z])
            index_mcp = np.array([norm.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].x,
                                  norm.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y,
                                  norm.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].z])

            # 右手: 手掌朝向 y 轴指小指; 左手: 指向食指
            vec_towards_y = (pinky_mcp - origin) if label == 'Right' else (index_mcp - origin)
            cross = np.cross(vec_towards_y, unit_z)
            unit_x = _unit(cross) if np.linalg.norm(cross) > 0 else np.array([1.0, 0.0, 0.0])
            unit_y = np.cross(unit_z, unit_x)
            R = np.array([unit_x, -unit_y, unit_z])  # 手部坐标系旋转矩阵

            tips = [R @ v for v in tip_vecs]

            # 原始归一化 4 指 tip 平面坐标 (用于指间距/base 计算)
            raw_tips = np.array([[norm.landmark[t].x, norm.landmark[t].y]
                                 for t in (mp_hands.HandLandmark.INDEX_FINGER_TIP,
                                           mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                                           mp_hands.HandLandmark.RING_FINGER_TIP,
                                           mp_hands.HandLandmark.THUMB_TIP)])

            tips_by_hand[label] = {"tips": tips, "raw_tips": raw_tips}

        return tips_by_hand if tips_by_hand else None

    def draw(self, frame):
        """在画面叠画手部骨架(用于 GUI 显示)。"""
        return frame

    def release(self):
        self.cap.release()


# ============================================================================
# tip 向量 → 差动舵机 (flex/base) 映射
# ============================================================================
# 差动模型: 每指 2 舵机, servo_a = base + flex, servo_b = base - flex
#   flex 范围 [-70, +70]:  +70=伸直, -70=弯曲
#   base 固定 90 (暂不做左右摆, 保持开合稳定)
#
# 实机标定 (2026-08-19):
#   flex (弯曲/伸直): 三指用 z 分量; 拇指用 y 分量(弯曲发生在 y 轴, 符号负)
#   这是验证过"开合正常"的参数, 左右摆后续再做
FLEX_SCALE = 700.0        # 三指: z → flex
THUMB_FLEX_GAIN = -900.0  # 拇指: y → flex


def tips_to_flex_base(hand_data):
    """手部数据 → [(flex, base) x4]

    hand_data: {"tips": [tip1..4] 手部坐标 3D, "raw_tips": 归一化 2D 平面}
    """
    tips = hand_data["tips"]

    # base 固定 90 (左右摆暂缓)
    base = 90.0

    out = []
    for fi, tip in enumerate(tips):
        if fi == 3:
            # 拇指: 用 y 分量 (弯曲/伸直发生在 y 轴)
            flex = np.clip(tip[1] * THUMB_FLEX_GAIN, -70, 70)
        else:
            # 食指/中指/无名指: 用 z 分量
            flex = np.clip(tip[2] * FLEX_SCALE, -70, 70)
        out.append((float(flex), float(base)))
    return out


def tips_to_angles(hand_data):
    """手部数据 → 8 舵机角度 [servo0..7]"""
    angles = []
    for flex, base in tips_to_flex_base(hand_data):
        a = int(round(base + flex))
        b = int(round(base - flex))
        a = max(0, min(180, a))
        b = max(0, min(180, b))
        angles.extend([a, b])
    return angles
