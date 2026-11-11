---
title: "Suivi de main PWM (MediaPipe intégré à la GUI)"
description: "Suivi de main de la version à servos PWM AmazingHand : MediaPipe intégré à la GUI, installation des dépendances, exécution, principe et limites, questions fréquentes."
version: pwm
---

# Suivi de main PWM (MediaPipe intégré à la GUI)

> Les commandes suivantes s'exécutent dans le répertoire `AmazingHand-PWM/` du dépôt.

Cette page présente le suivi de main de la **version à servos PWM** : MediaPipe est intégré à la GUI, la caméra reconnaît les points de repère de la main et les projette en temps réel sur les 8 voies PWM. La chaîne complète dora + IK MuJoCo relève de la démo officielle SCS0009, voir [Suivi de main SCS0009](scs0009.md).

> Chaîne : caméra → squelette de main MediaPipe → angles de flexion/extension des quatre doigts → ESP32 → servos PWM
>
> Applicable à : ESP32-S3 + 8 voies PWM. Flashage du firmware : [Démarrage rapide PWM](../02-quick-start/pwm.md) ; protocole : [Protocole et calibration PWM](../06-servo-tuning/pwm.md).

> La démo officielle nécessitant l'IK complet (MuJoCo + dora + Rust) n'est pas distribuée avec ce module ; ce tutoriel ne couvre que le suivi intégré à la GUI fourni par le module.

## I. Prérequis

1. **Matériel** : ESP32-S3 + 8 voies PWM alimentés, USB connecté, caméra disponible.
2. **Firmware** : déjà flashé (voir [Démarrage rapide PWM](../02-quick-start/pwm.md)).
3. **Python** : Python 3.12 64 bits (mediapipe 0.10.14 ne fournit qu'un wheel 64 bits).

## II. Installer les dépendances de suivi

Dans le répertoire racine du module (`AmazingHand-PWM/`) :

```bash
tools/setup_tracking.bat
```

Le script effectue automatiquement : recherche d'un Python 64 bits → création de l'environnement virtuel `tools/tracking_env` → installation de `tools/requirements-tracking.txt` (mediapipe 0.10.14, numpy<2, scipy, opencv, Pillow, pyserial) → vérification de mediapipe.

> Installation manuelle possible (avec Python 3.12 64 bits) :
> ```bash
> python -m pip install -r tools/requirements-tracking.txt
> ```

## III. Exécution

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

1. Choisissez le port COM de l'ESP32 en haut → cliquez sur « Connecter ».
2. Faites défiler jusqu'au panneau « Suivi de main (caméra MediaPipe) ».
3. Choisissez l'index de caméra (0 par défaut) → cliquez sur « Démarrer le suivi ».
4. Placez la main dans le champ ; la main suit la flexion/extension ; cliquez sur « Arrêter le suivi » pour terminer.

![Panneau de suivi de main intégré à la GUI : sélection de caméra, démarrage du suivi et messages d'état](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-tracking.png)

## IV. Principe et limites

- MediaPipe 0.10.14 extrait les vecteurs 3D des extrémités des 4 doigts (repère de la main).
- `tips_to_angles()` de `hand_tracking.py` mappe chaque doigt sur un angle différentiel :
  - flex (flexion/extension) : composante z pour trois doigts, composante y pour le pouce ;
  - base (écartement latéral) : fixe à 90 (écartement non implémenté pour l'instant).
- Ce sont des **axes de commande** ; à l'envoi, le programme les combine en angles des deux servos de chaque doigt (même sens = écartement, sens inverse = flexion).
- La GUI applique un lissage EMA intégré (alpha=0.4) + une limitation à 60 ms pour réduire le tremblement.

Limite : pas d'IK, précision inférieure à la chaîne complète MuJoCo + dora ; adapté à la démonstration et au démarrage rapide.

### Calibration des paramètres

- `FLEX_SCALE` / `THUMB_FLEX_GAIN` en bas de `hand_tracking.py` contrôlent l'amplitude et le sens de la flexion (les valeurs actuelles du code font foi).
- L'écartement gauche/droite n'est pas implémenté ; `base` est fixe à 90 ; pour l'écartement, utilisez la démo dora officielle SCS0009.
- Relancez la GUI après modification pour appliquer.

## V. Changer de main

Cochez « Main droite » / « Main gauche » en haut de la GUI. Après bascule, le sens du miroir du pouce diffère ; si vous constatez une inversion, cochez l'autre côté pour tester.

## VI. Questions fréquentes

| Symptôme | Traitement |
|------|------|
| Les servos ne bougent pas du tout | Vérifiez l'alimentation (5V 3A), le port COM, le câblage ; confirmez que le firmware est flashé |
| Pas d'image caméra | Autorisez la permission caméra (Paramètres → Confidentialité → Caméra) |
| La main ne suit pas / réaction lente | Éclairage suffisant, main entièrement dans le cadre, mouvements plus lents et plus amples |
| Forme de main inversée / sens du pouce inversé | Cochez la main gauche/droite opposée |
| Port série introuvable après changement de port USB | Resélectionnez le port COM dans la GUI |
| Erreur mediapipe manquant au démarrage | Lancez avec `tools\tracking_env\Scripts\python`, ou relancez `tools/setup_tracking.bat` |

## VII. IK complet / servos à bus SCS0009

- La chaîne IK complète (caméra → MediaPipe → MuJoCo + IK mink → AHControl → ESP32) provient du projet de démo dora indépendant et ne fait pas partie de ce module ; si nécessaire, utilisez le pack de livraison d'origine ou le projet MediaPipe.
- Les servos à bus SCS0009 sont pris en charge par `Amazinghand-web/` et `AmazingHandControl/` du dépôt.

## Description du répertoire

| Chemin | Contenu |
|------|------|
| `tools/hand_gui.py` | Outil de bureau Tkinter (gestes, pilotage direct, différentiel, suivi intégré) |
| `tools/hand_tracking.py` | Suivi de main MediaPipe et mapping des angles |
| `tools/setup_tracking.bat` | Crée `tools/tracking_env` et installe les dépendances de suivi |
| `tools/requirements-tracking.txt` | Liste des dépendances de suivi |
| `tools/serial_test.py` | Test de port série en ligne de commande |
