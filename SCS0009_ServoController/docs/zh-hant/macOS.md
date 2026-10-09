[English](../en/macOS.md) | [Deutsch](../de/macOS.md) | [Español](../es/macOS.md) | [Français](../fr/macOS.md) | [Italiano](../it/macOS.md) | [日本語](../ja/macOS.md) | [한국어](../ko/macOS.md) | [Português (BR)](../pt-br/macOS.md) | [Português (PT)](../pt-pt/macOS.md) | [简体中文](../zh-hans/macOS.md) | 繁體中文

# SoARM 系列校準工具 — macOS 使用教學

適用於 macOS 11 (Big Sur) 及以上。重點:序列埠命名(`cu.*` vs `tty.*`)、USB 驅動。

> ⚠️ **相容性說明:本系統目前僅支援 Feetech SCS0009 舵機**。暫存器表、xdat 參數格式均針對飛特 SCS0009 設計,其他品牌/型號不保證相容。

---

## 1. 環境需求

| 依賴 | 版本 |
|------|------|
| Python | >= 3.8(建議 3.10+,Homebrew 安裝) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| 系統 | macOS 11+ (Apple Silicon / Intel) |

## 2. 安裝 Python

建議用 Homebrew 安裝,避免系統內建 Python 版本過舊:

```bash
# 安装 Homebrew(如果没有)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python
brew install python
```

驗證:

```bash
python3 --version
```

## 3. 安裝依賴

```bash
cd SCS0009_ServoController

# 创建虚拟环境
python3 -m venv .venv

# 激活(macOS 用 source,不是 .bat)
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

> ⚠️ **虛擬環境只需建立一次**。重複執行會覆蓋原環境（清空已裝依賴）。之後每次只需 `source .venv/bin/activate`。

## 4. ⚠️ macOS 序列埠命名【關鍵】

macOS 把 USB 轉序列埠裝置放在 `/dev` 下,有**兩套命名**:

| 前綴 | 含義 | 是否可用 |
|------|------|---------|
| `/dev/tty.usbserial-*` | 數據機風格(阻塞式) | 可能卡住,不推薦 |
| `/dev/cu.usbserial-*` | 呼叫/終端機風格(**非阻塞**) | ✅ 推薦使用 |

**查看你的序列埠名稱:**

```bash
ls /dev/cu.*
```

典型輸出:

```
/dev/cu.usbserial-0001      # CP2102 / FTDI
/dev/cu.usbmodem141101      # 板载 USB 串口(Arduino/ESP32)
/dev/cu.wchusbserial1420    # CH340
```

> 程式會自動優先選擇 `cu.*` 裝置。若手動指定連接埠,請用 `cu.` 而非 `tty.`。

## 5. USB 驅動

大部分常見晶片(CH340、CP2102、FTDI)macOS 內建驅動,隨插即用。若裝置辨識不到:

```bash
system_profiler SPUSBDataType | grep -A5 -i "serial\|CH340\|CP210"
```

- **CH340**:較舊批次需安裝 WCH 官方驅動
- 一般 `ls /dev/cu.*` 能看到裝置即可

## 6. 檢查環境

```bash
python setup.py
```

## 7. 啟動 GUI

```bash
python -m src.gui.factory_calibration_tool
```

指定連接埠:

```bash
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

> 只有一個序列埠時,第二個連接埠自動禁用。

## 8. 介面操作流程

> 單面板版面配置,視窗高度不足時自動出現捲軸,最大化時自適應拉伸。

### 8.1 序列埠連線
選擇連接埠、鮑率(預設 1M),點擊 **連線**。

### 8.2 掃描舵機
點擊 **掃描舵機**,偵測 ID 1-254 線上舵機;點擊舵機列表列自動填入下拉式選單。

### 8.3 參數讀寫
- 讀取參數、參數表(44 個暫存器)、**點選連動填入位址/長度/值**
- 修改值後點寫入,程式自動解鎖/寫入/鎖定
- **寫入彈出視窗**:成功彈出綠色"✅ 已成功寫入",失敗彈出紅色"❌ 寫入失敗"(含原因)

### 8.4 位置控制
- **滑動條**拖曳調整目標位置(0-1023),數值框同步顯示
- 移動完成後提示關閉力矩

### 8.5 鮑率/恢復出廠
修改鮑率(失敗回復)、恢復出廠。

### 8.6 xdat 參數(僅儲存 EEPROM)
儲存目前舵機 → 開啟備份 → 恢復。

## 9. 常見問題

| 問題 | 解決 |
|------|------|
| 序列埠名稱帶 `tty.` 卡住 | 改用 `cu.` 前綴 |
| 找不到裝置 | `ls /dev/cu.*`;插拔後重插;`system_profiler SPUSBDataType` |
| 中文介面空白 | 系統內建 PingFang,一般正常;異常時安裝 Noto Sans CJK |
| 權限問題 | macOS 一般無需額外權限;若彈出存取控制,允許終端機存取 |
| 虛擬環境啟用失敗 | `source .venv/bin/activate`(不是 `.bat`) |
| Apple Silicon 編譯錯誤 | Python 3.10+ 原生支援,避免用 Rosetta 的舊 Python |

## 10. 命令列(選用)

```bash
# 列出可用串口
python -m src.gui.factory_calibration_tool --list-ports

# 指定端口启动
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 11. 提示

- **序列埠名稱會變**:不同 USB 埠插拔後 `cu.*` 名稱可能變化,每次啟動時在頂端列下拉式選單選擇即可
- **省電**:macOS 可能休眠導致序列埠中斷,操作時保持喚醒或調高睡眠時間
- **隱私權限**:首次執行如提示"存取可移除磁碟",點擊允許
