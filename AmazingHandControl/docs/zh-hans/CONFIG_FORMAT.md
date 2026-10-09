[English](../en/CONFIG_FORMAT.md) | [Deutsch](../de/CONFIG_FORMAT.md) | [Español](../es/CONFIG_FORMAT.md) | [Français](../fr/CONFIG_FORMAT.md) | [Italiano](../it/CONFIG_FORMAT.md) | [日本語](../ja/CONFIG_FORMAT.md) | [한국어](../ko/CONFIG_FORMAT.md) | [Português (BR)](../pt-br/CONFIG_FORMAT.md) | [Português (PT)](../pt-pt/CONFIG_FORMAT.md) | 简体中文 | [繁體中文](../zh-hant/CONFIG_FORMAT.md)

# 手部配置文件格式（YAML）

本文档说明 AmazingHand 使用的 YAML 配置文件。

| 文件 | 用途 |
|------|---------|
| `data/hand_config.yaml` | 姿态与序列（由 GUI 和 CLI 创建/编辑） |
| `data/config.yaml` | 应用设置（串口、舵机限位、速度、路径） |

---

## `data/config.yaml` – 应用设置

由 GUI 在启动时加载。若文件缺失，则使用内置默认值。
CLI 使用相同的默认值（可通过 `--port` / `--baudrate` 覆盖）。

### 完整结构

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

### 说明
- 所有键均为可选 —— 缺失的键会回落到上面所示的内置默认值。
- **不要**在此存储姿态或序列；它们属于 `data/hand_config.yaml`。
- 编辑此文件后需重启 GUI 更改才会生效。

---

## `data/hand_config.yaml` – 姿态与序列

由 GUI 和 CLI 创建与编辑。两个工具共用。

### YAML 结构

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

## 姿态

每个姿态用 8 个舵机值定义一只手完整的位置。

### 格式
```yaml
poses:
  pose_name:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
```

### 位置数组
- **8 个值**，表示各舵机的角度位置
- **舵机映射**：
  - 舵机 1：食指位置（0=张开，110=握紧）
  - 舵机 2：食指左右偏移（-20=左，0=中位，+20=右）
  - 舵机 3：中指位置
  - 舵机 4：中指左右偏移
  - 舵机 5：无名指位置
  - 舵机 6：无名指左右偏移
  - 舵机 7：拇指位置
  - 舵机 8：拇指左右偏移

- **开合滑块范围**：每根手指 0-110°（0=张开，110=握紧）
- **左右滑块范围**：-40°（左）到 +40°（右）
- **存储的舵机值**：由于 YAML 存储的是合成值（base ± side），实际下发的舵机指令大致落在 -40° 到 150° 之间
- **注意**：偶数编号舵机（2、4、6、8）在硬件中角度是反的

### 命名规则
- 允许字母、数字、下划线
- **禁用字符**：`: { } [ ] , & * # ? | - < > = ! % @ \` " '`
- 最多 50 个字符
- 区分大小写

### 示例
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

序列定义多步动画，可为各舵机单独设置速度与延时。

### 格式
```yaml
sequences:
  sequence_name:
    steps:
      - "pose_name:speed1,speed2,speed3,speed4,speed5,speed6,speed7,speed8|delay"
      - "SLEEP:duration"
```

### 步骤格式

**带单独速度与延时的姿态：**
```
"pose_name:s1,s2,s3,s4,s5,s6,s7,s8|delay"
```
- `pose_name`：要执行的姿态名称
- `s1-s8`：每个舵机的单独速度（1-6，6 最快）
- `delay`：运动完成后等待的时间（例如 `2.0s`）

**使用默认速度的姿态：**
```
"pose_name:3,3,3,3,3,3,3,3|2.0s"
```

**休眠/暂停：**
```
"SLEEP:1.5s"
```
- 暂停指定时长，不驱动舵机

### 速度值
- 范围：1（最慢）到 6（最快）
- 控制舵机的运动速度
- 一个步骤中每个舵机可以有不同的速度

### 循环控制
- 循环设置**不**存储在 YAML 中
- 通过 GUI 序列播放器中的复选框控制
- 无需编辑 YAML 即可灵活回放

### 示例
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

## 管理姿态与序列

### 通过 GUI（`amazing_hand_gui.py`）

**姿态：**
1. 用滑块或键盘摆放手指位置
2. 在 "Name:" 字段输入名称
3. 点击 "➕ Add New" 保存

**序列：**
1. 在 Sequence Player 区域点击 "Manage" 按钮
2. 在对话框中构建序列：
   - 选择姿态与速度
   - 在步骤之间添加延时
   - 用 ↑/↓ 按钮调整顺序
3. 输入序列名称并点击 "💾 Save"

**执行：**
- 从下拉框选择序列
- 若需连续播放，勾选 "Loop"
- 点击 "▶ Play"

### 通过 CLI（`amazing_hand_cmd.py`）

**列出所有姿态与序列：**
```bash
python amazing_hand_cmd.py --list
```

**执行一个姿态：**
```bash
python amazing_hand_cmd.py --pose open
```

**执行一个序列：**
```bash
python amazing_hand_cmd.py --sequence demo
```

**循环执行：**
```bash
python amazing_hand_cmd.py --sequence wave --loop
```

**使用其他配置：**
```bash
python amazing_hand_cmd.py --pose open --config /path/to/hand_config.yaml
```

## 手动编辑

你可以直接编辑 `data/hand_config.yaml`：

1. **遵循 YAML 语法** —— 缩进必须一致（2 或 4 个空格）
2. 位置**使用内联数组格式**：
   ```yaml
   positions: [0, 0, 0, 0, 0, 0, 0, 0]
   ```
3. **给序列步骤加引号**以保留特殊字符：
   ```yaml
   steps:
     - "open:3,3,3,3,3,3,3,3|2.0s"
   ```
4. **校验名称** —— 避免禁用字符
5. **重启 GUI** 以重新加载更改
6. 重大修改前**保留备份**

## 校验

GUI 和 CLI 会自动校验：
- 姿态/序列名称（禁用字符）
- 保存时的 YAML 语法
- 位置数组长度（必须是 8）

非法名称会被拒绝，并给出显示禁用字符的错误信息。

## 许可证

Copyright 2026 AmazingHand Control Contributors

依据 Apache License, Version 2.0 授权
