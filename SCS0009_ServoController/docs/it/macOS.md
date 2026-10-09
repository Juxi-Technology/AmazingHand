[English](../en/macOS.md) | [Deutsch](../de/macOS.md) | [Español](../es/macOS.md) | [Français](../fr/macOS.md) | Italiano | [日本語](../ja/macOS.md) | [한국어](../ko/macOS.md) | [Português (BR)](../pt-br/macOS.md) | [Português (PT)](../pt-pt/macOS.md) | [简体中文](../zh-hans/macOS.md) | [繁體中文](../zh-hant/macOS.md)

# Strumento di debug del servo SCS0009 — Guida per macOS

Per macOS 11 (Big Sur) e successivi. Punti chiave: denominazione delle porte seriali (`cu.*` vs `tty.*`), driver USB.

> ⚠️ **Compatibilità: questo strumento attualmente supporta solo servo Feetech SCS0009 (serie SCS, feedback di posizione con potenziometro, risoluzione a 10 bit 0-1023)**. La tabella dei registri e il formato xdat sono progettati per il Feetech SCS0009; altre marche/modelli non sono garantiti.

---

## 1. Requisiti

| Dipendenza | Versione |
|-----------|---------|
| Python | >= 3.8 (3.10+ consigliato, tramite Homebrew) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| OS | macOS 11+ (Apple Silicon / Intel) |

## 2. Installare Python

Consigliato tramite Homebrew:

```bash
# Install Homebrew if missing
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

Verificate:

```bash
python3 --version
```

## 3. Installare le dipendenze

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Create l'ambiente virtuale una sola volta**. Eseguirlo di nuovo reimposterebbe/sovrascriverebbe l'ambiente (cancellando le dipendenze installate). Dopo di che, basta `source .venv/bin/activate`.

## 4. ⚠️ Denominazione delle porte seriali su macOS [Importante]

macOS colloca i dispositivi seriali USB sotto `/dev` con **due convenzioni di denominazione**:

| Prefisso | Significato | Utilizzabile |
|--------|---------|--------|
| `/dev/tty.usbserial-*` | stile modem (bloccante) | può bloccarsi, non consigliato |
| `/dev/cu.usbserial-*` | stile call/terminal (**non bloccante**) | ✅ consigliato |

**Trovate la vostra porta:**

```bash
ls /dev/cu.*
```

Output tipico:

```
/dev/cu.usbserial-0001      # CP2102 / FTDI
/dev/cu.usbmodem141101      # onboard USB serial (Arduino/ESP32)
/dev/cu.wchusbserial1420    # CH340
```

> Lo strumento preferisce automaticamente i dispositivi `cu.*`. Se specificate manualmente una porta, usate `cu.` e non `tty.`.

## 5. Driver USB

I chip più comuni (CH340, CP2102, FTDI) hanno driver macOS integrati. Se il dispositivo non viene riconosciuto:

```bash
system_profiler SPUSBDataType | grep -A5 -i "serial\|CH340\|CP210"
```

- **CH340**: i lotti più vecchi richiedono il driver ufficiale WCH
- In generale, è sufficiente che `ls /dev/cu.*` mostri il dispositivo

## 6. Verificare l'ambiente

```bash
python setup.py
```

## 7. Avviare la GUI

```bash
python -m src.gui.factory_calibration_tool
```

Specificare la porta:

```bash
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 8. Flusso di lavoro dell'interfaccia

> Layout a pannello singolo. Una barra di scorrimento compare automaticamente quando la finestra è troppo corta; si estende per adattarsi quando è massimizzata.

### 8.1 Connessione seriale
Selezionare porta e baud rate (predefinito 1M), fare clic su **Connect**.

### 8.2 Scansione dei servo
Fare clic su **Scan Servos** (ID 1-254); fare clic su una riga dell'elenco per compilare automaticamente il menu a tendina.

### 8.3 Lettura/scrittura dei parametri
- Legge tutti i 44 registri; la selezione puntuale compila indirizzo/lunghezza/valore
- Scrittura con sblocco/scrittura/blocco automatici; viene mostrato un popup di successo/fallimento

### 8.4 Controllo della posizione
Trascinare lo slider (0-1023) o digitare un valore; al termine del movimento un messaggio chiede di disattivare la coppia.

### 8.5 Baud rate / Ripristino di fabbrica
Modifica del baud rate (rollback automatico in caso di errore), ripristino dei valori di fabbrica.

### 8.6 Parametri xdat (solo EEPROM)
Salva il servo corrente → apri backup → ripristina sul servo.

## 9. Risoluzione dei problemi

| Problema | Soluzione |
|---------|----------|
| Porta con `tty.` che si blocca | Usate il prefisso `cu.` invece |
| Dispositivo non trovato | `ls /dev/cu.*`; ricollegate; `system_profiler SPUSBDataType` |
| Interfaccia cinese vuota | Il PingFang di sistema di solito va bene; installate Noto Sans CJK se è corrotto |
| Problema di permessi | macOS in genere non richiede permessi aggiuntivi; consentite l'accesso al terminale se richiesto |
| Attivazione del venv non riuscita | `source .venv/bin/activate` (non `.bat`) |
| Errore di build su Apple Silicon | Python 3.10+ è nativo; evitate il vecchio Python sotto Rosetta |

## 10. Riga di comando (facoltativo)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 11. Suggerimenti

- **Il nome della porta cambia**: i nomi `cu.*` possono variare con porte USB diverse; selezionate dal menu a tendina a ogni avvio
- **Sospensione**: macOS può sospendersi e interrompere la seriale; tenete la macchina sveglia durante l'uso
- **Permesso di privacy**: se viene chiesto di "accedere ai dischi rimovibili", consentitelo
