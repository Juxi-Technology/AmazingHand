# AmazingHand PWM 伺服馬達版 — 快速上手

用 **ESP32-S3 + 8 路 PWM 伺服馬達**驅動 AmazingHand。完整手冊見本 `docs/` 目錄。

## 硬體

| 項目 | 型號 |
|------|------|
| 主控 | ESP32-S3 開發板（優信 YX-ESP32-S3 或同類） |
| 伺服馬達 | 8 個 PWM 伺服馬達——韌體依 **PTK 7452 MG-D 數位伺服馬達（333 Hz）** 標定 |
| 轉接板 | PWM 伺服馬達轉接板 |
| 電源 | 5 V / 3 A，轉接板與 ESP32 共地 |

> SG90 等 50 Hz 類比伺服馬達**不能**直接替換 333 Hz 韌體。

| 通道 | GPIO | 關節 | 通道 | GPIO | 關節 |
|---------|------|-------|---------|------|-------|
| PWM1 | 4 | 食指 1 | PWM5 | 15 | 無名指 1 |
| PWM2 | 5 | 食指 2 | PWM6 | 16 | 無名指 2 |
| PWM3 | 6 | 中指 1 | PWM7 | 17 | 拇指 1 |
| PWM4 | 7 | 中指 2 | PWM8 | 18 | 拇指 2 |

## 1. 燒錄韌體

使用 ESP-IDF：

```bash
cd firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

使用預編譯映像和 `esptool`：

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  firmware/prebuilt/amazinghand_pwm.bin
```

序列埠參數為 **115200-8N1**，上電後會印出啟動資訊。

## 2. 控制靈巧手

桌面 GUI：

```bash
pip install -r tools/requirements.txt
python tools/hand_gui.py
```

攝影機追蹤需要先執行 `tools/setup_tracking.bat` 建立環境，然後：

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

網頁控制：打開倉庫的 `Amazinghand-web-io/` 頁面（或執行 `Amazinghand-web/server.py --driver pwm`），驅動選擇 **PWM（ESP32-S3）**，選取 ESP32 序列埠並連線。

## 3. 完整文件

| 文件 | 內容 |
|----------|----------|
| [`../en/user_manual.md`](../en/user_manual.md) / [`../zh-hans/用户手册.md`](../zh-hans/用户手册.md) | 通訊協定、指令參考、接線、校正、常見問題 |
| [`../en/full_workflow.md`](../en/full_workflow.md) / [`../zh-hans/全流程使用教程.md`](../zh-hans/全流程使用教程.md) | 端對端工作流程 |
| [`../en/gui_usage.md`](../en/gui_usage.md) / [`../zh-hans/使用教程.md`](../zh-hans/使用教程.md) | GUI 與序列埠測試工具 |
| [`../en/hand_tracking.md`](../en/hand_tracking.md) / [`../zh-hans/手势追踪教程.md`](../zh-hans/手势追踪教程.md) | MediaPipe 手勢追蹤 |

## 4. 常見問題

- **無回應**：檢查鮑率 115200、ESP32 的 COM 埠、5 V / 3 A 供電與共地；網頁會自動重試 NOP 握手。
- **伺服馬達不動或抖動**：確認伺服馬達是 333 Hz 數位伺服馬達，且電源足夠。
- **方向相反**：在 `Amazinghand-web-io/config.json` 的 `pwm.calibration` 裡把對應手指的 `scale` 改為 `-1`。
- **中位偏移**：調整對應通道的 `offset_deg`。
- **提示「忙碌」**：韌體正在執行內建手勢，請等它完成或發送停止（`0xFF`）。
