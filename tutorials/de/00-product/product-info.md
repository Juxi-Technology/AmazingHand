---
title: "AmazingHand-Produktinformationen"
description: "Produktinformationen zur AmazingHand-Dexterhand: mechanischer Aufbau, Abmessungen, Traglast, zwei Servo-Varianten und Open-Source-Ressourcen."
version: both
---

# AmazingHand-Produktinformationen

AmazingHand ist eine Open-Source-, 3D-druckbare humanoide Dexterhand für Embodied-AI-Forschung, Robotikbildung und HMI-Prototypen. Der Handkörper ist identisch; derzeit gibt es zwei Hardware-Varianten: **SCS0009-Seriell-Bus-Servos** und **PWM-Servos (ESP32-S3)**.

## Mechanischer Aufbau

- **4 Finger, 8 Freiheitsgrade**: jeder Finger hat 2 Freiheitsgrade (Flexion + Spreizung), angetrieben von zwei Servos über einen Parallelmechanismus mit Differenzialantrieb.
- **Integrierte Antriebe**: alle Servos sind in der Hand montiert, keine Kabel zum Unterarm nötig.
- **3D-Druck**: Gehäuse und Gestänge sind druckbar, die gesamte Hand wiegt etwa 400 g.
- **Beidhändig**: linke oder rechte Hand einzeln, auch koordiniert als Zwei-Hand-Roboter.
- **Handgelenksschnittstelle**: das Originaldesign passt zum Orbita-3D-Handgelenk des Reachy 2, alternativ lässt sich ein anderer Roboterarm adaptieren.

## Grundparameter

| Parameter | Spezifikation |
|------|------|
| Gewicht | ca. 0,416 kg |
| Fingeranzahl | 4 |
| Freiheitsgrade pro Finger | 2 DoF |
| Gestreckte Höhe (ohne Sockel) | 195 mm |
| Handflächenbreite | 105 mm |
| Handflächendicke | ca. 90 mm |
| Maximaler Abstand zwischen Zeigefinger und Daumen | 180 mm |
| Traglast pro Finger | ca. 0,2 kg |
| Maximale Traglast bei geschlossener Vierfingerfaust | ca. 0,5 kg |

> Traglast, Spannung und Servo-Parameter hängen von der gewählten Servo-Version ab; die vollständige Gegenüberstellung findest du unter [Versionsvergleich und Auswahl](version-comparison.md).

## Zwei Hardware-Varianten

| Projekt | SCS0009-Seriell-Bus-Version | PWM-Servo-Version |
|------|--------------------|------------|
| Servo | Feetech SCS0009 ×8 | PTK 7452 MG-D digitaler PWM-Servo ×8 |
| Steuerung | PC/Raspberry Pi + Bus-Treiberplatine | ESP32-S3-Onboard-Firmware |
| Rückmeldung | Positions-/Geschwindigkeits-/Spannungs-/Temperaturrücklesung | keine Rücklesung |
| Geeignet für | Genauigkeit, Datenerfassung, LeRobot / SO-ARM101 | eigenständige Demonstration, Gesteninteraktion, schneller Einstieg |

## Software-Ökosystem

- **Websteuerung**: Browser-Schieberegler, 19 Preset-Posen, MediaPipe-Kamera-Teleop, Umschaltung zwischen SCS0009-/PWM-Treiber.
- **Desktop-GUI**: SCS0009 verwendet `AmazingHandControl` (Tkinter-GUI + CLI); PWM verwendet `AmazingHand-PWM/tools/hand_gui.py`.
- **Handtracking**: SCS0009 bietet das offizielle dora + MuJoCo-IK-Demo; PWM bietet integriertes MediaPipe-Tracking in der GUI.
- **Open-Source-Ressourcen**: CAD, Montage-/Druckdokumentation und Arduino-/Python-Beispiele sind im Repository enthalten.

## Open-Source-Ressourcen

- [Montageanleitung PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [Empfehlungen für den 3D-Druck PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand-Übersicht PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [CAD / STL / STEP](../../../AmazingHand-main/cad/)
- [Offizielles Upstream-Projekt (Pollen Robotics)](https://github.com/pollen-robotics/AmazingHand)

## Nächste Schritte

- [Versionsvergleich und Auswahl](version-comparison.md)
- [Hardware-Übersicht](../01-hardware/overview.md)
- [SCS0009-Schnellstart](../02-quick-start/scs0009.md)
- [PWM-Schnellstart](../02-quick-start/pwm.md)
