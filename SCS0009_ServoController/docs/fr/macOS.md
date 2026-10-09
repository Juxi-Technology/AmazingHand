[English](../en/macOS.md) | [Deutsch](../de/macOS.md) | [Español](../es/macOS.md) | Français | [Italiano](../it/macOS.md) | [日本語](../ja/macOS.md) | [한국어](../ko/macOS.md) | [Português (BR)](../pt-br/macOS.md) | [Português (PT)](../pt-pt/macOS.md) | [简体中文](../zh-hans/macOS.md) | [繁體中文](../zh-hant/macOS.md)

# Outil de débogage du servo SCS0009 — Guide pour macOS

Pour macOS 11 (Big Sur) et versions ultérieures. Points clés : nommage des ports série (`cu.*` vs `tty.*`), pilotes USB.

> ⚠️ **Compatibilité : cet outil ne prend en charge pour l'instant que les servos Feetech SCS0009 (série SCS, retour de position par potentiomètre, résolution 10 bits 0-1023)**. La table des registres et le format xdat sont conçus pour le Feetech SCS0009 ; les autres marques/modèles ne sont pas garantis.

---

## 1. Prérequis

| Dépendance | Version |
|-----------|---------|
| Python | >= 3.8 (3.10+ recommandé, via Homebrew) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| OS | macOS 11+ (Apple Silicon / Intel) |

## 2. Installer Python

Recommandé via Homebrew :

```bash
# Install Homebrew if missing
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

Vérifiez :

```bash
python3 --version
```

## 3. Installer les dépendances

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Ne créez l'environnement virtuel qu'UNE seule fois**. Le relancer réinitialiserait/écraserait l'environnement (ce qui effacerait les dépendances installées). Ensuite, faites simplement `source .venv/bin/activate`.

## 4. ⚠️ Nommage des ports série sous macOS [Important]

macOS place les périphériques série USB sous `/dev` avec **deux conventions de nommage** :

| Préfixe | Signification | Utilisable |
|--------|---------|--------|
| `/dev/tty.usbserial-*` | style modem (bloquant) | peut se bloquer, non recommandé |
| `/dev/cu.usbserial-*` | style call/terminal (**non bloquant**) | ✅ recommandé |

**Trouver votre port :**

```bash
ls /dev/cu.*
```

Sortie typique :

```
/dev/cu.usbserial-0001      # CP2102 / FTDI
/dev/cu.usbmodem141101      # onboard USB serial (Arduino/ESP32)
/dev/cu.wchusbserial1420    # CH340
```

> L'outil privilégie automatiquement les périphériques `cu.*`. Si vous spécifiez un port manuellement, utilisez `cu.` et non `tty.`.

## 5. Pilotes USB

Les puces les plus courantes (CH340, CP2102, FTDI) disposent de pilotes macOS intégrés. Si le périphérique n'est pas reconnu :

```bash
system_profiler SPUSBDataType | grep -A5 -i "serial\|CH340\|CP210"
```

- **CH340** : les anciens lots nécessitent le pilote officiel WCH
- En général, si `ls /dev/cu.*` affiche le périphérique, cela suffit

## 6. Vérifier l'environnement

```bash
python setup.py
```

## 7. Lancer l'interface graphique

```bash
python -m src.gui.factory_calibration_tool
```

Spécifier le port :

```bash
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 8. Déroulement de l'interface

> Disposition à panneau unique. Une barre de défilement apparaît automatiquement lorsque la fenêtre est trop courte ; elle s'étire pour s'adapter en mode agrandi.

### 8.1 Connexion série
Sélectionnez le port et le débit (1M par défaut), puis cliquez sur **Connecter**.

### 8.2 Analyser les servos
Cliquez sur **Analyser les servos** (ID 1-254) ; cliquez sur une ligne de la liste pour remplir automatiquement la liste déroulante.

### 8.3 Lecture/écriture des paramètres
- Lit les 44 registres ; la liaison par sélection de ligne remplit adresse/longueur/valeur
- Écriture avec déverrouillage/écriture/verrouillage automatiques ; popup de succès/échec affichée

### 8.4 Contrôle de position
Faites glisser le curseur (0-1023) ou saisissez une valeur ; invite de fin de mouvement pour couper le couple.

### 8.5 Débit / Réinitialisation d'usine
Modifier le débit (retour arrière automatique en cas d'échec), réinitialisation d'usine.

### 8.6 Paramètres xdat (EEPROM uniquement)
Enregistrer le servo actuel → ouvrir une sauvegarde → restaurer sur le servo.

## 9. Dépannage

| Problème | Solution |
|---------|----------|
| Un port en `tty.` se bloque | Utilisez le préfixe `cu.` à la place |
| Périphérique introuvable | `ls /dev/cu.*` ; rebranchez ; `system_profiler SPUSBDataType` |
| Interface chinoise vide | La police système PingFang convient généralement ; installez Noto Sans CJK si l'affichage est cassé |
| Problème de permission | macOS ne nécessite en général aucune permission supplémentaire ; autorisez l'accès au terminal si demandé |
| L'activation du venv échoue | `source .venv/bin/activate` (pas `.bat`) |
| Erreur de compilation Apple Silicon | Python 3.10+ est natif ; évitez l'ancien Python sous Rosetta |

## 10. Ligne de commande (facultatif)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 11. Conseils

- **Le nom du port change** : les noms `cu.*` peuvent varier selon le port USB ; sélectionnez dans la liste déroulante à chaque lancement
- **Veille** : macOS peut se mettre en veille et couper la liaison série ; maintenez la machine éveillée pendant l'utilisation
- **Autorisation de confidentialité** : si l'accès aux « disques amovibles » est demandé, autorisez-le
