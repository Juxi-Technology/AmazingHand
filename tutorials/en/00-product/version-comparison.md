---
title: "SCS0009 vs PWM Version Comparison and Selection"
description: "Complete comparison of the two AmazingHand hardware options: servos, feedback, controller, power, communication, ID/channel, firmware and use cases."
version: both
---

# SCS0009 vs PWM Version Comparison and Selection

AmazingHand's hand mechanics are the same, but there are two servo options. Selection mainly depends on whether you need **position feedback, precise angle control and data collection**.

## Quick conclusion

- **Choose SCS0009**: you need position/temperature/voltage readback, precise angles, and integration with an SO-ARM101 robot arm for LeRobot data-collection training.
- **Choose PWM**: standalone demos, gesture interaction, quick web/desktop start, and no feedback needed.
- **Do not mix them**: connect only one hardware set at a time; power, protocol and firmware all differ.

## Full comparison

| Item | SCS0009 serial bus version | PWM servo version |
|--------|--------------------|------------|
| Why choose it | Precise angle control + data readback; can integrate with an SO-ARM101 arm for LeRobot data-collection training | Standalone demos, gesture interaction, quick start |
| Servo model | Feetech SCS0009 serial bus servo ×8 | PTK 7452 MG-D **digital** PWM servo ×8 |
| Servo specs | 2.3 kg·cm@6V, 300° controllable, 0.293° resolution | 4.5 kg·cm@7.4V (about 2.8–3 kg·cm at this solution's 5V supply), 180°±10°, 333 Hz refresh |
| Position/temperature/voltage/speed feedback | ✅ readback supported | ❌ no readback; stall or step loss cannot be detected |
| Controller | none onboard; PC/Raspberry Pi connects directly through the bus driver board | ESP32-S3 onboard firmware |
| Hub | servo driver board + 9-port serial bus hub | PWM adapter board (8 × 3P headers + 5V/GND) |
| Power | 7–12V (DC5521) into the driver board; servos are nominally 6V class | 5V / 3A or more; the adapter board and ESP32 must share a common ground |
| Baud rate | **1,000,000** | no baud rate on the servos; host ↔ ESP32 serial at **115200 8N1** |
| Servo ID | must be set: right hand 1–8, left hand 11–18 | no ID; fixed channels CH1–CH8 (index 1/2, middle 3/4, ring 5/6, thumb 7/8), identical wiring for left and right hands |
| Communication link | host → driver board → bus → 8 servos | host → USB serial 115200 → ESP32 → 8 PWM channels |
| Command format | Feetech bus protocol, angles sent directly | binary frames: `0x01–0x0A / 0x0C` gestures, `0xF0` direct drive, `0xF1` left/right hand, `0x00` NOP, `0xFE` repeat, `0xFF` stop |
| Firmware | none (no flashing needed) | ESP-IDF build, or flash the prebuilt `amazinghand_pwm.bin` directly |
| Left/right hand | different servo IDs (right 1–8, left 11–18) | same set of channels, code mapping + `0xF1` to select the side |
| Torque release | torque on/off and release supported | not supported; an emergency stop only aborts the gesture, and the servos stay powered and hold position |
| Speed control | speed parameter supported | direct-drive frames have no speed parameter |

## SCS0009 version highlights

- Each servo has a unique ID; right hand 1–8, left hand 11–18. After rewiring or replacing a servo, the ID must be set again.
- Uses a serial bus and supports position, speed, voltage and temperature readback, suitable for closed-loop control and data collection.
- The PC/Raspberry Pi controls it directly through a USB bus driver board; no extra MCU firmware is needed.
- Powered by 7–12V into the bus driver board (servos are 6V class); make sure it shares a common ground with the driver board.
- Suited to training pipelines that need joint feedback, such as SO-ARM101 and LeRobot.

## PWM version highlights

- Uses **PTK 7452 MG-D digital servos** (333 Hz, 500–2500 µs); 50 Hz analog servos such as the SG90 cannot be used as drop-in replacements.
- Servos are rated 4.5 kg·cm@7.4V; this solution runs at 5V/3A, giving about 2.8–3 kg·cm of actual torque.
- The ESP32-S3 generates the 8 PWM channels; the host only needs to send commands over USB serial at 115200.
- No position feedback: angles, temperature and voltage cannot be read, and stall/step loss cannot be detected.
- Left and right hands share the same set of channels; each finger's servo pair uses odd channels on the right and even channels on the left, and the index finger is always CH1/2.
- Firmware must be flashed; the repository provides a prebuilt bin, and ESP-IDF can also be used to build it.
- Suited to standalone demos, gesture interaction and quick web/desktop start; not suited to feedback-dependent LeRobot training.

## Next steps

- [SCS0009 quick start](../02-quick-start/scs0009.md)
- [PWM quick start](../02-quick-start/pwm.md)
- [Hardware overview](../01-hardware/overview.md)
- [Downloads and resources](downloads.md)
