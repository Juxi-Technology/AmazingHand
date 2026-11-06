# AmazingHand — Édition servos PWM — Démarrage rapide

Pilotez l'AmazingHand avec un **ESP32-S3 et 8 servos PWM**. Les manuels complets se trouvent dans ce dossier `docs/`.

## Matériel

| Élément | Modèle |
|------|-------|
| Contrôleur | carte de développement ESP32-S3 (YX-ESP32-S3 ou équivalent) |
| Servos | 8 servos PWM — firmware calibré pour des **servos numériques PTK 7452 MG-D (333 Hz)** |
| Adaptateur | carte de dérivation pour servos PWM |
| Alimentation | 5 V / 3 A, masse commune avec l'ESP32 |

> Les servos SG90 et autres servos analogiques 50 Hz ne sont **pas** des remplacements directs du firmware 333 Hz.

| Canal | GPIO | Articulation | Canal | GPIO | Articulation |
|---------|------|-------|---------|------|-------|
| PWM1 | 4 | Index 1 | PWM5 | 15 | Annulaire 1 |
| PWM2 | 5 | Index 2 | PWM6 | 16 | Annulaire 2 |
| PWM3 | 6 | Majeur 1 | PWM7 | 17 | Pouce 1 |
| PWM4 | 7 | Majeur 2 | PWM8 | 18 | Pouce 2 |

## 1. Flasher le firmware

Avec ESP-IDF :

```bash
cd firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

Avec l'image précompilée et `esptool` :

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  firmware/prebuilt/amazinghand_pwm.bin
```

Le port série fonctionne en **115200-8N1** et affiche une bannière de démarrage.

## 2. Commander la main

Interface graphique de bureau :

```bash
pip install -r tools/requirements.txt
python tools/hand_gui.py
```

Le suivi par caméra nécessite l'environnement supplémentaire créé par `tools/setup_tracking.bat`, puis :

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

Contrôle web : ouvrez la page `Amazinghand-web-io/` du dépôt (ou exécutez `Amazinghand-web/server.py --driver pwm`), sélectionnez le pilote **PWM (ESP32-S3)**, choisissez le port série de l'ESP32 et connectez-vous.

## 3. Documentation complète

| Document | Contenu |
|----------|----------|
| [`../en/user_manual.md`](../en/user_manual.md) / [`../zh-hans/用户手册.md`](../zh-hans/用户手册.md) | Protocole, référence des commandes, câblage, calibration, FAQ |
| [`../en/full_workflow.md`](../en/full_workflow.md) / [`../zh-hans/全流程使用教程.md`](../zh-hans/全流程使用教程.md) | Flux de travail complet, de bout en bout |
| [`../en/gui_usage.md`](../en/gui_usage.md) / [`../zh-hans/使用教程.md`](../zh-hans/使用教程.md) | Interface graphique et outil de test série |
| [`../en/hand_tracking.md`](../en/hand_tracking.md) / [`../zh-hans/手势追踪教程.md`](../zh-hans/手势追踪教程.md) | Suivi des mains avec MediaPipe |

## 4. Problèmes courants

- **Aucune réponse** : vérifiez le débit de 115200 bauds, le port COM de l'ESP32, l'alimentation 5 V / 3 A et la masse commune. La page relance automatiquement la poignée de main NOP.
- **Le servo ne bouge pas / tremble** : vérifiez que le servo est un servo numérique 333 Hz et que l'alimentation est suffisante.
- **Direction inversée** : réglez `scale` du doigt correspondant sur `-1` dans `Amazinghand-web-io/config.json`, sous `pwm.calibration`.
- **Position médiane incorrecte** : ajustez `offset_deg` pour ce canal.
- **État « occupé »** : le firmware exécute un geste intégré ; attendez ou envoyez l'arrêt (`0xFF`).
