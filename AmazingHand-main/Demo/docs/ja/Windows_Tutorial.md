[English](../en/Windows_Tutorial.md) | [Deutsch](../de/Windows_Tutorial.md) | [Español](../es/Windows_Tutorial.md) | [Français](../fr/Windows_Tutorial.md) | [Italiano](../it/Windows_Tutorial.md) | 日本語 | [한국어](../ko/Windows_Tutorial.md) | [Português (BR)](../pt-br/Windows_Tutorial.md) | [Português (PT)](../pt-pt/Windows_Tutorial.md) | [简体中文](../zh-hans/Windows_Tutorial.md) | [繁體中文](../zh-hant/Windows_Tutorial.md)

# AmazingHand 器用なハンドのハンドトラッキング · Windows チュートリアル

本チュートリアルでは、AmazingHand（Pollen Robotics の器用なハンド）公式デモを、ワンクリックのデプロイスクリプトを使って解説します。
スクリプトは番号順に実行してください。**すべてのスクリプトは `Demo\Windows_Deploy_Scripts\` にあり、ダブルクリックで実行します。**

---

## 目次

1. [ハードウェアの準備](#1-ハードウェアの準備)
2. [環境のセットアップ（スクリプト 1）](#2-環境のセットアップスクリプト-1)
3. [配線](#3-配線)
4. [シリアルポートの設定（スクリプト 2）](#4-シリアルポートの設定スクリプト-2)
5. [コードのデプロイ（スクリプト 3）](#5-コードのデプロイスクリプト-3)
6. [デモの実行（スクリプト 4）](#6-デモの実行スクリプト-4)
7. [プロジェクトのクリーンアップ（スクリプト 0）](#7-プロジェクトのクリーンアップスクリプト-0)
8. [トラブルシューティングと注意事項](#8-トラブルシューティングと注意事項)
9. [コード構成](#9-コード構成)

---

## 1. ハードウェアの準備

| 項目 | 要件 |
|---|---|
| 器用なハンド | 右手 / 左手 / 両手 |
| サーボドライバ基板 | 外付け、USB で PC に接続 |
| 電源 | **少なくとも 5V 4A**（USB だけでは不足するため、外部電源を使用してください） |
| カメラ | 内蔵カメラまたは USB ウェブカメラ |

> モデルファイル（URDF など）は [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e) で閲覧・ダウンロードできます。

---

## 2. 環境のセットアップ（スクリプト 1）

**`1-Install_Env.bat` をダブルクリックします** — これは自動的に：

1. **MSVC ビルドツール（cl.exe）を確認** — Rust のコンパイルに必要です。ない場合は
   「C++ によるデスクトップ開発」ワークロードを含む Visual Studio 2022 Build Tools をインストールし、ターミナルを開き直します。
2. **Rust をインストール**（rustup + stable-msvc ツールチェーン）
3. **cargo の tuna ミラーを設定**（`C:\Users\<you>\.cargo\config.toml`）してクレートのダウンロードを高速化
4. **uv をインストール**（Python パッケージマネージャー）
5. **dora-cli 0.5.0 をインストール**（`cargo install`、初回コンパイルは約 10～20 分かかるので気長に待ってください）
6. **dora-rs の pip パッケージをインストール**（任意。デプロイ時に venv にもインストールされます）

> **重要**：スクリプト実行後は**ターミナルを閉じて開き直してください**。環境変数を反映させるためです。
> ネットワークによってはダウンロードが遅いことがあります — 中断せずに待ってください。

### 手動インストール（スクリプトが使用できない場合）

- **Rust**: <https://www.rust-lang.org/tools/install> — rustup-init.exe を使用し、既定の MSVC ツールチェーンを選びます。
  - PATH：`%USERPROFILE%\.cargo\bin` を追加
- **uv**: PowerShell：`irm https://astral.sh/uv/install.ps1 | iex`
  - PATH：`%USERPROFILE%\.local\bin` を追加
- **dora-cli**: `cargo install dora-cli --version 0.5.0`

### cargo tuna ミラー（config.toml）

```
[source.crates-io]
replace-with = "tuna"

[source.tuna]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[registries.tuna]
index = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[http]
check-revoke = false
```

> 必ず **sparse インデックス**（上記）を使用し、git リポジトリミラーは使わないでください。git ミラーはまず約 1 GB のインデックスをダウンロードし、`Updating 'tuna' index` で止まることがよくあります。

---

## 3. 配線

- サーボドライバ基板を USB で PC に接続し、**外部の 5V 4A 電源で給電します**
- ポートを確認します：**デバイスマネージャー → ポート（COM と LPT）**、例：`COM11`

---

## 4. シリアルポートの設定（スクリプト 2）

**`2-Setup_Serial.bat` をダブルクリックします**（ロジックは `2-Setup_Serial.ps1` にあります）：

1. 「ドライバ基板を接続してください」→ Enter を押してスキャン
2. 検出された COM ポートが一覧表示されます（デバイス名付き）
3. ポートが 1 つの場合は Enter で確定、複数の場合は番号を入力
4. 3 つの dataflow yml ファイルに `--serialport` を、`AHControl\src\main.rs` に既定のポートを書き込みます
5. 元のファイルは `.bak` としてバックアップされます

> USB ケーブルを抜き差しすると COM 番号が変わることがあります — このスクリプトを再実行してください。

---

## 5. コードのデプロイ（スクリプト 3）

**`3-Deploy_Demo.bat` をダブルクリックします** — これは自動的に：

1. dora デーモンを起動（`dora up`）
2. Python 3.12 の venv を作成（`uv venv --python 3.12`）
3. venv を有効化
4. AHControl の Rust ノードをビルド（`cargo build --release`、初回は約 10 分）
5. AHSimulation と HandTracking の依存関係を同期（`uv sync`）
6. mediapipe==0.10.14 を強制インストール（既知の落とし穴へのフォールバック）

> デプロイは一度だけ行います。再実行すると venv を再ビルドするか確認されます。

---

## 6. デモの実行（スクリプト 4）

**`4-Run_Demo.bat` をダブルクリックします** — 対話式メニュー：

```
============================================
  Select a run mode:
============================================
   1 - Simulation (webcam hand tracking)
   2 - Real hardware
   q - Quit
============================================
Enter number [1/2/q]:
```

- **1**：シミュレーション — ウェブカメラのジェスチャーで 2 つのシミュレーションハンドを動かします
- **2**：実機 — 右手／左手／両手のサブメニュー

```
============================================
  Real hardware - select the hand:
============================================
   1 - Right hand
   2 - Left hand
   3 - Both hands
   b - Back to main menu
============================================
```

その後 `dora build` + `dora run` を実行します。カメラウィンドウが開き、手のジェスチャーでハンドをリアルタイムに動かせます。**停止は Ctrl+C**。データフローが終了したら Enter を押してメニューに戻り、別のモードを選ぶか `q` で終了します。

> 初回実行時、Windows がカメラの権限を求めることがあります — 「許可」をクリックしてください。

---

## 7. プロジェクトのクリーンアップ（スクリプト 0）

**`0-Cleanup_Project.bat` をダブルクリック**し、`Y` と入力して確定します：

1. dora デーモンを停止
2. 3 つの仮想環境（`.venv`）を削除
3. Rust のビルド出力（`Demo\target`）を削除
4. `__pycache__`、`.bak` バックアップ、ログ、`Demo\out`（dora ログ）を削除
5. **既定のポートを復元**（`--serialport /dev/ttyACM0`）し、このマシンの COM の残りを消去します

> クリーンアップ後は、`AmazingHand-main` フォルダ全体を別のマシンへコピーできます — クリーンで移植可能です。
> 新しいマシンでは 1 → 2 → 3 → 4 の順に実行するだけです。

---

## 8. トラブルシューティングと注意事項

### 8.1 cargo が `Updating 'tuna' index` で止まる

- 原因：ミラーが **git-repo モード**（`.../git/crates.io-index.git`）で設定されており、初回実行で 1 GB 以上のインデックスをダウンロードする
- 対処：`C:\Users\<you>\.cargo\config.toml` を **sparse インデックス**に設定する（2.3 参照）、または `1-Install_Env.bat` を再実行する

### 8.2 mediapipe の solutions サブモジュールがない／インストールが壊れている

```bat
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- 有効化した venv 内（`Demo` フォルダ内）で実行してください
- `3-Deploy_Demo.bat` はすでにフォールバックとしてこれを行います

### 8.3 dora のバージョン不一致（メッセージ v0.8.0 と v0.7.0）

- 症状：`version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- 原因：dora-cli のバージョンが dora-node-api と異なる。**両方とも 0.5.0 である必要があります**
  - 確認：`dora --version` が `dora-cli 0.5.0` と `dora-message: 0.8.0` を表示するはずです
  - 対処：`cargo install dora-cli --version 0.5.0 --force`
  - `1-Install_Env.bat` は古いバージョンを自動検出し、0.5.0 を強制インストールするようになりました

### 8.4 MuJoCo / mediapipe のモデル読み込み失敗（中国語パス）

- 症状：`ParseXML: Error opening file '...\scene.xml'` または `Can't find file: ...\.tflite`
- 原因：MuJoCo 3.x / mediapipe の C++ ローダーは、**非 ASCII（中国語）文字を含む絶対パス**で失敗します（例：`D:\Claude工作区\...`）
- このプロジェクトにはすでに対処が含まれています：
  - `AHSimulation\AHSimulation\mj_mink_*.py` は読み込む前に作業ディレクトリを切り替えます
  - `HandTracking\mediapipe_patch.py` は 8.3 短縮パス + 相対パスを使用します
- **これらの修正ファイルを削除しないでください**

### 8.5 カメラの権限

- 初回実行時：「許可」を選択
- 設定 → プライバシー → カメラ → デスクトップアプリを許可

### 8.6 ポート番号が毎回変わる

- USB を抜き差しすると COM 番号が変わることがあります — `2-Setup_Serial.bat` を再実行してください

### 8.7 OpenCV が見つからない

```bat
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

（`HandTracking` フォルダ内、venv を有効化した状態で）

---

## 9. コード構成

### Demo フォルダ

| パス | 説明 |
|---|---|
| `AHControl` | サーボを制御する Rust ノード。エントリ：`src/main.rs` |
| `AHSimulation` | Python ノード：MuJoCo シミュレーション + 逆運動学（mink） |
| `HandTracking` | Python ノード：MediaPipe ハンドトラッキング |
| `dataflow_*.yml` | dora の dataflow 定義（ノードグラフ） |
| `Windows_Deploy_Scripts` | このスクリプトパック |

### dataflow ファイル

| ファイル | 用途 |
|---|---|
| `dataflow_tracking_simu.yml` | シミュレーション：ウェブカメラのジェスチャー → シミュレーションハンド |
| `dataflow_tracking_real_right.yml` | 実機の右手 |
| `dataflow_tracking_real_left.yml` | 実機の左手 |
| `dataflow_tracking_real_2hands.yml` | 実機の両手（同じドライバ基板） |

### データフローの原理

```
Webcam → HandTracking (MediaPipe hand detection)
              ↓ hand keypoints
         AHSimulation (MuJoCo simulation + IK)
              ↓ joint target angles
         AHControl (serial → servo driver board → hand)
```

### ポート設定の場所

- 3 つの `dataflow_tracking_real_*.yml` ファイルの `args:` 行：`--serialport COMxx`
- `AHControl\src\main.rs` の `default_value = "COMxx"`（serialport の既定値）
- `AHControl\config\*.toml`：サーボモデル、ID、オフセット（通常は変更不要）
