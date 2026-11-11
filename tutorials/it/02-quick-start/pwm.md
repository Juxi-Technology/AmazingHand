---
title: "Avvio rapido PWM"
description: "Percorso più breve per la versione con servo PWM di AmazingHand: cablaggio, flashing del firmware, GUI desktop o controllo web, primo movimento."
version: pwm
---

# Avvio rapido PWM

Adatta alla versione con ESP32-S3 + 8 servo PWM. Per le istruzioni complete vedi i link ai vari capitoli.

## 1. Cablaggio

- Inserire gli 8 servo PWM nei servo 1–8 della scheda adattatrice secondo la numerazione.
- Collegare PWM1–8 della scheda adattatrice ai GPIO 4, 5, 6, 7, 15, 16, 17, 18 dell'ESP32-S3.
- Collegare 5 V/GND della scheda adattatrice all'alimentazione 5 V/3 A, con massa comune all'ESP32.
- Cablaggio dettagliato: [Cablaggio, GPIO e alimentazione PWM](../01-hardware/pwm.md).

> I servo devono essere **servo digitali PTK 7452 MG-D (333 Hz)** o equivalenti; servo analogici a 50 Hz come l'SG90 non possono essere sostituiti direttamente.

## 2. Flashing del firmware

### Metodo A: bin precompilato (consigliato)

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  AmazingHand-PWM/firmware/prebuilt/amazinghand_pwm.bin
```

### Metodo B: compilazione con ESP-IDF

```bash
cd AmazingHand-PWM/firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

Struttura del progetto firmware:

```text
firmware/AmazingHand_Serial/
├── main/main.c                  Attività FreeRTOS, coda dei comandi e inizializzazione
└── components/
    ├── hand_servo/              Driver PWM LEDC e calibrazione dei servo
    ├── hand_gestures/           Macro dei parametri dei gesti e funzioni dei gesti
    └── hand_protocol/           Analisi dei frame seriali e smistamento dei comandi
```

> La compilazione con ESP-IDF non supporta percorsi con caratteri cinesi: sia la directory del progetto sia quella utente devono usare caratteri inglesi; si consigliano ESP-IDF v5.x / v6.x e il chip target **ESP32-S3**.

All'accensione la seriale dovrebbe stampare:

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

## 3. Connessione al PC host

| Modalità | Accesso |
|------|------|
| GUI desktop | [Applicazione desktop PWM](../04-desktop/pwm.md): `python AmazingHand-PWM/tools/hand_gui.py` |
| Controllo web | [Controllo web PWM](../03-web-control/pwm.md): seleziona il driver **PWM (ESP32-S3)**, seriale 115200 |
| Test da riga di comando | `python AmazingHand-PWM/tools/serial_test.py COM3 nop` |

## 4. Primo movimento

1. Dopo la connessione il firmware torna prima in posizione centrale (90°); verificare che non ci siano rumori anomali/inceppamenti.
2. Con lo slider di un singolo dito verificare uno per uno direzione e posizione centrale.
3. Provare poi pose di piccola ampiezza come «apri / pugno».
4. Se la direzione è invertita o la posizione centrale è sfalsata, regolare secondo [Protocollo e calibrazione PWM](../06-servo-tuning/pwm.md).

## Passi successivi

- [Protocollo e calibrazione PWM](../06-servo-tuning/pwm.md)
- [Tracciamento delle mani PWM](../05-hand-tracking/pwm.md)
- [Confronto tra versioni e scelta](../00-product/version-comparison.md)
