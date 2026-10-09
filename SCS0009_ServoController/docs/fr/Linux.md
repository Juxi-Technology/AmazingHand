[English](../en/Linux.md) | [Deutsch](../de/Linux.md) | [Español](../es/Linux.md) | Français | [Italiano](../it/Linux.md) | [日本語](../ja/Linux.md) | [한국어](../ko/Linux.md) | [Português (BR)](../pt-br/Linux.md) | [Português (PT)](../pt-pt/Linux.md) | [简体中文](../zh-hans/Linux.md) | [繁體中文](../zh-hant/Linux.md)

# Outil de débogage du servo SCS0009 — Guide pour Linux

Pour Ubuntu / Debian / autres distributions courantes. Points clés : permissions du port série (dialout), détection des adaptateurs USB-série.

> ⚠️ **Compatibilité : cet outil ne prend en charge pour l'instant que les servos Feetech SCS0009 (série SCS, retour de position par potentiomètre, résolution 10 bits 0-1023)**. La table des registres et le format xdat sont conçus pour le Feetech SCS0009 ; les autres marques/modèles ne sont pas garantis.

---

## 1. Prérequis

| Dépendance | Version |
|-----------|---------|
| Python | >= 3.8 (3.10+ recommandé) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| OS | Ubuntu 20.04+ / Debian 11+ |

Polices chinoises (requises pour l'interface en chinois) :

```bash
sudo apt install fonts-noto-cjk
```

Polices d'icônes emoji (pour ✅⚠️ etc. dans les logs) :

```bash
sudo apt install fonts-noto-color-emoji
```

## 2. Installer les dépendances Python

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Ne créez l'environnement virtuel qu'UNE seule fois**. Le relancer réinitialiserait/écraserait l'environnement (ce qui effacerait les dépendances installées). Ensuite, faites simplement `source .venv/bin/activate`.

> Si pip signale « externally-managed-environment », utilisez un venv ou `pip install --break-system-packages -r requirements.txt`.

## 3. ⚠️ Permission du port série (dialout) [Obligatoire]

Par défaut, un utilisateur normal **ne peut pas accéder** à `/dev/ttyUSB*` / `/dev/ttyACM*`. Ajoutez votre utilisateur au groupe `dialout` :

```bash
sudo usermod -a -G dialout $USER
```

**Déconnectez-vous puis reconnectez-vous** (ou redémarrez). Vérifiez :

```bash
groups
# output should include dialout
```

> Certaines distributions utilisent `uucp` (Arch) ou `tty`.

## 4. Identifier le périphérique série USB

Après le branchement :

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Sortie typique :

```
/dev/ttyUSB0   # CH340 / CP2102 / PL2303
/dev/ttyACM0   # native USB serial (Arduino/ESP32 onboard)
```

## 5. Vérifier l'environnement

```bash
python setup.py
```

## 6. Lancer l'interface graphique

```bash
python -m src.gui.factory_calibration_tool
```

Spécifier le port :

```bash
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

> S'il n'existe qu'un seul port, l'outil l'utilise directement.

## 7. Déroulement de l'interface

> Disposition à panneau unique. Une barre de défilement apparaît automatiquement lorsque la fenêtre est trop courte ; elle s'étire pour s'adapter en mode agrandi.

### 7.1 Connexion série
Sélectionnez le port et le débit (1M par défaut), puis cliquez sur **Connecter**.

### 7.2 Analyser les servos
Cliquez sur **Analyser les servos** (ID 1-254) ; cliquez sur une ligne de la liste pour remplir automatiquement la liste déroulante.

### 7.3 Lecture/écriture des paramètres
- Lit les 44 registres (EEPROM + SRAM) ; la liaison par sélection de ligne remplit adresse/longueur/valeur
- Écriture avec déverrouillage/écriture/verrouillage automatiques ; popup de succès/échec affichée

### 7.4 Contrôle de position
Faites glisser le curseur (0-1023) ou saisissez une valeur ; invite de fin de mouvement pour couper le couple.

### 7.5 Débit / Réinitialisation d'usine
Modifier le débit (retour arrière automatique en cas d'échec), réinitialisation d'usine.

### 7.6 Paramètres xdat (EEPROM uniquement)
Enregistrer le servo actuel → ouvrir une sauvegarde → restaurer sur le servo.

## 8. Dépannage

| Problème | Solution |
|---------|----------|
| **Permission denied: /dev/ttyUSB0** | Vous n'êtes pas dans le groupe dialout, voir section 3 ; ou `sudo chmod 666 /dev/ttyUSB0` (temporaire) |
| Aucun port série | `ls /dev/ttyUSB* /dev/ttyACM*` ; `lsusb` pour confirmer le périphérique |
| Le nom du périphérique change | La numérotation ttyUSB dépend de l'ordre de branchement ; utilisez une règle udev ou sélectionnez le port à chaque lancement |
| Interface chinoise vide | Installez `fonts-noto-cjk` |
| Les emojis s'affichent en carrés | Installez `fonts-noto-color-emoji` |
| Échec de pip install | Utilisez un venv ; ou `--break-system-packages` |
| L'application ne démarre pas | Vérifiez `python3 --version` ; `pip list` pour les dépendances |

## 9. Ligne de commande (facultatif)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

## 10. Avancé : nom de périphérique fixe via udev (facultatif)

Créez `/etc/udev/rules.d/99-servo.rules` pour fixer le nom du périphérique par ID USB :

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyServo"
```

Puis `ls -l /dev/ttyServo`. Obtenez l'ID du fabricant avec `lsusb`.
