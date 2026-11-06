# AmazingHand PWM Servo Edition — Quick Start

Drive the AmazingHand with an **ESP32-S3 and 8 PWM servos**. Complete manuals are in this `docs/` folder.

## Hardware

| Item | Model |
|------|-------|
| Controller | ESP32-S3 dev board (YX-ESP32-S3 or equivalent) |
| Servos | 8 PWM servos — firmware calibrated for **PTK 7452 MG-D digital servos (333 Hz)** |
| Adapter | PWM servo breakout board |
| Power | 5 V / 3 A, common ground with the ESP32 |

> SG90 and other 50 Hz analog servos are **not** drop-in replacements for the 333 Hz firmware.

| Channel | GPIO | Joint | Channel | GPIO | Joint |
|---------|------|-------|---------|------|-------|
| PWM1 | 4 | Index 1 | PWM5 | 15 | Ring 1 |
| PWM2 | 5 | Index 2 | PWM6 | 16 | Ring 2 |
| PWM3 | 6 | Middle 1 | PWM7 | 17 | Thumb 1 |
| PWM4 | 7 | Middle 2 | PWM8 | 18 | Thumb 2 |

## 1. Flash the firmware

With ESP-IDF:

```bash
cd firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

With the prebuilt image and `esptool`:

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  firmware/prebuilt/amazinghand_pwm.bin
```

The serial port runs at **115200-8N1** and prints a startup banner.

## 2. Control the hand

Desktop GUI:

```bash
pip install -r tools/requirements.txt
python tools/hand_gui.py
```

Camera tracking needs the extra environment created by `tools/setup_tracking.bat`, then:

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

Web control: open the repository's `Amazinghand-web-io/` page (or run `Amazinghand-web/server.py --driver pwm`), select the **PWM (ESP32-S3)** driver, pick the ESP32 serial port and connect.

## 3. Full documentation

| Document | Contents |
|----------|----------|
| [`../en/user_manual.md`](../en/user_manual.md) / [`../zh-hans/用户手册.md`](../zh-hans/用户手册.md) | Protocol, command reference, wiring, calibration, FAQ |
| [`../en/full_workflow.md`](../en/full_workflow.md) / [`../zh-hans/全流程使用教程.md`](../zh-hans/全流程使用教程.md) | End-to-end workflow |
| [`../en/gui_usage.md`](../en/gui_usage.md) / [`../zh-hans/使用教程.md`](../zh-hans/使用教程.md) | GUI and serial test tool |
| [`../en/hand_tracking.md`](../en/hand_tracking.md) / [`../zh-hans/手势追踪教程.md`](../zh-hans/手势追踪教程.md) | MediaPipe hand tracking |

## 4. Common issues

- **No response**: check 115200 baud, the ESP32 COM port, 5 V / 3 A power and common ground. The page retries the NOP handshake automatically.
- **Servo does not move / jitters**: verify the servo is a 333 Hz digital servo and the supply is adequate.
- **Direction reversed**: set the corresponding finger's `scale` to `-1` in `Amazinghand-web-io/config.json` under `pwm.calibration`.
- **Middle position off**: adjust `offset_deg` for that channel.
- **Busy status**: the firmware is running a built-in gesture; wait or send stop (`0xFF`).
