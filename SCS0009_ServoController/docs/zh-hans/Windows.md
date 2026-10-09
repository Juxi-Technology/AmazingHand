[English](../en/Windows.md) | [Deutsch](../de/Windows.md) | [Español](../es/Windows.md) | [Français](../fr/Windows.md) | [Italiano](../it/Windows.md) | [日本語](../ja/Windows.md) | [한국어](../ko/Windows.md) | [Português (BR)](../pt-br/Windows.md) | [Português (PT)](../pt-pt/Windows.md) | 简体中文 | [繁體中文](../zh-hant/Windows.md)

# SCS0009 舵机调试工具 — Windows 使用教程

适用于 Windows 10 / 11。本教程覆盖从环境安装到完整调试的每一步。

> ⚠️ **兼容性说明:本系统目前仅支持 Feetech SCS0009 舵机(SCS 系列,电位器位置反馈,10 位分辨率 0-1023)**。寄存器表、xdat 参数格式均针对飞特 SCS0009 设计,其他品牌/型号不保证兼容。

---

## 1. 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | >= 3.8 | 建议 3.10+，从 [python.org](https://www.python.org/downloads/) 下载 |
| PySide6 | >= 6.0 | GUI 框架 |
| pyserial | >= 3.5 | 串口通信 |
| 系统 | Win10 / Win11 | 任意版本 |

## 2. 安装 Python

1. 访问 <https://www.python.org/downloads/>
2. 下载 Python 3.10+ 安装包
3. 安装时**务必勾选 "Add Python to PATH"**(否则命令行找不到 python)

验证安装:

```bash
python --version
```

## 3. 安装依赖

推荐在虚拟环境中安装,避免污染系统 Python:

```bash
# 进入项目目录
cd SCS0009_ServoController

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境(Windows)
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

> ⚠️ **虚拟环境只需创建一次**。重复执行会覆盖原环境（清空已装依赖）。之后每次只需 `activate` 激活即可。

> 提示:激活后命令行前缀会出现 `(.venv)`。

## 4. 检查环境

```bash
python setup.py
```

看到 `[OK] 环境检查通过，可以运行项目` 即表示环境正确。

## 5. 连接硬件

1. 将 USB 转串口适配器(如 CH340 / CP2102)插入电脑
2. 连接舵机控制器(机械臂控制板)
3. 给舵机供电(建议 DC 5V 5A,Pro 版 DC 12V 5A)

打开设备管理器(`Win+X` → 设备管理器)确认串口号:

```
端口 (COM 和 LPT)
  └─ USB-SERIAL CH340 (COM3)     ← 你的舵机串口
```

> **记下 COM 号**,启动程序时选择。

## 6. 启动 GUI

```bash
python -m src.gui.factory_calibration_tool
```

或手动指定端口(串口被占用时):

```bash
python -m src.gui.factory_calibration_tool --port COM3
```

查看可用端口:

```bash
python -m src.gui.factory_calibration_tool --list-ports
```

## 7. 界面操作流程

> 界面为单面板布局,窗口高度不足时自动出现滚动条,最大化时自适应拉伸。

### 7.1 串口连接

- 选择端口、波特率(默认 1M),点击 **连接**
- 状态显示 `🟢 已连接`

### 7.2 扫描舵机

- 点击 **扫描舵机**,检测 ID 1-254 在线舵机
- 扫描结果实时显示在舵机列表(带型号)
- 点击舵机列表某行 → 自动填充到舵机下拉框

### 7.3 参数读写

- **读取参数**:读取全部 44 个寄存器(EEPROM + SRAM),日志实时显示结果
- **参数表**:5 列展示(地址/寄存器/值/存储区域/读写),EPROM/SRAM/DEFAULT 颜色区分
- **点选联动**:点击参数表某行 → 自动填充"写入地址""长度""值"
- **写入**:修改值后点写入,程序自动解锁/写入/锁定
- **写入结果弹窗**:成功弹绿色提示"✅ 已成功写入",失败弹红色提示"❌ 写入失败"(含原因)

### 7.4 位置控制

- **滑动条**:拖动滑块实时调整目标位置(0-1023),数值框同步显示
- **数值框**:也可直接输入目标位置,滑动条同步跟随
- 移动完成后状态栏提示"已移动完成,请关闭力矩"

### 7.5 波特率/恢复出厂

- **修改波特率**:选择新波特率(38400-1000000 bps),失败自动回滚
- **恢复出厂**:恢复为出厂默认(ID=1,波特率=1M),需重新扫描

### 7.6 xdat 参数(仅保存 EEPROM)

1. `💾 保存当前舵机`:保存当前 ID 舵机的 EEPROM 参数到 xdat 文件(备份)
2. `📂 打开 xdat`:加载备份文件
3. `📤 恢复参数到舵机`:把备份写回舵机

## 8. 常见问题

| 问题 | 解决 |
|------|------|
| 找不到串口 | 设备管理器检查驱动;换 USB 口;装 CH340 驱动 |
| 串口被占用 | 关闭串口监视器等程序;重启工具 |
| 中文字体显示空白 | 系统默认微软雅黑,若异常安装中文字体 |
| 舵机扫描不到 | 检查供电/接线;确认波特率 1M |
| 写入失败 | 检查舵机供电与连接;确认目标寄存器可写 |
| PermissionError 打开串口失败 | 确保没有其他进程占用该 COM 口 |

## 9. 命令行(可选)

```bash
# 列出可用串口
python -m src.gui.factory_calibration_tool --list-ports

# 指定端口启动
python -m src.gui.factory_calibration_tool --port COM3
```
