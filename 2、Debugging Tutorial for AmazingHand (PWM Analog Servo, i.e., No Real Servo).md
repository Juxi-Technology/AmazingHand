
> `If you have a dexterous hand with real servos, you can skip this tutorial!`

ESP32 Development Board Circuit Diagram
![Please add image description](https://i-blog.csdnimg.cn/direct/6d01181b5f864b7f815b5426c5c6bd36.jpeg)

Currently, debugging the PWM servo dexterous hand can only be done via a microcontroller. Here, we use the ESP32 for explanation.
First, download the "[Dexterous Hand Debugging.zip](https://juxitech.feishu.cn/wiki/QjYBwL0A0iJVlNkEpUUclLYGnBc)" compressed package and extract it. Ensure the Arduino software is already installed on your system.
1. Determine Servo IDs
Although PWM servos do not require setting servo IDs like TTL servos do, it is still necessary to clarify the logical IDs. The correspondence is as follows:
![Insert image description here](https://i-blog.csdnimg.cn/direct/b09398561f914064b4bbb40b6e268ca8.png)
2. Wiring Instructions
![Insert image description here](https://i-blog.csdnimg.cn/direct/72f39dc6eff44830bca77715f6fde4bd.png)
1. Servo <--> Adapter Board: Insert the 3P connectors of the 8 servos into the Servo 1 - Servo 8 pins on the adapter board according to the determined ID numbers.
![Insert image description here](https://i-blog.csdnimg.cn/direct/b0a272012bed4da89c3bd047826743ef.png)

2. Adapter Board <--> ESP Development Board:
(1) There are two sets of 5V GND power supply ports. One set is connected via a TYPE-C cable to a 5V-3A power supply. The other set can be connected to power the development board (5V pin), so the ESP32 does not need to be powered via the Micro port during operation.
(2) PW1-PW8: These are the pulse control interfaces for the 8 motors. Connect them in the following order:
        For example: SERVO_PIN1 corresponds to PWM1. Connect the adapter board's PWM1 to the development board's IO23.
![Insert image description here](https://i-blog.csdnimg.cn/direct/cf5b582cb3b54014a9938f8f164fe57b.png)

(3) GND: At least one GND wire must be connected for power supply.
3. Fix the Servo Horn
1. Download the program from "Use when installing the white servo horn"
   The purpose of this program: To position the servo gear at the center (90 degrees). Subsequent movement angles are based on this central position.
(1) Select "ESP32 Dev Module" as the development board type.
![Insert image description here](https://i-blog.csdnimg.cn/direct/c1f00265076e4962b278c59c3f83072b.png)

(2) Modify the following location according to the servo number (1-8) you want to debug. The value below controls servo number 1.
![Insert image description here](https://i-blog.csdnimg.cn/direct/37055bf959c04551a4212e1dce37497c.png)

(3) After running the program, enter the character "0" in the host computer's serial port assistant and click "Send". At this point, the servo rotates to 0 degrees.
![Insert image description here](https://i-blog.csdnimg.cn/direct/715d01a5feda40128630eee5694d3684.png)

(4) Install the test servo arm vertically. For servos 1, 3, 5, and 7, 0 degrees is at the bottom. For servos 2, 4, 6, and 8, 0 degrees is at the top.
![0-degree position for servos 1, 3, 5, 7](https://i-blog.csdnimg.cn/direct/33b8e02f54cf4886b084939f219ec3bf.png)
![0-degree position for servos 2, 4, 6, 8](https://i-blog.csdnimg.cn/direct/4a7187dd531b4172a52527a6307a24c0.png)

(5) Enter the character "90" in the serial port assistant and click "Send". The servo will now rotate to 90 degrees. Observe whether the servo arm is perpendicular to the servo body. If not, modify the value in `midPulseWidth[]`. The position for servo 1's value is shown below. Re-download the program, click "Send" again, and repeat this process until the servo arm is perpendicular to the servo body.
![Insert image description here](https://i-blog.csdnimg.cn/direct/a42d253dad31426db1f4afdb8cbb3a6b.png)

2. Install the servo horn on the gear, trying to keep it as parallel as possible.
![Insert image description here](https://i-blog.csdnimg.cn/direct/73ab2733e28640cbadbb464eb9c36a59.png)

4. Run the "01 Demo Program"
Navigate to the directory `灵巧手调试\01 PWM模拟舵机\arduino程序（PWM舵机）\01 演示程序` and double-click to open `Amazing_Hand_Demo.ino`.
Select "ESP32 Dev Module" as the development board type. ![Insert image description here](https://i-blog.csdnimg.cn/direct/ffd90087b1c742119ceaf2f8c058121b.png)
Compile and upload. The dexterous hand will continuously run the "01 Demo Program" in a loop.
![Insert image description here](https://i-blog.csdnimg.cn/direct/a74a15af63e8446e9ca78aa76c9ef31c.png)
