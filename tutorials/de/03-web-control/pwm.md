---
title: "PWM-Websteuerung"
description: "Websteuerung der AmazingHand PWM-Servo-Version: ESP32-S3-Verbindung, Treiberwechsel, Unterschiede zu SCS0009, Winkelkalibrierung und häufige Probleme."
version: pwm
---

# PWM-Websteuerung

Diese Seite ist die **PWM (ESP32-S3)**-spezifische Beschreibung der Websteuerung. Allgemeine Oberfläche, Start, Preset-Posen und Kamera-Teleop findest du in der [Websteuerungsübersicht](README.md).

## Hardware und Flashen

- Verkabelung, GPIO, Stromversorgung und Servomodell: [PWM-Verkabelung, GPIO und Stromversorgung](../01-hardware/pwm.md).
- Firmware flashen (ESP-IDF oder vorkompilierte bin): [PWM-Schnellstart](../02-quick-start/pwm.md).
- PC ↔ ESP32 fest **115200 8N1**; der Servo selbst hat keine Baudrate.

## Webverbindung

1. Oben im Dropdown „Treiber" **PWM (ESP32-S3)** wählen
2. Auf **Add port…** klicken und den USB-Port des ESP32-S3 auswählen
3. Auf **Connect** klicken: Die Seite führt automatisch den Handshake (NOP) aus, sendet die Auswahl der linken/rechten Hand und kehrt in die Mittelstellung zurück
4. Danach mit Schiebereglern, Preset-Posen und Kamera-Teleop steuern; die Fingerüberschriften zeigen **CH 1/2 …** (PWM-Kanalnummern)

![PWM-Modus: Treiberauswahl oben und CH-Kanalanzeige](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-port-bar.png)

![Manuelles Bedienfeld im PWM-Modus: Fingerüberschriften zeigen CH-Kanäle, Drehmomentbutton ausgeblendet](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-manual.png)

## Unterschiede zur SCS0009-Version

| Punkt | SCS0009-Bus-Version | PWM-Version |
|------|----------------|--------|
| Serielle Baudrate | 1.000.000 | **115.200** |
| Treiberplatine | USB-Bus-Treiberplatine | ESP32-S3 + PWM-Adapterplatine |
| Drehmoment | ein-/ausschaltbar | **keins** (die Firmware hat keinen Drehmomentbefehl, der Button wird ausgeblendet) |
| Not-Aus | gesamtes Drehmoment freigeben | `0xFF` senden, um die Geste abzubrechen; Servos bleiben bestromt und halten die Position |
| Geschwindigkeit | Geschwindigkeitsparameter unterstützt | Direktantriebs-Frames ohne Geschwindigkeitsparameter |
| Rückmeldung | Positions-/Temperatur-/Spannungs-/Geschwindigkeitsrückmeldung | **keine Rückmeldung**, Blockieren oder Schrittverlust nicht erkennbar |
| Linke/rechte Hand | unterschiedliche Servo-IDs | dieselbe Kanalgruppe, `0xF1` senden zum Umschalten (beeinflusst hauptsächlich Firmware-Gesten; Web-Posen nutzen die Zuordnung der jeweiligen Hand) |

## Winkelkalibrierung

Die Seite rechnet Posenwerte in 8 Winkel im Bereich 0–180° um, Standardformel:

```
angle = 90 + dir × scale × Posenwert + offset
```

- Der erste Kanal jedes Fingers hat `dir = -1`, der zweite Kanal `dir = +1`
- Standard `scale = 1`, `offset = 0`, d. h. der Servoachswinkel wird direkt gespiegelt
- Wenn `mirror_pose` wahr ist, zuerst die beiden Posenwerte jedes Fingers tauschen (in diesem Repository bei beiden Händen aktiv)

Wenn die Richtung am echten Gerät umgekehrt oder die Mittelstellung verschoben ist, bearbeite `pwm.calibration` in [`config.json`](../../../Amazinghand-web-io/config.json):

```jsonc
"pwm": {
  "calibration": {
    "right": {
      "pointer": { "scale": 1.0, "offset_deg": [0, 0] }
    }
  }
}
```

- Richtung umgekehrt: `scale` des entsprechenden Fingers auf `-1` setzen
- Mittelstellungsversatz: `offset_deg` anpassen (beide Kanäle getrennt)
- Vorgehen pro Finger: in Mittelstellung → einen Finger einzeln ziehen → Richtung/Mittelstellung beobachten → `scale`/`offset_deg` ändern → Seite neu laden und erneut testen

## Häufige Probleme

- **Verbindung fehlgeschlagen / ESP32 antwortet nicht**: prüfen, dass die Baudrate 115200 beträgt, der COM-Port des ESP32 gewählt ist und 5 V/3 A sowie gemeinsame Masse stimmen; nach dem Öffnen der seriellen Schnittstelle kann der ESP32 zurücksetzen, die Seite wiederholt den NOP automatisch
- **Servos bewegen sich nicht oder zittern**: zuerst bestätigen, dass es sich um 333-Hz-Digitalservos (PTK 7452 MG-D oder gleichwertig) handelt und die Stromversorgung ausreicht; beim SG90 muss die Firmware geändert werden
- **Richtung umgekehrt**: `scale` des entsprechenden Fingers auf `-1` setzen
- **Mittelstellung falsch**: `offset_deg` des entsprechenden Kanals anpassen
- **Meldung „Beschäftigt (Geste läuft)"**: Die Firmware führt gerade eine integrierte Geste aus; warte, bis sie beendet ist, oder drücke den Not-Aus (`0xFF`)
- **Servos scannen**: `tools/scan_servos.py` gilt nur für SCS0009; für PWM `AmazingHand-PWM/tools/serial_test.py` oder die Webseite verwenden

---

## Verwandte Seiten

- [PWM-Protokoll und Kalibrierung](../06-servo-tuning/pwm.md)
- [PWM-Desktop-GUI](../04-desktop/pwm.md)
- [PWM-Schnellstart](../02-quick-start/pwm.md)
