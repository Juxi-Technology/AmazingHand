---
title: "Confronto e scelta tra versioni SCS0009 e PWM"
description: "Confronto completo delle due soluzioni hardware AmazingHand: servo, retroazione, controllore, alimentazione, comunicazione, ID/canali, firmware e scenari d'uso."
version: both
---

# Confronto e scelta tra versioni SCS0009 e PWM

La struttura della mano meccanica di AmazingHand è identica, ma esistono due soluzioni per i servo. La scelta dipende principalmente dalla necessità di **retroazione di posizione, controllo preciso dell'angolo e acquisizione dati**.

## Conclusione rapida

- **Scegli SCS0009**: se servono lettura di posizione/temperatura/tensione, angoli precisi e integrazione con il braccio robotico SO-ARM101 per l'acquisizione e l'addestramento dati LeRobot.
- **Scegli PWM**: per dimostrazioni autonome, interazione gestuale e avvio rapido con web/desktop, senza necessità di retroazione.
- **Non mescolare**: collegare una sola soluzione hardware alla volta; alimentazione, protocollo e firmware sono diversi.

## Confronto completo

| Voce di confronto | Versione bus seriale SCS0009 | Versione con servo PWM |
|--------|--------------------|------------|
| Motivo consigliato | Controllo preciso dell'angolo + lettura dei dati; integrabile con il braccio robotico SO-ARM101 per l'acquisizione e l'addestramento dati LeRobot | Dimostrazioni autonome, interazione gestuale, avvio rapido |
| Modello di servo | Servo bus seriale Feetech SCS0009 ×8 | Servo PWM **digitale** PTK 7452 MG-D ×8 |
| Parametri del servo | 2,3 kg·cm@6 V, 300° controllabili, precisione 0,293° | 4,5 kg·cm@7,4 V (circa 2,8–3 kg·cm con l'alimentazione a 5 V di questa soluzione), 180°±10°, aggiornamento a 333 Hz |
| Retroazione di posizione/temperatura/tensione/velocità | ✅ Lettura supportata | ❌ Nessuna lettura, impossibile rilevare blocco o perdita di passi |
| Controllore | Nessuno a bordo; PC/Raspberry Pi collegati direttamente tramite la scheda driver bus | Firmware a bordo ESP32-S3 |
| Concentratore | Scheda driver servo + hub bus seriale a 9 vie | Scheda adattatrice PWM (8 connettori 3P + 5 V/GND) |
| Alimentazione | Ingresso 7–12 V (DC5521) sulla scheda driver, servo di classe 6 V nominali | 5 V / 3 A o più, massa comune obbligatoria tra scheda adattatrice ed ESP32 |
| Baudrate | **1.000.000** | Il servo non ha baudrate; seriale PC↔ESP32 **115200 8N1** |
| ID servo | Da impostare: mano destra 1–8, mano sinistra 11–18 | Nessun ID; canali fissi CH1–CH8 (indice 1/2, medio 3/4, anulare 5/6, pollice 7/8), cablaggio identico per mano destra e sinistra |
| Catena di comunicazione | PC → scheda driver → bus → 8 servo | PC → seriale USB 115200 → ESP32 → 8 canali PWM |
| Forma dei comandi | Protocollo bus Feetech, invio diretto dell'angolo | Frame binari: gesti `0x01–0x0A / 0x0C`, pilotaggio diretto `0xF0`, mano destra/sinistra `0xF1`, NOP `0x00`, ripetizione `0xFE`, stop `0xFF` |
| Firmware | Nessuno (nessun flashing richiesto) | Richiede compilazione con ESP-IDF oppure flashing diretto di `amazinghand_pwm.bin` precompilato |
| Mano destra/sinistra | ID servo diversi (destra 1–8, sinistra 11–18) | Stessi canali, mappatura nel codice + selezione del lato con `0xF1` |
| Rilascio della coppia | Supporta attivazione/rilascio della coppia | Non supportato; l'arresto di emergenza interrompe solo il gesto, i servo restano alimentati e mantengono la posizione |
| Controllo della velocità | Supporta il parametro di velocità | I frame di pilotaggio diretto non hanno parametro di velocità |

## Punti chiave della versione SCS0009

- Ogni servo ha un ID univoco; mano destra 1–8, mano sinistra 11–18. Dopo il cablaggio o la sostituzione di un servo è necessario reimpostare l'ID.
- Utilizza un bus seriale e supporta la lettura di posizione, velocità, tensione e temperatura; adatta al controllo in anello chiuso e all'acquisizione dati.
- PC/Raspberry Pi controllano direttamente tramite la scheda driver bus USB, senza firmware MCU aggiuntivo.
- Alimentazione 7–12 V in ingresso alla scheda driver bus (servo di classe 6 V); attenzione alla massa comune con la scheda driver.
- Adatta all'integrazione con SO-ARM101, LeRobot e altri flussi di addestramento che richiedono retroazione delle articolazioni.

## Punti chiave della versione PWM

- Usa **servo digitali PTK 7452 MG-D** (333 Hz, 500–2500 µs); non è possibile sostituirli direttamente con servo analogici a 50 Hz come l'SG90.
- Servo nominali 4,5 kg·cm@7,4 V; con l'alimentazione 5 V/3 A di questa soluzione la coppia effettiva è di circa 2,8–3 kg·cm.
- L'ESP32-S3 genera 8 canali PWM; il PC deve solo inviare comandi tramite la seriale USB a 115200.
- Nessuna retroazione di posizione; non è possibile leggere angolo, temperatura o tensione, né rilevare blocco/perdita di passi.
- Mano destra e sinistra condividono lo stesso gruppo di canali; per ogni dito la coppia di servo ha il canale dispari a destra e il pari a sinistra, con l'indice fisso su CH1/2.
- Richiede il flashing del firmware; il repository fornisce un bin precompilato, oppure è possibile compilare con ESP-IDF.
- Adatta a dimostrazioni autonome, interazione gestuale e avvio rapido con web/desktop; non adatta all'addestramento LeRobot che dipende dalla retroazione.

## Passi successivi

- [Avvio rapido SCS0009](../02-quick-start/scs0009.md)
- [Avvio rapido PWM](../02-quick-start/pwm.md)
- [Panoramica hardware](../01-hardware/overview.md)
- [Download e risorse](downloads.md)
