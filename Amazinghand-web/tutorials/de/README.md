Deutsch | [English](../en/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (Brasil)](../pt-br/README.md) | [Português (Portugal)](../pt-pt/README.md) | [简体中文](../zh-hans/README.md) | [繁體中文](../zh-hant/README.md)

# AmazingHand Web Control

Steuere die Dexterous Hand AmazingHand über einen Browser — **linke oder rechte Hand**, mit zwei Steuerungsarten:

- **Manuell** — 8 Servo-Schieberegler + 19 Preset-Posen + Rückkehr zur Mittelstellung mit einem Klick
- **Kamera-Teleop** — MediaPipe läuft lokal im Browser und überträgt deine Hand in Echtzeit auf die Finger (das Video verlässt niemals den Rechner)
- **Zweisprachige UI** — oben rechts zwischen Chinesisch und Englisch umschalten; die Auswahl wird vom Browser gespeichert

Die Servo-Zuordnung, die Pose-Bibliothek und die Umrechnungsformeln stimmen alle mit
[AmazingHandControl](https://github.com/pollen-robotics/AmazingHand) (der offiziellen GUI) überein.

---

## Schnellstart

```bash
pip install -r requirements.txt

python server.py --no-connect   # empfohlen: Server starten, Port in der Seite auswählen (nichts bewegt sich)

# python server.py                # seriellen Port automatisch erkennen und verbinden
# python server.py --port COM9    # einen bestimmten Port verwenden
# python server.py --hand left    # nur die linke Hand aktivieren
# python server.py --dry-run      # überhaupt kein serieller Port, nur die UI
```

Öffne dann **http://localhost:8000** in einem Browser.

### Seriellen Port in der Seite auswählen

Oben auf der Seite befindet sich eine Port-Leiste:

```
Port  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [Refresh]  [Connect]  [Disconnect]  Connected to COM3
```

- Das Dropdown listet jeden seriellen Port des Rechners auf. Gängige USB-Seriell-Chips (CH34x / CP210x / FTDI …) sind mit **★** markiert und werden zuerst einsortiert
- **Refresh** scannt erneut (nach dem Anstecken des Boards verwenden)
- **Connect** öffnet den ausgewählten Port; die Hand kehrt direkt danach in die Mittelstellung zurück
- **Disconnect** gibt zuerst das Drehmoment frei, damit die Servos nicht in ihrer aktuellen Position blockiert bleiben
- Um den Port zu wechseln, einfach den neuen auswählen und Connect klicken — der alte Port wird automatisch geschlossen

> **`--no-connect` ist für genau diesen Ablauf gedacht**: Der Server startet, ohne einen seriellen Port anzufassen,
> sodass er nicht den falschen greifen und die Hand ruckartig bewegen kann. Lass das Flag weg, wenn er beim Start verbinden soll.

Die seriellen Logs landen in `server.log` (wenn du über eine `.bat` startest, huscht das Fenster vorbei — lies stattdessen die Datei).

### Verdrahtungsprüfung

Listet die gefundenen Servo-IDs auf und gleicht sie Hand für Hand mit `config.json` ab.

```bash
python tools/scan_servos.py --port COM9
```

Ersetze COM9 durch deinen tatsächlichen Port.

---

## Servo-Zuordnung

Quelle: `DEFAULT_HAND_SERVOS` in `AmazingHandControl/hand_logic.py` und
`docs/zh-hans/CONFIG_FORMAT.md`.

| Finger | ID rechte Hand | ID linke Hand |
|---|---|---|
| Ringfinger | 5, 6 | 11, 12 |
| Mittelfinger | 3, 4 | 13, 14 |
| Zeigefinger | 1, 2 | 15, 16 |
| Daumen | 7, 8 | 17, 18 |

### Die zwei Servos eines Fingers haben unterschiedliche Aufgaben ⚠️

Offizielle Konvention:

```
servo1 (ungerade ID) = Flexionsachse   offen ↔ geschlossen
servo2 (gerade ID)   = Spreizachse     Finger zusammen ↔ auseinander
```

Die UI zeigt genau diese beiden Achsen. **„Der Finger spreizt sich nicht / schließt sich nicht" bedeutet, dass sich die Spreizachse nicht bewegt** —
ein scherenartiges V entsteht durch Index-Spreizung `+17` und Mittelfinger-Spreizung `−30` (einer positiv, einer negativ).

Sie werden auf dem Bus kombiniert (entsprechend dem offiziellen Speicherformat):

```
servo1 = Flexion + Spreizung
servo2 = Flexion − Spreizung
```

Bereich (abgeleitet aus den 19 offiziellen Posen plus Mittelstellung):

| Achse | Bereich | Bedeutung |
|---|---|---|
| Flexion | −50 ~ +90 | offen (negativ) ↔ geschlossen (positiv) |
| Spreizung | −45 ~ +45 | zusammen (negativ) ↔ gespreizt (positiv) |

**Zwei ID-Regeln** (werden sie falsch angewandt, verbrennen Servos oder die Bewegung kehrt sich um):

1. **Ungerade IDs sind der erste Servo eines Fingers, gerade IDs der zweite.** Gilt an beiden Händen
   (links 11/12, 13/14 … wechseln ebenfalls ab). Der zweite Servo ist **verkehrt herum montiert**, also im Umrechnungsschritt negieren.
2. **Die linke Hand hat nicht 9–16, sondern 11–18, nummeriert beginnend mit dem Ringfinger.** Sie sequenziell als 1–8 zu verdrahten ist immer falsch.

![Both_Hands-IDs](../../Both_Hands-IDs.jpg)

---

## Umrechnung

Identisch mit `apply_pose()` in `AmazingHandControl` (Pose für Pose verifiziert):

```
1) wenn mirror_pose true ist, zuerst die beiden Servowerte jedes Fingers tauschen
2) servo_deg = (ID ungerade ? +1 : -1) × (Pose-Wert − angle_offset_deg)
```

| Hand | angle_offset_deg | mirror_pose |
|---|---|---|
| Rechts | `0` | **ja** ⚠️ |
| Links | `-35.16` | ja |

`-35.16°` ist der physische Halbslot-Versatz der Servohörner der linken Hand gegenüber der rechten, entnommen aus der offiziellen Konfiguration.

> **Zu `mirror_pose` — dieser Build weicht vom offiziellen ab**
>
> In der offiziellen Referenz ist nur die linke Hand `true`. **Beim rechten Handmodul dieses Builds sind
> die Servopaare ebenfalls verkehrt herum montiert**, daher ist auch die rechte Hand `true`.
>
> Der Tausch kippt nur die **Spreizung**, niemals die Flexion: `base = (a+b)/2` bleibt beim Tausch
> unverändert, während `side = (a−b)/2` das Vorzeichen wechselt. Wenn also die Spreizung einer Hand
> gespiegelt herauskommt, ist dies der erste Schalter, den man prüfen sollte.

Das Pose-Array hat immer 8 Werte in der Reihenfolge **`[ring, middle, index, thumb]`**, zwei pro Finger —
byte-identisch zur offiziellen `data/hand_config.yaml`, sodass du sie direkt vergleichen kannst.

### Durchgerechnete Beispiele

| Pose | Rechts | Links |
|---|---|---|
| `open` `[-35]*8` | ID5 **−35** / ID6 **+35** | ID11 **+0.16** / ID12 **−0.16** |
| `close` `[75]*8` | ID5 **+75** / ID6 **−75** | ID11 **+110.16** / ID12 **−110.16** |
| middle `[-17.578]*8` | ID5 **−17.58** / ID6 **+17.58** | ID11 **+17.58** / ID12 **−17.58** |

> **Beachte, dass `close` bei der linken Hand ±110.16° benötigt**, weit mehr als bei der rechten. Deshalb setzt `config.json`
> das Limit auf **±120°** (der volle Bereich des SCS0009 liegt bei etwa ±150°). Ein Limit von ±90 würde die Faust der linken Hand abschneiden.

---

## Preset-Posen (19)

| Pose | | Pose | |
|---|---|---|---|
| `open` | Öffnen | `wave1` | Winken |
| `close` / `stone` | Faust | `wave_r` / `wave_l` | Nach rechts / links wischen |
| `ok` | OK | `ring_close` | Nur Ringfinger |
| `greeting` | Begrüßung | `middle_close` | Nur Mittelfinger |
| `victory` / `two` / `scissors` | Victory / Zwei | `pointer_close` | Nur Zeigefinger |
| `paper` | Papier | `thumb_close` | Nur Daumen |
| `one` / `three` | Eins / Drei | `hifive` | High five |

Um eine Pose zu ändern, bearbeite den Abschnitt `poses` in `config.json`; die Schlüssel entsprechen den Namen im offiziellen YAML.

### Links und rechts können unterschiedliche Werte verwenden

Innerhalb einer Pose ist `positions` **für beide Hände gemeinsam**. Wenn eine Hand aufgrund mechanischer
Montageunterschiede einen anderen Satz benötigt, füge dieser Definition einen Schlüssel `right` oder `left` hinzu — er überschreibt `positions`:

```jsonc
"close": {
  "label": "Fist",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // von beiden Händen gemeinsam genutzt
  "right":     [ ... 8 Werte ... ]                  // optional: nur rechte Hand
}
```

Eine Pose ohne `right`- / `left`-Schlüssel verwendet die geteilten Werte an beiden Händen — du musst also nur
die schreiben, die tatsächlich abweichen. Die Mittelstellung (`middle`) ist weiterhin für beide Hände gemeinsam.

---

## Zwei Modi

| Modus | Verhalten |
|---|---|
| **Rechte Hand** | Sendet nur an die 8 Servos der rechten Hand |
| **Linke Hand** | Sendet nur an die 8 Servos der linken Hand (Spiegelung + −35.16°-Versatz werden automatisch angewandt) |

Immer nur eine Hand gleichzeitig. Beide Hände hängen am selben Bus; umschalten mit **Target** oben.
Das Umschalten stört die andere Hand nicht — sie hält ihre Pose, wo sie ist.

---

## Kamera-Teleop

Die MediaPipe-Hand-Landmarks laufen lokal im Browser (Assets unter `web/mediapipe/`, offline-fähig).
Die 21 Landmarks werden in Pose-Werte für 4 Finger umgerechnet und an die ausgewählte Hand gestreamt.

### 1. Zuerst drei Posen aufnehmen

Starte die Kamera, forme dann mit deiner Hand die Pose und klicke auf die Aufnahmetaste dieser Pose (etwa 1 Sekunde Mittelung).
Die Reihenfolge spielt keine Rolle; klicke dieselbe Taste erneut, um neu aufzunehmen. **Der Status wird erst grün, wenn alle drei erfasst sind** —
vorher wird nichts gesendet, die Hand bleibt in der Mittelstellung.

| Taste | Pose | Liefert |
|---|---|---|
| ① Spread | Finger gestreckt und gespreizt, Daumen zeigt nach außen | Das „gestreckte“ Ende der Flexion + das „gespreizte“ Ende der Spreizung |
| ② Together | Finger gestreckt und zusammen, Daumen liegt am Zeigefinger an | Das „zusammen“-Ende der Spreizung |
| ③ Fist | Faust ballen, Daumen zur Handfläche eingezogen | Das „geschlossen“-Ende der Flexion |

### 2. Jede Achse ist eine Gerade durch zwei gemessene Punkte

Sowohl Flexion als auch Spreizung verwenden **zwei gemessene Endpunkte, um eine Gerade zu definieren**:

```
t       = (Messwert − EndpunktA) / (EndpunktB − EndpunktA)      // auf 0..1 begrenzt
Zielwert = A.Zielwert + (B.Zielwert − A.Zielwert) × t
```

Der Vorteil: **das Vorzeichen der Messung jedes Fingers wird automatisch absorbiert** — es gibt also
keine „Diesen Finger umkehren“-Checkbox zum Anklicken. (Zeigefinger und Ringfinger liegen auf gegenüberliegenden
Seiten der Mittellinie, und die Gelenkkette des Daumens unterscheidet sich, ihre Richtungen sind also wirklich
entgegengesetzt — zwei gemessene Endpunkte absorbieren das.)

Die Endpunkt-Zielwerte stehen im Abschnitt `camera` von `config.json`:

| Achse | Endpunkte | Ringfinger | Mittelfinger | Zeigefinger |
|---|---|---|---|---|
| Flexion | gestreckt → Faust | −50 → 90 | −50 → 90 | −50 → 90 |
| Spreizung | zusammen → gespreizt | −45 → +45 | 0 → 0 | +45 → −45 |

Beide Spreizungs-Endwerte sind 0 für den Mittelfinger (er schwingt nicht seitlich).

> **Diese beiden Sätze sind für beide Hände gemeinsam.** Wenn sich eine Hand falsch herum bewegt, ändere diese
> Hand in `camera.side_sign` (siehe die Tuning-Kurzübersicht am Ende) und lade die Seite neu.

### 3. Der Daumen führt nur Flexion aus ⚠️

Das CMC des Daumens ist ein **Sattelgelenk (opponierbar)**, und seine Flexion ist eng mit der Abduktion gekoppelt —
mit dem an den Zeigefinger angelegten Daumen befindet er sich bereits in einer Spreizposition, die dort gemessene
„Flexions-Null“ ist also verfälscht. Erzwingt man zwei Achsen, kommen beide falsch heraus.

Der Daumen **führt also nur Flexion aus; seine Spreizung ist immer 0** (beide seiner Servos erhalten denselben Wert). Die zwei
Referenzposen, die er benötigt, sind ① (nach außen zeigend) und ③ (zur Handfläche zeigend) — nichts zusätzlich aufzunehmen.

### 4. Die Spreizung klingt ab, während sich der Finger krümmt

Die endgültige Spreizung wird skaliert mit:

```
side = side_measured × (1 − curl)
```

`splayDeg` ist die Projektion der MCP→PIP-Richtung auf die laterale Achse der Handfläche, und die Fingerflexion
**rotiert genau um diese Achse** — ab einer bestimmten Krümmung kippt das Vorzeichen der Projektion und die gemessene
„Spreizung“ springt plötzlich auf das andere Ende.

Ohne das Abklingen wandert dieser Sprung durch `servo2 = Flexion − Spreizung` und zieht den **Servo mit gerader ID**
in die Rückwärtsrichtung. (Die ungerade ID erhält `Flexion + Spreizung`, bewegt sich also in dieselbe Richtung, nur schneller — das sieht man nicht.)
Das Symptom lautet „auf halbem Weg zur Faust kehren die Servos 12 und 16 plötzlich um“ — 12 ist der Spreizservo
des linken Ringfingers und 16 der des linken Zeigefingers, genau die beiden, deren Spreiz-Zielwerte ungleich null sind.

Mit dem Abklingen ist die Spreizung bei voller Krümmung **exakt 0**, egal wie wild die Messung wird.
Und eine Faust sollte ohnehin mit zusammengelegten Fingern ausgeführt werden.

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
Handflächen-Koordinatensystem der rechten Hand**, er kann also nicht einfach weggelassen werden. Das Modell regressiert
alle 21 Punkte auf einmal und kennt keinen Zustand „dieser Finger wurde nicht gesehen“ — wenn die Handfläche ihn
verdeckt, liefert es trotzdem eine **geratene** Position. Ihn gedämpft zu zeichnen macht offensichtlich, wann geraten wird.

### Tuning-Kurzübersicht

| Was du ändern willst | Wo |
|---|---|
| Achsen-Zielwerte | Abschnitt `camera` von `config.json` |
| **Linke und rechte Spreizung laufen entgegengesetzt** | setze diese Hand in `camera.side_sign` auf `-1` (`1` = unverändert) |
| Glättung | `SMOOTH` in `tracking.js` (Standard 0.35; niedriger ist stabiler, reagiert aber träger) |
| Wie schnell eine Krümmung erfasst wird | die drei Posen neu aufnehmen |

`side_sign` gilt für die Hand, die unter **Target** ausgewählt ist. Ändere ihn und lade die Seite neu —
kein Server-Neustart nötig:

```jsonc
"side_sign": { "right": 1, "left": -1 }   // die gesamte Spreizachse bei der linken Hand umkehren
```

Die Flexion wird von `side_sign` nicht beeinflusst.

---

## Projektstruktur

```
Amazinghand-web/
├── config.json          Servo-Zuordnung / Pose-Bibliothek / Sequenzen / Limits (aus dem offiziellen YAML generiert)
├── server.py            Backend: seriell + statische Dateien + WebSocket
├── requirements.txt
├── README.md            Englisch (Originaldokument)
├── tutorials/           de · en · es · fr · it · ja · ko · pt-br · pt-pt · zh-hans · zh-hant
├── tools/
│   └── scan_servos.py   den Bus nach Servos scannen und ihre IDs prüfen
└── web/
    ├── index.html · app.js · tracking.js · style.css
    ├── i18n.js          UI-Strings (Wörterbuch Chinesisch/Englisch + Umschalter oben rechts)
    └── mediapipe/       MediaPipe-Assets (lokal gebündelt, offline, ~42 MB)
```

Frontend-/Backend-Protokoll:

```jsonc
// Frontend → Backend   target: "left" | "right"
{ "cmd": "ports" }                                  // serielle Ports neu scannen
{ "cmd": "connect",    "port": "COM3" }
{ "cmd": "disconnect" }
{ "cmd": "target", "target": "left" }
{ "cmd": "set",    "target": "left", "angles": { "pointer": [0, 0], ... } }
{ "cmd": "pose",   "target": "left", "name": "close" }
{ "cmd": "middle", "target": "left" }
{ "cmd": "torque", "target": "left", "on": true }
{ "cmd": "stop" }

// Backend → Frontend
{ "type": "state", "hands": {...}, "poses": {...}, "positions": {...},
  "axes": {...}, "camera": {...}, "target": "left",
  "limits": {...}, "port": { "available": [...], "current": "COM3", "connected": true } }
{ "type": "ports" | "connected" | "disconnected", "ports": [...], ... }
{ "type": "error", "msg": "connect COM_FAKE failed: the system cannot find the file specified." }
```

---

## Sicherheit

| Punkt | |
|---|---|
| **Pose-Limits** | ±120° (`limits` in `config.json`); alle 19 Posen wurden geprüft, dass sie innerhalb bleiben |
| **Änderungs-Deduplizierung** | Änderungen unter 0.5° werden nicht gesendet, damit der Bus nicht mit Rauschen geflutet wird |
| **Schreib-Throttle** | mindestens 20 ms zwischen Schreibvorgängen |
| **Not-Aus** | der rote Button in der UI gibt alle Servos auf einmal frei |
| **Schutz beim Beenden** | bei Ctrl+C wird das Drehmoment automatisch freigegeben |
| **Debug für eine Hand** | `--hand left/right` |

---

## Fehlerbehebung

**Die Bewegung ist umgekehrt** → prüfe, dass die Verdrahtung „ungerade ID zuerst“ folgt; bei der linken Hand zusätzlich `angle_offset_deg = -35.16` bestätigen.

**Die Faust der linken Hand ist zu klein / Servos fiepen** → das Limit ist wahrscheinlich noch ±90; prüfe, dass `config.json` ±120 hat.

**Ein Finger bewegt sich nicht / „expected N motors, found M“** → führe `tools/scan_servos.py` aus; die IDs der linken Hand sind am leichtesten falsch zu verdrahten.

**Die Mittelstellung ist daneben** → der Mittelwert `-17.578125` ist aus den offiziellen Rohwerten 451/571 umgerechnet.
Um auf deine eigene Montage zu kalibrieren, bearbeite `middle.positions` in `config.json`.

**Das Kamera-Tracking zittert** → gleichmäßige Beleuchtung, Handfläche zur Kamera gerichtet. `SMOOTH` in `tracking.js`
(Standard 0.35) — höher ist glatter, reagiert aber träger.

**Kamera-Gesten falsch / ein Finger folgt nicht** → siehe den Abschnitt Kamera-Teleop oben. Prüfe zuerst drei Dinge:

1. **Sind alle drei Posen aufgenommen?** — der Status muss grün sein; vorher wird nichts gesendet und die Hand bleibt in der Mittelstellung
2. **Eine umgekehrte Richtung bedeutet, dass diese Pose verkehrt herum aufgenommen wurde** — nimm einfach diese eine Taste neu auf, keine Codeänderung nötig
3. **Der Daumen sollte sich nicht spreizen** — er führt nur Flexion aus, siehe Abschnitt 3 oben

**Ein Servo springt auf halbem Weg zur Faust in die Rückwärtsrichtung** → dieser Servo sollte eine **gerade ID** haben (die Spreizachse, z. B. linke Hand 12 / 16).
Normalerweise geht die Spreizung mit der Krümmung auf 0 und springt nie; wenn du das siehst, wirkt die Zeile `side *= (1 - curl)` in
`tracking.js` nicht, oder `curl` wird nicht berechnet.
