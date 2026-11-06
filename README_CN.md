[English](README.md) | 简体中文

# AmazingHand

![AmazingHand](AmazingHand-main/assets/AmazingHand_Couv.jpg)

AmazingHand 是一款开源、可 3D 打印的仿生人形机械手，**4 根手指、8 个自由度**。所有驱动都内置在手掌之内——无需向前臂引出线缆——整手约 400 g，零件成本低于 €200。

本仓库汇集了 [Pollen Robotics](https://github.com/pollen-robotics/AmazingHand) 原项目的机械设计与固件，以及钜犀科技（Juxi Technology）开发的控制软件、网页控制器与舵机工具。

## 📦 仓库内容

| 文件夹 | 说明 | README |
|--------|------|--------|
| **`AmazingHand-main/`** | 原版设计：STL/STEP CAD 文件、Arduino 与 Python 示例、演示程序（控制、仿真、手势追踪）、组装与 3D 打印指南、BOM 清单 | [English](AmazingHand-main/README.md) · [中文](AmazingHand-main/README_CN.md) |
| **`AmazingHandControl/`** | Python 控制工具：Tkinter 图形界面与命令行工具，支持标定、手势预设、序列与实时舵机控制 | [English](AmazingHandControl/README.md) · [中文](AmazingHandControl/README_CN.md) |
| **`SCS0009_ServoController/`** | SCS0009 舵机调试工具：PySide6 图形界面，可扫描总线、读写全部 44 个寄存器、修改波特率、恢复出厂设置，并以 `.xdat` 备份参数 | [English](SCS0009_ServoController/README.md) · [中文](SCS0009_ServoController/README_CN.md) |
| **`Amazinghand-web/`** | 网页控制：8 个舵机滑块、19 个预设手势，以及完全在页面内本地运行的 MediaPipe 摄像头遥操作——左手或右手、中英双语界面、11 种语言教程；同时支持 SCS0009 总线舵机与 PWM 舵机 | [English](Amazinghand-web/README.md) · [中文](Amazinghand-web/tutorials/zh-hans/README.md) |
| **`AmazingHand-PWM/`** | PWM 舵机版本：ESP32-S3 固件（ESP-IDF）、Tkinter 上位机、MediaPipe 手势追踪、串口测试工具、完整中文/英文文档 | [English](AmazingHand-PWM/README.md) · [中文](AmazingHand-PWM/README_CN.md) |

## 🚀 快速上手

| 我想做什么 | 去哪里 |
|-----------|--------|
| 用浏览器控制灵巧手——滑块、预设手势、摄像头遥操作 | [`Amazinghand-web/`](Amazinghand-web/README.md) —— `pip install -r requirements.txt`，再 `python server.py --no-connect`，打开 <http://localhost:8000> |
| 使用 PWM 舵机版本——ESP32-S3 直驱 8 路 PWM | [`AmazingHand-PWM/`](AmazingHand-PWM/README_CN.md) —— 烧录固件后用 `tools/hand_gui.py` 或网页版（驱动选 PWM），详见模块文档 |
| 跑桌面端 Demo——仿真、手势追踪、舵机控制 | [`AmazingHand-main/Demo/`](AmazingHand-main/Demo/README.md) —— 一键部署脚本：[Windows](AmazingHand-main/Demo/Windows_Deploy_Scripts/)、[Linux](AmazingHand-main/Demo/Linux_Deploy_Scripts/)、[macOS](AmazingHand-main/Demo/Mac_Deploy_Scripts/) |
| 离线标定舵机或编排手势 | [`AmazingHandControl/`](AmazingHandControl/README.md) · [`SCS0009_ServoController/`](SCS0009_ServoController/README.md) |

需要的硬件：装配好的灵巧手、外部 5 V / 2 A 电源，以及 USB 串口总线驱动板（见下方[硬件](#-硬件)）。

## 🔧 硬件

- 8 个 Feetech **SCS0009** 舵机（电位器反馈，10 位分辨率，0–1023）
- 外部 5 V / 2 A 电源
- 串口总线驱动板，或 Arduino + Feetech TTL Linker
- 3D 打印件——见 [BOM 清单](AmazingHand-main/README.md#bom-bill-of-materials)

**PWM 舵机版本**（见 [`AmazingHand-PWM/`](AmazingHand-PWM/README_CN.md)）：

- 8 个 PWM 舵机——固件按 PTK 7452 MG-D 数字舵机（333 Hz）标定；SG90 等 50 Hz 模拟舵机不能直接替换
- ESP32-S3 开发板 + PWM 舵机转接板
- 外部 5 V / 3 A 电源，与 ESP32 共地

每根手指由一个并联机构驱动：两个舵机分别控制其屈伸（flexion/extension）与收展（abduction/adduction）。

## 📖 文档

- [组装指南](AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [3D 打印建议](AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand 概览](AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [中文 BOM 清单](https://docs.google.com/spreadsheets/d/1fHZiTky79vyZwICj5UGP2c_RiuLLm89K8HrB3vpb2h4/edit?gid=837395814#gid=837395814)

## 📄 许可与署名

- 软件：[Apache License 2.0](AmazingHand-main/LICENSE)
- 机械设计：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- `SCS0009_ServoController/`：[MIT](SCS0009_ServoController/LICENSE)
- `AmazingHand-PWM/`：来源与第三方组件见 [NOTICE](AmazingHand-PWM/NOTICE.md)
- 随 `Amazinghand-web/` 一起分发的第三方组件（MediaPipe 等）：见[其 NOTICE](Amazinghand-web/NOTICE.md)

基于 Pollen Robotics 的 [AmazingHand](https://github.com/pollen-robotics/AmazingHand) 项目。
