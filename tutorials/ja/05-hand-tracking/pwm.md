---
title: "PWM ハンドトラッキング（GUI 内蔵 MediaPipe）"
description: "AmazingHand PWM サーボ版のハンドトラッキング：GUI 内蔵 MediaPipe、依存関係のインストール、実行、原理と限界、よくある問題。"
version: pwm
---

# PWM ハンドトラッキング（GUI 内蔵 MediaPipe）

> 以下のコマンドはリポジトリの `AmazingHand-PWM/` ディレクトリで実行します。

本ページでは **PWM サーボ版**のハンドトラッキングを説明します。GUI に MediaPipe が組み込まれており、カメラが手のランドマークを認識して、リアルタイムで PWM サーボ 8 系統へマッピングします。完全な dora + MuJoCo IK の経路は SCS0009 公式 Demo のもので、[SCS0009 ハンドトラッキング](scs0009.md) を参照してください。

> 経路：カメラ → MediaPipe の手のスケルトン → 4 指の屈曲／伸展角度 → ESP32 → PWM サーボ
>
> 対象：ESP32-S3 + PWM サーボ 8 系統。ファームウェアの書き込みは [PWM クイックスタート](../02-quick-start/pwm.md)、プロトコルは [PWM プロトコルとキャリブレーション](../06-servo-tuning/pwm.md) を参照してください。

> 完全な IK（MuJoCo + dora + Rust）が必要な公式 Demo は本モジュールには同梱されていません。本チュートリアルはモジュール付属の GUI 内蔵トラッキングのみを扱います。

## 1. 前提条件

1. **ハードウェア**：ESP32-S3 + PWM サーボ 8 系統に通電し、USB を接続し、カメラが使用可能であること。
2. **ファームウェア**：書き込み済みであること（[PWM クイックスタート](../02-quick-start/pwm.md) を参照）。
3. **Python**：64 ビット Python 3.12（mediapipe 0.10.14 は 64 ビット用 wheel のみ）。

## 2. トラッキング依存関係のインストール

モジュールのルートディレクトリ（`AmazingHand-PWM/`）で実行します：

```bash
tools/setup_tracking.bat
```

スクリプトは自動的に：64 ビット Python を探す → `tools/tracking_env` 仮想環境を作成する → `tools/requirements-tracking.txt`（mediapipe 0.10.14、numpy<2、scipy、opencv、Pillow、pyserial）をインストールする → mediapipe を検証する、という処理を行います。

> 手動でインストールすることもできます（64 ビット Python 3.12 を使用）：
> ```bash
> python -m pip install -r tools/requirements-tracking.txt
> ```

## 3. 実行

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

1. 上部で ESP32 の COM ポートを選択 → 「Connect」をクリック。
2. 「ハンドトラッキング（MediaPipe カメラ）」パネルまでスクロール。
3. カメラ番号を選択（デフォルト 0）→ 「Start Tracking」をクリック。
4. 手を画角に入れると、多指ハンドが屈曲／伸展に追従します。「Stop Tracking」で終了します。

![GUI 内蔵ハンドトラッキングパネル：カメラ選択、開始、状態表示](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-tracking.png)

## 4. 原理と限界

- MediaPipe 0.10.14 が 4 指の指尖の 3D ベクトルを抽出します（手の座標系）。
- `hand_tracking.py` の `tips_to_angles()` が各指を差動角度へマッピングします：
  - flex（屈曲／伸展）：3 本の指は z 成分、親指は y 成分を使用。
  - base（左右の振り）：固定で 90（左右の振りは未実装）。
- これらは**制御軸**です。送信時にプログラムがそれらを各指の 2 つのサーボ角度へ合成します（同方向＝開き、逆方向＝屈伸）。
- GUI には EMA 平滑化（alpha=0.4）＋ 60 ms のスロットルが組み込まれ、揺れを抑えます。

限界：IK がないため、完全な MuJoCo + dora の経路ほど高精度ではありません。デモやクイックスタート向けです。

### パラメータのキャリブレーション

- `hand_tracking.py` 下部の `FLEX_SCALE` / `THUMB_FLEX_GAIN` が屈伸の振幅と方向を制御します（現在の値はファイルのコードを参照）。
- 左右の振りは未実装で、`base` は 90 に固定されています。左右の振りが必要な場合は SCS0009 公式 dora Demo を使用してください。
- 変更後は GUI を再起動すると反映されます。

## 5. 左右手の切り替え

GUI 上部の「右手」／「左手」をチェックします。切り替えると親指のミラー方向が変わるため、逆に感じたら反対側を選んで試してください。

## 6. よくある問題

| 現象 | 対処 |
|------|------|
| サーボがまったく動かない | 給電（5V 3A）、COM ポート、配線を確認。ファームウェアが書き込み済みか確認 |
| カメラの映像が出ない | カメラの権限を許可（設定→プライバシー→カメラ） |
| 手に追従しない／反応が鈍い | 光量を十分にし、手を完全に画角へ入れ、動きをゆっくり大きくする |
| 手の向きが逆／親指の向きが逆 | 逆側の左右手をチェック |
| USB ポートを変えたらシリアルポートが見つからない | GUI で COM ポートを選び直す |
| 起動時に mediapipe が無いと表示される | `tools\tracking_env\Scripts\python` で起動するか、`tools/setup_tracking.bat` を再実行 |

## 7. 完全な IK／SCS0009 バスサーボ

- 完全な IK 経路（カメラ → MediaPipe → MuJoCo + mink IK → AHControl → ESP32）は独立した dora Demo プロジェクトのもので、本モジュールには含まれません。必要な場合は元の配布パッケージまたは MediaPipe プロジェクトを使用してください。
- SCS0009 バスサーボはリポジトリの `Amazinghand-web/` と `AmazingHandControl/` が対応します。

## ディレクトリの説明

| パス | 内容 |
|------|------|
| `tools/hand_gui.py` | Tkinter デスクトップツール（ジェスチャー、直接駆動、差動、内蔵トラッキング） |
| `tools/hand_tracking.py` | MediaPipe ハンドトラッキングと角度マッピング |
| `tools/setup_tracking.bat` | `tools/tracking_env` を作成しトラッキング依存関係をインストール |
| `tools/requirements-tracking.txt` | トラッキング依存関係のリスト |
| `tools/serial_test.py` | コマンドラインのシリアルテスト |
