[English](../en/Linux.md) | [Deutsch](../de/Linux.md) | [Español](../es/Linux.md) | [Français](../fr/Linux.md) | [Italiano](../it/Linux.md) | 日本語 | [한국어](../ko/Linux.md) | [Português (BR)](../pt-br/Linux.md) | [Português (PT)](../pt-pt/Linux.md) | [简体中文](../zh-hans/Linux.md) | [繁體中文](../zh-hant/Linux.md)

# SCS0009 サーボデバッグツール — Linux ガイド

Ubuntu / Debian / その他の主要ディストリビューション向け。要点：シリアル権限（dialout）、USB-シリアルデバイスの検出。

> ⚠️ **互換性：本ツールは現在、Feetech SCS0009 サーボ（SCS シリーズ、ポテンショメータ位置フィードバック、10 ビット分解能 0-1023）のみをサポートしています**。レジスタテーブルと xdat 形式は Feetech SCS0009 向けに設計されており、他ブランド/モデルでは保証されません。

---

## 1. 動作要件

| 依存関係 | バージョン |
|-----------|---------|
| Python | >= 3.8（3.10+ 推奨） |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| OS | Ubuntu 20.04+ / Debian 11+ |

中国語フォント（中国語 UI に必要）：

```bash
sudo apt install fonts-noto-cjk
```

絵文字アイコンフォント（ログ内の ✅⚠️ など向け）：

```bash
sudo apt install fonts-noto-color-emoji
```

## 2. Python 依存関係のインストール

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **仮想環境の作成は 1 回だけにしてください**。再実行すると環境がリセット/上書きされます（インストール済みの依存関係が消去されます）。以降は `source .venv/bin/activate` するだけです。

> pip が「externally-managed-environment」を報告する場合は、venv を使うか `pip install --break-system-packages -r requirements.txt` を実行してください。

## 3. ⚠️ シリアル権限（dialout）[必須]

既定では、一般ユーザーは `/dev/ttyUSB*` / `/dev/ttyACM*` に**アクセスできません**。ユーザーを `dialout` グループに追加します：

```bash
sudo usermod -a -G dialout $USER
```

**ログアウトして再ログイン**します（または再起動）。確認：

```bash
groups
# output should include dialout
```

> 一部のディストリビューションでは `uucp`（Arch）や `tty` を使用します。

## 4. USB シリアルデバイスの特定

接続後：

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

一般的な出力：

```
/dev/ttyUSB0   # CH340 / CP2102 / PL2303
/dev/ttyACM0   # native USB serial (Arduino/ESP32 onboard)
```

## 5. 環境の確認

```bash
python setup.py
```

## 6. GUI の起動

```bash
python -m src.gui.factory_calibration_tool
```

ポートを指定：

```bash
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

> ポートが 1 つだけ存在する場合、ツールはそれを直接使用します。

## 7. インターフェースの操作手順

> シングルパネルのレイアウト。ウィンドウが低すぎる場合はスクロールバーが自動的に表示され、最大化すると収まるように伸びます。

### 7.1 シリアル接続
ポートとボーレート（既定 1M）を選択し、**Connect** をクリックします。

### 7.2 サーボのスキャン
**Scan Servos** をクリックします（ID 1-254）。リストの行をクリックするとドロップダウンが自動入力されます。

### 7.3 パラメータの読み取り/書き込み
- 44 個すべてのレジスタ（EEPROM + SRAM）を読み取り、行を選択するとリンクしてアドレス/長さ/値が自動入力される
- 自動ロック解除/書き込み/ロックで書き込み、成功/失敗のポップアップが表示される

### 7.4 位置制御
スライダーをドラッグ（0-1023）するか値を入力します。移動完了時にトルクをオフにするよう促すプロンプトが表示されます。

### 7.5 ボーレート / ファクトリリセット
ボーレートの変更（失敗時は自動ロールバック）、ファクトリリセット。

### 7.6 xdat パラメータ（EEPROM のみ）
現在のサーボを保存 → バックアップを開く → サーボへ復元。

## 8. トラブルシューティング

| 問題 | 解決策 |
|---------|----------|
| **Permission denied: /dev/ttyUSB0** | dialout グループに所属していません。セクション 3 を参照；または `sudo chmod 666 /dev/ttyUSB0`（一時的） |
| シリアルポートがない | `ls /dev/ttyUSB* /dev/ttyACM*`；`lsusb` でデバイスを確認 |
| デバイス名が変わる | ttyUSB の番号は接続順に依存します。udev ルールを使うか、起動のたびに選択してください |
| 中国語 UI が表示されない | `fonts-noto-cjk` をインストール |
| 絵文字が四角（豆腐）で表示される | `fonts-noto-color-emoji` をインストール |
| pip install が失敗する | venv を使用；または `--break-system-packages` |
| アプリが起動しない | `python3 --version` を確認；依存関係は `pip list` |

## 9. コマンドライン（任意）

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

## 10. 応用：udev による固定デバイス名（任意）

`/etc/udev/rules.d/99-servo.rules` を作成し、USB ID でデバイス名を固定します：

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyServo"
```

その後 `ls -l /dev/ttyServo`。ベンダー ID は `lsusb` で取得します。
