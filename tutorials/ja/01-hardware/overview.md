---
title: "ハードウェア概要：構造、CAD、組み立て"
description: "AmazingHand の機械構造、CAD/STL/STEP、組み立てと 3D プリントのリソース。"
version: both
---

# ハードウェア概要

2 つのサーボ構成は同じハンド構造を共用します。違いはサーボの型番、ドライバ基板、配線です。ハンドを組み立てる前に、選択した版を確認してください。

## 機械構造

- 指 4 本、各指 2 自由度：屈伸（flexion/extension）+ 開き（abduction/adduction）。
- 各指は 2 つのサーボが並列リンク機構で差動駆動し、すべてのサーボは手部に搭載されます。
- 3D プリントの外装、リンク、柔軟な指関節。手全体で約 400 g。
- オリジナルの手首インターフェースは Reachy 2 の Orbita 3D に対応し、他のロボットアームへ独自に変換することもできます。

## CAD とモデル

- STL / STEP ファイル：[`AmazingHand-main/cad/`](../../../AmazingHand-main/cad/)
- Onshape のオンラインドキュメントと URDF：[`AmazingHand-main/README_CN.md`](../../../AmazingHand-main/README_CN.md) の CAD の章を参照。

## 組み立てと 3D プリント

- [組み立てガイド PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [3D プリントの推奨事項 PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand 概要 PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)

> 組み立て前にハンドを中間位置に合わせ、サーボホーンも中間位置に合わせて取り付けます。2 つのサーボはサーボホーン／スプラインとストロークが異なるため、混用できません。

## 2 つのハードウェアの配線

| 版 | 配線と給電ガイド |
|------|----------------|
| SCS0009 シリアルバス | [SCS0009 配線、ID、給電](scs0009.md) |
| PWM（ESP32-S3） | [PWM 配線、GPIO、給電](pwm.md) |
| カメラキット | [カメラキットの取り付け](camera-kit.md) |

## 次のステップ

- [バージョン比較と選定](../00-product/version-comparison.md)
- [クイックスタート：SCS0009](../02-quick-start/scs0009.md) · [クイックスタート：PWM](../02-quick-start/pwm.md)
