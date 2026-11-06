# AmazingHand PWM-Servo-Edition — Schnellstart

Steuere den AmazingHand mit einem **ESP32-S3 und 8 PWM-Servos**. Die vollständigen Handbücher findest du in diesem `docs/`-Ordner.

## Hardware

| Element | Modell |
|------|-------|
| Steuerung | ESP32-S3-Dev-Board (YX-ESP32-S3 oder gleichwertig) |
| Servos | 8 PWM-Servos — Firmware kalibriert für **digitale Servos PTK 7452 MG-D (333 Hz)** |
| Adapter | PWM-Servo-Breakout-Board |
| Stromversorgung | 5 V / 3 A, gemeinsame Masse mit dem ESP32 |

> SG90 und andere analoge 50-Hz-Servos sind **kein** direkter Ersatz für die 333-Hz-Firmware.

| Kanal | GPIO | Gelenk | Kanal | GPIO | Gelenk |
|---------|------|-------|---------|------|-------|
| PWM1 | 4 | Zeigefinger 1 | PWM5 | 15 | Ringfinger 1 |
| PWM2 | 5 | Zeigefinger 2 | PWM6 | 16 | Ringfinger 2 |
| PWM3 | 6 | Mittelfinger 1 | PWM7 | 17 | Daumen 1 |
| PWM4 | 7 | Mittelfinger 2 | PWM8 | 18 | Daumen 2 |

## 1. Firmware flashen

Mit ESP-IDF:

```bash
cd firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

Mit dem vorgefertigten Image und `esptool`:

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  firmware/prebuilt/amazinghand_pwm.bin
```

Die serielle Schnittstelle läuft mit **115200-8N1** und gibt ein Startbanner aus.

## 2. Die Hand steuern

Desktop-GUI:

```bash
pip install -r tools/requirements.txt
python tools/hand_gui.py
```

Die Kameranachverfolgung benötigt die zusätzliche Umgebung, die von `tools/setup_tracking.bat` erstellt wird, danach:

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

Websteuerung: Öffne die Seite `Amazinghand-web-io/` des Repositorys (oder führe `Amazinghand-web/server.py --driver pwm` aus), wähle den Treiber **PWM (ESP32-S3)**, wähle den seriellen Port des ESP32 und stelle die Verbindung her.

## 3. Vollständige Dokumentation

| Dokument | Inhalt |
|----------|----------|
| [`../en/user_manual.md`](../en/user_manual.md) / [`../zh-hans/用户手册.md`](../zh-hans/用户手册.md) | Protokoll, Befehlsreferenz, Verkabelung, Kalibrierung, FAQ |
| [`../en/full_workflow.md`](../en/full_workflow.md) / [`../zh-hans/全流程使用教程.md`](../zh-hans/全流程使用教程.md) | Durchgängiger Workflow |
| [`../en/gui_usage.md`](../en/gui_usage.md) / [`../zh-hans/使用教程.md`](../zh-hans/使用教程.md) | GUI und serielles Testwerkzeug |
| [`../en/hand_tracking.md`](../en/hand_tracking.md) / [`../zh-hans/手势追踪教程.md`](../zh-hans/手势追踪教程.md) | MediaPipe-Handtracking |

## 4. Häufige Probleme

- **Keine Antwort**: Prüfen Sie die Baudrate 115200, den COM-Port des ESP32, die Stromversorgung mit 5 V / 3 A und die gemeinsame Masse. Die Seite wiederholt den NOP-Handshake automatisch.
- **Servo bewegt sich nicht / zittert**: Stellen Sie sicher, dass es sich um ein digitales 333-Hz-Servo handelt und die Stromversorgung ausreichend ist.
- **Richtung vertauscht**: Setzen Sie `scale` des entsprechenden Fingers in `Amazinghand-web-io/config.json` unter `pwm.calibration` auf `-1`.
- **Mittelstellung falsch**: Passen Sie `offset_deg` für diesen Kanal an.
- **Status „Beschäftigt“**: Die Firmware führt eine integrierte Geste aus; warten Sie oder senden Sie Stopp (`0xFF`).
