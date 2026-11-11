---
title: "PWM Wiring, GPIO and Power"
description: "AmazingHand PWM servo version: ESP32-S3, 8 PWM channels, GPIO mapping, power supply and servo model notes."
version: pwm
---

# PWM Wiring, GPIO and Power

In the PWM version the ESP32-S3 generates the 8 PWM signals directly, and the computer only needs to send commands over USB serial.

## Hardware list

| Item | Specification |
|------|------|
| Controller | ESP32-S3 dev board (Youxin YX-ESP32-S3 or equivalent) |
| Servos | PTK 7452 MG-D **digital** PWM servo ×8 (333 Hz) |
| Adapter board | PWM servo adapter board (8 × 3P headers + 5V/GND) |
| Power | 5V / 3A or more; the adapter board and ESP32 must share a common ground |

> The servos are rated 4.5 kg·cm@7.4V; with this solution's 5V supply the actual torque is about 2.8–3 kg·cm.
>
> ⚠️ 50 Hz analog servos such as the SG90 cannot directly replace the 333 Hz firmware; changing the model requires updating both `LEDC_FREQ` and the pulse-width calibration.

## Channel → GPIO → finger

| Channel | GPIO | Joint | Channel | GPIO | Joint |
|------|------|------|------|------|------|
| PWM1 / CH1 | 4 | Index finger joint 1 | PWM5 / CH5 | 15 | Ring finger joint 1 |
| PWM2 / CH2 | 5 | Index finger joint 2 | PWM6 / CH6 | 16 | Ring finger joint 2 |
| PWM3 / CH3 | 6 | Middle finger joint 1 | PWM7 / CH7 | 17 | Thumb joint 1 |
| PWM4 / CH4 | 7 | Middle finger joint 2 | PWM8 / CH8 | 18 | Thumb joint 2 |

- Wiring is identical for the left and right hands; the index finger is always CH1/2.
- In each finger's servo pair, the right servo uses the odd channel and the left servo the even channel.
- Channel numbers are fixed by the firmware; no servo ID needs to be set.

## Wiring steps

1. Plug the 3P connectors of the 8 servos into the adapter board's servo 1–8 pin headers according to their numbers.
2. Connect the adapter board's PWM1–PWM8 to ESP32-S3 GPIO 4, 5, 6, 7, 15, 16, 17 and 18.
3. Connect the adapter board's 5V/GND to an external 5V/3A power supply.
4. Run another set of 5V/GND from the adapter board to the ESP32-S3; **a common ground is mandatory**.
5. Servo 3P wire order: brown/black GND, red V+, orange/white/yellow signal; plug according to the adapter board's silkscreen, and do not insert it backwards.

## Power and safety

- The current is high when all 8 servos move at once; 5V/3A or more is recommended, and do not rely on USB power alone.
- Before powering up for the first time, set the hand to its middle position and install the servo horns at 90°.
- Unused channels can be left empty without affecting the others; insulate unused plugs.
- Opening the serial port may reset the ESP32; the firmware automatically returns to the middle position.

## Next steps

- [PWM quick start](../02-quick-start/pwm.md) (flash the firmware + GUI/web)
- [PWM protocol and calibration](../06-servo-tuning/pwm.md)
- [Web control](../03-web-control/pwm.md)
