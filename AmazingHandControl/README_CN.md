[English](README.md) | 简体中文

# AmazingHand Python 控制工具

用 Python 编写的 GUI 与命令行工具,通过串口总线舵机驱动板控制 8 个 Feetech SCS0009 舵机,驱动 [Pollen Robotics 的 AmazingHand](https://github.com/pollen-robotics/AmazingHand) 灵巧手。

> **左右手都支持。** 启动时选择右手(舵机 ID 1-8)或左手(舵机 ID 11-18),`--hand` 可跳过提问。姿势库左右手共用,每只手在 `data/config.yaml` 里各自维护舵机映射、安装偏移和原始值目标。详见[左右手选择](#左右手选择)。

---

## 目录

- [项目结构](#项目结构)
- [环境要求](#环境要求)
- [安装](#安装)
- [标定](#标定)
- [运行 GUI](#运行-gui-amazing_hand_guipy)
- [运行 CLI](#运行-cli-amazing_hand_cmdpy)
- [配置文件](#配置文件)
- [手势与序列](#手势与序列)
- [测试](#测试)
- [舵机 ID 配置](#舵机-id-配置)

---

## 项目结构

```
amazing_hand_gui.py   – GUI 主程序
amazing_hand_cmd.py   – 命令行工具
hand_logic.py         – 共用业务逻辑(不依赖 UI)
pyproject.toml        – 包元数据、依赖、pytest 配置
data/
  config.yaml         – 应用设置(串口、限位、原始值目标)
  hand_config.yaml    – 已保存的手势与序列
docs/
  REQUIREMENTS.md       – 需求与验收标准
  user_manual.md        – 用户手册
  CONFIG_FORMAT.md      – 配置文件格式说明
  scs_servo_protocol.md – SCS0009 寄存器参考
  优化说明.md            – 相对原版的改动说明与原因
  CHANGES.md            – 同一份文档的英文版
tests/
  test_hand_logic.py      – hand_logic 单元测试(155 项)
  test_gui_utils.py       – GUI 工具函数单元测试(51 项)
  test_cmd.py             – CLI 单元测试(42 项)
  test_integration.py     – 集成测试(14 项)
  test_system.py          – 子进程系统测试(22 项)
  test_system_hardware.py – 硬件测试(33 项,需 --hardware)
  test_cmd_hardware.py    – CLI 硬件测试(21 项,需 --hardware)
```

## 环境要求

- Python 3.10 或更高版本(GUI 需要包含 Tkinter)
- 为 8 个舵机提供独立的 5V 外接电源
- 已安装好驱动的 USB 串口总线适配器

## 安装

推荐用 pip 安装(读取 `pyproject.toml`):

```bash
pip install -e .
```

或直接安装依赖:

```bash
pip install -r requirements.txt
```

开发与测试环境:

```bash
pip install -r requirements-dev.txt
```

---

## 标定

舵机的角度体系、手势预设和中位都取决于具体的机械手。这些参数全部集中在 `data/config.yaml`,**重新标定不需要改代码**。

### 左右手选择

两只手用的舵机和机械结构都不同,所以界面弹出之前先选:

```
  AmazingHand — which hand?
    1 = right hand  (servo IDs 1-8)
    2 = left hand   (servo IDs 11-18)
  Enter 1 or 2 [1]:
  LEFT hand — servo IDs 11-18
    Ring (11, 12)  Middle (13, 14)  Pointer (15, 16)  Thumb (17, 18)
    middle position raw: [571, 451, 571, 451, 571, 451, 571, 451]
```

跳过提问:

```bash
python amazing_hand_gui.py --hand left
python amazing_hand_cmd.py --pose victory --hand left
```

不加 `--hand` 时用 `data/config.yaml` 里的 `hand:` 值。

**为什么一只手不只是换组 ID。** 除了舵机编号(右手 1-8、左手 11-18,且左手的手指编号是镜像的 —— 无名指在前),左手还有两处机械差异,程序都会自动处理:

| | 右手 | 左手 |
|---|---|---|
| 舵机 ID | 1-8 | 11-18 |
| 手指 → ID | 食指 `1,2` / 中指 `3,4` / 无名指 `5,6` / 拇指 `7,8` | 无名指 `11,12` / 中指 `13,14` / 食指 `15,16` / 拇指 `17,18` |
| 厂商 `MiddlePos` | `[451, 571, …]` | `[571, 451, …]` |
| 安装偏移 | 0° | **−35.16°**(`hands.left.angle_offset`) |
| 同指双舵机 | `(a, b)` | **`(b, a)`**(`hands.left.mirror_pose`) |

上述后两项漏掉任何一个手势都会走形:安装偏移会让每根手指偏 35°,少了同指互换则张开方向整个反过来(V 字手势两指并拢、该并拢的三指反而张开)。

`data/hand_config.yaml` 是**左右手共用**的,存储的永远是右手序;左手在读取时转换、保存时换回。

**标定一只新手。** 以 `hands.left` 里的值为模板,然后按这个顺序核验:

1. 按 **Middle position**,看 `Current (0-1023)` 那行是否读到预期的原始值
2. 按 **Open All** / **Close All** —— 行程应该到机械限位且不堵转
3. 试一个张开手势(`victory` 张成 V 字、`greeting` 三指并拢)

哪一项不对,该调哪个参数:

| 现象 | 改哪里 |
|---|---|
| Middle position 读数不对 | `hands.<名称>.raw_positions.middle` |
| 张开方向反了 | `hands.<名称>.mirror_pose` |
| 行程不够或过头 | `hands.<名称>.raw_positions.open` / `close` |

### 角度体系

GUI 和 CLI 都使用**角度值**,由 rustypot 驱动换算成舵机内部的原始值:

```
raw = 1024 × angle / 300° + 511        (0.29297°/step,原始值范围 0–1023)
```

| 角度 | 含义 |
|---|---|
| **−35°** | 完全张开(伸直) |
| **0°** | 中位,手指自然微屈 |
| **+75°** | 完全握紧(拳) |

偶数 ID 舵机相对奇数 ID **取反**,所以一个姿势值就能让同一根手指的两个舵机朝相反方向运动。这一点由程序自动处理,你不需要手动换算。

### 限位

```yaml
limits:
  servo_min: -75      # 任何舵机指令的绝对行程上下限
  servo_max: 75
  base_min: -75       # 开合滑块范围
  base_max: 75
  side_min: -35       # 左右滑块范围
  side_max: 35
```

`side_min`/`side_max` 控制**左右张开**。由于程序做了归一化(`u = |side_offset| / |side_min|`),**只改这个范围不会改变实际张开幅度**,只是把滑块刻度压缩了。要真正改变手指张开的角度,必须同时修改 `auto_extremes`。

### 原始值目标

三个全局位置按钮把舵机驱动到**精确的原始值**,不经过角度模型:

```yaml
raw_positions:              # 下标 0 -> 舵机 ID 1 …… 下标 7 -> 舵机 ID 8
  open:   [260, 760, 260, 760, 260, 760, 260, 760]
  close:  [760, 260, 760, 260, 760, 260, 760, 260]
  middle: [451, 571, 451, 571, 451, 571, 451, 571]
```

- `open` / `close` —— 机械行程两端。用厂商的 Feetech 调试工具单独驱动舵机测出来。
- `middle` —— **标定后的机械中位**(即厂商 Arduino 演示程序里的 `MiddlePos`)。注意它**不是** open 和 close 的中点,而是偏离 raw 511 约 **±60 raw(±17.6°)**。

> 这些是**每只手各自的标定值**。厂商原话是 *"replace values by your calibration results"*。

**如何校验:** Servo Feedback 面板有一行 `Current (0-1023)`,实时显示原始位置。按下 **Middle position** 按钮后,这一行应该读到 `451, 571, 451, 571, …`。

### 控件范围速查

| 控件 | 范围 |
|---|---|
| 开合滑块(纵向) | −75 … +75 |
| 左右滑块(横向) | −35 … +35 |
| 速度 | 1(慢) … 6(快) |

速度值会由驱动当作 rad/s 传给舵机,所以 1–6 大致对应 **57–344 °/s**。带载后实际速度约为该值的 **70%** —— 排序列延时时要把这一点算进去。

---

## 运行 GUI (`amazing_hand_gui.py`)

pip 安装后可直接调用:

```bash
amazing-hand-gui
amazing-hand-gui --port /dev/ttyUSB0
```

或直接运行:

```bash
python amazing_hand_gui.py
python amazing_hand_gui.py --port /dev/ttyUSB0
```

端口下拉框会列出本机**实际存在的**串口(优先用 pyserial,没有则读 Windows 注册表),所以编号靠后的适配器也能显示出来。下拉框可以直接手输端口号。配置里的默认端口没插时,GUI 会自动从第一个真实端口启动;想固定端口就显式传 `--port`。

### 功能

- 逐指滑块控制开合与左右,支持 **Auto**(开合 + 左右)和 **Raw**(直接控制两个舵机角度)两种模式
- 逐指 Open / Close / Center 快捷按钮
- 逐指速度选择(1–6),另有全局速度同步下拉框
- 键盘快捷键,便于精确微调
- **全局位置按钮**: Open All、Close All、Center All、Middle position
- 基于 `data/hand_config.yaml` 的手势与序列管理
- 可直接在界面上删除已保存的手势(🗑 Delete 按钮)
- 实时舵机遥测曲线(位置、负载、温度、电压)
- Servo Feedback 表格,含实时**原始位置**(0–1023),可用于标定校验

### 键盘操作

- **1-4**: 选择手指(Ring 无名指、Middle 中指、Pointer 食指、Thumb 拇指)
- **方向键**: 移动选中的手指
  - 上/下: 握紧 / 张开
  - 左/右: 左右移动
- **修饰键**:
  - 无: 每次 1°(精调)
  - Shift: 每次 5°(常规)
  - Ctrl: 每次 10°(快速)
- **快捷动作**:
  - Q: 选中的手指完全握紧
  - E: 选中的手指完全张开
  - C: 左右位置回正

### 全局按钮

| 按钮 | 开合 | 左右 |
|---|---|---|
| ✋ **Open All** | 所有手指到原始值 `open` | 回正 |
| ✊ **Close All** | 所有手指到原始值 `close` | 回正 |
| ⊙ **Center All** | **保持不变** | 回正 |
| ⊙ **Middle position** | 所有手指到原始值 `middle` | — |

**Global Speed** 下拉框(1–6)会立刻把选定速度应用到所有手指控件,并同步各指的滑块显示。

三个原始值按钮(`Open All`、`Close All`、`Middle position`)绕过了角度模型,因此**执行后滑块显示的是最接近的可表示值,而不是精确值**。之后再碰滑块,手会偏离原始目标最多约 0.3° —— 这是为了精确命中标定位置的刻意取舍。

> 已知问题: `Center All` **不会**跳过处于 **Raw** 模式的手指,会覆盖你手动设置的原始角度。单指的 `⊙ Center` 按钮则不会。

---

## 运行 CLI (`amazing_hand_cmd.py`)

独立的命令行工具,无需启动 GUI 即可应用手势和播放序列。它读取与 GUI 相同的 `data/hand_config.yaml`,并**逐字发送**存储的姿势值 —— 与 GUI 发出的完全一致。

### Linux: 串口权限

USB 串口适配器通常表现为 `/dev/ttyACM0`(Waveshare / CDC-ACM)或 `/dev/ttyUSB0`(FTDI / CH340)。

查找方式:
```bash
ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
# 或者
dmesg | grep -E 'ttyACM|ttyUSB' | tail -5
```

如果报 **Permission denied**,把当前用户加入 `dialout` 组后重新登录:
```bash
sudo usermod -aG dialout $USER
```

### pip 安装后

```bash
amazing-hand-cmd --list
amazing-hand-cmd --pose open
amazing-hand-cmd --sequence demo --loop
amazing-hand-cmd --pose open --speed 6
# 需要时覆盖串口:
amazing-hand-cmd --pose open --port /dev/ttyUSB0
```

### 直接运行

```bash
python amazing_hand_cmd.py --list
python amazing_hand_cmd.py --pose open
python amazing_hand_cmd.py --pose close --speed 6
python amazing_hand_cmd.py --sequence demo
python amazing_hand_cmd.py --sequence wave --loop
python amazing_hand_cmd.py --port /dev/ttyUSB0 --pose open
python amazing_hand_cmd.py --list --config /path/to/hand_config.yaml
```

### 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--pose NAME` | – | 应用指定名称的手势 |
| `--sequence NAME` | – | 播放指定名称的序列 |
| `--list` | – | 列出所有手势与序列 |
| `--loop` | 关 | 循环播放序列,直到 Ctrl+C |
| `--speed N` | `3` | 舵机速度 1(慢)… 6(快) |
| `--port PORT` | Linux `/dev/ttyACM0` / Windows `COM9` | 串口 |
| `--baudrate N` | `1000000` | 波特率 |
| `--config PATH` | `data/hand_config.yaml` | 指定其他配置文件 |
| `--hand {right,left}` | `config.yaml` 的 `hand` | 指定使用哪只手(右手 1-8,左手 11-18) |

脚本退出时(包括 Ctrl+C)会自动关闭所有舵机的力矩。

> CLI 没有对应 `data/config.yaml` 的 `--config` 参数,该文件始终从项目目录加载。

---

## 配置文件

### `data/config.yaml`

| 段落 | 用途 |
|---|---|
| `serial` | 各平台默认串口、波特率、可选波特率列表 |
| `servos` | 每根手指对应的舵机 ID |
| `limits` | 舵机与两个滑块的角度范围 |
| `speeds` | 1–6 速度刻度的默认值/最小/最大值 |
| `auto_extremes` | 左右滑块到极限时的舵机位置 |
| `raw_positions` | 全局位置按钮的精确原始值目标 |
| `paths` | 手势/序列文件的位置 |

### 舵机与手指的对应关系

| 手指 | 舵机 ID | 姿势数组下标 |
|---|---|---|
| Pointer 食指 | 1, 2 | 4, 5 |
| Middle 中指 | 3, 4 | 2, 3 |
| Ring 无名指 | 5, 6 | 0, 1 |
| Thumb 拇指 | 7, 8 | 6, 7 |

**姿势数组的顺序是 无名指、中指、食指、拇指,不是按舵机 ID 排列。** 手工编辑 `hand_config.yaml` 时这是最容易搞错的一点。

> `amazing_hand_cmd.py` 顶部的注释写着 "index 0→servo1 … 7→servo8",**那个注释是错的**,上表才是代码的真实行为。

---

## 手势与序列

所有手势和序列都保存在 `data/hand_config.yaml`。文件不存在时 GUI 会自动创建。

### 保存手势

1. 用滑块或键盘把手摆到目标姿势
2. 在 "Name:" 输入框填入名称
3. 点击 Pose Management 区域的 "➕ Add New"

速度只影响滑块的移动快慢;保存的手势只记录 8 个舵机位置。

### 加载 / 删除手势

- 从下拉框选择后点击 **✓ Apply** 让手移动到该姿势
- 点击 Apply 右侧的 **🗑 Delete**,确认后永久删除

### 序列管理

1. 在 Sequence Player 中点击 "🔧 Manage" 打开序列管理器
2. **Saved Sequences**(左栏)
   - 查看、执行、编辑或删除已有序列
   - 双击或点击 "▶ Execute" 执行一次
3. **Sequence Builder**(右栏)
   - 双击 "Available Poses" 中的手势即可加入为一步
   - 可为每一步单独设置 8 个舵机的速度和延时;步骤以 `"pose:s1,s2,...,s8|delay"` 形式保存
   - 用 ↑/↓ 调整顺序,或用 "⏱ Delay" 按钮插入独立暂停
   - 填好名称后点击 "💾 Save Sequence" 保存;点 "▶ Execute" 可先试跑不保存
4. 回到主窗口,需要连续播放时勾选 Sequence Player 里的 **Loop**

### 步骤格式

```
pose_name:speed1,speed2,...,speed8|delay
```

- `speed1..speed8` —— 按姿势顺序排列的 8 个舵机速度(1–6)
- `delay` —— 距离下一步的等待时间,如 `0.6s`。**可省略**;省略时 GUI 会退回到固定的自动等待
- 独立暂停写作 `SLEEP:1.0s`(没有逗号分隔的速度列表)

**延时的选取。** 驱动本身能读到达舵机是否停止,但序列播放用的是固定延时。大致按 `行程角度 / (速度 × 57.3 × 0.7)` 秒来估算,并留出余量 —— 在带载的手上,超过约 130° 的动作在速度 3 下需要 1.0 秒以上。

### YAML 格式示例

```yaml
poses:
  open:
    positions: [-35, -35, -35, -35, -35, -35, -35, -35]
  close:
    positions: [75, 75, 75, 75, 75, 75, 75, 75]
  ring_close:                 # 无名指握紧,其余张开
    positions: [75, 75, -35, -35, -35, -35, -35, -35]

sequences:
  demo:
    steps:
      - "open:3,3,3,3,3,3,3,3|2.0s"
      - "close:6,6,6,6,6,6,6,6|2.0s"
      - "ok:3,3,3,3,3,3,3,3|1.0s"
      - "victory:3,3,3,3,3,3,3,3|1.0s"
      - "greeting:3,3,3,3,3,3,3,3|1.5s"
      - "close:6,6,6,6,6,6,6,6|2.0s"
  wave:
    steps:
      - "open:6,6,6,6,6,6,6,6|0.8s"
      - "wave_r:5,5,5,5,5,5,5,5|0.6s"
      - "wave_l:5,5,5,5,5,5,5,5|0.6s"
      - "open:5,5,5,5,5,5,5,5|0.8s"
  finger_roll:
    steps:
      - "open:6,6,6,6,6,6,6,6|0.5s"
      - "ring_close:5,5,5,5,5,5,5,5|0.6s"
      - "open:5,5,5,5,5,5,5,5|0.5s"
      - "middle_close:5,5,5,5,5,5,5,5|0.6s"
      - "open:5,5,5,5,5,5,5,5|0.5s"
```

循环播放由运行时控制(GUI 的复选框),不再写入 YAML。

---

## 测试

项目包含 284 项单元/集成/系统测试,以及 54 项硬件测试。

### 运行全部测试(无需硬件)

```bash
pytest
```

### 运行 GUI + CLI 硬件测试(需要连接舵机)

```bash
pytest tests/test_system_hardware.py --hardware --port /dev/ttyACM0
pytest tests/test_cmd_hardware.py --hardware --port /dev/ttyACM0
# 或两个一起:
pytest tests/test_system_hardware.py tests/test_cmd_hardware.py --hardware
```

`test_system_hardware.py` 验证连接、手势应用、遥测读取、单指张合/挥手、速度控制、序列执行与运动检测。

`test_cmd_hardware.py` 端到端验证 CLI 层:姿势位置、速度参数、序列步骤、`wait_for_motion`、`--list` 输出,以及退出时关闭力矩。

完整的验收标准见 `docs/REQUIREMENTS.md`。

> 注意:非硬件测试断言的是 `hand_logic.py` 里的**兜底默认值**,那套默认值仍是原版的 −40…110 尺度。运行时 `data/config.yaml` 会覆盖它们,所以无论你怎么标定,测试都能通过 —— 但也意味着**测试并不会校验你当前的标定参数**。

---

## 舵机 ID 配置

用 Feetech 官方软件配合串口总线驱动配置舵机 ID 的教程:
<https://www.robot-maker.com/forum/tutorials/article/168-brancher-et-controler-le-servomoteur-feetech-sts3032-360/>

Feetech 软件下载:
<https://github.com/Robot-Maker-SAS/FeetechServo>

---

## 致谢

原始项目:[Betatester777](https://github.com/Betatester777/AmazingHandControl)
硬件与参考固件:[Pollen Robotics](https://github.com/pollen-robotics/AmazingHand)
