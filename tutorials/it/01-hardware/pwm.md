---
title: "Cablaggio, GPIO e alimentazione PWM"
description: "Versione con servo PWM di AmazingHand: ESP32-S3, 8 canali PWM, mappatura GPIO, alimentazione e descrizione del modello di servo."
version: pwm
---

# Cablaggio, GPIO e alimentazione PWM

Nella versione PWM è l'ESP32-S3 a generare direttamente gli 8 segnali PWM; il PC deve solo inviare comandi tramite la seriale USB.

## Distinta hardware

| Voce | Specifica |
|------|------|
| Controllore | Scheda di sviluppo ESP32-S3 (Youxin YX-ESP32-S3 o equivalente) |
| Servo | Servo PWM **digitale** PTK 7452 MG-D ×8 (333 Hz) |
| Scheda adattatrice | Scheda adattatrice per servo PWM (8 connettori 3P + 5 V/GND) |
| Alimentazione | 5 V / 3 A o più; massa comune obbligatoria tra scheda adattatrice ed ESP32 |

> Servo nominali 4,5 kg·cm@7,4 V; con l'alimentazione 5 V di questa soluzione la coppia effettiva è di circa 2,8–3 kg·cm.
>
> ⚠️ Servo analogici a 50 Hz come l'SG90 non possono sostituire direttamente il firmware a 333 Hz; per cambiare modello è necessario modificare insieme `LEDC_FREQ` e la calibrazione della larghezza d'impulso.

## Canale → GPIO → dito

| Canale | GPIO | Giunto | Canale | GPIO | Giunto |
|------|------|------|------|------|------|
| PWM1 / CH1 | 4 | Giunto 1 dell'indice | PWM5 / CH5 | 15 | Giunto 1 dell'anulare |
| PWM2 / CH2 | 5 | Giunto 2 dell'indice | PWM6 / CH6 | 16 | Giunto 2 dell'anulare |
| PWM3 / CH3 | 6 | Giunto 1 del medio | PWM7 / CH7 | 17 | Giunto 1 del pollice |
| PWM4 / CH4 | 7 | Giunto 2 del medio | PWM8 / CH8 | 18 | Giunto 2 del pollice |

- Il cablaggio è identico per mano destra e sinistra; l'indice è fisso su CH1/2.
- Per ogni dito la coppia di servo ha il canale dispari a destra e il pari a sinistra.
- Il numero di canale è fissato dal firmware; non è necessario impostare l'ID del servo.

## Procedura di cablaggio

1. Inserire i connettori 3P degli 8 servo nei pin header 1–8 della scheda adattatrice secondo la numerazione.
2. Collegare PWM1–PWM8 della scheda adattatrice ai GPIO 4, 5, 6, 7, 15, 16, 17, 18 dell'ESP32-S3.
3. Collegare 5 V/GND della scheda adattatrice all'alimentazione esterna 5 V/3 A.
4. Portare un'altra coppia 5 V/GND dalla scheda adattatrice all'ESP32-S3; **la massa comune è obbligatoria**.
5. Ordine dei fili 3P dei servo: marrone/nero GND, rosso V+, arancione/bianco/giallo segnale; inserire seguendo la serigrafia della scheda adattatrice, senza invertire.

## Alimentazione e sicurezza

- Quando gli 8 servo si muovono contemporaneamente la corrente è elevata; si consigliano 5 V/3 A o più, evitando di alimentare solo tramite USB.
- Prima della prima accensione portare la mano in posizione centrale e installare i bracci dei servo a 90°.
- I canali non collegati possono restare vuoti senza influire sugli altri; isolare i connettori vuoti.
- L'apertura della seriale può resettare l'ESP32; il firmware torna automaticamente in posizione centrale.

## Passi successivi

- [Avvio rapido PWM](../02-quick-start/pwm.md) (flashing del firmware + GUI/web)
- [Protocollo e calibrazione PWM](../06-servo-tuning/pwm.md)
- [Controllo web](../03-web-control/pwm.md)
