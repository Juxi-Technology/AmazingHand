[English](../en/Windows.md) | [Deutsch](../de/Windows.md) | [Español](../es/Windows.md) | [Français](../fr/Windows.md) | [Italiano](../it/Windows.md) | 日本語 | [한국어](../ko/Windows.md) | [Português (BR)](../pt-br/Windows.md) | [Português (PT)](../pt-pt/Windows.md) | [简体中文](../zh-hans/Windows.md) | [繁體中文](../zh-hant/Windows.md)

# SCS0009 サーボデバッグツール — Windows ガイド

Windows 10 / 11 向け。インストールから本格的なサーボデバッグまでを扱います。

> ⚠️ **互換性：本ツールは現在、Feetech SCS0009 サーボ（SCS シリーズ、ポテンショメータ位置フィードバック、10 ビット分解能 0-1023）のみをサポートしています**。レジスタテーブルと xdat 形式は Feetech SCS0009 向けに設計されており、他ブランド/モデルでは保証されません。

---

## 1. 動作要件

| 依存関係 | バージョン | 備考 |
|-----------|---------|-------|
| Python | >= 3.8 | 3.10+ 推奨。[python.org](https://www.python.org/downloads/) からダウンロード |
| PySide6 | >= 6.0 | GUI フレームワーク |
| pyserial | >= 3.5 | シリアル通信 |
| OS | Win10 / Win11 | すべてのエディション |

## 2. Python のインストール

1. <https://www.python.org/downloads/> にアクセスする
2. Python 3.10+ のインストーラーをダウンロードする
3. インストール時に **「Add Python to PATH」にチェックを入れる**（そうしないとターミナルで python が見つかりません）

確認：

```bash
python --version
```

## 3. 依存関係のインストール

システム Python を汚さないよう、仮想環境にインストールします：

```bash
cd SCS0009_ServoController
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> ⚠️ **仮想環境の作成は 1 回だけにしてください**。再実行すると環境がリセット/上書きされます（インストール済みの依存関係が消去されます）。以降は、毎回 `activate` するだけです。

> アクティベート後、プロンプトに `(.venv)` が表示されます。

## 4. 環境の確認

```bash
python setup.py
```

`[OK] 环境检查通过，可以运行项目` は環境の準備が整ったことを意味します。

## 5. ハードウェアの接続

1. USB-シリアルアダプタ（CH340 / CP2102）を差し込む
2. サーボコントローラ（ロボットアーム制御ボード）を接続する
3. サーボに通電する（DC 5V 5A 標準、DC 12V 5A Pro）

デバイスマネージャーで COM ポートを確認します（`Win+X` → デバイスマネージャー）：

```
Ports (COM & LPT)
  └─ USB-SERIAL CH340 (COM3)     ← your servo port
```

> 起動時に選択するため、**COM 番号を控えておいて**ください。

## 6. GUI の起動

```bash
python -m src.gui.factory_calibration_tool
```

またはポートを指定：

```bash
python -m src.gui.factory_calibration_tool --port COM3
```

利用可能なポートを一覧表示：

```bash
python -m src.gui.factory_calibration_tool --list-ports
```

## 7. インターフェースの操作手順

> シングルパネルのレイアウト。ウィンドウが低すぎる場合はスクロールバーが自動的に表示され、最大化すると収まるように伸びます。

### 7.1 シリアル接続

- ポートとボーレート（既定 1M）を選択し、**Connect** をクリック
- ステータスに `🟢 Connected` が表示される

### 7.2 サーボのスキャン

- **Scan Servos** をクリックしてオンラインのサーボを検出（ID 1-254）
- 結果はサーボリストにリアルタイムで表示される（型番付き）
- リストの行をクリック → サーボのドロップダウンが自動入力される

### 7.3 パラメータの読み取り/書き込み

- **Read Params**：44 個すべてのレジスタ（EEPROM + SRAM）を読み取り、ログに結果がリアルタイムで表示される
- **Parameter Table**：5 列（Address/Register/Value/Memory/Access）。EEPROM/SRAM/DEFAULT で色分けされる
- **Row Select Linkage**：行をクリック → 「Write Address」「Length」「Value」が自動入力される
- **Write**：値を変更して書き込みをクリック。ツールが EEPROM のロック解除/書き込み/ロックを自動で行う
- **Write Result Popup**：成功時は緑の「✅ Written successfully」、失敗時は赤の「❌ Write failed」（理由付き）

### 7.4 位置制御

- **Slider**：ドラッグして目標位置を調整（0-1023）。値ボックスがリアルタイムで更新される
- **Value box**：目標位置を直接入力すると、スライダーが追従する
- 移動後、ステータスに「move complete, please turn off torque」が表示される

### 7.5 ボーレート / ファクトリリセット

- **Change Baud Rate**：38400-1000000 bps を選択、失敗時は自動ロールバック
- **Factory Reset**：工場出荷時の既定値に戻す（ID=1、baud=1M）。再スキャンが必要

### 7.6 xdat パラメータ（EEPROM のみ）

1. `💾 Save Current Servo`：現在のサーボの EEPROM パラメータを xdat ファイルに保存（バックアップ）
2. `📂 Open xdat`：バックアップファイルを読み込む
3. `📤 Restore to Servo`：バックアップをサーボへ書き戻す

## 8. トラブルシューティング

| 問題 | 解決策 |
|---------|----------|
| シリアルポートがない | デバイスマネージャーでドライバを確認；別の USB ポートを試す；CH340 ドライバをインストール |
| ポートが使用中 | シリアルモニタを閉じる；ツールを再起動 |
| 中国語テキストが表示されない | システムに Microsoft YaHei があります。表示が崩れる場合は CJK フォントをインストール |
| サーボが見つからない | 電源/配線を確認；1M ボーレートを確認 |
| 書き込みが失敗する | サーボの電源と接続を確認；レジスタが書き込み可能か確認 |
| ポートを開く際に PermissionError | 他のプロセスが COM ポートを保持していないことを確認 |

## 9. コマンドライン（任意）

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port COM3
```
