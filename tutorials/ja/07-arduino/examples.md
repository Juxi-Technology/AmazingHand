---
title: "Arduino と Python のサンプル"
description: "AmazingHand 公式の Arduino／Python サンプル：SCServo ライブラリ、Feetech 調整ツール、TTL Linker の配線モード、Arduino Uno／Mega のシリアル、Python の基本スクリプト。"
version: scs0009
---

# Arduino と Python のサンプル

本ページでは `AmazingHand-main/ArduinoExample/` と `AmazingHand-main/PythonExample/` の公式サンプルと配線の要点をまとめます。

## Arduino サンプル

### 準備

- Arduino IDE のライブラリマネージャーで **SCServo** ライブラリをインストールします。
- Feetech FD 調整ツール（`feetech debug tool`）でサーボ ID を設定します。
- Arduino と TTL Linker の間は **RX/TX を交差接続**します。

### Link モード：サーボ ID の変更

1. まず Arduino へ `Blink` サンプルを書き込みます。
2. Link モードで配線し、Feetech ソフトを開いて ID を変更します。

![Link モードの配線](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Link-mode.jpg)

![SCServo ライブラリのインストール](../../assets/robot-arms/amazing-hand/arduino-extension/SCServo.jpg)

### Control モード：Arduino でサーボを制御

独自のプログラムを書き込んだ後、Control モードで配線します：

![Control モードの配線](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Control-mode.jpg)

- **Arduino Uno**（シリアルポートが 1 つだけ）：図に従ってソフトウェアシリアル／指定ピンを使用します。
- **Arduino Mega**：**RX1 / TX1（19 / 18）**を使用します。

![Uno のシリアル配線](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Uno.jpg)

![Mega のシリアル配線](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Mega.jpg)

> ピン番号、ライブラリのバージョン、TTL Linker の向きは実際の基板のシルク印刷に従ってください。ID を変更する前に、バスの給電と共通グラウンドを確認してください。

## Python サンプル

`AmazingHand-main/PythonExample/` には 4 つの基本スクリプトがあります：

| スクリプト | 役割 |
|------|------|
| `AmazingHand_Demo.py` | 片手の基本デモ：バスへ接続し、動作を実行 |
| `AmazingHand_Demo_Both.py` | 両手のデモ |
| `AmazingHand_FingerTest.py` | 単指テスト |
| `AmazingHand_Hand_FingerMiddlePos.py` | 指の中間位置のキャリブレーション |

使用前の準備：

1. Feetech ソフトでサーボ ID を設定します（右 1–8、左 11–18）。
2. `pyserial` をインストールし、スクリプト内のシリアルポート名／ボーレートを変更してから実行します。
3. 外部サーボ電源が接続され、バスドライバ基板と共通グラウンドであることを確認します。

> これらは公式の基本サンプルです。より完全な GUI/CLI は [SCS0009 デスクトップツール](../04-desktop/scs0009.md)、TTL 配線と中間位置は [SCS0009 サーボ調整とキャリブレーション](../06-servo-tuning/scs0009.md) を参照してください。

## ソースの場所

- [`AmazingHand-main/ArduinoExample/`](../../../AmazingHand-main/ArduinoExample/)
- [`AmazingHand-main/PythonExample/`](../../../AmazingHand-main/PythonExample/)
