---
title: "PWM-Handtracking (integriertes MediaPipe in der GUI)"
description: "Handtracking der AmazingHand PWM-Servo-Version: integriertes MediaPipe in der GUI, Installation der Abhängigkeiten, Ausführung, Prinzip und Grenzen, häufige Probleme."
version: pwm
---

# PWM-Handtracking (integriertes MediaPipe in der GUI)

> Die folgenden Befehle werden im Verzeichnis `AmazingHand-PWM/` des Repositorys ausgeführt.

Diese Seite beschreibt das Handtracking der **PWM-Servo-Version**: MediaPipe ist in die GUI integriert, die Kamera erkennt Hand-Landmarks und bildet sie in Echtzeit auf 8 PWM-Servos ab. Die vollständige dora + MuJoCo-IK-Kette gehört zum offiziellen SCS0009-Demo, siehe [SCS0009-Handtracking](scs0009.md).

> Kette: Kamera → MediaPipe-Hand-Skelett → Beuge-/Streckwinkel der vier Finger → ESP32 → PWM-Servo
>
> Geeignet für: ESP32-S3 + 8 PWM-Servos. Firmware flashen siehe [PWM-Schnellstart](../02-quick-start/pwm.md), Protokoll siehe [PWM-Protokoll und Kalibrierung](../06-servo-tuning/pwm.md).

> Das offizielle Demo mit vollständiger IK (MuJoCo + dora + Rust) wird nicht mit diesem Modul ausgeliefert; dieses Tutorial beschreibt nur das in der GUI integrierte Tracking des Moduls.

## 1. Voraussetzungen

1. **Hardware**: ESP32-S3 + 8 PWM-Servos mit Stromversorgung, USB verbunden, Kamera verfügbar.
2. **Firmware**: bereits geflasht (siehe [PWM-Schnellstart](../02-quick-start/pwm.md)).
3. **Python**: 64-Bit-Python 3.12 (mediapipe 0.10.14 gibt es nur als 64-Bit-Wheel).

## 2. Tracking-Abhängigkeiten installieren

Im Modulstammverzeichnis (`AmazingHand-PWM/`) ausführen:

```bash
tools/setup_tracking.bat
```

Das Skript erledigt automatisch: 64-Bit-Python finden → virtuelle Umgebung `tools/tracking_env` anlegen → `tools/requirements-tracking.txt` installieren (mediapipe 0.10.14, numpy<2, scipy, opencv, Pillow, pyserial) → mediapipe prüfen.

> Alternativ manuell installieren (mit 64-Bit-Python 3.12):
> ```bash
> python -m pip install -r tools/requirements-tracking.txt
> ```

## 3. Ausführen

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

1. Oben den COM-Port des ESP32 wählen → auf „Verbinden" klicken.
2. Zum Panel „Handtracking (MediaPipe-Kamera)" scrollen.
3. Kameranummer wählen (Standard 0) → auf „Tracking starten" klicken.
4. Die Hand ins Bild halten, die Dexterhand folgt Beugen/Strecken; auf „Tracking stoppen" klicken zum Beenden.

![Integriertes Handtracking-Panel der GUI: Kamerawahl, Tracking starten und Statusanzeige](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-tracking.png)

## 4. Prinzip und Grenzen

- MediaPipe 0.10.14 extrahiert 3D-Vektoren der Fingerspitzen von 4 Fingern (im Handkoordinatensystem).
- `tips_to_angles()` in `hand_tracking.py` bildet jeden Finger auf einen Differenzialwinkel ab:
  - flex (Beugen/Strecken): die drei Finger verwenden die z-Komponente, der Daumen die y-Komponente;
  - base (seitliche Spreizung): fest 90 (seitliche Spreizung noch nicht implementiert).
- Dies sind **Steuerachsen**; beim Senden kombiniert das Programm sie zu den Winkeln der beiden Servos jedes Fingers (gleichsinnig = Spreizung, gegensinnig = Flexion).
- Die GUI hat eine eingebaute EMA-Glättung (alpha=0.4) + 60 ms Throttling, um Zittern zu reduzieren.

Grenzen: keine IK, Genauigkeit geringer als die vollständige MuJoCo + dora-Kette; geeignet für Demonstration und schnellen Einstieg.

### Parameterkalibrierung

- `FLEX_SCALE` / `THUMB_FLEX_GAIN` am Ende von `hand_tracking.py` steuern Amplitude und Richtung der Flexion (maßgeblich sind die Werte in der Datei).
- Seitliche Spreizung ist noch nicht implementiert, `base` fest 90; für seitliche Spreizung das offizielle SCS0009-dora-Demo verwenden.
- Nach Änderungen die GUI neu starten.

## 5. Linke/rechte Hand umschalten

Oben in der GUI „Rechte Hand"/„Linke Hand" ankreuzen. Nach dem Umschalten unterscheidet sich die gespiegelte Daumenrichtung; wenn sie verkehrt ist, die andere Seite ankreuzen und testen.

## 6. Häufige Probleme

| Symptom | Maßnahme |
|------|------|
| Servo bewegt sich überhaupt nicht | Stromversorgung (5 V 3 A), COM-Port, Verkabelung prüfen; bestätigen, dass die Firmware geflasht ist |
| Kein Kamerabild | Kameraberechtigung erlauben (Einstellungen→Datenschutz→Kamera) |
| Hand folgt nicht / träge | ausreichend Licht, Hand vollständig im Bild, langsamere und größere Bewegungen |
| Handform verkehrt / Daumenrichtung verkehrt | die entgegengesetzte linke/rechte Hand ankreuzen |
| Nach USB-Portwechsel kein serieller Port | in der GUI den COM-Port neu wählen |
| Beim Start fehlt mediapipe | mit `tools\tracking_env\Scripts\python` starten oder `tools/setup_tracking.bat` erneut ausführen |

## 7. Vollständige IK / SCS0009-Bus-Servos

- Die vollständige IK-Kette (Kamera → MediaPipe → MuJoCo + mink IK → AHControl → ESP32) stammt aus einem eigenständigen dora-Demo-Projekt und ist nicht in diesem Modul; bei Bedarf das Original-Lieferpaket oder das MediaPipe-Projekt verwenden.
- SCS0009-Bus-Servos werden von `Amazinghand-web/` und `AmazingHandControl/` im Repository unterstützt.

## Verzeichnisbeschreibung

| Pfad | Inhalt |
|------|------|
| `tools/hand_gui.py` | Tkinter-PC-Software (Gesten, Direktantrieb, Differenzial, integriertes Tracking) |
| `tools/hand_tracking.py` | MediaPipe-Handtracking und Winkelzuordnung |
| `tools/setup_tracking.bat` | legt `tools/tracking_env` an und installiert Tracking-Abhängigkeiten |
| `tools/requirements-tracking.txt` | Liste der Tracking-Abhängigkeiten |
| `tools/serial_test.py` | serieller Kommandozeilentest |
