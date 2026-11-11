---
title: "PWM-Desktop-GUI (Tkinter-GUI)"
description: "Desktopsteuerung der AmazingHand PWM-Servo-Version: Quellcode starten, GUI-Gesten/Differenzial/Direktantrieb, integriertes MediaPipe-Tracking, Kommandozeilentests und Paketierung."
version: pwm
---

# PWM-Desktop-GUI (Tkinter-GUI)

> Die folgenden Befehle werden im Verzeichnis `AmazingHand-PWM/` des Repositorys ausgeführt.

Diese Seite ist das Desktop-Steuerungstutorial der **PWM-Servo-Version**. Websteuerung siehe [PWM-Websteuerung](../03-web-control/pwm.md), Verkabelung siehe [PWM-Verkabelung](../01-hardware/pwm.md), Firmware flashen siehe [PWM-Schnellstart](../02-quick-start/pwm.md).

> Geeignet für: ESP32-S3 + 8 PWM-Servos (Differenzialantrieb). Firmware flashen siehe [PWM-Schnellstart](../02-quick-start/pwm.md), Protokoll und Befehle siehe [PWM-Protokoll und Kalibrierung](../06-servo-tuning/pwm.md).

## 1. Ausführungsart

| Art | Voraussetzung | Geeignet für |
|------|------|------|
| **Quellcode ausführen** (empfohlen) | 64-Bit-Python 3.12 + pyserial | alle Funktionen inkl. Handtracking |
| exe selbst paketieren | PyInstaller | Verteilung ohne Python-Installation (siehe Abschnitt 7) |

## 2. Quellcode ausführen

### Abhängigkeiten installieren

Im Modulstammverzeichnis (`AmazingHand-PWM/`) ausführen:

```bash
# Basisabhängigkeiten (pyserial)
pip install -r tools/requirements.txt

# nur bei Bedarf für Handtracking ausführen (legt automatisch tools/tracking_env an und installiert mediapipe)
tools/setup_tracking.bat
```

> mediapipe 0.10.14 gibt es nur als 64-Bit-Windows-Wheel; **64-Bit-Python 3.12** ist erforderlich.

### GUI starten

```bash
# beliebiges Python mit pyserial
python tools/hand_gui.py

# oder die Tracking-Umgebung verwenden (enthält mediapipe)
tools/tracking_env/Scripts/python tools/hand_gui.py
```

![Hauptoberfläche der PC-Software: serielle Leiste, Gestenbefehle, Servo-Direktantrieb und Finger-Differenzialsteuerung](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-main.png)

### GUI-Bedienung

1. **Seriellen Port wählen**: oben im Dropdown den COM-Port des ESP32 wählen (im Geräte-Manager nachsehen).
2. **Auf „Verbinden" klicken**: Die Statusanzeige wird grün, das Log zeigt „verbunden", automatisch wird ein NOP-Verbindungstest gesendet.
3. **Gestenbefehle**: Auf „Stein / Schere / Papier / Daumen hoch / OK / Kneifen / Zeigen / Öffnen / Faust" klicken, die Dexterhand führt die Geste aus.
4. **Linke/rechte Hand**: „Rechte Hand"/„Linke Hand" ankreuzen zum Umschalten (die gespiegelte Daumenrichtung unterscheidet sich).
5. **Servo-Direktantrieb**: die 8 Schieberegler ziehen, um den Winkel einzelner Servos in Echtzeit zu steuern (0–180°).
6. **Finger-Differenzialsteuerung**: zwei Schieberegler pro Finger —
   - **Beugen◀▶Strecken**: Finger beugen oder strecken (Bereich -70 ~ +70).
   - **Rechts◀▶Links**: Finger seitlich spreizen (Bereich 60 ~ 120, 90 = neutral).

   > Diese beiden Schieberegler sind **Steuerachsen**, nicht zwei Servos. Das Programm kombiniert sie zu den Winkeln der beiden Servos dieses Fingers: gleichsinniger Anteil erzeugt Spreizung, gegensinniger Anteil erzeugt Flexion.

7. **Wiederholen / Stopp**: letzte Geste wiederholen / sofort abbrechen.
8. **Kommunikationslog**: unten werden Sende-/Empfangsframes und Antworten in Echtzeit angezeigt.

![Finger-Differenzialsteuerungspanel: Beugen/Strecken und seitliches Spreizen pro Finger](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-differential.png)

### Integriertes Handtracking der GUI

Die GUI hat ein eigenes Handtracking-Panel (Kamera folgt der Handbewegung):

1. Nach dem Verbinden der seriellen Schnittstelle zum Panel „Handtracking (MediaPipe-Kamera)" scrollen.
2. Kameranummer wählen (Standard 0) und auf **„Tracking starten"** klicken.
3. Die Hand ins Kamerabild halten, die Dexterhand folgt Beugen/Strecken.

> Tracking erfordert mediapipe, installiert über `tools/setup_tracking.bat`; nur eine aus dem Quellcode gestartete GUI hat die Tracking-Funktion.

## 3. Kommandozeilentest (tools/serial_test.py)

Im Modulstammverzeichnis ausführen:

```bash
# Verbindungstest (zuerst prüfen, ob die Verbindung steht)
python tools/serial_test.py COM3 nop

# Gesten
python tools/serial_test.py COM3 rock         # Stein
python tools/serial_test.py COM3 thumbs_up    # Daumen hoch
python tools/serial_test.py COM3 index        # Zeigen
python tools/serial_test.py COM3 open         # Öffnen
python tools/serial_test.py COM3 close        # Faust

# einzelnen Servo direkt ansteuern
python tools/serial_test.py COM3 servo 1 90   # Servo 1 → 90°

# alles zentrieren
python tools/serial_test.py COM3 mid

# linke/rechte Hand setzen
python tools/serial_test.py COM3 hand L
python tools/serial_test.py COM3 hand R

# Sweep/Selbsttest
python tools/serial_test.py COM3 sweep 1      # Servo 1 Sweep
python tools/serial_test.py COM3 test         # alle Servos einzeln testen
```

## 4. Manueller Test mit seriellem Werkzeug (optional)

Ohne PC-Software kann die Verbindung auch direkt mit einem seriellen Werkzeug per Hex-Frame geprüft werden.

**CoolTerm** (Windows / macOS / Linux):

1. `Options` → Baudrate **115200**, 8N1.
2. `Connection` → `Send String` → `Hex` wählen.
3. `AA 01 00 01` senden (Stein); im Antwortbereich sollten `BB 01 00 01` (ACK) und `BB 01 10 11` (fertig) erscheinen.

**Linux / macOS Kommandozeile**:

```bash
# Linux
stty -F /dev/ttyUSB0 115200
printf '\xAA\x01\x00\x01' > /dev/ttyUSB0

# macOS
stty -f /dev/cu.usbserial-0001 115200
printf '\xAA\x01\x00\x01' > /dev/cu.usbserial-0001
```

Frame-Format, Prüfsumme und alle Befehle siehe [PWM-Protokoll und Kalibrierung](../06-servo-tuning/pwm.md).

## 5. Python-Steuerskript (eigene Entwicklung)

```python
import time
import serial

PORT, BAUD = "COM3", 115200          # unter Linux/macOS /dev/ttyUSB0 bzw. /dev/cu.usbserial-* verwenden

def frame(cmd, data=b""):
    checksum = cmd ^ len(data)
    for byte in data:
        checksum ^= byte
    return bytes([0xAA, cmd, len(data)]) + data + bytes([checksum & 0xFF])

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(1)                        # warten, bis der ESP32-Reset abgeschlossen ist

ser.write(frame(0x00))               # NOP-Verbindungstest
ser.write(frame(0x01))               # Stein
time.sleep(0.5)
ser.write(frame(0xF0, bytes([90] * 8)))  # alle 8 Servos auf 90°
ser.close()
```

Das Antwortframe ist `BB CMD STATUS CKSUM`; `STATUS=0x00` bedeutet akzeptiert, `0x10` bedeutet Geste abgeschlossen. Die vollständige Befehlstabelle sowie Direktantrieb-/Links-Rechts-Beispiele siehe [PWM-Protokoll und Kalibrierung](../06-servo-tuning/pwm.md).

## 6. Häufige Probleme

| Symptom | Maßnahme |
|------|------|
| Servo bewegt sich nicht | Stromversorgung prüfen (5 V 3 A eigenes Netzteil), COM-Port, Verkabelung |
| Keine Antwort / Servos zucken nach dem Öffnen des Ports | Baudrate 115200 bestätigen; die GUI sendet beim Verbinden zuerst einen NOP-Handshake |
| Kein Kamerabild | Kameraberechtigung erlauben (Einstellungen→Datenschutz→Kamera) |
| Handform verkehrt | die entgegengesetzte linke/rechte Hand ankreuzen |
| Tracking reagiert nicht | prüfen, dass mit dem Python aus `tools\tracking_env` gestartet wurde und mediapipe erfolgreich installiert ist |

## 7. exe selbst paketieren (optional)

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole --name "AmazingHand控制台" tools/hand_gui.py
```

Die gepackte Version enthält kein Handtracking (MediaPipe-Ressourcen sind zu groß); für Tracking bitte die Quellcode-Variante verwenden.

> Die vollständige Protokoll- und Befehlsbeschreibung siehe [PWM-Protokoll und Kalibrierung](../06-servo-tuning/pwm.md).
