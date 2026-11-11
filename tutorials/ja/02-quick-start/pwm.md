---
title: "PWM クイックスタート"
description: "AmazingHand PWM サーボ版の最短手順：配線、ファームウェア書き込み、デスクトップ GUI またはウェブコントロール、初回動作。"
version: pwm
---

# PWM クイックスタート

ESP32-S3 + PWM サーボ 8 系統の版向けです。詳しい説明は各章のリンクを参照してください。

## 1. 配線

- 8 個の PWM サーボを番号どおりに変換基板のサーボ 1–8 へ挿します。
- 変換基板の PWM1–8 を ESP32-S3 の GPIO 4、5、6、7、15、16、17、18 へ接続します。
- 変換基板の 5V/GND を 5V/3A 電源へ接続し、ESP32 と共通グラウンドにします。
- 詳細な配線：[PWM 配線、GPIO、給電](../01-hardware/pwm.md)。

> サーボは **PTK 7452 MG-D デジタルサーボ（333 Hz）** または同等品である必要があります。SG90 などの 50 Hz アナログサーボでは直接置き換えられません。

## 2. ファームウェアの書き込み

### 方法 A：ビルド済み bin（推奨）

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  AmazingHand-PWM/firmware/prebuilt/amazinghand_pwm.bin
```

### 方法 B：ESP-IDF でビルド

```bash
cd AmazingHand-PWM/firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

ファームウェアプロジェクトの構成：

```text
firmware/AmazingHand_Serial/
├── main/main.c                  FreeRTOS タスク、コマンドキュー、初期化
└── components/
    ├── hand_servo/              LEDC PWM ドライバとサーボキャリブレーション
    ├── hand_gestures/           ジェスチャーパラメータのマクロとジェスチャー関数
    └── hand_protocol/           シリアルフレーム解析とコマンドディスパッチ
```

> ESP-IDF のビルドは中国語パスに対応していません。プロジェクトディレクトリとユーザーディレクトリは英語にしてください。ESP-IDF v5.x / v6.x を推奨し、ターゲットチップは **ESP32-S3** を選びます。

通電後、シリアルには次のように出力されます：

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

## 3. PC との接続

| 方法 | 入口 |
|------|------|
| デスクトップ GUI | [PWM デスクトップツール](../04-desktop/pwm.md)：`python AmazingHand-PWM/tools/hand_gui.py` |
| ウェブコントロール | [PWM ウェブコントロール](../03-web-control/pwm.md)：ドライバーで **PWM（ESP32-S3）** を選択、シリアル 115200 |
| コマンドラインテスト | `python AmazingHand-PWM/tools/serial_test.py COM3 nop` |

## 4. 初回動作

1. 接続後、ファームウェアはまず中間位置（90°）へ戻ります。異音や引っかかりがないか確認します。
2. 単指スライダーで 1 本ずつ向きと中間位置を確認します。
3. 次に「開く／握り拳」など小さめのポーズを試します。
4. 向きが逆、または中間位置がずれている場合は [PWM プロトコルとキャリブレーション](../06-servo-tuning/pwm.md) に従って調整します。

## 次のステップ

- [PWM プロトコルとキャリブレーション](../06-servo-tuning/pwm.md)
- [PWM ハンドトラッキング](../05-hand-tracking/pwm.md)
- [バージョン比較と選定](../00-product/version-comparison.md)
