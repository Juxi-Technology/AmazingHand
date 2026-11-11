---
title: "PWM-Verkabelung, GPIO und Stromversorgung"
description: "AmazingHand PWM-Servo-Version: ESP32-S3, 8 PWM-Kanäle, GPIO-Zuordnung, Stromversorgung und Servomodell."
version: pwm
---

# PWM-Verkabelung, GPIO und Stromversorgung

Bei der PWM-Version erzeugt der ESP32-S3 direkt 8 PWM-Signale; der PC muss nur über USB-Seriell Befehle senden.

## Hardware-Liste

| Projekt | Spezifikation |
|------|------|
| Steuerung | ESP32-S3-Entwicklungsboard (Youxin YX-ESP32-S3 oder gleichwertig) |
| Servo | PTK 7452 MG-D **digitaler** PWM-Servo ×8 (333 Hz) |
| Adapterplatine | PWM-Servo-Adapterplatine (8× 3P-Steckerleiste + 5 V/GND) |
| Stromversorgung | 5 V / 3 A oder mehr; Adapterplatine und ESP32 müssen gemeinsame Masse haben |

> Servo nominal 4,5 kg·cm@7,4 V; bei 5-V-Versorgung dieser Variante beträgt das tatsächliche Drehmoment ca. 2,8–3 kg·cm.
>
> ⚠️ Analoge 50-Hz-Servos wie SG90 können die 333-Hz-Firmware nicht direkt ersetzen; bei einem Modellwechsel müssen `LEDC_FREQ` und die Pulsbreiten-Kalibrierung angepasst werden.

## Kanal → GPIO → Finger

| Kanal | GPIO | Gelenk | Kanal | GPIO | Gelenk |
|------|------|------|------|------|------|
| PWM1 / CH1 | 4 | Zeigefinger Gelenk 1 | PWM5 / CH5 | 15 | Ringfinger Gelenk 1 |
| PWM2 / CH2 | 5 | Zeigefinger Gelenk 2 | PWM6 / CH6 | 16 | Ringfinger Gelenk 2 |
| PWM3 / CH3 | 6 | Mittelfinger Gelenk 1 | PWM7 / CH7 | 17 | Daumen Gelenk 1 |
| PWM4 / CH4 | 7 | Mittelfinger Gelenk 2 | PWM8 / CH8 | 18 | Daumen Gelenk 2 |

- Verkabelung links/rechts identisch; Zeigefinger immer CH1/2.
- Pro Fingerpaar ist der rechte Servo der ungerade Kanal und der linke der gerade Kanal.
- Die Kanalnummer ist durch die Firmware fest vorgegeben; eine Servo-ID muss nicht eingestellt werden.

## Verkabelungsschritte

1. Die 3P-Stecker der 8 Servos nach Nummer an die Servo-Stiftleisten 1–8 der Adapterplatine stecken.
2. PWM1–PWM8 der Adapterplatine mit GPIO 4, 5, 6, 7, 15, 16, 17, 18 des ESP32-S3 verbinden.
3. 5 V/GND der Adapterplatine mit einer externen 5-V/3-A-Stromversorgung verbinden.
4. Von der Adapterplatine eine weitere 5-V/GND-Leitung zum ESP32-S3 führen, **gemeinsame Masse ist zwingend**.
5. 3P-Leitungsbelegung der Servos: braun/schwarz GND, rot V+, orange/weiß/gelb Signal; nach dem Siebdruck der Adapterplatine einstecken, nicht verpolen.

## Stromversorgung und Sicherheit

- Wenn 8 Servos gleichzeitig arbeiten, ist der Strom hoch; mindestens 5 V/3 A vorsehen und nicht nur über USB versorgen.
- Vor dem ersten Einschalten die Hand in die Mittelstellung bringen und die Servohörner bei 90° montieren.
- Nicht belegte Kanäle dürfen frei bleiben, ohne die anderen Kanäle zu beeinflussen; freie Stecker isolieren.
- Das Öffnen der seriellen Schnittstelle kann den ESP32 zurücksetzen; die Firmware kehrt automatisch in die Mittelstellung zurück.

## Nächste Schritte

- [PWM-Schnellstart](../02-quick-start/pwm.md) (Firmware flashen + GUI/Web)
- [PWM-Protokoll und Kalibrierung](../06-servo-tuning/pwm.md)
- [Websteuerung](../03-web-control/pwm.md)
