---
title: "Esempi Arduino e Python"
description: "Esempi ufficiali Arduino/Python di AmazingHand: libreria SCServo, strumento di debug Feetech, modalità di cablaggio TTL Linker, seriale Arduino Uno/Mega e script Python di base."
version: scs0009
---

# Esempi Arduino e Python

Questa pagina riassume gli esempi ufficiali e i punti chiave del cablaggio di `AmazingHand-main/ArduinoExample/` e `AmazingHand-main/PythonExample/`.

## Esempi Arduino

### Preparazione

- Installa la libreria **SCServo** nel Gestore librerie di Arduino IDE.
- Usa lo strumento di debug Feetech FD per impostare l'ID del servo (`feetech debug tool`).
- Tra Arduino e TTL Linker **collega RX/TX in modo incrociato**.

### Modalità Link: modifica dell'ID del servo

1. Carica prima l'esempio `Blink` su Arduino.
2. Collega secondo la modalità Link e apri il software Feetech per modificare l'ID.

![Cablaggio in modalità Link](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Link-mode.jpg)

![Installazione della libreria SCServo](../../assets/robot-arms/amazing-hand/arduino-extension/SCServo.jpg)

### Modalità Control: Arduino controlla i servo

Dopo aver caricato un programma personalizzato, collega secondo la modalità Control:

![Cablaggio in modalità Control](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Control-mode.jpg)

- **Arduino Uno** (con una sola seriale): usa la seriale software/i pin indicati nella figura.
- **Arduino Mega**: usa **RX1 / TX1 (19 / 18)**.

![Cablaggio seriale Uno](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Uno.jpg)

![Cablaggio seriale Mega](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Mega.jpg)

> Numeri dei pin, versione delle librerie e direzione del TTL Linker fanno fede secondo la serigrafia della scheda reale; prima di modificare l'ID verifica l'alimentazione del bus e la massa comune.

## Esempi Python

`AmazingHand-main/PythonExample/` fornisce 4 script di base:

| Script | Funzione |
|------|------|
| `AmazingHand_Demo.py` | Demo di base per una mano: connessione al bus, esecuzione dei movimenti |
| `AmazingHand_Demo_Both.py` | Demo con entrambe le mani |
| `AmazingHand_FingerTest.py` | Test di un singolo dito |
| `AmazingHand_Hand_FingerMiddlePos.py` | Calibrazione della posizione centrale delle dita |

Prima dell'uso:

1. Imposta l'ID dei servo con il software Feetech (destra 1–8, sinistra 11–18).
2. Installa `pyserial`, modifica il nome della seriale/il baudrate nello script e poi esegui.
3. Verifica che l'alimentazione esterna dei servo sia collegata e che ci sia massa comune con la scheda driver bus.

> Questi sono gli esempi di base ufficiali; per GUI/CLI più complete vedi [Applicazione desktop SCS0009](../04-desktop/scs0009.md), per il cablaggio TTL e la posizione centrale vedi [Messa a punto e calibrazione dei servo SCS0009](../06-servo-tuning/scs0009.md).

## Posizione del codice sorgente

- [`AmazingHand-main/ArduinoExample/`](../../../AmazingHand-main/ArduinoExample/)
- [`AmazingHand-main/PythonExample/`](../../../AmazingHand-main/PythonExample/)
