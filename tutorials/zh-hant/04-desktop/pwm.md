---
title: "PWM 桌面上位機（Tkinter GUI）"
description: "AmazingHand PWM 伺服馬達版桌面控制：原始碼執行、GUI 手勢/差動/直驅、內建 MediaPipe 追蹤、命令列測試與打包。"
version: pwm
---

# PWM 桌面上位機（Tkinter GUI）

> 以下命令在儲存庫的 `AmazingHand-PWM/` 目錄下執行。

本頁是 **PWM 伺服馬達版**的桌面控制教學。網頁控制見 [PWM 網頁控制](../03-web-control/pwm.md)，接線見 [PWM 接線](../01-hardware/pwm.md)，韌體燒錄見 [PWM 快速上手](../02-quick-start/pwm.md)。

> 適用：ESP32-S3 + 8 路 PWM 伺服馬達（差動驅動）。韌體燒錄見 [PWM 快速上手](../02-quick-start/pwm.md)，協定與命令見 [PWM 協定與標定](../06-servo-tuning/pwm.md)。

## 一、執行方式

| 方式 | 需要 | 適合 |
|------|------|------|
| **原始碼執行**（推薦） | 64 位 Python 3.12 + pyserial | 全部功能，含手勢追蹤 |
| 自行打包 exe | PyInstaller | 免裝 Python 分發（見第七節） |

## 二、原始碼執行

### 安裝相依套件

在模組根目錄（`AmazingHand-PWM/`）執行：

```bash
# 基礎相依套件（pyserial）
pip install -r tools/requirements.txt

# 需要手勢追蹤時再執行（自動建立 tools/tracking_env 並安裝 mediapipe）
tools/setup_tracking.bat
```

> mediapipe 0.10.14 只提供 64 位 Windows wheel，必須使用 **64 位 Python 3.12**。

### 啟動 GUI

```bash
# 任意帶 pyserial 的 Python
python tools/hand_gui.py

# 或使用追蹤環境（含 mediapipe）
tools/tracking_env/Scripts/python tools/hand_gui.py
```

![上位機主介面：序列埠欄、手勢命令、伺服馬達直驅與手指差動控制](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-main.png)

### GUI 使用

1. **選序列埠**：頂部下拉框選 ESP32 的 COM 埠（裝置管理員查看）。
2. **點「連線」**：狀態燈變綠，日誌顯示「已連線」，自動發 NOP 鏈路測試。
3. **手勢命令**：點「石頭 / 剪刀 / 布 / 比讚 / OK / 捏合 / 指向 / 張開 / 握拳」，靈巧手執行。
4. **左右手**：勾選「右手」/「左手」切換（拇指鏡像方向不同）。
5. **伺服馬達直驅**：拖 8 個滑桿，即時控制單個伺服馬達角度（0–180°）。
6. **手指差動控制**：每根手指兩個進度條——
   - **彎曲◀▶伸直**：手指彎曲或伸直（範圍 -70 ~ +70）。
   - **右擺◀▶左擺**：手指左右擺動（範圍 60 ~ 120，90=中立）。

   > 這兩個進度條是**控制軸**，不是兩個伺服馬達。程式會把它們合成為該指兩個伺服馬達的角度：同向分量產生側擺，反向分量產生屈伸。

7. **重複 / 停止**：重複上一次手勢 / 立即中斷。
8. **通訊日誌**：底部即時顯示收發幀和回應。

![手指差動控制面板：每根手指的彎曲/伸直與左右擺動](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-differential.png)

### GUI 內建手勢追蹤

GUI 自帶手勢追蹤面板（攝影機跟隨手部動作）：

1. 連接序列埠後，捲動到「手勢追蹤 (MediaPipe 攝影機)」面板。
2. 選攝影機號（預設 0），點**「開始追蹤」**。
3. 把手放進攝影機畫面，靈巧手跟隨彎曲/伸直。

> 追蹤需要 `tools/setup_tracking.bat` 裝好 mediapipe；用原始碼方式啟動的 GUI 才有追蹤功能。

## 三、命令列測試（tools/serial_test.py）

在模組根目錄執行：

```bash
# 鏈路測試（先確認能通）
python tools/serial_test.py COM3 nop

# 手勢
python tools/serial_test.py COM3 rock         # 石頭
python tools/serial_test.py COM3 thumbs_up    # 比讚
python tools/serial_test.py COM3 index        # 指向
python tools/serial_test.py COM3 open         # 張開
python tools/serial_test.py COM3 close        # 握拳

# 單伺服馬達直驅
python tools/serial_test.py COM3 servo 1 90   # 伺服馬達1 → 90°

# 全部歸中
python tools/serial_test.py COM3 mid

# 設左右手
python tools/serial_test.py COM3 hand L
python tools/serial_test.py COM3 hand R

# 掃頻/自檢
python tools/serial_test.py COM3 sweep 1      # 伺服馬達1 掃頻
python tools/serial_test.py COM3 test         # 全部伺服馬達逐個測試
```

## 四、序列埠工具手動測試（可選）

不用上位機，直接用序列埠工具發十六進位幀也能驗證鏈路。

**CoolTerm**（Windows / macOS / Linux）：

1. `Options` → 鮑率 **115200**、8N1。
2. `Connection` → `Send String` → 選擇 `Hex`。
3. 發送 `AA 01 00 01`（石頭），回應區應出現 `BB 01 00 01`（ACK）和 `BB 01 10 11`（完成）。

**Linux / macOS 命令列**：

```bash
# Linux
stty -F /dev/ttyUSB0 115200
printf '\xAA\x01\x00\x01' > /dev/ttyUSB0

# macOS
stty -f /dev/cu.usbserial-0001 115200
printf '\xAA\x01\x00\x01' > /dev/cu.usbserial-0001
```

幀格式、校驗和與全部命令見 [PWM 協定與標定](../06-servo-tuning/pwm.md)。

## 五、Python 控制腳本（自訂開發）

```python
import time
import serial

PORT, BAUD = "COM3", 115200          # Linux/macOS 換成 /dev/ttyUSB0、/dev/cu.usbserial-*

def frame(cmd, data=b""):
    checksum = cmd ^ len(data)
    for byte in data:
        checksum ^= byte
    return bytes([0xAA, cmd, len(data)]) + data + bytes([checksum & 0xFF])

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(1)                        # 等待 ESP32 重置完成

ser.write(frame(0x00))               # NOP 鏈路測試
ser.write(frame(0x01))               # 石頭
time.sleep(0.5)
ser.write(frame(0xF0, bytes([90] * 8)))  # 8 路伺服馬達全部 90°
ser.close()
```

回應幀為 `BB CMD STATUS CKSUM`，`STATUS=0x00` 表示已接受、`0x10` 表示手勢完成。完整命令表和直驅/左右手範例見 [PWM 協定與標定](../06-servo-tuning/pwm.md)。

## 六、常見問題

| 現象 | 處理 |
|------|------|
| 伺服馬達不動 | 檢查供電（5V 3A 獨立電源）、COM 埠、接線 |
| 無回應 / 開啟序列埠後伺服馬達亂動 | 確認鮑率 115200；GUI 連線時會先發 NOP 握手 |
| 攝影機沒畫面 | 允許攝影機權限（設定→隱私→相機） |
| 手型反了 | 勾選相反的左右手 |
| 追蹤沒反應 | 確認用 `tools\tracking_env` 的 Python 啟動，且 mediapipe 安裝成功 |

## 七、自行打包 exe（可選）

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole --name "AmazingHand控制台" tools/hand_gui.py
```

打包版不包含手勢追蹤（mediapipe 資源較大）；需要追蹤時請用原始碼方式。

> 完整協定與命令說明見 [PWM 協定與標定](../06-servo-tuning/pwm.md)。
