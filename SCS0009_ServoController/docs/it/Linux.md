[English](../en/Linux.md) | [Deutsch](../de/Linux.md) | [Español](../es/Linux.md) | [Français](../fr/Linux.md) | Italiano | [日本語](../ja/Linux.md) | [한국어](../ko/Linux.md) | [Português (BR)](../pt-br/Linux.md) | [Português (PT)](../pt-pt/Linux.md) | [简体中文](../zh-hans/Linux.md) | [繁體中文](../zh-hant/Linux.md)

# Strumento di debug del servo SCS0009 — Guida per Linux

Per Ubuntu / Debian / altre distribuzioni principali. Punti chiave: permessi della porta seriale (dialout), rilevamento dei dispositivi USB-seriale.

> ⚠️ **Compatibilità: questo strumento attualmente supporta solo servo Feetech SCS0009 (serie SCS, feedback di posizione con potenziometro, risoluzione a 10 bit 0-1023)**. La tabella dei registri e il formato xdat sono progettati per il Feetech SCS0009; altre marche/modelli non sono garantiti.

---

## 1. Requisiti

| Dipendenza | Versione |
|-----------|---------|
| Python | >= 3.8 (3.10+ consigliato) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| OS | Ubuntu 20.04+ / Debian 11+ |

Font cinesi (necessari per l'interfaccia in cinese):

```bash
sudo apt install fonts-noto-cjk
```

Font delle icone emoji (per ✅⚠️ ecc. nei log):

```bash
sudo apt install fonts-noto-color-emoji
```

## 2. Installare le dipendenze Python

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Create l'ambiente virtuale una sola volta**. Eseguirlo di nuovo reimposterebbe/sovrascriverebbe l'ambiente (cancellando le dipendenze installate). Dopo di che, basta `source .venv/bin/activate`.

> Se pip segnala "externally-managed-environment", usate un venv oppure `pip install --break-system-packages -r requirements.txt`.

## 3. ⚠️ Permessi della porta seriale (dialout) [Obbligatorio]

Per impostazione predefinita, un utente normale **non può accedere** a `/dev/ttyUSB*` / `/dev/ttyACM*`. Aggiungete il vostro utente al gruppo `dialout`:

```bash
sudo usermod -a -G dialout $USER
```

**Uscite e rientrate** (oppure riavviate). Verificate:

```bash
groups
# output should include dialout
```

> Alcune distribuzioni usano `uucp` (Arch) o `tty`.

## 4. Identificare il dispositivo seriale USB

Dopo averlo collegato:

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Output tipico:

```
/dev/ttyUSB0   # CH340 / CP2102 / PL2303
/dev/ttyACM0   # native USB serial (Arduino/ESP32 onboard)
```

## 5. Verificare l'ambiente

```bash
python setup.py
```

## 6. Avviare la GUI

```bash
python -m src.gui.factory_calibration_tool
```

Specificare la porta:

```bash
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

> Se esiste una sola porta, lo strumento la usa direttamente.

## 7. Flusso di lavoro dell'interfaccia

> Layout a pannello singolo. Una barra di scorrimento compare automaticamente quando la finestra è troppo corta; si estende per adattarsi quando è massimizzata.

### 7.1 Connessione seriale
Selezionare porta e baud rate (predefinito 1M), fare clic su **Connect**.

### 7.2 Scansione dei servo
Fare clic su **Scan Servos** (ID 1-254); fare clic su una riga dell'elenco per compilare automaticamente il menu a tendina.

### 7.3 Lettura/scrittura dei parametri
- Legge tutti i 44 registri (EEPROM + SRAM); la selezione puntuale compila indirizzo/lunghezza/valore
- Scrittura con sblocco/scrittura/blocco automatici; viene mostrato un popup di successo/fallimento

### 7.4 Controllo della posizione
Trascinare lo slider (0-1023) o digitare un valore; al termine del movimento un messaggio chiede di disattivare la coppia.

### 7.5 Baud rate / Ripristino di fabbrica
Modifica del baud rate (rollback automatico in caso di errore), ripristino dei valori di fabbrica.

### 7.6 Parametri xdat (solo EEPROM)
Salva il servo corrente → apri backup → ripristina sul servo.

## 8. Risoluzione dei problemi

| Problema | Soluzione |
|---------|----------|
| **Permission denied: /dev/ttyUSB0** | Non siete nel gruppo dialout, vedi la sezione 3; oppure `sudo chmod 666 /dev/ttyUSB0` (temporaneo) |
| Nessuna porta seriale | `ls /dev/ttyUSB* /dev/ttyACM*`; `lsusb` per confermare il dispositivo |
| Il nome del dispositivo cambia | La numerazione ttyUSB dipende dall'ordine di collegamento; usate una regola udev oppure selezionate a ogni avvio |
| Interfaccia cinese vuota | Installate `fonts-noto-cjk` |
| Le emoji appaiono come quadrati | Installate `fonts-noto-color-emoji` |
| pip install fallisce | Usate un venv; oppure `--break-system-packages` |
| L'app non si avvia | Controllate `python3 --version`; `pip list` per le dipendenze |

## 9. Riga di comando (facoltativo)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

## 10. Avanzate: nome fisso del dispositivo con udev (facoltativo)

Create `/etc/udev/rules.d/99-servo.rules` per fissare il nome del dispositivo tramite l'ID USB:

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyServo"
```

Poi `ls -l /dev/ttyServo`. Ottenete l'ID del produttore con `lsusb`.
