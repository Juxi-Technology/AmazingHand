---
title: "AmazingHand 产品资料"
description: "AmazingHand 灵巧手产品资料：机械结构、尺寸、负载、两套舵机方案与开源资源。"
version: both
---

# AmazingHand 产品资料

AmazingHand 是一款开源、可 3D 打印的仿人灵巧手，面向具身智能研究、机器人教育和人机交互原型。机械手本体相同，目前提供 **SCS0009 串口总线舵机** 和 **PWM 舵机（ESP32-S3）** 两套硬件方案。

## 机械结构

- **4 根手指、8 个自由度**：每根手指 2 个自由度（屈伸 + 收展），由两个舵机通过并联机构差动驱动。
- **驱动器内置**：所有舵机安装在手部，不需要向前臂引出线缆。
- **3D 打印**：外壳和连杆可打印，整手约 400 g。
- **双手支持**：可单独使用左手或右手，也可双手机器人协同。
- **腕部接口**：原版设计适配 Reachy 2 的 Orbita 3D 腕部，也可转接其他机械臂。

## 基础参数

| 参数 | 规格 |
|------|------|
| 重量 | 约 0.416 kg |
| 手指数量 | 4 |
| 单指自由度 | 2 DoF |
| 伸展高度（不含底座） | 195 mm |
| 手掌宽度 | 105 mm |
| 手掌厚度 | 约 90 mm |
| 食指与拇指最大张开距离 | 180 mm |
| 单指负重 | 约 0.2 kg |
| 四指紧握最大负重 | 约 0.5 kg |

> 负载、电压和舵机参数随所选舵机版本不同；完整对照见 [版本对比与选型](version-comparison.md)。

## 两套硬件方案

| 项目 | SCS0009 串口总线版 | PWM 舵机版 |
|------|--------------------|------------|
| 舵机 | 飞特 SCS0009 ×8 | PTK 7452 MG-D 数字 PWM 舵机 ×8 |
| 控制 | 电脑/树莓派 + 总线驱动板 | ESP32-S3 板载固件 |
| 反馈 | 位置/速度/电压/温度回读 | 无回读 |
| 适用 | 精度、数据采集、LeRobot / SO-ARM101 | 独立演示、手势交互、快速上手 |

## 软件生态

- **网页控制**：浏览器滑块、19 个预设姿态、MediaPipe 摄像头遥操作，支持 SCS0009 / PWM 驱动切换。
- **桌面上位机**：SCS0009 使用 `AmazingHandControl`（Tkinter GUI + CLI）；PWM 使用 `AmazingHand-PWM/tools/hand_gui.py`。
- **手势追踪**：SCS0009 提供官方 dora + MuJoCo IK Demo；PWM 提供 GUI 内置 MediaPipe 追踪。
- **开源资源**：CAD、组装/打印文档、Arduino/Python 示例均在仓库中。

## 开源资源

- [组装指南 PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [3D 打印建议 PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand 概览 PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [CAD / STL / STEP](../../../AmazingHand-main/cad/)
- [官方上游项目（Pollen Robotics）](https://github.com/pollen-robotics/AmazingHand)

## 下一步

- [版本对比与选型](version-comparison.md)
- [硬件总览](../01-hardware/overview.md)
- [SCS0009 快速上手](../02-quick-start/scs0009.md)
- [PWM 快速上手](../02-quick-start/pwm.md)
