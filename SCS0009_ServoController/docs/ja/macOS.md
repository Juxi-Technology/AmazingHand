[English](../en/macOS.md) | [Deutsch](../de/macOS.md) | [Español](../es/macOS.md) | [Français](../fr/macOS.md) | [Italiano](../it/macOS.md) | 日本語 | [한국어](../ko/macOS.md) | [Português (BR)](../pt-br/macOS.md) | [Português (PT)](../pt-pt/macOS.md) | [简体中文](../zh-hans/macOS.md) | [繁體中文](../zh-hant/macOS.md)

# SCS0009 サーボデバッグツール — macOS ガイド

macOS 11（Big Sur）以降向け。要点：シリアルの命名規則（`cu.*` と `tty.*`）、USB ドライバ。

> ⚠️ **互換性：本ツールは現在、Feetech SCS0009 サーボ（SCS シリーズ、ポテンショメータ位置フィードバック、10 ビット分解能 0-1023）のみをサポートしています**。レジスタテーブルと xdat 形式は Feetech SCS0009 向けに設計されており、他ブランド/モデルでは保証されません。

---

## 1. 動作要件

| 依存関係 | バージョン |
|-----------|---------|
| Python | >= 3.8（3.10+ 推奨、Homebrew 経由） |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| OS | macOS 11+（Apple Silicon / Intel） |

## 2. Python のインストール

Homebrew 経由を推奨：

```bash
# Install Homebrew if missing
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

確認：

```bash
python3 --version
```

## 3. 依存関係のインストール

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **仮想環境の作成は 1 回だけにしてください**。再実行すると環境がリセット/上書きされます（インストール済みの依存関係が消去されます）。以降は `source .venv/bin/activate` するだけです。

## 4. ⚠️ macOS のシリアル命名規則 [重要]

macOS は USB シリアルデバイスを `/dev` 配下に**2 つの命名規則**で配置します：

| プレフィックス | 意味 | 使用可否 |
|--------|---------|--------|
| `/dev/tty.usbserial-*` | モデムスタイル（ブロッキング） | ハングする可能性があるため非推奨 |
| `/dev/cu.usbserial-*` | call/terminal スタイル（**ノンブロッキング**） | ✅ 推奨 |

**ポートを見つける：**

```bash
ls /dev/cu.*
```

一般的な出力：

```
/dev/cu.usbserial-0001      # CP2102 / FTDI
/dev/cu.usbmodem141101      # onboard USB serial (Arduino/ESP32)
/dev/cu.wchusbserial1420    # CH340
```

> ツールは `cu.*` デバイスを自動的に優先します。手動でポートを指定する場合は、`tty.` ではなく `cu.` を使用してください。

## 5. USB ドライバ

一般的なチップ（CH340、CP2102、FTDI）には macOS 用のドライバが組み込まれています。デバイスが認識されない場合：

```bash
system_profiler SPUSBDataType | grep -A5 -i "serial\|CH340\|CP210"
```

- **CH340**：古いロットでは WCH 公式ドライバが必要
- 一般的には、`ls /dev/cu.*` でデバイスが表示されれば十分

## 6. 環境の確認

```bash
python setup.py
```

## 7. GUI の起動

```bash
python -m src.gui.factory_calibration_tool
```

ポートを指定：

```bash
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 8. インターフェースの操作手順

> シングルパネルのレイアウト。ウィンドウが低すぎる場合はスクロールバーが自動的に表示され、最大化すると収まるように伸びます。

### 8.1 シリアル接続
ポートとボーレート（既定 1M）を選択し、**Connect** をクリックします。

### 8.2 サーボのスキャン
**Scan Servos** をクリックします（ID 1-254）。リストの行をクリックするとドロップダウンが自動入力されます。

### 8.3 パラメータの読み取り/書き込み
- 44 個すべてのレジスタを読み取り、行を選択するとリンクしてアドレス/長さ/値が自動入力される
- 自動ロック解除/書き込み/ロックで書き込み、成功/失敗のポップアップが表示される

### 8.4 位置制御
スライダーをドラッグ（0-1023）するか値を入力します。移動完了時にトルクをオフにするよう促すプロンプトが表示されます。

### 8.5 ボーレート / ファクトリリセット
ボーレートの変更（失敗時は自動ロールバック）、ファクトリリセット。

### 8.6 xdat パラメータ（EEPROM のみ）
現在のサーボを保存 → バックアップを開く → サーボへ復元。

## 9. トラブルシューティング

| 問題 | 解決策 |
|---------|----------|
| `tty.` のポートがハングする | 代わりに `cu.` プレフィックスを使用 |
| デバイスが見つからない | `ls /dev/cu.*`；差し直す；`system_profiler SPUSBDataType` |
| 中国語 UI が表示されない | 通常はシステムの PingFang で問題ありません。崩れる場合は Noto Sans CJK をインストール |
| 権限の問題 | macOS では通常、追加の権限は不要です。求められた場合はターミナルのアクセスを許可 |
| venv のアクティベートが失敗する | `source .venv/bin/activate`（`.bat` ではない） |
| Apple Silicon でのビルドエラー | Python 3.10+ はネイティブです。Rosetta の古い Python を避ける |

## 10. コマンドライン（任意）

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 11. ヒント

- **ポート名の変化**：`cu.*` の名前は USB ポートによって変わる場合があります。起動のたびにドロップダウンで選択してください
- **スリープ**：macOS がスリープしてシリアル接続が切れる場合があります。操作中はスリープさせないでください
- **プライバシー権限**：「リムーバブルディスクへのアクセス」を求められた場合は許可してください
