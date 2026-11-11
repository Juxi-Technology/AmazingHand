---
title: "PWM-Schnellstart"
description: "Kürzester Einstieg in die AmazingHand PWM-Servo-Version: Verkabelung, Firmware flashen, Desktop-GUI oder Websteuerung, erste Bewegung."
version: pwm
---

# PWM-Schnellstart

Geeignet für die Version mit ESP32-S3 + 8 PWM-Servos. Vollständige Erläuterungen findest du über die Links der einzelnen Kapitel.

## 1. Verkabelung

- Die 8 PWM-Servos nach Nummer an die Servo-Stiftleisten 1–8 der Adapterplatine stecken.
- PWM1–8 der Adapterplatine mit GPIO 4, 5, 6, 7, 15, 16, 17, 18 des ESP32-S3 verbinden.
- 5 V/GND der Adapterplatine mit einer 5-V/3-A-Stromversorgung verbinden und gemeinsame Masse mit dem ESP32 herstellen.
- Detaillierte Verkabelung: [PWM-Verkabelung, GPIO und Stromversorgung](../01-hardware/pwm.md).

> Der Servo muss ein **digitaler PTK 7452 MG-D (333 Hz)** oder gleichwertig sein; analoge 50-Hz-Servos wie SG90 können nicht direkt ersetzt werden.

## 2. Firmware flashen

### Variante A: vorkompilierte bin (empfohlen)

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  AmazingHand-PWM/firmware/prebuilt/amazinghand_pwm.bin
```

### Variante B: ESP-IDF kompilieren

```bash
cd AmazingHand-PWM/firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

Firmware-Projektstruktur:

```text
firmware/AmazingHand_Serial/
├── main/main.c                  FreeRTOS-Aufgaben, Befehlswarteschlange und Initialisierung
└── components/
    ├── hand_servo/              LEDC-PWM-Treiber und Servo-Kalibrierung
    ├── hand_gestures/           Geste-Parameter-Makros und Geste-Funktionen
    └── hand_protocol/           Seriell-Frame-Parsing und Befehlsverteilung
```

> ESP-IDF unterstützt keine chinesischen Pfade: Projekt- und Benutzerverzeichnis müssen englische Namen verwenden; empfohlen wird ESP-IDF v5.x / v6.x, Zielchip **ESP32-S3**.

Nach dem Einschalten sollte die serielle Schnittstelle ausgeben:

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

## 3. Mit der PC-Software verbinden

| Art | Einstieg |
|------|------|
| Desktop-GUI | [PWM-Desktop-GUI](../04-desktop/pwm.md): `python AmazingHand-PWM/tools/hand_gui.py` |
| Websteuerung | [PWM-Websteuerung](../03-web-control/pwm.md): Treiber **PWM (ESP32-S3)** wählen, seriell 115200 |
| Kommandozeilentest | `python AmazingHand-PWM/tools/serial_test.py COM3 nop` |

## 4. Erste Bewegung

1. Nach dem Verbinden fährt die Firmware zuerst in die Mittelstellung (90°); prüfe, dass keine ungewöhnlichen Geräusche/Klemmer auftreten.
2. Mit den Schiebereglern einzelner Finger Richtung und Mittelstellung nacheinander prüfen.
3. Dann kleine Preset-Posen wie „Öffnen / Faust" ausprobieren.
4. Wenn die Richtung vertauscht oder die Mittelstellung verschoben ist, nach [PWM-Protokoll und Kalibrierung](../06-servo-tuning/pwm.md) anpassen.

## Nächste Schritte

- [PWM-Protokoll und Kalibrierung](../06-servo-tuning/pwm.md)
- [PWM-Handtracking](../05-hand-tracking/pwm.md)
- [Versionsvergleich und Auswahl](../00-product/version-comparison.md)
