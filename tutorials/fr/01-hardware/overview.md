---
title: "Vue d'ensemble du matériel : structure, CAO et assemblage"
description: "Structure mécanique, CAO/STL/STEP, assemblage et ressources d'impression 3D AmazingHand."
version: both
---

# Vue d'ensemble du matériel

Les deux solutions de servos partagent la même structure mécanique ; les différences portent sur le modèle de servo, la carte de commande et le câblage. Avant d'assembler la main, confirmez la version choisie.

## Structure mécanique

- 4 doigts, 2 degrés de liberté chacun : flexion/extension + abduction/adduction.
- Chaque doigt est entraîné par deux servos via un mécanisme parallèle à entraînement différentiel ; tous les servos sont montés dans la main.
- Boîtier, tringlerie et phalanges souples imprimés en 3D ; main d'environ 400 g.
- L'interface de poignet d'origine s'adapte à l'Orbita 3D du Reachy 2 ; adaptation possible à d'autres bras robotisés.

## CAO et modèles

- Fichiers STL / STEP : [`AmazingHand-main/cad/`](../../../AmazingHand-main/cad/)
- Document en ligne Onshape et URDF : voir la section CAO de [`AmazingHand-main/README_CN.md`](../../../AmazingHand-main/README_CN.md).

## Assemblage et impression 3D

- [Guide d'assemblage PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [Conseils d'impression 3D PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [Vue d'ensemble AmazingHand PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)

> Avant l'assemblage, placez la main en position médiane et montez les palonniers en position médiane ; les palonniers/cannelures et les courses des deux types de servos diffèrent et ne sont pas interchangeables.

## Câblage des deux architectures

| Version | Guide de câblage et d'alimentation |
|------|----------------|
| Version à bus série SCS0009 | [Câblage, ID et alimentation SCS0009](scs0009.md) |
| PWM (ESP32-S3) | [Câblage, GPIO et alimentation PWM](pwm.md) |
| Kit caméra | [Installation du kit caméra](camera-kit.md) |

## Étapes suivantes

- [Comparaison des versions et choix](../00-product/version-comparison.md)
- [Démarrage rapide : SCS0009](../02-quick-start/scs0009.md) · [Démarrage rapide : PWM](../02-quick-start/pwm.md)
