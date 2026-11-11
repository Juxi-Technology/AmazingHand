---
title: "Arduino Nano Tutorial"
description: "Run the AmazingHand \"02 演示程序\" with an Arduino Nano (328P) and a servo driver board: wiring, library installation, compiling/uploading and the result."
version: scs0009
---

# Arduino Nano Tutorial

> This page is the Arduino Nano demo for the **SCS0009 bus servo version**. For TTL wiring and ID setup, see [SCS0009 servo debugging and calibration](../06-servo-tuning/scs0009.md); for more examples, see [Arduino / Python examples](examples.md).


## Wiring (servo driver board + Nano board)

**Check the pin positions on the Nano board (i.e. the 328P dev board) carefully!**

![Nano board pin positions (1)](../../assets/robot-arms/amazing-hand/arduino-nano/01.png)

![Nano board pin positions (2)](../../assets/robot-arms/amazing-hand/arduino-nano/02.png)

![Nano board pin positions (3)](../../assets/robot-arms/amazing-hand/arduino-nano/03.png)

![Nano board pin positions (4)](../../assets/robot-arms/amazing-hand/arduino-nano/04.png)

The process below uses an MCU. The MCU keeps looping the demo program, so just disconnect the data cable to stop it.

## Running the "02 演示程序"

1. Install the Arduino IDE yourself.

2. Open the corresponding `.ino` file for the **left or right hand**.

   ![The 02 演示程序 ino file for the left/right hand](../../assets/robot-arms/amazing-hand/arduino-nano/05.png)

3. Before compiling and uploading the Arduino program to the Nano board, first install the **FTServo library** and the **SCServo library** in the "Library Manager".

   ![Installing the FTServo and SCServo libraries in the Library Manager](../../assets/robot-arms/amazing-hand/arduino-nano/06.png)

4. Select the Nano board type "**Arduino Nano**".

   ![Selecting Arduino Nano as the board type](../../assets/robot-arms/amazing-hand/arduino-nano/07.png)

5. Compile and upload.

> **Note:** at this point the computer is connected only to the Nano board, and the Nano board is not yet connected to the servo driver board (i.e. not connected to the dexterous hand).

After a successful upload, connect the Nano board to the servo driver board with three jumper wires, and connect the servos to the servo driver board; refer to [MEGA328P Nano board debugging wiring](https://juxitech.feishu.cn/wiki/Wt46wtt26imdWkkQlxTcL87qnHd#share-HdS4dNgwyo2seVxRZ9PcZ1R3nuc).

The dexterous hand will keep looping the "02 演示程序"; the result looks like this:

![Result of the 02 演示程序](../../assets/robot-arms/amazing-hand/arduino-nano/08.png)
