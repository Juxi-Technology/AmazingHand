[English](../en/user_manual.md) | [Deutsch](../de/user_manual.md) | [Español](../es/user_manual.md) | [Français](../fr/user_manual.md) | [Italiano](../it/user_manual.md) | 日本語 | [한국어](../ko/user_manual.md) | [Português (BR)](../pt-br/user_manual.md) | [Português (PT)](../pt-pt/user_manual.md) | [简体中文](../zh-hans/user_manual.md) | [繁體中文](../zh-hant/user_manual.md)

# AmazingHand Controller – ユーザーマニュアル

> **バージョン：** 2026-03-22  
> **対象：** `amazing_hand_gui.py` (GUI)、`amazing_hand_cmd.py` (CLI)

---

## 1. はじめに

AmazingHand Controller GUI は、Feetech SCS0009 アクチュエータで駆動する 8 サーボのロボットハンドに対して、リアルタイム監視と手動制御を提供します。インターフェースは、指の制御、グローバル管理、テレメトリの可視化、アクティビティログのパネルに分かれています。本ガイドでは、インストール、操作方法、よくあるワークフローを順を追って説明します。

> **ヒント：**GUI を操作する間は、このマニュアルを開いておいてください。アプリケーションに埋め込まれたツールチップは、コントロールにカーソルを合わせると同じ説明を繰り返します。

![AmazingHand hardware with controller connected](../en/screenshots/hand_overview.png)

---

## 2. クイックスタートチェックリスト

1. **依存関係のインストール**（環境ごとに 1 回）：
   ```bash
   python -m pip install -r requirements.txt
   ```
2. **ハードウェアへの通電：**5 V 電源をサーボチェーンに接続し、USB シリアルアダプタを差し込みます。
3. **GUI の起動：**
   ```bash
   python amazing_hand_gui.py
   ```
4. **コントローラへの接続：**シリアル**ポート**（例：`COM9`）を選択し、**▶ Connect** をクリックします。
5. **テレメトリの確認：**グラフとフィードバックテーブルにライブ更新が表示されることを確認します。

---

## 3. 画面の概要

```
+--------------------------------------------------------------------------------+
|                              AmazingHand Controller                            |
+---------------------------+-----------------------------------------------+----+
| Finger Controls           | Chart Controls & Telemetry Plot                    |
| (Ring – Middle – Pointer) | (Display menu, chart canvas)                       |
+---------------------------+-----------------------------------------------+----+
| Control Stack             | Thumb finger   | Feedback Table (Servo Metrics)    |
| (Connection, Global, Pose,| control        | (Goal, Position, Load, etc.)      |
|  Sequence)                |                |                                   |
+---------------------------+                                                    |
| Execution Log & Status    |                                                    |
+--------------------------------------------------------------------------------+
```

![Main window overview highlighting the major panels](../en/screenshots/mainscreen.png)

### 3.1 パネル一覧

| パネル | 位置 | 目的 |
|-------|----------|---------|
| **指コントロール** | 左、上部（3 本の指）+ 右下（親指） | 各指ペアの個別スライダーと速度セレクター。Mimic インジケーターと指ごとのステータス LED を含む。 |
| **右コントロールスタック** | 左、右下 | 接続設定、グローバルコントロール、ポーズ管理、シーケンスプレイヤー。 |
| **テレメトリパネル** | 右 | ズーム/パンスライダー付きのリアルタイムグラフと、設定可能なフィードバックテーブル。 |
| **実行ログ** | 下 | ステータスメッセージ、警告、シーケンスの進行状況のストリーム。 |

---

## 4. パネル詳細ガイド

### 4.1 指制御パネル（左カラム）

各指ウィジェットは 1 対のサーボ（位置 + 左右オフセット）を制御します：

- **モード切替：****Auto**（base + offset スライダー）と **Raw**（サーボ目標値を直接指定）を切り替えます。
- **ステータス LED：**グレー（アイドル）、緑（動作中）、赤（ブロックの可能性、負荷と目標の比較に基づく）。
- **位置スライダー：**0–110°（開く〜閉じる）。マウスホイールで 1° ずつ調整、ドラッグはすばやく追従します。
- **左右スライダー：**±40°、左右の調整用。親指の左右スライダーは**反転**しており、物理的な方向がハンドの解剖学的な向きに一致します——右へドラッグすると、ハードウェアの取り付けに対して親指が正方向に動きます。
- **速度セレクター：**指ペアの両方のサーボの動作速度を制御する 1–6 のドロップダウン。
- **Mimic チェックボックス：**Auto モード中、協調動作のためにソース指からの開閉動作をミラーリングします。

**指モード：Auto と Raw**

- **Auto モード**（既定）は、開閉スライダー、左右オフセットスライダー、速度ドロップダウン、Center ボタンを表示します。GUI は、`data/hand_config.yaml` に保存されたキャリブレーション済みの極値を用いて、これら 2 つのスライダー値をサーボコマンドへ合成するため、手作業でのサーボ計算なしに、指ペアが自然な指のポーズを追従します。Mimic はここでも有効です——複数の指で有効にすると、現在調整している指と同期して駆動できます。
- **Raw モード**は、Auto のコントロールを、サーボごとにラベル付けされた 2 つの垂直スライダーに置き換えます。エンドストップのテスト、キャリブレーションの検証、リンケージの問題の診断を行う際に、基になるサーボ角度を直接指令するには、これらを動かします。Raw は自動ミックス処理を経由しないため、Center ボタンと Mimic チェックボックスは無効化されますが、キーボードショートカットは引き続き機能し、上/下がサーボ 1、左/右がサーボ 2 を駆動します。Raw は最後に選択した速度値を使用するため、特定の動作速度が必要な場合は切り替える前に速度を設定してください。

**Auto モードがサーボ目標値を計算する方法**

- 開閉スライダーの値は `limits.base_min/base_max` にクランプされた後、正規化され（`t = base / base_max`）、指の各側について `auto_extremes` の開いたポーズと閉じたポーズの間を補間します。
- 左右オフセットスライダーは `limits.side_min/side_max` にクランプされ、ブレンド係数（`u`）に変換されます。負のオフセットは中央のポーズから `left_open`/`left_closed` へ補間し、正のオフセットは右側の極値へ補間します。
- 左右オフセットがない場合、両方のサーボはそのまま base スライダーの値を受け取ります。最終的なサーボ目標値は発行前に `limits.servo_min/servo_max` にクランプされ、動作はキャリブレーション済みの安全範囲内に保たれます。

キーボードショートカットはスライダーを補完します（§5.2 に記載）。

![Finger control panel with per-finger sliders and status indicators](../en/screenshots/finger_control_frame.png)

### 4.2 グローバルコントロールスタック（指パネルの右）

1. **Connection：**ポートとボーレートの選択（接続中は両方のドロップダウンが無効化されます）、connect/disconnect ボタン。下部のステータスバーが成功またはエラーを報告します。
2. **Global Controls：**
   - **Open All / Close All / Center All** – すべての指に即座に適用します。
   - **Global Speed ドロップダウン** – 指ごとの速度セレクターを共通の値（1–6）に設定します。
3. **Pose Management：**`data/hand_config.yaml` に保存されたポーズを保存、読み込み、適用、削除します。
   - レイアウト：`Pose: [dropdown]  ✓ Apply  🗑 Delete  Name: [entry]  ➕ Add New`
   - **🗑 Delete** は選択したポーズを完全に削除します（確認ダイアログが表示されます）。
4. **Sequence Player：**多段階のアニメーションを選択して実行します。ループは任意です。シーケンスマネージャーダイアログには **🔧 Manage** からアクセスします。

![Connection, global controls, pose management, and sequence player stack](../en/screenshots/control_frame.png)

### 4.3 テレメトリとフィードバックパネル（右カラム）

- **コントロール行：**
  - グラフ更新の一時停止/再開。
  - ローリングウィンドウの切り替え。
  - 指標の選択（位置、負荷、速度、温度、電圧、moving フラグ）。
  - モード切替（Multi-Servo と Scope）。後者ではサーボセレクターを伴う。
  - サーボ表示ドロップダウンと「All/None/Clear」ヘルパー。
  
![Display mode, metric selection, and scope controls](../en/screenshots/chart_mode_controls.png)

![Display menu for choosing telemetry metrics](../en/screenshots/chart_select_display_values.png)

![Servo visibility menu with quick actions](../en/screenshots/chart_servos_selection.png)

#### グラフモード

- **Multi-Servo**（既定）は、有効なすべてのサーボのトレースをグラフに表示します。**Servos** ドロップダウンでグループをすばやくオン/オフし、指ごとの動作や負荷を比較できます。
- **Scope** は **Scope Servo** セレクターを有効にし、同じ指標チェックボックスを使いながら単一のチャンネルに注目できます。このモードをサーボ表示メニューと組み合わせると（例：すべて非表示にしてからスコープサーボを再度有効にする）、他のトレースのないオシロスコープ風の表示が得られます。
- モードにかかわらず、テレメトリテーブルはすべてのサーボを表示し続けるため、注目しているグラフとより広いデータのスナップショットを関連付けることができます。
- **グラフ領域：**選択したテレメトリを表示する Matplotlib プロット。スライダーでズーム：
  - **Y Zoom / Pan：**垂直方向のスケーリングとシフト。
  - **Time Zoom / Pan：**最近の履歴または古いサンプルに注目。
- **フィードバックテーブル：**各サーボの目標、位置、速度、負荷、電圧、温度、ステータス、moving フラグをまとめたスクロール可能なグリッド。

![Chart controls with zoom/pan sliders and telemetry traces](../en/screenshots/chart_frame.png)

![Feedback table showing live servo metrics](../en/screenshots/feedback_frame.png)

### 4.4 実行ログとステータスバー

指パネルの下に位置するログは、操作を時系列順に記録します。ステータスバーは最新の操作または警告を表示します。

![Execution log and current status bar](../en/screenshots/log_and_last_action_frame.png)

---

## 5. ハンドの操作

### 5.1 ハードウェアへの接続

1. サーボに通電し、USB アダプタを接続します。
2. GUI を起動し、正しい**ポート**が自動選択されることを確認します（Windows では `COM*`、Linux/macOS では `/dev/tty*`）。
3. **▶ Connect** をクリックします。成功するとボタンの状態が変わり、ステータスバーが更新されます。
4. 接続に失敗した場合は、ケーブル、電源、ポートの割り当てを確認してください。

### 5.2 手動操作とショートカット

- キー **1–4** で指を選択します（1 = 薬指、2 = 中指、3 = 人差し指、4 = 親指）。
- **矢印キー：**上/下で位置を調整、左/右で左右オフセットを調整します。
- **Shift** を押しながらだとステップ幅が 5 倍、**Ctrl** は 10 倍になります。
- **Q / E：**選択した指を完全に閉じる / 開く。
- **C：**左右オフセットを中央に。
- 画面上のスライダーは、キーボード入力をリアルタイムで反映します。

![Manual finger control panel with keyboard shortcut overlay](../en/screenshots/manual_finger_control_frame.png)

![Example of fully closing a finger using controls](../en/screenshots/close_finger.png)

![Example of lateral movement adjustment](../en/screenshots/move_finger.png)

### 5.3 速度の設定

- 指ごとの速度ドロップダウン（1 = 遅い、6 = 速い）がサーボの速度を制御します。
- **Global Speed** セレクターがすべての指の速度を同期します。
- 動作中はフィードバックテーブル（`Speed` 行）で速度の変化を観察します。

### 5.4 ポーズの適用と削除

1. スライダーまたはキーボードショートカットで指の位置を整えます。
2. **Pose Management** で一意の名前を入力し、**➕ Add New** をクリックします。
3. 適用するには、ドロップダウンからポーズを選択し、**✓ Apply** をクリックします。
4. 削除するには、ドロップダウンからポーズを選択し、**🗑 Delete** をクリックします。確認ダイアログが誤削除を防ぎます。

> ポーズはサーボ位置のみを保存します。速度は実行時に GUI の設定によって決まります。

### 5.5 シーケンスの構築と実行

1. Sequence Player で **🔧 Manage** をクリックします。
2. ダイアログ内で：
   - **Available Poses** リストを使ってステップを追加します（ダブルクリックまたは **➕ Add** を押す）。
   - スピンボックスで指ごとの速度を調整し、任意のステップ遅延を設定します。
   - **⏱ Delay** を使って専用のスリープ区間を挿入します。
   - ↑/↓ ボタンでステップを並べ替えます。
   - 名前を入力し、**💾 Save Sequence** をクリックします。
   - 保存せずにテストするには **▶ Execute** をクリックします。
3. メインウィンドウに戻り、シーケンスを選択して **▶ Play** を押します。連続再生には **Loop** を有効にします。

> シーケンス定義は `data/hand_config.yaml` の `sequences` キーの下にあります。ループは実行時側で制御され、YAML にはありません。

![Sequence manager dialog with available poses and sequence builder](../en/screenshots/sequences_editor.png)

### 5.6 テレメトリの監視

- 必要な指標が **Display** メニューでチェックされていることを確認します。
- ズーム/パンスライダーで関心のある区間に注目します。
- グラフ要素にカーソルを合わせると（Matplotlib 標準の操作）、値を確認できます。
- フィードバックテーブルは非同期で更新されます。強調表示されたセルは最近の変更を示します。
- グラフが煩雑になった場合は、**⌫ Clear** をクリックして収集したデータをリセットします。

---

## 6. コマンドラインインターフェース（`amazing_hand_cmd.py`）

CLI を使うと、GUI を起動せずにターミナルから直接ポーズを適用し、シーケンスを再生できます。同じ `data/hand_config.yaml` ファイルを読み取ります。

### 6.1 基本的な使い方

```bash
# List all saved poses and sequences
python amazing_hand_cmd.py --list

# Apply a single pose
python amazing_hand_cmd.py --pose open
python amazing_hand_cmd.py --pose close

# Play a sequence once
python amazing_hand_cmd.py --sequence demo

# Play a sequence in a loop (Ctrl+C to stop)
python amazing_hand_cmd.py --sequence wave --loop
```

### 6.2 オプション

| オプション | 既定値 | 説明 |
|--------|---------|-------------|
| `--pose NAME` | – | 指定したポーズを適用して終了 |
| `--sequence NAME` | – | 指定したシーケンスを再生して終了 |
| `--list` | – | すべてのポーズとシーケンスを一覧表示 |
| `--loop` | off | Ctrl+C までシーケンスを連続ループ |
| `--port PORT` | `/dev/ttyACM0` (Linux) / `COM9` (Win) | シリアルポートの上書き |
| `--baudrate N` | `1000000` | ボーレートの上書き |
| `--config PATH` | `data/hand_config.yaml` | 代替設定ファイルへのパス |

### 6.3 注意事項

- トルクは接続時に**有効化**され、終了時に**無効化**されるため、スクリプト終了後にサーボが脱力します。
- ステップごとの速度と遅延は、GUI のシーケンスプレイヤーとまったく同じように動作します。
- `--loop` フラグは `--sequence` と組み合わせてのみ使用できます。

---

## 7. トラブルシューティング

| 症状 | 推奨される対処 |
|---------|-----------------|
| **シリアルポートが表示されない** | USB アダプタを差し直す、ドライバをインストールする、または GUI を再起動します。 |
| **Connect ボタンがグレーアウトしている** | すでに接続済みです。先に **⏹ Disconnect** をクリックしてください。 |
| **サイズ変更中に UI が重い** | パフォーマンス最適化（デバウンスされたリサイズ、スロットリングされた再描画）がこれを最小限に抑えますが、不要なウィンドウを閉じると改善する場合があります。 |
| **シーケンスですべての指が動かない** | ステップごとの速度を確認し、各ポーズが 8 個すべてのサーボ値を含んでいることを確かめてください。 |
| **ブロックインジケーターが消えない** | 機械的な障害物を調べます。ブロック状態は、目標と位置が大きく異なり、かつ動作がない場合にトリガーされます。 |

---

## 8. 付録

### 8.1 ファイル構成

```
AmazingHandControl/
├── amazing_hand_gui.py          # GUI application
├── amazing_hand_cmd.py          # CLI tool
├── data/hand_config.yaml        # Poses & sequences
├── data/config.yaml             # Application settings
├── docs/<lang>/user_manual.md        # This document
├── docs/<lang>/CONFIG_FORMAT.md      # YAML config file reference
├── docs/en/screenshots/              # PNG captures embedded in this manual
├── docs/<lang>/scs_servo_protocol.md # SCS servo protocol reference
└── README.md                    # Quick reference
```

### 8.2 参考リンク

- [AmazingHand（公式プロジェクト）](https://github.com/pollen-robotics/AmazingHand)
- [Feetech サーボデバッグツール](https://github.com/Robot-Maker-SAS/FeetechServo/tree/main/feetech%20debug%20tool%20master/FD1.9.8.2)
- [サーボの識別チュートリアル](https://www.robot-maker.com/forum/tutorials/article/168-brancher-et-controler-le-servomoteur-feetech-sts3032-360/)

---

## 9. 改訂履歴

| 日付 | 作者 | 備考 |
|------|--------|-------|
| 2026-03-22 | Ingo | CLI（`amazing_hand_cmd.py`）セクションを追加；マニュアルのバージョンを更新。 |
| 2026-03-21 | Ingo | パネルレイアウトの更新：薬指/人差し指を入れ替え、親指を右へ移動、コントロールスタックを左へ移動。親指の左右スライダーを反転。Apply と Name の間にポーズ削除ボタンを追加。接続中はポートとボーレートのドロップダウンをロックするように。キーボードショートカット 1–4 が薬指/中指/人差し指/親指にマッピングされるように。 |
| 2025-11-25 | Ingo | 拡張スクリーンショットギャラリー、グラフモードの説明、刷新されたパネルウォークスルーを追加。 |
| 2025-11-25 | Ingo | UI パネル、ワークフロー、テレメトリの使用法を扱う初版マニュアル。 |
