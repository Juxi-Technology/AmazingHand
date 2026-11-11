---
title: "PWM 網頁控制"
description: "AmazingHand PWM 伺服馬達版網頁控制：ESP32-S3 連線、驅動切換、與 SCS0009 的差異、角度標定與常見問題。"
version: pwm
---

# PWM 網頁控制

本頁是網頁控制的 **PWM（ESP32-S3）版**專用說明。通用介面、啟動方式、預設姿態、攝影機遙操作見 [網頁控制總覽](README.md)。

## 硬體與燒錄

- 接線、GPIO、供電和伺服馬達型號見 [PWM 接線、GPIO 與供電](../01-hardware/pwm.md)。
- 韌體燒錄（ESP-IDF 或預編譯 bin）見 [PWM 快速上手](../02-quick-start/pwm.md)。
- 上位機↔ESP32 固定 **115200 8N1**；伺服馬達本身沒有鮑率。

## 網頁連線

1. 頂部「驅動」下拉選 **PWM（ESP32-S3）**
2. 點 **新增序列埠…**，選中 ESP32-S3 的 USB 序列埠
3. 點 **連線**：頁面會自動握手（NOP）、發送左右手選擇並回中位
4. 之後用滑桿、預設姿態、攝影機遙操作控制；手指標題顯示 **CH 1/2 …**（PWM 通道號）

![PWM 模式：頂部驅動選擇與 CH 通道顯示](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-port-bar.png)

![PWM 模式的手動控制面板：手指標題顯示 CH 通道，力矩按鈕隱藏](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-manual.png)

## 和 SCS0009 版的差異

| 項目 | SCS0009 匯流排版 | PWM 版 |
|------|----------------|--------|
| 序列埠鮑率 | 1,000,000 | **115,200** |
| 驅動板 | USB 匯流排驅動板 | ESP32-S3 + PWM 轉接板 |
| 力矩 | 可開啟/釋放 | **無**（韌體沒有力矩命令，按鈕會隱藏） |
| 急停 | 鬆開全部力矩 | 發送 `0xFF` 中止手勢，伺服馬達仍通電保持位置 |
| 速度 | 支援速度參數 | 直驅幀無速度參數 |
| 回饋 | 位置/溫度/電壓/速度回讀 | **無回讀**，無法偵測堵轉或失步 |
| 左右手 | 不同伺服馬達 ID | 同一組通道，發 `0xF1` 切換（主要影響韌體手勢；網頁姿態用各自手的映射） |

## 角度標定

網頁把姿態值換算成 8 路 0–180° 角度，預設公式：

```
angle = 90 + dir × scale × 姿態值 + offset
```

- 每根手指第一個通道 `dir = -1`，第二個通道 `dir = +1`
- 預設 `scale = 1`、`offset = 0`，即直接鏡像伺服馬達軸角度
- `mirror_pose` 為真時先交換每指兩個姿態值（本儲存庫左右手均開啟）

如果實機方向相反或中位偏了，編輯 [`config.json`](../../../Amazinghand-web-io/config.json) 的 `pwm.calibration`：

```jsonc
"pwm": {
  "calibration": {
    "right": {
      "pointer": { "scale": 1.0, "offset_deg": [0, 0] }
    }
  }
}
```

- 方向相反：把對應指的 `scale` 改為 `-1`
- 中位偏移：調 `offset_deg`（兩個通道分別調）
- 逐指步驟：回中位 → 單獨拖動一根手指 → 觀察方向/中位 → 改 `scale`/`offset_deg` → 重新整理頁面重試

## 常見問題

- **連線失敗 / ESP32 無回應**：確認鮑率是 115200、選的是 ESP32 的 COM 埠、5 V/3 A 供電和共地；開啟序列埠後 ESP32 可能重置，頁面會自動重試 NOP
- **伺服馬達不動或抖動**：先確認伺服馬達是 333 Hz 數位伺服馬達（PTK 7452 MG-D 或同類），電源足夠；SG90 需改韌體
- **方向反了**：改對應指的 `scale` 為 `-1`
- **中位不對**：調對應通道的 `offset_deg`
- **提示「忙碌（手勢執行中）」**：韌體正在執行內建手勢，等它完成或點急停（`0xFF`）
- **掃描伺服馬達**：`tools/scan_servos.py` 只適用於 SCS0009；PWM 用 `AmazingHand-PWM/tools/serial_test.py` 或網頁

---

## 相關頁面

- [PWM 協定與標定](../06-servo-tuning/pwm.md)
- [PWM 桌面上位機](../04-desktop/pwm.md)
- [PWM 快速上手](../02-quick-start/pwm.md)
