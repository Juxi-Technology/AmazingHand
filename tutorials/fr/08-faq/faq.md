---
title: "Questions fréquentes (FAQ)"
description: "Questions fréquentes AmazingHand : généralités, SCS0009, PWM, contrôle web, outils de bureau et suivi de main."
version: both
---

# Questions fréquentes (FAQ)

## Généralités

**Faut-il choisir SCS0009 ou PWM ?**
SCS0009 pour le retour de position, la précision et la collecte de données LeRobot/SO-ARM101 ; PWM pour la démonstration autonome, l'interaction par gestes et le démarrage rapide web/bureau. Détails : [Comparaison des versions](../00-product/version-comparison.md).

**Peut-on brancher les deux types de servos en même temps ?**
Non. Alimentation, protocole et firmware diffèrent ; une seule architecture à la fois.

**Peut-on mettre la main sous tension directement ?**
Avant la première mise sous tension, placez la main en position médiane et montez les palonniers en position médiane ; l'alimentation externe et la carte de commande/l'ESP32 doivent partager la masse commune.

**Peut-on changer de modèle de servo ?**
La version SCS0009 utilise des servos à bus ; le firmware PWM est calibré pour le PTK 7452 MG-D (servo numérique 333 Hz). Les servos analogiques 50 Hz comme le SG90 ne peuvent pas remplacer directement la version PWM : il faut modifier `LEDC_FREQ` et la calibration de la largeur d'impulsion.

## Version à bus série SCS0009

**Sens du mouvement inversé** → vérifiez si le câblage respecte « ID impair en premier » ; pour la main gauche, confirmez `angle_offset_deg = -35.16`.

**Poing gauche insuffisant / servos qui sifflent** → vérifiez si la limite de `config.json` est bien à ±120° (la valeur par défaut ±90 rogne le poing de la main gauche).

**Doigt immobile / message « N moteurs attendus, M détectés »** → lancez `tools/scan_servos.py` ; les ID de la main gauche sont les plus faciles à mal câbler (11–18, pas 9–16).

**Position médiane incorrecte** → la valeur médiane `-17.578125` correspond au brut officiel 451/571 ; pour calibrer selon votre assemblage, modifiez `middle.positions` dans `config.json`.

**Comment définir les ID de servo ?** → utilisez l'[outil de débogage SCS0009](../06-servo-tuning/scs0009.md) pour scanner et modifier les ID ; main droite 1–8, main gauche 11–18.

**Linux n'ouvre pas le port série** → ajoutez l'utilisateur courant au groupe `dialout` et reconnectez-vous.

**Peut-on lire position/température/tension ?** → oui, SCS0009 prend en charge la relecture de position, vitesse, tension et température ; table mémoire du protocole : [`scs_servo_protocol.md`](../../../AmazingHandControl/docs/zh-hans/scs_servo_protocol.md).

## Version à servos PWM

**Échec de connexion / ESP32 sans réponse** → vérifiez le débit 115200, le port COM de l'ESP32, l'alimentation 5V/3A et la masse commune ; l'ouverture du port série peut réinitialiser la carte, la page réessaie automatiquement le NOP.

**Servos immobiles ou vibrants** → vérifiez qu'il s'agit de servos numériques 333 Hz (PTK 7452 MG-D ou équivalent) et que l'alimentation suffit ; le SG90 nécessite une modification du firmware.

**Direction inversée** → dans `pwm.calibration` de `config.json` côté web, passez le `scale` du doigt concerné à `-1`.

**Milieu incorrect** → ajustez l'`offset_deg` du canal concerné ; détails : [Protocole, commandes et calibration PWM](../06-servo-tuning/pwm.md).

**Message « occupé (geste en cours) »** → le firmware exécute un geste intégré ; attendez la fin ou envoyez l'arrêt (`0xFF`).

**La version PWM a-t-elle un retour ?** → pas de relecture position/température/tension ; blocage ou perte de pas non détectable.

**Les servos PWM ont-ils un débit ?** → non, pas les servos eux-mêmes ; le port série PC hôte ↔ ESP32 est fixe à 115200 8N1.

**Peut-on tester avec seulement une partie des servos ?** → oui. Les canaux non connectés restent libres sans affecter les autres ; isolez les connecteurs vides.

**La caméra affiche une image mais la main ne suit pas / réaction lente** → éclairage uniforme, paume à environ 40–80 cm de la caméra et face à elle ; fermez les autres programmes utilisant la caméra ; confirmez que le port série est connecté. Paramètres de suivi de la GUI : [Suivi de main PWM](../05-hand-tracking/pwm.md).

**La bascule gauche/droite ne prend pas effet** → le firmware utilise `0xF1` pour basculer gauche/droite (la page web l'envoie automatiquement à la connexion) ; ce réglage affecte surtout le sens du pouce des gestes intégrés au firmware ; les poses web utilisent le mapping de la main sélectionnée.

**L'image de suivi se fige / le journal s'arrête** → arrêtez puis redémarrez le suivi ; si toujours sans réponse, fermez et rouvrez la GUI, et vérifiez que la caméra n'est pas occupée par un autre programme.

**Port série introuvable après changement de port USB** → vérifiez le nouveau numéro COM dans le gestionnaire de périphériques, cliquez sur « Refresh » dans la GUI ou la page web puis resélectionnez.

## Contrôle web

**Échec du modèle / échec du chargement du suivi caméra** → confirmez que la page est servie par un serveur local (pas ouverte directement en `file://`) et que le chemin des ressources MediaPipe est accessible ; le tutoriel local a corrigé le routage MediaPipe côté serveur. En cas d'échec persistant, consultez Console/Network du navigateur pour les erreurs 404 ou de permission.

**Reconnaissance caméra imprécise** → éclairage uniforme, paume face à la caméra ; dans `tracking.js`, `SMOOTH` (défaut 0.35) plus grand = plus lisse mais plus lent.

**Un doigt ne suit pas** → recapturez les trois poses ; si un sens est inversé, recapturez la pose correspondante ; le pouce ne fait que fléchir et ne participe pas à l'écartement.

**Un servo s'inverse à mi-poings** → l'écartement doit s'atténuer jusqu'à 0 avec la flexion (`side *= (1 - curl)`) ; vérifiez le signe et l'amplitude de la commande d'écartement.

**Comment basculer le driver web ?** → dans la liste « Driver » en haut, choisissez SCS0009 ou PWM ; pour PWM, sélectionnez un port série 115200 ; détails : [Vue d'ensemble du contrôle web](../03-web-control/README.md).

## Outils de bureau

**La GUI SCS0009 ne liste aucun port série** → rebranchez l'adaptateur USB, installez le pilote ou redémarrez la GUI ; sous Linux, vérifiez `dialout`.

**Bouton Connect grisé** → déjà connecté ; cliquez d'abord sur Disconnect.

**La séquence n'entraîne pas tous les doigts** → vérifiez la vitesse de chaque étape et assurez-vous que chaque pose contient les 8 valeurs de servos.

**Indicateur de blocage persistant** → vérifiez un blocage mécanique ; un écart important entre cible et position réelle sans mouvement déclenche un blocage.

**La GUI PWM signale mediapipe manquant au démarrage** → lancez avec le Python de `tools/tracking_env`, ou relancez `tools/setup_tracking.bat`.

## Suivi de main

**Sous-module solutions de mediapipe manquant** → installez `mediapipe==0.10.14` et confirmez que Python 3.12 est en 64 bits.

**Version dora incompatible** → alignez la version de dora selon `pyproject.toml` et les journaux ; nettoyez puis réinstallez.

**Échec de chargement du modèle (chemin chinois)** → placez le projet/les modèles dans un chemin entièrement en anglais.

**Pas d'image caméra / permissions** → autorisez la permission caméra du système ; en machine virtuelle, passez la caméra USB en direct.

**Quelle différence entre la démo officielle SCS0009 et le suivi de la GUI PWM ?** → SCS0009 utilise la chaîne complète dora + IK MuJoCo ; la version PWM fournit un suivi MediaPipe léger intégré à la GUI, le dora Demo n'étant pas inclus dans le module. Détails : [Suivi de main SCS0009](../05-hand-tracking/scs0009.md) / [Suivi de main PWM](../05-hand-tracking/pwm.md).

## Pour aller plus loin

- [Comparaison des versions et choix](../00-product/version-comparison.md)
- [Vue d'ensemble du matériel](../01-hardware/overview.md)
- [Téléchargements et ressources](../00-product/downloads.md)
