---
title: "PWM 网页控制"
description: "AmazingHand PWM 舵机版网页控制：ESP32-S3 连接、驱动切换、与 SCS0009 的差异、角度标定与常见问题。"
version: pwm
---

# PWM 网页控制

本页是网页控制的 **PWM（ESP32-S3）版**专用说明。通用界面、启动方式、预设姿态、摄像头遥操作见 [网页控制总览](README.md)。

## 硬件与烧录

- 接线、GPIO、供电和舵机型号见 [PWM 接线、GPIO 与供电](../01-hardware/pwm.md)。
- 固件烧录（ESP-IDF 或预编译 bin）见 [PWM 快速上手](../02-quick-start/pwm.md)。
- 上位机↔ESP32 固定 **115200 8N1**；舵机本身没有波特率。

## 网页连接

1. 顶部“驱动”下拉选 **PWM（ESP32-S3）**
2. 点 **添加串口…**，选中 ESP32-S3 的 USB 串口
3. 点 **连接**：页面会自动握手（NOP）、发送左右手选择并回中位
4. 之后用滑块、预设姿态、摄像头遥操作控制；手指标题显示 **CH 1/2 …**（PWM 通道号）

![PWM 模式：顶部驱动选择与 CH 通道显示](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-port-bar.png)

![PWM 模式的手动控制面板：手指标题显示 CH 通道，力矩按钮隐藏](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-manual.png)

## 和 SCS0009 版的差异

| 项目 | SCS0009 总线版 | PWM 版 |
|------|----------------|--------|
| 串口波特率 | 1,000,000 | **115,200** |
| 驱动板 | USB 总线驱动板 | ESP32-S3 + PWM 转接板 |
| 力矩 | 可开启/释放 | **无**（固件没有力矩命令，按钮会隐藏） |
| 急停 | 松开全部力矩 | 发送 `0xFF` 中止手势，舵机仍通电保持位置 |
| 速度 | 支持速度参数 | 直驱帧无速度参数 |
| 反馈 | 位置/温度/电压/速度回读 | **无回读**，无法检测堵转或失步 |
| 左右手 | 不同舵机 ID | 同一组通道，发 `0xF1` 切换（主要影响固件手势；网页姿态用各自手的映射） |

## 角度标定

网页把姿态值换算成 8 路 0–180° 角度，默认公式：

```
angle = 90 + dir × scale × 姿态值 + offset
```

- 每根手指第一个通道 `dir = -1`，第二个通道 `dir = +1`
- 默认 `scale = 1`、`offset = 0`，即直接镜像舵机轴角度
- `mirror_pose` 为真时先交换每指两个姿态值（本仓库左右手均开启）

如果实机方向相反或中位偏了，编辑 [`config.json`](../../../Amazinghand-web-io/config.json) 的 `pwm.calibration`：

```jsonc
"pwm": {
  "calibration": {
    "right": {
      "pointer": { "scale": 1.0, "offset_deg": [0, 0] }
    }
  }
}
```

- 方向相反：把对应指的 `scale` 改为 `-1`
- 中位偏移：调 `offset_deg`（两个通道分别调）
- 逐指步骤：回中位 → 单独拖动一根手指 → 观察方向/中位 → 改 `scale`/`offset_deg` → 刷新页面重试

## 常见问题

- **连接失败 / ESP32 无响应**：确认波特率是 115200、选的是 ESP32 的 COM 口、5 V/3 A 供电和共地；打开串口后 ESP32 可能复位，页面会自动重试 NOP
- **舵机不动或抖动**：先确认舵机是 333 Hz 数字舵机（PTK 7452 MG-D 或同类），电源足够；SG90 需改固件
- **方向反了**：改对应指的 `scale` 为 `-1`
- **中位不对**：调对应通道的 `offset_deg`
- **提示“忙（手势执行中）”**：固件正在执行内置手势，等它完成或点急停（`0xFF`）
- **扫描舵机**：`tools/scan_servos.py` 只适用于 SCS0009；PWM 用 `AmazingHand-PWM/tools/serial_test.py` 或网页

---

## 相关页面

- [PWM 协议与标定](../06-servo-tuning/pwm.md)
- [PWM 桌面上位机](../04-desktop/pwm.md)
- [PWM 快速上手](../02-quick-start/pwm.md)
