[English](../en/CHANGES.md) | Deutsch | [Español](../es/CHANGES.md) | [Français](../fr/CHANGES.md) | [Italiano](../it/CHANGES.md) | [日本語](../ja/CHANGES.md) | [한국어](../ko/CHANGES.md) | [Português (BR)](../pt-br/CHANGES.md) | [Português (PT)](../pt-pt/CHANGES.md) | [简体中文](../zh-hans/CHANGES.md) | [繁體中文](../zh-hant/CHANGES.md)

# AmazingHand Controller · Änderungsprotokoll & Begründung

Was gegenüber dem ursprünglichen Projekt geändert wurde, warum, und was das Ergebnis tatsächlich ist.

Ursprüngliches Projekt: `Betatester777/AmazingHandControl` (Python-GUI + CLI für den AmazingHand)
Hardware: JuxiTechnology AmazingHand (8× Feetech SCS0009 Servos, Potentiometer-Feedback) — **beide Hände unterstützt**, Auswahl beim Start

---

## Inhalt

1. [Neukalibrierung des Winkelsystems](#1-neukalibrierung-des-winkelsystems)
2. [Globale Tasten: exakte Rohpositionen anfahren](#2-globale-tasten-exakte-rohpositionen-anfahren)
3. [Neue Taste „Mittelposition"](#3-neue-taste-mittelposition)
4. [GUI und CLI weichen voneinander ab (der Kernfehler)](#4-gui-und-cli-weichen-voneinander-ab-der-kernfehler)
5. [Korrekturen der Pose-Daten](#5-korrekturen-der-pose-daten)
6. [Sequenz-Player: Timing und Diagnose](#6-sequenz-player-timing-und-diagnose)
7. [Neue Zeile für Rohposition in der Servo-Rückmeldung](#7-neue-zeile-für-rohposition-in-der-servo-rückmeldung)
8. [**Unterstützung für linke und rechte Hand**](#8-unterstützung-für-linke-und-rechte-hand)
9. [Automatische Erkennung des seriellen Ports](#9-automatische-erkennung-des-seriellen-ports)
10. [Konfigurationsreferenz](#10-konfigurationsreferenz)
11. [Gemessene Ergebnisse](#11-gemessene-ergebnisse)
12. [Zusammenfassung Datei für Datei](#12-zusammenfassung-datei-für-datei)

---

## 1. Neukalibrierung des Winkelsystems

### 1.1 Winkelgrenzen: `0..110` → `-75..75`

Das Original war auf `0° = offen, 110° = geschlossen` kalibriert. Der tatsächliche Verfahrweg dieser Hand liegt in `-75..75`, daher wurde alles neu kalibriert.

**`data/config.yaml`**

| Schlüssel | Vorher | Nachher |
|---|---|---|
| `servo_min` / `servo_max` | -40 / 110 | **-75 / 75** |
| `base_min` / `base_max` | 0 / 110 | **-75 / 75** |
| `side_min` / `side_max` | -40 / 40 | **-35 / 35** |
| `left_open` | `[32, -40]` | **`[32, -35]`** |
| `right_open` | `[-40, 32]` | **`[-35, 32]`** |
| `left_closed` / `right_closed` | `[110, 110]` | **`[75, 75]`** |
| `center_closed` | `[110, 110]` | **`[75, 75]`** |

**Alle 19 Posen wurden neu skaliert**, z. B. `open` von `[0]*8` auf `[-35]*8`, `close` von `[110]*8` auf `[75]*8`.

### 1.2 Seitliche Spreizung: `±40°` → `±35°`

Der Side-Schieberegler normalisiert mit `u = |side_offset| / |side_min|`; eine Änderung nur der Grenze ändert also **nicht**, wie weit die Finger tatsächlich spreizen — sie skaliert lediglich den Schieberegler neu. Um die physische Spreizung zu ändern, muss zusätzlich `auto_extremes` angepasst werden. Mit beidem geändert:

| | Vorher (±40) | Nachher (±35) |
|---|---|---|
| Schieberegler-Bereich | −40 … +40 | −35 … +35 |
| Vollständig offen, am seitlichen Extrem | `(32, -40)`, Spreizung **72°** | `(32, -35)`, Spreizung **67°** |

### 1.3 Abgleich mit der Referenz des Herstellers

Die Arduino-Demo des Herstellers (`Amazing_RHand_Demo.ino`) rechnet folgendermaßen um:

```c
float Step = 0.293; // 300°/1024
sc.RegWritePos(1, MiddlePos[0] + Pos_1 / Step, 0, Speed);
```

Und rustypot 1.4.2 (`src/servo/feetech/scs0009.rs`):

```rust
fn to_raw(value: f64) -> i16 {
    let a = (1024.0 * value / (300.0_f64.to_radians()) + 511.0) as i16;
    a.to_be()
}
```

**Schlussfolgerung: Beide Seiten verwenden dieselbe Grad-Skala** (0.29297°/Schritt, 300° Vollbereich, raw 0–1023) — es gibt keinen Verhältnisfehler. Der einzige systematische Unterschied ist der Nullpunkt:

- rustypot zentriert immer auf raw **511**
- die Hersteller-Firmware verwendet einen servoindividuellen Kalibrierwert, `MiddlePos = {451, 571, 451, 571, 451, 571, 451, 571}`

Sie unterscheiden sich um **±60 raw = ±17.6°**. Genau das adressiert die unten beschriebene Taste „Mittelposition".

---

## 2. Globale Tasten: exakte Rohpositionen anfahren

### 2.1 Das Problem

Das ursprüngliche `open_all()` / `close_all()` verwendete fest einprogrammierte Winkel:

```python
def open_all(self):
    for finger in self.fingers:
        finger.pos_var.set(0)      # hard-coded 0
        finger.side_var.set(0)
        ...
def close_all(self):
    for finger in self.fingers:
        finger.pos_var.set(110)    # hard-coded 110
```

Diese Werte stammen aus der **alten Kalibrierungsskala** (0 = offen, 110 = geschlossen). Nach der Neukalibrierung auf `-35 / 75`:

- `open_all` setzte 0° → rechnet auf raw **511** um, also ungefähr die mechanische Mitte — die Finger öffneten sich nie
- `close_all` setzte 110° → durch `base_max = 75` begrenzt, erreichte also nur 75, während die Anzeige weiterhin 110° anzeigte

### 2.2 Die Lösung: ein direkter Pfad zur Rohposition

Der Winkelpfad läuft über das `base/side`-Interpolationsmodell, das einen beliebigen Rohwert nicht exakt treffen kann (siehe Abschnitt 4). Die globalen Tasten erhielten daher einen Pfad, der Roh-Servopositionen direkt schreibt.

**Ein wichtiges Implementierungsdetail:** Dies verwendet *nicht* rustypots `sync_write_raw_goal_position`. Die Lektüre des makro-generierten Quellcodes zeigt, dass die Roh-API `values.to_le_bytes()` direkt auf die Leitung schreibt, während die umrechnende API zuerst `to_be()` anwendet:

```rust
fn to_raw(value: f64) -> i16 { let a = (...) as i16; a.to_be() }
// sync_write_raw_*: values.iter().map(|v| v.to_le_bytes())   <- no to_be
```

Die Übergabe von `451` würde daher `0xC301` (49921) ausgeben. Stattdessen verwendet der Code `sync_write_goal_position` (Radiant) und löst nach dem Radiantwert, der **exakt** auf dem Ziel-Rohwert landet, wobei die Mitte jedes Rohschritts genommen wird, um Abschneidefehler zu vermeiden.

### 2.3 Rohziele für die drei Tasten

`raw_positions` zu `data/config.yaml` hinzugefügt (Index 0 → Servo-ID 1):

```yaml
raw_positions:
  open:   [260, 760, 260, 760, 260, 760, 260, 760]
  close:  [760, 260, 760, 260, 760, 260, 760, 260]
  middle: [451, 571, 451, 571, 451, 571, 451, 571]
```

| Taste | Aktion | Servo-IDs 1–8 raw |
|---|---|---|
| ✋ Alle öffnen | vollständig gestreckt | 260, 760, 260, 760, 260, 760, 260, 760 |
| ✊ Alle schließen | vollständig geschlossen | 760, 260, 760, 260, 760, 260, 760, 260 |
| ⊙ Alle zentrieren | seitliche Neuzentrierung (keine Änderung von Öffnen/Schließen) | — |
| **Mittelposition** | **zurück zur kalibrierten Mitte** | 451, 571, 451, 571, 451, 571, 451, 571 |

> ⚠️ `raw_positions` sind **Kalibrierwerte pro Hand**. Der Kommentar des Herstellers selbst lautet *"replace values by your calibration results"* — nach dem Tausch von Händen oder Servos neu vermessen.

### 2.4 Der Kompromiss bei der Schieberegler-Synchronisierung

Rohziele umgehen das `base/side`-Modell, haben also keine exakte Schieberegler-Entsprechung. Nach Ausführung einer Taste werden die Schieberegler auf die nächste ganze Zahl gesetzt:

| Position | Schieberegler zeigt |
|---|---|
| open | base = −73, side = 0 |
| close | base = +73, side = 0 |
| middle | base = −17, side = 0 |

Der Preis: Wird danach ein Schieberegler berührt, bewegt sich die Hand um bis zu ~1 raw-Einheit (0.3°) vom Ziel weg. Das ist beabsichtigt — die kalibrierte Position exakt zu treffen, ist wichtiger.

---

## 3. Neue Taste „Mittelposition"

Rechts neben `✋ Alle öffnen` / `✊ Alle schließen` / `⊙ Alle zentrieren` platziert. Sie bringt die Hand in die **vom Hersteller kalibrierte mechanische Mitte** zurück (raw 451/571).

**Warum sie nötig ist:** Der Mittelpunkt zwischen `open_all` und `close_all` ist *nicht* die mechanische Mitte. Die Mitte des Herstellers ist `MiddlePos`, die ±60 raw (±17.6°) von raw 511 entfernt liegt. Nach dem Einschalten möchte man einen wohldefinierten, wiederholbaren Nullpunkt.

---

## 4. GUI und CLI weichen voneinander ab (der Kernfehler)

### 4.1 Symptom

**Dieselbe Pose erzeugt eine unterschiedliche Handbewegung, je nachdem ob sie mit `✓ Anwenden` in der GUI oder mit `--pose` in der CLI angewendet wird.**

### 4.2 Ursache

Die GUI wandte Posen an über:

```
set_positions(p1, p2)  →  decompose into (base, side), stored in the sliders
                       →  get_positions() recomputes via compute_auto_positions() in Auto mode
```

Aber `compute_auto_positions` ist **nicht** die exakte Umkehrung von `decompose_servo_positions` (seine Mitte und Extreme sind empirische Werte). Die CLI sendet die Werte mit `apply_pose()` direkt.

Gemessen: **12 von 19 Posen wurden verzerrt**, um bis zu 32°:

| Pose | Gespeichert | GUI sendete tatsächlich | Abweichung |
|---|---|---|---|
| `ring_close` | Ring `(75, -35)` | Ring `(43, -5)` | **32° / 30°** |
| `middle_close` | Middle `(75, -35)` | Middle `(43, -5)` | **32° / 30°** |
| `pointer_close` | Pointer `(75, -35)` | Pointer `(43, -5)` | **32° / 30°** |
| `thumb_close` | Thumb `(75, -35)` | Thumb `(43, -5)` | **32° / 30°** |
| `wave1` | `(-75, -3)` | `(-75, 9)` | 12° |
| `hifive` | Thumb `(-75, -3)` | Thumb `(-75, 9)` | 12° |
| `greeting` | Ring `(-18, -57)` | Ring `(-10, -68)` | 8° / 11° |
| `victory` | Middle `(-68, -9)` | Middle `(-75, 1)` | 7° / 10° |
| `paper` | Pointer `(-52, -22)` | Pointer `(-59, -16)` | 7° / 6° |
| `ok` | Pointer `(36, 46)` | Pointer `(38, 43)` | 2° / 3° |

**Das Muster:** Symmetrische Posen, bei denen jeder Finger `pos1 == pos2` hat (`open` `close` `stone` `two` `scissors` `one` `three`), laufen exakt hin und zurück. Jede asymmetrische Pose mit seitlicher Spreizung driftet.

### 4.3 Lösung

`_send_exact_positions()` hinzugefügt, das Winkel direkt in `SERVO_PAIRS`-Reihenfolge an die Servos sendet (entspricht `apply_pose` der CLI). Beide Pose-Einstiegspunkte verwenden es nun:

- die Taste `✓ Anwenden` in der Posenverwaltung
- `_apply_pose_from_config()` — der Sequenz-Player und die Posenliste

Die Schieberegler werden weiterhin von `set_positions()` für die Anzeige aktualisiert, **entscheiden aber nicht mehr darüber, was gesendet wird**.

### 4.4 Ergebnis

Nach der Korrektur erfüllen **alle 19 Posen `stored == GUI-sent == CLI-sent`**.

**Nebenwirkung:** Die tatsächlichen Gesten in der GUI ändern sich, insbesondere die asymmetrischen. Das ist der beabsichtigte Effekt der Korrektur.

---

## 5. Korrekturen der Pose-Daten

### 5.1 Vier `*_close`-Posen waren falsch geschrieben

```yaml
# Before — target finger (75, -35)
ring_close:    [75, -35, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, -35, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, -35, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, -35]
```

`(75, -35)` zerlegt sich zu `base = 20, side = -55` (außerhalb des Bereichs) — das bedeutet *„nur zu 27% gebeugt, hart nach links geschwenkt"*, nicht „diesen Finger schließen". In Übereinstimmung mit `close` und `one` ist die korrekte Form `(75, 75)`:

```yaml
# After — target finger fully closed (75, 75), others stay open (-35, -35)
ring_close:    [75, 75, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, 75, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, 75, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, 75]
```

Durch Zerlegung verifiziert: Zielfinger `base = 75` (vollständig geschlossen), `side = 0` (nicht zu einer Seite ausgelenkt).

**Auswirkung:** Die Sequenz `finger_roll`, die diese vier verwendet, ist erst jetzt ein echtes „jeden Finger der Reihe nach einrollen".

### 5.2 Der Daumen in `greeting` / `paper`

Beide hatten ursprünglich den Daumen auf `(75, 75)` (vollständig geschlossen). Für `paper` (布, eine offene flache Handfläche) ist ein geschlossener Daumen schlicht falsch.

`greeting` wurde zunächst auf `(-75, -3)` geändert (unter Wiederverwendung des gespreizten Daumens von `hifive`), aber der Hardwaretest zeigte, dass dieser Schritt den Daumen **150°** weit bewegen müsste, was nicht in 1.0 s passt (siehe 6.3). Endzustand:

```yaml
greeting: [-18, -57, -32, -32, -70, -7, -35, -35]   # thumb (-35, -35), same as open
paper:    [-19, -56, -34, -34, -52, -22, -75, -3]   # keeps the splayed thumb (flat palm)
```

Das trennt die beiden Gesten: `greeting` ist ein Winken, bei dem der Daumen einfach natürlich öffnet; `paper` ist eine flache Handfläche, bei der der Daumen spreizt.

---

## 6. Sequenz-Player: Timing und Diagnose

### 6.1 Falsche Warnungen „Ziel nicht erreicht" korrigieren

Das Ausführen von `demo` auf der Hardware erzeugte drei Fehlalarme:

```
⚠ Pose #42 'greeting': Servos did not reach target! Max error: 52°
```

**Ursache:** `_log_pose_completion` subtrahierte zwei Arrays, die in **unterschiedlicher Reihenfolge** vorlagen.

- `monitor_servos()` schreibt seinen Cache in **Servo-ID-Reihenfolge**: `latest_actual_positions[servo_id - 1] = ...` (Index 0 = ID1 = Zeigefinger)
- die übergebenen `target_positions` sind ein Pose-Array in **Widget-Reihenfolge** Ringfinger / Mittelfinger / Zeigefinger / Daumen (Index 0 = Ringfinger = ID5)

Es wurde also der Messwert des Zeigefingers vom Zielwert des Ringfingers abgezogen.

**Belege** (neu berechnet aus dem gemessenen Log):

```
target (widget order)   : [-18, -57, -32, -32, -70, -7, -75, -3]
actual (servo-ID order) : [-68.85, -6.74, -33.69, -31.35, -18.46, -54.79, -74.12, -3.22]
compared as-is          -> max error 52°      <-- what the old code did
target reordered        : [-70, -7, -32, -32, -18, -57, -75, -3]
compared in servo order -> max error 2.21°    <-- actually spot on
```

**Lösung:** `pose_to_servo_order()` / `servo_to_pose_order()` hinzugefügt, angewendet vor dem Vergleich; das ausgegebene `current` wird zurückkonvertiert, sodass `target` und `current` im Log spaltenweise übereinstimmen.

### 6.2 Korrektur, wann die Erreichbarkeitsprüfung läuft

Das Original prüfte **fest 2000 ms** nach dem Senden:

```python
self.root.after(2000, lambda ...: self._log_pose_completion(...))
```

Doch Sequenzschritte warten nur 1.0 s, sodass zum Zeitpunkt der Prüfung der nächste Schritt bereits gesendet worden war — der Messwert gehört zwangsläufig zur *nächsten* Bewegung:

```
25.388  Pose #40 'ok'      sent
26.782  Pose #41 'victory' sent        <- already moved on
27.742  Pose #40 'ok'      checked -> reading is mid-way to victory
```

**Lösung:**

1. `_apply_pose_from_config` erhielt einen `check_after`-Parameter. Das Klicken auf `✓ Anwenden` für eine einzelne Pose bleibt unverändert (2.0 s, dann auf Stillstand warten); die Sequenzwiedergabe übergibt **die eigene Verzögerung des Schritts**, sodass die Prüfung auf die Schrittgrenze fällt (Verzögerung − 100 ms) und nicht mehr auf Stillstand wartet.
2. Ein **Supersession-Guard** hinzugefügt: `_log_pose_start` zeichnet `current_pose_id` auf; wenn inzwischen ein neuerer Befehl übernommen hat, wird die Erreichbarkeitsprüfung übersprungen und das Log zeigt `current=<superseded>`.

### 6.3 Feinabstimmung der Sequenzverzögerungen

Rückgerechnete **effektive Geschwindigkeit** aus dem Hardware-Log (Geschwindigkeit 3 ist nominal 172°/s):

| Pose | Weg | Fehler bei 0.9 s | Implizierte effektive Geschwindigkeit |
|---|---|---|---|
| `ok` | 110° | 0.5° | 121.7°/s (71% der Nominalgeschwindigkeit) |
| `victory` | 110° | 1.0° | 121.1°/s (70%) |
| `greeting` | 132° | 7.0° | 138.9°/s (81%) |

> Unter Last beträgt die tatsächliche Geschwindigkeit nur etwa **70%** der Nominalgeschwindigkeit. Diese Zahl zählt bei der Wahl der Verzögerungen.

**Änderungen an `demo`:**

```yaml
  demo:
    steps:
    - open:3,3,3,3,3,3,3,3|2.0s
    - close:6,6,6,6,6,6,6,6|2.0s
    - ok:3,3,3,3,3,3,3,3|1.0s
    - victory:3,3,3,3,3,3,3,3|1.0s
    - greeting:3,3,3,3,3,3,3,3|1.5s      # was 1.0s
    - close:6,6,6,6,6,6,6,6|2.0s         # new: settle back into a fist
```

- `greeting` 1.0 s → **1.5 s**: Dieser Schritt legt 132° zurück (zweiter Servo des Ringfingers) und kann nicht in 1.0 s abgeschlossen werden
- **neues abschließendes `close`**: Damit endet `demo` mit geschlossener Hand, was auch das Looping sauber macht
- Gesamtlaufzeit 7.0 s → **9.5 s**

### 6.4 `wave`: Begrenzung des seitlichen Schwungs auf ±30°

Die ursprünglichen `wave_r` / `wave_l` implizierten ein `side` von **±36** (über der Grenze von ±35, wurde also auf 35 begrenzt).

Auflösen von `side = base − pos1`, `base = (pos1 + pos2) / 2` ergibt `pos1 = base − side`, `pos2 = base + side`. Bei Beibehaltung von `base = −39` und Reduzierung von `side` auf ±30:

```yaml
wave_r: [-9, -69, -9, -69, -9, -69, -69, -9]     # was [-3, -75, -3, -75, -3, -75, -75, -3]
wave_l: [-69, -9, -69, -9, -69, -9, -9, -69]     # was [-75, -3, -75, -3, -75, -3, -3, -75]
```

Verifiziert: `wave_r` hat side `[-30, -30, -30, +30]`, und `wave_l` ist dessen Spiegelung pro Finger.

**Nebenwirkung (erwartet):** Der Weg jedes Schwungs sinkt ebenfalls von 40°/72° auf **34°/60°**. Die Welle ist insgesamt schmaler, was den Zeitpuffer nur vergrößert.

---

## 7. Neue Zeile für Rohposition in der Servo-Rückmeldung

Eine Zeile **`Current (0-1023)`** sitzt direkt unter `Position (°)` und zeigt die Live-Rohposition des Servos.

```
1. Goal (°)
2. Position (°)
3. Current (0-1023)      <== new
4. Speed (°/s)
5. Torque (%)
6. Voltage (V)
7. Current (mA)
8. Temperature (°C)
9. Status
10. Moving
```

**Kompromiss:** keine zusätzlichen seriellen Lesevorgänge. Der Rohwert wird aus der Position abgeleitet, die der Überwachungs-Thread **bereits** gelesen hat, sodass die Abfrageschleife ihren seriellen Verkehr nicht verdoppelt. Die Genauigkeit wurde erschöpfend verifiziert: **2048 Kombinationen (raw 0–1023 × ungerader/gerader Servo) laufen mit null Fehler hin und zurück**.

**Verwendung:** direkt mit der Kalibrierung des Herstellers vergleichen — `open` sollte abwechselnd `260 / 760` anzeigen, `middle` sollte `451 / 571` anzeigen.

> Der Zeilenname trägt ein Bereichspräfix, um ihn vom bestehenden `Current (mA)` (geschätzter Stromverbrauch) zu unterscheiden.

---

## 8. Unterstützung für linke und rechte Hand

### 8.1 Der Hersteller liefert zwei Firmwares

Der Hersteller stellt eine separate Arduino-Demo pro Hand bereit, mit völlig unterschiedlichen Parametern:

| | Rechte `Amazing_RHand_Demo` | Linke `Amazing_LHand_Demo` |
|---|---|---|
| Servo-IDs | **1–8** | **11–18** |
| Finger → ID | Zeigefinger `1,2` / Mittelfinger `3,4` / Ringfinger `5,6` / Daumen `7,8` | **Ringfinger `11,12` / Mittelfinger `13,14` / Zeigefinger `15,16` / Daumen `17,18`** |
| Mitte `MiddlePos` | `[451, 571, 451, 571, …]` | `[571, 451, 571, 451, …]` |

Das Debug-Tutorial sagt es klar: *„eine einzelne Hand verwendet 8 Servos; die IDs der rechten Hand müssen auf 1-8 gesetzt werden, die der linken Hand auf 11-18."*

Beachten Sie, dass die Nummerierung der linken Hand **in umgekehrter Reihenfolge** läuft (Ringfinger zuerst) — passend zu ihrer gespiegelten mechanischen Anordnung.

### 8.2 Warum das Ändern der IDs nicht ausreicht

Die IDs sind nur die erste Ebene. Zwischen den Händen bleiben zwei physische Unterschiede, und wer einen davon übersieht, verzerrt die Gesten.

#### Unterschied 1: ein Montageversatz von 35.16°

Beide Hände verwenden **denselben Gestenwert plus ihren eigenen `MiddlePos`**:

```c
// Right
#define MiddlePos {451, 571, ...}
Move_Index(-35, 35)  →  ID1 = 451 + (-35)/0.293 = 331.5

// Left
#define MiddlePos {571, 451, ...}
Move_Index(-35, 35)  →  ID15 = 571 + (-35)/0.293 = 451.5
```

Dieselbe „open"-Geste landet an jeder Hand auf unterschiedlichen Rohwerten. In den Winkelraum dieses Programms umgerechnet unterscheiden sie sich um **120 raw = 35.16°**.

#### Unterschied 2: Die beiden Servos eines Fingers sind vertauscht

```c
// Right Victory                      // Left Victory
Move_Index (-15, 65);                Move_Index (-65, 15);
Move_Middle(-65, 15);                Move_Middle(-15, 65);
```

Pro Finger gilt `(a, b) → (-b, -a)`; in Pose-Werten bedeutet das **das Vertauschen der beiden Zahlen jedes Fingers**.

Wer das übersieht, **kehrt die Spreizrichtung um** — das Symptom ist ein V-Zeichen, dessen beide Finger kollabieren, während die Finger, die zusammen sein sollten, auseinanderspreizen.

> Ein leichtes Missverständnis: In `Perfect` sind die Werte von Zeige- und Mittelfinger an beiden Händen **identisch** (`(50,-50)`, `(0,0)`), und nur der Daumen unterscheidet sich. Die Regel lautet also nicht „Zeige- und Mittelfinger vertauschen", sondern ein `(-b,-a)` pro Finger — was für symmetrische Paare die Identität ist.

### 8.3 Implementierung

**Beide Hände teilen sich eine `hand_config.yaml`.** Gespeicherte Posen liegen immer in **Reihenfolge der rechten Hand** vor; die linke Hand konvertiert auf dem Hin- und Rückweg, sodass keine zweite Posenbibliothek gepflegt werden muss.

Die Konvertierung liegt in `hand_logic.py`:

| Funktion | Zweck |
|---|---|
| `resolve_hand_config(app_config, hand)` | Legt `hands.<name>` über die Konfiguration auf oberster Ebene (rechte Hand) |
| `servo_pairs()` / `servo_ids()` | Die `(servo1_id, servo2_id)` dieser Hand pro Finger / alle Servo-IDs aufsteigend |
| `hand_angle_offset()` / `hand_mirrors_pose()` | Liest die beiden Unterschiedsparameter der Hand aus |
| `adapt_pose_for_hand(positions, mirror)` | Vertauscht `(pos1, pos2)` jedes Fingers. **Das Vertauschen ist seine eigene Umkehrung**, sodass dieselbe Funktion beim Anwenden konvertiert und beim Speichern zurückkonvertiert |

**Eingebunden in:**

- GUI: Posenanwendung (die Taste `✓ Anwenden` und die Sequenzwiedergabe) sowie das Speichern einer Pose
- CLI: `--pose` / `--sequence`

**Die Rohziele der drei globalen Tasten** werden pro Hand konfiguriert und durchlaufen diese Konvertierung nicht (`raw_positions` wird unter `hands.left` ausgeschrieben).

### 8.4 Verwendung

Die GUI fragt vor dem Öffnen:

```
  AmazingHand — which hand?
    1 = right hand  (servo IDs 1-8)
    2 = left hand   (servo IDs 11-18)
  Enter 1 or 2 [1]:
  LEFT hand — servo IDs 11-18
    Ring (11, 12)  Middle (13, 14)  Pointer (15, 16)  Thumb (17, 18)
    middle position raw: [571, 451, 571, 451, 571, 451, 571, 451]
```

Durch Drücken der Eingabetaste wird der Wert `hand:` aus `config.yaml` verwendet. Um die Abfrage zu überspringen:

```bash
python amazing_hand_gui.py --hand left
python amazing_hand_cmd.py --pose victory --hand left
```

### 8.5 Checkliste für die erste Verwendung der linken Hand

In `hands.left.raw_positions` ist nur **middle** der Standard des Herstellers (`571, 451`); `open` und `close` wurden aus der Demo des Herstellers abgeleitet:

| Taste | Raw der linken Hand | Quelle |
|---|---|---|
| Mittelposition | `571, 451, …` | Standard des Herstellers |
| Alle öffnen | `380, 642, …` | Abgeleitet: dieselbe Geste wie „Alle öffnen" der rechten Hand, angewendet auf den linken `MiddlePos` |
| Alle schließen | `880, 142, …` | Ebenso |

**Prüfen Sie sie beim ersten Anschließen der linken Hand in dieser Reihenfolge:**

1. Drücken Sie **Mittelposition** und bestätigen Sie, dass die Zeile `Current (0-1023)` `571, 451, 571, 451, …` anzeigt
2. Drücken Sie **Alle öffnen** / **Alle schließen** — der Weg sollte die Anschläge ohne Stocken erreichen
3. Probieren Sie `victory` (Zeige- und Mittelfinger öffnen sich zu einem V), `greeting` (drei Finger zusammen), `ok` (Daumen- und Zeigefingerspitzen treffen sich)

Falls etwas nicht stimmt:

| Symptom | Änderung |
|---|---|
| Mittelposition liest falsch | `hands.left.raw_positions.middle` |
| Spreizrichtung umgekehrt | `hands.left.mirror_pose` auf `false` setzen |
| Weg zu kurz oder zu weit | `hands.left.raw_positions.open` / `close` |

### 8.6 Falls Ihre linke Hand mit 1-8 nummeriert ist

Manche nummerieren die Servos der linken Hand auf 1–8 um. In diesem Fall muss nur `hands.left.servos` geändert werden:

```yaml
hands:
  left:
    servos:
      # Renumbered following the vendor's left-hand order: ring first
      ring:    [1, 2]
      middle:  [3, 4]
      pointer: [5, 6]
      thumb:   [7, 8]
      all_ids: [1, 2, 3, 4, 5, 6, 7, 8]
```

> `angle_offset` und `mirror_pose` **ändern sich nicht** — sie beschreiben den mechanischen Aufbau, nicht die ID-Nummerierung. Auch die Umkehrung der geraden Servos gilt weiterhin, weil das Paar jedes Fingers „ungerade ID zuerst" beibehält.

---

## 9. Automatische Erkennung des seriellen Ports

### 9.1 Das Problem

Das Original hatte die Windows-Portliste auf `COM1`–`COM20` fest einprogrammiert:

```python
available_ports = [f'COM{i}' for i in range(1, 21)]
```

Doch ein Adapter kann auf jeder beliebigen Portnummer landen (dieser Rechner maß `COM243`). Das Ergebnis: **Ihr Port fehlt einfach im Dropdown**, und die automatische Verbindung fällt auf einen konfigurierten Standard zurück, der nicht existiert, und schlägt fehl mit "the system cannot find the file specified".

### 9.2 Lösung

`available_serial_ports()` hinzugefügt, mit stufenweisem Rückgriff:

1. `list_ports.comports()` von pyserial (wird verwendet, wenn installiert — reichhaltigste Informationen)
2. Windows ohne pyserial: den Registrierungsschlüssel `HARDWARE\DEVICEMAP\SERIALCOMM` lesen (**nur Standardbibliothek**, keine neue Abhängigkeit)
3. Linux/macOS: Glob über `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`, `/dev/cu.usb*`
4. Nur wenn alles oben Genannte fehlschlägt, auf die ursprüngliche Kandidatenliste zurückgreifen

Ports werden **natürlich** sortiert, sodass `COM2` vor `COM10` kommt.

### 9.3 Begleitende Änderungen

- Das Dropdown wechselte von `readonly` zu **editierbar** — Sie können einen Port eintippen, wenn die Erkennung ihn verfehlt
- Wenn der konfigurierte Standard nicht vorhanden ist, **startet die GUI auf dem ersten tatsächlich existierenden Port**, statt einen Standard zu versuchen, der nicht da ist
- **Ein explizites `--port` wird nie** von diesem Rückgriff **überschrieben** (verfolgt über `port_was_explicit`)

---

## 10. Konfigurationsreferenz

### `data/config.yaml`

Die obersten `servos` / `auto_extremes` / `raw_positions` beschreiben die **rechte Hand** und dienen als Standardwerte; `hands.<name>` legt sie Schlüssel für Schlüssel darüber.

```yaml
hand: right           # active hand: right | left (the GUI asks; --hand skips it)

limits:
  servo_min: -75      # absolute lower travel limit
  servo_max: 75       # absolute upper travel limit
  base_min: -75       # open/close slider range (-75 = fully open)
  base_max: 75        #                          ( 75 = fully closed)
  side_min: -35       # left/right slider range
  side_max: 35

auto_extremes:        # servo positions at the side slider's extremes — right hand
  left_open:  [32, -35]
  right_open: [-35, 32]
  left_closed:  [75, 75]
  right_closed: [75, 75]

raw_positions:        # global buttons' raw targets — right hand (index 0 → servo ID 1)
  open:   [260, 760, ...]
  close:  [760, 260, ...]
  middle: [451, 571, ...]

hands:
  left:               # overrides for the left hand; only list what differs
    servos:
      ring:    [11, 12]
      middle:  [13, 14]
      pointer: [15, 16]
      thumb:   [17, 18]
    raw_positions:    # index 0 → servo ID 11
      open:   [380, 642, ...]
      close:  [880, 142, ...]
      middle: [571, 451, ...]
    angle_offset: -35.16   # mounting offset (see 8.2)
    mirror_pose: true      # per-finger servo swap (see 8.2)
```

`auto_extremes` wird von beiden Händen **gemeinsam genutzt** — der Side-Schieberegler verhält sich im Posenraum gleich; eine gespiegelte Hand spreizt physisch einfach in die andere Richtung.

### `data/hand_config.yaml`

Die 8 Werte einer Pose sind in der Reihenfolge **Ringfinger, Mittelfinger, Zeigefinger, Daumen** angeordnet (Servopaare `(5,6) (3,4) (1,2) (7,8)`), **nicht** nach Servo-ID.

**Diese Datei wird von beiden Händen gemeinsam genutzt und immer in der Reihenfolge der rechten Hand gespeichert.** Die linke Hand vertauscht beim Anwenden das Paar jedes Fingers und vertauscht beim Speichern wieder zurück.

> ⚠️ Der Docstring am Anfang von `amazing_hand_cmd.py` behauptet "index 0→servo1 … 7→servo8". Dieser Kommentar ist **falsch**; die obige Reihenfolge ist das, was der Code tatsächlich tut.

---

## 11. Gemessene Ergebnisse

### Erreichbarkeitsgenauigkeit (nach den Korrekturen)

| Pose | Ziel | Ist | Max. Fehler |
|---|---|---|---|
| `open` | alle −35 | −36.6 … −33.4 | ≤1.6° |
| `close` | alle 75 | 74.7 … 75.3 | ≤0.3° |
| `ok` | — | — | 0.5° |
| `victory` | — | — | 1.0° |
| `greeting` | — | — | 2.2° |

### Konvertierungsprüfungen

```
raw -> degrees -> raw: 2048 combinations, zero error
open    raw [260, 760] -> back [260, 760]
middle  raw [451, 571] -> back [451, 571]
close   raw [760, 260] -> back [760, 260]
```

### Bekannte verbleibende Probleme

- **`ok` und `victory` in `demo` haben fast keinen Zeitpuffer** (+0.01 s bei der gemessenen Geschwindigkeit). Sie bestehen derzeit nur, weil die Toleranz < 5° sie auffängt. Ein Absinken der Batteriespannung, eine Temperaturänderung oder eine etwas schwergängigere Hand könnte sie über die Grenze drücken. Beide Verzögerungen von 1.0 s auf 1.2 s zu erhöhen, ist der naheliegende nächste Schritt.
- **`scissors` ist byte-identisch mit `two`**, und **`stone` ist byte-identisch mit `close`**. Semantisch in Ordnung (Schere = zwei Finger, Stein = Faust), aber buchstäblich dupliziert und nicht bereinigt.
- **Die Schieberegler weisen weiterhin einen Darstellungsfehler von ~0.3°** gegenüber den Rohzielen auf (siehe 2.4).
- **`config.yaml` und `default_config` in `hand_logic.py` sind nicht synchron.** Letzteres trägt noch die ursprüngliche Skala (`servo_min: -40` usw.); es wird nur verwendet, wenn `config.yaml` fehlt. Der Test `test_hand_logic.py::TestAngleLimits::test_defaults` prüft genau diese alten Standardwerte.

---

## 12. Zusammenfassung Datei für Datei

| Datei | Änderungen |
|---|---|
| `hand_logic.py` | Neue SCS0009-Konvertierungskonstanten; `raw_to_degrees` / `raw_to_radians` / `degrees_to_raw` / `pose_to_servo_order` / `servo_to_pose_order`; `raw_position`-Anzeigeformat; `raw_positions`-Standardwerte; **Hand-Unterstützung** (`HAND_NAMES` / `DEFAULT_HAND_SERVOS` / `resolve_hand_config` / `servo_pairs` / `servo_ids` / `hand_angle_offset` / `hand_mirrors_pose` / `adapt_pose_for_hand`); **`available_serial_ports()`**; Konfigurationsdatei-I/O auf **UTF-8** umgestellt (es verwendete den Windows-Standard GBK und stürzte bei Nicht-ASCII-Kommentaren ab) |
| `amazing_hand_gui.py` | Neues `_apply_raw_hand_position` / `middle_all` / `_send_exact_positions`; `open_all` / `close_all` / `_apply_pose_from_config` / `_log_pose_completion` neu geschrieben; neue Taste **Mittelposition**; neue Rohpositions-Zeile in der Servo-Rückmeldung; `self.app_config` zu einem Instanzattribut befördert; das ungenutzte `latest_goal_positions` entfernt und die Schreibreihenfolge von `feedback_data['goal']` vereinheitlicht; **Handauswahl beim Start + `--hand`**; **8 fest einprogrammierte `range(1,9)` durch die echten IDs der Hand ersetzt**; Fenstertitel zeigt die aktive Hand; Winkelversatz- und Spiegelkonvertierung in jeden Posenpfad eingebunden; **Port-Dropdown listet nun erkannte Ports und akzeptiert Tippeingabe** |
| `amazing_hand_cmd.py` | Neues `--hand`; `connect` / `apply_pose` / `wait_for_motion` / Drehmoment-aus-bei-Exit verwenden nun die echten IDs der Hand; Posen- und Sequenzpfade wenden den Winkelversatz und die Spiegelkonvertierung an; Konfigurationslesen auf UTF-8 umgestellt |
| `data/config.yaml` | `limits` / `auto_extremes` neu kalibriert; `raw_positions` hinzugefügt; `hand` und ein `hands.left`-Überschreibungsblock hinzugefügt |
| `data/hand_config.yaml` | Alle 19 Posen neu skaliert; die vier `*_close`-Posen korrigiert; `greeting` / `paper` Daumen korrigiert; `wave_r` / `wave_l` Schwung auf ±30 verengt; `demo` erhielt eine längere `greeting`-Verzögerung und einen neuen abschließenden Schritt |
| `pyproject.toml` | `build-backend` korrigiert (`setuptools.backends.legacy:build` → `setuptools.build_meta`) |

### Glossar

| Begriff | Bedeutung |
|---|---|
| **Auto-Modus** | Zwei Schieberegler — "base" (Öffnen/Schließen) und "side" (seitlich) — steuern indirekt die beiden Servos eines Fingers |
| **Raw-Modus** | Beide Servowinkel eines Fingers werden direkt gesteuert |
| **base** | Öffnungs-/Schließbetrag, `(pos1 + pos2) / 2` |
| **side** | Seitlicher Versatz, `base − pos1` |
| **raw** | Die interne Positionseinheit des Servos: 0–1023 über 300°, Mitte 511 |
| **MiddlePos** | Die servoindividuelle Mittelkalibrierung der Hersteller-Firmware; unterscheidet sich zwischen den Händen (siehe 8.1) |
| **angle_offset** | Der Montageversatz von 35.16° zwischen den Händen (siehe 8.2) |
| **mirror_pose** | Der Servopaar-Tausch pro Finger bei der linken Hand (siehe 8.2) |
