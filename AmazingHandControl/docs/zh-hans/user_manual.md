[English](../en/user_manual.md) | [Deutsch](../de/user_manual.md) | [Español](../es/user_manual.md) | [Français](../fr/user_manual.md) | [Italiano](../it/user_manual.md) | [日本語](../ja/user_manual.md) | [한국어](../ko/user_manual.md) | [Português (BR)](../pt-br/user_manual.md) | [Português (PT)](../pt-pt/user_manual.md) | 简体中文 | [繁體中文](../zh-hant/user_manual.md)

# AmazingHand 控制器 – 用户手册

> **版本：** 2026-03-22  
> **适用对象：** `amazing_hand_gui.py`（GUI）、`amazing_hand_cmd.py`（CLI）

---

## 一、简介

AmazingHand 控制器 GUI 为使用 Feetech SCS0009 舵机驱动的八舵机机械手提供实时监控与手动控制。界面划分为手指控制、全局管理、遥测可视化和活动日志等面板。本指南将带你了解安装、界面导航和常见工作流程。

> **提示：** 操作 GUI 时请保持本手册打开。应用内嵌的工具提示会在你悬停于控件上时复述相同的说明。

![AmazingHand hardware with controller connected](../en/screenshots/hand_overview.png)

---

## 二、快速上手清单

1. **安装依赖**（每个环境一次）：
   ```bash
   python -m pip install -r requirements.txt
   ```
2. **给硬件上电：** 将 5 V 电源接到舵机链，并插上 USB 串口适配器。
3. **启动 GUI：**
   ```bash
   python amazing_hand_gui.py
   ```
4. **连接到控制器：** 选择串口 **Port**（例如 `COM9`）并点击 **▶ Connect**。
5. **验证遥测：** 查看图表和反馈表中的实时更新。

---

## 三、界面概览

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

### 3.1 面板一览

| 面板 | 位置 | 用途 |
|-------|----------|---------|
| **Finger Controls** | 左侧，上部（3 指）+ 右下（拇指） | 每个手指对的独立滑块与速度选择器。包含 mimic 指示与逐手指状态 LED。 |
| **Right Control Stack** | 左侧，右下 | 连接设置、全局控制、姿态管理和序列播放器。 |
| **Telemetry Panel** | 右侧 | 带缩放/平移滑块的实时图表，以及可配置的反馈表。 |
| **Execution Log** | 底部 | 状态消息、警告和序列进度的消息流。 |

---

## 四、面板详解

### 4.1 手指控制面板（左列）

每个手指控件控制一对舵机（位置 + 左右偏移）：

- **模式切换：** 在 **Auto**（base + offset 滑块）与 **Raw**（直接舵机目标）之间切换。
- **状态 LED：** 灰色（空闲）、绿色（运动）、红色（可能阻塞，依据负载与目标比较）。
- **位置滑块：** 0–110°（张开到握紧）。鼠标滚轮以 1° 调整；拖动会快速跟随。
- **左右滑块：** ±40°，用于横向调整。拇指的左右滑块是**反向**的，使物理方向与手的解剖朝向一致 —— 向右拖动时，拇指按其硬件安装方向朝正方向移动。
- **速度选择器：** 1–6 下拉框，控制该手指对两个舵机的运动速度。
- **Mimic 复选框：** 在 Auto 模式下镜像来自源手指的开合运动，实现协同运动。

**手指模式：Auto 与 Raw**

- **Auto 模式**（默认）显示开合滑块、横向偏移滑块、速度下拉框和 center 按钮。GUI 使用存储在 `data/hand_config.yaml` 中的标定极值，将这两个滑块的值混合成舵机指令，因此该手指对能跟随自然的手指标定姿态，无需手动做舵机数学换算。Mimic 在此保持可用 —— 在多根手指上启用它，即可让它们与你当前正在调整的那根手指同步运动。
- **Raw 模式**用两个按舵机标注的竖直滑块替换 Auto 控件。在测试限位、验证标定或诊断连杆问题时，移动它们可直接控制底层舵机角度。center 按钮和 mimic 复选框被禁用，因为 Raw 绕过了自动混合逻辑；键盘快捷键仍然有效，上/下驱动舵机 1，左/右驱动舵机 2。Raw 使用最后选择的速度值，因此如果需要特定运动速率，请在切换前设置好速度。

**Auto 模式如何计算舵机目标**

- 开合滑块值被夹到 `limits.base_min/base_max`，然后归一化（`t = base / base_max`），在手指每一侧的 `auto_extremes` 张开与握紧姿态之间插值。
- 左右偏移滑块被夹到 `limits.side_min/side_max` 并转换为混合因子（`u`）。负偏移从中心姿态向 `left_open`/`left_closed` 线性插值；正偏移向右侧极值线性插值。
- 无横向偏移时，两个舵机直接接收 base 滑块值。最终舵机目标在下发前被夹到 `limits.servo_min/servo_max`，使运动保持在标定的安全范围内。

键盘快捷键是对滑块的补充（见 §5.2）。

![Finger control panel with per-finger sliders and status indicators](../en/screenshots/finger_control_frame.png)

### 4.2 全局控制堆栈（手指面板右侧）

1. **Connection：** 端口与波特率选择（连接时两个下拉框均被禁用）、连接/断开按钮。底部状态栏报告成功或错误。
2. **Global Controls：**
   - **Open All / Close All / Center All** —— 立即应用于每根手指。
   - **Global Speed 下拉框** —— 将逐手指速度选择器设为同一个值（1–6）。
3. **Pose Management：** 保存、加载、应用和删除 `data/hand_config.yaml` 中存储的姿态。
   - 布局：`Pose: [dropdown]  ✓ Apply  🗑 Delete  Name: [entry]  ➕ Add New`
   - **🗑 Delete** 永久移除所选姿态（会显示确认对话框）。
4. **Sequence Player：** 选择并执行多步动画，可选循环。通过 **🔧 Manage** 访问序列管理器对话框。

![Connection, global controls, pose management, and sequence player stack](../en/screenshots/control_frame.png)

### 4.3 遥测与反馈面板（右列）

- **控件行：**
  - 暂停/恢复图表更新。
  - 滚动窗口开关。
  - 指标选择（位置、负载、速度、温度、电压、运动标志）。
  - 模式切换（Multi-Servo 与 Scope），后者带舵机选择器。
  - 舵机可见性下拉框，带 "All/None/Clear" 辅助项。
  

![Display mode, metric selection, and scope controls](../en/screenshots/chart_mode_controls.png)

![Display menu for choosing telemetry metrics](../en/screenshots/chart_select_display_values.png)

![Servo visibility menu with quick actions](../en/screenshots/chart_servos_selection.png)

#### 图表模式

- **Multi-Servo**（默认）在图表上保留每条已启用的舵机曲线。用 **Servos** 下拉框快速开关分组，比较各手指的运动或负载。
- **Scope** 激活 **Scope Servo** 选择器，让你聚焦单个通道，同时仍使用相同的指标复选框。将此模式与舵机可见性菜单配合（例如先全部隐藏，再重新启用该 scope 舵机），即可获得不受其他曲线干扰的示波器式视图。
- 无论何种模式，遥测表始终呈现所有舵机，便于你将聚焦的图表与更全面的数据快照相互对照。
- **图表区：** 显示所选遥测的 Matplotlib 图。通过滑块缩放：
  - **Y Zoom / Pan：** 竖直方向的缩放与平移。
  - **Time Zoom / Pan：** 聚焦近期历史或更早的样本。
- **反馈表：** 可滚动的网格，汇总每个舵机的 Goal、Position、Speed、Load、Voltage、Temperature、Status 和 Moving 标志。

![Chart controls with zoom/pan sliders and telemetry traces](../en/screenshots/chart_frame.png)

![Feedback table showing live servo metrics](../en/screenshots/feedback_frame.png)

### 4.4 执行日志与状态栏

日志位于手指面板下方，按时间顺序记录操作。状态栏显示最新操作或警告。

![Execution log and current status bar](../en/screenshots/log_and_last_action_frame.png)

---

## 五、操作机械手

### 5.1 连接硬件

1. 给舵机上电并连接 USB 适配器。
2. 启动 GUI 并确认自动选中了正确的 **Port**（Windows 上为 `COM*`，Linux/macOS 上为 `/dev/tty*`）。
3. 点击 **▶ Connect**。成功后会改变按钮状态并更新状态栏。
4. 若连接失败，请检查线缆、电源和端口分配。

### 5.2 手动控制与快捷键

- 用按键 **1–4** 选择手指（1 = Ring，2 = Middle，3 = Pointer，4 = Thumb）。
- **方向键：** 上/下调整位置；左/右调整横向偏移。
- 按住 **Shift** 使步长乘以 5；**Ctrl** 乘以 10。
- **Q / E：** 将所选手指完全握紧 / 张开。
- **C：** 将横向偏移回正。
- 屏幕上的滑块实时反映键盘输入。

![Manual finger control panel with keyboard shortcut overlay](../en/screenshots/manual_finger_control_frame.png)

![Example of fully closing a finger using controls](../en/screenshots/close_finger.png)

![Example of lateral movement adjustment](../en/screenshots/move_finger.png)

### 5.3 设置速度

- 逐手指速度下拉框（1 = 慢，6 = 快）控制舵机速度。
- **Global Speed** 选择器同步所有手指的速度。
- 运动过程中在反馈表（`Speed` 行）观察速度变化。

### 5.4 应用与删除姿态

1. 用滑块或键盘快捷键摆放手指位置。
2. 在 **Pose Management** 中输入唯一名称并点击 **➕ Add New**。
3. 要应用，从下拉框选择该姿态并点击 **✓ Apply**。
4. 要删除，从下拉框选择该姿态并点击 **🗑 Delete**。确认对话框可防止误删。

> 姿态仅存储舵机位置；速度由 GUI 设置在运行时决定。

### 5.5 构建与执行序列

1. 在 Sequence Player 中点击 **🔧 Manage**。
2. 在对话框中：
   - 用 **Available Poses** 列表添加步骤（双击或按 **➕ Add**）。
   - 通过微调框调整逐手指速度，并设置可选的步骤延时。
   - 用 **⏱ Delay** 插入专门的休眠间隔。
   - 用 ↑/↓ 按钮调整步骤顺序。
   - 输入名称并点击 **💾 Save Sequence**。
   - 点击 **▶ Execute** 可在不保存的情况下测试。
3. 回到主窗口，选择该序列并按 **▶ Play**。启用 **Loop** 可连续播放。

> 序列定义位于 `data/hand_config.yaml` 的 `sequences` 键下。循环由运行端控制，而非 YAML。

![Sequence manager dialog with available poses and sequence builder](../en/screenshots/sequences_editor.png)

### 5.6 监控遥测

- 确保在 **Display** 菜单中勾选了所需指标。
- 用缩放/平移滑块聚焦感兴趣的区段。
- 悬停在图表元素上（Matplotlib 标准交互）即可查看数值。
- 反馈表异步更新；高亮的单元格表示最近发生的变化。
- 若图表变得杂乱，点击 **⌫ Clear** 重置已采集的数据。

---

## 六、命令行界面（`amazing_hand_cmd.py`）

CLI 让你无需启动 GUI，即可直接从终端应用姿态和播放序列。它读取同一个 `data/hand_config.yaml` 文件。

### 6.1 基本用法

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

### 6.2 选项

| 选项 | 默认值 | 说明 |
|--------|---------|-------------|
| `--pose NAME` | – | 应用指定名称的姿态后退出 |
| `--sequence NAME` | – | 播放指定名称的序列后退出 |
| `--list` | – | 列出所有姿态与序列 |
| `--loop` | off | 连续循环播放序列，直到 Ctrl+C |
| `--port PORT` | `/dev/ttyACM0` (Linux) / `COM9` (Win) | 串口覆盖 |
| `--baudrate N` | `1000000` | 波特率覆盖 |
| `--config PATH` | `data/hand_config.yaml` | 其他配置文件的路径 |

### 6.3 说明

- 连接时**启用**力矩，退出时**禁用**力矩，使舵机在脚本结束后放松。
- 每步的速度与延时行为与 GUI 序列播放器完全一致。
- `--loop` 标志只能与 `--sequence` 一起使用。

---

## 七、故障排查

| 现象 | 建议操作 |
|---------|-----------------| 
| **未列出串口** | 重新插拔 USB 适配器、安装驱动，或重启 GUI。 |
| **Connect 按钮变灰** | 已连接；请先点击 **⏹ Disconnect**。 |
| **调整窗口大小时界面卡顿** | 性能优化（防抖 resize、限流重绘）已将影响降到最低，但关闭不必要的窗口也有帮助。 |
| **序列未能驱动所有手指** | 检查每步速度，并确保每个姿态都包含全部 8 个舵机值。 |
| **阻塞指示持续存在** | 检查机械卡阻；当目标与实际位置差异显著且无运动时，会触发阻塞状态。 |

---

## 八、附录

### 8.1 文件结构

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

### 8.2 实用链接

- [AmazingHand（官方项目）](https://github.com/pollen-robotics/AmazingHand)
- [Feetech 舵机调试工具](https://github.com/Robot-Maker-SAS/FeetechServo/tree/main/feetech%20debug%20tool%20master/FD1.9.8.2)
- [舵机识别教程](https://www.robot-maker.com/forum/tutorials/article/168-brancher-et-controler-le-servomoteur-feetech-sts3032-360/)

---

## 九、修订历史

| 日期 | 作者 | 说明 |
|------|--------|-------|
| 2026-03-22 | Ingo | 新增 CLI（`amazing_hand_cmd.py`）章节；手册版本提升。 |
| 2026-03-21 | Ingo | 面板布局更新：Ring/Pointer 互换，拇指移到右侧，控制堆栈移到左侧。拇指左右滑块改为反向。在 Apply 与 Name 之间新增删除姿态按钮。连接时端口与波特率下拉框现在被锁定。键盘快捷键 1–4 现在映射为 Ring/Middle/Pointer/Thumb。 |
| 2025-11-25 | Ingo | 新增扩展截图库、图表模式说明，并更新了面板讲解。 |
| 2025-11-25 | Ingo | 初始手册，涵盖 UI 面板、工作流程和遥测用法。 |
