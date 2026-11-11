---
title: "Scheda prodotto AmazingHand"
description: "Scheda prodotto della mano robotica AmazingHand: struttura meccanica, dimensioni, carico, due soluzioni con servo e risorse open source."
version: both
---

# Scheda prodotto AmazingHand

AmazingHand è una mano robotica antropomorfa open source e stampabile in 3D, pensata per la ricerca sull'intelligenza incarnata, l'educazione robotica e i prototipi di interazione uomo-macchina. Il corpo della mano meccanica è identico; sono attualmente disponibili due soluzioni hardware: **servo bus seriale SCS0009** e **servo PWM (ESP32-S3)**.

## Struttura meccanica

- **4 dita, 8 gradi di libertà**: ogni dito ha 2 gradi di libertà (flessione/estensione + divaricazione/adduzione), azionati in modo differenziale da due servo tramite un meccanismo parallelo.
- **Attuatori integrati**: tutti i servo sono montati nella mano; non servono cavi verso l'avambraccio.
- **Stampa 3D**: guscio e leveraggi sono stampabili; l'intera mano pesa circa 400 g.
- **Supporto per due mani**: è possibile usare la mano sinistra o la destra da sola, oppure entrambe in modo coordinato su un robot.
- **Interfaccia del polso**: il design originale si adatta al polso Orbita 3D di Reachy 2 e può essere adattato ad altri bracci robotici.

## Specifiche di base

| Parametro | Specifica |
|------|------|
| Peso | circa 0,416 kg |
| Numero di dita | 4 |
| Gradi di libertà per dito | 2 DoF |
| Altezza estesa (senza base) | 195 mm |
| Larghezza del palmo | 105 mm |
| Spessore del palmo | circa 90 mm |
| Distanza massima tra indice e pollice | 180 mm |
| Carico per dito | circa 0,2 kg |
| Carico massimo con le quattro dita chiuse | circa 0,5 kg |

> Carico, tensione e parametri dei servo variano in base alla versione scelta; per il confronto completo vedi [Confronto tra versioni e scelta](version-comparison.md).

## Due soluzioni hardware

| Voce | Versione bus seriale SCS0009 | Versione con servo PWM |
|------|--------------------|------------|
| Servo | Feetech SCS0009 ×8 | Servo PWM digitale PTK 7452 MG-D ×8 |
| Controllo | PC/Raspberry Pi + scheda driver bus | Firmware a bordo ESP32-S3 |
| Retroazione | Lettura di posizione/velocità/tensione/temperatura | Nessuna lettura |
| Adatta a | Precisione, acquisizione dati, LeRobot / SO-ARM101 | Dimostrazioni autonome, interazione gestuale, avvio rapido |

## Ecosistema software

- **Controllo web**: slider nel browser, 19 pose predefinite, teleoperazione con telecamera MediaPipe, supporto alla selezione del driver SCS0009 / PWM.
- **Applicazione desktop**: SCS0009 usa `AmazingHandControl` (GUI Tkinter + CLI); PWM usa `AmazingHand-PWM/tools/hand_gui.py`.
- **Tracciamento delle mani**: SCS0009 offre la demo ufficiale dora + MuJoCo IK; PWM offre il tracciamento MediaPipe integrato nella GUI.
- **Risorse open source**: CAD, documentazione di assemblaggio/stampa ed esempi Arduino/Python sono tutti nel repository.

## Risorse open source

- [Guida all'assemblaggio PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [Suggerimenti per la stampa 3D PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [Panoramica AmazingHand PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [CAD / STL / STEP](../../../AmazingHand-main/cad/)
- [Progetto upstream ufficiale (Pollen Robotics)](https://github.com/pollen-robotics/AmazingHand)

## Passi successivi

- [Confronto tra versioni e scelta](version-comparison.md)
- [Panoramica hardware](../01-hardware/overview.md)
- [Avvio rapido SCS0009](../02-quick-start/scs0009.md)
- [Avvio rapido PWM](../02-quick-start/pwm.md)
