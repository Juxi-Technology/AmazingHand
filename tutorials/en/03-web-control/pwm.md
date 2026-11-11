---
title: "PWM Web Control"
description: "AmazingHand PWM servo version web control: ESP32-S3 connection, driver switching, differences from SCS0009, angle calibration and FAQ."
version: pwm
---

# PWM Web Control

This page is the **PWM (ESP32-S3) version**-specific guide for web control. For the general interface, startup, preset poses and camera teleoperation, see the [web control overview](README.md).

## Hardware and flashing

- For wiring, GPIO, power and the servo model, see [PWM wiring, GPIO and power](../01-hardware/pwm.md).
- For firmware flashing (ESP-IDF or the prebuilt bin), see [PWM quick start](../02-quick-start/pwm.md).
- Host ↔ ESP32 is fixed at **115200 8N1**; the servos themselves have no baud rate.

## Connecting from the web page

1. In the "driver" dropdown at the top, select **PWM (ESP32-S3)**
2. Click **Add port…** and select the ESP32-S3's USB serial port
3. Click **Connect**: the page automatically performs a handshake (NOP), sends the left/right hand selection and returns to middle
4. After that, use the sliders, preset poses and camera teleoperation to control it; the finger headings show **CH 1/2 …** (PWM channel numbers)

![PWM mode: driver selection at the top and CH channel display](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-port-bar.png)

![PWM mode manual control panel: finger headings show CH channels, torque button hidden](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-manual.png)

## Differences from the SCS0009 version

| Item | SCS0009 bus version | PWM version |
|------|----------------|--------|
| Serial baud rate | 1,000,000 | **115,200** |
| Driver board | USB bus driver board | ESP32-S3 + PWM adapter board |
| Torque | can be enabled/released | **none** (the firmware has no torque command; the button is hidden) |
| E-stop | releases all torque | sends `0xFF` to abort the gesture; the servos stay powered and hold position |
| Speed | supports a speed parameter | direct-drive frames have no speed parameter |
| Feedback | position/temperature/voltage/speed readback | **no readback**; stall or step loss cannot be detected |
| Left/right hand | different servo IDs | same set of channels, send `0xF1` to switch (mainly affects firmware gestures; the web poses use each hand's own mapping) |

## Angle calibration

The web page converts pose values into 8 angles in the range 0–180°; the default formula is:

```
angle = 90 + dir × scale × pose value + offset
```

- The first channel of each finger has `dir = -1`, the second has `dir = +1`
- By default `scale = 1` and `offset = 0`, i.e. the servo shaft angle is mirrored directly
- When `mirror_pose` is true, the two pose values of each finger are swapped first (enabled for both hands in this repository)

If the direction is reversed on the real hardware or the middle position is off, edit `pwm.calibration` in [`config.json`](../../../Amazinghand-web-io/config.json):

```jsonc
"pwm": {
  "calibration": {
    "right": {
      "pointer": { "scale": 1.0, "offset_deg": [0, 0] }
    }
  }
}
```

- Direction reversed: set the corresponding finger's `scale` to `-1`
- Middle position offset: adjust `offset_deg` (the two channels separately)
- Per-finger procedure: return to middle → drag one finger alone → observe the direction/middle position → change `scale`/`offset_deg` → refresh the page and retry

## FAQ

- **Connection failed / no response from the ESP32**: confirm the baud rate is 115200, that the ESP32's COM port is selected, and that the 5 V/3 A supply and common ground are correct; opening the serial port may reset the ESP32, and the page automatically retries the NOP
- **Servos do not move or jitter**: first confirm the servos are 333 Hz digital servos (PTK 7452 MG-D or equivalent) and that the power supply is adequate; the SG90 requires firmware changes
- **Direction reversed**: set the corresponding finger's `scale` to `-1`
- **Middle position incorrect**: adjust the corresponding channel's `offset_deg`
- **"Busy (gesture executing)" prompt**: the firmware is executing a built-in gesture; wait for it to finish or click E-stop (`0xFF`)
- **Scanning servos**: `tools/scan_servos.py` only applies to SCS0009; for PWM use `AmazingHand-PWM/tools/serial_test.py` or the web page

---

## Related pages

- [PWM protocol and calibration](../06-servo-tuning/pwm.md)
- [PWM desktop host software](../04-desktop/pwm.md)
- [PWM quick start](../02-quick-start/pwm.md)
