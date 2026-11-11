---
title: "AmazingHand-Websteuerung"
description: "Übersicht über die AmazingHand-Websteuerung: Start, Treiberwechsel, serielle Leiste, manuelle Steuerung, Kamera-Teleop und Sicherheitskonzept."
version: both
---

# AmazingHand-Websteuerung

Steuere die AmazingHand-Dexterhand über einen Browser, **zwei Modi für linke/rechte Hand**, zwei Bedienarten:

- **Manuelle Steuerung** — 8 Servo-Schieberegler + 19 Preset-Posen + Ein-Klick-Rückkehr zur Mittelstellung
- **Kamera-Interaktionsteleop** — MediaPipe erkennt Handbewegungen lokal im Browser und bildet sie in Echtzeit auf die Finger ab (das Bild verlässt den Rechner nicht)
- **Umschaltung Chinesisch/Englisch** — oben rechts umschalten, die Auswahl wird im Browser gespeichert; beim nächsten Öffnen gilt wieder die zuletzt gewählte Sprache

> Diese Seite ist die **allgemeine Beschreibung der Websteuerung**. Die SCS0009-spezifische Zuordnung/Umrechnung findest du unter [SCS0009-Websteuerung](scs0009.md); die PWM-spezifische Verkabelung/Flashen/Kalibrierung unter [PWM-Websteuerung](pwm.md).

## Schnellstart

Öffne ein Terminal und wechsle in das Amazinghand-web-Verzeichnis:

```bash
pip install -r requirements.txt

python server.py --no-connect   # empfohlen: zuerst den Dienst starten, seriellen Port in der Seite wählen (Servos werden nicht angesteuert)

# python server.py                # seriellen Port automatisch erkennen und verbinden
# python server.py --port COM9    # einen bestimmten Port verwenden
# python server.py --hand left    # nur die linke Hand aktivieren
# python server.py --driver pwm   # die ESP32-S3-PWM-Servo-Version verwenden
# python server.py --dry-run      # überhaupt keinen seriellen Port öffnen, nur die Oberfläche prüfen
```

Öffne dann **http://localhost:8000** im Browser.

Alternativ kannst du das statische Frontend direkt verwenden (Web Serial, ohne Python-Server):

- Online: <https://juxi-technology.github.io/AmazingHand/Amazinghand-web-io/> (Chrome / Edge)
- Lokal: im Repository-Stamm `python -m http.server 8099` ausführen und <http://localhost:8099/Amazinghand-web-io/> öffnen

### Seriellen Port in der Seite wählen

Oben auf der Seite befindet sich eine Werkzeugleiste; wähle zuerst den Treiber, dann den Port:

```
Driver  [SCS0009 bus ▾]  Port  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [Refresh]  [Connect]  [Disconnect]  Connected to COM3
```

- Treiber-Dropdown: **SCS0009 bus** (offizielle Bus-Servos, Standard) oder **PWM (ESP32-S3)** (siehe [PWM-Websteuerung](pwm.md))
- Das Dropdown listet alle seriellen Ports des Rechners auf; gängige USB-Seriell-Chips (CH34x / CP210x / FTDI …) sind mit **★** markiert und stehen vorn
- **Refresh** scannt erneut (nach dem Anstecken/Abtrennen des Boards verwenden)
- **Connect** verbindet den ausgewählten Port; nach dem Verbinden wird automatisch in die Mittelstellung gefahren
- **Disconnect** gibt zuerst das Drehmoment frei und trennt dann, damit die Servos nicht in ihrer aktuellen Position blockiert bleiben (die PWM-Version hat keinen Drehmomentbefehl, siehe unten)
- Um den Port zu wechseln, einfach den neuen auswählen und Connect klicken — der alte Port wird automatisch geschlossen

> **Statisches Deployment (GitHub Pages) hat keinen Python-Server**: Aus Datenschutzgründen kann der Browser serielle Ports nicht stillschweigend auflisten und sieht nur Geräte, die du autorisiert hast. Klicke dann auf **Add port…** und wähle die Platine im Browser-Dialog; das oben beschriebene „alle lokalen Ports auflisten" gilt nur im `server.py`-Servermodus.

![Webseite oben: Treiberauswahl, serielle Werkzeugleiste und Umschaltung linke/rechte Hand](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-port-bar.png)

> **`--no-connect` ist für genau diesen Ablauf gedacht**: Beim Start wird nur der Dienst gestartet und kein serieller Port angefasst,
> sodass die Hand nicht durch eine falsche automatische Verbindung unkontrolliert bewegt wird. Wenn beim Start automatisch verbunden werden soll, lass den Parameter weg.

Die seriellen Logs stehen in `server.log` (beim Start per Doppelklick auf die .bat huscht das Fenster vorbei — lies diese Datei).

### Verkabelungsprüfung

Listet die gefundenen Servo-IDs auf und gleicht sie Hand für Hand mit `config.json` ab.

```bash
python tools/scan_servos.py --port COM9
```

COM9 durch den eigenen tatsächlichen Port ersetzen

> Dieses Werkzeug gilt nur für **SCS0009-Bus-Servos**. Die Verkabelungsprüfung der PWM-Version findest du unter [PWM-Websteuerung](pwm.md) oder mit `AmazingHand-PWM/tools/serial_test.py`.

---

## Preset-Posen (19)

![Manuelles Bedienfeld: Vier-Finger-Schieberegler, 19 Preset-Posen und Aktionsbuttons](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-manual.png)

| Pose | Beschreibung | Pose | Beschreibung |
|---|---|---|---|
| `open` | Öffnen | `wave1` | Winken |
| `close` / `stone` | Faust | `wave_r` / `wave_l` | Nach rechts / links schwenken |
| `ok` | OK | `ring_close` | Nur Ringfinger schließen |
| `greeting` | Begrüßung | `middle_close` | Nur Mittelfinger schließen |
| `victory` / `two` / `scissors` | Victory / Zwei | `pointer_close` | Nur Zeigefinger schließen |
| `paper` | Papier | `thumb_close` | Nur Daumen schließen |
| `one` / `three` | Eins / Drei | `hifive` | High five |

Wenn du Posen selbst ändern willst, bearbeite den Abschnitt `poses` in `config.json`; die Schlüsselnamen entsprechen den Namen im offiziellen YAML.

### Linke und rechte Hand können unterschiedliche Posenwerte haben

`positions` in einer Pose ist **für beide Hände gemeinsam**. Wenn eine Hand wegen mechanischer Montageunterschiede einen anderen Satz benötigt,
füge derselben Definition einen Schlüssel `right` oder `left` hinzu; er überschreibt `positions`:

```jsonc
"close": {
  "label": "握拳",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // von beiden Händen gemeinsam genutzt
  "right":     [ ... 8 Werte ... ]                   // optional: nur für die rechte Hand
}
```

---

## Zwei Modi

| Modus | Verhalten |
|---|---|
| **Rechte Hand** | sendet nur an die 8 Servos der rechten Hand |
| **Linke Hand** | sendet nur an die 8 Servos der linken Hand (SCS0009 wendet automatisch Spiegelung und −35,16°-Offset an; PWM verwendet die Kanalzuordnung der linken Hand) |

Immer nur eine Hand gleichzeitig steuern, oben mit „Steuerobjekt" umschalten; das Umschalten beeinflusst die andere Hand nicht, sie hält ihre aktuelle Pose. Bei SCS0009 können beide Hände am selben Bus hängen; bei PWM wird jede Hand von einem eigenen ESP32-S3 gesteuert.

---

## Kamera-Interaktionsteleop

MediaPipe-Hand-Landmarks laufen lokal im Browser (Assets unter `Amazinghand-web/web/mediapipe/`, offline nutzbar; die Seite probiert bevorzugt auch `Amazinghand-web-io/mediapipe/`),
die 21 Landmarks werden in Posenwerte für 4 Finger umgerechnet und in Echtzeit an die aktuell gewählte Hand gesendet.

![Kamerapanel: Start, Skelettanzeige, dreistufige Posenerfassung und Statusbereich](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-camera.png)

### 1. Zuerst drei Posen aufnehmen

Starte die Kamera, forme dann eine Pose und klicke auf den Aufnahmebutton der entsprechenden Pose (ca. 1 Sekunde Mittelung).
Die Reihenfolge ist beliebig; bei einem Fehler denselben Button erneut klicken. **Der Status wird erst grün, wenn alle drei erfasst sind**;
vorher wird nichts gesendet und die Hand bleibt in der Mittelstellung.

| Button | Pose | Liefert |
|---|---|---|
| ① Spread | Finger gestreckt und gespreizt, Daumen zeigt nach außen | Das „gestreckt"-Ende der Flexion + das „gespreizt"-Ende der Spreizung |
| ② Together | Finger gestreckt und zusammengeführt, Daumen liegt am Zeigefinger an | Das „zusammengeführt"-Ende der Spreizung |
| ③ Fist | Faust ballen, Daumen zur Handfläche eingezogen | Das „geschlossen"-Ende der Flexion |

### 2. Jede Achse ist eine Gerade durch zwei gemessene Punkte

Sowohl Flexion als auch Spreizung verwenden **zwei gemessene Endpunkte, um eine Gerade zu definieren**:

```
t       = (Messwert − EndpunktA) / (EndpunktB − EndpunktA)      // auf 0..1 begrenzt
Zielwert = A.Zielwert + (B.Zielwert − A.Zielwert) × t
```

Der Vorteil: **das Vorzeichen der Messung jedes Fingers wird automatisch absorbiert** — es gibt also
keine Checkbox „Diesen Finger umkehren" zum Anklicken. (Zeigefinger und Ringfinger liegen auf gegenüberliegenden
Seiten der Mittellinie, und die Gelenkkette des Daumens unterscheidet sich, ihre Richtungen sind also wirklich
entgegengesetzt — zwei gemessene Endpunkte absorbieren das.)

Die Endpunkt-Zielwerte stehen im Abschnitt `camera` von `config.json`:

| Achse | Endpunkte | Ringfinger | Mittelfinger | Zeigefinger |
|---|---|---|---|---|
| Flexion | gestreckt → Faust | −50 → 90 | −50 → 90 | −50 → 90 |
| Spreizung | zusammengeführt → gespreizt | −45 → +45 | 0 → 0 | +45 → −45 |

Beide Spreizungs-Endwerte sind 0 für den Mittelfinger (er schwenkt nicht seitlich).

### 3. Der Daumen führt nur Flexion aus ⚠️

Das CMC des Daumens ist ein **Sattelgelenk (opponierbar)**, und seine Flexion ist eng mit der Abduktion gekoppelt —
mit dem an den Zeigefinger angelegten Daumen befindet er sich bereits in einer Spreizposition, die dort gemessene
„Flexions-Null" ist also verfälscht. Erzwingt man zwei Achsen, kommen beide falsch heraus.

Der Daumen **führt also nur Flexion aus; seine Spreizung ist immer 0** (beide seiner Servos erhalten denselben Wert). Die zwei
Referenzposen, die er benötigt, sind ① (nach außen zeigend) und ③ (zur Handfläche zeigend) — nichts zusätzlich aufzunehmen.

### 4. Die Spreizung klingt ab, während sich der Finger krümmt

Die endgültige Spreizung wird skaliert mit:

```
side = side_measured × (1 − curl)
```

`splayDeg` ist die Projektion der MCP→PIP-Richtung auf die laterale Achse der Handfläche, und die Fingerflexion
**rotiert genau um diese Achse** — ab einer bestimmten Krümmung kippt das Vorzeichen der Projektion und die gemessene
„Spreizung" springt plötzlich auf das andere Ende.

Ohne das Abklingen wandert dieser Sprung durch `servo2 = Flexion − Spreizung` und zieht den **Servo mit gerader ID**
in die Rückwärtsrichtung. (Die ungerade ID erhält `Flexion + Spreizung`, ihre Änderung läuft also entgegengesetzt und fällt weniger auf.)
Das Symptom lautet „auf halbem Weg zur Faust kehren die Servos 12 und 16 plötzlich um" — 12 ist der zweite Servo des linken Ringfingers und 16 der des linken Zeigefingers, genau die beiden, deren Spreizanteil ungleich null ist.

Mit dem Abklingen ist die Spreizung bei voller Krümmung **exakt 0**, egal wie wild die Messung wird. Und eine Faust sollte ohnehin mit zusammengelegten Fingern ausgeführt werden.

### 5. Farben des Skeletts

| Finger | Farbe |
|---|---|
| Daumen | orange |
| Zeigefinger | rot |
| Mittelfinger | blau |
| Ringfinger | gelb |
| Kleiner Finger | gedämpftes Grau |
| Handflächenknochen | neutrales Grau |

Der kleine Finger wird nicht für das Gesten-Mapping verwendet, aber sein **Basis-MCP (Landmark 17) definiert das
Handflächen-Koordinatensystem der rechten Hand**, er kann also nicht einfach weggelassen werden.

### Tuning-Kurzübersicht

| Was du ändern willst | Wo |
|---|---|
| Achsen-Zielwerte | Abschnitt `camera` von `config.json` |
| **Linke und rechte Spreizung laufen entgegengesetzt** | setze diese Hand in `camera.side_sign` auf `-1` (`1` = unverändert) |
| Glättung | `SMOOTH` in `tracking.js` (Standard 0,35; niedriger ist stabiler, reagiert aber träger) |
| Wie schnell eine Krümmung erfasst wird | die drei Posen neu aufnehmen |

`side_sign` gilt für die Hand, die unter **Steuerobjekt** ausgewählt ist. Ändere ihn und lade die Seite neu —
kein Server-Neustart nötig:

```jsonc
"side_sign": { "right": 1, "left": -1 }   // die gesamte Spreizachse der linken Hand umkehren
```

Die Flexion wird von `side_sign` nicht beeinflusst.

---

## Projektstruktur

```
Amazinghand-web-io/          Frontend (statisch, separat deploybar)
├── index.html
├── app.js                   Oberfläche, Treiberwechsel, Posen- und Kamera-UI
├── io.js                    SCS0009 Web-Serial-Backend
├── pwm.js                   PWM Web-Serial-Backend
├── common.js                gemeinsame Konfiguration, Posenumrechnung und Limits
├── ws.js                    WebSocket-Backend (Python-Servermodus)
├── tracking.js              MediaPipe-Kamera-Tracking
├── i18n.js                  chinesische/englische Texte
├── config.json              Treiber, Servozuordnung, Posenbibliothek, Kameraparameter
└── tools/pwm_protocol_test.mjs

Amazinghand-web/
├── server.py                HTTP + WebSocket + serieller Server
├── requirements.txt
├── tools/scan_servos.py     SCS0009-Bus scannen und IDs prüfen
└── web/mediapipe/           MediaPipe-Ressourcen (offline, ca. 42 MB)
```

Frontend-/Backend-Protokoll:

```jsonc
// Frontend → Backend   target: "left" | "right"
{ "cmd": "ports" }                                  // serielle Ports neu scannen
{ "cmd": "driver", "driver": "pwm" }                // scs0009 | pwm
{ "cmd": "connect",    "port": "COM3" }
{ "cmd": "disconnect" }
{ "cmd": "target", "target": "left" }
{ "cmd": "set",    "target": "left", "angles": { "pointer": [0, 0], ... } }
{ "cmd": "pose",   "target": "left", "name": "close" }
{ "cmd": "middle", "target": "left" }
{ "cmd": "torque", "target": "left", "on": true }   // nur SCS0009
{ "cmd": "stop" }

// Backend → Frontend
{ "type": "state", "hands": {...}, "poses": {...}, "positions": {...},
  "axes": {...}, "camera": {...}, "target": "left", "driver": "scs0009",
  "capabilities": { "torque": true, "speed": true }, "pwm": {...},
  "limits": {...}, "port": { "available": [...], "current": "COM3", "connected": true } }
{ "type": "ports" | "connected" | "disconnected", "ports": [...], ... }
{ "type": "error", "msg": "连接 COM_FAKE 失败：系统找不到指定的文件。" }
```

---

## Sicherheitskonzept

| Punkt | Beschreibung |
|---|---|
| **Posen-Limits** | Posenwerte ±120° (`limits` in `config.json`), alle 19 Posen wurden geprüft und bleiben innerhalb |
| **Änderungs-Deduplizierung** | Änderungen < 0,5° werden nicht gesendet, damit der Bus nicht mit Rauschen geflutet wird |
| **Schreib-Throttle** | SCS0009 minimaler Abstand 20 ms; PWM-Direktantrieb ca. 30 ms |
| **Not-Aus** | SCS0009: gesamtes Drehmoment freigeben; PWM: `0xFF` senden, um die Geste abzubrechen, Servos bleiben bestromt und halten die Position |
| **Schutz beim Beenden** | SCS0009: Ctrl+C schaltet das Drehmoment ab; PWM: nach dem Trennen der seriellen Schnittstelle halten die Servos die Position |
| **Debug für eine Hand** | `--hand left/right` |

---

## Häufige Probleme

**Kameraerkennung ungenau** → gleichmäßige Beleuchtung, Handfläche zur Kamera. Je größer `SMOOTH` in `tracking.js` (Standard 0,35), desto glatter, aber träger.

**Kamerageste falsch, ein Finger folgt nicht** → zuerst bestätigen, dass alle drei Posen aufgenommen sind (Status grün); bei umgekehrter Richtung die entsprechende Pose neu aufnehmen; der Daumen führt nur Flexion aus und nimmt nicht an der Spreizung teil.

**Auf halbem Weg zur Faust kehrt ein Servo plötzlich um** → prüfen, ob die Spreizung mit der Krümmung auf 0 abklingt (`side *= (1 - curl)`), und ob Vorzeichen/Größe des Spreiz-Steuerwerts ungewöhnlich sind.

**SCS0009: Probleme mit Richtung/ID/Mittelstellung** → siehe [SCS0009-Websteuerung](scs0009.md) und [SCS0009-Debugging und Kalibrierung](../06-servo-tuning/scs0009.md).

**PWM: Probleme mit Verbindung/Baudrate/Kalibrierung** → siehe [PWM-Websteuerung](pwm.md).

**Weitere Fragen** → [FAQ](../08-faq/faq.md).
