---
title: "Hardware-Übersicht: Struktur, CAD und Montage"
description: "Mechanische Struktur, CAD/STL/STEP, Montage und 3D-Druck-Ressourcen der AmazingHand."
version: both
---

# Hardware-Übersicht

Beide Servo-Varianten nutzen dieselbe mechanische Handstruktur; Unterschiede liegen bei Servomodell, Treiberplatine und Verkabelung. Bestätige vor der Montage die gewählte Version.

## Mechanischer Aufbau

- 4 Finger, jeder mit 2 Freiheitsgraden: Flexion/Extension + Abduktion/Adduktion.
- Jeder Finger wird von zwei Servos über einen Parallelmechanismus mit Differenzialantrieb bewegt; alle Servos sind in der Hand montiert.
- 3D-gedrucktes Gehäuse, Gestänge und weiche Fingerglieder; die gesamte Hand wiegt etwa 400 g.
- Die originale Handgelenksschnittstelle passt zum Orbita 3D des Reachy 2; andere Roboterarme lassen sich selbst adaptieren.

## CAD und Modelle

- STL-/STEP-Dateien: [`AmazingHand-main/cad/`](../../../AmazingHand-main/cad/)
- Onshape-Online-Dokument und URDF: siehe CAD-Kapitel in [`AmazingHand-main/README_CN.md`](../../../AmazingHand-main/README_CN.md).

## Montage und 3D-Druck

- [Montageanleitung PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [Empfehlungen für den 3D-Druck PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand-Übersicht PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)

> Vor der Montage die Hand in die Mittelstellung bringen und die Servohörner in Mittelstellung montieren; Servohorn/Verzahnung und Stellweg der beiden Servo-Varianten unterscheiden sich und dürfen nicht gemischt werden.

## Verkabelung der beiden Hardware-Varianten

| Version | Verkabelungs- und Stromversorgungsanleitung |
|------|----------------|
| SCS0009-Seriell-Bus | [SCS0009-Verkabelung, IDs und Stromversorgung](scs0009.md) |
| PWM (ESP32-S3) | [PWM-Verkabelung, GPIO und Stromversorgung](pwm.md) |
| Kamera-Kit | [Installation des Kamera-Kits](camera-kit.md) |

## Nächste Schritte

- [Versionsvergleich und Auswahl](../00-product/version-comparison.md)
- [Schnellstart: SCS0009](../02-quick-start/scs0009.md) · [Schnellstart: PWM](../02-quick-start/pwm.md)
