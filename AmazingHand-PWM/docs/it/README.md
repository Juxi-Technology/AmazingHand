# AmazingHand PWM Servo Edition — Guida rapida

Pilota l'AmazingHand con un **ESP32-S3 e 8 servo PWM**. I manuali completi sono in questa cartella `docs/`.

## Hardware

| Voce | Modello |
|------|-------|
| Controllore | Scheda di sviluppo ESP32-S3 (YX-ESP32-S3 o equivalente) |
| Servo | 8 servo PWM — firmware calibrato per **servo digitali PTK 7452 MG-D (333 Hz)** |
| Adattatore | Scheda breakout per servo PWM |
| Alimentazione | 5 V / 3 A, massa comune con l'ESP32 |

> Gli SG90 e gli altri servo analogici a 50 Hz **non** sono sostituti diretti per il firmware a 333 Hz.

| Canale | GPIO | Giunto | Canale | GPIO | Giunto |
|---------|------|-------|---------|------|-------|
| PWM1 | 4 | Indice 1 | PWM5 | 15 | Anulare 1 |
| PWM2 | 5 | Indice 2 | PWM6 | 16 | Anulare 2 |
| PWM3 | 6 | Medio 1 | PWM7 | 17 | Pollice 1 |
| PWM4 | 7 | Medio 2 | PWM8 | 18 | Pollice 2 |

## 1. Flash del firmware

Con ESP-IDF:

```bash
cd firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

Con l'immagine precompilata e `esptool`:

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  firmware/prebuilt/amazinghand_pwm.bin
```

La porta seriale funziona a **115200-8N1** e stampa un banner di avvio.

## 2. Controllo della mano

GUI desktop:

```bash
pip install -r tools/requirements.txt
python tools/hand_gui.py
```

Il tracciamento tramite telecamera richiede l'ambiente aggiuntivo creato da `tools/setup_tracking.bat`, quindi:

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

Controllo web: apri la pagina `Amazinghand-web-io/` del repository (oppure esegui `Amazinghand-web/server.py --driver pwm`), seleziona il driver **PWM (ESP32-S3)**, scegli la porta seriale dell'ESP32 e connetti.

## 3. Documentazione completa

| Documento | Contenuti |
|----------|----------|
| [`../en/user_manual.md`](../en/user_manual.md) / [`../zh-hans/用户手册.md`](../zh-hans/用户手册.md) | Protocollo, riferimento dei comandi, cablaggio, calibrazione, FAQ |
| [`../en/full_workflow.md`](../en/full_workflow.md) / [`../zh-hans/全流程使用教程.md`](../zh-hans/全流程使用教程.md) | Flusso di lavoro end-to-end |
| [`../en/gui_usage.md`](../en/gui_usage.md) / [`../zh-hans/使用教程.md`](../zh-hans/使用教程.md) | GUI e strumento di test seriale |
| [`../en/hand_tracking.md`](../en/hand_tracking.md) / [`../zh-hans/手势追踪教程.md`](../zh-hans/手势追踪教程.md) | Tracciamento delle mani con MediaPipe |

## 4. Problemi comuni

- **Nessuna risposta**: controlla i 115200 baud, la porta COM dell'ESP32, l'alimentazione 5 V / 3 A e la massa comune. La pagina ritenta automaticamente l'handshake NOP.
- **Il servo non si muove / trema**: verifica che il servo sia un servo digitale a 333 Hz e che l'alimentazione sia adeguata.
- **Direzione invertita**: imposta `scale` del dito corrispondente a `-1` in `Amazinghand-web-io/config.json` sotto `pwm.calibration`.
- **Posizione centrale errata**: regola `offset_deg` per quel canale.
- **Stato occupato**: il firmware sta eseguendo un gesto integrato; attendi o invia stop (`0xFF`).
