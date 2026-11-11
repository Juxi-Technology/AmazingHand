---
title: "Vue d'ensemble du tutoriel AmazingHand"
description: "Point d'entrée unifié du tutoriel de la main dextre AmazingHand : choix entre la version à servos à bus série SCS0009 et la version à servos PWM, câblage matériel, démarrage rapide, contrôle web, outil de bureau, suivi de main, calibration des servos et FAQ."
version: both
---

# Tutoriel de la main dextre AmazingHand

AmazingHand est une main dextre humanoïde open source et imprimable en 3D : 4 doigts, 8 degrés de liberté, tous les actionneurs intégrés dans la main, environ 400 g. Deux architectures matérielles sont actuellement proposées ; la structure mécanique de la main est identique, seuls les servos, la carte de commande et le mode de communication diffèrent.

## Choisir d'abord la version

| Élément de comparaison | Version à bus série SCS0009 | Version à servos PWM |
|--------|--------------------|------------|
| Cas recommandé | Contrôle précis de l'angle, relecture des données, intégration à la collecte et à l'entraînement de données SO-ARM101 / LeRobot | Démonstration autonome, interaction par gestes, démarrage rapide web/bureau |
| Servos | Servos à bus série Feetech SCS0009 ×8 | Servos PWM **numériques** PTK 7452 MG-D ×8 |
| Caractéristiques des servos | 2.3 kg·cm@6V, 300° contrôlables, précision 0.293° | 4.5 kg·cm@7.4V (environ 2.8–3 kg·cm sous alimentation 5V), 180°±10°, 333 Hz |
| Retour position/température/tension | ✅ Pris en charge | ❌ Aucun retour ; blocage ou perte de pas non détectable |
| Contrôleur | Aucun embarqué ; PC/Raspberry Pi connecté directement via la carte de commande de bus | Firmware embarqué ESP32-S3 |
| Alimentation | Entrée 7–12V (DC5521) sur la carte de commande | 5V / 3A ou plus, masse commune obligatoire |
| Communication | Protocole de bus à 1,000,000 bauds | PC hôte ↔ ESP32 en série **115200** (les servos eux-mêmes n'ont pas de débit) |
| ID de servo | À définir : main droite 1–8, main gauche 11–18 | Pas d'ID ; canaux fixes CH1–CH8 : index 1/2, majeur 3/4, annulaire 5/6, pouce 7/8 |
| Firmware | Aucun flashage nécessaire | Compilation ESP-IDF requise, ou flashage direct du bin précompilé |

> Si vous avez besoin de **relecture de position, de précision ou de collecte de données d'entraînement LeRobot**, choisissez SCS0009 ; si vous voulez seulement une **démonstration autonome, une interaction par gestes ou un démarrage rapide**, choisissez PWM.

Comparaison complète et guide de choix : [Comparaison des versions](00-product/version-comparison.md).

## Navigation par mode d'utilisation

| Mode d'utilisation | Version à bus série SCS0009 | Version à servos PWM |
|----------|--------------------|------------|
| Démarrage rapide | [Démarrage rapide SCS0009](02-quick-start/scs0009.md) | [Démarrage rapide PWM](02-quick-start/pwm.md) |
| Contrôle web | [Contrôle web SCS0009](03-web-control/scs0009.md) | [Contrôle web PWM](03-web-control/pwm.md) |
| Outil de bureau / CLI | [GUI et CLI SCS0009](04-desktop/scs0009.md) | [Outil de bureau PWM](04-desktop/pwm.md) |
| Suivi de main | [Démo officielle SCS0009](05-hand-tracking/scs0009.md) | [Suivi GUI / dora PWM](05-hand-tracking/pwm.md) |
| Débogage et calibration des servos | [Débogage et calibration SCS0009](06-servo-tuning/scs0009.md) | [Protocole et calibration PWM](06-servo-tuning/pwm.md) |
| Arduino / développement secondaire | [Arduino Nano](07-arduino/arduino-nano.md) · [Exemples de code](07-arduino/examples.md) | Idem (structure mécanique partagée) |

Vue d'ensemble du contrôle web (bascule de driver, barre de port série, description de l'interface) : [README du contrôle web](03-web-control/README.md).

## Avant de commencer

- [Informations produit](00-product/product-info.md) — caractéristiques, positionnement, ressources
- [Comparaison des versions et choix](00-product/version-comparison.md) — différences complètes entre les deux architectures
- [Vue d'ensemble du matériel](01-hardware/overview.md) — structure, CAO, assemblage, impression 3D
- [Câblage SCS0009](01-hardware/scs0009.md) / [Câblage PWM](01-hardware/pwm.md)
- [Installation du kit caméra](01-hardware/camera-kit.md)
- [Téléchargements et ressources](00-product/downloads.md)

## Consignes de sécurité

- L'alimentation externe des servos et l'ESP32/la carte de commande doivent impérativement partager la **masse commune**.
- Avant la première mise sous tension, placez la main en position médiane et montez les palonniers de servo en position médiane, pour éviter de buter en fin de course.
- Les deux architectures SCS0009 et PWM ne se branchent pas en même temps ; ne les mélangez pas.
- Les servos PWM n'ont pas de retour de position : l'arrêt d'urgence ne peut qu'interrompre le geste, sans lire ni relâcher le couple comme sur les servos à bus.

## Languages

[简体中文](../zh-hans/README.md) | [English](../en/README.md) | [Deutsch](../de/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (BR)](../pt-br/README.md) | [Português (PT)](../pt-pt/README.md) | [繁體中文](../zh-hant/README.md)
