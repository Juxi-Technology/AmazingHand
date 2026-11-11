---
title: "Arduino Nano 使用教程"
description: "用 Arduino Nano（328P）和舵机驱动板运行 AmazingHand「02 演示程序」：接线、库安装、编译上传与运行结果。"
version: scs0009
---

# Arduino Nano 使用教程

> 本页是 **SCS0009 总线舵机版**的 Arduino Nano 演示。TTL 接线与 ID 设置见 [SCS0009 舵机调试与标定](../06-servo-tuning/scs0009.md)，更多示例见 [Arduino / Python 示例](examples.md)。


## 接线方式（舵机驱动板 + Nano 板）

**看清楚 Nano 板（即 328P 开发板）的针脚位置！**

![Nano 板针脚位置（1）](../../assets/robot-arms/amazing-hand/arduino-nano/01.png)

![Nano 板针脚位置（2）](../../assets/robot-arms/amazing-hand/arduino-nano/02.png)

![Nano 板针脚位置（3）](../../assets/robot-arms/amazing-hand/arduino-nano/03.png)

![Nano 板针脚位置（4）](../../assets/robot-arms/amazing-hand/arduino-nano/04.png)

下面描述的是使用单片机的调试过程。单片机本身会不断循环运行演示程序，只需断开数据线即可停止。

## 运行「02 演示程序」

1. 自行安装 Arduino IDE。

2. 根据**左手还是右手**，打开对应的 `.ino` 文件。

   ![左手/右手对应的 02 演示程序 ino 文件](../../assets/robot-arms/amazing-hand/arduino-nano/05.png)

3. 编译上传 Arduino 程序到 Nano 板之前，先在「库管理器」里安装 **FTServo 库** 和 **SCServo 库**。

   ![库管理器安装 FTServo 与 SCServo 库](../../assets/robot-arms/amazing-hand/arduino-nano/06.png)

4. Nano 板类型选择「**Arduino Nano**」。

   ![开发板类型选择 Arduino Nano](../../assets/robot-arms/amazing-hand/arduino-nano/07.png)

5. 编译并上传。

> **注意：** 此时电脑只单独连接到 Nano 板，Nano 板先不连接舵机驱动板（即不和灵巧手连接）。

上传成功后，将 Nano 板通过三根跳线连接到舵机驱动板上，舵机连接到舵机驱动板，参考 [MEGA328P Nano 板调试时的接线方式](https://juxitech.feishu.cn/wiki/Wt46wtt26imdWkkQlxTcL87qnHd#share-HdS4dNgwyo2seVxRZ9PcZ1R3nuc)。

灵巧手会不断循环运行「02 演示程序」，运行结果如下：

![02 演示程序运行结果](../../assets/robot-arms/amazing-hand/arduino-nano/08.png)
