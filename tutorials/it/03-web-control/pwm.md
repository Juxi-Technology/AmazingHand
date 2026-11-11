---
title: "Controllo web PWM"
description: "Controllo web della versione con servo PWM di AmazingHand: connessione ESP32-S3, selezione del driver, differenze rispetto a SCS0009, calibrazione degli angoli e domande frequenti."
version: pwm
---

# Controllo web PWM

Questa pagina è la descrizione dedicata alla **versione PWM (ESP32-S3)** del controllo web. Per l'interfaccia comune, le modalità di avvio, le pose predefinite e la teleoperazione con telecamera vedi [Panoramica del controllo web](README.md).

## Hardware e flashing

- Cablaggio, GPIO, alimentazione e modello di servo: [Cablaggio, GPIO e alimentazione PWM](../01-hardware/pwm.md).
- Flashing del firmware (ESP-IDF o bin precompilato): [Avvio rapido PWM](../02-quick-start/pwm.md).
- Seriale PC↔ESP32 fissa a **115200 8N1**; il servo stesso non ha baudrate.

## Connessione web

1. Nel menu a tendina «Driver» in alto seleziona **PWM (ESP32-S3)**
2. Fai clic su **Add port…** e seleziona la porta USB dell'ESP32-S3
3. Fai clic su **Connect**: la pagina esegue automaticamente l'handshake (NOP), invia la scelta della mano e torna alla posizione centrale
4. Poi controlla con gli slider, le pose predefinite e la teleoperazione con la telecamera; il titolo delle dita mostra **CH 1/2 …** (numero di canale PWM)

![Modalità PWM: selezione del driver in alto e visualizzazione dei canali CH](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-port-bar.png)

![Pannello di controllo manuale in modalità PWM: il titolo delle dita mostra i canali CH, il pulsante della coppia è nascosto](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-manual.png)

## Differenze rispetto alla versione SCS0009

| Voce | Versione bus SCS0009 | Versione PWM |
|------|----------------|--------|
| Baudrate seriale | 1.000.000 | **115.200** |
| Scheda driver | Scheda driver bus USB | ESP32-S3 + scheda adattatrice PWM |
| Coppia | Attivabile/rilasciabile | **Nessuna** (il firmware non ha comandi di coppia, il pulsante viene nascosto) |
| Arresto di emergenza | Rilascia tutta la coppia | Invia `0xFF` per interrompere il gesto; i servo restano alimentati e mantengono la posizione |
| Velocità | Supporta il parametro di velocità | I frame di pilotaggio diretto non hanno parametro di velocità |
| Retroazione | Lettura di posizione/temperatura/tensione/velocità | **Nessuna lettura**, impossibile rilevare blocco o perdita di passi |
| Mano destra/sinistra | ID servo diversi | Stessi canali, invio di `0xF1` per cambiare (influenza soprattutto i gesti del firmware; le pose della pagina usano la mappatura della rispettiva mano) |

## Calibrazione degli angoli

La pagina converte i valori di posa in 8 angoli da 0 a 180°, con la formula predefinita:

```
angle = 90 + dir × scale × valore di posa + offset
```

- Per ogni dito il primo canale ha `dir = -1`, il secondo `dir = +1`
- Per impostazione predefinita `scale = 1`, `offset = 0`, cioè si rispecchia direttamente l'angolo dell'asse del servo
- Se `mirror_pose` è vero, si scambiano prima i due valori di posa di ogni dito (in questo repository è attivo per entrambe le mani)

Se sulla macchina reale la direzione è opposta o il centro è sfalsato, modifica `pwm.calibration` in [`config.json`](../../../Amazinghand-web-io/config.json):

```jsonc
"pwm": {
  "calibration": {
    "right": {
      "pointer": { "scale": 1.0, "offset_deg": [0, 0] }
    }
  }
}
```

- Direzione opposta: imposta `scale` del dito corrispondente a `-1`
- Offset del centro: regola `offset_deg` (separatamente per i due canali)
- Procedura dito per dito: torna al centro → trascina un singolo dito → osserva direzione/centro → modifica `scale`/`offset_deg` → ricarica la pagina e riprova

## Domande frequenti

- **Connessione fallita / ESP32 non risponde**: verifica che il baudrate sia 115200, che sia selezionata la porta COM dell'ESP32, che l'alimentazione sia 5 V/3 A e che ci sia massa comune; all'apertura della porta l'ESP32 può resettarsi e la pagina ritenta automaticamente il NOP
- **I servo non si muovono o tremano**: verifica prima che i servo siano digitali a 333 Hz (PTK 7452 MG-D o equivalenti) e che l'alimentazione sia sufficiente; l'SG90 richiede una modifica del firmware
- **Direzione invertita**: imposta `scale` del dito corrispondente a `-1`
- **Centro sbagliato**: regola `offset_deg` del canale corrispondente
- **Messaggio «occupato (gesto in corso)»**: il firmware sta eseguendo un gesto integrato; attendi che finisca o premi l'arresto di emergenza (`0xFF`)
- **Scansione dei servo**: `tools/scan_servos.py` vale solo per SCS0009; per il PWM usa `AmazingHand-PWM/tools/serial_test.py` o la pagina web

---

## Pagine correlate

- [Protocollo e calibrazione PWM](../06-servo-tuning/pwm.md)
- [Applicazione desktop PWM](../04-desktop/pwm.md)
- [Avvio rapido PWM](../02-quick-start/pwm.md)
