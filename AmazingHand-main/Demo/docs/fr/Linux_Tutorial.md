[English](../en/Linux_Tutorial.md) | [Deutsch](../de/Linux_Tutorial.md) | [Español](../es/Linux_Tutorial.md) | Français | [Italiano](../it/Linux_Tutorial.md) | [日本語](../ja/Linux_Tutorial.md) | [한국어](../ko/Linux_Tutorial.md) | [Português (BR)](../pt-br/Linux_Tutorial.md) | [Português (PT)](../pt-pt/Linux_Tutorial.md) | [简体中文](../zh-hans/Linux_Tutorial.md) | [繁體中文](../zh-hant/Linux_Tutorial.md)

# AmazingHand, main dextre · Suivi de main · Tutoriel Linux (Ubuntu)

Ce tutoriel présente la démo officielle de l'AmazingHand (main dextre de Pollen Robotics) avec des scripts de déploiement en un clic.
Exécutez les scripts dans l'ordre numéroté. **Tous les scripts se trouvent dans `Demo/Linux_Deploy_Scripts/` — exécutez `./script` depuis un terminal.**

---

## Sommaire

1. [Préparation du matériel](#1-préparation-du-matériel)
2. [Accorder les permissions des scripts (important)](#2-accorder-les-permissions-des-scripts-important)
3. [Configuration de l'environnement (script 1)](#3-configuration-de-lenvironnement-script-1)
4. [Câblage](#4-câblage)
5. [Configuration du port série (script 2)](#5-configuration-du-port-série-script-2)
6. [Déploiement du code (script 3)](#6-déploiement-du-code-script-3)
7. [Exécuter la démo (script 4)](#7-exécuter-la-démo-script-4)
8. [Nettoyage du projet (script 0)](#8-nettoyage-du-projet-script-0)
9. [Dépannage et remarques](#9-dépannage-et-remarques)
10. [Structure du code](#10-structure-du-code)

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

## 2. Accorder les permissions des scripts (important)

**Lorsque des scripts sont copiés depuis Windows ou depuis un zip vers Linux, la permission d'exécution (`+x`) est perdue** — les exécuter directement renvoie
`Permission denied`. **Exécutez ceci une fois avant la première utilisation :**

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
chmod +x *.sh
```

Ensuite, chaque script peut être exécuté avec `./script`. Ou combinez le tout :

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts" && chmod +x *.sh && ./1-Install_Env.sh
```

> Astuce : pour déplacer le dossier `AmazingHand-main` vers Linux en conservant les permissions, créez une archive avec **tar** :
> `tar czf AmazingHand-main.tar.gz AmazingHand-main`, ou exécutez simplement `chmod +x *.sh` une fois après l'extraction.

---

## 3. Configuration de l'environnement (script 1)

Depuis le dossier des scripts, exécutez (après le `chmod +x` de l'étape 2) :

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
./1-Install_Env.sh
```

Il effectue automatiquement :

1. **L'installation de Rust** (rustup + toolchain stable)
2. **La configuration du miroir tuna pour cargo** (`~/.cargo/config.toml`) afin d'accélérer le téléchargement des crates
3. **L'installation de uv** (gestionnaire de paquets Python)
4. **L'installation de dora-cli 0.5.0** (`cargo install`, la première compilation prend ~10–20 min, soyez patient). Les anciennes versions de dora sont détectées automatiquement et remplacées de force.
5. **L'installation du paquet pip dora-rs** (facultatif)

> **Important** : **fermez puis rouvrez le terminal** après le script pour que les variables d'environnement prennent effet.
> Si une version apparaît vide, ajoutez à `~/.bashrc` :
>
> ```bash
> export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
> ```

### Installation manuelle (si le script n'est pas utilisable)

- **Rust** :
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```
- **uv** :
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **dora-cli** :
  ```bash
  cargo install dora-cli --version 0.5.0
  ```

### Miroir cargo tuna (~/.cargo/config.toml)

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

## 4. Câblage

- Reliez la carte de commande de servos au PC en USB, **alimentez-la avec une alimentation externe 5 V 4 A**
- Trouvez le port :
  ```bash
  ls /dev/ttyUSB* /dev/ttyACM*
  ```
  Généralement `/dev/ttyACM0`

---

## 5. Configuration du port série (script 2)

**Exécutez `./2-Setup_Serial.sh`** :

1. « Connectez la carte de commande » → appuyez sur Entrée pour lancer l'analyse
2. Les ports série détectés sont listés (`/dev/ttyACM*` / `/dev/ttyUSB*`)
3. Port unique : appuyez sur Entrée pour confirmer ; plusieurs : tapez l'index
4. Il écrit `--serialport` dans les 3 fichiers yml de dataflow et le port par défaut dans `AHControl/src/main.rs`
5. **Configure automatiquement les permissions du port série** :
   ```bash
   sudo chmod 666 /dev/ttyACM0
   ```
   Recommandé : ajoutez l'utilisateur courant au groupe dialout (évite de ressaisir le mot de passe ; déconnectez-vous/reconnectez-vous pour appliquer) :
   ```bash
   sudo usermod -aG dialout $USER
   ```

> Si `ls /dev/ttyUSB* /dev/ttyACM*` ne trouve rien dans une VM, connectez le périphérique USB à la VM dans les paramètres de la VM.

---

## 6. Déploiement du code (script 3)

**Exécutez `./3-Deploy_Demo.sh`** — il effectue automatiquement :

1. Le démarrage du démon dora (`dora up`)
2. La création d'un venv Python 3.12 (`uv venv --python 3.12`)
3. L'activation du venv
4. La compilation du nœud Rust AHControl (`cargo build --release`, ~10 min la première fois)
5. La synchronisation des dépendances AHSimulation et HandTracking (`uv sync`)
6. L'installation forcée de mediapipe==0.10.14 (piège connu, solution de repli)

> Déployez une seule fois. Une nouvelle exécution demande si le venv doit être reconstruit.

---

## 7. Exécuter la démo (script 4)

**Exécutez `./4-Run_Demo.sh`** — menu interactif :

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

> Le bureau Linux a besoin de la permission d'accès à la caméra (Ubuntu : Paramètres → Confidentialité → Caméra). Assurez-vous que la caméra n'est pas utilisée par une autre application. Problèmes de caméra en VM : voir [9.6](#96-permission-de-la-caméra--caméra-de-machine-virtuelle-non-fonctionnelle).

---

## 8. Nettoyage du projet (script 0)

**Exécutez `./0-Cleanup_Project.sh`**, tapez `Y` pour confirmer :

1. Arrête le démon dora
2. Supprime les 3 environnements virtuels (`.venv`)
3. Supprime la sortie de compilation Rust (`Demo/target`)
4. Supprime `__pycache__`, les sauvegardes `.bak`, les logs et `Demo/out` (logs dora)
5. **Restaure le port par défaut** (`--serialport /dev/ttyACM0`), en supprimant les résidus de port de cette machine

> Après le nettoyage, vous pouvez copier tout le dossier `AmazingHand-main` vers une autre machine — propre et portable.
> Sur la nouvelle machine, exécutez simplement 1 → 2 → 3 → 4 dans l'ordre.

---

## 9. Dépannage et remarques

### 9.1 `Permission denied` (le script n'a pas la permission d'exécution)

- Symptôme : `bash: ./1-Install_Env.sh: Permission denied`
- Cause : le script a perdu son bit d'exécution lors de la copie depuis Windows / un zip
- Correction :
  ```bash
  chmod +x *.sh
  ```
  Puis exécutez avec `./script` (et non `bash script`).

### 9.2 cargo bloqué sur `Updating 'tuna' index`

- Cause : miroir configuré en **mode dépôt git** (`.../git/crates.io-index.git`), la première exécution télécharge un index de 1 Go et plus
- Correction : réglez `~/.cargo/config.toml` sur l'**index sparse** (voir 3.2), ou relancez `1-Install_Env.sh`

### 9.3 Sous-module solutions de mediapipe manquant / installation cassée

```bash
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- À exécuter dans le venv activé (dans le dossier `Demo`)
- `3-Deploy_Demo.sh` effectue déjà cette opération en solution de repli

### 9.4 Incompatibilité de version de dora (message v0.8.0 vs v0.7.0)

- Symptôme : `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Cause : la version de dora-cli diffère de dora-node-api. **Les deux doivent être en 0.5.0**
  - Vérification : `dora --version` doit afficher `dora-cli 0.5.0` et `dora-message: 0.8.0`
  - `1-Install_Env.sh` détecte désormais automatiquement les anciennes versions et installe de force la 0.5.0

**Si une ancienne version de dora (par ex. 0.4.1) subsiste sur le système, nettoyez-la d'abord :**

```bash
# 1. Find where the old dora is
which dora
ls -la ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora 2>/dev/null

# 2. Delete the found old versions (adjust paths; there may be several)
rm -f ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora

# 3. Force-install 0.5.0 (goes to ~/.cargo/bin)
cargo install dora-cli --version 0.5.0 --force

# 4. Verify (should print dora-cli 0.5.0 / dora-message: 0.8.0)
dora --version
```

> Si `dora --version` affiche encore une ancienne version, une autre copie se cache quelque part dans le PATH — utilisez `which dora` pour la trouver et la supprimer, et assurez-vous que `~/.cargo/bin` figure au début du PATH.

### 9.5 Permission refusée sur le port série

```bash
sudo chmod 666 /dev/ttyACM*
```

- Rebrancher le câble peut réinitialiser les permissions
- Correction permanente : `sudo usermod -aG dialout $USER`, déconnexion/reconnexion

### 9.6 Permission de la caméra / Caméra de machine virtuelle non fonctionnelle

**Machine réelle** :
- Ubuntu : Paramètres → Confidentialité → Caméra → autoriser les applications
- Assurez-vous qu'aucune autre application (application Caméra, Zoom, etc.) n'utilise la webcam

**Caméra non fonctionnelle dans une machine virtuelle (VMware)** :

Symptômes : `open VIDEOIO(V4L2:/dev/video0): can't open camera by index` ou `select() timeout` ;
`/dev/video0` existe et `v4l2-ctl` capture des images, mais OpenCV `cap.read()` renvoie toujours `ret = False`.

Diagnostic et correction (dans l'ordre) :

1. **Transférez la caméra vers la VM** : Menu → VM → Removable Devices → Camera → Connect
2. **Changez la version du contrôleur USB (correctif VMware le plus efficace)** :
   - VM → Settings → **USB Controller** → basculez entre `USB 2.0` / `USB 3.1`
   - **Redémarrez la VM** après le changement
3. Vérifiez que le périphérique existe :
   ```bash
   ls -l /dev/video0
   sudo usermod -aG video $USER   # add to video group, log out/in
   ```
4. Vérifiez que la caméra peut réellement produire des images avec v4l2 (si oui, le pilote est correct et le problème vient de la compatibilité OpenCV) :
   ```bash
   v4l2-ctl --device=/dev/video0 --set-fmt-video=width=640,height=480,pixelformat=MJPG --stream-mmap --stream-count=1 --stream-to=/tmp/frame.jpg
   ls -l /tmp/frame.jpg   # tens to hundreds of KB = stream works
   ```

### 9.7 Le numéro de port change à chaque fois

- Après avoir rebranché l'USB, le nom du périphérique peut changer — relancez `2-Setup_Serial.sh`

### 9.8 OpenCV manquant

```bash
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(dans le dossier `HandTracking`, venv activé)

---

## 10. Structure du code

### Dossier Demo

| Chemin | Description |
|---|---|
| `AHControl` | Nœud Rust commandant les servos. Entrée : `src/main.rs` |
| `AHSimulation` | Nœud Python : simulation MuJoCo + cinématique inverse (mink) |
| `HandTracking` | Nœud Python : suivi de main MediaPipe |
| `dataflow_*.yml` | Définitions de dataflow dora (graphe de nœuds) |
| `Linux_Deploy_Scripts` | Ce pack de scripts |

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

- La ligne `args:` des 3 fichiers `dataflow_tracking_real_*.yml` : `--serialport /dev/ttyACMx`
- `AHControl/src/main.rs` `default_value = "/dev/ttyACM0"` (valeur par défaut du port série)
- `AHControl/config/*.toml` : modèle de servo, IDs, offsets (aucune modification nécessaire en général)
