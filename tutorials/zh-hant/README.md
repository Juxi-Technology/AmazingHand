---
title: "AmazingHand 靈巧手教學總覽"
description: "AmazingHand 靈巧手統一教學入口：SCS0009 序列匯流排伺服馬達版與 PWM 伺服馬達版的產品選型、硬體接線、快速上手、網頁控制、桌面上位機、手勢追蹤、伺服馬達調校和 FAQ。"
version: both
---

# AmazingHand 靈巧手教學

AmazingHand 是一款開源、可 3D 列印的仿人靈巧手：4 根手指、8 個自由度，所有驅動器內建於手部，整隻手約 400 g。目前提供兩套硬體方案，機械手結構相同，伺服馬達、驅動板和通訊方式不同。

## 先選版本

| 對比項目 | SCS0009 序列匯流排版 | PWM 伺服馬達版 |
|--------|--------------------|------------|
| 推薦場景 | 精確角度控制、資料回讀、接入 SO-ARM101 / LeRobot 資料採集訓練 | 獨立演示、手勢互動、網頁/桌面快速上手 |
| 伺服馬達 | 飛特 SCS0009 序列匯流排伺服馬達 ×8 | PTK 7452 MG-D **數位** PWM 伺服馬達 ×8 |
| 伺服馬達參數 | 2.3 kg·cm@6V，300° 可控，0.293° 精度 | 4.5 kg·cm@7.4V（5V 供電約 2.8–3 kg·cm），180°±10°，333 Hz |
| 位置/溫度/電壓回饋 | ✅ 支援 | ❌ 無回讀，無法偵測堵轉或失步 |
| 主控 | 無板載，電腦/樹莓派透過匯流排驅動板直連 | ESP32-S3 板載韌體 |
| 供電 | 7–12V（DC5521）輸入驅動板 | 5V / 3A 以上，必須共地 |
| 通訊 | 1,000,000 鮑率匯流排協定 | 上位機↔ESP32 序列埠 **115200**（伺服馬達本身無鮑率） |
| 伺服馬達 ID | 必須設定：右手 1–8，左手 11–18 | 不設 ID，固定通道 CH1–CH8：食指 1/2、中指 3/4、無名指 5/6、拇指 7/8 |
| 韌體 | 無需燒錄 | 需要 ESP-IDF 編譯，或直接燒錄預編譯 bin |

> 需要**位置回讀、精度或 LeRobot 訓練資料採集**，選 SCS0009；只需要**獨立演示、手勢互動、快速上手**，選 PWM。

完整對比與選型說明見 [版本比較](00-product/version-comparison.md)。

## 依使用方式導覽

| 使用方式 | SCS0009 序列匯流排版 | PWM 伺服馬達版 |
|----------|--------------------|------------|
| 快速上手 | [SCS0009 快速上手](02-quick-start/scs0009.md) | [PWM 快速上手](02-quick-start/pwm.md) |
| 網頁控制 | [SCS0009 網頁控制](03-web-control/scs0009.md) | [PWM 網頁控制](03-web-control/pwm.md) |
| 桌面上位機 / CLI | [SCS0009 GUI 與 CLI](04-desktop/scs0009.md) | [PWM 桌面上位機](04-desktop/pwm.md) |
| 手勢追蹤 | [SCS0009 官方 Demo](05-hand-tracking/scs0009.md) | [PWM GUI / dora 追蹤](05-hand-tracking/pwm.md) |
| 伺服馬達調校與標定 | [SCS0009 調校與標定](06-servo-tuning/scs0009.md) | [PWM 協定與標定](06-servo-tuning/pwm.md) |
| Arduino / 二次開發 | [Arduino Nano](07-arduino/arduino-nano.md) · [範例程式](07-arduino/examples.md) | 同左（共用機械結構） |

網頁控制總覽（驅動切換、序列埠欄、介面說明）見 [網頁控制 README](03-web-control/README.md)。

## 開始之前

- [產品資料](00-product/product-info.md) — 參數、定位、資料
- [版本比較與選型](00-product/version-comparison.md) — 兩套硬體的完整差異
- [硬體總覽](01-hardware/overview.md) — 結構、CAD、組裝、3D 列印
- [SCS0009 接線](01-hardware/scs0009.md) / [PWM 接線](01-hardware/pwm.md)
- [攝影機套件安裝](01-hardware/camera-kit.md)
- [下載與資源](00-product/downloads.md)

## 安全提示

- 外部伺服馬達電源與 ESP32/驅動板必須**共地**。
- 首次上電前把機械手擺到中位，伺服馬達臂按中位安裝，避免頂到行程盡頭。
- SCS0009 與 PWM 兩套硬體**同一時刻只接一套**，不要混接。
- PWM 伺服馬達無位置回饋，急停只能中止手勢，不能像匯流排伺服馬達一樣讀取或釋放力矩。

## Languages

[简体中文](../zh-hans/README.md) | [English](../en/README.md) | [Deutsch](../de/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (BR)](../pt-br/README.md) | [Português (PT)](../pt-pt/README.md) | [繁體中文](../zh-hant/README.md)
