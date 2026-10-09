[English](../en/macOS.md) | [Deutsch](../de/macOS.md) | [Español](../es/macOS.md) | [Français](../fr/macOS.md) | [Italiano](../it/macOS.md) | [日本語](../ja/macOS.md) | [한국어](../ko/macOS.md) | [Português (BR)](../pt-br/macOS.md) | [Português (PT)](../pt-pt/macOS.md) | 简体中文 | [繁體中文](../zh-hant/macOS.md)

# SoARM 系列校准工具 — macOS 使用教程

适用于 macOS 11 (Big Sur) 及以上。重点:串口命名(`cu.*` vs `tty.*`)、USB 驱动。

> ⚠️ **兼容性说明:本系统目前仅支持 Feetech SCS0009 舵机**。寄存器表、xdat 参数格式均针对飞特 SCS0009 设计,其他品牌/型号不保证兼容。

---

## 1. 环境要求

| 依赖 | 版本 |
|------|------|
| Python | >= 3.8(建议 3.10+,Homebrew 安装) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| 系统 | macOS 11+ (Apple Silicon / Intel) |

## 2. 安装 Python

推荐用 Homebrew 安装,避免系统自带 Python 版本过旧:

```bash
# 安装 Homebrew(如果没有)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python
brew install python
```

验证:

```bash
python3 --version
```

## 3. 安装依赖

```bash
cd SCS0009_ServoController

# 创建虚拟环境
python3 -m venv .venv

# 激活(macOS 用 source,不是 .bat)
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

> ⚠️ **虚拟环境只需创建一次**。重复执行会覆盖原环境（清空已装依赖）。之后每次只需 `source .venv/bin/activate`。

## 4. ⚠️ macOS 串口命名【关键】

macOS 把 USB 转串口设备放在 `/dev` 下,有**两套命名**:

| 前缀 | 含义 | 是否可用 |
|------|------|---------|
| `/dev/tty.usbserial-*` | 调制解调器风格(阻塞式) | 可能卡住,不推荐 |
| `/dev/cu.usbserial-*` | 调用/终端风格(**非阻塞**) | ✅ 推荐使用 |

**查看你的串口名:**

```bash
ls /dev/cu.*
```

典型输出:

```
/dev/cu.usbserial-0001      # CP2102 / FTDI
/dev/cu.usbmodem141101      # 板载 USB 串口(Arduino/ESP32)
/dev/cu.wchusbserial1420    # CH340
```

> 程序会自动优先选择 `cu.*` 设备。若手动指定端口,请用 `cu.` 而非 `tty.`。

## 5. USB 驱动

大部分常见芯片(CH340、CP2102、FTDI)macOS 自带驱动,即插即用。若设备不识别:

```bash
system_profiler SPUSBDataType | grep -A5 -i "serial\|CH340\|CP210"
```

- **CH340**:较老批次需安装 WCH 官方驱动
- 一般 `ls /dev/cu.*` 能看到设备即可

## 6. 检查环境

```bash
python setup.py
```

## 7. 启动 GUI

```bash
python -m src.gui.factory_calibration_tool
```

指定端口:

```bash
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

> 只有一个串口时,第二个端口自动禁用。

## 8. 界面操作流程

> 单面板布局,窗口高度不足时自动出现滚动条,最大化时自适应拉伸。

### 8.1 串口连接
选择端口、波特率(默认 1M),点击 **连接**。

### 8.2 扫描舵机
点击 **扫描舵机**,检测 ID 1-254 在线舵机;点击舵机列表行自动填充下拉框。

### 8.3 参数读写
- 读取参数、参数表(44 个寄存器)、**点选联动填充地址/长度/值**
- 修改值后点写入,程序自动解锁/写入/锁定
- **写入弹窗**:成功弹绿色"✅ 已成功写入",失败弹红色"❌ 写入失败"(含原因)

### 8.4 位置控制
- **滑动条**拖动调整目标位置(0-1023),数值框同步显示
- 移动完成后提示关闭力矩

### 8.5 波特率/恢复出厂
修改波特率(失败回滚)、恢复出厂。

### 8.6 xdat 参数(仅保存 EEPROM)
保存当前舵机 → 打开备份 → 恢复。

## 9. 常见问题

| 问题 | 解决 |
|------|------|
| 串口名带 `tty.` 卡住 | 改用 `cu.` 前缀 |
| 找不到设备 | `ls /dev/cu.*`;插拔后重插;`system_profiler SPUSBDataType` |
| 中文界面空白 | 系统自带 PingFang,一般正常;异常时安装 Noto Sans CJK |
| 权限问题 | macOS 一般无需额外权限;若弹出访问控制,允许终端访问 |
| 虚拟环境激活失败 | `source .venv/bin/activate`(不是 `.bat`) |
| Apple Silicon 编译错误 | Python 3.10+ 原生支持,避免用 Rosetta 的旧 Python |

## 10. 命令行(可选)

```bash
# 列出可用串口
python -m src.gui.factory_calibration_tool --list-ports

# 指定端口启动
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 11. 提示

- **串口名会变**:不同 USB 口插拔后 `cu.*` 名可能变化,每次启动时在顶栏下拉框选择即可
- **省电**:macOS 可能休眠导致串口断开,操作时保持唤醒或调高睡眠时间
- **隐私权限**:首次运行如提示"访问可移动磁盘",点击允许
