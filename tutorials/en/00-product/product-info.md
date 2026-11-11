---
title: "AmazingHand Product Information"
description: "AmazingHand dexterous hand product information: mechanics, dimensions, payload, the two servo options and open-source resources."
version: both
---

# AmazingHand Product Information

AmazingHand is an open-source, 3D-printable humanoid dexterous hand aimed at embodied-intelligence research, robotics education and human-robot interaction prototypes. The hand body is the same; two hardware options are currently offered: **SCS0009 serial bus servos** and **PWM servos (ESP32-S3)**.

## Mechanical structure

- **4 fingers, 8 degrees of freedom**: each finger has 2 DoF (flexion/extension + abduction/adduction), driven differentially by two servos through a parallel mechanism.
- **Actuators built in**: all servos are mounted in the hand; no cables need to run to the forearm.
- **3D printable**: the shell and linkages can be printed; the whole hand weighs about 400 g.
- **Both hands supported**: use the left or right hand alone, or two hands together on a robot.
- **Wrist interface**: the original design fits Reachy 2's Orbita 3D wrist, and can be adapted to other robot arms.

## Basic specifications

| Parameter | Specification |
|------|------|
| Weight | about 0.416 kg |
| Number of fingers | 4 |
| DoF per finger | 2 DoF |
| Extended height (excluding base) | 195 mm |
| Palm width | 105 mm |
| Palm thickness | about 90 mm |
| Maximum span between index finger and thumb | 180 mm |
| Load per finger | about 0.2 kg |
| Maximum load with four fingers clenched | about 0.5 kg |

> Payload, voltage and servo parameters depend on the servo version chosen; for the full comparison, see [Version comparison and selection](version-comparison.md).

## Two hardware options

| Item | SCS0009 serial bus version | PWM servo version |
|------|--------------------|------------|
| Servos | Feetech SCS0009 ×8 | PTK 7452 MG-D digital PWM servo ×8 |
| Control | PC/Raspberry Pi + bus driver board | ESP32-S3 onboard firmware |
| Feedback | position/speed/voltage/temperature readback | no readback |
| Suited for | precision, data collection, LeRobot / SO-ARM101 | standalone demos, gesture interaction, quick start |

## Software ecosystem

- **Web control**: browser sliders, 19 preset poses, MediaPipe camera teleoperation, with SCS0009 / PWM driver switching.
- **Desktop host software**: SCS0009 uses `AmazingHandControl` (Tkinter GUI + CLI); PWM uses `AmazingHand-PWM/tools/hand_gui.py`.
- **Hand tracking**: SCS0009 offers the official dora + MuJoCo IK demo; PWM offers MediaPipe tracking built into the GUI.
- **Open-source resources**: CAD, assembly/printing documentation and Arduino/Python examples are all in the repository.

## Open-source resources

- [Assembly guide PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [3D printing tips PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand overview PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [CAD / STL / STEP](../../../AmazingHand-main/cad/)
- [Official upstream project (Pollen Robotics)](https://github.com/pollen-robotics/AmazingHand)

## Next steps

- [Version comparison and selection](version-comparison.md)
- [Hardware overview](../01-hardware/overview.md)
- [SCS0009 quick start](../02-quick-start/scs0009.md)
- [PWM quick start](../02-quick-start/pwm.md)
