---
title: "PWM 快速上手"
description: "AmazingHand PWM 伺服馬達版最短上手路徑：接線、燒錄韌體、桌面 GUI 或網頁控制、首次動作。"
version: pwm
---

# PWM 快速上手

適合 ESP32-S3 + 8 路 PWM 伺服馬達版本。完整說明見各章節連結。

## 1. 接線

- 8 個 PWM 伺服馬達按編號插到轉接板伺服馬達 1–8。
- 轉接板 PWM1–8 接 ESP32-S3 GPIO 4、5、6、7、15、16、17、18。
- 轉接板 5V/GND 接 5V/3A 電源，並與 ESP32 共地。
- 詳細接線：[PWM 接線、GPIO 與供電](../01-hardware/pwm.md)。

> 伺服馬達必須是 **PTK 7452 MG-D 數位伺服馬達（333 Hz）** 或同類；SG90 等 50 Hz 類比伺服馬達不能直接替換。

## 2. 燒錄韌體

### 方式 A：預編譯 bin（推薦）

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  AmazingHand-PWM/firmware/prebuilt/amazinghand_pwm.bin
```

### 方式 B：ESP-IDF 編譯

```bash
cd AmazingHand-PWM/firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

韌體專案結構：

```text
firmware/AmazingHand_Serial/
├── main/main.c                  FreeRTOS 任務、命令佇列與初始化
└── components/
    ├── hand_servo/              LEDC PWM 驅動與伺服馬達校準
    ├── hand_gestures/           手勢參數巨集與手勢函式
    └── hand_protocol/           序列埠幀解析與命令分發
```

> ESP-IDF 編譯不支援中文路徑：專案目錄和使用者目錄都要使用英文；建議 ESP-IDF v5.x / v6.x，目標晶片選 **ESP32-S3**。

上電後序列埠應印出：

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

## 3. 連接上位機

| 方式 | 入口 |
|------|------|
| 桌面 GUI | [PWM 桌面上位機](../04-desktop/pwm.md)：`python AmazingHand-PWM/tools/hand_gui.py` |
| 網頁控制 | [PWM 網頁控制](../03-web-control/pwm.md)：驅動選 **PWM（ESP32-S3）**，序列埠 115200 |
| 命令列測試 | `python AmazingHand-PWM/tools/serial_test.py COM3 nop` |

## 4. 首次動作

1. 連線後韌體會先回中位（90°），確認沒有異音/卡澀。
2. 用單指滑桿逐個確認方向和中位。
3. 再試「張開 / 握拳」等小範圍姿態。
4. 方向反了或中位偏了，按 [PWM 協定與標定](../06-servo-tuning/pwm.md) 調整。

## 下一步

- [PWM 協定與標定](../06-servo-tuning/pwm.md)
- [PWM 手勢追蹤](../05-hand-tracking/pwm.md)
- [版本比較與選型](../00-product/version-comparison.md)
