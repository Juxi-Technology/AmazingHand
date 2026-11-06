# AmazingHand PWM 舵机版

基于 **ESP32-S3 + 8 路 PWM 舵机**的 AmazingHand 灵巧手控制方案。ESP32-S3 通过 LEDC 产生 8 路 PWM 信号直接驱动舵机，上位机（PC / 树莓派 / 其他 MCU）通过串口发送二进制帧指令，即可执行预设手势或直接指定 8 个舵机的角度。

> 这是与官方 **SCS0009 总线舵机版**并列的另一条产品线。两者的机械手相同，但舵机、驱动板、通信协议完全不同。

## 硬件

| 项目 | 型号 |
|------|------|
| 主控 | ESP32-S3 开发板（优信 YX-ESP32-S3 或同类） |
| 舵机 | 8 路 PWM 舵机——固件按 **PTK 7452 MG-D 数字舵机（333 Hz）** 标定 |
| 转接板 | PWM 舵机转接板 |
| 电源 | 5 V / 3 A，转接板与 ESP32 共地 |

> ⚠️ 常见 SG90 是 50 Hz 模拟舵机，不能直接替换当前 333 Hz 固件；如要使用 SG90，需要同时修改 `LEDC_FREQ` 和脉宽标定并重新验证。

PWM 通道与 GPIO：

| 通道 | GPIO | 对应关节 | 通道 | GPIO | 对应关节 |
|------|------|----------|------|------|----------|
| PWM1 | 4 | 食指关节 1 | PWM5 | 15 | 无名指关节 1 |
| PWM2 | 5 | 食指关节 2 | PWM6 | 16 | 无名指关节 2 |
| PWM3 | 6 | 中指关节 1 | PWM7 | 17 | 拇指关节 1 |
| PWM4 | 7 | 中指关节 2 | PWM8 | 18 | 拇指关节 2 |

## 目录内容

| 路径 | 说明 |
|------|------|
| [`firmware/AmazingHand_Serial/`](firmware/AmazingHand_Serial/) | ESP-IDF v5/v6 固件工程（ESP32-S3 + FreeRTOS） |
| [`firmware/prebuilt/amazinghand_pwm.bin`](firmware/prebuilt/amazinghand_pwm.bin) | 合并固件，可直接烧录 |
| [`tools/hand_gui.py`](tools/hand_gui.py) | Tkinter 图形界面上位机：手势按钮、差动滑块、摄像头追踪 |
| [`tools/hand_tracking.py`](tools/hand_tracking.py) | MediaPipe 手势追踪模块（供 GUI 调用） |
| [`tools/serial_test.py`](tools/serial_test.py) | 命令行 / REPL 测试工具 |
| [`docs/zh-hans/`](docs/zh-hans/) | 完整中文文档：用户手册、全流程教程、手势追踪教程、GUI 教程 |
| [`docs/en/`](docs/en/) | 完整英文翻译 |
| `docs/<lang>/README.md` | 其他语言的快速上手页 |

## 快速开始

### 1. 烧录固件

已安装 ESP-IDF 时：

```bash
cd firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

没装 ESP-IDF 时，用预编译固件（需要 `esptool`）：

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 firmware/prebuilt/amazinghand_pwm.bin
```

上电后串口会打印：

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

### 2. 桌面 GUI

```bash
pip install -r tools/requirements.txt
python tools/hand_gui.py
```

选择 COM 口 → 连接 → 点手势按钮或用滑块控制。手势追踪需要额外安装 `requirements-tracking.txt` 并运行 `tools/setup_tracking.bat`。

### 3. 网页控制

网页版同时支持 SCS0009 和 PWM 两种驱动：

- 静态页：从仓库根目录启动 `python -m http.server 8099`，打开 <http://localhost:8099/Amazinghand-web-io/>，驱动选择 **PWM（ESP32-S3）**；
- Python 服务端：`python Amazinghand-web/server.py --driver pwm`。

详见 [`Amazinghand-web/README.md`](../Amazinghand-web/README.md) 和 11 种语言教程。

## 串口协议速览

- 物理层：115200 baud，8N1，无流控
- 命令帧：`0xAA | CMD | LEN | DATA... | CHECKSUM`，`CHECKSUM = CMD ^ LEN ^ DATA...`
- 响应帧：`0xBB | CMD | STATUS | CHECKSUM`，`CHECKSUM = CMD ^ STATUS`
- 状态码：`0x00` OK、`0x01` 无效命令、`0x02` 参数错误、`0x03` 忙、`0x10` 完成
- 常用命令：`0xF0` 直驱（8 字节 0–180°）、`0xF1` 选左右手、`0xFF` 停止、`0x00` NOP

完整命令表、手势参数与接线说明见 [`docs/zh-hans/用户手册.md`](docs/zh-hans/用户手册.md)。

## 许可与来源

- 本模块代码来自钜犀科技 PWM 舵机产品线（Gitee: `white-leaf-tee/amazinghand-pwm-gpio`），随本仓库以 Apache License 2.0 分发。
- 机械设计与上游 AmazingHand 项目来自 [Pollen Robotics](https://github.com/pollen-robotics/AmazingHand)：软件 Apache 2.0，机械设计 CC BY 4.0。
- MediaPipe 等第三方组件见 [`NOTICE.md`](NOTICE.md)。
