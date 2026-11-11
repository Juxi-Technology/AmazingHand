---
title: "Häufige Fragen (FAQ)"
description: "FAQ zu AmazingHand allgemein, SCS0009, PWM, Websteuerung, Desktop-GUI und Handtracking."
version: both
---

# Häufige Fragen (FAQ)

## Allgemein

**SCS0009 oder PWM wählen?**
Für Positionsrückmeldung, Genauigkeit und LeRobot/SO-ARM101-Datenerfassung SCS0009; für eigenständige Demonstration, Gesteninteraktion und schnellen Einstieg über Web/Desktop PWM. Details siehe [Versionsvergleich](../00-product/version-comparison.md).

**Können beide Servo-Varianten gleichzeitig angeschlossen werden?**
Nein. Stromversorgung, Protokoll und Firmware unterscheiden sich; immer nur eine Variante gleichzeitig anschließen.

**Kann die Hand direkt eingeschaltet werden?**
Vor dem ersten Einschalten die Hand in die Mittelstellung bringen und die Servohörner in Mittelstellung montieren; externe Stromversorgung und Treiberplatine/ESP32 müssen gemeinsame Masse haben.

**Kann das Servomodell gewechselt werden?**
Die SCS0009-Version verwendet Bus-Servos; die PWM-Firmware ist auf PTK 7452 MG-D (digitale 333-Hz-Servos) kalibriert. Analoge 50-Hz-Servos wie SG90 können die PWM-Version nicht direkt ersetzen; `LEDC_FREQ` und Pulsbreiten-Kalibrierung müssen geändert werden.

## SCS0009-Seriell-Bus-Version

**Bewegungsrichtung verkehrt** → prüfen, ob nach „ungerade ID zuerst" verkabelt wurde; bei der linken Hand `angle_offset_deg = -35.16` bestätigen.

**Faust der linken Hand zu klein / Servos fiepen** → prüfen, ob das Limit in `config.json` auf ±120° gesetzt ist (Standard ±90 würde die Faust der linken Hand abschneiden).

**Finger bewegt sich nicht / Meldung „expected N motors, found M"** → `tools/scan_servos.py` ausführen; die IDs der linken Hand sind am leichtesten falsch zu verkabeln (11–18, nicht 9–16).

**Mittelstellung falsch** → Mittelwert `-17.578125` entspricht den offiziellen Rohwerten 451/571; für die mechanische Montage `middle.positions` in `config.json` anpassen.

**Wie setze ich die Servo-IDs?** → mit dem [SCS0009-Debugging-Werkzeug](../06-servo-tuning/scs0009.md) scannen und ID ändern; rechte Hand 1–8, linke Hand 11–18.

**Linux kann den seriellen Port nicht öffnen** → aktuellen Benutzer zur Gruppe `dialout` hinzufügen und neu anmelden.

**Können Position/Temperatur/Spannung gelesen werden?** → Ja, SCS0009 unterstützt Positions-, Geschwindigkeits-, Spannungs- und Temperaturrücklesung; Protokollspeichertabelle siehe [`scs_servo_protocol.md`](../../../AmazingHandControl/docs/zh-hans/scs_servo_protocol.md).

## PWM-Servo-Version

**Verbindung fehlgeschlagen / ESP32 antwortet nicht** → 115200 Baud, COM-Port des ESP32, 5 V/3 A und gemeinsame Masse bestätigen; Öffnen der seriellen Schnittstelle kann einen Reset auslösen, die Seite wiederholt NOP automatisch.

**Servo bewegt sich nicht oder zittert** → bestätigen, dass es ein 333-Hz-Digitalservo ist (PTK 7452 MG-D oder gleichwertig), Stromversorgung ausreichend; SG90 erfordert Firmware-Änderung.

**Richtung verkehrt** → in `pwm.calibration` der Web-`config.json` `scale` des entsprechenden Fingers auf `-1` setzen.

**Mittelstellung falsch** → `offset_deg` des entsprechenden Kanals anpassen; Details siehe [PWM-Protokoll, Befehle und Kalibrierung](../06-servo-tuning/pwm.md).

**Meldung „Beschäftigt (Geste läuft)"** → die Firmware führt eine integrierte Geste aus; warten oder Stopp senden (`0xFF`).

**Hat die PWM-Version Rückmeldung?** → keine Positions-/Temperatur-/Spannungsrücklesung, Blockieren oder Schrittverlust nicht erkennbar.

**Haben PWM-Servos eine Baudrate?** → Der Servo selbst nicht; PC↔ESP32 seriell fest 115200 8N1.

**Kann ich mit nur einigen angeschlossenen Servos testen?** → Ja. Nicht belegte Kanäle beeinflussen die anderen nicht; freie Stecker isolieren.

**Kamera hat Bild, aber die Hand folgt nicht / reagiert träge** → gleichmäßiges Licht, Handfläche etwa 40–80 cm von der Kamera entfernt und frontal; andere Programme, die die Kamera belegen, schließen; bestätigen, dass die serielle Schnittstelle verbunden ist. GUI-Tracking-Parameter siehe [PWM-Handtracking](../05-hand-tracking/pwm.md).

**Umschalten linke/rechte Hand ohne Wirkung** → die Firmware schaltet mit `0xF1` zwischen linker/rechter Hand (beim Webverbinden automatisch gesendet); diese Einstellung beeinflusst hauptsächlich die Daumenrichtung der firmwareinternen Gesten; Web-Posen verwenden die jeweilige Zuordnung des aktuellen Steuerobjekts.

**Trackingbild hängt / Log bleibt stehen** → Tracking stoppen und neu starten; wenn weiterhin keine Reaktion, GUI schließen und neu öffnen und prüfen, dass die Kamera nicht von anderen Programmen belegt ist.

**Nach USB-Portwechsel kein serieller Port** → im Geräte-Manager die neue COM-Nummer prüfen, in GUI oder Webseite auf „Aktualisieren" klicken und neu wählen.

## Websteuerung

**Modell fehlgeschlagen / Kamera-Tracking lädt nicht** → bestätigen, dass die Seite von einem lokalen Dienst ausgeliefert wird (nicht direkt über `file://` geöffnet), MediaPipe-Ressourcenpfad erreichbar; das lokale Tutorial hat das serverseitige MediaPipe-Routing korrigiert. Bei weiterhin auftretenden Fehlern 404- oder Berechtigungsfehler in der Browser-Konsole/Netzwerk prüfen.

**Kameraerkennung ungenau** → gleichmäßiges Licht, Handfläche frontal zur Kamera; je größer `SMOOTH` in `tracking.js` (Standard 0,35), desto glatter, aber träger.

**Ein Finger folgt nicht** → die drei Posen neu aufnehmen; bei umgekehrter Richtung die entsprechende Pose neu aufnehmen; der Daumen führt nur Flexion aus und nimmt nicht an der Spreizung teil.

**Auf halbem Weg zur Faust kehrt ein Servo um** → die Spreizung sollte mit der Krümmung auf 0 abklingen (`side *= (1 - curl)`); Vorzeichen und Größe des Spreiz-Steuerwerts auf Anomalien prüfen.

**Wie wechsle ich den Web-Treiber?** → Oben im Dropdown „Treiber" SCS0009 oder PWM wählen; für PWM einen 115200-Seriellport wählen, Details siehe [Websteuerungsübersicht](../03-web-control/README.md).

## Desktop-GUI

**SCS0009-GUI listet keinen seriellen Port** → USB-Adapter neu anstecken, Treiber installieren oder GUI neu starten; unter Linux `dialout` prüfen.

**Connect-Button ausgegraut** → bereits verbunden, zuerst Disconnect klicken.

**Sequenz treibt nicht alle Finger** → Geschwindigkeit jedes Schritts prüfen und sicherstellen, dass jede Pose alle 8 Servowerte enthält.

**Blockierungsanzeige bleibt bestehen** → mechanische Blockierung prüfen; große Abweichung zwischen Ziel und Ist ohne Bewegung löst Blockierung aus.

**PWM-GUI meldet beim Start fehlendes mediapipe** → mit dem Python aus `tools/tracking_env` starten oder `tools/setup_tracking.bat` erneut ausführen.

## Handtracking

**mediapipe fehlt das solutions-Submodul** → `mediapipe==0.10.14` installieren und bestätigen, dass Python 3.12 64-Bit ist.

**dora-Version inkompatibel** → dora-Version gemäß `pyproject.toml` und Logs angleichen; nach Bereinigung neu installieren.

**Modellladen fehlgeschlagen (chinesische Pfade)** → Projekt/Modell in einen rein englischen Pfad legen.

**Kamera kein Bild / Berechtigung** → Systemkameraberechtigung erlauben; in der VM USB-Durchreichung der Kamera nötig.

**Was ist der Unterschied zwischen dem offiziellen SCS0009-Demo und dem PWM-GUI-Tracking?** → SCS0009 verwendet die vollständige dora + MuJoCo-IK-Kette; die PWM-Version bietet leichtes MediaPipe-Tracking direkt in der GUI, das dora-Demo ist nicht im Modul. Details siehe [SCS0009-Handtracking](../05-hand-tracking/scs0009.md) / [PWM-Handtracking](../05-hand-tracking/pwm.md).

## Mehr

- [Versionsvergleich und Auswahl](../00-product/version-comparison.md)
- [Hardware-Übersicht](../01-hardware/overview.md)
- [Downloads und Ressourcen](../00-product/downloads.md)
