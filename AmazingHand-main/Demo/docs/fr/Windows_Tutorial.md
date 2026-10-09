[English](../en/Windows_Tutorial.md) | [Deutsch](../de/Windows_Tutorial.md) | [Español](../es/Windows_Tutorial.md) | Français | [Italiano](../it/Windows_Tutorial.md) | [日本語](../ja/Windows_Tutorial.md) | [한국어](../ko/Windows_Tutorial.md) | [Português (BR)](../pt-br/Windows_Tutorial.md) | [Português (PT)](../pt-pt/Windows_Tutorial.md) | [简体中文](../zh-hans/Windows_Tutorial.md) | [繁體中文](../zh-hant/Windows_Tutorial.md)

# AmazingHand, main dextre · Suivi de main · Tutoriel Windows

Ce tutoriel présente la démo officielle de l'AmazingHand (main dextre de Pollen Robotics) avec des scripts de déploiement en un clic.
Exécutez les scripts dans l'ordre numéroté. **Tous les scripts se trouvent dans `Demo\Windows_Deploy_Scripts\` — double-cliquez pour les exécuter.**

---

## Sommaire

1. [Préparation du matériel](#1-préparation-du-matériel)
2. [Configuration de l'environnement (script 1)](#2-configuration-de-lenvironnement-script-1)
3. [Câblage](#3-câblage)
4. [Configuration du port série (script 2)](#4-configuration-du-port-série-script-2)
5. [Déploiement du code (script 3)](#5-déploiement-du-code-script-3)
6. [Exécuter la démo (script 4)](#6-exécuter-la-démo-script-4)
7. [Nettoyage du projet (script 0)](#7-nettoyage-du-projet-script-0)
8. [Dépannage et remarques](#8-dépannage-et-remarques)
9. [Structure du code](#9-structure-du-code)

---

## 1. Préparation du matériel

| Élément | Exigence |
|---|---|
| Main dextre | Droite / Gauche / Les deux |
| Carte de commande de servos | Externe, USB vers le PC |
| Alimentation | **Au moins 5 V 4 A** (l'USB seul ne suffit pas, utilisez une alimentation externe) |
| Caméra | Intégrée ou webcam USB |

> Les fichiers de modèle (URDF, etc.) peuvent être consultés/téléchargés sur [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e).

---

## 2. Configuration de l'environnement (script 1)

**Double-cliquez sur `1-Install_Env.bat`** — il effectue automatiquement :

1. **La vérification des outils de compilation MSVC** (cl.exe) — nécessaires pour compiler Rust. S'ils manquent, installez
   Visual Studio 2022 Build Tools avec la charge de travail « Développement Desktop en C++ », puis rouvrez le terminal.
2. **L'installation de Rust** (rustup + toolchain stable-msvc)
3. **La configuration du miroir tuna pour cargo** (`C:\Users\<vous>\.cargo\config.toml`) afin d'accélérer le téléchargement des crates
4. **L'installation de uv** (gestionnaire de paquets Python)
5. **L'installation de dora-cli 0.5.0** (`cargo install`, la première compilation prend ~10–20 min, soyez patient)
6. **L'installation du paquet pip dora-rs** (facultatif ; il est également installé dans le venv lors du déploiement)

> **Important** : **fermez puis rouvrez le terminal** après le script pour que les variables d'environnement prennent effet.
> Les téléchargements peuvent être lents selon votre réseau — attendez, n'interrompez pas.

### Installation manuelle (si le script n'est pas utilisable)

- **Rust** : <https://www.rust-lang.org/tools/install> — utilisez rustup-init.exe, toolchain MSVC par défaut.
  - PATH : ajoutez `%USERPROFILE%\.cargo\bin`
- **uv** : PowerShell : `irm https://astral.sh/uv/install.ps1 | iex`
  - PATH : ajoutez `%USERPROFILE%\.local\bin`
- **dora-cli** : `cargo install dora-cli --version 0.5.0`

### Miroir cargo tuna (config.toml)

```
[source.crates-io]
replace-with = "tuna"

[source.tuna]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[registries.tuna]
index = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[http]
check-revoke = false
```

> Utilisez l'**index sparse** (ci-dessus), PAS le miroir de type dépôt git — le miroir git télécharge d'abord ~1 Go d'index et reste souvent bloqué sur `Updating 'tuna' index`.

---

## 3. Câblage

- Reliez la carte de commande de servos au PC en USB, **alimentez-la avec une alimentation externe 5 V 4 A**
- Trouvez le port : **Gestionnaire de périphériques → Ports (COM et LPT)**, par ex. `COM11`

---

## 4. Configuration du port série (script 2)

**Double-cliquez sur `2-Setup_Serial.bat`** (la logique se trouve dans `2-Setup_Serial.ps1`) :

1. « Connectez la carte de commande » → appuyez sur Entrée pour lancer l'analyse
2. Les ports COM détectés sont listés (avec les noms des périphériques)
3. Port unique : appuyez sur Entrée pour confirmer ; plusieurs : tapez l'index
4. Il écrit `--serialport` dans les 3 fichiers yml de dataflow et le port par défaut dans `AHControl\src\main.rs`
5. Les fichiers d'origine sont sauvegardés en `.bak`

> Si vous rebranchez le câble USB, le numéro de COM peut changer — relancez ce script.

---

## 5. Déploiement du code (script 3)

**Double-cliquez sur `3-Deploy_Demo.bat`** — il effectue automatiquement :

1. Le démarrage du démon dora (`dora up`)
2. La création d'un venv Python 3.12 (`uv venv --python 3.12`)
3. L'activation du venv
4. La compilation du nœud Rust AHControl (`cargo build --release`, ~10 min la première fois)
5. La synchronisation des dépendances AHSimulation et HandTracking (`uv sync`)
6. L'installation forcée de mediapipe==0.10.14 (piège connu, solution de repli)

> Déployez une seule fois. Une nouvelle exécution demande si le venv doit être reconstruit.

---

## 6. Exécuter la démo (script 4)

**Double-cliquez sur `4-Run_Demo.bat`** — menu interactif :

```
============================================
  Select a run mode:
============================================
   1 - Simulation (webcam hand tracking)
   2 - Real hardware
   q - Quit
============================================
Enter number [1/2/q]:
```

- **1** : Simulation — les gestes de la webcam pilotent deux mains simulées
- **2** : Matériel réel — sous-menu pour la main droite / gauche / les deux

```
============================================
  Real hardware - select the hand:
============================================
   1 - Right hand
   2 - Left hand
   3 - Both hands
   b - Back to main menu
============================================
```

Il exécute ensuite `dora build` + `dora run`. Une fenêtre de caméra s'ouvre ; faites des gestes de la main pour déplacer la ou les mains en temps réel. **Ctrl+C pour arrêter**. Une fois le dataflow terminé, appuyez sur Entrée pour revenir au menu et choisir un autre mode, ou sur `q` pour quitter.

> Au premier lancement, Windows peut demander la permission d'accès à la caméra — cliquez sur « Autoriser ».

---

## 7. Nettoyage du projet (script 0)

**Double-cliquez sur `0-Cleanup_Project.bat`**, tapez `Y` pour confirmer :

1. Arrête le démon dora
2. Supprime les 3 environnements virtuels (`.venv`)
3. Supprime la sortie de compilation Rust (`Demo\target`)
4. Supprime `__pycache__`, les sauvegardes `.bak`, les logs et `Demo\out` (logs dora)
5. **Restaure le port par défaut** (`--serialport /dev/ttyACM0`), en supprimant les résidus de COM de cette machine

> Après le nettoyage, vous pouvez copier tout le dossier `AmazingHand-main` vers une autre machine — propre et portable.
> Sur la nouvelle machine, exécutez simplement 1 → 2 → 3 → 4 dans l'ordre.

---

## 8. Dépannage et remarques

### 8.1 cargo bloqué sur `Updating 'tuna' index`

- Cause : miroir configuré en **mode dépôt git** (`.../git/crates.io-index.git`), la première exécution télécharge un index de 1 Go et plus
- Correction : réglez `C:\Users\<vous>\.cargo\config.toml` sur l'**index sparse** (voir 2.3), ou relancez `1-Install_Env.bat`

### 8.2 Sous-module solutions de mediapipe manquant / installation cassée

```bat
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- À exécuter dans le venv activé (dans le dossier `Demo`)
- `3-Deploy_Demo.bat` effectue déjà cette opération en solution de repli

### 8.3 Incompatibilité de version de dora (message v0.8.0 vs v0.7.0)

- Symptôme : `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Cause : la version de dora-cli diffère de dora-node-api. **Les deux doivent être en 0.5.0**
  - Vérification : `dora --version` doit afficher `dora-cli 0.5.0` et `dora-message: 0.8.0`
  - Correction : `cargo install dora-cli --version 0.5.0 --force`
  - `1-Install_Env.bat` détecte désormais automatiquement les anciennes versions et installe de force la 0.5.0

### 8.4 Échec du chargement des modèles MuJoCo / mediapipe (chemins chinois)

- Symptôme : `ParseXML: Error opening file '...\scene.xml'` ou `Can't find file: ...\.tflite`
- Cause : les chargeurs C++ de MuJoCo 3.x / mediapipe échouent sur les **chemins absolus contenant des caractères non ASCII (chinois)** (par ex. `D:\Claude工作区\...`)
- Ce projet inclut déjà des correctifs :
  - `AHSimulation\AHSimulation\mj_mink_*.py` change le répertoire de travail avant le chargement
  - `HandTracking\mediapipe_patch.py` utilise les chemins courts 8.3 + des chemins relatifs
- **Ne supprimez pas ces fichiers de correctif**

### 8.5 Permission de la caméra

- Premier lancement : choisissez « Autoriser »
- Paramètres → Confidentialité → Caméra → autoriser les applications de bureau

### 8.6 Le numéro de port change à chaque fois

- Après avoir rebranché l'USB, le numéro de COM peut changer — relancez `2-Setup_Serial.bat`

### 8.7 OpenCV manquant

```bat
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(dans le dossier `HandTracking`, venv activé)

---

## 9. Structure du code

### Dossier Demo

| Chemin | Description |
|---|---|
| `AHControl` | Nœud Rust commandant les servos. Entrée : `src/main.rs` |
| `AHSimulation` | Nœud Python : simulation MuJoCo + cinématique inverse (mink) |
| `HandTracking` | Nœud Python : suivi de main MediaPipe |
| `dataflow_*.yml` | Définitions de dataflow dora (graphe de nœuds) |
| `Windows_Deploy_Scripts` | Ce pack de scripts |

### Fichiers dataflow

| Fichier | Rôle |
|---|---|
| `dataflow_tracking_simu.yml` | Simulation : gestes de la webcam → mains simulées |
| `dataflow_tracking_real_right.yml` | Main droite réelle |
| `dataflow_tracking_real_left.yml` | Main gauche réelle |
| `dataflow_tracking_real_2hands.yml` | Les deux mains réelles (même carte de commande) |

### Principe du dataflow

```
Webcam → HandTracking (MediaPipe hand detection)
              ↓ hand keypoints
         AHSimulation (MuJoCo simulation + IK)
              ↓ joint target angles
         AHControl (serial → servo driver board → hand)
```

### Emplacements de la configuration du port

- La ligne `args:` des 3 fichiers `dataflow_tracking_real_*.yml` : `--serialport COMxx`
- `AHControl\src\main.rs` `default_value = "COMxx"` (valeur par défaut du port série)
- `AHControl\config\*.toml` : modèle de servo, IDs, offsets (aucune modification nécessaire en général)
