---
title: "Hardware Overview: Mechanics, CAD and Assembly"
description: "AmazingHand mechanics, CAD/STL/STEP, assembly and 3D printing resources."
version: both
---

# Hardware Overview

The two servo options share the same hand mechanics; the differences are the servo model, driver board and wiring. Confirm which version you have before assembling the hand.

## Mechanical structure

- 4 fingers, each with 2 degrees of freedom: flexion/extension + abduction/adduction.
- Each finger is driven differentially by two servos through a parallel mechanism, and all servos are mounted in the hand.
- 3D-printed shell, linkages and soft finger joints; the whole hand weighs about 400 g.
- The original wrist interface fits Reachy 2's Orbita 3D, and can also be adapted to other robot arms.

## CAD and models

- STL / STEP files: [`AmazingHand-main/cad/`](../../../AmazingHand-main/cad/)
- Onshape online document and URDF: see the CAD section of [`AmazingHand-main/README_CN.md`](../../../AmazingHand-main/README_CN.md).

## Assembly and 3D printing

- [Assembly guide PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [3D printing tips PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand overview PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)

> Before assembly, set the hand to its middle position and install the servo horns at the middle position; the two servo options have different servo horns/splines and travel ranges, so they cannot be mixed.

## Wiring for the two hardware options

| Version | Wiring and power guide |
|------|----------------|
| SCS0009 serial bus | [SCS0009 wiring, ID and power](scs0009.md) |
| PWM (ESP32-S3) | [PWM wiring, GPIO and power](pwm.md) |
| Camera kit | [Camera kit installation](camera-kit.md) |

## Next steps

- [Version comparison and selection](../00-product/version-comparison.md)
- [Quick start: SCS0009](../02-quick-start/scs0009.md) · [Quick start: PWM](../02-quick-start/pwm.md)
