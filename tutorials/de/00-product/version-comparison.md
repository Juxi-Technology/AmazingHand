---
title: "SCS0009- und PWM-Version im Vergleich und Auswahl"
description: "Vollständiger Vergleich der beiden AmazingHand-Hardware-Varianten: Servos, Rückmeldung, Steuerung, Stromversorgung, Kommunikation, IDs/Kanäle, Firmware und Einsatzszenarien."
version: both
---

# SCS0009- und PWM-Version im Vergleich und Auswahl

Die mechanische Struktur der AmazingHand ist bei beiden Varianten gleich, es gibt jedoch zwei Servo-Varianten. Für die Auswahl ist vor allem entscheidend, ob **Positionsrückmeldung, präzise Winkelsteuerung und Datenerfassung** benötigt werden.

## Kurzfazit

- **SCS0009 wählen**: wenn Positions-/Temperatur-/Spannungsrücklesung, präzise Winkel und die Anbindung an einen SO-ARM101-Roboterarm für LeRobot-Trainingsdatenerfassung benötigt werden.
- **PWM wählen**: für eigenständige Demonstration, Gesteninteraktion und schnellen Einstieg über Web/Desktop, ohne Rückmeldung.
- **Nicht mischen**: immer nur eine der beiden Hardware-Varianten gleichzeitig anschließen; Stromversorgung, Protokoll und Firmware unterscheiden sich.

## Vollständiger Vergleich

| Vergleichspunkt | SCS0009-Seriell-Bus-Version | PWM-Servo-Version |
|--------|--------------------|------------|
| Empfohlener Grund | präzise Winkelsteuerung + Datenrücklesung; an SO-ARM101-Roboterarm für LeRobot-Trainingsdatenerfassung anbindbar | eigenständige Demonstration, Gesteninteraktion, schneller Einstieg |
| Servomodell | Feetech SCS0009 serieller Bus-Servo ×8 | PTK 7452 MG-D **digitaler** PWM-Servo ×8 |
| Servo-Parameter | 2,3 kg·cm@6 V, 300° steuerbar, 0,293° Genauigkeit | 4,5 kg·cm@7,4 V (bei 5-V-Versorgung dieser Variante ca. 2,8–3 kg·cm), 180°±10°, 333 Hz Aktualisierungsrate |
| Positions-/Temperatur-/Spannungs-/Geschwindigkeitsrückmeldung | ✅ Rücklesung unterstützt | ❌ keine Rücklesung, Blockieren oder Schrittverlust nicht erkennbar |
| Steuerung | kein Onboard; PC/Raspberry Pi über Bus-Treiberplatine direkt verbunden | ESP32-S3-Onboard-Firmware |
| Verteilung | Servo-Treiberplatine + 9-Kanal-Seriell-Bus-Hub | PWM-Adapterplatine (8× 3P-Steckerleiste + 5 V/GND) |
| Stromversorgung | 7–12 V (DC5521) Eingang an Treiberplatine, Servos nominal 6-V-Klasse | 5 V / 3 A oder mehr, Adapterplatine und ESP32 müssen gemeinsame Masse haben |
| Baudrate | **1.000.000** | Servo ohne Baudrate; PC↔ESP32 seriell **115200 8N1** |
| Servo-ID | muss eingestellt werden: rechte Hand 1–8, linke Hand 11–18 | keine ID; feste Kanäle CH1–CH8 (Zeigefinger 1/2, Mittelfinger 3/4, Ringfinger 5/6, Daumen 7/8), Verkabelung links/rechts identisch |
| Kommunikationskette | PC → Treiberplatine → Bus → 8 Servos | PC → USB-Seriell 115200 → ESP32 → 8 PWM-Kanäle |
| Befehlsform | Feetech-Bus-Protokoll, Winkel direkt gesendet | Binärframes: `0x01–0x0A / 0x0C` Gesten, `0xF0` Direktantrieb, `0xF1` linke/rechte Hand, `0x00` NOP, `0xFE` Wiederholen, `0xFF` Stopp |
| Firmware | keine (kein Flashen nötig) | ESP-IDF-Kompilierung erforderlich oder vorkompilierte `amazinghand_pwm.bin` direkt flashen |
| Linke/rechte Hand | unterschiedliche Servo-IDs (rechts 1–8, links 11–18) | dieselbe Kanalgruppe, Code-Mapping + `0xF1` Seitenwahl |
| Drehmomentfreigabe | Drehmoment ein/aus und Freigabe unterstützt | nicht unterstützt; Not-Aus bricht nur die Geste ab, Servos bleiben bestromt und halten die Position |
| Geschwindigkeitssteuerung | Geschwindigkeitsparameter unterstützt | Direktantriebs-Frames ohne Geschwindigkeitsparameter |

## Wichtige Punkte der SCS0009-Version

- Jeder Servo hat eine eindeutige ID; rechte Hand 1–8, linke Hand 11–18. Nach Verkabelung/Servotausch muss die ID neu gesetzt werden.
- Serieller Bus, unterstützt Positions-, Geschwindigkeits-, Spannungs- und Temperaturrücklesung; geeignet für Regelung und Datenerfassung.
- PC/Raspberry Pi steuert über USB-Bus-Treiberplatine direkt, keine zusätzliche MCU-Firmware nötig.
- Stromversorgung 7–12 V Eingang an Bus-Treiberplatine (Servos 6-V-Klasse), auf gemeinsame Masse mit der Treiberplatine achten.
- Geeignet für Trainingsabläufe mit Gelenkrückmeldung wie SO-ARM101, LeRobot.

## Wichtige Punkte der PWM-Version

- Verwendet **digitale PTK 7452 MG-D-Servos** (333 Hz, 500–2500 µs); SG90 oder andere analoge 50-Hz-Servos können nicht direkt ersetzt werden.
- Servo nominal 4,5 kg·cm@7,4 V; diese Variante nutzt 5 V/3 A, tatsächliches Drehmoment ca. 2,8–3 kg·cm.
- ESP32-S3 erzeugt 8 PWM-Kanäle; der PC muss nur über USB-Seriell 115200 Befehle senden.
- Keine Positionsrückmeldung; Winkel, Temperatur und Spannung können nicht gelesen werden, Blockieren/Schrittverlust nicht erkannt werden.
- Linke und rechte Hand teilen dieselbe Kanalgruppe; pro Fingerpaar ist der rechte Servo der ungerade und der linke der gerade Kanal, der Zeigefinger ist immer CH1/2.
- Firmware muss geflasht werden; das Repository bietet eine vorkompilierte bin, alternativ Kompilierung mit ESP-IDF.
- Geeignet für eigenständige Demonstration, Gesteninteraktion und schnellen Einstieg über Web/Desktop; nicht für rückmeldungsabhängiges LeRobot-Training.

## Nächste Schritte

- [SCS0009-Schnellstart](../02-quick-start/scs0009.md)
- [PWM-Schnellstart](../02-quick-start/pwm.md)
- [Hardware-Übersicht](../01-hardware/overview.md)
- [Downloads und Ressourcen](downloads.md)
