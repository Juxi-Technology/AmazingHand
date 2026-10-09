[English](../en/CONFIG_FORMAT.md) | [Deutsch](../de/CONFIG_FORMAT.md) | [Español](../es/CONFIG_FORMAT.md) | [Français](../fr/CONFIG_FORMAT.md) | [Italiano](../it/CONFIG_FORMAT.md) | [日本語](../ja/CONFIG_FORMAT.md) | [한국어](../ko/CONFIG_FORMAT.md) | [Português (BR)](../pt-br/CONFIG_FORMAT.md) | [Português (PT)](../pt-pt/CONFIG_FORMAT.md) | [简体中文](../zh-hans/CONFIG_FORMAT.md) | 繁體中文

# 手部設定檔格式（YAML）

本文件說明 AmazingHand 使用的 YAML 設定檔。

| 檔案 | 用途 |
|------|---------|
| `data/hand_config.yaml` | 姿態與序列（由 GUI 和 CLI 建立/編輯） |
| `data/config.yaml` | 應用程式設定（序列埠、舵機限位、速度、路徑） |

---

## `data/config.yaml` – 應用程式設定

由 GUI 在啟動時載入。若檔案缺失，則使用內建預設值。
CLI 使用相同的預設值（可透過 `--port` / `--baudrate` 覆寫）。

### 完整結構

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

### 說明
- 所有鍵均為選用 —— 缺失的鍵會回退到上面所示的內建預設值。
- **不要**在此儲存姿態或序列；它們屬於 `data/hand_config.yaml`。
- 編輯此檔案後需重新啟動 GUI，變更才會生效。

---

## `data/hand_config.yaml` – 姿態與序列

由 GUI 和 CLI 建立與編輯。兩個工具共用。

### YAML 結構

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

## 姿態

每個姿態用 8 個舵機值定義一隻手完整的位置。

### 格式
```yaml
poses:
  pose_name:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
```

### 位置陣列
- **8 個值**，表示各舵機的角度位置
- **舵機對應**：
  - 舵機 1：食指位置（0=張開，110=握緊）
  - 舵機 2：食指左右偏移（-20=左，0=中位，+20=右）
  - 舵機 3：中指位置
  - 舵機 4：中指左右偏移
  - 舵機 5：無名指位置
  - 舵機 6：無名指左右偏移
  - 舵機 7：拇指位置
  - 舵機 8：拇指左右偏移

- **開合滑桿範圍**：每根手指 0-110°（0=張開，110=握緊）
- **左右滑桿範圍**：-40°（左）到 +40°（右）
- **儲存的舵機值**：由於 YAML 儲存的是合成值（base ± side），實際下發的舵機指令大致落在 -40° 到 150° 之間
- **注意**：偶數編號舵機（2、4、6、8）在硬體中角度是反的

### 命名規則
- 允許字母、數字、底線
- **禁用字元**：`: { } [ ] , & * # ? | - < > = ! % @ \` " '`
- 最多 50 個字元
- 區分大小寫

### 範例
```yaml
poses:
  open:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
  close:
    positions: [110, 0, 110, 0, 110, 0, 110, 0]
  peace:
    positions: [0, 0, 110, 0, 0, 0, 0, 0]
```

## 序列

序列定義多步動畫，可為各舵機個別設定速度與延時。

### 格式
```yaml
sequences:
  sequence_name:
    steps:
      - "pose_name:speed1,speed2,speed3,speed4,speed5,speed6,speed7,speed8|delay"
      - "SLEEP:duration"
```

### 步驟格式

**帶個別速度與延時的姿態：**
```
"pose_name:s1,s2,s3,s4,s5,s6,s7,s8|delay"
```
- `pose_name`：要執行的姿態名稱
- `s1-s8`：每個舵機的個別速度（1-6，6 最快）
- `delay`：運動完成後等待的時間（例如 `2.0s`）

**使用預設速度的姿態：**
```
"pose_name:3,3,3,3,3,3,3,3|2.0s"
```

**休眠/暫停：**
```
"SLEEP:1.5s"
```
- 暫停指定時長，不驅動舵機

### 速度值
- 範圍：1（最慢）到 6（最快）
- 控制舵機的運動速度
- 一個步驟中每個舵機可以有不同的速度

### 迴圈控制
- 迴圈設定**不**儲存在 YAML 中
- 透過 GUI 序列播放器中的核取方塊控制
- 無需編輯 YAML 即可靈活回放

### 範例
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

## 管理姿態與序列

### 透過 GUI（`amazing_hand_gui.py`）

**姿態：**
1. 用滑桿或鍵盤擺放手指位置
2. 在 "Name:" 欄位輸入名稱
3. 點擊 "➕ Add New" 儲存

**序列：**
1. 在 Sequence Player 區域點擊 "Manage" 按鈕
2. 在對話方塊中建構序列：
   - 選擇姿態與速度
   - 在步驟之間新增延時
   - 用 ↑/↓ 按鈕調整順序
3. 輸入序列名稱並點擊 "💾 Save"

**執行：**
- 從下拉式選單選擇序列
- 若需連續播放，勾選 "Loop"
- 點擊 "▶ Play"

### 透過 CLI（`amazing_hand_cmd.py`）

**列出所有姿態與序列：**
```bash
python amazing_hand_cmd.py --list
```

**執行一個姿態：**
```bash
python amazing_hand_cmd.py --pose open
```

**執行一個序列：**
```bash
python amazing_hand_cmd.py --sequence demo
```

**迴圈執行：**
```bash
python amazing_hand_cmd.py --sequence wave --loop
```

**使用其他設定：**
```bash
python amazing_hand_cmd.py --pose open --config /path/to/hand_config.yaml
```

## 手動編輯

你可以直接編輯 `data/hand_config.yaml`：

1. **遵循 YAML 語法** —— 縮排必須一致（2 或 4 個空格）
2. 位置**使用內嵌陣列格式**：
   ```yaml
   positions: [0, 0, 0, 0, 0, 0, 0, 0]
   ```
3. **為序列步驟加引號**以保留特殊字元：
   ```yaml
   steps:
     - "open:3,3,3,3,3,3,3,3|2.0s"
   ```
4. **驗證名稱** —— 避免禁用字元
5. **重新啟動 GUI** 以重新載入變更
6. 重大修改前**保留備份**

## 驗證

GUI 和 CLI 會自動驗證：
- 姿態/序列名稱（禁用字元）
- 儲存時的 YAML 語法
- 位置陣列長度（必須是 8）

非法名稱會被拒絕，並顯示含有禁用字元的錯誤訊息。

## 授權條款

Copyright 2026 AmazingHand Control Contributors

依 Apache License, Version 2.0 授權
