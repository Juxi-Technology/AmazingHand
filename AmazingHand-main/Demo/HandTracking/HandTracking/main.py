# ==============================================
# Imports - MediaPipe compatibility ensured
# ==============================================
import os
import sys

# mediapipe 中文路径兼容补丁（必须在 import mediapipe 之前加载）
# main.py 位于 HandTracking/HandTracking/，补丁位于 HandTracking/（上一级）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mediapipe_patch  # noqa: E402,F401  （导入即注入补丁）

# MediaPipe - fixed at version 0.10.9/0.10.14 for solutions API
import mediapipe as mp  # noqa: E402
from mediapipe import solutions  # noqa: E402

# Other imports
import numpy as np

# ==============================================
# 正常导入
# ==============================================
import argparse
import os
import time

import cv2
import pyarrow as pa
from dora import Node
from scipy.spatial.transform import Rotation

mp_drawing = solutions.drawing_utils
mp_drawing_styles = solutions.drawing_styles
mp_hands = solutions.hands

def process_img(hand_proc, image):
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hand_proc.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    r_res=None
    l_res=None
    if results.multi_hand_landmarks:
        for index,handedness_classif in enumerate(results.multi_handedness):
            if handedness_classif.classification[0].score>0.8:
                hand_landmarks=results.multi_hand_world_landmarks[index]
                hand_landmarks_norm=results.multi_hand_landmarks[index]

                tip1_x=hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x-hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].x
                tip1_y=hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y-hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y
                tip1_z=hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].z-hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].z

                tip2_x=hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x-hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x
                tip2_y=hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y-hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y
                tip2_z=hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].z-hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].z

                tip3_x=hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x-hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].x
                tip3_y=hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y-hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y
                tip3_z=hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].z-hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].z

                tip4_x=hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x-hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP].x
                tip4_y=hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y-hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP].y
                tip4_z=hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].z-hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP].z

                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks_norm,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

                origin=np.array([hand_landmarks_norm.landmark[mp_hands.HandLandmark.WRIST].x,hand_landmarks_norm.landmark[mp_hands.HandLandmark.WRIST].y,hand_landmarks_norm.landmark[mp_hands.HandLandmark.WRIST].z])
                mid_mcp=np.array([hand_landmarks_norm.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x,hand_landmarks_norm.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y,hand_landmarks_norm.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].z])
                unit_z=mid_mcp-origin
                if np.linalg.norm(unit_z) > 0:
                    unit_z=unit_z/np.linalg.norm(unit_z)
                else:
                    unit_z = np.array([0, 0, 1])

                pinky_mcp=np.array([hand_landmarks_norm.landmark[mp_hands.HandLandmark.PINKY_MCP].x,hand_landmarks_norm.landmark[mp_hands.HandLandmark.PINKY_MCP].y,hand_landmarks_norm.landmark[mp_hands.HandLandmark.PINKY_MCP].z])
                index_mcp=np.array([hand_landmarks_norm.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].x,hand_landmarks_norm.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y,hand_landmarks_norm.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].z])

                if handedness_classif.classification[0].label=='Right':
                    vec_towards_y=pinky_mcp-origin
                if handedness_classif.classification[0].label=='Left':
                    vec_towards_y=index_mcp-origin

                cross_product = np.cross(vec_towards_y, unit_z)
                if np.linalg.norm(cross_product) > 0:
                    unit_x = cross_product / np.linalg.norm(cross_product)
                else:
                    unit_x = np.array([1, 0, 0])
                unit_y=np.cross(unit_z, unit_x)

                if handedness_classif.classification[0].label=='Right':
                    R=np.array([unit_x,-unit_y,unit_z]).reshape((3,3))
                if handedness_classif.classification[0].label=='Left':
                    R=np.array([unit_x,-unit_y,unit_z]).reshape((3,3))
                tip1=R@np.array([tip1_x,tip1_y,tip1_z])
                tip2=R@np.array([tip2_x,tip2_y,tip2_z])
                tip3=R@np.array([tip3_x,tip3_y,tip3_z])
                tip4=R@np.array([tip4_x,tip4_y,tip4_z])

                if handedness_classif.classification[0].label=='Right':
                    r_res=[{'r_tip1': tip1,'r_tip2': tip2,'r_tip3': tip3,'r_tip4': tip4}]
                elif handedness_classif.classification[0].label=='Left':
                    l_res=[{'l_tip1': tip1,'l_tip2': tip2,'l_tip3': tip3,'l_tip4': tip4}]
    return image,r_res,l_res

def main():
    node = Node()
    pa.array([])
    cap = cv2.VideoCapture(0)
    # 降低摄像头分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    # 降低帧率
    cap.set(cv2.CAP_PROP_FPS, 15)

    with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            max_num_hands=2) as hands:
        frame_count = 0
        show_window = True  # 设置为False以禁用显示

        for event in node:
            event_type = event["type"]

            if event_type == "INPUT":
                event_id = event["id"]

                if event_id == "tick":
                    ret, frame = cap.read()
                    if not ret:
                        continue
                    # 每2帧处理一次
                    frame_count += 1
                    if frame_count % 2 != 0:
                        continue
                    frame = cv2.flip(frame, 1)
                    frame,r_res,l_res=process_img(hands,frame)

                    if r_res is not None:
                        node.send_output('r_hand_pos',pa.array(r_res))
                    if l_res is not None:
                        node.send_output('l_hand_pos',pa.array(l_res))
                    
                    # 仅在需要时显示窗口
                    if show_window:
                        cv2.imshow('MediaPipe Hands', frame)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            break
                    else:
                        cv2.waitKey(1)

            elif event_type == "ERROR":
                raise RuntimeError(event["error"])
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()