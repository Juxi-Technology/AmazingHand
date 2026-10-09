[English](../en/Linux.md) | [Deutsch](../de/Linux.md) | [Español](../es/Linux.md) | [Français](../fr/Linux.md) | [Italiano](../it/Linux.md) | [日本語](../ja/Linux.md) | [한국어](../ko/Linux.md) | [Português (BR)](../pt-br/Linux.md) | [Português (PT)](../pt-pt/Linux.md) | [简体中文](../zh-hans/Linux.md) | 繁體中文

# SoARM 系列校準工具 — Linux 使用教學

適用於 Ubuntu / Debian / 其他主流發行版。重點:序列埠權限(dialout)、USB 轉序列埠裝置辨識。

> ⚠️ **相容性說明:本系統目前僅支援 Feetech SCS0009 舵機**。暫存器表、xdat 參數格式均針對飛特 SCS0009 設計,其他品牌/型號不保證相容。

---

## 1. 環境需求

| 依賴 | 版本 |
|------|------|
| Python | >= 3.8(建議 3.10+) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| 系統 | Ubuntu 20.04+ / Debian 11+ |

中文字體(顯示中文介面必需):

```bash
sudo apt install fonts-noto-cjk
```

emoji 圖示字體(日誌中的 ✅⚠️ 等):

```bash
sudo apt install fonts-noto-color-emoji
```

## 2. 安裝 Python 依賴

```bash
cd SCS0009_ServoController

# 创建虚拟环境
python3 -m venv .venv

# 激活
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

> ⚠️ **虛擬環境只需建立一次**。重複執行會覆蓋原環境（清空已裝依賴）。之後每次只需 `source .venv/bin/activate`。

> 若 pip 報 externall managed environment,用 `pip install --break-system-packages -r requirements.txt` 或使用 venv。

## 3. ⚠️ 序列埠權限(dialout)【必需】

Linux 預設**一般使用者無法存取** `/dev/ttyUSB*` / `/dev/ttyACM*`。將目前使用者加入 `dialout` 群組:

```bash
sudo usermod -a -G dialout $USER
```

**登出並重新登入**(或重新開機)後生效。驗證:

```bash
groups
# 输出应包含 dialout
```

> 不生效時:重新開機;部分發行版群組名稱是 `uucp`(Arch)或 `tty`。

## 4. 辨識 USB 轉序列埠裝置

插入轉接器後,查看裝置:

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

典型輸出:

```
/dev/ttyUSB0   # CH340 / CP2102 / PL2303
/dev/ttyACM0   # 原生 USB 串口(Arduino/ESP32 板载)
```

查看詳細製造商資訊:

```bash
dmesg | tail -20 | grep -i tty
# 或
lsusb
```

> 多個裝置時按插拔順序分配 ttyUSB0/ttyUSB1,可能不穩定。建議**用 /dev/ttyACM* 或按製造商固定**。

## 5. 檢查環境

```bash
python setup.py
```

## 6. 啟動 GUI

```bash
python -m src.gui.factory_calibration_tool
```

指定連接埠:

```bash
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

> 若只有一個序列埠,工具會自動把第二個連接埠設為"禁用"。

## 7. 介面操作流程

> 單面板版面配置,視窗高度不足時自動出現捲軸,最大化時自適應拉伸。

### 7.1 序列埠連線
選擇連接埠、鮑率(預設 1M),點擊 **連線**。

### 7.2 掃描舵機
點擊 **掃描舵機**,偵測 ID 1-254 線上舵機;點擊舵機列表列自動填入下拉式選單。

### 7.3 參數讀寫
- 讀取參數、參數表(44 個暫存器)、**點選連動填入位址/長度/值**
- 修改值後點寫入,程式自動解鎖/寫入/鎖定
- **寫入彈出視窗**:成功彈出綠色"✅ 已成功寫入",失敗彈出紅色"❌ 寫入失敗"(含原因)

### 7.4 位置控制
- **滑動條**拖曳調整目標位置(0-1023),數值框同步顯示
- 移動完成後提示關閉力矩

### 7.5 鮑率/恢復出廠
修改鮑率(失敗回復)、恢復出廠。

### 7.6 xdat 參數(僅儲存 EEPROM)
儲存目前舵機 → 開啟備份 → 恢復。

## 8. 常見問題

| 問題 | 解決 |
|------|------|
| **Permission denied: /dev/ttyUSB0** | 未加入 dialout 群組,見第 3 節;或 `sudo chmod 666 /dev/ttyUSB0`(暫時) |
| 找不到序列埠 | `ls /dev/ttyUSB* /dev/ttyACM*`;`lsusb` 確認裝置 |
| 裝置名稱變化 | 插拔順序影響 ttyUSB 編號;用 `udev` 規則固定或每次啟動時選擇 |
| 中文介面空白 | 安裝 `fonts-noto-cjk` |
| emoji 顯示方塊 | 安裝 `fonts-noto-color-emoji` |
| pip 安裝失敗 | 用虛擬環境;或 `--break-system-packages` |
| 程式無法啟動 | `python3 --version` 確認版本;`pip list` 檢查依賴 |

## 9. 命令列(選用)

```bash
# 列出可用串口
python -m src.gui.factory_calibration_tool --list-ports

# 指定端口启动
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

## 10. 進階:udev 固定裝置名稱(選用)

建立 `/etc/udev/rules.d/99-servo.rules` 按 USB ID 固定:

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyServo"
```

`ls -l /dev/ttyServo` 即可用固定名稱。廠商 ID 用 `lsusb` 查詢。
