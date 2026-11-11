---
title: "Câblage, GPIO et alimentation PWM"
description: "Version à servos PWM d'AmazingHand : ESP32-S3, 8 canaux PWM, mapping GPIO, alimentation et modèle de servo."
version: pwm
---

# Câblage, GPIO et alimentation PWM

Dans la version PWM, l'ESP32-S3 génère directement les 8 signaux PWM ; l'ordinateur n'a qu'à envoyer des commandes via le port série USB.

## Liste du matériel

| Élément | Spécification |
|------|------|
| Contrôleur | Carte de développement ESP32-S3 (Youxin YX-ESP32-S3 ou équivalent) |
| Servos | Servos PWM **numériques** PTK 7452 MG-D ×8 (333 Hz) |
| Carte d'adaptation | Carte d'adaptation pour servos PWM (8 connecteurs 3 broches + 5V/GND) |
| Alimentation | 5V / 3A ou plus ; masse commune obligatoire entre carte d'adaptation et ESP32 |

> Servo donné pour 4.5 kg·cm@7.4V ; avec l'alimentation 5V de cette solution, le couple réel est d'environ 2.8–3 kg·cm.
>
> ⚠️ Les servos analogiques 50 Hz comme le SG90 ne peuvent pas remplacer directement le firmware 333 Hz ; changer de modèle impose de modifier à la fois `LEDC_FREQ` et la calibration de la largeur d'impulsion.

## Canal → GPIO → doigt

| Canal | GPIO | Articulation | Canal | GPIO | Articulation |
|------|------|------|------|------|------|
| PWM1 / CH1 | 4 | Index articulation 1 | PWM5 / CH5 | 15 | Annulaire articulation 1 |
| PWM2 / CH2 | 5 | Index articulation 2 | PWM6 / CH6 | 16 | Annulaire articulation 2 |
| PWM3 / CH3 | 6 | Majeur articulation 1 | PWM7 / CH7 | 17 | Pouce articulation 1 |
| PWM4 / CH4 | 7 | Majeur articulation 2 | PWM8 / CH8 | 18 | Pouce articulation 2 |

- Câblage identique pour les deux mains ; l'index est toujours CH1/2.
- Pour chaque doigt, le servo de droite est sur un canal impair, celui de gauche sur un canal pair.
- Les numéros de canal sont fixés par le firmware ; aucun ID de servo à définir.

## Étapes de câblage

1. Branchez les connecteurs 3P des 8 servos sur les broches servo 1–8 de la carte d'adaptation, selon leur numéro.
2. Reliez PWM1–PWM8 de la carte d'adaptation aux GPIO 4, 5, 6, 7, 15, 16, 17, 18 de l'ESP32-S3.
3. Reliez le 5V/GND de la carte d'adaptation à l'alimentation externe 5V/3A.
4. Ramenez une paire 5V/GND de la carte d'adaptation vers l'ESP32-S3 ; **masse commune obligatoire**.
5. Ordre des fils 3P des servos : brun/noir GND, rouge V+, orange/blanc/jaune signal ; suivez la sérigraphie de la carte d'adaptation, ne les inversez pas.

## Alimentation et sécurité

- Les 8 servos en mouvement simultané consomment beaucoup ; prévoyez 5V / 3A ou plus et évitez l'alimentation par USB seule.
- Avant la première mise sous tension, placez la main en position médiane et montez les palonniers à 90°.
- Les canaux non connectés peuvent rester libres sans affecter les autres ; isolez les connecteurs vides.
- L'ouverture du port série peut réinitialiser l'ESP32 ; le firmware revient automatiquement en position médiane.

## Étapes suivantes

- [Démarrage rapide PWM](../02-quick-start/pwm.md) (flashage du firmware + GUI/web)
- [Protocole et calibration PWM](../06-servo-tuning/pwm.md)
- [Contrôle web](../03-web-control/pwm.md)
