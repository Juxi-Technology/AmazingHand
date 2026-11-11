---
title: "AmazingHand Dexterous Hand Tutorials Overview"
description: "Unified tutorial entry for the AmazingHand dexterous hand: product selection, hardware wiring, quick start, web control, desktop host software, hand tracking, servo tuning and FAQ for the SCS0009 serial bus version and the PWM servo version."
version: both
---

# AmazingHand Dexterous Hand Tutorials

AmazingHand is an open-source, 3D-printable humanoid dexterous hand: 4 fingers and 8 degrees of freedom, with every actuator built into the hand and a total weight of about 400 g. Two hardware options are currently available; the hand mechanics are identical, but the servos, driver board and communication differ.

## Choose a version first

| Item | SCS0009 serial bus version | PWM servo version |
|--------|--------------------|------------|
| Recommended for | Precise angle control, data readback, integration with SO-ARM101 / LeRobot data-collection training | Standalone demos, gesture interaction, quick web/desktop start |
| Servos | Feetech SCS0009 serial bus servo ×8 | PTK 7452 MG-D **digital** PWM servo ×8 |
| Servo specs | 2.3 kg·cm@6V, 300° controllable, 0.293° resolution | 4.5 kg·cm@7.4V (about 2.8–3 kg·cm at 5V), 180°±10°, 333 Hz |
| Position/temperature/voltage feedback | ✅ supported | ❌ no readback; stall or step loss cannot be detected |
| Controller | none onboard; PC/Raspberry Pi connects directly through the bus driver board | ESP32-S3 with onboard firmware |
| Power | 7–12V (DC5521) into the driver board | 5V / 3A or more; common ground required |
| Communication | 1,000,000 baud bus protocol | host ↔ ESP32 serial at **115200** (the servos themselves have no baud rate) |
| Servo ID | must be set: right hand 1–8, left hand 11–18 | no ID; fixed channels CH1–CH8: index 1/2, middle 3/4, ring 5/6, thumb 7/8 |
| Firmware | none needed | ESP-IDF build, or flash the prebuilt bin directly |

> If you need **position readback, precision or LeRobot training-data collection**, choose SCS0009; if you only need **standalone demos, gesture interaction or a quick start**, choose PWM.

For the full comparison and selection guidance, see [Version comparison](00-product/version-comparison.md).

## Navigate by usage method

| Usage method | SCS0009 serial bus version | PWM servo version |
|----------|--------------------|------------|
| Quick start | [SCS0009 quick start](02-quick-start/scs0009.md) | [PWM quick start](02-quick-start/pwm.md) |
| Web control | [SCS0009 web control](03-web-control/scs0009.md) | [PWM web control](03-web-control/pwm.md) |
| Desktop host software / CLI | [SCS0009 GUI and CLI](04-desktop/scs0009.md) | [PWM desktop host software](04-desktop/pwm.md) |
| Hand tracking | [SCS0009 official demo](05-hand-tracking/scs0009.md) | [PWM GUI / dora tracking](05-hand-tracking/pwm.md) |
| Servo tuning and calibration | [SCS0009 debugging and calibration](06-servo-tuning/scs0009.md) | [PWM protocol and calibration](06-servo-tuning/pwm.md) |
| Arduino / custom development | [Arduino Nano](07-arduino/arduino-nano.md) · [Example code](07-arduino/examples.md) | Same (shared mechanics) |

For the web control overview (driver switching, serial port bar, interface guide), see [Web control README](03-web-control/README.md).

## Before you start

- [Product information](00-product/product-info.md) — specs, positioning, resources
- [Version comparison and selection](00-product/version-comparison.md) — full differences between the two hardware sets
- [Hardware overview](01-hardware/overview.md) — mechanics, CAD, assembly, 3D printing
- [SCS0009 wiring](01-hardware/scs0009.md) / [PWM wiring](01-hardware/pwm.md)
- [Camera kit installation](01-hardware/camera-kit.md)
- [Downloads and resources](00-product/downloads.md)

## Safety notes

- The external servo power supply and the ESP32/driver board must share a **common ground**.
- Before powering up for the first time, set the hand to its middle position and install the servo horns at the middle position, so they do not hit the end of travel.
- Connect only **one** of the two hardware sets (SCS0009 or PWM) at a time; do not connect both.
- PWM servos have no position feedback: an emergency stop can only abort the gesture, and cannot read or release torque the way bus servos can.

## Languages

[简体中文](../zh-hans/README.md) | [English](../en/README.md) | [Deutsch](../de/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (BR)](../pt-br/README.md) | [Português (PT)](../pt-pt/README.md) | [繁體中文](../zh-hant/README.md)
