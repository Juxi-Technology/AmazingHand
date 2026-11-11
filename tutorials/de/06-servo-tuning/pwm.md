---
title: "PWM-Servo-Protokoll, Befehle und Kalibrierung"
description: "AmazingHand PWM-Version: unterstützte Gesten, Firmware-Kalibrierung, serielles Protokoll, Befehlsreferenz, Feinabstimmung der Geste-Parameter und häufige Probleme."
version: pwm
---

# PWM-Servo-Protokoll, Befehle und Kalibrierung

Diese Seite behandelt das serielle Protokoll, die Befehle, die Kalibrierung und die Feinabstimmung der Parameter der PWM-Firmware. Verkabelung siehe [PWM-Verkabelung](../01-hardware/pwm.md), Flashen siehe [PWM-Schnellstart](../02-quick-start/pwm.md), Desktop/Web siehe [PWM-Desktop-GUI](../04-desktop/pwm.md) / [PWM-Websteuerung](../03-web-control/pwm.md).

> Die folgenden Befehle werden im Verzeichnis `AmazingHand-PWM/` des Repositorys ausgeführt. Firmware-Quellcode: [`firmware/AmazingHand_Serial/`](../../../AmazingHand-PWM/firmware/AmazingHand_Serial/).

## 1. Befehls- und Gestenübersicht

Die ersten 11 Zeilen sind Gestenbefehle, die übrigen sind Direktantrieb, Seitenwahl, Wiederholen, Stopp und Verbindungstest.

| Geste/Befehl | Befehl | Beschreibung |
|------|------|------|
| Stein | 0x01 | Schere-Stein-Papier: alle Finger zur Faust |
| Schere | 0x02 | Schere-Stein-Papier: Zeige- + Mittelfinger gestreckt, V-Form |
| Papier | 0x03 | Schere-Stein-Papier: alle Finger geöffnet |
| Daumen hoch | 0x04 | Daumen nach oben, übrige Finger Faust |
| Spott 1 | 0x05 | Zeigefinger schütteln („nein, nein, nein") |
| Spott 2 | 0x06 | Ringfinger strecken und schütteln (ersetzt den kleinen Finger) |
| Öffnen | 0x07 | alle Finger öffnen |
| Faust | 0x08 | alle Finger schließen |
| OK | 0x09 | OK-Geste |
| Kneifen | 0x0A | Kneifgeste |
| Zeigen | 0x0C | Zeigefinger gestreckt, „zeigen" |
| Direktantrieb | 0xF0 | 8 Servowinkel direkt steuern |
| Linke/rechte Hand setzen | 0xF1 | Modus linke/rechte Hand umschalten |
| Wiederholen | 0xFE | letzte Geste wiederholen |
| Stopp | 0xFF | aktuelle Geste sofort abbrechen |
| NOP | 0x00 | Verbindungstest |

> Hinweis: Befehl 0x0B ist deaktiviert (das ursprüngliche „Daumen nach unten" wiederholte „Daumen hoch" und wurde entfernt).

---

## 2. Firmware-Kalibrierung (optional, beim ersten Einsatz empfohlen)

Servo-Mittelposition und Pulsbreite müssen an die tatsächliche Mechanik angepasst werden; direkt im Firmware-Quellcode änderbar:

- `middle_pos[8]` und `min_pw/mid_pw/max_pw[8]` am Kopf von `components/hand_servo/hand_servo.c` bearbeiten.

Nach der Kalibrierung neu kompilieren und flashen.

---

## 3. Serielles Kommunikationsprotokoll

### 3.1 Physikalische Ebene

| Parameter | Wert |
|------|-----|
| Schnittstelle | USB Serial (UART0) |
| Baudrate | **115200** |
| Datenbits | 8 |
| Paritätsbit | keine (None) |
| Stoppbits | 1 |
| Flusskontrolle | keine |

### 3.2 Frame-Format

#### Host → ESP32 (Befehlframe)

```
┌────────┬────────┬──────────┬────────────────┬──────────┐
│  0xAA  │ CMD_ID │ DATA_LEN │ DATA[0 .. N-1] │ CHECKSUM │
│ 1 Byte │ 1 Byte │  1 Byte  │    N Bytes     │  1 Byte  │
└────────┴────────┴──────────┴────────────────┴──────────┘
 Frame-Header  Befehl-ID  Datenlänge   Nutzdaten     Prüfsumme
```

- **Frame-Header**: fest `0xAA`, kennzeichnet den Frameanfang
- **CMD_ID**: Befehlsnummer (siehe [Befehlsreferenz](#4-befehlsreferenz))
- **DATA_LEN**: Byteanzahl der Nutzdaten (0-8, Frames über 8 sind ungültig)
- **DATA**: Nutzdaten, Länge durch DATA_LEN bestimmt
- **CHECKSUM**: `CMD_ID ^ DATA_LEN ^ DATA[0] ^ ... ^ DATA[N-1]` (XOR-Prüfsumme)

> Wenn DATA_LEN = 0, dann CHECKSUM = CMD_ID.

#### ESP32 → Host (Antwortframe)

```
┌────────┬────────┬────────┬──────────┐
│  0xBB  │ CMD_ID │ STATUS │ CHECKSUM │
│ 1 Byte │ 1 Byte │ 1 Byte │  1 Byte  │
└────────┴────────┴────────┴──────────┘
 Frame-Header  Befehl-ID  Statuscode  Prüfsumme
```

- **Frame-Header**: fest `0xBB`
- **CMD_ID**: ursprüngliche Befehlsnummer
- **STATUS**: Statuscode (siehe Tabelle unten)
- **CHECKSUM**: `CMD_ID ^ STATUS`

#### Statuscodes

| STATUS | Bedeutung | Beschreibung |
|--------|------|------|
| 0x00 | OK | Befehl akzeptiert, Ausführung beginnt |
| 0x01 | Ungültiger Befehl | CMD_ID nicht in der Befehlstabelle |
| 0x02 | Parameterfehler | Datenlänge oder Inhalt falsch |
| 0x03 | Beschäftigt | Geste wird ausgeführt, neue Befehle momentan nicht akzeptiert |
| 0x10 | Fertig | Geste abgeschlossen |

### 3.3 Kommunikationsablauf

```
Host                          ESP32
 │                              │
 │──── [AA 01 00 01] ────────→│  Befehl „Stein" senden
 │                              │
 │←─── [BB 01 00 01] ─────────│  ACK: Befehl akzeptiert
 │                              │
 │                      (Geste wird ausgeführt)
 │                              │
 │←─── [BB 01 10 11] ─────────│  Fertig: Geste abgeschlossen
 │                              │
 │──── [AA 02 00 02] ────────→│  Befehl „Schere" senden
 │                              │
 │←─── [BB 02 00 02] ─────────│  ACK
 │                              │
```

### 3.4 Geste stoppen & Frame-Timeout

- `[AA FF 00 FF]` senden kann eine laufende Geste jederzeit abbrechen
- Hat der ESP32 einen Frame nicht innerhalb von 200 ms vollständig empfangen, wird er automatisch verworfen (verhindert dauerhaften Schrittverlust durch verlorene Bytes)
- Frames mit falscher Prüfsumme werden stillschweigend verworfen; die PC-Software sollte Timeout-Wiederholung implementieren

### 3.5 Modus linke/rechte Hand

Standard ist der Rechtshandmodus. `[AA F1 01 02 F2]` schaltet auf die linke Hand, `[AA F1 01 01 F1]` zurück auf die rechte. Linke/rechte Hand beeinflusst die Bewegungsrichtung des Daumens (Stein/Schere/Daumen hoch/OK/Kneifen usw. mit Daumen).

---

## 4. Befehlsreferenz

### 4.1 Gestenbefehle (0x01–0x0A, 0x0C)

Diese Befehle benötigen keine Nutzdaten (DATA_LEN=0); der ESP32 führt nach Empfang sofort die entsprechende Geste aus.

| Befehl | HEX-Frame | Antwort | Beschreibung |
|------|--------|------|------|
| Stein | `AA 01 00 01` | `BB 01 00 01` → `BB 01 10 11` | alle Finger zur Faust |
| Schere | `AA 02 00 02` | `BB 02 00 02` → `BB 02 10 12` | Zeige- + Mittelfinger gestreckt |
| Papier | `AA 03 00 03` | `BB 03 00 03` → `BB 03 10 13` | alle Finger öffnen |
| Daumen hoch | `AA 04 00 04` | `BB 04 00 04` → `BB 04 10 14` | Daumen nach oben |
| Spott 1 | `AA 05 00 05` | `BB 05 00 05` → `BB 05 10 15` | Zeigefinger schütteln (ca. 2,5 s) |
| Spott 2 | `AA 06 00 06` | `BB 06 00 06` → `BB 06 10 16` | Ringfinger schütteln (ca. 2,5 s) |
| Öffnen | `AA 07 00 07` | `BB 07 00 07` → `BB 07 10 17` | alle Finger öffnen |
| Faust | `AA 08 00 08` | `BB 08 00 08` → `BB 08 10 18` | alle Finger schließen |
| OK | `AA 09 00 09` | `BB 09 00 09` → `BB 09 10 19` | OK-Geste |
| Kneifen | `AA 0A 00 0A` | `BB 0A 00 0A` → `BB 0A 10 1A` | Kneifgeste |
| Zeigen | `AA 0C 00 0C` | `BB 0C 00 0C` → `BB 0C 10 1C` | Zeigefinger gestreckt, „zeigen" |

### 4.2 Direktantriebsbefehl (0xF0)

Steuert die 8 Servowinkel direkt; die 8 Datenbytes entsprechen den Servos 1-8, jeder Bytewert liegt im Bereich 0-180.

**Beispiel: alle Servos in Mittelstellung (90°)**

```
Senden: AA F0 08 5A 5A 5A 5A 5A 5A 5A 5A F8
       │  │  │  └── 8× 0x5A (90°) ──┘  │
       │  │  │                            └── CHECKSUM
       │  │  └── DATA_LEN = 8
       │  └── CMD_DIRECT_DRIVE
       └── Frame-Header
```

Prüfsumme = `F0 ^ 08 ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A` = `F8`

> Acht gleiche 0x5A XOR-verknüpft ergeben 0x00, am Ende `0xF0 ^ 0x08 ^ 0x00 = 0xF8`

**Beispiel: Zeigefinger geöffnet (Servo1=170°, Servo2=10°), übrige in Mittelstellung (90°)**

```
Senden: AA F0 08 AA 0A 5A 5A 5A 5A 5A 5A 58
               └─170°  └─10°
```

### 4.3 Linke/rechte Hand setzen (0xF1)

1 Datenbyte: `0x01` = rechte Hand, `0x02` = linke Hand.

```
Rechte Hand setzen: AA F1 01 01 F1
Linke Hand setzen: AA F1 01 02 F2
```

### 4.4 Steuerbefehle

| Befehl | HEX-Frame | Beschreibung |
|------|--------|------|
| NOP | `AA 00 00 00` | Verbindungstest, sofortige Antwort `BB 00 00 00` |
| Wiederholen | `AA FE 00 FE` | letzte Geste wiederholen |
| Stopp | `AA FF 00 FF` | aktuelle Geste sofort abbrechen |

### 4.5 Antwort-Kurzübersicht

Bei ungültigem Befehl (Beispiel: nicht existierender Befehl 0xFC):

```
Senden: AA FC 00 FC
Antwort: BB FC 01 FD    (STATUS=0x01 ungültiger Befehl)
```

> Prüfsummenprüfung: `FC ^ 00 = FC`, Antwort `FC ^ 01 = FD`

---

## 5. Feinabstimmung der Geste-Parameter

### 5.1 Parameterposition

Der Winkeloffset jeder Geste ist als `#define`-Makro definiert, **Logikcode muss nicht geändert werden**, nur die Werte.

- **ESP-IDF-Version**: Bereich „Geste-Parameter (benutzeranpassbar)" am Kopf von `components/hand_gestures/hand_gestures.c`

### 5.2 Bedeutung der Parameter

```c
// Beispiel: Stein-Geste
#define ROCK_IDX_OFF1    70    // Offset Gelenk 1 des Zeigefingers
#define ROCK_IDX_OFF2   -70    // Offset Gelenk 2 des Zeigefingers
```

- **positiv = beugen/schließen**, **negativ = strecken/öffnen**
- 2 Offsets pro Finger, relativ zu `middle_pos` (Standard 90°)
- Differenzialstruktur: zwei Servos nebeneinander, kollineare Achsen; gleichsinnige Drehung erzeugt seitliche Spreizung, gegensinnige Drehung erzeugt Flexion; die Summe der beiden Offsets entspricht der Spreizung, die Differenz der Flexion.

### 5.3 Kalibrierschritte

1. Das `#define`-Makro der entsprechenden Geste finden
2. Wert ändern (größer → größere Amplitude; kleiner → kleinere Amplitude)
3. Neu kompilieren und flashen, mit der PC-Software testen
4. Wiederholt feinjustieren, bis die Bewegung natürlich wirkt

---

## 6. Häufige Probleme

### F1: PC-Software kann keine Verbindung zur seriellen Schnittstelle herstellen?

1. Bestätigen, dass der ESP32 per Type-C mit dem PC verbunden ist
2. Prüfen, ob die COM-Nummer im Geräte-Manager mit der GUI-Auswahl übereinstimmt
3. Baudrate 115200 bestätigen
4. Andere Software, die den seriellen Port belegt, trennen

### F2: Befehl gesendet, keine Reaktion?

1. Zuerst `AA 00 00 00` (NOP) senden, Antwort sollte `BB 00 00 00` sein
2. Bestätigen, dass die Firmware geflasht ist und der Zielchip ESP32-S3 ist
3. Verkabelung prüfen (GND gemeinsame Masse)

### F3: Geste mit falscher Amplitude oder umgekehrter Richtung?

In die Feinabstimmung der Geste-Parameter (siehe [Abschnitt 5](#5-feinabstimmung-der-geste-parameter)) gehen und das entsprechende Makro anpassen.

### F4: Welche Gesten beeinflusst der Modus linke/rechte Hand?

Gesten **mit Daumen** wie Stein/Schere/Daumen hoch/OK/Kneifen; nach dem Umschalten ist die Daumenrichtung gespiegelt.

### F5: Finger klemmt, lässt sich nicht strecken?

Vor allen kontrahierenden Gesten wird automatisch „erst die ganze Hand öffnen, dann schließen" ausgeführt, damit Finger nicht an der vorherigen Geste hängen bleiben. Wenn es weiterhin klemmt, die mechanische Montage prüfen oder die Kontraktionsamplitude verringern.

## Verwandte Seiten

- [PWM-Verkabelung, GPIO und Stromversorgung](../01-hardware/pwm.md)
- [PWM-Schnellstart](../02-quick-start/pwm.md)
- [PWM-Desktop-GUI](../04-desktop/pwm.md)
- [PWM-Handtracking](../05-hand-tracking/pwm.md)
- [FAQ](../08-faq/faq.md)
