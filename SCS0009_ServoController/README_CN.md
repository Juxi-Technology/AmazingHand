[English](README.md) | 简体中文

<div align="center">

# SCS0009 舵机调试工具

**专为 Feetech SCS0009 舵机（电位器反馈）设计的 FTServo 调试工具**

> ⚠️ **兼容性说明:本系统目前仅支持 Feetech SCS0009 舵机（SCS 系列，电位器位置反馈，10 位分辨率 0-1023）**。寄存器表、xdat 参数格式、波特率表均针对飞特 SCS0009 设计。

> 📜 **版权说明:本工具由 JUXI_Technology 开发并维护**,采用 MIT 许可发布(见 [LICENSE](LICENSE))。FT 调试器、xdat 参数备份/恢复、跨平台支持等功能均为自主实现。

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Ubuntu%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![GUI](https://img.shields.io/badge/GUI-PySide6-orange)

[功能特性](#-功能特性) · [界面介绍](#-界面介绍) · [快速开始](#-快速开始) · [使用步骤](#-使用步骤) · [注意事项](#-注意事项) · [故障排除](#-故障排除)

</div>

---

## ✨ 功能特性

| 特性 | 说明 |
| ---- | ---- |
| 自动端口检测 | 智能识别 USB 串口，自动过滤虚拟设备 |
| 跨平台支持 | Windows / Ubuntu / macOS 全平台兼容 |
| 中英文切换 | 界面内一键切换中 / 英文，选择自动记忆 |
| 串口连接 | 手动/自动选择串口，8 档波特率（38400~1M） |
| 舵机扫描 | 自动检测在线舵机（ID 1–254），实时显示 |
| 参数读取 | 读取全部 44 个寄存器（EEPROM + SRAM） |
| 参数表 | 5 列展示（地址/寄存器/值/存储区域/读写），点选联动 |
| 位置控制 | 目标位置/速度控制，移动完成提示关闭力矩 |
| 波特率修改 | 修改舵机波特率，失败自动回滚 |
| 恢复出厂 | 一键恢复出厂默认设置 |
| xdat 参数 | 保存当前舵机 EEPROM 参数 / 打开备份恢复 |

---

## 📚 详细教程

### 中文

| 系统 | 教程 |
|------|------|
| Windows | [Windows 使用教程](docs/zh-hans/Windows.md) |
| Linux | [Linux 使用教程](docs/zh-hans/Linux.md) |
| macOS | [macOS 使用教程](docs/zh-hans/macOS.md) |

### English

| OS | Guide |
|----|-------|
| Windows | [Windows Guide](docs/en/Windows.md) |
| Linux | [Linux Guide](docs/en/Linux.md) |
| macOS | [macOS Guide](docs/en/macOS.md) |

---

## 🖥️ 界面介绍

主程序为单面板布局（FT 调试器）:

```
┌─────────────────────────────────────────────────────────────┐
│  SCS0009 舵机调试工具                     [EN / English]     │  ← 顶栏
├─────────────────────────────────────────────────────────────┤
│  🔌 串口连接   [端口▾][🔄][波特率▾][连接] [🔴未连接]         │
│  🎯 舵机      [🔍扫描][舵机▾][读取参数][读取状态]            │
│               ┌ 扫描到的舵机列表 ┐                           │
│  📋 参数表    地址|寄存器|值|存储区域|读写  (44 个寄存器)      │
│  🎯 位置控制  目标位置|速度|移动|力矩开|力矩关 | 状态         │
│  🔧 波特率/恢复出厂  新波特率|修改波特率|恢复出厂            │
│  📁 xdat 参数(仅保存EEPROM) 保存当前舵机|打开xdat|恢复参数    │
│  📜 日志                                                      │
└─────────────────────────────────────────────────────────────┘
```

- **顶栏**：应用标题、语言切换按钮。
- **🔌 串口连接**：选择端口、波特率、连接/断开。
- **🎯 舵机**：扫描、选择舵机、读取参数/状态。
- **📋 参数表**：44 个寄存器 5 列展示，点选自动联动写入地址。
- **🎯 位置控制**：目标位置/速度，移动完成后状态栏提示关闭力矩。
- **🔧 波特率/恢复出厂**：修改波特率（失败回滚）、恢复出厂。
- **📁 xdat 参数（仅保存 EEPROM）**：保存当前舵机参数、打开备份、恢复。

---

## 🚀 快速开始

> 完整分系统教程见 [📚 详细教程](#-详细教程)。以下为各系统要点。

### Windows

1. 安装 [Python 3.10+](https://www.python.org/downloads/)(勾选 **Add to PATH**)
2. 创建虚拟环境并安装依赖:

```bash
cd SCS0009_ServoController
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> ⚠️ **虚拟环境只需创建一次**。重复执行 `python -m venv .venv` 会重置/覆盖原环境（清空已安装的依赖）。之后每次只需 `activate` 激活即可。

3. 检查环境并启动:

```bash
python setup.py
python -m src.gui.factory_calibration_tool
```

4. 设备管理器确认串口号(如 `COM3`),顶栏选择。手动指定端口:

```bash
python -m src.gui.factory_calibration_tool --port COM3
```

### Linux (Ubuntu / Debian)

1. 安装中文字体与依赖:

```bash
sudo apt install python3-venv fonts-noto-cjk fonts-noto-color-emoji
```

2. **⚠️ 添加串口权限(dialout 组)**【必需】:

```bash
sudo usermod -a -G dialout $USER
# 注销并重新登录后生效
```

3. 创建虚拟环境、安装依赖、启动:

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup.py
python -m src.gui.factory_calibration_tool
```

> ⚠️ **虚拟环境只需创建一次**。重复 `python3 -m venv .venv` 会覆盖原环境（清空已装依赖）。之后只需 `source .venv/bin/activate`。

4. 串口设备为 `/dev/ttyUSB0` / `/dev/ttyACM0`。手动指定:

```bash
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

### macOS

1. 用 Homebrew 安装 Python:

```bash
brew install python
```

2. 创建虚拟环境、安装依赖、启动:

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup.py
python -m src.gui.factory_calibration_tool
```

> ⚠️ **虚拟环境只需创建一次**。重复 `python3 -m venv .venv` 会覆盖原环境（清空已装依赖）。之后只需 `source .venv/bin/activate`。

3. **⚠️ 串口命名**:macOS 用 `/dev/cu.usbserial-*`(**推荐,非阻塞**)而非 `/dev/tty.*`。查看:

```bash
ls /dev/cu.*
```

手动指定:

```bash
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

### 命令行

```bash
# 列出可用串口
python -m src.gui.factory_calibration_tool --list-ports

# 指定端口启动
python -m src.gui.factory_calibration_tool --port <串口>
```

---

## 📖 使用步骤

### 1. 连接与识别舵机

1. 通过 USB 转串口适配器连接机械臂控制板，给舵机供电。
2. 打开 GUI，在"🔌 串口连接"区选择端口（或点击 `🔄` 刷新），设置波特率（默认 1M）。
3. 点击 **连接**，状态显示 `🟢 已连接`。

> 若提示串口占用，请确认没有其他程序（串口监视器、上一个未退出的工具）占用该端口。

### 2. 扫描舵机

1. 点击 **🔍 扫描舵机**，检测 ID 1–254 范围内的在线舵机。
2. 扫描结果实时显示在舵机列表中（带型号）。
3. 在舵机列表点击某一行，自动填充到"舵机"下拉框。

### 3. 读取参数

1. 选中舵机后，点击 **📖 读取参数**，逐个读取全部 44 个寄存器。
2. 参数表 5 列展示（地址/寄存器/值/存储区域/读写），EPROM/SRAM/DEFAULT 颜色区分。
3. 日志区显示每个寄存器的读取结果和失败原因。

### 4. 修改参数 / 写入

1. 在参数表点击要修改的寄存器行 → 自动联动"写入地址"、"长度"、"值"。
2. 在"值"输入框修改新值，点击 **✏️ 写入**。
3. 程序执行：解锁 EEPROM → 写入 → 重新锁定。
4. 写入结果弹窗：成功显示"✅ 已成功写入"，失败显示"❌ 写入失败"（含原因）。

### 5. 修改舵机 ID

1. 在参数表找到"舵机 ID"（地址 0x05）行，点击选中。
2. 修改"值"为新 ID，点击 **✏️ 写入**。
3. 程序执行：解锁 → 写入地址 5 → 重新锁定。

> ⚠️ 修改 ID 前务必确保总线上只有这一只舵机，避免 ID 冲突。

### 6. 位置控制

1. 在"🎯 位置控制"区,**拖动滑动条**调整目标位置(0–1023,电位器 10 位分辨率),数值框同步显示;也可直接在数值框输入。
2. 点击 **▶ 移动**，舵机开始移动，状态栏显示"移动中..."。
3. 移动完成后显示"✅ 已移动完成，请关闭力矩"，点击 **⏹ 力矩关**。

### 7. 修改波特率 / 恢复出厂设置

- **修改波特率**：在"🔧 波特率/恢复出厂"区选择新波特率（38400 – 1000000 bps）后点击 **🔧 修改波特率**。写入后自动切换串口波特率并 ping 验证，失败自动回滚。
- **恢复出厂设置**：点击 **🔄 恢复出厂**，舵机恢复为出厂默认（ID=1，波特率=1000000），之后需重新扫描。

### 8. xdat 参数备份与恢复

在"📁 xdat 参数（仅保存 EEPROM）"区：

1. **💾 保存当前舵机**：把当前选中舵机的 EEPROM 参数保存为 xdat 文件（备份）。
2. 随意修改舵机参数后，如想恢复：
3. **📂 打开 xdat**：加载备份文件。
4. **📤 恢复参数到舵机**：把备份写回当前舵机 EEPROM。

---

## ⚠️ 注意事项

1. **安全第一**：写入参数会持久化到 EEPROM。写入前确认供电稳定、机械臂不会碰撞到人或物。
2. **供电**：SoARM 101 标准版建议 DC 5V 5A，Pro 版建议 DC 12V 5A。供电不足会导致舵机丢步或通信失败。
3. **串口独占**：Windows 下串口被程序独占，同一端口不能同时被两个程序占用。请勿在别的程序（串口监视器）打开同一端口时使用本工具。
4. **Linux 串口权限**：访问 `/dev/ttyUSB*` / `/dev/ttyACM*` 需将用户加入 `dialout` 组（见 [Linux 教程](docs/zh-hans/Linux.md)）。
5. **macOS 串口命名**：请使用 `/dev/cu.*`（非阻塞）而非 `/dev/tty.*`（阻塞，可能卡住），见 [macOS 教程](docs/zh-hans/macOS.md)。
6. **热插拔**：拔掉 USB 后程序会尝试自动重连；重新插回后点击 `🔄` 刷新端口列表。
7. **过温 / 过压保护**：程序会监控电压与温度（温度 > 60°C 告警）。若舵机连续高温，请停机散热。
8. **参数写入不可逆**：EEPROM 写入后原值被覆盖，无法撤销。建议先用"xdat 保存当前舵机"备份再修改。
9. **ID 修改风险**：写入失败或验证失败时程序会报错，但极端情况下舵机可能"失联"。遇到失联可尝试"恢复出厂设置"（复位后 ID 回到 1）。
10. **编码问题**：若在 Windows 控制台出现 emoji 乱码，请设置 `PYTHONIOENCODING=utf-8` 后再运行命令行工具。Linux/macOS 原生 UTF-8 一般无此问题。

---

## 🛠️ 故障排除

| 现象 | 可能原因 | 解决办法 |
| ---- | -------- | -------- |
| 无法打开串口 / 端口被占用 | 其他程序占用 | 关闭串口监视器等程序，或更换端口后重启工具 |
| 扫描不到舵机 | 供电不足 / 接线错误 / 波特率不符 | 检查供电与接线，确认舵机为 1M 波特率 |
| 读取参数失败 | 串口被占用 / 舵机未响应 | 关闭其他程序；重新连接；检查地址是否正确 |
| 温升过快 | 负载过大或堵转 | 检查机构卡滞，降低速度/加速度 |
| 修改 ID 后找不到舵机 | ID 冲突或写失败 | 恢复出厂设置，重新扫描 |

---

## 📁 目录结构

```
SCS0009_ServoController/
├── docs/                    # 分系统教程，按语言分目录
│   └── <lang>/              # en、zh-hans、zh-hant、de、es、fr、it、ja、ko、pt-br、pt-pt
│       ├── Windows.md       # 各语言文件名一致
│       ├── Linux.md
│       └── macOS.md
├── src/
│   ├── gui/                  # PySide6 图形界面
│   │   ├── factory_calibration_tool.py   # 主窗口（FT 调试器 + 语言切换）
│   │   ├── ft_debugger.py                # FT 调试器面板（参数读写 / xdat 备份）
│   │   ├── theme_utils.py                # 浅色主题
│   │   └── language_dialog.py            # 语言选择对话框
│   ├── xdat_utils.py         # xdat 参数文件读写
│   ├── i18n*.py / i18n_translations/     # 中英文国际化
│   └── port_utils.py         # 串口检测
├── scservo_sdk/              # FTServo 舵机通信 SDK
├── requirements.txt
└── setup.py                  # 环境检查脚本
```
