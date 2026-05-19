First, download the ["AmazingHand Debugging.zip"](https://juxitech.feishu.cn/wiki/QjYBwL0A0iJVlNkEpUUclLYGnBc) compressed package. After extraction, you can use the "Using Arduino Program to Debug AmazingHand Process (TTL Servo)" document for servo ID setting, calibration, center calibration, and demonstration program execution, or refer to the [official open-source code](https://github.com/pollen-robotics/AmazingHand/tree/main/ArduinoExample).

For finished products without disassembly (factory servo ID setting, calibration, and center calibration are already debugged), you can directly skip to `Step 6: Run "02 Demo Program"` and `Step 7: Hand Tracking`.

![Image](https://i-blog.csdnimg.cn/direct/9d9e2f9fa32c41d191c1cebf4f030131.png)

1. **Wiring Methods for Debugging the AmazingHand**
   There are two main methods:
   - Using a computer to run upper-level software like Python, such as the Feite Servo upper-level software or Python code.
   - Using a microcontroller like MEGA328P or a self-purchased development board/main controller.
   
   Wiring methods are as follows:
   
   (1) **Wiring for `Python method` debugging** (only connect the servo driver board):
   ![Image](https://i-blog.csdnimg.cn/direct/52aa78fd03ac4adeb23c3e2dc1cda3f1.png)
   
   (2) **Wiring for `MEGA328P development board` debugging** (servo driver board + 328P development board) (This tutorial uses Arduino Nano):
   Pay attention to the `pin positions` on the MEGA328P development board!
   ![Insert image description here](https://i-blog.csdnimg.cn/direct/8d45fc2aae6f4ee28d7c0c84233a0ac5.png)
   ![Insert image description here](https://i-blog.csdnimg.cn/direct/4597737bc4894d9bbed3650dacf8d10c.png)
   ![Insert image description here](https://i-blog.csdnimg.cn/direct/f0938d4795b54d13b80c19a65f16d964.png)
   ![Insert image description here](https://i-blog.csdnimg.cn/direct/2f3f51c7a1314b69872e5b5e82487f1a.png)
   
   The following description is for the debugging process using a microcontroller. The microcontroller itself will continuously loop the demonstration program; simply disconnect the data cable to stop it.

2. **Set Servo IDs**
   A single AmazingHand uses 8 servos. For the right hand, IDs need to be set to 1-8; for the left hand, IDs need to be set to 11-18.
   
   Center calibration default values for finished products:
   - `Right hand: [451,571,451,571,451,571,451,571]`
   - `Left hand: [571,451,571,451,571,451,571,451]`
   
   1. **Wiring**: Connect `individual` servos and the servo driver board one by one.
      ![Image](https://i-blog.csdnimg.cn/direct/5685a4fc272c4c85b202fe6553c56ae9.png)
   
   2. **Use the servo manufacturer's upper-level software FD1.9.8.2 for setting**
      [https://gitee.com/ftservo](https://gitee.com/ftservo)
      ![Image](https://i-blog.csdnimg.cn/direct/24ec9599c5a74ecbb54eb380efc38616.png)
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/8a6658d6f9854449b9aba31057da163c.png)
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/2b43e68085d04851a80c6a79e876d82d.png)

3. **Install Servo Horns**
   1. **Upload the code program "For installing white servo horns" to the development board.**
      The purpose of this program: To position the servo gear at an approximately centered location. Subsequent motion angles are based on this center position.
      
      (1) Install the Arduino software yourself. Refer to the [installation tutorial](https://blog.csdn.net/weixin_35509395/article/details/156188274) based on your system. To compile and upload Arduino programs, first install the `FTServo library` and `SCServo library` in the Library Manager.
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/61a2af1ea5b9405aa2df439251a9f7c8.png)
      
      (2) Select board type: Choose "Arduino Nano".
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/a4d591173bae40b9b488cd4b4f590c2c.png)
   
   2. **Debug servos 1 and 2**
      (1) **Edit**: Modify the following location according to the servo ID you want to debug. For example, to debug the index finger, set the ID values to 1 and 2.
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/fd536255a13f4430a5c154017af9cb3b.png)
      
      (2) **Upload the program to the development board.**
      
      (3) **Wiring**: Connect the development board to the servo driver board and servos 1 and 2. You should hear the servo gears rotate a certain angle and then stop.
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/fac29c94e2254be6b9d2cf14dbdfffde.png)
      
      (4) **Install the servo horn on the gear**, trying to keep it as parallel as possible.
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/31569168b1a34d9cb7e56c068090bcc6.png)
   
   3. **Debug servos 3 and 4**
      (1) `Disconnect the wiring between the 328P development board and the servo driver board (otherwise uploading will fail).`
      (2) **Edit**: Set ID values to 3 and 4.
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/d7a4639fb3e143d0ae21f1294dc7b131.png)
      
      (3) **Upload the program to the development board.**
      (4) **Wiring**: Connect the development board to the servo driver board and servos 3 and 4. You should hear the servo gears rotate a certain angle and then stop.
      (5) **Install the servo horn on the gear**, trying to keep it as parallel as possible.
   
   4. **Debug servos 5 and 6**
      Steps are the same as above.
   
   5. **Debug servos 7 and 8**
      Steps are the same as above.

4. **Fine-tune the Middle Position Values**
   1. **Upload the code program "01 For fine-tuning MiddlePos values" to the development board.**
   2. When the finger is in the closed position, immediately stop the program (simply disconnect the data cable) and check if the servo horn is correctly aligned (as shown in the image below). If not aligned, adjust the values of MiddlePos_1 and MiddlePos_2 in the program until aligned. Record these values (8 values corresponding to 8 servos) for use in the final program.
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/2e1fa777a31a4f5ea51f0a4b8fb26400.png)
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/e6a856057cc04b3c8122a324766e44b3.png)

5. **Run the Test Program**
   1. Fill the MiddlePos_1 and MiddlePos_2 values saved above into the array below, then download the program.
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/50c783df9cdf4901ae6ac90eb4dffba8.png)

6. **Run "02 Demo Program"**
   (1) Install the Arduino software yourself. Refer to the [installation tutorial](https://blog.csdn.net/weixin_35509395/article/details/156188274) based on your system.
   (2) In the directory `AmazingHand Debugging\00 TTL Serial Servo\arduino program (MEGA328P development board)\02 Demo Program`, open the corresponding `ino file` based on whether it's for the left or right hand.
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/f8abb771cf4345fe8150283555a67697.png)
   
   (3) To compile and upload the Arduino program to the development board, first install the FTServo library and SCServo library in the Library Manager.
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/0eef39bae0344e4186d86c450aefb8b5.png)
   
   (4) Select board type: Choose "Arduino Nano".
      ![Insert image description here](https://i-blog.csdnimg.cn/direct/88558bd3656a4591aa51c275292f154f.png)
   
   (5) Compile and upload.
   
   > **Note**: `At this point, the computer should only be connected to the development board. Do not connect the development board to the servo driver board yet (i.e., do not connect to the AmazingHand).`
   
   After successful upload, connect the development board to the servo driver board using three jumper wires, and connect the servos to the servo driver board. Refer to the `MEGA328P development board wiring method described above`.
   The AmazingHand will continuously loop the `"02 Demo Program"`.
   The running result is as follows:
   ![Insert image description here](https://i-blog.csdnimg.cn/direct/8273881d2b884c2e85c08f98ab541c34.png)
