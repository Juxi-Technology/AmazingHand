---
title: "PWM 快速上手"
description: "AmazingHand PWM 舵机版最短上手路径：接线、烧录固件、桌面 GUI 或网页控制、首次动作。"
version: pwm
---

# PWM 快速上手

适合 ESP32-S3 + 8 路 PWM 舵机版本。完整说明见各章节链接。

## 1. 接线

- 8 个 PWM 舵机按编号插到转接板舵机 1–8。
- 转接板 PWM1–8 接 ESP32-S3 GPIO 4、5、6、7、15、16、17、18。
- 转接板 5V/GND 接 5V/3A 电源，并与 ESP32 共地。
- 详细接线：[PWM 接线、GPIO 与供电](../01-hardware/pwm.md)。

> 舵机必须是 **PTK 7452 MG-D 数字舵机（333 Hz）** 或同类；SG90 等 50 Hz 模拟舵机不能直接替换。

## 2. 烧录固件

### 方式 A：预编译 bin（推荐）

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  AmazingHand-PWM/firmware/prebuilt/amazinghand_pwm.bin
```

### 方式 B：ESP-IDF 编译

```bash
cd AmazingHand-PWM/firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

固件工程结构：

```text
firmware/AmazingHand_Serial/
├── main/main.c                  FreeRTOS 任务、命令队列与初始化
└── components/
    ├── hand_servo/              LEDC PWM 驱动与舵机校准
    ├── hand_gestures/           手势参数宏与手势函数
    └── hand_protocol/           串口帧解析与命令分发
```

> ESP-IDF 编译不支持中文路径：工程目录和用户目录都要使用英文；建议 ESP-IDF v5.x / v6.x，目标芯片选 **ESP32-S3**。

上电后串口应打印：

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

## 3. 连接上位机

| 方式 | 入口 |
|------|------|
| 桌面 GUI | [PWM 桌面上位机](../04-desktop/pwm.md)：`python AmazingHand-PWM/tools/hand_gui.py` |
| 网页控制 | [PWM 网页控制](../03-web-control/pwm.md)：驱动选 **PWM（ESP32-S3）**，串口 115200 |
| 命令行测试 | `python AmazingHand-PWM/tools/serial_test.py COM3 nop` |

## 4. 首次动作

1. 连接后固件会先回中位（90°），确认没有异响/卡涩。
2. 用单指滑块逐个确认方向和中位。
3. 再试“张开 / 握拳”等小范围姿态。
4. 方向反了或中位偏了，按 [PWM 协议与标定](../06-servo-tuning/pwm.md) 调整。

## 下一步

- [PWM 协议与标定](../06-servo-tuning/pwm.md)
- [PWM 手势追踪](../05-hand-tracking/pwm.md)
- [版本对比与选型](../00-product/version-comparison.md)
