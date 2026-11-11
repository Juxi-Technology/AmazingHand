---
title: "Comparaison et choix entre les versions SCS0009 et PWM"
description: "Comparaison complète des deux architectures matérielles AmazingHand : servos, retour d'information, contrôleur, alimentation, communication, ID/canaux, firmware et cas d'usage."
version: both
---

# Comparaison et choix entre les versions SCS0009 et PWM

La structure mécanique de la main AmazingHand est identique, mais deux solutions de servos existent. Le choix dépend principalement du besoin de **retour de position, de contrôle précis de l'angle et de collecte de données**.

## Conclusion rapide

- **Choisir SCS0009** : besoin de relecture position/température/tension, d'angles précis, d'intégration au bras SO-ARM101 pour la collecte et l'entraînement de données LeRobot.
- **Choisir PWM** : démonstration autonome, interaction par gestes, démarrage rapide web/bureau, sans besoin de retour.
- **Ne pas mélanger** : une seule architecture à la fois ; alimentation, protocole et firmware diffèrent.

## Comparaison complète

| Élément de comparaison | Version à bus série SCS0009 | Version à servos PWM |
|--------|--------------------|------------|
| Raison recommandée | Contrôle précis de l'angle + relecture des données ; intégrable au bras SO-ARM101 pour la collecte et l'entraînement LeRobot | Démonstration autonome, interaction par gestes, démarrage rapide |
| Modèle de servo | Servos à bus série Feetech SCS0009 ×8 | Servos PWM **numériques** PTK 7452 MG-D ×8 |
| Caractéristiques des servos | 2.3 kg·cm@6V, 300° contrôlables, précision 0.293° | 4.5 kg·cm@7.4V (environ 2.8–3 kg·cm avec l'alimentation 5V de cette solution), 180°±10°, rafraîchissement 333 Hz |
| Retour position/température/tension/vitesse | ✅ Relecture prise en charge | ❌ Aucun retour ; blocage ou perte de pas non détectable |
| Contrôleur | Aucun embarqué ; PC/Raspberry Pi connecté directement via la carte de commande de bus | Firmware embarqué ESP32-S3 |
| Concentrateur | Carte de commande de servos + concentrateur de bus série 9 voies | Carte d'adaptation PWM (8 connecteurs 3 broches + 5V/GND) |
| Alimentation | Entrée 7–12V (DC5521) sur la carte de commande, servos de classe 6V | 5V / 3A ou plus, masse commune obligatoire entre carte d'adaptation et ESP32 |
| Débit | **1,000,000** | Pas de débit pour les servos ; série PC hôte ↔ ESP32 **115200 8N1** |
| ID de servo | À définir : droite 1–8, gauche 11–18 | Aucun ID ; canaux fixes CH1–CH8 (index 1/2, majeur 3/4, annulaire 5/6, pouce 7/8), câblage identique gauche/droite |
| Chaîne de communication | PC hôte → carte de commande → bus → 8 servos | PC hôte → port série USB 115200 → ESP32 → 8 voies PWM |
| Forme des commandes | Protocole de bus Feetech, angle envoyé directement | Trames binaires : gestes `0x01–0x0A / 0x0C`, pilotage direct `0xF0`, main gauche/droite `0xF1`, NOP `0x00`, répétition `0xFE`, arrêt `0xFF` |
| Firmware | Aucun (pas de flashage) | Compilation ESP-IDF requise, ou flashage direct du `amazinghand_pwm.bin` précompilé |
| Main gauche/droite | ID de servos différents (droite 1–8, gauche 11–18) | Même groupe de canaux, mapping logiciel + sélection du côté par `0xF1` |
| Relâchement du couple | Activation/relâchement du couple pris en charge | Non pris en charge ; l'arrêt d'urgence interrompt seulement le geste, les servos restent alimentés et gardent leur position |
| Contrôle de vitesse | Paramètre de vitesse pris en charge | Les trames de pilotage direct n'ont pas de paramètre de vitesse |

## Points clés de la version SCS0009

- Chaque servo possède un ID unique ; main droite 1–8, main gauche 11–18 ; après câblage/remplacement d'un servo, l'ID doit être redéfini.
- Bus série avec relecture de position, vitesse, tension et température ; adapté au contrôle en boucle fermée et à la collecte de données.
- Le PC/Raspberry Pi commande directement via la carte de commande de bus USB, sans firmware MCU supplémentaire.
- Alimentation 7–12V en entrée de la carte de commande de bus (servos de classe 6V) ; veiller à la masse commune avec la carte.
- Adapté aux flux d'entraînement nécessitant un retour d'articulation, comme SO-ARM101 et LeRobot.

## Points clés de la version PWM

- Utilise des **servos numériques PTK 7452 MG-D** (333 Hz, 500–2500 µs) ; les servos analogiques 50 Hz comme le SG90 ne peuvent pas les remplacer directement.
- Servo donné pour 4.5 kg·cm@7.4V ; avec l'alimentation 5V/3A de cette solution, le couple réel est d'environ 2.8–3 kg·cm.
- L'ESP32-S3 génère 8 voies PWM ; le PC hôte n'a qu'à envoyer des commandes via le port série USB à 115200.
- Aucun retour de position ; impossible de lire l'angle, la température ou la tension, ni de détecter un blocage/une perte de pas.
- Gauche et droite partagent le même groupe de canaux ; pour chaque doigt, le servo de droite est impair et celui de gauche pair ; l'index est toujours CH1/2.
- Firmware à flasher ; le dépôt fournit un bin précompilé, ou une compilation via ESP-IDF.
- Adapté à la démonstration autonome, l'interaction par gestes et le démarrage rapide web/bureau ; non adapté à l'entraînement LeRobot dépendant du retour.

## Étapes suivantes

- [Démarrage rapide SCS0009](../02-quick-start/scs0009.md)
- [Démarrage rapide PWM](../02-quick-start/pwm.md)
- [Vue d'ensemble du matériel](../01-hardware/overview.md)
- [Téléchargements et ressources](downloads.md)
