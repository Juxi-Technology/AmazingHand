---
title: "AmazingHand-Dexterhand-Tutorial – Übersicht"
description: "Zentraler Einstieg in das AmazingHand-Dexterhand-Tutorial: Produktauswahl für die SCS0009-Seriell-Bus-Version und die PWM-Servo-Version, Hardware-Verkabelung, Schnellstart, Websteuerung, Desktop-GUI, Handtracking, Servo-Debugging und FAQ."
version: both
---

# AmazingHand-Dexterhand-Tutorial

AmazingHand ist eine Open-Source-, 3D-druckbare humanoide Dexterhand: 4 Finger, 8 Freiheitsgrade, alle Antriebe sind in der Hand integriert, die gesamte Hand wiegt etwa 400 g. Derzeit gibt es zwei Hardware-Varianten; die mechanische Struktur der Hand ist identisch, aber Servos, Treiberplatine und Kommunikationsart unterscheiden sich.

## Zuerst die Version wählen

| Vergleichspunkt | SCS0009-Seriell-Bus-Version | PWM-Servo-Version |
|--------|--------------------|------------|
| Empfohlenes Szenario | Präzise Winkelsteuerung, Datenrücklesung, Anbindung an SO-ARM101 / LeRobot-Datenerfassung und -Training | Eigenständige Demonstration, Gesteninteraktion, schneller Einstieg über Web/Desktop |
| Servo | Feetech SCS0009 serieller Bus-Servo ×8 | PTK 7452 MG-D **digitaler** PWM-Servo ×8 |
| Servo-Parameter | 2,3 kg·cm@6 V, 300° steuerbar, 0,293° Genauigkeit | 4,5 kg·cm@7,4 V (bei 5-V-Versorgung ca. 2,8–3 kg·cm), 180°±10°, 333 Hz |
| Positions-/Temperatur-/Spannungsrückmeldung | ✅ unterstützt | ❌ keine Rücklesung, Blockieren oder Schrittverlust nicht erkennbar |
| Steuerung | nicht an Bord; PC/Raspberry Pi über Bus-Treiberplatine direkt verbunden | ESP32-S3-Onboard-Firmware |
| Stromversorgung | 7–12 V (DC5521) Eingang an Treiberplatine | 5 V / 3 A oder mehr, gemeinsame Masse zwingend |
| Kommunikation | Bus-Protokoll mit 1.000.000 Baud | PC ↔ ESP32 seriell **115200** (der Servo selbst hat keine Baudrate) |
| Servo-ID | muss eingestellt werden: rechte Hand 1–8, linke Hand 11–18 | keine ID; feste Kanäle CH1–CH8: Zeigefinger 1/2, Mittelfinger 3/4, Ringfinger 5/6, Daumen 7/8 |
| Firmware | kein Flashen nötig | ESP-IDF-Kompilierung oder direkt vorkompilierte bin flashen |

> Wenn du **Positionsrücklesung, Genauigkeit oder LeRobot-Trainingsdatenerfassung** brauchst, wähle SCS0009; wenn du nur **eigenständige Demonstration, Gesteninteraktion, schnellen Einstieg** brauchst, wähle PWM.

Den vollständigen Vergleich und die Auswahlhilfe findest du unter [Versionsvergleich](00-product/version-comparison.md).

## Navigation nach Nutzungsart

| Nutzungsart | SCS0009-Seriell-Bus-Version | PWM-Servo-Version |
|----------|--------------------|------------|
| Schnellstart | [SCS0009-Schnellstart](02-quick-start/scs0009.md) | [PWM-Schnellstart](02-quick-start/pwm.md) |
| Websteuerung | [SCS0009-Websteuerung](03-web-control/scs0009.md) | [PWM-Websteuerung](03-web-control/pwm.md) |
| Desktop-GUI / CLI | [SCS0009 GUI und CLI](04-desktop/scs0009.md) | [PWM-Desktop-GUI](04-desktop/pwm.md) |
| Handtracking | [Offizielles SCS0009-Demo](05-hand-tracking/scs0009.md) | [PWM-GUI / dora-Tracking](05-hand-tracking/pwm.md) |
| Servo-Debugging und Kalibrierung | [SCS0009-Debugging und Kalibrierung](06-servo-tuning/scs0009.md) | [PWM-Protokoll und Kalibrierung](06-servo-tuning/pwm.md) |
| Arduino / Sekundärentwicklung | [Arduino Nano](07-arduino/arduino-nano.md) · [Beispielcode](07-arduino/examples.md) | Wie links (gemeinsame mechanische Struktur) |

Eine Übersicht der Websteuerung (Treiberwechsel, serielle Leiste, Bedienoberfläche) findest du in der [Websteuerung-README](03-web-control/README.md).

## Vor dem Start

- [Produktinformationen](00-product/product-info.md) — Parameter, Positionierung, Unterlagen
- [Versionsvergleich und Auswahl](00-product/version-comparison.md) — alle Unterschiede der beiden Hardware-Varianten
- [Hardware-Übersicht](01-hardware/overview.md) — Struktur, CAD, Montage, 3D-Druck
- [SCS0009-Verkabelung](01-hardware/scs0009.md) / [PWM-Verkabelung](01-hardware/pwm.md)
- [Installation des Kamera-Kits](01-hardware/camera-kit.md)
- [Downloads und Ressourcen](00-product/downloads.md)

## Sicherheitshinweise

- Externe Servo-Stromversorgung und ESP32/Treiberplatine müssen **gemeinsame Masse** haben.
- Vor dem ersten Einschalten die Hand in die Mittelstellung bringen und die Servohörner in Mittelstellung montieren, damit sie nicht an den Endanschlag fahren.
- Von den beiden Hardware-Varianten SCS0009 und PWM **immer nur eine gleichzeitig anschließen**, nicht mischen.
- PWM-Servos haben keine Positionsrückmeldung; ein Not-Aus kann nur die Geste abbrechen, nicht wie bei Bus-Servos das Drehmoment auslesen oder freigeben.

## Languages

[简体中文](../zh-hans/README.md) | [English](../en/README.md) | [Deutsch](../de/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (BR)](../pt-br/README.md) | [Português (PT)](../pt-pt/README.md) | [繁體中文](../zh-hant/README.md)
