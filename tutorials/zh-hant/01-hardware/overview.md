---
title: "硬體總覽：結構、CAD 與組裝"
description: "AmazingHand 機械結構、CAD/STL/STEP、組裝與 3D 列印資源。"
version: both
---

# 硬體總覽

兩套伺服馬達方案共用同一套機械手結構；差別在伺服馬達型號、驅動板和接線。組裝機械手前先確認所選版本。

## 機械結構

- 4 根手指，每根 2 個自由度：屈伸（flexion/extension）+ 收展（abduction/adduction）。
- 每根手指由兩個伺服馬達透過並聯機構差動驅動，所有伺服馬達安裝在手部。
- 3D 列印外殼、連桿和軟性指節；整隻手約 400 g。
- 原版腕部介面適配 Reachy 2 的 Orbita 3D，也可自行轉接其他機械臂。

## CAD 與模型

- STL / STEP 檔案：[`AmazingHand-main/cad/`](../../../AmazingHand-main/cad/)
- Onshape 線上文件與 URDF：見 [`AmazingHand-main/README_CN.md`](../../../AmazingHand-main/README_CN.md) 的 CAD 章節。

## 組裝與 3D 列印

- [組裝指南 PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [3D 列印建議 PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand 概覽 PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)

> 組裝前先把機械手擺到中位，伺服馬達臂按中位安裝；兩套伺服馬達的伺服馬達臂/花鍵和行程不同，不能混用。

## 兩套硬體接線

| 版本 | 接線與供電指南 |
|------|----------------|
| SCS0009 序列匯流排 | [SCS0009 接線、ID 與供電](scs0009.md) |
| PWM（ESP32-S3） | [PWM 接線、GPIO 與供電](pwm.md) |
| 攝影機套件 | [攝影機套件安裝](camera-kit.md) |

## 下一步

- [版本比較與選型](../00-product/version-comparison.md)
- [快速上手：SCS0009](../02-quick-start/scs0009.md) · [快速上手：PWM](../02-quick-start/pwm.md)
