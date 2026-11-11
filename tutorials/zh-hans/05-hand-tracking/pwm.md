---
title: "PWM 手势追踪（GUI 内置 MediaPipe）"
description: "AmazingHand PWM 舵机版手势追踪：GUI 内置 MediaPipe、依赖安装、运行、原理与局限、常见问题。"
version: pwm
---

# PWM 手势追踪（GUI 内置 MediaPipe）

> 以下命令在仓库的 `AmazingHand-PWM/` 目录下执行。

本页介绍 **PWM 舵机版**的手势追踪：GUI 内置 MediaPipe，摄像头识别手部关键点，实时映射到 8 路 PWM 舵机。完整的 dora + MuJoCo IK 链路属于 SCS0009 官方 Demo，见 [SCS0009 手势追踪](scs0009.md)。

> 链路：摄像头 → MediaPipe 手部骨架 → 四指弯曲/伸直角度 → ESP32 → PWM 舵机
>
> 适用：ESP32-S3 + 8 路 PWM 舵机。固件烧录见 [PWM 快速上手](../02-quick-start/pwm.md)，协议见 [PWM 协议与标定](../06-servo-tuning/pwm.md)。

> 需要完整 IK（MuJoCo + dora + Rust）的官方 Demo 不随本模块分发；本教程只介绍模块自带的 GUI 内置追踪。

## 一、前置条件

1. **硬件**：ESP32-S3 + 8 路 PWM 舵机通电、USB 接好、摄像头可用。
2. **固件**：已烧录（见 [PWM 快速上手](../02-quick-start/pwm.md)）。
3. **Python**：64 位 Python 3.12（mediapipe 0.10.14 只提供 64 位 wheel）。

## 二、安装追踪依赖

在模块根目录（`AmazingHand-PWM/`）执行：

```bash
tools/setup_tracking.bat
```

脚本会自动：查找 64 位 Python → 创建 `tools/tracking_env` 虚拟环境 → 安装 `tools/requirements-tracking.txt`（mediapipe 0.10.14、numpy<2、scipy、opencv、Pillow、pyserial）→ 验证 mediapipe。

> 也可以手动安装（用 64 位 Python 3.12）：
> ```bash
> python -m pip install -r tools/requirements-tracking.txt
> ```

## 三、运行

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

1. 顶部选 ESP32 的 COM 口 → 点「连接」。
2. 滚动到「手势追踪 (MediaPipe 摄像头)」面板。
3. 选摄像头号（默认 0）→ 点「开始追踪」。
4. 把手放进画面，灵巧手跟随弯曲/伸直；点「停止追踪」结束。

![GUI 内置手势追踪面板：摄像头选择、开始追踪与状态提示](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-tracking.png)

## 四、原理与局限

- MediaPipe 0.10.14 提取 4 指指尖的 3D 向量（手部坐标系）。
- `hand_tracking.py` 的 `tips_to_angles()` 把每指映射为差动角度：
  - flex（弯曲/伸直）：三指用 z 分量，拇指用 y 分量；
  - base（左右摆）：固定 90（暂未实现左右摆）。
- 这些是**控制轴**；下发时程序再把它们合成为每根手指两个舵机的角度（同向=侧摆，反向=屈伸）。
- GUI 内置 EMA 平滑（alpha=0.4）+ 60 ms 节流，减少抖动。

局限：没有 IK，精度不如完整的 MuJoCo + dora 链路；适合演示和快速上手。

### 参数标定

- `hand_tracking.py` 底部的 `FLEX_SCALE` / `THUMB_FLEX_GAIN` 控制屈伸幅度和方向（当前代码取值以文件为准）。
- 左右摆暂未实现，`base` 固定 90；需要左右摆请使用 SCS0009 官方 dora Demo。
- 修改后重新启动 GUI 生效。

## 五、切换左右手

在 GUI 顶部勾选「右手」/「左手」。切换后拇指镜像方向会不同，如果发现反了，勾选另一侧测试。

## 六、常见问题

| 现象 | 处理 |
|------|------|
| 舵机完全不动 | 查供电（5V 3A）、COM 口、接线；确认固件已烧录 |
| 摄像头没画面 | 允许摄像头权限（设置→隐私→相机） |
| 手不跟随 / 迟钝 | 光线充足、手完整入画、动作慢一点幅度大一点 |
| 手型反了 / 拇指方向反 | 勾选相反的左右手 |
| 换了 USB 口找不到串口 | 在 GUI 里重新选 COM 口 |
| 启动就报 mediapipe 缺失 | 用 `tools\tracking_env\Scripts\python` 启动，或重跑 `tools/setup_tracking.bat` |

## 七、完整 IK / SCS0009 总线舵机

- 完整 IK 链路（摄像头 → MediaPipe → MuJoCo + mink IK → AHControl → ESP32）来自独立的 dora Demo 项目，不在本模块内；需要时请使用原始交付包或 MediaPipe 项目。
- SCS0009 总线舵机由仓库的 `Amazinghand-web/` 与 `AmazingHandControl/` 支持。

## 目录说明

| 路径 | 内容 |
|------|------|
| `tools/hand_gui.py` | Tkinter 上位机（手势、直驱、差动、内置追踪） |
| `tools/hand_tracking.py` | MediaPipe 手部追踪与角度映射 |
| `tools/setup_tracking.bat` | 创建 `tools/tracking_env` 并安装追踪依赖 |
| `tools/requirements-tracking.txt` | 追踪依赖清单 |
| `tools/serial_test.py` | 命令行串口测试 |
