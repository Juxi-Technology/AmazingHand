---
title: "Outil de bureau PWM (GUI Tkinter)"
description: "Contrôle de bureau de la version à servos PWM AmazingHand : exécution depuis les sources, gestes/différentiel/pilotage direct dans la GUI, suivi MediaPipe intégré, tests en ligne de commande et packaging."
version: pwm
---

# Outil de bureau PWM (GUI Tkinter)

> Les commandes suivantes s'exécutent dans le répertoire `AmazingHand-PWM/` du dépôt.

Cette page est le tutoriel de contrôle de bureau de la **version à servos PWM**. Pour le contrôle web, voir [Contrôle web PWM](../03-web-control/pwm.md) ; pour le câblage, voir [Câblage PWM](../01-hardware/pwm.md) ; pour le flashage du firmware, voir [Démarrage rapide PWM](../02-quick-start/pwm.md).

> Applicable à : ESP32-S3 + 8 voies PWM (entraînement différentiel). Flashage du firmware : [Démarrage rapide PWM](../02-quick-start/pwm.md) ; protocole et commandes : [Protocole et calibration PWM](../06-servo-tuning/pwm.md).

## I. Modes d'exécution

| Mode | Nécessite | Adapté à |
|------|------|------|
| **Exécution depuis les sources** (recommandé) | Python 3.12 64 bits + pyserial | Toutes les fonctionnalités, suivi de main compris |
| Packaging exe personnel | PyInstaller | Distribution sans installation de Python (voir section VII) |

## II. Exécution depuis les sources

### Installer les dépendances

Dans le répertoire racine du module (`AmazingHand-PWM/`) :

```bash
# dépendances de base (pyserial)
pip install -r tools/requirements.txt

# à exécuter seulement si vous voulez le suivi de main (crée automatiquement tools/tracking_env et installe mediapipe)
tools/setup_tracking.bat
```

> mediapipe 0.10.14 ne fournit qu'un wheel Windows 64 bits ; utilisez obligatoirement **Python 3.12 64 bits**.

### Lancer la GUI

```bash
# n'importe quel Python avec pyserial
python tools/hand_gui.py

# ou avec l'environnement de suivi (inclut mediapipe)
tools/tracking_env/Scripts/python tools/hand_gui.py
```

![Interface principale : barre de port série, commandes de gestes, pilotage direct des servos et contrôle différentiel des doigts](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-main.png)

### Utilisation de la GUI

1. **Choisir le port série** : dans la liste en haut, choisissez le port COM de l'ESP32 (visible dans le gestionnaire de périphériques).
2. **Cliquer sur « Connecter »** : le voyant d'état passe au vert, le journal affiche « connecté » et un test de liaison NOP est envoyé automatiquement.
3. **Commandes de gestes** : cliquez sur « Pierre / Ciseaux / Feuille / Pouce levé / OK / Pincement / Pointage / Ouvrir / Poing », la main exécute le geste.
4. **Main gauche/droite** : cochez « Main droite » / « Main gauche » pour basculer (le sens du miroir du pouce diffère).
5. **Pilotage direct des servos** : faites glisser les 8 curseurs pour contrôler en temps réel l'angle d'un servo (0–180°).
6. **Contrôle différentiel des doigts** : deux barres de progression par doigt —
   - **Flexion ◀▶ Extension** : fléchir ou étendre le doigt (plage -70 ~ +70).
   - **Balayage droite ◀▶ gauche** : balayage latéral du doigt (plage 60 ~ 120, 90 = neutre).

   > Ces deux barres sont des **axes de commande**, pas deux servos. Le programme les combine en angles des deux servos du doigt : la composante de même sens produit l'écartement, la composante de sens inverse la flexion.

7. **Répéter / Arrêter** : rejoue le dernier geste / interrompt immédiatement.
8. **Journal de communication** : affiche en temps réel les trames émises/reçues et les réponses en bas.

![Panneau de contrôle différentiel des doigts : flexion/extension et balayage latéral de chaque doigt](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-differential.png)

### Suivi de main intégré à la GUI

La GUI intègre un panneau de suivi de main (la caméra suit les mouvements de la main) :

1. Après connexion du port série, faites défiler jusqu'au panneau « Suivi de main (caméra MediaPipe) ».
2. Choisissez l'index de caméra (0 par défaut) et cliquez sur **« Démarrer le suivi »**.
3. Placez la main dans le champ de la caméra ; la main suit la flexion/extension.

> Le suivi nécessite que `tools/setup_tracking.bat` ait installé mediapipe ; seule une GUI lancée depuis les sources dispose du suivi.

## III. Tests en ligne de commande (tools/serial_test.py)

Dans le répertoire racine du module :

```bash
# test de liaison (vérifie d'abord que la communication passe)
python tools/serial_test.py COM3 nop

# gestes
python tools/serial_test.py COM3 rock         # Pierre
python tools/serial_test.py COM3 thumbs_up    # Pouce levé
python tools/serial_test.py COM3 index        # Pointage
python tools/serial_test.py COM3 open         # Ouvrir
python tools/serial_test.py COM3 close        # Poing

# pilotage direct d'un servo
python tools/serial_test.py COM3 servo 1 90   # servo 1 → 90°

# tout recentrer
python tools/serial_test.py COM3 mid

# définir main gauche/droite
python tools/serial_test.py COM3 hand L
python tools/serial_test.py COM3 hand R

# balayage / autotest
python tools/serial_test.py COM3 sweep 1      # balayage du servo 1
python tools/serial_test.py COM3 test         # test de tous les servos un par un
```

## IV. Test manuel avec un outil de port série (facultatif)

Sans logiciel hôte, vous pouvez aussi valider la liaison en envoyant directement des trames hexadécimales avec un outil de port série.

**CoolTerm** (Windows / macOS / Linux) :

1. `Options` → débit **115200**, 8N1.
2. `Connection` → `Send String` → choisissez `Hex`.
3. Envoyez `AA 01 00 01` (Pierre) ; la zone de réponse doit afficher `BB 01 00 01` (ACK) et `BB 01 10 11` (terminé).

**Ligne de commande Linux / macOS** :

```bash
# Linux
stty -F /dev/ttyUSB0 115200
printf '\xAA\x01\x00\x01' > /dev/ttyUSB0

# macOS
stty -f /dev/cu.usbserial-0001 115200
printf '\xAA\x01\x00\x01' > /dev/cu.usbserial-0001
```

Format des trames, somme de contrôle et toutes les commandes : [Protocole et calibration PWM](../06-servo-tuning/pwm.md).

## V. Script de contrôle Python (développement personnalisé)

```python
import time
import serial

PORT, BAUD = "COM3", 115200          # sous Linux/macOS, remplacer par /dev/ttyUSB0, /dev/cu.usbserial-*

def frame(cmd, data=b""):
    checksum = cmd ^ len(data)
    for byte in data:
        checksum ^= byte
    return bytes([0xAA, cmd, len(data)]) + data + bytes([checksum & 0xFF])

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(1)                        # attendre la fin de la réinitialisation de l'ESP32

ser.write(frame(0x00))               # test de liaison NOP
ser.write(frame(0x01))               # Pierre
time.sleep(0.5)
ser.write(frame(0xF0, bytes([90] * 8)))  # les 8 servos à 90°
ser.close()
```

La trame de réponse est `BB CMD STATUS CKSUM` ; `STATUS=0x00` signifie accepté, `0x10` signifie geste terminé. Le tableau complet des commandes et les exemples de pilotage direct/main gauche-droite sont dans [Protocole et calibration PWM](../06-servo-tuning/pwm.md).

## VI. Questions fréquentes

| Symptôme | Traitement |
|------|------|
| Les servos ne bougent pas | Vérifiez l'alimentation (alimentation indépendante 5V 3A), le port COM, le câblage |
| Aucune réponse / les servos s'agitent après ouverture du port | Vérifiez le débit 115200 ; la GUI envoie d'abord un handshake NOP à la connexion |
| Pas d'image caméra | Autorisez la permission caméra (Paramètres → Confidentialité → Caméra) |
| Forme de main inversée | Cochez la main gauche/droite opposée |
| Le suivi ne réagit pas | Vérifiez que vous lancez avec le Python de `tools\tracking_env` et que mediapipe est bien installé |

## VII. Packaging exe personnel (facultatif)

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole --name "AmazingHand控制台" tools/hand_gui.py
```

La version packagée n'inclut pas le suivi de main (ressources mediapipe volumineuses) ; pour le suivi, utilisez l'exécution depuis les sources.

> Protocole et commandes complets : [Protocole et calibration PWM](../06-servo-tuning/pwm.md).
