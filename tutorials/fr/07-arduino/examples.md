---
title: "Exemples Arduino et Python"
description: "Exemples Arduino/Python officiels AmazingHand : bibliothèque SCServo, outil de débogage Feetech, modes de câblage TTL Linker, ports série Arduino Uno/Mega et scripts Python de base."
version: scs0009
---

# Exemples Arduino et Python

Cette page rassemble les exemples officiels et les points clés de câblage de `AmazingHand-main/ArduinoExample/` et `AmazingHand-main/PythonExample/`.

## Exemples Arduino

### Préparation

- Installez la bibliothèque **SCServo** dans le gestionnaire de bibliothèques de l'IDE Arduino.
- Utilisez l'outil de débogage Feetech FD (`feetech debug tool`) pour définir les ID de servo.
- Entre l'Arduino et le TTL Linker, **croisez RX/TX**.

### Mode Link : modifier l'ID de servo

1. Téléversez d'abord l'exemple `Blink` sur l'Arduino.
2. Câblez selon le mode Link, ouvrez le logiciel Feetech et modifiez l'ID.

![Câblage en mode Link](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Link-mode.jpg)

![Installation de la bibliothèque SCServo](../../assets/robot-arms/amazing-hand/arduino-extension/SCServo.jpg)

### Mode Control : l'Arduino commande les servos

Après avoir téléversé un programme personnalisé, câblez selon le mode Control :

![Câblage en mode Control](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Control-mode.jpg)

- **Arduino Uno** (un seul port série) : suivez le schéma et utilisez un port série logiciel/des broches dédiées.
- **Arduino Mega** : utilisez **RX1 / TX1 (19 / 18)**.

![Câblage du port série Uno](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Uno.jpg)

![Câblage du port série Mega](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Mega.jpg)

> Les numéros de broches, versions de bibliothèques et le sens du TTL Linker dépendent de la sérigraphie réelle de la carte ; avant de changer un ID, vérifiez l'alimentation du bus et la masse commune.

## Exemples Python

`AmazingHand-main/PythonExample/` fournit 4 scripts de base :

| Script | Rôle |
|------|------|
| `AmazingHand_Demo.py` | Démonstration de base d'une main : connexion au bus, exécution de mouvements |
| `AmazingHand_Demo_Both.py` | Démonstration des deux mains |
| `AmazingHand_FingerTest.py` | Test d'un seul doigt |
| `AmazingHand_Hand_FingerMiddlePos.py` | Calibration de la position médiane des doigts |

Avant utilisation :

1. Définissez les ID de servo avec le logiciel Feetech (droite 1–8, gauche 11–18).
2. Installez `pyserial`, adaptez le nom de port série/débit dans le script puis exécutez.
3. Confirmez que l'alimentation externe des servos est connectée et partage la masse commune avec la carte de commande de bus.

> Ce sont des exemples de base officiels ; pour une GUI/CLI plus complète, voir [Outil de bureau SCS0009](../04-desktop/scs0009.md) ; câblage TTL et position médiane : [Débogage et calibration des servos SCS0009](../06-servo-tuning/scs0009.md).

## Emplacement des sources

- [`AmazingHand-main/ArduinoExample/`](../../../AmazingHand-main/ArduinoExample/)
- [`AmazingHand-main/PythonExample/`](../../../AmazingHand-main/PythonExample/)
