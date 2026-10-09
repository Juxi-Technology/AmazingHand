[English](../en/REQUIREMENTS.md) | Deutsch | [Español](../es/REQUIREMENTS.md) | [Français](../fr/REQUIREMENTS.md) | [Italiano](../it/REQUIREMENTS.md) | [日本語](../ja/REQUIREMENTS.md) | [한국어](../ko/REQUIREMENTS.md) | [Português (BR)](../pt-br/REQUIREMENTS.md) | [Português (PT)](../pt-pt/REQUIREMENTS.md) | [简体中文](../zh-hans/REQUIREMENTS.md) | [繁體中文](../zh-hant/REQUIREMENTS.md)

# AmazingHandGUI — Anforderungen & Abnahmekriterien

Dieses Dokument hält die funktionalen Anforderungen und Abnahmekriterien fest,
die aus der aktuellen Implementierung abgeleitet sind. Jede Anforderung verweist auf
die Quelldatei(en), in der bzw. denen das Verhalten implementiert ist.

---

## 1. Verbindungsverwaltung

### FR-CONN-1: Auswahl des seriellen Ports
Die GUI bietet ein Kombinationsfeld, das automatisch erkannte serielle Ports auflistet.

| AC | Kriterium |
|----|-----------|
| 1.1 | Unter Linux erscheinen Geräte `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`; existieren keine, werden `/dev/ttyACM0` und `/dev/ttyUSB0` als Ausweichoptionen aufgelistet. |
| 1.2 | Unter Windows werden `COM1`–`COM20` aufgelistet. |
| 1.3 | Der Standard entspricht dem plattformspezifischen Wert aus `config.yaml` (`/dev/ttyACM0` oder `COM9`). |

### FR-CONN-2: Auswahl der Baudrate
Ein Kombinationsfeld bietet konfigurierbare Baudrate-Optionen.

| AC | Kriterium |
|----|-----------|
| 2.1 | Die Optionen stammen aus `config.yaml` → `serial.baudrate_options` (Standard `[9600, 115200, 1000000]`). |
| 2.2 | Die Standardauswahl ist `1000000`. |
| 2.3 | Das Dropdown ist während einer bestehenden Verbindung deaktiviert. |

### FR-CONN-3: Verbinden / Trennen
Die Tasten Verbinden und Trennen verwalten die serielle Verbindung und das Servo-Drehmoment.

| AC | Kriterium |
|----|-----------|
| 3.1 | Verbinden öffnet den seriellen Port, aktiviert das Drehmoment an den Servos 1–8, deaktiviert die Bedienelemente Verbinden/Port/Baudrate und aktiviert Trennen. |
| 3.2 | Trennen deaktiviert das Drehmoment an allen 8 Servos, aktiviert Verbinden/Port/Baudrate wieder und deaktiviert Trennen. |
| 3.3 | Ein Verbindungsfehler zeigt einen Fehler in der Statusleiste und im Log an; die GUI bleibt getrennt. |

### FR-CONN-4: Automatisches Verbinden beim Start
Die GUI versucht 100 ms nach dem Start automatisch zu verbinden.

| AC | Kriterium |
|----|-----------|
| 4.1 | `connect_controller()` wird während der Initialisierung über `root.after(100, …)` aufgerufen. |

### FR-CONN-5: CLI-Verbindung
Die CLI verbindet über die Argumente `--port` und `--baudrate`.

| AC | Kriterium |
|----|-----------|
| 5.1 | `--port` und `--baudrate` überschreiben die Standardwerte. |
| 5.2 | Beim Verbinden wird das Drehmoment an allen 8 Servos aktiviert. |
| 5.3 | Beim Beenden wird das Drehmoment deaktiviert (einschließlich Ctrl+C über einen `finally`-Block). |
| 5.4 | `--list` öffnet **keine** Hardwareverbindung. |

---

## 2. Fingersteuerung

### FR-FING-1: Vier Finger-Widgets
Es werden vier Finger-Bedienelemente angezeigt: Ringfinger, Mittelfinger, Zeigefinger, Daumen — jeweils mit 2 Servos.

| AC | Kriterium |
|----|-----------|
| 1.1 | Genau 4 `FingerControl`-Widgets werden gerendert, mit Namen passend zu den Servopaaren aus `config.yaml`: Ringfinger (5,6), Mittelfinger (3,4), Zeigefinger (1,2), Daumen (7,8). |

### FR-FING-2: Auto-Modus (Base + Side)
Der Auto-Modus bietet einen vertikalen Schließen/Öffnen-Schieberegler und einen horizontalen Seitwärts-Schieberegler.

| AC | Kriterium |
|----|-----------|
| 2.1 | Vertikaler Schieberegler: 0° (offen) bis 110° (geschlossen); oben = geschlossen, unten = offen. |
| 2.2 | Horizontaler Schieberegler: −40° bis +40°. |
| 2.3 | Das Bewegen eines der beiden Schieberegler sendet interpolierte Positionen (über `compute_auto_positions`) an beide Servos. |

### FR-FING-3: Raw-Modus
Der Raw-Modus zeigt zwei unabhängige vertikale Schieberegler (einen pro Servo).

| AC | Kriterium |
|----|-----------|
| 3.1 | Die Auswahl von Raw blendet die Auto-Schieberegler aus und zeigt zwei vertikale Schieberegler pro Servo (−40 bis 110). |
| 3.2 | Das Mimic-Kontrollkästchen ist deaktiviert und nicht angekreuzt; die Taste Zentrieren ist deaktiviert. |
| 3.3 | Der Moduswechsel synchronisiert die Werte bidirektional (auto ↔ raw über `decompose_servo_positions`). |

### FR-FING-4: Geschwindigkeitssteuerung
Jeder Finger hat ein Geschwindigkeits-Kombinationsfeld (1–6).

| AC | Kriterium |
|----|-----------|
| 4.1 | Der Bereich reicht von `speeds.min` (1) bis `speeds.max` (6), Standard `speeds.default` (3). |
| 4.2 | Die Geschwindigkeit wird über `write_goal_speed()` pro Servo vor den Positionsbefehlen gesendet. |

### FR-FING-5: Mimic-Modus
Schließen-/Öffnen-Änderungen an einem nachahmenden Finger werden an alle anderen Finger mit aktiviertem Mimic weitergegeben.

| AC | Kriterium |
|----|-----------|
| 5.1 | Wird Mimic bei A und B aktiviert, werden Änderungen am Schließen-/Öffnen-Schieberegler von A auf B gespiegelt und umgekehrt. |
| 5.2 | Mimic gilt nur im Auto-Modus; der Wechsel zu Raw deaktiviert es. |

### FR-FING-6: Zentrieren-Taste
Setzt den Seitenversatz auf 0° zurück.

| AC | Kriterium |
|----|-----------|
| 6.1 | Ein Klick auf Zentrieren setzt `side_var` auf 0 und löst eine Positionsaktualisierung aus. |
| 6.2 | Zentrieren ist im Raw-Modus deaktiviert. |

### FR-FING-7: Mausrad am Positions-Schieberegler
Das Scrollrad verstellt die Position um ±5°.

| AC | Kriterium |
|----|-----------|
| 7.1 | Nach oben scrollen → +5° (schließen), nach unten scrollen → −5° (öffnen), begrenzt auf die Grenzwerte. |

### FR-FING-8: LED-Aktivitätsanzeige
Jeder Finger zeigt eine Status-LED.

| AC | Kriterium |
|----|-----------|
| 8.1 | In Bewegung (moving-Flag = true) → blinkendes Grün im Intervall von ~350 ms. |
| 8.2 | Blockiert (Fehler zwischen Ziel und Position ≥ 8° und keine Bewegung) → dauerhaftes Rot. |
| 8.3 | Untätig → grau. |

---

## 3. Tastatursteuerung

### FR-KEY-1: Fingerauswahl
Die Tasten 1–4 wählen den aktiven Finger.

| AC | Kriterium |
|----|-----------|
| 1.1 | 1 = Ringfinger, 2 = Mittelfinger, 3 = Zeigefinger, 4 = Daumen. |
| 1.2 | Die Statusleiste zeigt den Namen des ausgewählten Fingers. |

### FR-KEY-2: Bewegung mit den Pfeiltasten
Die Pfeiltasten bewegen den ausgewählten Finger.

| AC | Kriterium |
|----|-----------|
| 2.1 | Hoch = schließen (Position erhöhen), Runter = öffnen (verringern). |
| 2.2 | Rechts = Seitenversatz erhöhen, Links = verringern. |

### FR-KEY-3: Präzisionsmodifikatoren
Die Schrittweite variiert je nach Modifikatortaste.

| AC | Kriterium |
|----|-----------|
| 3.1 | Kein Modifikator: 1° (präzise). |
| 3.2 | Shift: 5° (normal). |
| 3.3 | Ctrl: 10° (schnell). |
| 3.4 | Die Statusleiste zeigt den Modusnamen und den resultierenden Winkel. |

### FR-KEY-4: Schnellaktionen
Eintastige Tastenkürzel für häufige Aktionen.

| AC | Kriterium |
|----|-----------|
| 4.1 | Q = vollständig auf 110° schließen. |
| 4.2 | E = vollständig auf 0° öffnen. |
| 4.3 | C = Seite auf 0° zentrieren. |

---

## 4. Globale Steuerung

### FR-GLOB-1: Alle öffnen
Setzt alle Finger auf vollständig offen.

| AC | Kriterium |
|----|-----------|
| 1.1 | Alle `pos_var` → 0, alle `side_var` → 0, Positionen an die Hardware gesendet. |

### FR-GLOB-2: Alle schließen
Setzt alle Finger auf vollständig geschlossen.

| AC | Kriterium |
|----|-----------|
| 2.1 | Alle `pos_var` → 110, alle `side_var` → 0, Positionen gesendet. |

### FR-GLOB-3: Alle zentrieren
Setzt alle Seitenversätze zurück.

| AC | Kriterium |
|----|-----------|
| 3.1 | Alle `side_var` → 0, Positionen gesendet. |

### FR-GLOB-4: Globale Geschwindigkeit
Ein Dropdown setzt alle Fingergeschwindigkeiten auf einmal.

| AC | Kriterium |
|----|-----------|
| 4.1 | Die Auswahl eines Werts aktualisiert jedes Geschwindigkeits-Kombinationsfeld pro Finger. |
| 4.2 | Geschwindigkeit auf [1, 6] begrenzt. |

---

## 5. Posenverwaltung

### FR-POSE-1: Pose speichern
Der Benutzer gibt einen Namen ein und speichert die aktuellen 8-Servopositionen.

| AC | Kriterium |
|----|-----------|
| 1.1 | Die Positionen aller 4 Finger (8 Werte) werden über `get_positions()` erfasst. |
| 1.2 | Der Name wird vor dem Speichern über `validate_name()` validiert. |
| 1.3 | Bei Erfolg: das Dropdown wird aktualisiert (sortiert), das Eingabefeld wird geleert, die Statusleiste bestätigt. |
| 1.4 | Ein ungültiger oder leerer Name zeigt ein Fehler-Dialogfeld. |

### FR-POSE-2: Pose anwenden
Das Auswählen einer Pose und Klicken auf Anwenden bewegt die Hand in diese Pose.

| AC | Kriterium |
|----|-----------|
| 2.1 | Die 8 Positionen werden auf alle Finger-Widgets angewendet. |
| 2.2 | Die Servopositionen werden an die Hardware gesendet. |
| 2.3 | Die Verzögerung wird aus Bewegungsweg und Geschwindigkeit geschätzt; der Posenabschluss wird nach dieser Verzögerung mit einem Vergleich Ziel vs. Ist protokolliert. |

### FR-POSE-3: Pose löschen
Entfernt die ausgewählte Pose nach Bestätigung.

| AC | Kriterium |
|----|-----------|
| 3.1 | Ein Ja/Nein-Dialogfeld fragt nach einer Bestätigung. |
| 3.2 | Bei Bestätigung: die Pose wird aus der Konfiguration entfernt, die YAML gespeichert, das Dropdown aktualisiert. |
| 3.3 | Wenn keine Posen verbleiben, zeigt das Dropdown `<no poses>`. |

### FR-POSE-4: Namensvalidierung
Namen werden validiert, um eine Beschädigung der YAML zu verhindern.

| AC | Kriterium |
|----|-----------|
| 4.1 | Leer / nur Leerzeichen → abgelehnt. |
| 4.2 | Länger als 50 Zeichen → abgelehnt. |
| 4.3 | Enthält `: { } [ ] , & * # ? \| - < > = ! % @ \` " '` → abgelehnt. |
| 4.4 | Enthält Steuerzeichen (ASCII < 32) → abgelehnt. |
| 4.5 | Führende/abschließende Leerzeichen → abgelehnt. |

---

## 6. Sequenzverwaltung

### FR-SEQ-1: Sequenz-Player (Hauptfenster)
Dropdown-Auswahl, Loop-Kontrollkästchen, Tasten Abspielen / Pause / Stop.

| AC | Kriterium |
|----|-----------|
| 1.1 | Das Dropdown listet alle gespeicherten Sequenzen auf (oder `<no sequences>`). |
| 1.2 | Das Loop-Kontrollkästchen aktiviert die fortlaufende Wiederholung. |
| 1.3 | Abspielen startet die Sequenz in einem Hintergrund-Thread. |
| 1.4 | Pause schaltet zwischen Pausiert/Fortgesetzt um; der Tastentext wechselt zwischen „⏸ Pause" und „▶ Fortsetzen". |
| 1.5 | Stop setzt `stop_sequence = True`; der Sequenz-Thread wird beendet. |

### FR-SEQ-2: Sequenz-Ausführungsengine
Sequenzen laufen in einem Hintergrund-Thread mit unterbrechbaren Ruhephasen.

| AC | Kriterium |
|----|-----------|
| 2.1 | Posenschritte parsen das Format `"pose_name:s1,s2,...,s8\|delay"`. |
| 2.2 | `SLEEP:duration`-Schritte pausieren ohne Hardwarebefehle. |
| 2.3 | Ohne explizite Verzögerung: Auto-Wartezeit = `15.0 − (avg_speed − 1) × 2.4` Sekunden. |
| 2.4 | Ruhephasen laufen in 0.1-s-Schritten ab und prüfen bei jedem Takt die Stop-/Pause-Flags. |
| 2.5 | Im Loop-Modus trennt eine Lücke von 0.5 s die Iterationen. |
| 2.6 | Unbekannte Posennamen werden mit einer Warnung übersprungen. |
| 2.7 | Die Tasten Abspielen/Pause/Stop wechseln während der Ausführung zwischen aktiviert/deaktiviert. |

### FR-SEQ-3: Sequenz-Manager-Dialog
Zweigeteilter Dialog, erreichbar über die Taste „🔧 Verwalten".

| AC | Kriterium |
|----|-----------|
| 3.1 | Linkes Panel: Listenfeld der gespeicherten Sequenzen mit den Tasten Ausführen, Bearbeiten, Löschen. |
| 3.2 | Ein Doppelklick führt die Sequenz einmal aus (ohne Loop), ohne den Dialog zu schließen. |
| 3.3 | Bearbeiten lädt die Schritte in den Builder und füllt das Namensfeld vor. |

### FR-SEQ-4: Sequenz-Builder
Rechtes Panel zum Zusammenstellen von Sequenzen aus Posen.

| AC | Kriterium |
|----|-----------|
| 4.1 | Verfügbare Posen werden aufgelistet; ein Doppelklick fügt einen Schritt mit aktueller Geschwindigkeit/Verzögerung hinzu. |
| 4.2 | Geschwindigkeits-Spinboxen pro Finger (1–6); „⬇ Aus UI kopieren" importiert die Geschwindigkeiten des Hauptfensters. |
| 4.3 | Die Verzögerungseingabe hängt das Suffix `\|delay` an Posenschritte an. |
| 4.4 | „⏱ Verzögerung" fügt einen eigenständigen Schritt `SLEEP:Xs` ein. |
| 4.5 | ↑/↓ umsortieren, ➖ entfernen, 🗑 alles leeren. |
| 4.6 | „💾 Sequenz speichern" validiert den Namen, speichert und aktualisiert die Dropdowns. |
| 4.7 | „▶ Ausführen" führt die erstellte Sequenz aus, ohne zu speichern oder den Dialog zu schließen. |

### FR-SEQ-5: Validierung der Verzögerungseingabe
Ungültige Gleitkommawerte in der Verzögerungseingabe werden fehlerfrei behandelt.

| AC | Kriterium |
|----|-----------|
| 5.1 | Eine nicht numerische Verzögerung führt standardmäßig zu keiner Verzögerung (Schritt ohne `\|delay` hinzugefügt). |
| 5.2 | Eine nicht numerische SLEEP-Verzögerung zeigt „Invalid delay value" in der Statusleiste an. |

---

## 7. Servo-Überwachung

### FR-MON-1: Telemetrieerfassung im Hintergrund
Ein Daemon-Thread fragt alle 8 Servos mit ~10 Hz ab.

| AC | Kriterium |
|----|-----------|
| 1.1 | Der Thread wartet 0.1 s zwischen den Iterationen. |
| 1.2 | Pro Servo erfasste Messgrößen: Position, Last, Temperatur, Spannung, Geschwindigkeit, Moving-Flag, Status, Ziel. |
| 1.3 | Ein fehlgeschlagenes Lesen wiederholt den zuletzt bekannten Wert, um die Arrays synchron zu halten. |
| 1.4 | Die Feedback-Daten werden unter `feedback_lock` atomar aktualisiert. |

### FR-MON-2: Diagrammanzeige
Ein in das rechte Panel eingebettetes Matplotlib-Diagramm.

| AC | Kriterium |
|----|-----------|
| 2.1 | Auswählbare Messgrößen: Position, Ziel vs. Ist, Drehmoment, Geschwindigkeit, Temperatur, Spannung, Bewegung. |
| 2.2 | Das Dropdown „Servos" schaltet um, welche der 8 Kurven sichtbar sind (mit ✓ Alle / ✕ Keine). |
| 2.3 | Diagramm-Neuzeichnungen werden auf ≥100 ms Abstand gedrosselt. |
| 2.4 | Keine Messgröße ausgewählt → Meldung „Select at least one metric". |
| 2.5 | Keine Daten → Meldung „Waiting for data...". |

### FR-MON-3: Diagramm-Modi
Zwei Modi: Multi-Servo und Scope.

| AC | Kriterium |
|----|-----------|
| 3.1 | Der Scope-Modus zeigt eine Auswahl „Scope Servo", um sich auf einen einzelnen Servo zu konzentrieren. |
| 3.2 | Multi-Servo blendet die Auswahl Scope Servo aus. |

### FR-MON-4: Diagramm-Zoom & Pan
Vier Schieberegler zur Steuerung der Ansicht.

| AC | Kriterium |
|----|-----------|
| 4.1 | Y-Zoom: 0.2× bis 5.0×, Standard 1.1×. |
| 4.2 | Y-Pan: −3.0 bis +3.0, Standard 0.0. |
| 4.3 | Zeit-Zoom: 10 % bis 100 % der verfügbaren Daten. |
| 4.4 | Zeit-Pan: 0 % (früheste) bis 100 % (neueste). |
| 4.5 | Alle Schieberegler lösen entprellte Diagramm-Neuzeichnungen aus. |

### FR-MON-5: Rolling-Modus
Begrenzt das Diagramm auf die neuesten N Datenpunkte.

| AC | Kriterium |
|----|-----------|
| 5.1 | Wenn aktiviert und die Daten `max_data_points` (100) überschreiten, werden die ältesten Stichproben verworfen. |
| 5.2 | Das Deaktivieren von Rolling behält alle gesammelten Daten. |

### FR-MON-6: Pause / Fortsetzen / Diagramm leeren

| AC | Kriterium |
|----|-----------|
| 6.1 | Pause stoppt die Diagramm-Neuzeichnungen; die Telemetrieerfassung läuft weiter. |
| 6.2 | Leeren setzt alle Datenarrays und Zoom/Pan auf die Standardwerte zurück. |

### FR-MON-7: Feedback-Panel
Rastertabelle mit Live-Telemetrie für alle Servos.

| AC | Kriterium |
|----|-----------|
| 7.1 | Spalten: S1–S8. Zeilen: Ziel, Position, Geschwindigkeit, Drehmoment, Spannung, Strom, Temperatur, Status, Bewegung. |
| 7.2 | Werte formatiert durch `format_feedback_value()`: Position `X.XX°`, Geschwindigkeit `X.X°/s`, Spannung `X.XX V`, Temperatur `X.X °C`, Strom `X mA`, Last `X.X %`, Status `0xHH`, Bewegung `Yes/No`. |
| 7.3 | Nur geänderte Zellen werden aktualisiert (Diff-Cache). |
| 7.4 | Die Aktualisierung wird auf ≥50 ms zwischen den Updates gedrosselt. |

---

## 8. Konfiguration

### FR-CFG-1: Laden der App-Konfiguration
`config.yaml` wird geladen, wobei alle fehlenden Schlüssel mit Standardwerten belegt werden.

| AC | Kriterium |
|----|-----------|
| 1.1 | Fehlende Datei → vollständige Standardkonfiguration wird verwendet. |
| 1.2 | Fehlende Schlüssel werden aus den Standardwerten zusammengeführt (zweistufiges Zusammenführen). |
| 1.3 | Parse-Fehler → Standardwerte werden zurückgegeben, der Fehler wird auf stdout ausgegeben. |

### FR-CFG-2: Servozuordnung
Die Servo-IDs pro Finger sind in `config.yaml` → `servos` definiert.

| AC | Kriterium |
|----|-----------|
| 2.1 | Die Konfiguration definiert pointer=[1,2], middle=[3,4], ring=[5,6], thumb=[7,8]. |
| 2.2 | `all_ids` = [1,2,3,4,5,6,7,8]. |

### FR-CFG-3: Winkelgrenzen

| AC | Kriterium |
|----|-----------|
| 3.1 | `servo_min` = −40, `servo_max` = 110, `base_min` = 0, `base_max` = 110, `side_min` = −40, `side_max` = 40. |
| 3.2 | Alle Schieberegler-Bereiche leiten sich aus diesen Werten ab. |

### FR-CFG-4: Auto-Extremwerte
Bilineare Interpolationsendpunkte für die Berechnung des Seitenversatzes.

| AC | Kriterium |
|----|-----------|
| 4.1 | `left_open`, `right_open`, `left_closed`, `right_closed`, `center_open`, `center_closed` sind konfigurierbar. |
| 4.2 | `compute_auto_positions()` verwendet diese für die Interpolation. |

### FR-CFG-5: Geschwindigkeitskonfiguration

| AC | Kriterium |
|----|-----------|
| 5.1 | `speeds.default` = 3, `speeds.min` = 1, `speeds.max` = 6. |

---

## 9. CLI-Werkzeug

### FR-CLI-1: Posen und Sequenzen auflisten
`--list` gibt alle Posen und Sequenzen aus, ohne eine Verbindung zu öffnen.

| AC | Kriterium |
|----|-----------|
| 1.1 | Die Ausgabe zeigt die Anzahl der Posen und jeden Namen mit Positionen. |
| 1.2 | Die Ausgabe zeigt die Anzahl der Sequenzen und jeden Namen mit Schrittanzahl und Details. |
| 1.3 | Es wird keine serielle Verbindung geöffnet. |

### FR-CLI-2: Pose anwenden
`--pose NAME` sendet eine gespeicherte Pose an die Hardware.

| AC | Kriterium |
|----|-----------|
| 2.1 | Positionen werden aus der Konfiguration geladen; die Standardgeschwindigkeit 3 wird auf alle Servos angewendet. |
| 2.2 | Unbekannte Pose → Fehler + `sys.exit(1)`. |

### FR-CLI-3: Sequenz abspielen
`--sequence NAME` spielt eine Sequenz ab; `--loop` wiederholt sie bis Ctrl+C.

| AC | Kriterium |
|----|-----------|
| 3.1 | Geschwindigkeiten und Verzögerung werden aus dem Schritt-String geparst. |
| 3.2 | `SLEEP`-Schritte pausieren ohne Hardwarebefehle. |
| 3.3 | Keine explizite Verzögerung → Auto-Wartezeit = `15.0 − (avg_speed − 1) × 2.4` Sekunden. |
| 3.4 | SIGINT setzt `stop_flag` für eine saubere Unterbrechung. |
| 3.5 | Unbekannte Sequenz → Beenden mit Fehler. |
| 3.6 | Leere Sequenz → Beenden mit Fehler. |
| 3.7 | Unbekannte Posen innerhalb einer Sequenz werden mit einer WARNING übersprungen. |

### FR-CLI-4: Schritt-Parsing
`parse_step()` verarbeitet mehrere Formate.

| AC | Kriterium |
|----|-----------|
| 4.1 | `SLEEP:2.0s` → Ruhephase von 2.0 s. |
| 4.2 | `open:3,3,...\|2.0s` → Pose „open" mit Geschwindigkeiten und 2.0 s Verzögerung. |
| 4.3 | `open` (bloßer Name) → Pose mit Standardgeschwindigkeiten, ohne Verzögerung. |
| 4.4 | Weniger als 8 Geschwindigkeiten werden mit 3 aufgefüllt; mehr werden abgeschnitten. |
| 4.5 | Das Suffix `s` / `S` für die Dauer wird entfernt. |

### FR-CLI-5: Sich gegenseitig ausschließende Aktionen
`--list`, `--pose` und `--sequence` schließen sich gegenseitig aus.

| AC | Kriterium |
|----|-----------|
| 5.1 | Mehrere Aktionen angeben → Exit ungleich null. |
| 5.2 | `--loop` ohne `--sequence` → Fehler. |

### FR-CLI-6: Überschreiben der Konfigurationsdatei
`--config PATH` verwendet eine alternative YAML-Datei.

| AC | Kriterium |
|----|-----------|
| 6.1 | Fehlende Datei → Fehler + `sys.exit(1)`. |

---

## 10. Datenpersistenz

### FR-DATA-1: YAML-Konfigurationsdatei
Posen und Sequenzen werden in `data/hand_config.yaml` gespeichert.

| AC | Kriterium |
|----|-----------|
| 1.1 | Die Datei verwendet das YAML-Format mit den Schlüsseln `poses` und `sequences` auf oberster Ebene. |

### FR-DATA-2: Konfiguration laden

| AC | Kriterium |
|----|-----------|
| 2.1 | Fehlende Datei → `{'poses': {}, 'sequences': {}}`. |
| 2.2 | Leere Datei → Schlüssel werden automatisch befüllt. |
| 2.3 | Fehlerhafte YAML → leere Struktur, Fehler wird auf stdout ausgegeben. |

### FR-DATA-3: Konfiguration mit Inline-Arrays speichern
Positionen werden über Regex-Nachbearbeitung im Flow-Stil gespeichert.

| AC | Kriterium |
|----|-----------|
| 3.1 | Die Datei enthält den Stil `positions: [v1, v2, …, v8]`. |
| 3.2 | Negative Werte bleiben im Inline-Format erhalten. |
| 3.3 | Gibt bei Erfolg `True` zurück, bei Fehler `False`. |

### FR-DATA-4: Automatische Erstellung des Datenverzeichnisses

| AC | Kriterium |
|----|-----------|
| 4.1 | Das Verzeichnis `data/` wird vor dem Schreiben erstellt, falls es nicht existiert. |

### FR-DATA-5: Integrität des Hin- und Rücklaufs
Von der GUI geschriebene Daten können von der CLI gelesen werden und umgekehrt.

| AC | Kriterium |
|----|-----------|
| 5.1 | Posen, negative Positionen und Sequenzschritte überstehen einen Hin- und Rücklauf GUI-Speichern → CLI-Lesen. |

---

## 11. Fehlerbehandlung

### FR-ERR-1: Verbindungsfehler
Fehlgeschlagene Verbindungen bringen die Anwendung nicht zum Absturz.

| AC | Kriterium |
|----|-----------|
| 1.1 | Die Statusleiste zeigt „Connection failed: …"; `connected` bleibt `False`. |

### FR-ERR-2: Ungültige Baudrate

| AC | Kriterium |
|----|-----------|
| 2.1 | Nicht numerische Baudrate → die Statusleiste zeigt „Invalid baudrate". |

### FR-ERR-3: Wiederherstellung des Überwachungs-Threads

| AC | Kriterium |
|----|-----------|
| 3.1 | Ein einzelner fehlgeschlagener Servo-Lesevorgang bringt den Thread nicht zum Absturz. |
| 3.2 | Fehler werden auf stdout ausgegeben. |

### FR-ERR-4: Degradation des Moving-Flags

| AC | Kriterium |
|----|-----------|
| 4.1 | Nach 3 aufeinanderfolgenden `read_moving`-Fehlern wird die Überwachung mit einer Log-Meldung deaktiviert. |
| 4.2 | Beim ersten Sync-Fehler wird von `sync_read_moving` auf Lesevorgänge pro Servo zurückgegriffen. |

### FR-ERR-5: Warnungen zum Posenabschluss

| AC | Kriterium |
|----|-----------|
| 5.1 | Ein Fehler Ziel vs. Ist > 5° löst eine ⚠-Warnung im Log aus. |
| 5.2 | Ein Bewegungstimeout (6.0 s) löst eine Timeout-Warnung aus, wenn die Servos nie aufhören, sich zu bewegen. |

### FR-ERR-6: Fehlende Konfiguration (CLI)

| AC | Kriterium |
|----|-----------|
| 6.1 | Fehlende Konfigurationsdatei → Fehlermeldung + `sys.exit(1)`. |

### FR-ERR-7: Leere / ungültige Sequenz

| AC | Kriterium |
|----|-----------|
| 7.1 | Leere Sequenzschritte → `sys.exit(1)`. |
| 7.2 | Unbekannte Posen in der Sequenz → mit WARNING übersprungen. |

---

## 12. UI-Layout

### FR-UI-1: Fensterstruktur

| AC | Kriterium |
|----|-----------|
| 1.1 | Der Titel enthält die Version: „AmazingHand Controller v0.8". |
| 1.2 | Anfangsgeometrie: 1920×1200. |
| 1.3 | Ein horizontales `PanedWindow` trennt das linke (Bedienelemente) und das rechte (Diagramm) Panel. |

### FR-UI-2: Linkes Panel

| AC | Kriterium |
|----|-----------|
| 2.1 | Zeile 1: Ringfinger, Mittelfinger, Zeigefinger (3 Finger nebeneinander). |
| 2.2 | Zeile 2: Daumen (rechts) + gestapelte Bedienelemente (Verbindung, Global, Pose, Sequenz). |
| 2.3 | Das Ausführungs-Log unterhalb der Bedienelemente in einem in der Größe veränderbaren vertikalen Splitter. |

### FR-UI-3: Statusleiste

| AC | Kriterium |
|----|-----------|
| 3.1 | Aktualisierungen bei Verbinden, Trennen, Fingerauswahl, Geschwindigkeitsänderung, Posenoperationen und Fehlern. |

### FR-UI-4: Ausführungs-Log

| AC | Kriterium |
|----|-----------|
| 4.1 | Meldungen mit dem Zeitstempel `[HH:MM:SS.mmm]` als Präfix. |
| 4.2 | Scrollt automatisch zum neuesten Eintrag. |
| 4.3 | Meldungen werden zusätzlich auf stdout ausgegeben. |

### FR-UI-5: Tooltips

| AC | Kriterium |
|----|-----------|
| 5.1 | Ein gelbes Popup erscheint nach 500 ms Hover, rechts unterhalb des Widgets positioniert. |
| 5.2 | Verschwindet beim Verlassen der Maus oder beim Tastendruck. |

### FR-UI-6: Rechtes Panel (Diagrammbereich)

| AC | Kriterium |
|----|-----------|
| 6.1 | Vertikales `PanedWindow`: Diagramm oben (min. 200 px), Feedback unten (min. 150 px). |
| 6.2 | Zeit-Schieberegler unterhalb des Diagramms; Y-Schieberegler rechts. |

### FR-UI-7: CLI-Hilfe

| AC | Kriterium |
|----|-----------|
| 7.1 | `--help` beendet mit 0 und zeigt alle Optionen. |

### FR-UI-8: GUI-Kommandozeilenargumente

| AC | Kriterium |
|----|-----------|
| 8.1 | `--port` überschreibt den standardmäßigen seriellen Port. |
| 8.2 | `--baudrate` überschreibt die standardmäßige Baudrate (1000000). |

---

## Zusammenfassung der Testabdeckung

| Testdatei | Umfang | Anzahl |
|-----------|-------|-------|
| `tests/test_hand_logic.py` | `load_app_config` (6), `servo_mapping` (3), `angle_limits` (1), `auto_extremes` (2), `speed_config` (1), `default_serial_port` (2), `ensure_data_dir` (2), `load_pose_definitions` (3), `compute_auto_positions` (6), `decompose_servo_positions` (5), `coerce_numeric` (11), `coerce_angle_degrees` (6), `coerce_bool` (6), `load_to_percent` (7), `estimate_current_from_load` (5), `format_feedback_value` (12), `get_time_window_indices` (8), `angle_rad` (3) | 89 |
| `tests/test_gui_utils.py` | `validate_name` (21), `clamp` (8), `load_config` (6), `save_config` (6) | 41 + 10 parametrisiert |
| `tests/test_cmd.py` | `angle_rad` (8), `parse_step` (11), `cmd_list` (4), `load_config` (2), `apply_pose` (6), `_interruptible_sleep` (2), `auto_wait` (3), `mutual_exclusion` (1), `config_override` (2) | 41 |
| `tests/test_integration.py` | `cmd_pose` e2e (5), `cmd_sequence` e2e (6), config round-trip (3) | 14 |
| `tests/test_system.py` | CLI-Subprozess: `--help` (5), `--list` (9), `--help` options (3), error paths (5) | 22 |
| `tests/test_system_hardware.py` | Echte Hardware: connect (2), CLI connection (2), pose apply (3), speed (2), telemetry (6), sequence (2), error recovery (1), movement (2), disconnect (1) — **erfordert das Flag `--hardware`** | 21 |
| **Gesamt (ohne Hardware)** | **217 Tests** |
| **Gesamt (mit Hardware)** | **238 Tests** |
