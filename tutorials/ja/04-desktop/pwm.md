---
title: "PWM デスクトップツール（Tkinter GUI）"
description: "AmazingHand PWM サーボ版のデスクトップ制御：ソースからの実行、GUI のジェスチャー／差動／直接駆動、内蔵 MediaPipe トラッキング、コマンドラインテスト、パッケージ化。"
version: pwm
---

# PWM デスクトップツール（Tkinter GUI）

> 以下のコマンドはリポジトリの `AmazingHand-PWM/` ディレクトリで実行します。

本ページは **PWM サーボ版**のデスクトップ制御チュートリアルです。ウェブコントロールは [PWM ウェブコントロール](../03-web-control/pwm.md)、配線は [PWM 配線](../01-hardware/pwm.md)、ファームウェアの書き込みは [PWM クイックスタート](../02-quick-start/pwm.md) を参照してください。

> 対象：ESP32-S3 + PWM サーボ 8 系統（差動駆動）。ファームウェアの書き込みは [PWM クイックスタート](../02-quick-start/pwm.md)、プロトコルとコマンドは [PWM プロトコルとキャリブレーション](../06-servo-tuning/pwm.md) を参照してください。

## 1. 実行方法

| 方法 | 必要なもの | 向いている用途 |
|------|------|------|
| **ソースから実行**（推奨） | 64 ビット Python 3.12 + pyserial | すべての機能（ハンドトラッキングを含む） |
| 自分で exe をパッケージ化 | PyInstaller | Python を入れずに配布（第 7 節を参照） |

## 2. ソースから実行

### 依存関係のインストール

モジュールのルートディレクトリ（`AmazingHand-PWM/`）で実行します：

```bash
# 基本依存関係（pyserial）
pip install -r tools/requirements.txt

# ハンドトラッキングが必要な場合に実行（tools/tracking_env を自動作成し mediapipe をインストール）
tools/setup_tracking.bat
```

> mediapipe 0.10.14 は 64 ビット Windows 用 wheel しか提供されていないため、**64 ビット Python 3.12** を使用する必要があります。

### GUI の起動

```bash
# pyserial が入った任意の Python
python tools/hand_gui.py

# またはトラッキング環境（mediapipe 入り）を使用
tools/tracking_env/Scripts/python tools/hand_gui.py
```

![デスクトップツールのメイン画面：シリアルポートバー、ジェスチャーコマンド、サーボ直接駆動、指の差動制御](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-main.png)

### GUI の使い方

1. **シリアルポートの選択**：上部のドロップダウンで ESP32 の COM ポートを選びます（デバイスマネージャーで確認）。
2. **「Connect」をクリック**：ステータスランプが緑になり、ログに「connected」と表示され、自動的に NOP のリンクテストを送信します。
3. **ジェスチャーコマンド**：「グー／チョキ／パー／サムズアップ／OK／ピンチ／指差し／開く／握り拳」をクリックすると、多指ハンドが実行します。
4. **左右手**：「右手」／「左手」のチェックで切り替えます（親指のミラー方向が異なります）。
5. **サーボ直接駆動**：8 本のスライダーをドラッグし、個々のサーボ角度をリアルタイムに制御します（0–180°）。
6. **指の差動制御**：各指に 2 本のプログレスバーがあります ——
   - **屈曲◀▶伸展**：指を曲げる／伸ばす（範囲 -70 ~ +70）。
   - **右◀▶左**：指を左右に振る（範囲 60 ~ 120、90=中立）。

   > この 2 本のプログレスバーは**制御軸**で、2 つのサーボではありません。プログラムがこれらをその指の 2 つのサーボ角度へ合成します。同方向成分が開き、逆方向成分が屈伸になります。

7. **繰り返し／停止**：前回のジェスチャーを繰り返す／即座に中断します。
8. **通信ログ**：下部に送受信フレームと応答をリアルタイム表示します。

![指の差動制御パネル：各指の屈曲／伸展と左右の振り](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-differential.png)

### GUI 内蔵のハンドトラッキング

GUI にはハンドトラッキングパネルが付属しています（カメラが手の動きを追従します）：

1. シリアルポートへ接続したら、「ハンドトラッキング（MediaPipe カメラ）」パネルまでスクロールします。
2. カメラ番号を選び（デフォルト 0）、**「Start Tracking」**をクリックします。
3. 手をカメラの画角に入れると、多指ハンドが屈曲／伸展に追従します。

> トラッキングには `tools/setup_tracking.bat` でインストールした mediapipe が必要です。ソースから起動した GUI でのみトラッキング機能があります。

## 3. コマンドラインテスト（tools/serial_test.py）

モジュールのルートディレクトリで実行します：

```bash
# リンクテスト（まず通信できることを確認）
python tools/serial_test.py COM3 nop

# ジェスチャー
python tools/serial_test.py COM3 rock         # グー
python tools/serial_test.py COM3 thumbs_up    # サムズアップ
python tools/serial_test.py COM3 index        # 指差し
python tools/serial_test.py COM3 open         # 開く
python tools/serial_test.py COM3 close        # 握り拳

# 単一サーボの直接駆動
python tools/serial_test.py COM3 servo 1 90   # サーボ1 → 90°

# すべて中間位置へ
python tools/serial_test.py COM3 mid

# 左右手の設定
python tools/serial_test.py COM3 hand L
python tools/serial_test.py COM3 hand R

# スイープ／セルフテスト
python tools/serial_test.py COM3 sweep 1      # サーボ1 スイープ
python tools/serial_test.py COM3 test         # すべてのサーボを 1 個ずつテスト
```

## 4. シリアルツールでの手動テスト（任意）

デスクトップツールを使わず、シリアルツールで 16 進フレームを直接送ってもリンクを検証できます。

**CoolTerm**（Windows / macOS / Linux）：

1. `Options` → ボーレート **115200**、8N1。
2. `Connection` → `Send String` → `Hex` を選択。
3. `AA 01 00 01`（グー）を送信すると、応答エリアに `BB 01 00 01`（ACK）と `BB 01 10 11`（完了）が現れます。

**Linux / macOS のコマンドライン**：

```bash
# Linux
stty -F /dev/ttyUSB0 115200
printf '\xAA\x01\x00\x01' > /dev/ttyUSB0

# macOS
stty -f /dev/cu.usbserial-0001 115200
printf '\xAA\x01\x00\x01' > /dev/cu.usbserial-0001
```

フレーム形式、チェックサム、すべてのコマンドは [PWM プロトコルとキャリブレーション](../06-servo-tuning/pwm.md) を参照してください。

## 5. Python 制御スクリプト（独自開発）

```python
import time
import serial

PORT, BAUD = "COM3", 115200          # Linux/macOS では /dev/ttyUSB0、/dev/cu.usbserial-* に変更

def frame(cmd, data=b""):
    checksum = cmd ^ len(data)
    for byte in data:
        checksum ^= byte
    return bytes([0xAA, cmd, len(data)]) + data + bytes([checksum & 0xFF])

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(1)                        # ESP32 のリセット完了を待つ

ser.write(frame(0x00))               # NOP リンクテスト
ser.write(frame(0x01))               # グー
time.sleep(0.5)
ser.write(frame(0xF0, bytes([90] * 8)))  # 8 系統のサーボをすべて 90°
ser.close()
```

応答フレームは `BB CMD STATUS CKSUM` で、`STATUS=0x00` は受け付け済み、`0x10` はジェスチャー完了を表します。完全なコマンド表と直接駆動／左右手の例は [PWM プロトコルとキャリブレーション](../06-servo-tuning/pwm.md) を参照してください。

## 6. よくある問題

| 現象 | 対処 |
|------|------|
| サーボが動かない | 給電（5V 3A の独立電源）、COM ポート、配線を確認 |
| 応答がない／シリアルポートを開くとサーボが勝手に動く | ボーレートが 115200 であることを確認。GUI は接続時にまず NOP ハンドシェイクを送信します |
| カメラの映像が出ない | カメラの権限を許可（設定→プライバシー→カメラ） |
| 手の向きが逆 | 逆側の左右手をチェック |
| トラッキングが反応しない | `tools\tracking_env` の Python で起動していること、mediapipe のインストールが成功していることを確認 |

## 7. 自分で exe をパッケージ化（任意）

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole --name "AmazingHand控制台" tools/hand_gui.py
```

パッケージ版にはハンドトラッキングは含まれません（mediapipe のリソースが大きいため）。トラッキングが必要な場合はソースから実行してください。

> 完全なプロトコルとコマンドの説明は [PWM プロトコルとキャリブレーション](../06-servo-tuning/pwm.md) を参照してください。
