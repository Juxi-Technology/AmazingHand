[English](../en/Windows.md) | [Deutsch](../de/Windows.md) | [Español](../es/Windows.md) | [Français](../fr/Windows.md) | Italiano | [日本語](../ja/Windows.md) | [한국어](../ko/Windows.md) | [Português (BR)](../pt-br/Windows.md) | [Português (PT)](../pt-pt/Windows.md) | [简体中文](../zh-hans/Windows.md) | [繁體中文](../zh-hant/Windows.md)

# Strumento di debug del servo SCS0009 — Guida per Windows

Per Windows 10 / 11. Copre dall'installazione al debug completo dei servo.

> ⚠️ **Compatibilità: questo strumento attualmente supporta solo servo Feetech SCS0009 (serie SCS, feedback di posizione con potenziometro, risoluzione a 10 bit 0-1023)**. La tabella dei registri e il formato xdat sono progettati per il Feetech SCS0009; altre marche/modelli non sono garantiti.

---

## 1. Requisiti

| Dipendenza | Versione | Note |
|-----------|---------|-------|
| Python | >= 3.8 | 3.10+ consigliato, scaricatelo da [python.org](https://www.python.org/downloads/) |
| PySide6 | >= 6.0 | Framework GUI |
| pyserial | >= 3.5 | Comunicazione seriale |
| OS | Win10 / Win11 | Qualsiasi edizione |

## 2. Installare Python

1. Visitate <https://www.python.org/downloads/>
2. Scaricate l'installer di Python 3.10+
3. **Spuntate "Add Python to PATH"** durante l'installazione (altrimenti python non verrà trovato nel terminale)

Verificate:

```bash
python --version
```

## 3. Installare le dipendenze

Installate in un ambiente virtuale per non sporcare il Python di sistema:

```bash
cd SCS0009_ServoController
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> ⚠️ **Create l'ambiente virtuale una sola volta**. Eseguirlo di nuovo reimposterebbe/sovrascriverebbe l'ambiente (cancellando le dipendenze installate). Dopo di che, basta attivarlo (con `activate`) ogni volta.

> Il prompt mostrerà `(.venv)` dopo l'attivazione.

## 4. Verificare l'ambiente

```bash
python setup.py
```

`[OK] 环境检查通过，可以运行项目` significa che l'ambiente è pronto.

## 5. Collegare l'hardware

1. Inserire l'adattatore USB-seriale (CH340 / CP2102)
2. Collegare il controller dei servo (scheda di controllo del braccio robotico)
3. Alimentare i servo (standard DC 5V 5A, Pro DC 12V 5A)

Controllate la porta COM in Gestione dispositivi (`Win+X` → Gestione dispositivi):

```
Ports (COM & LPT)
  └─ USB-SERIAL CH340 (COM3)     ← your servo port
```

> **Annotate il numero COM** per selezionarlo all'avvio.

## 6. Avviare la GUI

```bash
python -m src.gui.factory_calibration_tool
```

Oppure specificate la porta:

```bash
python -m src.gui.factory_calibration_tool --port COM3
```

Elencare le porte disponibili:

```bash
python -m src.gui.factory_calibration_tool --list-ports
```

## 7. Flusso di lavoro dell'interfaccia

> Layout a pannello singolo. Una barra di scorrimento compare automaticamente quando la finestra è troppo corta; si estende per adattarsi quando è massimizzata.

### 7.1 Connessione seriale

- Selezionare porta e baud rate (predefinito 1M), fare clic su **Connect**
- Lo stato mostra `🟢 Connected`

### 7.2 Scansione dei servo

- Fare clic su **Scan Servos** per rilevare i servo online (ID 1-254)
- I risultati compaiono in tempo reale nell'elenco dei servo (con il modello)
- Fare clic su una riga dell'elenco → compila automaticamente il menu a tendina dei servo

### 7.3 Lettura/scrittura dei parametri

- **Leggi parametri**: legge tutti i 44 registri (EEPROM + SRAM); il log mostra i risultati in tempo reale
- **Tabella dei parametri**: 5 colonne (Address/Register/Value/Memory/Access), codificate a colori per EEPROM/SRAM/DEFAULT
- **Collegamento per selezione di riga**: fare clic su una riga → compila automaticamente "Indirizzo di scrittura", "Lunghezza" e "Valore"
- **Scrivi**: modificate il valore e fate clic su scrivi; lo strumento sblocca/scrive/blocca automaticamente l'EEPROM
- **Popup del risultato di scrittura**: verde "✅ Written successfully" in caso di successo, rosso "❌ Write failed" (con la motivazione) in caso di errore

### 7.4 Controllo della posizione

- **Slider**: trascinate per regolare la posizione obiettivo (0-1023); il campo del valore si aggiorna in tempo reale
- **Campo del valore**: digitate direttamente la posizione obiettivo, lo slider segue
- Dopo il movimento, lo stato mostra "move complete, please turn off torque"

### 7.5 Baud rate / Ripristino di fabbrica

- **Modifica baud rate**: selezionate 38400-1000000 bps, rollback automatico in caso di errore
- **Ripristino di fabbrica**: ripristina i valori di fabbrica (ID=1, baud=1M), è necessaria una nuova scansione

### 7.6 Parametri xdat (solo EEPROM)

1. `💾 Salva servo corrente`: salva i parametri EEPROM del servo corrente in un file xdat (backup)
2. `📂 Apri xdat`: carica un file di backup
3. `📤 Ripristina sul servo`: riscrive il backup nel servo

## 8. Risoluzione dei problemi

| Problema | Soluzione |
|---------|----------|
| Nessuna porta seriale | Controllate il driver in Gestione dispositivi; provate un'altra porta USB; installate il driver CH340 |
| Porta in uso | Chiudete i monitor seriali; riavviate lo strumento |
| Testo cinese vuoto | Il sistema ha Microsoft YaHei; installate un font CJK se è corrotto |
| Servo non trovato | Controllate l'alimentazione/i collegamenti; confermate il baud 1M |
| Scrittura fallita | Controllate l'alimentazione e la connessione del servo; confermate che il registro sia scrivibile |
| PermissionError all'apertura della porta | Assicuratevi che nessun altro processo tenga la porta COM |

## 9. Riga di comando (facoltativo)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port COM3
```
