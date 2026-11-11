---
title: "Arduino Nano – Anleitung"
description: "Das AmazingHand-„02-Demoprogramm" mit Arduino Nano (328P) und Servo-Treiberplatine ausführen: Verkabelung, Bibliotheksinstallation, Kompilieren/Hochladen und Ergebnis."
version: scs0009
---

# Arduino Nano – Anleitung

> Diese Seite ist das Arduino-Nano-Demo der **SCS0009-Bus-Servo-Version**. TTL-Verkabelung und ID-Einstellung siehe [SCS0009-Servo-Debugging und Kalibrierung](../06-servo-tuning/scs0009.md), weitere Beispiele siehe [Arduino-/Python-Beispiele](examples.md).


## Verkabelung (Servo-Treiberplatine + Nano-Board)

**Auf die Pinpositionen des Nano-Boards (d. h. des 328P-Entwicklungsboards) achten!**

![Pinpositionen des Nano-Boards (1)](../../assets/robot-arms/amazing-hand/arduino-nano/01.png)

![Pinpositionen des Nano-Boards (2)](../../assets/robot-arms/amazing-hand/arduino-nano/02.png)

![Pinpositionen des Nano-Boards (3)](../../assets/robot-arms/amazing-hand/arduino-nano/03.png)

![Pinpositionen des Nano-Boards (4)](../../assets/robot-arms/amazing-hand/arduino-nano/04.png)

Im Folgenden wird der Debugging-Ablauf mit dem Mikrocontroller beschrieben. Der Mikrocontroller führt das Demo-Programm fortlaufend in einer Schleife aus; zum Stoppen einfach das Datenkabel abziehen.

## „02-Demoprogramm" ausführen

1. Arduino IDE selbst installieren.

2. Je nach **linker oder rechter Hand** die entsprechende `.ino`-Datei öffnen.

   ![ino-Dateien des 02-Demoprogramms für linke/rechte Hand](../../assets/robot-arms/amazing-hand/arduino-nano/05.png)

3. Vor dem Kompilieren und Hochladen des Arduino-Programms auf das Nano-Board in der „Bibliotheksverwaltung" die **FTServo-Bibliothek** und die **SCServo-Bibliothek** installieren.

   ![FTServo- und SCServo-Bibliothek in der Bibliotheksverwaltung installieren](../../assets/robot-arms/amazing-hand/arduino-nano/06.png)

4. Board-Typ „**Arduino Nano**" wählen.

   ![Board-Typ Arduino Nano wählen](../../assets/robot-arms/amazing-hand/arduino-nano/07.png)

5. Kompilieren und hochladen.

> **Achtung:** Der PC ist jetzt nur mit dem Nano-Board verbunden, das Nano-Board noch nicht mit der Servo-Treiberplatine (also nicht mit der Dexterhand).

Nach erfolgreichem Hochladen das Nano-Board über drei Jumperkabel mit der Servo-Treiberplatine verbinden, die Servos an die Servo-Treiberplatine, siehe [Verkabelung beim Debugging mit dem MEGA328P-Nano-Board](https://juxitech.feishu.cn/wiki/Wt46wtt26imdWkkQlxTcL87qnHd#share-HdS4dNgwyo2seVxRZ9PcZ1R3nuc).

Die Dexterhand führt das „02-Demoprogramm" fortlaufend in einer Schleife aus, Ergebnis:

![Ergebnis des 02-Demoprogramms](../../assets/robot-arms/amazing-hand/arduino-nano/08.png)
