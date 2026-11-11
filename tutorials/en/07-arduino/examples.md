---
title: "Arduino and Python Examples"
description: "AmazingHand official Arduino/Python examples: SCServo library, Feetech debug tool, TTL Linker wiring modes, Arduino Uno/Mega serial ports and basic Python scripts."
version: scs0009
---

# Arduino and Python Examples

This page collects the official examples and wiring essentials from `AmazingHand-main/ArduinoExample/` and `AmazingHand-main/PythonExample/`.

## Arduino examples

### Preparation

- Install the **SCServo** library in the Arduino IDE's Library Manager.
- Use the Feetech FD debug tool to set servo IDs (`feetech debug tool`).
- **Cross-connect RX/TX** between the Arduino and the TTL Linker.

### Link mode: changing servo IDs

1. First upload the `Blink` example to the Arduino.
2. Wire according to Link mode and open the Feetech software to change IDs.

![Link mode wiring](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Link-mode.jpg)

![Installing the SCServo library](../../assets/robot-arms/amazing-hand/arduino-extension/SCServo.jpg)

### Control mode: the Arduino controls the servos

After uploading your custom program, wire according to Control mode:

![Control mode wiring](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Control-mode.jpg)

- **Arduino Uno** (only one serial port): use a software serial port / the specified pins as shown.
- **Arduino Mega**: use **RX1 / TX1 (19 / 18)**.

![Uno serial port wiring](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Uno.jpg)

![Mega serial port wiring](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Mega.jpg)

> Pin numbers, library versions and TTL Linker orientation follow the actual board's silkscreen; confirm the bus power and common ground before changing IDs.

## Python examples

`AmazingHand-main/PythonExample/` provides 4 basic scripts:

| Script | Purpose |
|------|------|
| `AmazingHand_Demo.py` | Basic single-hand demo: connect to the bus, perform motions |
| `AmazingHand_Demo_Both.py` | Two-hand demo |
| `AmazingHand_FingerTest.py` | Single-finger test |
| `AmazingHand_Hand_FingerMiddlePos.py` | Finger middle-position calibration |

Before use:

1. Use the Feetech software to set the servo IDs (right 1–8, left 11–18).
2. Install `pyserial`, change the serial port name/baud rate inside the script as needed, then run it.
3. Confirm the external servo power supply is connected and shares a common ground with the bus driver board.

> These are the official basic examples; for the more complete GUI/CLI see [SCS0009 desktop host software](../04-desktop/scs0009.md), and for TTL wiring and the middle position see [SCS0009 servo debugging and calibration](../06-servo-tuning/scs0009.md).

## Source locations

- [`AmazingHand-main/ArduinoExample/`](../../../AmazingHand-main/ArduinoExample/)
- [`AmazingHand-main/PythonExample/`](../../../AmazingHand-main/PythonExample/)
