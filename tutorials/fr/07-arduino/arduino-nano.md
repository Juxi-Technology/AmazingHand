---
title: "Tutoriel Arduino Nano"
description: "Exécuter le « programme de démonstration 02 » d'AmazingHand avec un Arduino Nano (328P) et une carte de commande de servos : câblage, installation des bibliothèques, compilation, téléversement et résultat."
version: scs0009
---

# Tutoriel Arduino Nano

> Cette page présente la démonstration Arduino Nano de la **version à bus série SCS0009**. Câblage TTL et définition des ID : [Débogage et calibration des servos SCS0009](../06-servo-tuning/scs0009.md) ; autres exemples : [Exemples Arduino / Python](examples.md).


## Câblage (carte de commande de servos + carte Nano)

**Repérez bien l'emplacement des broches de la carte Nano (carte de développement 328P) !**

![Emplacement des broches de la carte Nano (1)](../../assets/robot-arms/amazing-hand/arduino-nano/01.png)

![Emplacement des broches de la carte Nano (2)](../../assets/robot-arms/amazing-hand/arduino-nano/02.png)

![Emplacement des broches de la carte Nano (3)](../../assets/robot-arms/amazing-hand/arduino-nano/03.png)

![Emplacement des broches de la carte Nano (4)](../../assets/robot-arms/amazing-hand/arduino-nano/04.png)

Ce qui suit décrit la procédure de débogage avec le microcontrôleur. Le microcontrôleur exécute en boucle le programme de démonstration ; il suffit de débrancher le câble de données pour l'arrêter.

## Exécuter le « programme de démonstration 02 »

1. Installez vous-même l'IDE Arduino.

2. Selon la **main gauche ou droite**, ouvrez le fichier `.ino` correspondant.

   ![Fichiers .ino du programme de démonstration 02 pour main gauche/droite](../../assets/robot-arms/amazing-hand/arduino-nano/05.png)

3. Avant de compiler et téléverser le programme Arduino sur la carte Nano, installez les bibliothèques **FTServo** et **SCServo** dans le « gestionnaire de bibliothèques ».

   ![Installation des bibliothèques FTServo et SCServo dans le gestionnaire de bibliothèques](../../assets/robot-arms/amazing-hand/arduino-nano/06.png)

4. Pour le type de carte Nano, choisissez « **Arduino Nano** ».

   ![Sélection du type de carte Arduino Nano](../../assets/robot-arms/amazing-hand/arduino-nano/07.png)

5. Compilez et téléversez.

> **Attention :** à ce stade, l'ordinateur est connecté uniquement à la carte Nano, et la carte Nano ne doit pas encore être reliée à la carte de commande de servos (c'est-à-dire pas reliée à la main dextre).

Après un téléversement réussi, reliez la carte Nano à la carte de commande de servos par trois câbles de liaison, connectez les servos à la carte de commande, en suivant [le câblage de débogage de la carte MEGA328P Nano](https://juxitech.feishu.cn/wiki/Wt46wtt26imdWkkQlxTcL87qnHd#share-HdS4dNgwyo2seVxRZ9PcZ1R3nuc).

La main dextre exécute alors en boucle le « programme de démonstration 02 » ; résultat ci-dessous :

![Résultat d'exécution du programme de démonstration 02](../../assets/robot-arms/amazing-hand/arduino-nano/08.png)
