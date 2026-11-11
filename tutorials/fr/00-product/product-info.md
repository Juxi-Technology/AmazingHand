---
title: "Informations produit AmazingHand"
description: "Informations produit de la main dextre AmazingHand : structure mécanique, dimensions, charge, deux solutions de servos et ressources open source."
version: both
---

# Informations produit AmazingHand

AmazingHand est une main dextre humanoïde open source et imprimable en 3D, destinée à la recherche en intelligence incarnée, à l'éducation robotique et aux prototypes d'interaction homme-machine. Le corps de la main est identique ; deux architectures matérielles sont proposées : **servos à bus série SCS0009** et **servos PWM (ESP32-S3)**.

## Structure mécanique

- **4 doigts, 8 degrés de liberté** : 2 degrés de liberté par doigt (flexion + écartement), entraînés par deux servos via un mécanisme parallèle à entraînement différentiel.
- **Actionneurs intégrés** : tous les servos sont montés dans la main, sans câblage à tirer vers l'avant-bras.
- **Impression 3D** : boîtier et tringlerie imprimables ; main d'environ 400 g.
- **Prise en charge des deux mains** : main gauche ou droite utilisable seule, ou coordination des deux mains sur un robot.
- **Interface de poignet** : la conception d'origine s'adapte au poignet Orbita 3D du Reachy 2 ; adaptation possible à d'autres bras robotisés.

## Caractéristiques de base

| Paramètre | Spécification |
|------|------|
| Poids | environ 0.416 kg |
| Nombre de doigts | 4 |
| Degrés de liberté par doigt | 2 DoF |
| Hauteur déployée (sans base) | 195 mm |
| Largeur de la paume | 105 mm |
| Épaisseur de la paume | environ 90 mm |
| Distance maximale entre index et pouce | 180 mm |
| Charge d'un doigt | environ 0.2 kg |
| Charge maximale des quatre doigts serrés | environ 0.5 kg |

> La charge, la tension et les caractéristiques des servos varient selon la version de servos choisie ; tableau complet dans [Comparaison des versions et choix](version-comparison.md).

## Deux architectures matérielles

| Élément | Version à bus série SCS0009 | Version à servos PWM |
|------|--------------------|------------|
| Servos | Feetech SCS0009 ×8 | Servos PWM numériques PTK 7452 MG-D ×8 |
| Contrôle | PC/Raspberry Pi + carte de commande de bus | Firmware embarqué ESP32-S3 |
| Retour | Relecture position/vitesse/tension/température | Aucun retour |
| Usage | Précision, collecte de données, LeRobot / SO-ARM101 | Démonstration autonome, interaction par gestes, démarrage rapide |

## Écosystème logiciel

- **Contrôle web** : curseurs dans le navigateur, 19 poses prédéfinies, téléopération caméra MediaPipe, bascule de driver SCS0009 / PWM.
- **Outil de bureau** : SCS0009 utilise `AmazingHandControl` (GUI Tkinter + CLI) ; PWM utilise `AmazingHand-PWM/tools/hand_gui.py`.
- **Suivi de main** : SCS0009 fournit la démo officielle dora + IK MuJoCo ; PWM fournit un suivi MediaPipe intégré à la GUI.
- **Ressources open source** : CAO, documentation d'assemblage/impression, exemples Arduino/Python, tous présents dans le dépôt.

## Ressources open source

- [Guide d'assemblage PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [Conseils d'impression 3D PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [Vue d'ensemble AmazingHand PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [CAO / STL / STEP](../../../AmazingHand-main/cad/)
- [Projet amont officiel (Pollen Robotics)](https://github.com/pollen-robotics/AmazingHand)

## Étapes suivantes

- [Comparaison des versions et choix](version-comparison.md)
- [Vue d'ensemble du matériel](../01-hardware/overview.md)
- [Démarrage rapide SCS0009](../02-quick-start/scs0009.md)
- [Démarrage rapide PWM](../02-quick-start/pwm.md)
