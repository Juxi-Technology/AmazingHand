[English](../en/user_manual.md) | Deutsch | [Español](../es/user_manual.md) | [Français](../fr/user_manual.md) | [Italiano](../it/user_manual.md) | [日本語](../ja/user_manual.md) | [한국어](../ko/user_manual.md) | [Português (BR)](../pt-br/user_manual.md) | [Português (PT)](../pt-pt/user_manual.md) | [简体中文](../zh-hans/user_manual.md) | [繁體中文](../zh-hant/user_manual.md)

# AmazingHand Controller – Benutzerhandbuch

> **Version:** 2026-03-22  
> **Gilt für:** `amazing_hand_gui.py` (GUI), `amazing_hand_cmd.py` (CLI)

---

## 1. Einführung

Die GUI des AmazingHand Controller bietet Echtzeitüberwachung und manuelle Steuerung für eine Roboterhand mit acht Servos, angetrieben von Feetech SCS0009-Aktoren. Die Oberfläche ist in Panels für Fingersteuerung, globale Verwaltung, Telemetrievisualisierung und Aktivitätsprotokollierung unterteilt. Dieser Leitfaden führt Sie durch Installation, Navigation und gängige Arbeitsabläufe.

> **Tipp:** Halten Sie dieses Handbuch geöffnet, während Sie die GUI bedienen. In die Anwendung eingebettete Tooltips wiederholen dieselben Beschreibungen, wenn Sie mit der Maus über Bedienelemente fahren.

![AmazingHand hardware with controller connected](../en/screenshots/hand_overview.png)

---

## 2. Schnellstart-Checkliste

1. **Abhängigkeiten installieren** (einmalig pro Umgebung):
   ```bash
   python -m pip install -r requirements.txt
   ```
2. **Hardware mit Strom versorgen:** Schließen Sie die 5 V-Versorgung an die Servokette an und stecken Sie den USB-Seriell-Adapter ein.
3. **GUI starten:**
   ```bash
   python amazing_hand_gui.py
   ```
4. **Mit dem Controller verbinden:** Wählen Sie den seriellen **Port** (z. B. `COM9`) und klicken Sie auf **▶ Verbinden**.
5. **Telemetrie prüfen:** Achten Sie auf Live-Aktualisierungen im Diagramm und in der Feedback-Tabelle.

---

## 3. Bildschirmübersicht

```
+--------------------------------------------------------------------------------+
|                              AmazingHand Controller                            |
+---------------------------+-----------------------------------------------+----+
| Finger Controls           | Chart Controls & Telemetry Plot                    |
| (Ring – Middle – Pointer) | (Display menu, chart canvas)                       |
+---------------------------+-----------------------------------------------+----+
| Control Stack             | Thumb finger   | Feedback Table (Servo Metrics)    |
| (Connection, Global, Pose,| control        | (Goal, Position, Load, etc.)      |
|  Sequence)                |                |                                   |
+---------------------------+                                                    |
| Execution Log & Status    |                                                    |
+--------------------------------------------------------------------------------+
```

![Main window overview highlighting the major panels](../en/screenshots/mainscreen.png)

### 3.1 Die Panels auf einen Blick

| Panel | Position | Zweck |
|-------|----------|---------|
| **Fingersteuerung** | Links, oben (3 Finger) + unten rechts (Daumen) | Einzelne Schieberegler und Geschwindigkeitsauswahl für jedes Fingerpaar. Enthält Mimic-Anzeigen und Status-LEDs pro Finger. |
| **Rechter Steuerungsstapel** | Links, unten rechts | Verbindungseinstellungen, globale Steuerung, Posenverwaltung und Sequenz-Player. |
| **Telemetrie-Panel** | Rechts | Echtzeitdiagramme mit Zoom-/Pan-Schiebereglern und einer konfigurierbaren Feedback-Tabelle. |
| **Ausführungs-Log** | Unten | Strom von Statusmeldungen, Warnungen und Sequenzfortschritt. |

---

## 4. Detaillierte Panel-Anleitung

### 4.1 Fingersteuerungs-Panel (linke Spalte)

Jedes Finger-Widget steuert ein Paar Servos (Position + Seitenversatz):

- **Modusumschalter:** Umschalten zwischen **Auto** (base + Offset-Schieberegler) und **Raw** (direkte Servo-Ziele).
- **Status-LED:** grau (untätig), grün (in Bewegung), rot (mögliche Blockierung, basierend auf Last vs. Ziel).
- **Positions-Schieberegler:** 0–110° (offen bis geschlossen). Das Mausrad verstellt um 1°; Ziehen reagiert schnell.
- **Seiten-Schieberegler:** ±40° für seitliche Anpassungen. Der Seiten-Schieberegler des Daumens ist **invertiert**, sodass die physische Richtung mit der anatomischen Ausrichtung der Hand übereinstimmt — Ziehen nach rechts bewegt den Daumen relativ zu seiner Hardware-Montage in die positive Richtung.
- **Geschwindigkeitsauswahl:** Dropdown 1–6, das die Bewegungsgeschwindigkeit für beide Servos des Fingerpaars steuert.
- **Mimic-Kontrollkästchen:** spiegelt Schließen-/Öffnen-Bewegungen von einem Quellfinger für koordinierte Bewegung im Auto-Modus.

**Fingermodi: Auto vs. Raw**

- **Auto-Modus** (Standard) zeigt den Schließen/Öffnen-Schieberegler, den seitlichen Versatz-Schieberegler, das Geschwindigkeits-Dropdown und die Zentrieren-Taste. Die GUI mischt diese beiden Schiebereglerwerte mithilfe der in `data/hand_config.yaml` gespeicherten kalibrierten Extremwerte zu Servobefehlen, sodass das Paar natürlichen Fingerposen folgt, ohne manuelle Servomathematik. Mimic bleibt hier aktiv — aktivieren Sie es an mehreren Fingern, um sie synchron mit dem gerade angepassten Finger anzusteuern.
- **Raw-Modus** ersetzt die Auto-Bedienelemente durch zwei vertikale, nach Servo beschriftete Schieberegler. Bewegen Sie sie, um die darunterliegenden Servowinkel direkt anzusteuern, wenn Sie Endanschläge testen, die Kalibrierung validieren oder Probleme mit der Mechanik diagnostizieren. Die Zentrieren-Taste und das Mimic-Kontrollkästchen sind deaktiviert, weil Raw die Auto-Mischlogik umgeht; die Tastenkürzel funktionieren weiterhin, wobei Hoch/Runter Servo 1 und Links/Rechts Servo 2 ansteuern. Raw verwendet den zuletzt gewählten Geschwindigkeitswert; stellen Sie die Geschwindigkeiten daher vor dem Umschalten ein, wenn Sie eine bestimmte Bewegungsrate benötigen.

**Wie der Auto-Modus die Servo-Ziele berechnet**

- Der Wert des Schließen/Öffnen-Schiebereglers wird auf `limits.base_min/base_max` begrenzt und dann normalisiert (`t = base / base_max`), um zwischen den `auto_extremes`-Posen Offen vs. Geschlossen für jede Seite des Fingers zu interpolieren.
- Der Seitenversatz-Schieberegler wird auf `limits.side_min/side_max` begrenzt und in einen Mischfaktor (`u`) umgewandelt. Negative Versätze interpolieren von der Mittelpose in Richtung `left_open`/`left_closed`; positive Versätze interpolieren in Richtung der rechten Extremwerte.
- Ohne seitlichen Versatz erhalten beide Servos einfach den Wert des base-Schiebereglers. Die endgültigen Servo-Ziele werden vor der Ausgabe auf `limits.servo_min/servo_max` begrenzt, wodurch die Bewegungen innerhalb kalibrierter sicherer Grenzen bleiben.

Tastenkürzel ergänzen die Schieberegler (dokumentiert in §5.2).

![Finger control panel with per-finger sliders and status indicators](../en/screenshots/finger_control_frame.png)

### 4.2 Globaler Steuerungsstapel (rechts vom Finger-Panel)

1. **Verbindung:** Auswahl von Port und Baudrate (beide Dropdowns sind während einer bestehenden Verbindung deaktiviert), Verbinden-/Trennen-Tasten. Die Statusleiste unten meldet Erfolg oder Fehler.
2. **Globale Steuerung:**
   - **Alle öffnen / Alle schließen / Alle zentrieren** – wirken sofort auf jeden Finger.
   - **Global-Speed-Dropdown** – setzt die Geschwindigkeitsauswahl pro Finger auf einen gemeinsamen Wert (1–6).
3. **Posenverwaltung:** gespeicherte Posen aus `data/hand_config.yaml` speichern, laden, anwenden und löschen.
   - Layout: `Pose: [Dropdown]  ✓ Anwenden  🗑 Löschen  Name: [Eingabe]  ➕ Neu hinzufügen`
   - **🗑 Löschen** entfernt die ausgewählte Pose dauerhaft (Bestätigungsdialog wird angezeigt).
4. **Sequenz-Player:** mehrstufige Animationen auswählen und ausführen, optional mit Loop. Den Sequenz-Manager-Dialog erreichen Sie über **🔧 Verwalten**.

![Connection, global controls, pose management, and sequence player stack](../en/screenshots/control_frame.png)

### 4.3 Telemetrie- & Feedback-Panel (rechte Spalte)

- **Steuerungszeile:**
  - Diagrammaktualisierungen pausieren/fortsetzen.
  - Umschalter für das rollierende Fenster.
  - Auswahl der Messgröße (Position, Last, Geschwindigkeit, Temperatur, Spannung, Moving-Flag).
  - Modusumschaltung (Multi-Servo vs. Scope) mit Servo-Auswahl für Letzteres.
  - Servo-Sichtbarkeits-Dropdown mit „Alle/Keine/Leeren"-Helfern.
  
![Display mode, metric selection, and scope controls](../en/screenshots/chart_mode_controls.png)

![Display menu for choosing telemetry metrics](../en/screenshots/chart_select_display_values.png)

![Servo visibility menu with quick actions](../en/screenshots/chart_servos_selection.png)

#### Diagramm-Modi

- **Multi-Servo** (Standard) behält alle aktivierten Servo-Kurven im Diagramm. Verwenden Sie das Dropdown **Servos**, um Gruppen schnell ein-/auszuschalten und Bewegung oder Last zwischen Fingern zu vergleichen.
- **Scope** aktiviert die Auswahl **Scope Servo** und ermöglicht es Ihnen, sich auf einen einzelnen Kanal zu konzentrieren, während Sie weiterhin dieselben Messgrößen-Kontrollkästchen verwenden. Kombinieren Sie diesen Modus mit dem Servo-Sichtbarkeitsmenü (z. B. alle ausblenden und dann den Scope-Servo wieder aktivieren), um eine Ansicht im Oszilloskop-Stil ohne andere Kurven zu erhalten.
- Unabhängig vom Modus zeigt die Telemetrietabelle weiterhin alle Servos an, sodass Sie das fokussierte Diagramm mit dem breiteren Datenausschnitt abgleichen können.
- **Diagrammbereich:** Matplotlib-Diagramm, das die ausgewählte Telemetrie zeigt. Zoom über Schieberegler:
  - **Y-Zoom / Pan:** vertikale Skalierung und Verschiebung.
  - **Zeit-Zoom / Pan:** Fokus auf aktuelle Historie oder ältere Stichproben.
- **Feedback-Tabelle:** scrollbares Raster, das Ziel, Position, Geschwindigkeit, Last, Spannung, Temperatur, Status und Moving-Flags für jeden Servo zusammenfasst.

![Chart controls with zoom/pan sliders and telemetry traces](../en/screenshots/chart_frame.png)

![Feedback table showing live servo metrics](../en/screenshots/feedback_frame.png)

### 4.4 Ausführungs-Log & Statusleiste

Das Log befindet sich unterhalb des Finger-Panels und zeichnet Vorgänge in chronologischer Reihenfolge auf. Die Statusleiste zeigt die letzte Aktion oder Warnung an.

![Execution log and current status bar](../en/screenshots/log_and_last_action_frame.png)

---

## 5. Bedienung der Hand

### 5.1 Verbindung mit der Hardware

1. Versorgen Sie die Servos mit Strom und schließen Sie den USB-Adapter an.
2. Starten Sie die GUI und bestätigen Sie, dass der richtige **Port** automatisch ausgewählt wird (`COM*` unter Windows oder `/dev/tty*` unter Linux/macOS).
3. Klicken Sie auf **▶ Verbinden**. Bei Erfolg ändern sich die Tastenzustände und die Statusleiste wird aktualisiert.
4. Wenn die Verbindung fehlschlägt, prüfen Sie Verkabelung, Stromversorgung und Portzuordnung.

### 5.2 Manuelle Steuerung und Tastenkürzel

- Wählen Sie einen Finger mit den Tasten **1–4** (1 = Ringfinger, 2 = Mittelfinger, 3 = Zeigefinger, 4 = Daumen).
- **Pfeiltasten:** Hoch/Runter verstellen die Position; Links/Rechts verstellen den seitlichen Versatz.
- Gedrückthalten von **Shift** multipliziert die Schrittweite mit 5; **Ctrl** multipliziert mit 10.
- **Q / E:** den ausgewählten Finger vollständig schließen / öffnen.
- **C:** den seitlichen Versatz zentrieren.
- Die Schieberegler auf dem Bildschirm spiegeln die Tastatureingabe in Echtzeit.

![Manual finger control panel with keyboard shortcut overlay](../en/screenshots/manual_finger_control_frame.png)

![Example of fully closing a finger using controls](../en/screenshots/close_finger.png)

![Example of lateral movement adjustment](../en/screenshots/move_finger.png)

### 5.3 Geschwindigkeiten einstellen

- Das Geschwindigkeits-Dropdown pro Finger (1 = langsam, 6 = schnell) steuert die Servogeschwindigkeit.
- Die Auswahl **Global-Speed** synchronisiert alle Fingergeschwindigkeiten.
- Beobachten Sie Geschwindigkeitsänderungen in der Feedback-Tabelle (Zeile `Speed`) während der Bewegung.

### 5.4 Posen anwenden und löschen

1. Stellen Sie die Fingerpositionen mit Schiebereglern oder Tastenkürzeln ein.
2. Geben Sie in der **Posenverwaltung** einen eindeutigen Namen ein und klicken Sie auf **➕ Neu hinzufügen**.
3. Zum Anwenden wählen Sie die Pose im Dropdown aus und klicken auf **✓ Anwenden**.
4. Zum Löschen wählen Sie die Pose im Dropdown aus und klicken auf **🗑 Löschen**. Ein Bestätigungsdialog verhindert ein versehentliches Entfernen.

> Posen speichern nur Servopositionen; die Geschwindigkeiten werden zur Laufzeit durch die GUI-Einstellungen bestimmt.

### 5.5 Sequenzen erstellen und ausführen

1. Klicken Sie im Sequenz-Player auf **🔧 Verwalten**.
2. Im Dialog:
   - Verwenden Sie die Liste **Verfügbare Posen**, um Schritte hinzuzufügen (Doppelklick oder **➕ Hinzufügen** drücken).
   - Passen Sie die Geschwindigkeiten pro Finger über Spinboxen an und legen Sie optionale Schrittverzögerungen fest.
   - Fügen Sie eigene Ruheintervalle über **⏱ Verzögerung** ein.
   - Sortieren Sie die Schritte mit den Tasten ↑/↓ um.
   - Geben Sie einen Namen ein und klicken Sie auf **💾 Sequenz speichern**.
   - Klicken Sie auf **▶ Ausführen**, um ohne Speichern zu testen.
3. Zurück im Hauptfenster wählen Sie die Sequenz aus und drücken **▶ Abspielen**. Aktivieren Sie **Loop** für eine fortlaufende Wiedergabe.

> Sequenzdefinitionen liegen in `data/hand_config.yaml` unter dem Schlüssel `sequences`. Loops werden zur Laufzeit gesteuert, nicht in YAML.

![Sequence manager dialog with available poses and sequence builder](../en/screenshots/sequences_editor.png)

### 5.6 Telemetrie überwachen

- Stellen Sie sicher, dass die gewünschten Messgrößen im Menü **Display** angekreuzt sind.
- Verwenden Sie die Zoom-/Pan-Schieberegler, um sich auf interessante Abschnitte zu konzentrieren.
- Fahren Sie mit der Maus über Diagrammelemente (Standardinteraktionen von Matplotlib), um Werte zu prüfen.
- Die Feedback-Tabelle wird asynchron aktualisiert; hervorgehobene Zellen zeigen kürzliche Änderungen an.
- Wenn das Diagramm unübersichtlich wird, klicken Sie auf **⌫ Leeren**, um die gesammelten Daten zurückzusetzen.

---

## 6. Kommandozeilenschnittstelle (`amazing_hand_cmd.py`)

Die CLI ermöglicht es Ihnen, Posen anzuwenden und Sequenzen direkt von einem Terminal aus abzuspielen, ohne die GUI zu starten. Sie liest dieselbe Datei `data/hand_config.yaml`.

### 6.1 Grundlegende Verwendung

```bash
# List all saved poses and sequences
python amazing_hand_cmd.py --list

# Apply a single pose
python amazing_hand_cmd.py --pose open
python amazing_hand_cmd.py --pose close

# Play a sequence once
python amazing_hand_cmd.py --sequence demo

# Play a sequence in a loop (Ctrl+C to stop)
python amazing_hand_cmd.py --sequence wave --loop
```

### 6.2 Optionen

| Option | Standard | Beschreibung |
|--------|---------|-------------|
| `--pose NAME` | – | die benannte Pose anwenden und dann beenden |
| `--sequence NAME` | – | die benannte Sequenz abspielen und dann beenden |
| `--list` | – | alle Posen und Sequenzen auflisten |
| `--loop` | off | die Sequenz fortlaufend wiederholen bis Ctrl+C |
| `--port PORT` | `/dev/ttyACM0` (Linux) / `COM9` (Win) | seriellen Port überschreiben |
| `--baudrate N` | `1000000` | Baudrate überschreiben |
| `--config PATH` | `data/hand_config.yaml` | Pfad zu einer alternativen Konfigurationsdatei |

### 6.3 Hinweise

- Das Drehmoment wird beim Verbinden **aktiviert** und beim Beenden **deaktiviert**, damit die Servos nach dem Ende des Skripts entspannen.
- Geschwindigkeiten und Verzögerungen pro Schritt verhalten sich identisch zum GUI-Sequenz-Player.
- Das Flag `--loop` kann nur zusammen mit `--sequence` verwendet werden.

---

## 7. Fehlerbehebung

| Symptom | Empfohlene Maßnahme |
|---------|-----------------| 
| **Keine seriellen Ports aufgelistet** | USB-Adapter neu einstecken, Treiber installieren oder die GUI neu starten. |
| **Verbinden-Taste ausgegraut** | Bereits verbunden; klicken Sie zuerst auf **⏹ Trennen**. |
| **Träge Oberfläche beim Größenändern** | Leistungsoptimierungen (entprelltes Resize, gedrosselte Neuzeichnungen) minimieren dies, aber das Schließen unnötiger Fenster kann helfen. |
| **Sequenz bewegt nicht alle Finger** | Prüfen Sie die Geschwindigkeiten pro Schritt und stellen Sie sicher, dass jede Pose alle acht Servowerte enthält. |
| **Blockiert-Anzeige bleibt bestehen** | Untersuchen Sie mechanische Hindernisse; der Blockiert-Status wird ausgelöst, wenn Ziel und Position deutlich voneinander abweichen, ohne dass eine Bewegung erfolgt. |

---

## 8. Anhang

### 8.1 Dateistruktur

```
AmazingHandControl/
├── amazing_hand_gui.py          # GUI application
├── amazing_hand_cmd.py          # CLI tool
├── data/hand_config.yaml        # Poses & sequences
├── data/config.yaml             # Application settings
├── docs/<lang>/user_manual.md        # This document
├── docs/<lang>/CONFIG_FORMAT.md      # YAML config file reference
├── docs/en/screenshots/              # PNG captures embedded in this manual
├── docs/<lang>/scs_servo_protocol.md # SCS servo protocol reference
└── README.md                    # Quick reference
```

### 8.2 Nützliche Links

- [AmazingHand (offizielles Projekt)](https://github.com/pollen-robotics/AmazingHand)
- [Feetech Servo Debug Tool](https://github.com/Robot-Maker-SAS/FeetechServo/tree/main/feetech%20debug%20tool%20master/FD1.9.8.2)
- [Tutorial zur Servo-Identifikation](https://www.robot-maker.com/forum/tutorials/article/168-brancher-et-controler-le-servomoteur-feetech-sts3032-360/)

---

## 9. Revisionshistorie

| Datum | Autor | Anmerkungen |
|------|--------|-------|
| 2026-03-22 | Ingo | Abschnitt zur CLI (`amazing_hand_cmd.py`) hinzugefügt; Version des Handbuchs erhöht. |
| 2026-03-21 | Ingo | Panel-Layout aktualisiert: Ring/Zeigefinger getauscht, Daumen nach rechts verschoben, Steuerungsstapel nach links verschoben. Seiten-Schieberegler des Daumens invertiert. Löschen-Pose-Taste zwischen Anwenden und Name hinzugefügt. Port- und Baudrate-Dropdowns sind während einer bestehenden Verbindung nun gesperrt. Das Tastenkürzel 1–4 bildet nun Ringfinger/Mittelfinger/Zeigefinger/Daumen ab. |
| 2025-11-25 | Ingo | Erweiterte Screenshot-Galerie, Erläuterungen zu den Diagramm-Modi und überarbeitete Panel-Rundgänge hinzugefügt. |
| 2025-11-25 | Ingo | Ursprüngliches Handbuch zu UI-Panels, Arbeitsabläufen und Telemetrienutzung. |
