---
title: "Arduino 与 Python 示例"
description: "AmazingHand 官方 Arduino/Python 示例：SCServo 库、Feetech 调试工具、TTL Linker 接线模式、Arduino Uno/Mega 串口与 Python 基础脚本。"
version: scs0009
---

# Arduino 与 Python 示例

本页整理 `AmazingHand-main/ArduinoExample/` 与 `AmazingHand-main/PythonExample/` 的官方示例和接线要点。

## Arduino 示例

### 准备工作

- 在 Arduino IDE 的库管理器中安装 **SCServo** 库。
- 使用 Feetech FD 调试工具设置舵机 ID（`feetech debug tool`）。
- Arduino 与 TTL Linker 之间 **RX/TX 交叉连接**。

### Link 模式：修改舵机 ID

1. 先在 Arduino 上传 `Blink` 示例。
2. 按 Link 模式接线，打开 Feetech 软件修改 ID。

![Link 模式接线](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Link-mode.jpg)

![安装 SCServo 库](../../assets/robot-arms/amazing-hand/arduino-extension/SCServo.jpg)

### Control 模式：Arduino 控制舵机

上传自定义程序后，按 Control 模式接线：

![Control 模式接线](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Control-mode.jpg)

- **Arduino Uno**（只有一个串口）：按图使用软串口/指定引脚。
- **Arduino Mega**：使用 **RX1 / TX1（19 / 18）**。

![Uno 串口接线](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Uno.jpg)

![Mega 串口接线](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Mega.jpg)

> 引脚号、库版本和 TTL Linker 方向以实际板卡丝印为准；改 ID 前先确认总线供电和共地。

## Python 示例

`AmazingHand-main/PythonExample/` 提供 4 个基础脚本：

| 脚本 | 作用 |
|------|------|
| `AmazingHand_Demo.py` | 单手基础演示：连接总线、执行动作 |
| `AmazingHand_Demo_Both.py` | 双手演示 |
| `AmazingHand_FingerTest.py` | 单指测试 |
| `AmazingHand_Hand_FingerMiddlePos.py` | 手指中位校准 |

使用前：

1. 用 Feetech 软件设置舵机 ID（右 1–8、左 11–18）。
2. 安装 `pyserial`，按脚本内的串口名/波特率修改后运行。
3. 确认外部舵机电源已接好并与总线驱动板共地。

> 这些是官方基础示例；更完整的 GUI/CLI 见 [SCS0009 桌面上位机](../04-desktop/scs0009.md)，TTL 接线与中位见 [SCS0009 舵机调试与标定](../06-servo-tuning/scs0009.md)。

## 源码位置

- [`AmazingHand-main/ArduinoExample/`](../../../AmazingHand-main/ArduinoExample/)
- [`AmazingHand-main/PythonExample/`](../../../AmazingHand-main/PythonExample/)
