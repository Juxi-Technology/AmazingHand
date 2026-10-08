# SoARM 系列校准工具 — Linux 使用教程

适用于 Ubuntu / Debian / 其他主流发行版。重点:串口权限(dialout)、USB 转串口设备识别。

> ⚠️ **兼容性说明:本系统目前仅支持 Feetech SCS0009 舵机**。寄存器表、xdat 参数格式均针对飞特 SCS0009 设计,其他品牌/型号不保证兼容。

---

## 1. 环境要求

| 依赖 | 版本 |
|------|------|
| Python | >= 3.8(建议 3.10+) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| 系统 | Ubuntu 20.04+ / Debian 11+ |

中文字体(显示中文界面必需):

```bash
sudo apt install fonts-noto-cjk
```

emoji 图标字体(日志中的 ✅⚠️ 等):

```bash
sudo apt install fonts-noto-color-emoji
```

## 2. 安装 Python 依赖

```bash
cd SCS0009_ServoController

# 创建虚拟环境
python3 -m venv .venv

# 激活
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

> ⚠️ **虚拟环境只需创建一次**。重复执行会覆盖原环境（清空已装依赖）。之后每次只需 `source .venv/bin/activate`。


> 若 pip 报 externall managed environment,用 `pip install --break-system-packages -r requirements.txt` 或使用 venv。

## 3. ⚠️ 串口权限(dialout)【必需】

Linux 默认**普通用户无法访问** `/dev/ttyUSB*` / `/dev/ttyACM*`。将当前用户加入 `dialout` 组:

```bash
sudo usermod -a -G dialout $USER
```

**注销并重新登录**(或重启)后生效。验证:

```bash
groups
# 输出应包含 dialout
```

> 不生效时:重启电脑;部分发行版组名是 `uucp`(Arch)或 `tty`。

## 4. 识别 USB 转串口设备

插入适配器后,查看设备:

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

典型输出:

```
/dev/ttyUSB0   # CH340 / CP2102 / PL2303
/dev/ttyACM0   # 原生 USB 串口(Arduino/ESP32 板载)
```

查看详细制造商信息:

```bash
dmesg | tail -20 | grep -i tty
# 或
lsusb
```

> 多个设备时按插拔顺序分配 ttyUSB0/ttyUSB1,可能不稳定。建议**用 /dev/ttyACM* 或按制造商固定**。

## 5. 检查环境

```bash
python setup.py
```

## 6. 启动 GUI

```bash
python -m src.gui.factory_calibration_tool
```

指定端口:

```bash
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

> 若只有一个串口,工具会自动把第二个端口设为"禁用"。

## 7. 界面操作流程

> 单面板布局,窗口高度不足时自动出现滚动条,最大化时自适应拉伸。

### 7.1 串口连接
选择端口、波特率(默认 1M),点击 **连接**。

### 7.2 扫描舵机
点击 **扫描舵机**,检测 ID 1-254 在线舵机;点击舵机列表行自动填充下拉框。

### 7.3 参数读写
- 读取参数、参数表(44 个寄存器)、**点选联动填充地址/长度/值**
- 修改值后点写入,程序自动解锁/写入/锁定
- **写入弹窗**:成功弹绿色"✅ 已成功写入",失败弹红色"❌ 写入失败"(含原因)

### 7.4 位置控制
- **滑动条**拖动调整目标位置(0-1023),数值框同步显示
- 移动完成后提示关闭力矩

### 7.5 波特率/恢复出厂
修改波特率(失败回滚)、恢复出厂。

### 7.6 xdat 参数(仅保存 EEPROM)
保存当前舵机 → 打开备份 → 恢复。

## 8. 常见问题

| 问题 | 解决 |
|------|------|
| **Permission denied: /dev/ttyUSB0** | 未加入 dialout 组,见第 3 节;或 `sudo chmod 666 /dev/ttyUSB0`(临时) |
| 找不到串口 | `ls /dev/ttyUSB* /dev/ttyACM*`;`lsusb` 确认设备 |
| 设备名变化 | 插拔顺序影响 ttyUSB 编号;用 `udev` 规则固定或每次启动时选择 |
| 中文界面空白 | 安装 `fonts-noto-cjk` |
| emoji 显示方块 | 安装 `fonts-noto-color-emoji` |
| pip 安装失败 | 用虚拟环境;或 `--break-system-packages` |
| 程序无法启动 | `python3 --version` 确认版本;`pip list` 检查依赖 |

## 9. 命令行(可选)

```bash
# 列出可用串口
python -m src.gui.factory_calibration_tool --list-ports

# 指定端口启动
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

## 10. 高级:udev 固定设备名(可选)

创建 `/etc/udev/rules.d/99-servo.rules` 按 USB ID 固定:

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyServo"
```

`ls -l /dev/ttyServo` 即可用固定名。厂商 ID 用 `lsusb` 查询。
