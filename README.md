English | [简体中文](README_CN.md)

# AmazingHand

![AmazingHand](AmazingHand-main/assets/AmazingHand_Couv.jpg)

AmazingHand is an open-source, 3D-printable humanoid robotic hand with **8 degrees of freedom across 4 fingers**. Every actuator sits inside the hand — no cables running to the forearm — for roughly 400 g and under €200 in parts.

This repository gathers the original mechanical design and firmware from the [Pollen Robotics](https://github.com/pollen-robotics/AmazingHand) project together with the control software and servo tooling developed by Juxi Technology.

## 📦 Contents

| Folder | Description | README |
|--------|-------------|--------|
| **`AmazingHand-main/`** | Original design: STL/STEP CAD files, Arduino & Python examples, demos (control, simulation, hand tracking), assembly and 3D-printing guides, BOM | [English](AmazingHand-main/README.md) · [简体中文](AmazingHand-main/README_CN.md) |
| **`AmazingHandControl/`** | Python control tools: Tkinter GUI and CLI for calibration, pose presets, sequences and live servo control | [English](AmazingHandControl/README.md) · [简体中文](AmazingHandControl/README_CN.md) |
| **`SCS0009_ServoController/`** | SCS0009 servo debug tool: PySide6 GUI to scan the bus, read and write all 44 registers, change baud rate, factory reset, and back up parameters as `.xdat` | [English](SCS0009_ServoController/README.md) · [简体中文](SCS0009_ServoController/README_CN.md) |

## 🔧 Hardware

- 8 × Feetech **SCS0009** servos (potentiometer feedback, 10-bit resolution, 0–1023)
- External 5 V / 2 A power supply
- Serial bus adapter, or an Arduino with a Feetech TTL Linker
- 3D-printed parts — see the [BOM](AmazingHand-main/README.md#bom-bill-of-materials)

Each finger is driven by a parallel mechanism: two SCS0009 servos move it in flexion/extension and abduction/adduction.

## 📖 Documentation

- [Assembly guide](AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [3D printing tips](AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand overview](AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [Chinese BOM](https://docs.google.com/spreadsheets/d/1fHZiTky79vyZwICj5UGP2c_RiuLLm89K8HrB3vpb2h4/edit?gid=837395814#gid=837395814)

## 📄 License & attribution

- Software: [Apache License 2.0](AmazingHand-main/LICENSE)
- Mechanical design: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- `SCS0009_ServoController/`: [MIT](SCS0009_ServoController/LICENSE)

Based on [AmazingHand](https://github.com/pollen-robotics/AmazingHand) by Pollen Robotics.
