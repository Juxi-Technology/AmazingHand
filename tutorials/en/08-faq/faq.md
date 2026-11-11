---
title: "Frequently Asked Questions (FAQ)"
description: "A collection of frequently asked questions about AmazingHand in general, SCS0009, PWM, web control, desktop host software and hand tracking."
version: both
---

# Frequently Asked Questions (FAQ)

## General

**Should I choose SCS0009 or PWM?**
Choose SCS0009 if you need position feedback, precision or LeRobot/SO-ARM101 data collection; choose PWM for standalone demos, gesture interaction or a quick web/desktop start. See [Version comparison](../00-product/version-comparison.md) for details.

**Can the two servo sets be connected at the same time?**
No. Power, protocol and firmware all differ, so connect only one set at a time.

**Can the hand be powered on directly?**
Before powering up for the first time, set the hand to its middle position and install the servo horns at the middle position; the external power supply must share a common ground with the driver board/ESP32.

**Can the servo model be changed?**
The SCS0009 version uses bus servos; the PWM version's firmware is calibrated for the PTK 7452 MG-D (333 Hz digital servo). 50 Hz analog servos such as the SG90 cannot directly replace the PWM version's servos; `LEDC_FREQ` and the pulse-width calibration must be changed.

## SCS0009 serial bus version

**Motion direction reversed** → check whether the wiring follows "odd ID first"; for the left hand, confirm `angle_offset_deg = -35.16`.

**Left hand's fist is not tight enough / servos buzz** → check whether the limit in `config.json` has been raised to ±120° (the default ±90 clips the left hand's fist).

**Fingers do not move / "expected N motors, found M"** → run `tools/scan_servos.py`; the left hand's IDs are the easiest to wire incorrectly (11–18, not 9–16).

**Middle position incorrect** → the middle value `-17.578125` corresponds to the official raw 451/571; to calibrate for your own mechanical assembly, edit `middle.positions` in `config.json`.

**How do I set servo IDs?** → Use the [SCS0009 debug tool](../06-servo-tuning/scs0009.md) to scan and change IDs; right hand 1–8, left hand 11–18.

**Linux cannot open the serial port** → add the current user to the `dialout` group and log in again.

**Can position/temperature/voltage be read?** → Yes; SCS0009 supports position, speed, voltage and temperature readback; for the protocol memory table see [`scs_servo_protocol.md`](../../../AmazingHandControl/docs/zh-hans/scs_servo_protocol.md).

## PWM servo version

**Connection failed / no response from the ESP32** → confirm the 115200 baud rate, the ESP32's COM port, the 5V/3A supply and common ground; opening the serial port may reset it, and the page automatically retries the NOP.

**Servos do not move or jitter** → confirm they are 333 Hz digital servos (PTK 7452 MG-D or equivalent) and that the power supply is adequate; the SG90 requires firmware changes.

**Direction reversed** → set the corresponding finger's `scale` to `-1` in `pwm.calibration` of the web `config.json`.

**Middle position incorrect** → adjust the corresponding channel's `offset_deg`; see [PWM protocol, commands and calibration](../06-servo-tuning/pwm.md) for details.

**"Busy (gesture executing)" prompt** → the firmware is executing a built-in gesture; wait for it to finish or send stop (`0xFF`).

**Does the PWM version have feedback?** → No position/temperature/voltage readback, and stall or step loss cannot be detected.

**Do PWM servos have a baud rate?** → Not the servos themselves; host ↔ ESP32 serial is fixed at 115200 8N1.

**Can I test with only some servos connected?** → Yes. Unused channels can be left empty without affecting the others; insulate unused plugs.

**The camera shows an image but the hand does not follow / responds slowly** → use even lighting, hold the palm about 40–80 cm from the camera and face it toward the lens; close other programs using the camera; confirm the serial port is connected. For GUI tracking parameters see [PWM hand tracking](../05-hand-tracking/pwm.md).

**Switching left/right hand has no effect** → the firmware switches left/right hand with `0xF1` (sent automatically when the web page connects); this setting mainly affects the thumb direction of the firmware's built-in gestures, while web poses use their own mapping for the current Target.

**Tracking image freezes / log stops** → stop tracking and start it again; if still unresponsive, close and reopen the GUI, and confirm the camera is not occupied by another program.

**Cannot find the serial port after changing USB ports** → check the new COM number in Device Manager, click "Refresh" in the GUI or web page and select it again.

## Web control

**Model failed to load / camera tracking failed to load** → confirm the page is served by a local server (not opened directly via `file://`) and that the MediaPipe resource path is accessible; the local tutorial already fixes the server-side MediaPipe routing. If it still fails, check the 404 or permission errors in the browser Console/Network.

**Camera recognition is inaccurate** → use even lighting and face the palm toward the camera; in `tracking.js`, a larger `SMOOTH` (default 0.35) is smoother but laggier.

**A finger does not follow** → re-capture the three poses; if a direction is reversed, re-capture the corresponding pose; the thumb only flexes and does not take part in splay.

**A servo reverses halfway into a fist** → splay should fade to 0 as the finger curls (`side *= (1 - curl)`); check whether the sign and magnitude of the splay control value are abnormal.

**How do I switch the web driver?** → Select SCS0009 or PWM in the "driver" dropdown at the top; PWM requires selecting the 115200 serial port; see [Web control overview](../03-web-control/README.md) for details.

## Desktop host software

**The SCS0009 GUI does not list the serial port** → re-plug the USB adapter, install the driver or restart the GUI; on Linux check `dialout`.

**Connect button greyed out** → already connected; click Disconnect first.

**Sequence does not drive all fingers** → check each step's speed and make sure every pose contains all 8 servo values.

**Blocked indicator persists** → check for mechanical binding; a large difference between target and actual position with no motion triggers "blocked".

**PWM GUI reports mediapipe missing on startup** → launch with the Python from `tools/tracking_env`, or re-run `tools/setup_tracking.bat`.

## Hand tracking

**mediapipe missing the solutions submodule** → install `mediapipe==0.10.14`, and confirm Python 3.12 is 64-bit.

**dora version incompatible** → align the dora version with `pyproject.toml` and the logs; clean up and reinstall.

**Model load failure (Chinese paths)** → put the project/models in an all-English path.

**No camera image / permissions** → grant the system camera permission; in a virtual machine, pass the USB camera through.

**What is the difference between the SCS0009 official demo and PWM GUI tracking?** → SCS0009 uses the full dora + MuJoCo IK pipeline; the PWM version provides lightweight MediaPipe tracking built into the GUI, and the dora demo is not part of the module. See [SCS0009 hand tracking](../05-hand-tracking/scs0009.md) / [PWM hand tracking](../05-hand-tracking/pwm.md) for details.

## More

- [Version comparison and selection](../00-product/version-comparison.md)
- [Hardware overview](../01-hardware/overview.md)
- [Downloads and resources](../00-product/downloads.md)
