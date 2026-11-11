---
title: "PWM Quick Start"
description: "Shortest path to get started with the AmazingHand PWM servo version: wiring, flashing the firmware, desktop GUI or web control, and first motion."
version: pwm
---

# PWM Quick Start

For the ESP32-S3 + 8-channel PWM servo version. See the chapter links for full details.

## 1. Wiring

- Plug the 8 PWM servos into the adapter board's servo 1–8 headers according to their numbers.
- Connect the adapter board's PWM1–8 to ESP32-S3 GPIO 4, 5, 6, 7, 15, 16, 17 and 18.
- Connect the adapter board's 5V/GND to a 5V/3A power supply, with a common ground to the ESP32.
- Detailed wiring: [PWM wiring, GPIO and power](../01-hardware/pwm.md).

> The servos must be **PTK 7452 MG-D digital servos (333 Hz)** or equivalent; 50 Hz analog servos such as the SG90 cannot be used as direct replacements.

## 2. Flash the firmware

### Option A: prebuilt bin (recommended)

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  AmazingHand-PWM/firmware/prebuilt/amazinghand_pwm.bin
```

### Option B: ESP-IDF build

```bash
cd AmazingHand-PWM/firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

Firmware project structure:

```text
firmware/AmazingHand_Serial/
├── main/main.c                  FreeRTOS tasks, command queue and initialization
└── components/
    ├── hand_servo/              LEDC PWM driver and servo calibration
    ├── hand_gestures/           Gesture parameter macros and gesture functions
    └── hand_protocol/           Serial frame parsing and command dispatch
```

> The ESP-IDF build does not support Chinese characters in paths: both the project directory and the user directory must use English characters. ESP-IDF v5.x / v6.x is recommended, and the target chip must be **ESP32-S3**.

After power-up the serial port should print:

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

## 3. Connect the host

| Method | Entry point |
|------|------|
| Desktop GUI | [PWM desktop host software](../04-desktop/pwm.md): `python AmazingHand-PWM/tools/hand_gui.py` |
| Web control | [PWM web control](../03-web-control/pwm.md): select driver **PWM (ESP32-S3)**, serial port 115200 |
| Command-line test | `python AmazingHand-PWM/tools/serial_test.py COM3 nop` |

## 4. First motion

1. After connecting, the firmware first returns to the middle position (90°); confirm there is no abnormal noise or binding.
2. Use the single-finger sliders to check the direction and middle position one finger at a time.
3. Then try small-range poses such as "open / fist".
4. If a direction is reversed or the middle position is off, adjust it as described in [PWM protocol and calibration](../06-servo-tuning/pwm.md).

## Next steps

- [PWM protocol and calibration](../06-servo-tuning/pwm.md)
- [PWM hand tracking](../05-hand-tracking/pwm.md)
- [Version comparison and selection](../00-product/version-comparison.md)
