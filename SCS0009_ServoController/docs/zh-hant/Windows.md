[English](../en/Windows.md) | [Deutsch](../de/Windows.md) | [Español](../es/Windows.md) | [Français](../fr/Windows.md) | [Italiano](../it/Windows.md) | [日本語](../ja/Windows.md) | [한국어](../ko/Windows.md) | [Português (BR)](../pt-br/Windows.md) | [Português (PT)](../pt-pt/Windows.md) | [简体中文](../zh-hans/Windows.md) | 繁體中文

# SCS0009 舵機除錯工具 — Windows 使用教學

適用於 Windows 10 / 11。本教學涵蓋從環境安裝到完整除錯的每一步。

> ⚠️ **相容性說明:本系統目前僅支援 Feetech SCS0009 舵機(SCS 系列,電位器位置回饋,10 位元解析度 0-1023)**。暫存器表、xdat 參數格式均針對飛特 SCS0009 設計,其他品牌/型號不保證相容。

---

## 1. 環境需求

| 依賴 | 版本 | 說明 |
|------|------|------|
| Python | >= 3.8 | 建議 3.10+，從 [python.org](https://www.python.org/downloads/) 下載 |
| PySide6 | >= 6.0 | GUI 框架 |
| pyserial | >= 3.5 | 序列埠通訊 |
| 系統 | Win10 / Win11 | 任意版本 |

## 2. 安裝 Python

1. 造訪 <https://www.python.org/downloads/>
2. 下載 Python 3.10+ 安裝套件
3. 安裝時**務必勾選 "Add Python to PATH"**(否則命令列找不到 python)

驗證安裝:

```bash
python --version
```

## 3. 安裝依賴

建議在虛擬環境中安裝,避免汙染系統 Python:

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

> ⚠️ **虛擬環境只需建立一次**。重複執行會覆蓋原環境（清空已裝依賴）。之後每次只需 `activate` 啟用即可。

> 提示:啟用後命令列前綴會出現 `(.venv)`。

## 4. 檢查環境

```bash
python setup.py
```

看到 `[OK] 环境检查通过，可以运行项目` 即表示環境正確。

## 5. 連接硬體

1. 將 USB 轉序列埠轉接器(如 CH340 / CP2102)插入電腦
2. 連接舵機控制器(機械手臂控制板)
3. 為舵機供電(建議 DC 5V 5A,Pro 版 DC 12V 5A)

開啟裝置管理員(`Win+X` → 裝置管理員)確認連接埠號:

```
端口 (COM 和 LPT)
  └─ USB-SERIAL CH340 (COM3)     ← 你的舵机串口
```

> **記下 COM 號**,啟動程式時選擇。

## 6. 啟動 GUI

```bash
python -m src.gui.factory_calibration_tool
```

或手動指定連接埠(序列埠被占用時):

```bash
python -m src.gui.factory_calibration_tool --port COM3
```

查看可用連接埠:

```bash
python -m src.gui.factory_calibration_tool --list-ports
```

## 7. 介面操作流程

> 介面為單面板版面配置,視窗高度不足時自動出現捲軸,最大化時自適應拉伸。

### 7.1 序列埠連線

- 選擇連接埠、鮑率(預設 1M),點擊 **連線**
- 狀態顯示 `🟢 已连接`

### 7.2 掃描舵機

- 點擊 **掃描舵機**,偵測 ID 1-254 線上舵機
- 掃描結果即時顯示在舵機列表(帶型號)
- 點擊舵機列表某列 → 自動填入到舵機下拉式選單

### 7.3 參數讀寫

- **讀取參數**:讀取全部 44 個暫存器(EEPROM + SRAM),日誌即時顯示結果
- **參數表**:5 欄顯示(位址/暫存器/值/儲存區域/讀寫),EPROM/SRAM/DEFAULT 顏色區分
- **點選連動**:點擊參數表某列 → 自動填入"寫入位址""長度""值"
- **寫入**:修改值後點寫入,程式自動解鎖/寫入/鎖定
- **寫入結果彈出視窗**:成功彈出綠色提示"✅ 已成功寫入",失敗彈出紅色提示"❌ 寫入失敗"(含原因)

### 7.4 位置控制

- **滑動條**:拖曳滑桿即時調整目標位置(0-1023),數值框同步顯示
- **數值框**:也可直接輸入目標位置,滑動條同步跟隨
- 移動完成後狀態列提示"已移動完成,請關閉力矩"

### 7.5 鮑率/恢復出廠

- **修改鮑率**:選擇新鮑率(38400-1000000 bps),失敗自動回復
- **恢復出廠**:恢復為出廠預設(ID=1,鮑率=1M),需重新掃描

### 7.6 xdat 參數(僅儲存 EEPROM)

1. `💾 保存当前舵机`:儲存目前 ID 舵機的 EEPROM 參數到 xdat 檔案(備份)
2. `📂 打开 xdat`:載入備份檔案
3. `📤 恢复参数到舵机`:把備份寫回舵機

## 8. 常見問題

| 問題 | 解決 |
|------|------|
| 找不到序列埠 | 裝置管理員檢查驅動;換 USB 埠;裝 CH340 驅動 |
| 序列埠被占用 | 關閉序列埠監視器等程式;重新啟動工具 |
| 中文字體顯示空白 | 系統預設微軟雅黑,若異常安裝中文字體 |
| 舵機掃描不到 | 檢查供電/接線;確認鮑率 1M |
| 寫入失敗 | 檢查舵機供電與連線;確認目標暫存器可寫 |
| PermissionError 開啟序列埠失敗 | 確保沒有其他行程占用該 COM 埠 |

## 9. 命令列(選用)

```bash
# 列出可用串口
python -m src.gui.factory_calibration_tool --list-ports

# 指定端口启动
python -m src.gui.factory_calibration_tool --port COM3
```
