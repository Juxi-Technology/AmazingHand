[English](../en/CONFIG_FORMAT.md) | [Deutsch](../de/CONFIG_FORMAT.md) | [Español](../es/CONFIG_FORMAT.md) | [Français](../fr/CONFIG_FORMAT.md) | Italiano | [日本語](../ja/CONFIG_FORMAT.md) | [한국어](../ko/CONFIG_FORMAT.md) | [Português (BR)](../pt-br/CONFIG_FORMAT.md) | [Português (PT)](../pt-pt/CONFIG_FORMAT.md) | [简体中文](../zh-hans/CONFIG_FORMAT.md) | [繁體中文](../zh-hant/CONFIG_FORMAT.md)

# Formato di configurazione della mano (YAML)

Questo documento descrive i file di configurazione YAML usati da AmazingHand.

| File | Scopo |
|------|---------|
| `data/hand_config.yaml` | Pose e sequenze (create/modificate da GUI e CLI) |
| `data/config.yaml` | Impostazioni dell'applicazione (porta seriale, limiti dei servo, velocità, percorsi) |

---

## `data/config.yaml` – Impostazioni dell'applicazione

Caricato all'avvio dalla GUI. Se il file è assente, vengono usati i valori predefiniti integrati.
La CLI usa gli stessi valori predefiniti (sovrascrivibili tramite `--port` / `--baudrate`).

### Struttura completa

```yaml
# Serial port settings
serial:
  port_windows: COM9          # Default port on Windows
  port_linux: /dev/ttyACM0   # Default port on Linux/macOS
  baudrate: 1000000           # Default baud rate
  baudrate_options: [9600, 115200, 1000000]  # Shown in GUI dropdown

# Servo assignments — [servo1_id, servo2_id] per finger
# servo1 (odd ID)  = position axis (open/close)
# servo2 (even ID) = side axis (left/right)
servos:
  ring:    [1, 2]
  middle:  [3, 4]
  pointer: [5, 6]
  thumb:   [7, 8]
  all_ids: [1, 2, 3, 4, 5, 6, 7, 8]

# Servo angle limits (degrees)
limits:
  servo_min: -40   # Absolute minimum for any servo command
  servo_max: 110   # Absolute maximum for any servo command
  base_min: 0      # Open/close slider minimum
  base_max: 110    # Open/close slider maximum
  side_min: -40    # Left/right slider minimum
  side_max: 40     # Left/right slider maximum

# Movement speeds (1–6 scale, where 6 is fastest)
speeds:
  default: 3
  min: 1
  max: 6

# Auto-mode blending extremes — [servo1_deg, servo2_deg]
# Used to interpolate combined position+side values in Auto mode
auto_extremes:
  left_open:    [32, -40]
  right_open:   [-40, 32]
  left_closed:  [110, 110]
  right_closed: [110, 110]
  center_open:  [0, 0]
  center_closed: [110, 110]

# File paths (relative to project root)
paths:
  poses_sequences_file: data/hand_config.yaml
```

### Note
- Tutte le chiavi sono opzionali — le chiavi mancanti ricadono sui valori predefiniti integrati mostrati sopra.
- **Non** memorizzare pose o sequenze qui; quelle appartengono a `data/hand_config.yaml`.
- Riavviare la GUI dopo aver modificato questo file perché le modifiche abbiano effetto.

---

## `data/hand_config.yaml` – Pose e sequenze

Create e modificate dalla GUI e dalla CLI. Condivise tra i due strumenti.

### Struttura YAML

```yaml
poses:
  <pose_name>:
    positions: [pos1, pos2, pos3, pos4, pos5, pos6, pos7, pos8]

sequences:
  <sequence_name>:
    steps:
      - "<pose_name>:speed1,speed2,...,speed8|delay"
      - "SLEEP:duration"
```

## Pose

Ogni posa definisce una posizione completa della mano con 8 valori di servo.

### Formato
```yaml
poses:
  pose_name:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
```

### Array delle posizioni
- **8 valori** che rappresentano le posizioni dei servo in gradi
- **Mappatura dei servo**:
  - Servo 1: posizione del dito indice (0=aperto, 110=chiuso)
  - Servo 2: lato del dito indice (-20=sinistra, 0=centro, +20=destra)
  - Servo 3: posizione del dito medio
  - Servo 4: lato del dito medio
  - Servo 5: posizione del dito anulare
  - Servo 6: lato del dito anulare
  - Servo 7: posizione del pollice
  - Servo 8: lato del pollice

- **Intervallo dello slider chiudi/apri**: 0-110° per dito (0=aperto, 110=chiuso)
- **Intervallo dello slider laterale**: -40° (sinistra) a +40° (destra)
- **Valori di servo memorizzati**: poiché lo YAML memorizza i valori combinati (base ± side), aspettarsi che i comandi effettivi dei servo cadano approssimativamente tra -40° e 150°
- **Nota**: i servo con numero pari (2,4,6,8) hanno angoli invertiti nell'hardware

### Regole di denominazione
- Sono ammessi lettere, numeri e underscore
- **Caratteri vietati**: `: { } [ ] , & * # ? | - < > = ! % @ \` " '`
- Massimo 50 caratteri
- Distinzione tra maiuscole e minuscole

### Esempio
```yaml
poses:
  open:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
  close:
    positions: [110, 0, 110, 0, 110, 0, 110, 0]
  peace:
    positions: [0, 0, 110, 0, 0, 0, 0, 0]
```

## Sequenze

Le sequenze definiscono animazioni multi-passo con velocità e ritardi individuali per servo.

### Formato
```yaml
sequences:
  sequence_name:
    steps:
      - "pose_name:speed1,speed2,speed3,speed4,speed5,speed6,speed7,speed8|delay"
      - "SLEEP:duration"
```

### Formato del passo

**Posa con velocità individuali e ritardo:**
```
"pose_name:s1,s2,s3,s4,s5,s6,s7,s8|delay"
```
- `pose_name`: nome della posa da eseguire
- `s1-s8`: velocità individuale di ciascun servo (1-6, dove 6 è la più veloce)
- `delay`: tempo di attesa dopo il completamento del movimento (ad es. `2.0s`)

**Posa con velocità predefinite:**
```
"pose_name:3,3,3,3,3,3,3,3|2.0s"
```

**Sleep/pausa:**
```
"SLEEP:1.5s"
```
- Mette in pausa per la durata specificata senza muovere i servo

### Valori di velocità
- Intervallo: da 1 (la più lenta) a 6 (la più veloce)
- Controlla la velocità di movimento dei servo
- Ogni servo può avere una velocità diversa in un passo

### Controllo del loop
- L'impostazione di loop **NON** è memorizzata nello YAML
- È controllata tramite casella di controllo nel riproduttore di sequenze della GUI
- Consente una riproduzione flessibile senza modificare lo YAML

### Esempio
```yaml
sequences:
  demo:
    steps:
      - "open:3,3,3,3,3,3,3,3|2.0s"
      - "close:3,3,3,3,3,3,3,3|2.0s"
      - "open:3,3,3,3,3,3,3,3|1.0s"
  
  wave:
    steps:
      - "open:5,5,5,5,5,5,5,5|0.5s"
      - "SLEEP:0.3s"
      - "close:5,5,5,5,5,5,5,5|0.5s"
      - "SLEEP:0.3s"
```

## Gestione di pose e sequenze

### Tramite GUI (`amazing_hand_gui.py`)

**Pose:**
1. Posizionare le dita usando gli slider o la tastiera
2. Inserire il nome nel campo "Name:"
3. Fare clic su "➕ Add New" per salvare

**Sequenze:**
1. Fare clic sul pulsante "Manage" nella sezione Sequence Player
2. Costruire la sequenza nella finestra di dialogo:
   - Selezionare pose e velocità
   - Aggiungere ritardi tra i passi
   - Riordinare con i pulsanti ↑/↓
3. Inserire il nome della sequenza e fare clic su "💾 Save"

**Esecuzione:**
- Selezionare la sequenza dal menu a tendina
- Selezionare "Loop" se si desidera la riproduzione continua
- Fare clic su "▶ Play"

### Tramite CLI (`amazing_hand_cmd.py`)

**Elencare tutte le pose e le sequenze:**
```bash
python amazing_hand_cmd.py --list
```

**Eseguire una posa:**
```bash
python amazing_hand_cmd.py --pose open
```

**Eseguire una sequenza:**
```bash
python amazing_hand_cmd.py --sequence demo
```

**Eseguire con loop:**
```bash
python amazing_hand_cmd.py --sequence wave --loop
```

**Usare una configurazione alternativa:**
```bash
python amazing_hand_cmd.py --pose open --config /path/to/hand_config.yaml
```

## Modifica manuale

È possibile modificare direttamente `data/hand_config.yaml`:

1. **Rispettare la sintassi YAML** - L'indentazione deve essere coerente (2 o 4 spazi)
2. **Usare il formato array inline** per le posizioni:
   ```yaml
   positions: [0, 0, 0, 0, 0, 0, 0, 0]
   ```
3. **Racchiudere tra virgolette i passi di sequenza** per preservare i caratteri speciali:
   ```yaml
   steps:
     - "open:3,3,3,3,3,3,3,3|2.0s"
   ```
4. **Convalidare i nomi** - Evitare i caratteri vietati
5. **Riavviare la GUI** per ricaricare le modifiche
6. **Conservare copie di backup** prima di modifiche importanti

## Convalida

La GUI e la CLI convalidano automaticamente:
- Nomi di pose/sequenze (caratteri vietati)
- Sintassi YAML al salvataggio
- Lunghezza dell'array delle posizioni (deve essere 8)

I nomi non validi vengono rifiutati con un messaggio di errore che mostra i caratteri vietati.

## Licenza

Copyright 2026 AmazingHand Control Contributors

Concesso in licenza secondo la Apache License, Version 2.0
