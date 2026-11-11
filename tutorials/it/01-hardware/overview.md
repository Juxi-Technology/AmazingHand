---
title: "Panoramica hardware: struttura, CAD e assemblaggio"
description: "Struttura meccanica, CAD/STL/STEP, assemblaggio e risorse per la stampa 3D di AmazingHand."
version: both
---

# Panoramica hardware

Le due soluzioni con servo condividono la stessa struttura della mano meccanica; cambiano modello di servo, scheda driver e cablaggio. Prima di assemblare la mano, conferma la versione scelta.

## Struttura meccanica

- 4 dita, 2 gradi di libertà ciascuna: flessione/estensione + divaricazione/adduzione.
- Ogni dito è azionato in modo differenziale da due servo tramite un meccanismo parallelo; tutti i servo sono montati nella mano.
- Guscio, leveraggi e articolazioni in materiale morbido stampati in 3D; l'intera mano pesa circa 400 g.
- L'interfaccia del polso originale si adatta all'Orbita 3D di Reachy 2 e può essere adattata ad altri bracci robotici.

## CAD e modelli

- File STL / STEP: [`AmazingHand-main/cad/`](../../../AmazingHand-main/cad/)
- Documentazione online Onshape e URDF: vedi la sezione CAD di [`AmazingHand-main/README_CN.md`](../../../AmazingHand-main/README_CN.md).

## Assemblaggio e stampa 3D

- [Guida all'assemblaggio PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [Suggerimenti per la stampa 3D PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [Panoramica AmazingHand PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)

> Prima dell'assemblaggio portare la mano in posizione centrale e installare i bracci dei servo in posizione centrale; bracci/scanalature e corse dei due tipi di servo sono diversi e non possono essere mescolati.

## Cablaggio delle due soluzioni hardware

| Versione | Guida a cablaggio e alimentazione |
|------|----------------|
| SCS0009 bus seriale | [Cablaggio, ID e alimentazione SCS0009](scs0009.md) |
| PWM (ESP32-S3) | [Cablaggio, GPIO e alimentazione PWM](pwm.md) |
| Kit telecamera | [Installazione del kit telecamera](camera-kit.md) |

## Passi successivi

- [Confronto tra versioni e scelta](../00-product/version-comparison.md)
- [Avvio rapido: SCS0009](../02-quick-start/scs0009.md) · [Avvio rapido: PWM](../02-quick-start/pwm.md)
