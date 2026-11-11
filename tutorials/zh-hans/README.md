---
title: "AmazingHand 灵巧手教程总览"
description: "AmazingHand 灵巧手统一教程入口：SCS0009 串口舵机版与 PWM 舵机版的产品选型、硬件接线、快速上手、网页控制、桌面上位机、手势追踪、舵机调试和 FAQ。"
version: both
---

# AmazingHand 灵巧手教程

AmazingHand 是一款开源、可 3D 打印的仿人灵巧手：4 根手指、8 个自由度，所有驱动器内置在手部，整手约 400 g。目前提供两套硬件方案，机械手结构相同，舵机、驱动板和通信方式不同。

## 先选版本

| 对比项 | SCS0009 串口总线版 | PWM 舵机版 |
|--------|--------------------|------------|
| 推荐场景 | 精确角度控制、数据回读、接入 SO-ARM101 / LeRobot 数据采集训练 | 独立演示、手势交互、网页/桌面快速上手 |
| 舵机 | 飞特 SCS0009 串行总线舵机 ×8 | PTK 7452 MG-D **数字** PWM 舵机 ×8 |
| 舵机参数 | 2.3 kg·cm@6V，300° 可控，0.293° 精度 | 4.5 kg·cm@7.4V（5V 供电约 2.8–3 kg·cm），180°±10°，333 Hz |
| 位置/温度/电压反馈 | ✅ 支持 | ❌ 无回读，无法检测堵转或失步 |
| 主控 | 无板载，电脑/树莓派通过总线驱动板直连 | ESP32-S3 板载固件 |
| 供电 | 7–12V（DC5521）输入驱动板 | 5V / 3A 以上，必须共地 |
| 通信 | 1,000,000 波特率总线协议 | 上位机↔ESP32 串口 **115200**（舵机本身无波特率） |
| 舵机 ID | 必须设置：右手 1–8，左手 11–18 | 不设 ID，固定通道 CH1–CH8：食指 1/2、中指 3/4、无名指 5/6、拇指 7/8 |
| 固件 | 无需烧录 | 需要 ESP-IDF 编译，或直接烧录预编译 bin |

> 需要**位置回读、精度或 LeRobot 训练数据采集**，选 SCS0009；只需要**独立演示、手势互动、快速上手**，选 PWM。

完整对比与选型说明见 [版本对比](00-product/version-comparison.md)。

## 按使用方式导航

| 使用方式 | SCS0009 串口总线版 | PWM 舵机版 |
|----------|--------------------|------------|
| 快速上手 | [SCS0009 快速上手](02-quick-start/scs0009.md) | [PWM 快速上手](02-quick-start/pwm.md) |
| 网页控制 | [SCS0009 网页控制](03-web-control/scs0009.md) | [PWM 网页控制](03-web-control/pwm.md) |
| 桌面上位机 / CLI | [SCS0009 GUI 与 CLI](04-desktop/scs0009.md) | [PWM 桌面上位机](04-desktop/pwm.md) |
| 手势追踪 | [SCS0009 官方 Demo](05-hand-tracking/scs0009.md) | [PWM GUI / dora 追踪](05-hand-tracking/pwm.md) |
| 舵机调试与标定 | [SCS0009 调试与标定](06-servo-tuning/scs0009.md) | [PWM 协议与标定](06-servo-tuning/pwm.md) |
| Arduino / 二次开发 | [Arduino Nano](07-arduino/arduino-nano.md) · [示例代码](07-arduino/examples.md) | 同左（共用机械结构） |

网页控制总览（驱动切换、串口栏、界面说明）见 [网页控制 README](03-web-control/README.md)。

## 开始之前

- [产品资料](00-product/product-info.md) — 参数、定位、资料
- [版本对比与选型](00-product/version-comparison.md) — 两套硬件的完整差异
- [硬件总览](01-hardware/overview.md) — 结构、CAD、组装、3D 打印
- [SCS0009 接线](01-hardware/scs0009.md) / [PWM 接线](01-hardware/pwm.md)
- [相机套件安装](01-hardware/camera-kit.md)
- [下载与资源](00-product/downloads.md)

## 安全提示

- 外部舵机电源与 ESP32/驱动板必须**共地**。
- 首次上电前把机械手摆到中位，舵机臂按中位安装，避免顶到行程尽头。
- SCS0009 与 PWM 两套硬件**同一时刻只接一套**，不要混接。
- PWM 舵机无位置反馈，急停只能中止手势，不能像总线舵机一样读取或释放力矩。

## Languages

[简体中文](../zh-hans/README.md) | [English](../en/README.md) | [Deutsch](../de/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (BR)](../pt-br/README.md) | [Português (PT)](../pt-pt/README.md) | [繁體中文](../zh-hant/README.md)
