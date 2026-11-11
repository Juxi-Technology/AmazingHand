---
title: "Arduino Nano 使用教學"
description: "用 Arduino Nano（328P）和伺服馬達驅動板執行 AmazingHand「02 演示程式」：接線、函式庫安裝、編譯上傳與執行結果。"
version: scs0009
---

# Arduino Nano 使用教學

> 本頁是 **SCS0009 匯流排伺服馬達版**的 Arduino Nano 演示。TTL 接線與 ID 設定見 [SCS0009 伺服馬達調校與標定](../06-servo-tuning/scs0009.md)，更多範例見 [Arduino / Python 範例](examples.md)。


## 接線方式（伺服馬達驅動板 + Nano 板）

**看清楚 Nano 板（即 328P 開發板）的針腳位置！**

![Nano 板針腳位置（1）](../../assets/robot-arms/amazing-hand/arduino-nano/01.png)

![Nano 板針腳位置（2）](../../assets/robot-arms/amazing-hand/arduino-nano/02.png)

![Nano 板針腳位置（3）](../../assets/robot-arms/amazing-hand/arduino-nano/03.png)

![Nano 板針腳位置（4）](../../assets/robot-arms/amazing-hand/arduino-nano/04.png)

下面描述的是使用單晶片的調校過程。單晶片本身會不斷循環執行演示程式，只需斷開資料線即可停止。

## 執行「02 演示程式」

1. 自行安裝 Arduino IDE。

2. 根據**左手還是右手**，開啟對應的 `.ino` 檔案。

   ![左手/右手對應的 02 演示程式 ino 檔案](../../assets/robot-arms/amazing-hand/arduino-nano/05.png)

3. 編譯上傳 Arduino 程式到 Nano 板之前，先在「函式庫管理器」裡安裝 **FTServo 函式庫** 和 **SCServo 函式庫**。

   ![函式庫管理器安裝 FTServo 與 SCServo 函式庫](../../assets/robot-arms/amazing-hand/arduino-nano/06.png)

4. Nano 板類型選擇「**Arduino Nano**」。

   ![開發板類型選擇 Arduino Nano](../../assets/robot-arms/amazing-hand/arduino-nano/07.png)

5. 編譯並上傳。

> **注意：** 此時電腦只單獨連接到 Nano 板，Nano 板先不連接伺服馬達驅動板（即不和靈巧手連接）。

上傳成功後，將 Nano 板透過三根跳線連接到伺服馬達驅動板上，伺服馬達連接到伺服馬達驅動板，參考 [MEGA328P Nano 板調校時的接線方式](https://juxitech.feishu.cn/wiki/Wt46wtt26imdWkkQlxTcL87qnHd#share-HdS4dNgwyo2seVxRZ9PcZ1R3nuc)。

靈巧手會不斷循環執行「02 演示程式」，執行結果如下：

![02 演示程式執行結果](../../assets/robot-arms/amazing-hand/arduino-nano/08.png)
