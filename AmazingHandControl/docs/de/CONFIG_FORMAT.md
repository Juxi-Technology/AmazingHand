[English](../en/CONFIG_FORMAT.md) | Deutsch | [Español](../es/CONFIG_FORMAT.md) | [Français](../fr/CONFIG_FORMAT.md) | [Italiano](../it/CONFIG_FORMAT.md) | [日本語](../ja/CONFIG_FORMAT.md) | [한국어](../ko/CONFIG_FORMAT.md) | [Português (BR)](../pt-br/CONFIG_FORMAT.md) | [Português (PT)](../pt-pt/CONFIG_FORMAT.md) | [简体中文](../zh-hans/CONFIG_FORMAT.md) | [繁體中文](../zh-hant/CONFIG_FORMAT.md)

# Hand-Konfigurationsformat (YAML)

Dieses Dokument beschreibt die von AmazingHand verwendeten YAML-Konfigurationsdateien.

| Datei | Zweck |
|------|---------|
| `data/hand_config.yaml` | Posen und Sequenzen (erstellt/bearbeitet von GUI und CLI) |
| `data/config.yaml` | Anwendungseinstellungen (serieller Port, Servogrenzen, Geschwindigkeiten, Pfade) |

---

## `data/config.yaml` – Anwendungseinstellungen

Wird beim Start von der GUI geladen. Fehlt die Datei, werden integrierte Standardwerte verwendet.
Die CLI verwendet dieselben Standardwerte (überschreibbar über `--port` / `--baudrate`).

### Vollständige Struktur

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

### Hinweise
- Alle Schlüssel sind optional — fehlende Schlüssel fallen auf die oben gezeigten integrierten Standardwerte zurück.
- Speichern Sie hier **keine** Posen oder Sequenzen; diese gehören in `data/hand_config.yaml`.
- Starten Sie die GUI nach dem Bearbeiten dieser Datei neu, damit die Änderungen wirksam werden.

---

## `data/hand_config.yaml` – Posen & Sequenzen

Wird von der GUI und der CLI erstellt und bearbeitet. Wird von beiden Werkzeugen gemeinsam genutzt.

### YAML-Struktur

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

## Posen

Jede Pose definiert eine vollständige Handposition mit 8 Servowerten.

### Format
```yaml
poses:
  pose_name:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
```

### Positions-Array
- **8 Werte**, die Servopositionen in Grad darstellen
- **Servo-Zuordnung**:
  - Servo 1: Position des Zeigefingers (0=offen, 110=geschlossen)
  - Servo 2: Seite des Zeigefingers (-20=links, 0=Mitte, +20=rechts)
  - Servo 3: Position des Mittelfingers
  - Servo 4: Seite des Mittelfingers
  - Servo 5: Position des Ringfingers
  - Servo 6: Seite des Ringfingers
  - Servo 7: Position des Daumens
  - Servo 8: Seite des Daumens

- **Bereich des Schließen/Öffnen-Schiebereglers**: 0-110° pro Finger (0=offen, 110=geschlossen)
- **Bereich des Seiten-Schiebereglers**: -40° (links) bis +40° (rechts)
- **Gespeicherte Servowerte**: Da die YAML-Datei die kombinierten Werte (base ± side) speichert, liegen die tatsächlichen Servobefehle voraussichtlich etwa zwischen -40° und 150°
- **Hinweis**: Geradzahlige Servos (2,4,6,8) haben in der Hardware invertierte Winkel

### Namensregeln
- Buchstaben, Zahlen und Unterstriche sind erlaubt
- **Verbotene Zeichen**: `: { } [ ] , & * # ? | - < > = ! % @ \` " '`
- Maximal 50 Zeichen
- Groß-/Kleinschreibung wird unterschieden

### Beispiel
```yaml
poses:
  open:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
  close:
    positions: [110, 0, 110, 0, 110, 0, 110, 0]
  peace:
    positions: [0, 0, 110, 0, 0, 0, 0, 0]
```

## Sequenzen

Sequenzen definieren mehrstufige Animationen mit individuellen Servogeschwindigkeiten und Verzögerungen.

### Format
```yaml
sequences:
  sequence_name:
    steps:
      - "pose_name:speed1,speed2,speed3,speed4,speed5,speed6,speed7,speed8|delay"
      - "SLEEP:duration"
```

### Schrittformat

**Pose mit individuellen Geschwindigkeiten und Verzögerung:**
```
"pose_name:s1,s2,s3,s4,s5,s6,s7,s8|delay"
```
- `pose_name`: Name der auszuführenden Pose
- `s1-s8`: Individuelle Geschwindigkeit für jeden Servo (1-6, wobei 6 am schnellsten ist)
- `delay`: Wartezeit nach Abschluss der Bewegung (z. B. `2.0s`)

**Pose mit Standardgeschwindigkeiten:**
```
"pose_name:3,3,3,3,3,3,3,3|2.0s"
```

**Schlafen/Pause:**
```
"SLEEP:1.5s"
```
- Pausiert für die angegebene Dauer, ohne die Servos zu bewegen

### Geschwindigkeitswerte
- Bereich: 1 (langsamste) bis 6 (schnellste)
- Steuert die Bewegungsgeschwindigkeit der Servos
- Jeder Servo kann in einem Schritt eine andere Geschwindigkeit haben

### Loop-Steuerung
- Die Loop-Einstellung wird **NICHT** in YAML gespeichert
- Wird über ein Kontrollkästchen im GUI-Sequenz-Player gesteuert
- Ermöglicht flexible Wiedergabe ohne Bearbeitung der YAML

### Beispiel
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

## Posen und Sequenzen verwalten

### Über die GUI (`amazing_hand_gui.py`)

**Posen:**
1. Positionieren Sie die Finger mit den Schiebereglern oder der Tastatur
2. Geben Sie einen Namen in das Feld „Name:" ein
3. Klicken Sie auf „➕ Neu hinzufügen", um zu speichern

**Sequenzen:**
1. Klicken Sie im Abschnitt Sequenz-Player auf die Taste „Verwalten"
2. Erstellen Sie die Sequenz im Dialog:
   - Posen und Geschwindigkeiten auswählen
   - Verzögerungen zwischen den Schritten hinzufügen
   - Mit den Tasten ↑/↓ umsortieren
3. Sequenznamen eingeben und auf „💾 Speichern" klicken

**Ausführung:**
- Sequenz aus dem Dropdown auswählen
- „Loop" ankreuzen, wenn eine fortlaufende Wiedergabe gewünscht ist
- Auf „▶ Abspielen" klicken

### Über die CLI (`amazing_hand_cmd.py`)

**Alle Posen und Sequenzen auflisten:**
```bash
python amazing_hand_cmd.py --list
```

**Eine Pose ausführen:**
```bash
python amazing_hand_cmd.py --pose open
```

**Eine Sequenz ausführen:**
```bash
python amazing_hand_cmd.py --sequence demo
```

**Mit Loop ausführen:**
```bash
python amazing_hand_cmd.py --sequence wave --loop
```

**Eine alternative Konfiguration verwenden:**
```bash
python amazing_hand_cmd.py --pose open --config /path/to/hand_config.yaml
```

## Manuelle Bearbeitung

Sie können `data/hand_config.yaml` direkt bearbeiten:

1. **YAML-Syntax beachten** - Die Einrückung muss konsistent sein (2 oder 4 Leerzeichen)
2. **Inline-Array-Format** für Positionen verwenden:
   ```yaml
   positions: [0, 0, 0, 0, 0, 0, 0, 0]
   ```
3. **Sequenzschritte in Anführungszeichen setzen**, um Sonderzeichen zu erhalten:
   ```yaml
   steps:
     - "open:3,3,3,3,3,3,3,3|2.0s"
   ```
4. **Namen validieren** - Verbotene Zeichen vermeiden
5. **GUI neu starten**, um Änderungen neu zu laden
6. **Backups anlegen** vor größeren Änderungen

## Validierung

Die GUI und die CLI validieren automatisch:
- Posen-/Sequenznamen (verbotene Zeichen)
- YAML-Syntax beim Speichern
- Länge des Positions-Arrays (muss 8 sein)

Ungültige Namen werden mit einer Fehlermeldung abgelehnt, die die verbotenen Zeichen anzeigt.

## Lizenz

Copyright 2026 AmazingHand Control Contributors

Lizenziert unter der Apache License, Version 2.0
