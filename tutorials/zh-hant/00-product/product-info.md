---
title: "AmazingHand 產品資料"
description: "AmazingHand 靈巧手產品資料：機械結構、尺寸、負載、兩套伺服馬達方案與開源資源。"
version: both
---

# AmazingHand 產品資料

AmazingHand 是一款開源、可 3D 列印的仿人靈巧手，面向具身智能研究、機器人教育和人機互動原型。機械手本體相同，目前提供 **SCS0009 序列匯流排伺服馬達** 和 **PWM 伺服馬達（ESP32-S3）** 兩套硬體方案。

## 機械結構

- **4 根手指、8 個自由度**：每根手指 2 個自由度（屈伸 + 收展），由兩個伺服馬達透過並聯機構差動驅動。
- **驅動器內建**：所有伺服馬達安裝在手部，不需要向前臂引出線纜。
- **3D 列印**：外殼和連桿可列印，整隻手約 400 g。
- **雙手支援**：可單獨使用左手或右手，也可雙手機器人協同。
- **腕部介面**：原版設計適配 Reachy 2 的 Orbita 3D 腕部，也可轉接其他機械臂。

## 基礎參數

| 參數 | 規格 |
|------|------|
| 重量 | 約 0.416 kg |
| 手指數量 | 4 |
| 單指自由度 | 2 DoF |
| 伸展高度（不含底座） | 195 mm |
| 手掌寬度 | 105 mm |
| 手掌厚度 | 約 90 mm |
| 食指與拇指最大張開距離 | 180 mm |
| 單指負重 | 約 0.2 kg |
| 四指緊握最大負重 | 約 0.5 kg |

> 負載、電壓和伺服馬達參數隨所選伺服馬達版本不同；完整對照見 [版本比較與選型](version-comparison.md)。

## 兩套硬體方案

| 項目 | SCS0009 序列匯流排版 | PWM 伺服馬達版 |
|------|--------------------|------------|
| 伺服馬達 | 飛特 SCS0009 ×8 | PTK 7452 MG-D 數位 PWM 伺服馬達 ×8 |
| 控制 | 電腦/樹莓派 + 匯流排驅動板 | ESP32-S3 板載韌體 |
| 回饋 | 位置/速度/電壓/溫度回讀 | 無回讀 |
| 適用 | 精度、資料採集、LeRobot / SO-ARM101 | 獨立演示、手勢互動、快速上手 |

## 軟體生態

- **網頁控制**：瀏覽器滑桿、19 個預設姿態、MediaPipe 攝影機遙操作，支援 SCS0009 / PWM 驅動切換。
- **桌面上位機**：SCS0009 使用 `AmazingHandControl`（Tkinter GUI + CLI）；PWM 使用 `AmazingHand-PWM/tools/hand_gui.py`。
- **手勢追蹤**：SCS0009 提供官方 dora + MuJoCo IK Demo；PWM 提供 GUI 內建 MediaPipe 追蹤。
- **開源資源**：CAD、組裝/列印文件、Arduino/Python 範例均在儲存庫中。

## 開源資源

- [組裝指南 PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [3D 列印建議 PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand 概覽 PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [CAD / STL / STEP](../../../AmazingHand-main/cad/)
- [官方上游專案（Pollen Robotics）](https://github.com/pollen-robotics/AmazingHand)

## 下一步

- [版本比較與選型](version-comparison.md)
- [硬體總覽](../01-hardware/overview.md)
- [SCS0009 快速上手](../02-quick-start/scs0009.md)
- [PWM 快速上手](../02-quick-start/pwm.md)
