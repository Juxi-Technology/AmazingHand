[English](../en/CONFIG_FORMAT.md) | [Deutsch](../de/CONFIG_FORMAT.md) | [Español](../es/CONFIG_FORMAT.md) | [Français](../fr/CONFIG_FORMAT.md) | [Italiano](../it/CONFIG_FORMAT.md) | 日本語 | [한국어](../ko/CONFIG_FORMAT.md) | [Português (BR)](../pt-br/CONFIG_FORMAT.md) | [Português (PT)](../pt-pt/CONFIG_FORMAT.md) | [简体中文](../zh-hans/CONFIG_FORMAT.md) | [繁體中文](../zh-hant/CONFIG_FORMAT.md)

# ハンド設定フォーマット（YAML）

本書では、AmazingHand が使用する YAML 設定ファイルについて説明します。

| ファイル | 目的 |
|------|---------|
| `data/hand_config.yaml` | ポーズとシーケンス（GUI と CLI で作成/編集） |
| `data/config.yaml` | アプリケーション設定（シリアルポート、サーボ限界、速度、パス） |

---

## `data/config.yaml` – アプリケーション設定

GUI が起動時に読み込みます。ファイルが存在しない場合は、組み込みの既定値が使用されます。
CLI も同じ既定値を使用します（`--port` / `--baudrate` で上書き可能）。

### 全体構造

```yaml
# Serial port settings
serial:
  port_windows: COM9          # Default port on Windows
  port_linux: /dev/ttyACM0   # Default port on Linux/macOS
  baudrate: 1000000           # Default baud rate
  baudrate_options: [9600, 115200, 1000000]  # Shown in GUI dropdown

# Servo assignments — [servo1_id, servo2_id] per finger
# servo1 (odd ID)  = position axis (open/close)
# servo2 (even ID) = side axis (left/right)
servos:
  ring:    [1, 2]
  middle:  [3, 4]
  pointer: [5, 6]
  thumb:   [7, 8]
  all_ids: [1, 2, 3, 4, 5, 6, 7, 8]

# Servo angle limits (degrees)
limits:
  servo_min: -40   # Absolute minimum for any servo command
  servo_max: 110   # Absolute maximum for any servo command
  base_min: 0      # Open/close slider minimum
  base_max: 110    # Open/close slider maximum
  side_min: -40    # Left/right slider minimum
  side_max: 40     # Left/right slider maximum

# Movement speeds (1–6 scale, where 6 is fastest)
speeds:
  default: 3
  min: 1
  max: 6

# Auto-mode blending extremes — [servo1_deg, servo2_deg]
# Used to interpolate combined position+side values in Auto mode
auto_extremes:
  left_open:    [32, -40]
  right_open:   [-40, 32]
  left_closed:  [110, 110]
  right_closed: [110, 110]
  center_open:  [0, 0]
  center_closed: [110, 110]

# File paths (relative to project root)
paths:
  poses_sequences_file: data/hand_config.yaml
```

### 注意事項
- すべてのキーは任意です——欠落したキーは上記の組み込み既定値にフォールバックします。
- ここにポーズやシーケンスを保存し**ないでください**。それらは `data/hand_config.yaml` に属します。
- このファイルを編集した後は、変更を反映するために GUI を再起動してください。

---

## `data/hand_config.yaml` – ポーズとシーケンス

GUI と CLI によって作成・編集されます。両方のツールで共有されます。

### YAML 構造

```yaml
poses:
  <pose_name>:
    positions: [pos1, pos2, pos3, pos4, pos5, pos6, pos7, pos8]

sequences:
  <sequence_name>:
    steps:
      - "<pose_name>:speed1,speed2,...,speed8|delay"
      - "SLEEP:duration"
```

## ポーズ

各ポーズは、8 個のサーボ値で 1 つの完全なハンド位置を定義します。

### フォーマット
```yaml
poses:
  pose_name:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
```

### 位置配列
- **8 個の値**で、サーボ位置を度数で表します
- **サーボ対応**：
  - サーボ 1：人差し指の位置（0=開く、110=閉じる）
  - サーボ 2：人差し指の左右（-20=左、0=中央、+20=右）
  - サーボ 3：中指の位置
  - サーボ 4：中指の左右
  - サーボ 5：薬指の位置
  - サーボ 6：薬指の左右
  - サーボ 7：親指の位置
  - サーボ 8：親指の左右

- **開閉スライダー範囲**：指ごとに 0-110°（0=開く、110=閉じる）
- **左右スライダー範囲**：-40°（左）〜+40°（右）
- **保存されるサーボ値**：YAML は合成値（base ± side）を保存するため、実際のサーボコマンドはおおむね -40° 〜 150° の範囲になると想定されます
- **備考**：偶数番号のサーボ（2,4,6,8）はハードウェア上で角度が反転しています

### 命名規則
- 使用できるのは英字、数字、アンダースコア
- **禁止文字**：`: { } [ ] , & * # ? | - < > = ! % @ \` " '`
- 最大 50 文字
- 大文字と小文字を区別

### 例
```yaml
poses:
  open:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
  close:
    positions: [110, 0, 110, 0, 110, 0, 110, 0]
  peace:
    positions: [0, 0, 110, 0, 0, 0, 0, 0]
```

## シーケンス

シーケンスは、サーボごとの速度と遅延を伴う多段階のアニメーションを定義します。

### フォーマット
```yaml
sequences:
  sequence_name:
    steps:
      - "pose_name:speed1,speed2,speed3,speed4,speed5,speed6,speed7,speed8|delay"
      - "SLEEP:duration"
```

### ステップフォーマット

**個別速度と遅延を伴うポーズ：**
```
"pose_name:s1,s2,s3,s4,s5,s6,s7,s8|delay"
```
- `pose_name`：実行するポーズの名前
- `s1-s8`：各サーボの個別速度（1-6、6 が最速）
- `delay`：動作完了後に待機する時間（例：`2.0s`）

**既定速度のポーズ：**
```
"pose_name:3,3,3,3,3,3,3,3|2.0s"
```

**スリープ/一時停止：**
```
"SLEEP:1.5s"
```
- 指定した時間だけサーボを動かさずに一時停止します

### 速度値
- 範囲：1（最遅）〜6（最速）
- サーボの動作速度を制御します
- ステップ内でサーボごとに異なる速度を指定できます

### ループ制御
- ループ設定は YAML に**保存されません**
- GUI のシーケンスプレイヤーのチェックボックスで制御します
- YAML を編集せずに柔軟な再生が可能です

### 例
```yaml
sequences:
  demo:
    steps:
      - "open:3,3,3,3,3,3,3,3|2.0s"
      - "close:3,3,3,3,3,3,3,3|2.0s"
      - "open:3,3,3,3,3,3,3,3|1.0s"
  
  wave:
    steps:
      - "open:5,5,5,5,5,5,5,5|0.5s"
      - "SLEEP:0.3s"
      - "close:5,5,5,5,5,5,5,5|0.5s"
      - "SLEEP:0.3s"
```

## ポーズとシーケンスの管理

### GUI から（`amazing_hand_gui.py`）

**ポーズ：**
1. スライダーまたはキーボードで指の位置を決める
2. 「Name:」欄に名前を入力する
3. 「➕ Add New」をクリックして保存する

**シーケンス：**
1. Sequence Player セクションの「Manage」ボタンをクリックする
2. ダイアログでシーケンスを構築する：
   - ポーズと速度を選択する
   - ステップ間に遅延を追加する
   - ↑/↓ ボタンで並べ替える
3. シーケンス名を入力し、「💾 Save」をクリックする

**実行：**
- ドロップダウンからシーケンスを選択する
- 連続再生する場合は「Loop」にチェックする
- 「▶ Play」をクリックする

### CLI から（`amazing_hand_cmd.py`）

**すべてのポーズとシーケンスを一覧表示：**
```bash
python amazing_hand_cmd.py --list
```

**ポーズを実行：**
```bash
python amazing_hand_cmd.py --pose open
```

**シーケンスを実行：**
```bash
python amazing_hand_cmd.py --sequence demo
```

**ループ付きで実行：**
```bash
python amazing_hand_cmd.py --sequence wave --loop
```

**別の設定を使用：**
```bash
python amazing_hand_cmd.py --pose open --config /path/to/hand_config.yaml
```

## 手動編集

`data/hand_config.yaml` を直接編集できます：

1. **YAML 構文に従う** - インデントは一貫させる（2 または 4 スペース）
2. 位置には**インライン配列形式**を使用する：
   ```yaml
   positions: [0, 0, 0, 0, 0, 0, 0, 0]
   ```
3. 特殊文字を保持するため**シーケンスのステップを引用する**：
   ```yaml
   steps:
     - "open:3,3,3,3,3,3,3,3|2.0s"
   ```
4. **名前を検証する** - 禁止文字を避ける
5. 変更を再読み込みするため**GUI を再起動する**
6. 大きな編集の前に**バックアップを取る**

## 検証

GUI と CLI は自動的に次を検証します：
- ポーズ/シーケンス名（禁止文字）
- 保存時の YAML 構文
- 位置配列の長さ（8 であること）

無効な名前は、禁止文字を示すエラーメッセージとともに拒否されます。

## ライセンス

Copyright 2026 AmazingHand Control Contributors

Apache License, Version 2.0 に基づいてライセンスされています
