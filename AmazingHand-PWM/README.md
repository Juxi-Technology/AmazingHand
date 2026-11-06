# AmazingHand PWM Servo Edition

Drive the AmazingHand dexterous hand with an **ESP32-S3 and eight PWM servos**. The ESP32-S3 generates eight LEDC PWM channels, and a host (PC, Raspberry Pi or another MCU) sends compact binary frames over a serial link to run preset gestures or set all eight servo angles directly.

> This is a separate product line alongside the official **SCS0009 serial-bus servo** version. The mechanical hand is the same; the servos, driver board and protocol are different.

## Hardware

| Item | Model |
|------|-------|
| Controller | ESP32-S3 development board (YX-ESP32-S3 or equivalent) |
| Servos | 8 × PWM servos — firmware is calibrated for **PTK 7452 MG-D digital servos (333 Hz)** |
| Adapter | PWM servo breakout board |
| Power | 5 V / 3 A, common ground with the ESP32 |

> ⚠️ A common SG90 is a 50 Hz analog servo and is **not** a drop-in replacement for the current 333 Hz firmware. Using SG90 requires changing `LEDC_FREQ` and the pulse calibration, then revalidating the hand.

PWM channels and GPIOs:

| Channel | GPIO | Joint | Channel | GPIO | Joint |
|---------|------|-------|---------|------|-------|
| PWM1 | 4 | Index joint 1 | PWM5 | 15 | Ring joint 1 |
| PWM2 | 5 | Index joint 2 | PWM6 | 16 | Ring joint 2 |
| PWM3 | 6 | Middle joint 1 | PWM7 | 17 | Thumb joint 1 |
| PWM4 | 7 | Middle joint 2 | PWM8 | 18 | Thumb joint 2 |

## Contents

| Path | Description |
|------|-------------|
| [`firmware/AmazingHand_Serial/`](firmware/AmazingHand_Serial/) | ESP-IDF v5/v6 firmware project (ESP32-S3 + FreeRTOS) |
| [`firmware/prebuilt/amazinghand_pwm.bin`](firmware/prebuilt/amazinghand_pwm.bin) | Merged firmware image, ready to flash |
| [`tools/hand_gui.py`](tools/hand_gui.py) | Tkinter GUI: gesture buttons, differential sliders, camera tracking |
| [`tools/hand_tracking.py`](tools/hand_tracking.py) | MediaPipe hand-tracking module used by the GUI |
| [`tools/serial_test.py`](tools/serial_test.py) | Command-line / REPL test tool |
| [`docs/zh-hans/`](docs/zh-hans/) | Complete Chinese manuals: user manual, workflow, tracking, GUI |
| [`docs/en/`](docs/en/) | Complete English translations |
| `docs/<lang>/README.md` | Quick-start pages in other languages |

## Quick start

### 1. Flash the firmware

With ESP-IDF installed:

```bash
cd firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

Without ESP-IDF, flash the prebuilt image with `esptool`:

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 firmware/prebuilt/amazinghand_pwm.bin
```

On boot the firmware prints:

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

### 2. Desktop GUI

```bash
pip install -r tools/requirements.txt
python tools/hand_gui.py
```

Pick the COM port, connect, then use the gesture buttons or sliders. Camera tracking needs `requirements-tracking.txt` and `tools/setup_tracking.bat`.

### 3. Web control

The web app supports both SCS0009 and PWM drivers:

- Static page: from the repository root run `python -m http.server 8099`, open <http://localhost:8099/Amazinghand-web-io/> and select **PWM (ESP32-S3)**.
- Python server: `python Amazinghand-web/server.py --driver pwm`.

See [`Amazinghand-web/README.md`](../Amazinghand-web/README.md) and the 11-language tutorials.

## Protocol at a glance

- Physical layer: 115200 baud, 8N1, no flow control
- Command frame: `0xAA | CMD | LEN | DATA... | CHECKSUM`, where `CHECKSUM = CMD ^ LEN ^ DATA...`
- Response frame: `0xBB | CMD | STATUS | CHECKSUM`, where `CHECKSUM = CMD ^ STATUS`
- Statuses: `0x00` OK, `0x01` invalid command, `0x02` invalid parameter, `0x03` busy, `0x10` completed
- Key commands: `0xF0` direct drive (8 angle bytes, 0–180°), `0xF1` select left/right hand, `0xFF` stop, `0x00` NOP

See [`docs/en/user_manual.md`](docs/en/user_manual.md) for the full command table, gesture parameters and wiring details.

## License and attribution

- This module originates from Juxi Technology's PWM servo product line (Gitee: `white-leaf-tee/amazinghand-pwm-gpio`) and is distributed with this repository under the Apache License 2.0.
- The mechanical design and upstream AmazingHand project come from [Pollen Robotics](https://github.com/pollen-robotics/AmazingHand): software Apache 2.0, mechanical design CC BY 4.0.
- Third-party components such as MediaPipe are listed in [`NOTICE.md`](NOTICE.md).
