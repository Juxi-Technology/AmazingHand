---
title: "Panoramica del tutorial della mano robotica AmazingHand"
description: "Punto di accesso unificato al tutorial della mano robotica AmazingHand: scelta del prodotto, cablaggio hardware, avvio rapido, controllo web, applicazione desktop, tracciamento delle mani, messa a punto dei servo e FAQ per le versioni con servo bus seriale SCS0009 e con servo PWM."
version: both
---

# Tutorial della mano robotica AmazingHand

AmazingHand è una mano robotica antropomorfa open source e stampabile in 3D: 4 dita, 8 gradi di libertà, tutti gli attuatori integrati nella mano, circa 400 g per l'intera mano. Sono attualmente disponibili due soluzioni hardware: la struttura della mano meccanica è identica, cambiano servo, scheda driver e metodo di comunicazione.

## Scegliere prima la versione

| Voce di confronto | Versione bus seriale SCS0009 | Versione con servo PWM |
|--------|--------------------|------------|
| Scenario consigliato | Controllo preciso dell'angolo, lettura dei dati, integrazione con SO-ARM101 / acquisizione e addestramento dati LeRobot | Dimostrazioni autonome, interazione gestuale, avvio rapido con web/desktop |
| Servo | Servo bus seriale Feetech SCS0009 ×8 | Servo PWM **digitale** PTK 7452 MG-D ×8 |
| Parametri del servo | 2,3 kg·cm@6 V, 300° controllabili, precisione 0,293° | 4,5 kg·cm@7,4 V (circa 2,8–3 kg·cm con alimentazione a 5 V), 180°±10°, 333 Hz |
| Retroazione di posizione/temperatura/tensione | ✅ Supportata | ❌ Nessuna lettura, impossibile rilevare blocco o perdita di passi |
| Controllore | Nessuno a bordo, PC/Raspberry Pi collegati direttamente tramite la scheda driver bus | Firmware a bordo ESP32-S3 |
| Alimentazione | Ingresso 7–12 V (DC5521) sulla scheda driver | 5 V / 3 A o più, massa comune obbligatoria |
| Comunicazione | Protocollo bus a 1.000.000 di baud | Seriale PC↔ESP32 **115200** (il servo stesso non ha baudrate) |
| ID servo | Da impostare: mano destra 1–8, mano sinistra 11–18 | Nessun ID, canali fissi CH1–CH8: indice 1/2, medio 3/4, anulare 5/6, pollice 7/8 |
| Firmware | Nessun flashing richiesto | Richiede compilazione con ESP-IDF oppure flashing diretto del bin precompilato |

> Se servono **lettura di posizione, precisione o acquisizione dati per l'addestramento LeRobot**, scegli SCS0009; se servono solo **dimostrazioni autonome, interazione gestuale e avvio rapido**, scegli PWM.

Confronto completo e guida alla scelta in [Confronto tra versioni](00-product/version-comparison.md).

## Navigazione per modalità d'uso

| Modalità d'uso | Versione bus seriale SCS0009 | Versione con servo PWM |
|----------|--------------------|------------|
| Avvio rapido | [Avvio rapido SCS0009](02-quick-start/scs0009.md) | [Avvio rapido PWM](02-quick-start/pwm.md) |
| Controllo web | [Controllo web SCS0009](03-web-control/scs0009.md) | [Controllo web PWM](03-web-control/pwm.md) |
| Applicazione desktop / CLI | [GUI e CLI SCS0009](04-desktop/scs0009.md) | [Applicazione desktop PWM](04-desktop/pwm.md) |
| Tracciamento delle mani | [Demo ufficiale SCS0009](05-hand-tracking/scs0009.md) | [Tracciamento GUI / dora PWM](05-hand-tracking/pwm.md) |
| Messa a punto e calibrazione dei servo | [Messa a punto e calibrazione SCS0009](06-servo-tuning/scs0009.md) | [Protocollo e calibrazione PWM](06-servo-tuning/pwm.md) |
| Arduino / sviluppo personalizzato | [Arduino Nano](07-arduino/arduino-nano.md) · [Codice di esempio](07-arduino/examples.md) | Come sopra (struttura meccanica condivisa) |

Panoramica del controllo web (selezione del driver, barra della porta seriale, descrizione dell'interfaccia) in [README del controllo web](03-web-control/README.md).

## Prima di iniziare

- [Scheda prodotto](00-product/product-info.md) — specifiche, posizionamento, risorse
- [Confronto tra versioni e scelta](00-product/version-comparison.md) — differenze complete tra le due soluzioni hardware
- [Panoramica hardware](01-hardware/overview.md) — struttura, CAD, assemblaggio, stampa 3D
- [Cablaggio SCS0009](01-hardware/scs0009.md) / [Cablaggio PWM](01-hardware/pwm.md)
- [Installazione del kit telecamera](01-hardware/camera-kit.md)
- [Download e risorse](00-product/downloads.md)

## Avvertenze di sicurezza

- L'alimentazione esterna dei servo e l'ESP32/scheda driver devono avere **massa comune**.
- Prima della prima accensione portare la mano in posizione centrale e installare i bracci dei servo in posizione centrale, per evitare di urtare il finecorsa.
- Collegare **una sola** delle due soluzioni hardware SCS0009 e PWM alla volta; non collegarle insieme.
- I servo PWM non hanno retroazione di posizione: l'arresto di emergenza può solo interrompere il gesto, non leggere o rilasciare la coppia come i servo bus.

## Languages

[简体中文](../zh-hans/README.md) | [English](../en/README.md) | [Deutsch](../de/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (BR)](../pt-br/README.md) | [Português (PT)](../pt-pt/README.md) | [繁體中文](../zh-hant/README.md)
