# AmazingHand PWM サーボ版 — クイックスタート

**ESP32-S3 と 8 個の PWM サーボ**で AmazingHand を動かします。完全なマニュアルはこの `docs/` フォルダーにあります。

## ハードウェア

| 項目 | 型番 |
|------|------|
| メインコントローラ | ESP32-S3 開発ボード（YX-ESP32-S3 または同等品） |
| サーボ | PWM サーボ 8 個 —— ファームウェアは **PTK 7452 MG-D デジタルサーボ（333 Hz）** に合わせて校正済み |
| 変換基板 | PWM サーボ用変換基板 |
| 電源 | 5 V / 3 A、ESP32 と共通グラウンド |

> SG90 などの 50 Hz アナログサーボは、333 Hz ファームウェアの**代替品にはなりません**。

| チャンネル | GPIO | 関節 | チャンネル | GPIO | 関節 |
|---------|------|-------|---------|------|-------|
| PWM1 | 4 | 人差し指 1 | PWM5 | 15 | 薬指 1 |
| PWM2 | 5 | 人差し指 2 | PWM6 | 16 | 薬指 2 |
| PWM3 | 6 | 中指 1 | PWM7 | 17 | 親指 1 |
| PWM4 | 7 | 中指 2 | PWM8 | 18 | 親指 2 |

## 1. ファームウェアの書き込み

ESP-IDF を使用する場合：

```bash
cd firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

ビルド済みイメージと `esptool` を使用する場合：

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  firmware/prebuilt/amazinghand_pwm.bin
```

シリアルポートは **115200-8N1** で動作し、起動時にバナーを出力します。

## 2. ハンドの操作

デスクトップ GUI：

```bash
pip install -r tools/requirements.txt
python tools/hand_gui.py
```

カメラトラッキングには、`tools/setup_tracking.bat` で作成する追加環境が必要です。その後：

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

ウェブ操作：リポジトリの `Amazinghand-web-io/` ページを開き（または `Amazinghand-web/server.py --driver pwm` を実行し）、ドライバーで **PWM（ESP32-S3）** を選択して ESP32 のシリアルポートを選び、接続します。

## 3. 完全版ドキュメント

| ドキュメント | 内容 |
|----------|----------|
| [`../en/user_manual.md`](../en/user_manual.md) / [`../zh-hans/用户手册.md`](../zh-hans/用户手册.md) | プロトコル、コマンドリファレンス、配線、校正、FAQ |
| [`../en/full_workflow.md`](../en/full_workflow.md) / [`../zh-hans/全流程使用教程.md`](../zh-hans/全流程使用教程.md) | エンドツーエンドのワークフロー |
| [`../en/gui_usage.md`](../en/gui_usage.md) / [`../zh-hans/使用教程.md`](../zh-hans/使用教程.md) | GUI とシリアルテストツール |
| [`../en/hand_tracking.md`](../en/hand_tracking.md) / [`../zh-hans/手势追踪教程.md`](../zh-hans/手势追踪教程.md) | MediaPipe によるハンドトラッキング |

## 4. よくある問題

- **応答がない**：ボーレートが 115200 であること、ESP32 の COM ポート、5 V / 3 A の電源、共通グラウンドを確認してください。ページは NOP ハンドシェイクを自動的に再試行します。
- **サーボが動かない／震える**：サーボが 333 Hz のデジタルサーボであること、電源容量が十分であることを確認してください。
- **向きが逆**：`Amazinghand-web-io/config.json` の `pwm.calibration` で、該当する指の `scale` を `-1` に設定してください。
- **中立位置がずれている**：該当するチャンネルの `offset_deg` を調整してください。
- **ビジー状態**：ファームウェアが内蔵ジェスチャーを実行中です。完了を待つか、停止コマンド（`0xFF`）を送信してください。
