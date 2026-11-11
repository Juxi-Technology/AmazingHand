---
title: "Arduino 與 Python 範例"
description: "AmazingHand 官方 Arduino/Python 範例：SCServo 函式庫、Feetech 調校工具、TTL Linker 接線模式、Arduino Uno/Mega 序列埠與 Python 基礎腳本。"
version: scs0009
---

# Arduino 與 Python 範例

本頁整理 `AmazingHand-main/ArduinoExample/` 與 `AmazingHand-main/PythonExample/` 的官方範例和接線要點。

## Arduino 範例

### 準備工作

- 在 Arduino IDE 的函式庫管理器中安裝 **SCServo** 函式庫。
- 使用 Feetech FD 調校工具設定伺服馬達 ID（`feetech debug tool`）。
- Arduino 與 TTL Linker 之間 **RX/TX 交叉連接**。

### Link 模式：修改伺服馬達 ID

1. 先在 Arduino 上傳 `Blink` 範例。
2. 按 Link 模式接線，開啟 Feetech 軟體修改 ID。

![Link 模式接線](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Link-mode.jpg)

![安裝 SCServo 函式庫](../../assets/robot-arms/amazing-hand/arduino-extension/SCServo.jpg)

### Control 模式：Arduino 控制伺服馬達

上傳自訂程式後，按 Control 模式接線：

![Control 模式接線](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Control-mode.jpg)

- **Arduino Uno**（只有一個序列埠）：按圖使用軟體序列埠/指定腳位。
- **Arduino Mega**：使用 **RX1 / TX1（19 / 18）**。

![Uno 序列埠接線](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Uno.jpg)

![Mega 序列埠接線](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Mega.jpg)

> 腳位號、函式庫版本和 TTL Linker 方向以實際板卡絲印為準；改 ID 前先確認匯流排供電和共地。

## Python 範例

`AmazingHand-main/PythonExample/` 提供 4 個基礎腳本：

| 腳本 | 作用 |
|------|------|
| `AmazingHand_Demo.py` | 單手基礎演示：連接匯流排、執行動作 |
| `AmazingHand_Demo_Both.py` | 雙手演示 |
| `AmazingHand_FingerTest.py` | 單指測試 |
| `AmazingHand_Hand_FingerMiddlePos.py` | 手指中位校準 |

使用前：

1. 用 Feetech 軟體設定伺服馬達 ID（右 1–8、左 11–18）。
2. 安裝 `pyserial`，按腳本內的序列埠名/鮑率修改後執行。
3. 確認外部伺服馬達電源已接好並與匯流排驅動板共地。

> 這些是官方基礎範例；更完整的 GUI/CLI 見 [SCS0009 桌面上位機](../04-desktop/scs0009.md)，TTL 接線與中位見 [SCS0009 伺服馬達調校與標定](../06-servo-tuning/scs0009.md)。

## 原始碼位置

- [`AmazingHand-main/ArduinoExample/`](../../../AmazingHand-main/ArduinoExample/)
- [`AmazingHand-main/PythonExample/`](../../../AmazingHand-main/PythonExample/)
