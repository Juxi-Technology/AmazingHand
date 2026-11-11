---
title: "Applicazione desktop PWM (GUI Tkinter)"
description: "Controllo desktop della versione con servo PWM di AmazingHand: esecuzione dal sorgente, gesti/differenziale/pilotaggio diretto nella GUI, tracciamento MediaPipe integrato, test da riga di comando e packaging."
version: pwm
---

# Applicazione desktop PWM (GUI Tkinter)

> I seguenti comandi si eseguono nella directory `AmazingHand-PWM/` del repository.

Questa pagina è il tutorial del controllo desktop per la **versione con servo PWM**. Per il controllo web vedi [Controllo web PWM](../03-web-control/pwm.md), per il cablaggio vedi [Cablaggio PWM](../01-hardware/pwm.md), per il flashing del firmware vedi [Avvio rapido PWM](../02-quick-start/pwm.md).

> Applicabile a: ESP32-S3 + 8 servo PWM (azionamento differenziale). Per il flashing del firmware vedi [Avvio rapido PWM](../02-quick-start/pwm.md), per protocollo e comandi vedi [Protocollo e calibrazione PWM](../06-servo-tuning/pwm.md).

## 1. Modalità di esecuzione

| Modalità | Richiede | Adatta a |
|------|------|------|
| **Esecuzione dal sorgente** (consigliata) | Python 3.12 a 64 bit + pyserial | Tutte le funzionalità, incluso il tracciamento delle mani |
| Creazione autonoma dell'exe | PyInstaller | Distribuzione senza installazione di Python (vedi sezione 7) |

## 2. Esecuzione dal sorgente

### Installazione delle dipendenze

Nella directory radice del modulo (`AmazingHand-PWM/`) esegui:

```bash
# dipendenze di base (pyserial)
pip install -r tools/requirements.txt

# esegui solo se serve il tracciamento delle mani (crea automaticamente tools/tracking_env e installa mediapipe)
tools/setup_tracking.bat
```

> mediapipe 0.10.14 fornisce wheel solo per Windows a 64 bit; è obbligatorio usare **Python 3.12 a 64 bit**.

### Avvio della GUI

```bash
# qualsiasi Python con pyserial
python tools/hand_gui.py

# oppure usa l'ambiente di tracciamento (con mediapipe)
tools/tracking_env/Scripts/python tools/hand_gui.py
```

![Interfaccia principale dell'applicazione desktop: barra seriale, comandi dei gesti, pilotaggio diretto dei servo e controllo differenziale delle dita](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-main.png)

### Uso della GUI

1. **Seleziona la porta seriale**: scegli la porta COM dell'ESP32 nel menu a tendina in alto (vedi Gestione dispositivi).
2. **Fai clic su «Connetti»**: la spia di stato diventa verde, il log mostra «connesso» e viene inviato automaticamente un NOP per il test del collegamento.
3. **Comandi dei gesti**: fai clic su «Sasso / Forbici / Carta / Pollice su / OK / Pizzico / Indica / Apri / Pugno» e la mano robotica esegue il gesto.
4. **Mano destra/sinistra**: seleziona «Mano destra» / «Mano sinistra» (la direzione speculare del pollice è diversa).
5. **Pilotaggio diretto dei servo**: trascina gli 8 slider per controllare in tempo reale l'angolo di un singolo servo (0–180°).
6. **Controllo differenziale delle dita**: due barre di avanzamento per ogni dito —
   - **Flessione◀▶Estensione**: il dito si piega o si distende (intervallo -70 ~ +70).
   - **Oscillazione destra◀▶sinistra**: il dito oscilla a destra e a sinistra (intervallo 60 ~ 120, 90 = neutro).

   > Queste due barre di avanzamento sono **assi di controllo**, non due servo. Il programma li combina negli angoli dei due servo di quel dito: la componente nello stesso verso produce la divaricazione, quella in versi opposti produce la flessione.

7. **Ripeti / Ferma**: ripete l'ultimo gesto / interrompe immediatamente.
8. **Log di comunicazione**: in basso mostra in tempo reale i frame inviati/ricevuti e le risposte.

![Pannello di controllo differenziale delle dita: flessione/estensione e oscillazione laterale per ogni dito](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-differential.png)

### Tracciamento delle mani integrato nella GUI

La GUI include un pannello di tracciamento delle mani (la telecamera segue i movimenti della mano):

1. Dopo aver collegato la seriale, scorri fino al pannello «Tracciamento delle mani (telecamera MediaPipe)».
2. Seleziona il numero della telecamera (predefinito 0) e fai clic su **«Avvia tracciamento»**.
3. Metti la mano nell'inquadratura; la mano robotica segue flessione/estensione.

> Il tracciamento richiede mediapipe installato tramite `tools/setup_tracking.bat`; solo la GUI avviata dal sorgente dispone della funzione di tracciamento.

## 3. Test da riga di comando (tools/serial_test.py)

Esegui nella directory radice del modulo:

```bash
# test del collegamento (verifica prima che comunichi)
python tools/serial_test.py COM3 nop

# gesti
python tools/serial_test.py COM3 rock         # sasso
python tools/serial_test.py COM3 thumbs_up    # pollice su
python tools/serial_test.py COM3 index        # indica
python tools/serial_test.py COM3 open         # apri
python tools/serial_test.py COM3 close        # pugno

# pilotaggio diretto di un singolo servo
python tools/serial_test.py COM3 servo 1 90   # servo1 → 90°

# riporta tutto al centro
python tools/serial_test.py COM3 mid

# imposta mano destra/sinistra
python tools/serial_test.py COM3 hand L
python tools/serial_test.py COM3 hand R

# sweep/autotest
python tools/serial_test.py COM3 sweep 1      # sweep del servo1
python tools/serial_test.py COM3 test         # test di tutti i servo uno per uno
```

## 4. Test manuale con strumento seriale (opzionale)

Senza applicazione desktop è possibile verificare il collegamento inviando frame esadecimali direttamente con uno strumento seriale.

**CoolTerm** (Windows / macOS / Linux):

1. `Options` → baudrate **115200**, 8N1.
2. `Connection` → `Send String` → seleziona `Hex`.
3. Invia `AA 01 00 01` (sasso); nell'area delle risposte dovrebbero comparire `BB 01 00 01` (ACK) e `BB 01 10 11` (completato).

**Riga di comando Linux / macOS**:

```bash
# Linux
stty -F /dev/ttyUSB0 115200
printf '\xAA\x01\x00\x01' > /dev/ttyUSB0

# macOS
stty -f /dev/cu.usbserial-0001 115200
printf '\xAA\x01\x00\x01' > /dev/cu.usbserial-0001
```

Formato dei frame, checksum e tutti i comandi in [Protocollo e calibrazione PWM](../06-servo-tuning/pwm.md).

## 5. Script di controllo Python (sviluppo personalizzato)

```python
import time
import serial

PORT, BAUD = "COM3", 115200          # su Linux/macOS sostituisci con /dev/ttyUSB0, /dev/cu.usbserial-*

def frame(cmd, data=b""):
    checksum = cmd ^ len(data)
    for byte in data:
        checksum ^= byte
    return bytes([0xAA, cmd, len(data)]) + data + bytes([checksum & 0xFF])

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(1)                        # attendi il completamento del reset dell'ESP32

ser.write(frame(0x00))               # test del collegamento NOP
ser.write(frame(0x01))               # sasso
time.sleep(0.5)
ser.write(frame(0xF0, bytes([90] * 8)))  # tutti gli 8 servo a 90°
ser.close()
```

Il frame di risposta è `BB CMD STATUS CKSUM`; `STATUS=0x00` indica accettato, `0x10` indica gesto completato. La tabella completa dei comandi e gli esempi di pilotaggio diretto/mano destra-sinistra sono in [Protocollo e calibrazione PWM](../06-servo-tuning/pwm.md).

## 6. Domande frequenti

| Sintomo | Soluzione |
|------|------|
| I servo non si muovono | Controlla l'alimentazione (alimentatore separato 5V 3A), la porta COM, il cablaggio |
| Nessuna risposta / i servo si muovono a caso dopo l'apertura della seriale | Verifica il baudrate 115200; durante la connessione la GUI invia prima l'handshake NOP |
| La telecamera non mostra immagini | Consenti il permesso della telecamera (Impostazioni→Privacy→Fotocamera) |
| Il verso della mano è invertito | Seleziona la mano destra/sinistra opposta |
| Il tracciamento non risponde | Verifica di avviare con il Python di `tools\tracking_env` e che mediapipe sia installato correttamente |

## 7. Creazione autonoma dell'exe (opzionale)

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole --name "AmazingHand控制台" tools/hand_gui.py
```

La versione pacchettizzata non include il tracciamento delle mani (le risorse mediapipe sono grandi); per il tracciamento usa l'esecuzione dal sorgente.

> Per la descrizione completa del protocollo e dei comandi vedi [Protocollo e calibrazione PWM](../06-servo-tuning/pwm.md).
