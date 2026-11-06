# NOTICE — AmazingHand PWM Servo Edition

This module is part of the `Juxi-Technology/AmazingHand` repository and is
distributed under the Apache License 2.0 (see `../AmazingHand-main/LICENSE`).

本模块是 `Juxi-Technology/AmazingHand` 仓库的一部分，随仓库以 Apache License 2.0 分发
（许可证见 `../AmazingHand-main/LICENSE`）。

## 1. Origin of this module / 模块来源

Firmware, host tools and Chinese documentation were developed by Juxi Technology
(钜犀科技) for the PWM servo product line and are mirrored from the Gitee
repository `white-leaf-tee/amazinghand-pwm-gpio`.

- Upstream commits mirrored: `97d8362`, `95a6903`, `57a67dc` plus the delivered
  componentized firmware and `delivery_package` working tree.
- The upstream PWM project did not ship a standalone LICENSE file. It is
  included here under this repository's Apache License 2.0; if the copyright
  holder has different terms, those terms take precedence.

本模块的固件、上位机工具与中文文档由钜犀科技为 PWM 舵机产品线开发，取自 Gitee 仓库
`white-leaf-tee/amazinghand-pwm-gpio`。原 PWM 项目未附带独立 LICENSE 文件，现按本仓库
的 Apache License 2.0 收录；如版权方另有许可要求，以其为准。

## 2. Upstream AmazingHand / 上游 AmazingHand

Mechanical design and the original hand project come from Pollen Robotics:

- Project: <https://github.com/pollen-robotics/AmazingHand>
- Software: Apache License 2.0
- Mechanical design: Creative Commons Attribution 4.0 (CC BY 4.0)

机械设计与原始灵巧手项目来自 Pollen Robotics（链接同上）：软件 Apache 2.0，机械设计 CC BY 4.0。

## 3. Third-party dependencies / 第三方依赖

| Component | Used by | License / note |
|-----------|---------|----------------|
| ESP-IDF | `firmware/AmazingHand_Serial` | Apache 2.0; framework is not bundled |
| pyserial | `tools/*.py`, `Amazinghand-web/server.py` | BSD 3-Clause; runtime dependency |
| MediaPipe | `tools/hand_tracking.py` | Apache 2.0; not bundled |
| OpenCV / NumPy / SciPy / Pillow | `tools/hand_tracking.py` | Runtime dependencies, not bundled |

## 4. Data and assets / 数据与资源

The ESP32 board schematic PDF (`firmware/esp32_devkitc_v4-sch.pdf`) is
Espressif's publicly available ESP32-DevKitC V4 schematic, included for wiring
reference.

`firmware/esp32_devkitc_v4-sch.pdf` 为乐鑫公开的 ESP32-DevKitC V4 开发板电路图，用于接线参考。
