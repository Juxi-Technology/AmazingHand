---
title: "Tracciamento delle mani PWM (MediaPipe integrato nella GUI)"
description: "Tracciamento delle mani della versione con servo PWM di AmazingHand: MediaPipe integrato nella GUI, installazione delle dipendenze, esecuzione, principio e limiti, domande frequenti."
version: pwm
---

# Tracciamento delle mani PWM (MediaPipe integrato nella GUI)

> I seguenti comandi si eseguono nella directory `AmazingHand-PWM/` del repository.

Questa pagina descrive il tracciamento delle mani della **versione con servo PWM**: MediaPipe integrato nella GUI riconosce i landmark della mano dalla telecamera e li mappa in tempo reale sugli 8 servo PWM. La catena completa dora + MuJoCo IK appartiene alla demo ufficiale SCS0009, vedi [Tracciamento delle mani SCS0009](scs0009.md).

> Catena: telecamera → scheletro della mano MediaPipe → angoli di flessione/estensione delle quattro dita → ESP32 → servo PWM
>
> Applicabile a: ESP32-S3 + 8 servo PWM. Per il flashing del firmware vedi [Avvio rapido PWM](../02-quick-start/pwm.md), per il protocollo vedi [Protocollo e calibrazione PWM](../06-servo-tuning/pwm.md).

> La demo ufficiale che richiede l'IK completo (MuJoCo + dora + Rust) non viene distribuita con questo modulo; questo tutorial descrive solo il tracciamento integrato nella GUI fornito dal modulo.

## 1. Prerequisiti

1. **Hardware**: ESP32-S3 + 8 servo PWM alimentati, USB collegato, telecamera funzionante.
2. **Firmware**: già flashato (vedi [Avvio rapido PWM](../02-quick-start/pwm.md)).
3. **Python**: Python 3.12 a 64 bit (mediapipe 0.10.14 fornisce solo wheel a 64 bit).

## 2. Installazione delle dipendenze di tracciamento

Nella directory radice del modulo (`AmazingHand-PWM/`) esegui:

```bash
tools/setup_tracking.bat
```

Lo script esegue automaticamente: ricerca di Python a 64 bit → creazione dell'ambiente virtuale `tools/tracking_env` → installazione di `tools/requirements-tracking.txt` (mediapipe 0.10.14, numpy<2, scipy, opencv, Pillow, pyserial) → verifica di mediapipe.

> È possibile anche installare manualmente (con Python 3.12 a 64 bit):
> ```bash
> python -m pip install -r tools/requirements-tracking.txt
> ```

## 3. Esecuzione

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

1. Seleziona la porta COM dell'ESP32 in alto → fai clic su «Connetti».
2. Scorri fino al pannello «Tracciamento delle mani (telecamera MediaPipe)».
3. Seleziona il numero della telecamera (predefinito 0) → fai clic su «Avvia tracciamento».
4. Metti la mano nell'inquadratura; la mano robotica segue flessione/estensione; fai clic su «Ferma tracciamento» per terminare.

![Pannello di tracciamento delle mani integrato nella GUI: selezione della telecamera, avvio del tracciamento e messaggi di stato](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-tracking.png)

## 4. Principio e limiti

- MediaPipe 0.10.14 estrae i vettori 3D delle punte delle 4 dita (sistema di coordinate della mano).
- `tips_to_angles()` di `hand_tracking.py` mappa ogni dito in un angolo differenziale:
  - flex (flessione/estensione): per tre dita usa la componente z, per il pollice la componente y;
  - base (oscillazione laterale): fissata a 90 (oscillazione laterale non ancora implementata).
- Questi sono **assi di controllo**; al momento dell'invio il programma li combina negli angoli dei due servo di ogni dito (stesso verso = divaricazione, versi opposti = flessione).
- La GUI integra uno smoothing EMA (alpha=0.4) + throttling a 60 ms per ridurre il tremolio.

Limiti: senza IK la precisione è inferiore alla catena completa MuJoCo + dora; adatta a dimostrazioni e avvio rapido.

### Calibrazione dei parametri

- `FLEX_SCALE` / `THUMB_FLEX_GAIN` in fondo a `hand_tracking.py` controllano ampiezza e direzione della flessione (i valori correnti del codice fanno fede).
- L'oscillazione laterale non è ancora implementata; `base` è fissato a 90; per l'oscillazione laterale usa la demo ufficiale dora SCS0009.
- Le modifiche hanno effetto dopo il riavvio della GUI.

## 5. Cambio mano destra/sinistra

In alto nella GUI seleziona «Mano destra» / «Mano sinistra». Dopo il cambio la direzione speculare del pollice cambia; se risulta invertita, seleziona l'altro lato per fare una prova.

## 6. Domande frequenti

| Sintomo | Soluzione |
|------|------|
| I servo non si muovono affatto | Controlla alimentazione (5V 3A), porta COM, cablaggio; verifica che il firmware sia flashato |
| La telecamera non mostra immagini | Consenti il permesso della telecamera (Impostazioni→Privacy→Fotocamera) |
| La mano non segue / è lenta | Luce sufficiente, mano completamente nell'inquadratura, movimenti più lenti e ampi |
| Il verso della mano è invertito / direzione del pollice invertita | Seleziona la mano destra/sinistra opposta |
| Dopo aver cambiato porta USB non si trova la seriale | Riseleziona la porta COM nella GUI |
| All'avvio segnala mediapipe mancante | Avvia con `tools\tracking_env\Scripts\python`, oppure riesegui `tools/setup_tracking.bat` |

## 7. IK completo / servo bus SCS0009

- La catena IK completa (telecamera → MediaPipe → MuJoCo + mink IK → AHControl → ESP32) proviene da un progetto demo dora separato e non è inclusa in questo modulo; se necessario usa il pacchetto di consegna originale o il progetto MediaPipe.
- I servo bus SCS0009 sono supportati da `Amazinghand-web/` e `AmazingHandControl/` del repository.

## Descrizione delle directory

| Percorso | Contenuto |
|------|------|
| `tools/hand_gui.py` | Applicazione desktop Tkinter (gesti, pilotaggio diretto, differenziale, tracciamento integrato) |
| `tools/hand_tracking.py` | Tracciamento della mano MediaPipe e mappatura degli angoli |
| `tools/setup_tracking.bat` | Crea `tools/tracking_env` e installa le dipendenze di tracciamento |
| `tools/requirements-tracking.txt` | Elenco delle dipendenze di tracciamento |
| `tools/serial_test.py` | Test seriale da riga di comando |
