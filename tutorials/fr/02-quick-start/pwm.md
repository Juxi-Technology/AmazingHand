---
title: "Démarrage rapide PWM"
description: "Chemin le plus court pour la version à servos PWM d'AmazingHand : câblage, flashage du firmware, GUI de bureau ou contrôle web, premier mouvement."
version: pwm
---

# Démarrage rapide PWM

Pour la version ESP32-S3 + 8 voies de servos PWM. Les explications complètes sont dans les liens de chaque chapitre.

## 1. Câblage

- Branchez les 8 servos PWM sur les servos 1–8 de la carte d'adaptation selon leur numéro.
- Reliez PWM1–8 de la carte d'adaptation aux GPIO 4, 5, 6, 7, 15, 16, 17, 18 de l'ESP32-S3.
- Reliez le 5V/GND de la carte d'adaptation à une alimentation 5V/3A, avec masse commune avec l'ESP32.
- Câblage détaillé : [Câblage, GPIO et alimentation PWM](../01-hardware/pwm.md).

> Les servos doivent être des **servos numériques PTK 7452 MG-D (333 Hz)** ou équivalents ; les servos analogiques 50 Hz comme le SG90 ne sont pas interchangeables.

## 2. Flasher le firmware

### Méthode A : bin précompilé (recommandé)

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  AmazingHand-PWM/firmware/prebuilt/amazinghand_pwm.bin
```

### Méthode B : compilation ESP-IDF

```bash
cd AmazingHand-PWM/firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

Structure du projet firmware :

```text
firmware/AmazingHand_Serial/
├── main/main.c                  Tâches FreeRTOS, file de commandes et initialisation
└── components/
    ├── hand_servo/              Driver PWM LEDC et calibration des servos
    ├── hand_gestures/           Macros de paramètres de gestes et fonctions de gestes
    └── hand_protocol/           Analyse des trames série et distribution des commandes
```

> La compilation ESP-IDF ne prend pas en charge les chemins chinois : le répertoire du projet et le répertoire utilisateur doivent être en anglais ; ESP-IDF v5.x / v6.x recommandé, puce cible **ESP32-S3**.

À la mise sous tension, le port série doit afficher :

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

## 3. Connecter le logiciel hôte

| Mode | Entrée |
|------|------|
| GUI de bureau | [Outil de bureau PWM](../04-desktop/pwm.md) : `python AmazingHand-PWM/tools/hand_gui.py` |
| Contrôle web | [Contrôle web PWM](../03-web-control/pwm.md) : choisissez le driver **PWM (ESP32-S3)**, port série 115200 |
| Test en ligne de commande | `python AmazingHand-PWM/tools/serial_test.py COM3 nop` |

## 4. Premier mouvement

1. Après connexion, le firmware revient d'abord en position médiane (90°) ; vérifiez l'absence de bruit anormal ou de point dur.
2. Vérifiez un à un le sens et la position médiane avec les curseurs doigt par doigt.
3. Essayez ensuite des poses de faible amplitude comme « ouvrir / poing ».
4. Si un sens est inversé ou la position médiane décalée, ajustez selon [Protocole et calibration PWM](../06-servo-tuning/pwm.md).

## Étapes suivantes

- [Protocole et calibration PWM](../06-servo-tuning/pwm.md)
- [Suivi de main PWM](../05-hand-tracking/pwm.md)
- [Comparaison des versions et choix](../00-product/version-comparison.md)
