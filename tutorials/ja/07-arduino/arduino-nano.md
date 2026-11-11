---
title: "Arduino Nano の使い方"
description: "Arduino Nano（328P）とサーボドライバ基板で AmazingHand の「02 デモプログラム」を実行：配線、ライブラリのインストール、コンパイルとアップロード、実行結果。"
version: scs0009
---

# Arduino Nano の使い方

> 本ページは **SCS0009 バスサーボ版**の Arduino Nano デモです。TTL 配線と ID 設定は [SCS0009 サーボ調整とキャリブレーション](../06-servo-tuning/scs0009.md)、その他のサンプルは [Arduino / Python サンプル](examples.md) を参照してください。


## 配線方法（サーボドライバ基板 + Nano ボード）

**Nano ボード（328P 開発ボード）のピン位置をよく確認してください！**

![Nano ボードのピン位置（1）](../../assets/robot-arms/amazing-hand/arduino-nano/01.png)

![Nano ボードのピン位置（2）](../../assets/robot-arms/amazing-hand/arduino-nano/02.png)

![Nano ボードのピン位置（3）](../../assets/robot-arms/amazing-hand/arduino-nano/03.png)

![Nano ボードのピン位置（4）](../../assets/robot-arms/amazing-hand/arduino-nano/04.png)

以下ではマイコンを使った調整手順を説明します。マイコン自体はデモプログラムを繰り返し実行し続けるため、データ線を外すだけで停止できます。

## 「02 デモプログラム」を実行

1. Arduino IDE をインストールします。

2. **左手か右手か**に応じて、対応する `.ino` ファイルを開きます。

   ![左手／右手に対応する 02 デモプログラムの ino ファイル](../../assets/robot-arms/amazing-hand/arduino-nano/05.png)

3. Arduino プログラムをコンパイルして Nano ボードへアップロードする前に、まず「ライブラリマネージャー」で **FTServo ライブラリ** と **SCServo ライブラリ** をインストールします。

   ![ライブラリマネージャーで FTServo と SCServo ライブラリをインストール](../../assets/robot-arms/amazing-hand/arduino-nano/06.png)

4. Nano ボードの種類は「**Arduino Nano**」を選択します。

   ![ボードの種類で Arduino Nano を選択](../../assets/robot-arms/amazing-hand/arduino-nano/07.png)

5. コンパイルしてアップロードします。

> **注意：** このとき PC は Nano ボードだけを単独で接続し、Nano ボードはまだサーボドライバ基板へ接続しません（つまり多指ハンドとは接続しません）。

アップロードが成功したら、Nano ボードを 3 本のジャンパー線でサーボドライバ基板へ接続し、サーボをサーボドライバ基板へ接続します。参考：[MEGA328P Nano ボードで調整するときの配線方法](https://juxitech.feishu.cn/wiki/Wt46wtt26imdWkkQlxTcL87qnHd#share-HdS4dNgwyo2seVxRZ9PcZ1R3nuc)。

多指ハンドは「02 デモプログラム」を繰り返し実行し続けます。実行結果は次のとおりです：

![02 デモプログラムの実行結果](../../assets/robot-arms/amazing-hand/arduino-nano/08.png)
