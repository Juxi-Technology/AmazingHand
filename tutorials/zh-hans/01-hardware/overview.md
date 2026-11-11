---
title: "硬件总览：结构、CAD 与组装"
description: "AmazingHand 机械结构、CAD/STL/STEP、组装与 3D 打印资源。"
version: both
---

# 硬件总览

两套舵机方案共用同一套机械手结构；区别在舵机型号、驱动板和接线。组装机械手前先确认所选版本。

## 机械结构

- 4 根手指，每根 2 个自由度：屈伸（flexion/extension）+ 收展（abduction/adduction）。
- 每根手指由两个舵机通过并联机构差动驱动，所有舵机安装在手部。
- 3D 打印外壳、连杆和软性指节；整手约 400 g。
- 原版腕部接口适配 Reachy 2 的 Orbita 3D，也可自行转接其他机械臂。

## CAD 与模型

- STL / STEP 文件：[`AmazingHand-main/cad/`](../../../AmazingHand-main/cad/)
- Onshape 在线文档与 URDF：见 [`AmazingHand-main/README_CN.md`](../../../AmazingHand-main/README_CN.md) 的 CAD 章节。

## 组装与 3D 打印

- [组装指南 PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [3D 打印建议 PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand 概览 PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)

> 组装前先把机械手摆到中位，舵机臂按中位安装；两套舵机的舵机臂/花键和行程不同，不能混用。

## 两套硬件接线

| 版本 | 接线与供电指南 |
|------|----------------|
| SCS0009 串口总线 | [SCS0009 接线、ID 与供电](scs0009.md) |
| PWM（ESP32-S3） | [PWM 接线、GPIO 与供电](pwm.md) |
| 相机套件 | [相机套件安装](camera-kit.md) |

## 下一步

- [版本对比与选型](../00-product/version-comparison.md)
- [快速上手：SCS0009](../02-quick-start/scs0009.md) · [快速上手：PWM](../02-quick-start/pwm.md)
