---
title: "AmazingHand 製品資料"
description: "AmazingHand 多指ハンドの製品資料：機械構造、寸法、負荷、2 つのサーボ構成、オープンソースリソース。"
version: both
---

# AmazingHand 製品資料

AmazingHand はオープンソースで 3D プリント可能なヒューマノイド型多指ハンドで、エンボディド AI 研究、ロボット教育、ヒューマンロボットインタラクションのプロトタイピングを対象としています。ハンド本体は共通で、現在 **SCS0009 シリアルバスサーボ**と **PWM サーボ（ESP32-S3）** の 2 つのハードウェア構成を提供しています。

## 機械構造

- **指 4 本、自由度 8**：各指 2 自由度（屈伸 + 開き）を、2 つのサーボが並列リンク機構で差動駆動します。
- **アクチュエータ内蔵**：すべてのサーボを手部に搭載し、前腕へケーブルを引き出す必要がありません。
- **3D プリント**：外装とリンクをプリントでき、手全体で約 400 g です。
- **両手対応**：左手または右手を単独で使うことも、両手ロボットとして協調させることもできます。
- **手首インターフェース**：オリジナル設計は Reachy 2 の Orbita 3D 手首に対応し、他のロボットアームへ変換することもできます。

## 基本仕様

| 項目 | 仕様 |
|------|------|
| 重量 | 約 0.416 kg |
| 指の本数 | 4 |
| 単指自由度 | 2 DoF |
| 伸展時の高さ（ベースを除く） | 195 mm |
| 手のひらの幅 | 105 mm |
| 手のひらの厚さ | 約 90 mm |
| 人差し指と親指の最大開き幅 | 180 mm |
| 単指の耐荷重 | 約 0.2 kg |
| 四指を握った状態の最大耐荷重 | 約 0.5 kg |

> 負荷、電圧、サーボ仕様は選択したサーボ版によって異なります。完全な対照表は [バージョン比較と選定](version-comparison.md) を参照してください。

## 2 つのハードウェア構成

| 項目 | SCS0009 シリアルバス版 | PWM サーボ版 |
|------|--------------------|------------|
| サーボ | Feetech SCS0009 ×8 | PTK 7452 MG-D デジタル PWM サーボ ×8 |
| 制御 | PC／Raspberry Pi + バスドライバ基板 | ESP32-S3 オンボードファームウェア |
| フィードバック | 位置／速度／電圧／温度の読み戻し | 読み戻しなし |
| 用途 | 精度、データ収集、LeRobot / SO-ARM101 | 単体デモ、ジェスチャー操作、クイックスタート |

## ソフトウェアエコシステム

- **ウェブコントロール**：ブラウザのスライダー、19 種のプリセットポーズ、MediaPipe カメラテレオペ。SCS0009 / PWM のドライバー切り替えに対応。
- **デスクトップツール**：SCS0009 は `AmazingHandControl`（Tkinter GUI + CLI）、PWM は `AmazingHand-PWM/tools/hand_gui.py` を使用。
- **ハンドトラッキング**：SCS0009 は公式 dora + MuJoCo IK Demo、PWM は GUI 内蔵の MediaPipe トラッキングを提供。
- **オープンソースリソース**：CAD、組み立て／プリントのドキュメント、Arduino／Python のサンプルはすべてリポジトリにあります。

## オープンソースリソース

- [組み立てガイド PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [3D プリントの推奨事項 PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand 概要 PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [CAD / STL / STEP](../../../AmazingHand-main/cad/)
- [公式アップストリームプロジェクト（Pollen Robotics）](https://github.com/pollen-robotics/AmazingHand)

## 次のステップ

- [バージョン比較と選定](version-comparison.md)
- [ハードウェア概要](../01-hardware/overview.md)
- [SCS0009 クイックスタート](../02-quick-start/scs0009.md)
- [PWM クイックスタート](../02-quick-start/pwm.md)
