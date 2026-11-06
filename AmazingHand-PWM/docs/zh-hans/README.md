# AmazingHand PWM 舵机版 — 快速上手

用 **ESP32-S3 + 8 路 PWM 舵机**驱动 AmazingHand。完整手册见本 `docs/` 目录。

## 硬件

| 项目 | 型号 |
|------|------|
| 主控 | ESP32-S3 开发板（优信 YX-ESP32-S3 或同类） |
| 舵机 | 8 个 PWM 舵机——固件按 **PTK 7452 MG-D 数字舵机（333 Hz）** 标定 |
| 转接板 | PWM 舵机转接板 |
| 电源 | 5 V / 3 A，转接板与 ESP32 共地 |

> SG90 等 50 Hz 模拟舵机**不能**直接替换 333 Hz 固件。

| 通道 | GPIO | 关节 | 通道 | GPIO | 关节 |
|------|------|------|------|------|------|
| PWM1 | 4 | 食指 1 | PWM5 | 15 | 无名指 1 |
| PWM2 | 5 | 食指 2 | PWM6 | 16 | 无名指 2 |
| PWM3 | 6 | 中指 1 | PWM7 | 17 | 拇指 1 |
| PWM4 | 7 | 中指 2 | PWM8 | 18 | 拇指 2 |

## 1. 烧录固件

使用 ESP-IDF：

```bash
cd firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

使用预编译镜像和 `esptool`：

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  firmware/prebuilt/amazinghand_pwm.bin
```

串口参数为 **115200-8N1**，上电后会打印启动信息。

## 2. 控制灵巧手

桌面 GUI：

```bash
pip install -r tools/requirements.txt
python tools/hand_gui.py
```

摄像头追踪需要先运行 `tools/setup_tracking.bat` 创建环境，然后：

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

网页控制：打开仓库的 `Amazinghand-web-io/` 页面（或运行 `Amazinghand-web/server.py --driver pwm`），
驱动选 **PWM（ESP32-S3）**，选中 ESP32 串口并连接。

## 3. 完整文档

| 文档 | 内容 |
|------|------|
| [`用户手册.md`](用户手册.md) | 协议、命令参考、接线、标定、常见问题 |
| [`全流程使用教程.md`](全流程使用教程.md) | 从环境准备到手势追踪的完整流程 |
| [`使用教程.md`](使用教程.md) | GUI 与命令行测试工具 |
| [`手势追踪教程.md`](手势追踪教程.md) | GUI 内置 MediaPipe 手势追踪 |

## 4. 常见问题

- **无响应**：检查波特率 115200、ESP32 的 COM 口、5 V/3 A 供电和共地；网页会自动重试 NOP 握手。
- **舵机不动 / 抖动**：确认舵机是 333 Hz 数字舵机，电源足够。
- **方向反了**：在 `Amazinghand-web-io/config.json` 的 `pwm.calibration` 里把对应指的 `scale` 改为 `-1`。
- **中位偏了**：调整对应通道的 `offset_deg`。
- **提示忙**：固件正在执行内置手势，等待完成或发送停止（`0xFF`）。
