[English](../en/Linux_Tutorial.md) | [Deutsch](../de/Linux_Tutorial.md) | [Español](../es/Linux_Tutorial.md) | [Français](../fr/Linux_Tutorial.md) | [Italiano](../it/Linux_Tutorial.md) | 日本語 | [한국어](../ko/Linux_Tutorial.md) | [Português (BR)](../pt-br/Linux_Tutorial.md) | [Português (PT)](../pt-pt/Linux_Tutorial.md) | [简体中文](../zh-hans/Linux_Tutorial.md) | [繁體中文](../zh-hant/Linux_Tutorial.md)

# AmazingHand 器用なハンドのハンドトラッキング · Linux（Ubuntu）チュートリアル

本チュートリアルでは、AmazingHand（Pollen Robotics の器用なハンド）公式デモを、ワンクリックのデプロイスクリプトを使って解説します。
スクリプトは番号順に実行してください。**すべてのスクリプトは `Demo/Linux_Deploy_Scripts/` にあり、ターミナルで `./script` を実行します。**

---

## 目次

1. [ハードウェアの準備](#1-ハードウェアの準備)
2. [スクリプトの実行権限の付与（重要）](#2-スクリプトの実行権限の付与重要)
3. [環境のセットアップ（スクリプト 1）](#3-環境のセットアップスクリプト-1)
4. [配線](#4-配線)
5. [シリアルポートの設定（スクリプト 2）](#5-シリアルポートの設定スクリプト-2)
6. [コードのデプロイ（スクリプト 3）](#6-コードのデプロイスクリプト-3)
7. [デモの実行（スクリプト 4）](#7-デモの実行スクリプト-4)
8. [プロジェクトのクリーンアップ（スクリプト 0）](#8-プロジェクトのクリーンアップスクリプト-0)
9. [トラブルシューティングと注意事項](#9-トラブルシューティングと注意事項)
10. [コード構成](#10-コード構成)

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

## 2. スクリプトの実行権限の付与（重要）

**Windows や zip から Linux へスクリプトをコピーすると、実行権限（`+x`）が失われます** — そのまま実行すると
`Permission denied` になります。**初回使用の前に一度これを実行してください：**

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
chmod +x *.sh
```

これで各スクリプトを `./script` で実行できます。または次のようにまとめて実行することもできます：

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts" && chmod +x *.sh && ./1-Install_Env.sh
```

> ヒント：権限を保ったまま `AmazingHand-main` フォルダを Linux へ移動するには、**tar** でパッケージ化します：
> `tar czf AmazingHand-main.tar.gz AmazingHand-main`、または展開後に一度 `chmod +x *.sh` を実行するだけでもかまいません。

---

## 3. 環境のセットアップ（スクリプト 1）

スクリプトフォルダから（手順 2 の `chmod +x` の後で）実行します：

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
./1-Install_Env.sh
```

これは自動的に次を行います：

1. **Rust をインストール**（rustup + stable ツールチェーン）
2. **cargo の tuna ミラーを設定**（`~/.cargo/config.toml`）してクレートのダウンロードを高速化
3. **uv をインストール**（Python パッケージマネージャー）
4. **dora-cli 0.5.0 をインストール**（`cargo install`、初回コンパイルは約 10～20 分かかるので気長に待ってください）。古い dora のバージョンは自動検出され、強制的に置き換えられます。
5. **dora-rs の pip パッケージをインストール**（任意）

> **重要**：スクリプト実行後は**ターミナルを閉じて開き直してください**。環境変数を反映させるためです。
> いずれかのバージョンが空で表示される場合は、`~/.bashrc` に次を追加してください：
>
> ```bash
> export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
> ```

### 手動インストール（スクリプトが使用できない場合）

- **Rust**:
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```
- **uv**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **dora-cli**:
  ```bash
  cargo install dora-cli --version 0.5.0
  ```

### cargo tuna ミラー（~/.cargo/config.toml）

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

## 4. 配線

- サーボドライバ基板を USB で PC に接続し、**外部の 5V 4A 電源で給電します**
- ポートを確認します：
  ```bash
  ls /dev/ttyUSB* /dev/ttyACM*
  ```
  通常は `/dev/ttyACM0` です

---

## 5. シリアルポートの設定（スクリプト 2）

**`./2-Setup_Serial.sh` を実行します**：

1. 「ドライバ基板を接続してください」→ Enter を押してスキャン
2. 検出されたシリアルポートが一覧表示されます（`/dev/ttyACM*` / `/dev/ttyUSB*`）
3. ポートが 1 つの場合は Enter で確定、複数の場合は番号を入力
4. 3 つの dataflow yml ファイルに `--serialport` を、`AHControl/src/main.rs` に既定のポートを書き込みます
5. **シリアル権限を自動設定します**：
   ```bash
   sudo chmod 666 /dev/ttyACM0
   ```
   推奨：現在のユーザーを dialout グループに追加します（パスワードの再入力を避けられます。適用にはログアウト／ログインが必要です）：
   ```bash
   sudo usermod -aG dialout $USER
   ```

> VM 内で `ls /dev/ttyUSB* /dev/ttyACM*` が何も見つけない場合は、VM の設定で USB デバイスを VM に接続してください。

---

## 6. コードのデプロイ（スクリプト 3）

**`./3-Deploy_Demo.sh` を実行します** — これは自動的に：

1. dora デーモンを起動（`dora up`）
2. Python 3.12 の venv を作成（`uv venv --python 3.12`）
3. venv を有効化
4. AHControl の Rust ノードをビルド（`cargo build --release`、初回は約 10 分）
5. AHSimulation と HandTracking の依存関係を同期（`uv sync`）
6. mediapipe==0.10.14 を強制インストール（既知の落とし穴へのフォールバック）

> デプロイは一度だけ行います。再実行すると venv を再ビルドするか確認されます。

---

## 7. デモの実行（スクリプト 4）

**`./4-Run_Demo.sh` を実行します** — 対話式メニュー：

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

> Linux デスクトップにはカメラの権限が必要です（Ubuntu：設定 → プライバシー → カメラ）。カメラが他のアプリで使用されていないことを確認してください。VM のカメラ問題は [9.6](#96-カメラの権限--仮想マシンのカメラが動作しない) を参照してください。

---

## 8. プロジェクトのクリーンアップ（スクリプト 0）

**`./0-Cleanup_Project.sh` を実行**し、`Y` と入力して確定します：

1. dora デーモンを停止
2. 3 つの仮想環境（`.venv`）を削除
3. Rust のビルド出力（`Demo/target`）を削除
4. `__pycache__`、`.bak` バックアップ、ログ、`Demo/out`（dora ログ）を削除
5. **既定のポートを復元**（`--serialport /dev/ttyACM0`）し、このマシンのポートの残りを消去します

> クリーンアップ後は、`AmazingHand-main` フォルダ全体を別のマシンへコピーできます — クリーンで移植可能です。
> 新しいマシンでは 1 → 2 → 3 → 4 の順に実行するだけです。

---

## 9. トラブルシューティングと注意事項

### 9.1 `Permission denied`（スクリプトに実行権限がない）

- 症状：`bash: ./1-Install_Env.sh: Permission denied`
- 原因：Windows や zip からコピーした際に実行ビットが失われた
- 対処：
  ```bash
  chmod +x *.sh
  ```
  その後、`./script` で実行します（`bash script` ではなく）。

### 9.2 cargo が `Updating 'tuna' index` で止まる

- 原因：ミラーが **git-repo モード**（`.../git/crates.io-index.git`）で設定されており、初回実行で 1 GB 以上のインデックスをダウンロードする
- 対処：`~/.cargo/config.toml` を **sparse インデックス**に設定する（3.2 参照）、または `1-Install_Env.sh` を再実行する

### 9.3 mediapipe の solutions サブモジュールがない／インストールが壊れている

```bash
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- 有効化した venv 内（`Demo` フォルダ内）で実行してください
- `3-Deploy_Demo.sh` はすでにフォールバックとしてこれを行います

### 9.4 dora のバージョン不一致（メッセージ v0.8.0 と v0.7.0）

- 症状：`version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- 原因：dora-cli のバージョンが dora-node-api と異なる。**両方とも 0.5.0 である必要があります**
  - 確認：`dora --version` が `dora-cli 0.5.0` と `dora-message: 0.8.0` を表示するはずです
  - `1-Install_Env.sh` は古いバージョンを自動検出し、0.5.0 を強制インストールするようになりました

**古い dora（例：0.4.1）がシステムに残っている場合は、まずそれを削除してください：**

```bash
# 1. Find where the old dora is
which dora
ls -la ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora 2>/dev/null

# 2. Delete the found old versions (adjust paths; there may be several)
rm -f ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora

# 3. Force-install 0.5.0 (goes to ~/.cargo/bin)
cargo install dora-cli --version 0.5.0 --force

# 4. Verify (should print dora-cli 0.5.0 / dora-message: 0.8.0)
dora --version
```

> `dora --version` がまだ古いバージョンを示す場合、別の古いコピーが PATH のどこかに隠れています。`which dora` で見つけて削除し、`~/.cargo/bin` が PATH の前方にあることを確認してください。

### 9.5 シリアルポートのアクセス拒否

```bash
sudo chmod 666 /dev/ttyACM*
```

- 抜き差しすると権限がリセットされることがあります
- 恒久的な対処：`sudo usermod -aG dialout $USER` を実行し、ログアウト／ログインします

### 9.6 カメラの権限 / 仮想マシンのカメラが動作しない

**実機**:
- Ubuntu：設定 → プライバシー → カメラ → アプリを許可
- 他のアプリ（カメラアプリ、Zoom など）がウェブカメラを使用していないことを確認してください

**仮想マシン（VMware）のカメラが動作しない**:

症状：`open VIDEOIO(V4L2:/dev/video0): can't open camera by index` または `select() timeout`；
`/dev/video0` は存在し、`v4l2-ctl` はフレームをキャプチャできるのに、OpenCV の `cap.read()` が `ret = False` を返し続けます。

トラブルシューティングと対処（順番に）：

1. **カメラを VM に転送する**：メニュー → VM → リムーバブルデバイス → カメラ → 接続
2. **USB コントローラーのバージョンを切り替える（VMware で最も効果的）**：
   - VM → 設定 → **USB コントローラー** → `USB 2.0` / `USB 3.1` を切り替え
   - 切り替え後は**VM を再起動**してください
3. デバイスが存在することを確認します：
   ```bash
   ls -l /dev/video0
   sudo usermod -aG video $USER   # add to video group, log out/in
   ```
4. v4l2 でカメラが実際にフレームを生成できるか確認します（生成できればドライバは正常で、問題は OpenCV の互換性です）：
   ```bash
   v4l2-ctl --device=/dev/video0 --set-fmt-video=width=640,height=480,pixelformat=MJPG --stream-mmap --stream-count=1 --stream-to=/tmp/frame.jpg
   ls -l /tmp/frame.jpg   # tens to hundreds of KB = stream works
   ```

### 9.7 ポート番号が毎回変わる

- USB を抜き差しするとデバイス名が変わることがあります — `2-Setup_Serial.sh` を再実行してください

### 9.8 OpenCV が見つからない

```bash
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

（`HandTracking` フォルダ内、venv を有効化した状態で）

---

## 10. コード構成

### Demo フォルダ

| パス | 説明 |
|---|---|
| `AHControl` | サーボを制御する Rust ノード。エントリ：`src/main.rs` |
| `AHSimulation` | Python ノード：MuJoCo シミュレーション + 逆運動学（mink） |
| `HandTracking` | Python ノード：MediaPipe ハンドトラッキング |
| `dataflow_*.yml` | dora の dataflow 定義（ノードグラフ） |
| `Linux_Deploy_Scripts` | このスクリプトパック |

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

- 3 つの `dataflow_tracking_real_*.yml` ファイルの `args:` 行：`--serialport /dev/ttyACMx`
- `AHControl/src/main.rs` の `default_value = "/dev/ttyACM0"`（serialport の既定値）
- `AHControl/config/*.toml`：サーボモデル、ID、オフセット（通常は変更不要）
