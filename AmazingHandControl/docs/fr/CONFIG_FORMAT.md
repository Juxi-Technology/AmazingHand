[English](../en/CONFIG_FORMAT.md) | [Deutsch](../de/CONFIG_FORMAT.md) | [Español](../es/CONFIG_FORMAT.md) | Français | [Italiano](../it/CONFIG_FORMAT.md) | [日本語](../ja/CONFIG_FORMAT.md) | [한국어](../ko/CONFIG_FORMAT.md) | [Português (BR)](../pt-br/CONFIG_FORMAT.md) | [Português (PT)](../pt-pt/CONFIG_FORMAT.md) | [简体中文](../zh-hans/CONFIG_FORMAT.md) | [繁體中文](../zh-hant/CONFIG_FORMAT.md)

# Format de configuration de la main (YAML)

Ce document décrit les fichiers de configuration YAML utilisés par AmazingHand.

| Fichier | Rôle |
|------|---------|
| `data/hand_config.yaml` | Poses et séquences (créés/modifiés par la GUI et la CLI) |
| `data/config.yaml` | Paramètres de l'application (port série, limites de servo, vitesses, chemins) |

---

## `data/config.yaml` – Paramètres de l'application

Chargé au démarrage par la GUI. Si le fichier est absent, les valeurs par défaut intégrées sont utilisées.
La CLI utilise les mêmes valeurs par défaut (surchargeables via `--port` / `--baudrate`).

### Structure complète

```yaml
# Serial port settings
serial:
  port_windows: COM9          # Default port on Windows
  port_linux: /dev/ttyACM0   # Default port on Linux/macOS
  baudrate: 1000000           # Default baud rate
  baudrate_options: [9600, 115200, 1000000]  # Shown in GUI dropdown

# Servo assignments — [servo1_id, servo2_id] per finger
# servo1 (odd ID)  = position axis (open/close)
# servo2 (even ID) = side axis (left/right)
servos:
  ring:    [1, 2]
  middle:  [3, 4]
  pointer: [5, 6]
  thumb:   [7, 8]
  all_ids: [1, 2, 3, 4, 5, 6, 7, 8]

# Servo angle limits (degrees)
limits:
  servo_min: -40   # Absolute minimum for any servo command
  servo_max: 110   # Absolute maximum for any servo command
  base_min: 0      # Open/close slider minimum
  base_max: 110    # Open/close slider maximum
  side_min: -40    # Left/right slider minimum
  side_max: 40     # Left/right slider maximum

# Movement speeds (1–6 scale, where 6 is fastest)
speeds:
  default: 3
  min: 1
  max: 6

# Auto-mode blending extremes — [servo1_deg, servo2_deg]
# Used to interpolate combined position+side values in Auto mode
auto_extremes:
  left_open:    [32, -40]
  right_open:   [-40, 32]
  left_closed:  [110, 110]
  right_closed: [110, 110]
  center_open:  [0, 0]
  center_closed: [110, 110]

# File paths (relative to project root)
paths:
  poses_sequences_file: data/hand_config.yaml
```

### Remarques
- Toutes les clés sont facultatives — les clés absentes reprennent les valeurs par défaut intégrées indiquées ci-dessus.
- Ne stockez **pas** de poses ni de séquences ici ; celles-ci appartiennent à `data/hand_config.yaml`.
- Redémarrez la GUI après avoir modifié ce fichier pour que les changements prennent effet.

---

## `data/hand_config.yaml` – Poses et séquences

Créé et modifié par la GUI et la CLI. Partagé entre les deux outils.

### Structure YAML

```yaml
poses:
  <pose_name>:
    positions: [pos1, pos2, pos3, pos4, pos5, pos6, pos7, pos8]

sequences:
  <sequence_name>:
    steps:
      - "<pose_name>:speed1,speed2,...,speed8|delay"
      - "SLEEP:duration"
```

## Poses

Chaque pose définit une position complète de la main avec 8 valeurs de servo.

### Format
```yaml
poses:
  pose_name:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
```

### Tableau des positions
- **8 valeurs** représentant les positions des servos en degrés
- **Correspondance des servos** :
  - Servo 1 : position du doigt index (0=ouvert, 110=fermé)
  - Servo 2 : latéral du doigt index (-20=gauche, 0=centre, +20=droite)
  - Servo 3 : position du majeur
  - Servo 4 : latéral du majeur
  - Servo 5 : position de l'annulaire
  - Servo 6 : latéral de l'annulaire
  - Servo 7 : position du pouce
  - Servo 8 : latéral du pouce

- **Plage du curseur fermé/ouvert** : 0-110° par doigt (0=ouvert, 110=fermé)
- **Plage du curseur latéral** : -40° (gauche) à +40° (droite)
- **Valeurs de servo stockées** : comme le YAML stocke les valeurs combinées (base ± side), attendez-vous à ce que les commandes réelles des servos se situent à peu près entre -40° et 150°
- **Remarque** : les servos à numéro pair (2,4,6,8) ont des angles inversés au niveau matériel

### Règles de nommage
- Lettres, chiffres et traits de soulignement (underscore) autorisés
- **Caractères interdits** : `: { } [ ] , & * # ? | - < > = ! % @ \` " '`
- 50 caractères maximum
- Sensible à la casse

### Exemple
```yaml
poses:
  open:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
  close:
    positions: [110, 0, 110, 0, 110, 0, 110, 0]
  peace:
    positions: [0, 0, 110, 0, 0, 0, 0, 0]
```

## Séquences

Les séquences définissent des animations multi-étapes avec des vitesses et des délais propres à chaque servo.

### Format
```yaml
sequences:
  sequence_name:
    steps:
      - "pose_name:speed1,speed2,speed3,speed4,speed5,speed6,speed7,speed8|delay"
      - "SLEEP:duration"
```

### Format d'une étape

**Pose avec vitesses individuelles et délai :**
```
"pose_name:s1,s2,s3,s4,s5,s6,s7,s8|delay"
```
- `pose_name` : nom de la pose à exécuter
- `s1-s8` : vitesse individuelle de chaque servo (1-6, où 6 est la plus rapide)
- `delay` : temps d'attente après la fin du mouvement (par ex. `2.0s`)

**Pose avec vitesses par défaut :**
```
"pose_name:3,3,3,3,3,3,3,3|2.0s"
```

**Pause/sleep :**
```
"SLEEP:1.5s"
```
- Met en pause pendant la durée indiquée sans bouger les servos

### Valeurs de vitesse
- Plage : 1 (la plus lente) à 6 (la plus rapide)
- Contrôle la vitesse de déplacement des servos
- Chaque servo peut avoir une vitesse différente dans une étape

### Contrôle de la boucle
- Le réglage de boucle n'est **PAS** stocké dans le YAML
- Contrôlé par une case à cocher dans le lecteur de séquences de la GUI
- Permet une lecture flexible sans modifier le YAML

### Exemple
```yaml
sequences:
  demo:
    steps:
      - "open:3,3,3,3,3,3,3,3|2.0s"
      - "close:3,3,3,3,3,3,3,3|2.0s"
      - "open:3,3,3,3,3,3,3,3|1.0s"
  
  wave:
    steps:
      - "open:5,5,5,5,5,5,5,5|0.5s"
      - "SLEEP:0.3s"
      - "close:5,5,5,5,5,5,5,5|0.5s"
      - "SLEEP:0.3s"
```

## Gestion des poses et des séquences

### Via la GUI (`amazing_hand_gui.py`)

**Poses :**
1. Positionnez les doigts à l'aide des curseurs ou du clavier
2. Saisissez un nom dans le champ "Name:"
3. Cliquez sur "➕ Add New" pour enregistrer

**Séquences :**
1. Cliquez sur le bouton "Manage" dans la section Sequence Player
2. Construisez la séquence dans la boîte de dialogue :
   - Sélectionnez des poses et des vitesses
   - Ajoutez des délais entre les étapes
   - Réorganisez avec les boutons ↑/↓
3. Saisissez le nom de la séquence et cliquez sur "💾 Save"

**Exécution :**
- Sélectionnez la séquence dans la liste déroulante
- Cochez "Loop" si vous souhaitez une lecture continue
- Cliquez sur "▶ Play"

### Via la CLI (`amazing_hand_cmd.py`)

**Lister toutes les poses et séquences :**
```bash
python amazing_hand_cmd.py --list
```

**Exécuter une pose :**
```bash
python amazing_hand_cmd.py --pose open
```

**Exécuter une séquence :**
```bash
python amazing_hand_cmd.py --sequence demo
```

**Exécuter avec boucle :**
```bash
python amazing_hand_cmd.py --sequence wave --loop
```

**Utiliser une configuration alternative :**
```bash
python amazing_hand_cmd.py --pose open --config /path/to/hand_config.yaml
```

## Édition manuelle

Vous pouvez modifier `data/hand_config.yaml` directement :

1. **Respectez la syntaxe YAML** - l'indentation doit être cohérente (2 ou 4 espaces)
2. **Utilisez le format de tableau en ligne** pour les positions :
   ```yaml
   positions: [0, 0, 0, 0, 0, 0, 0, 0]
   ```
3. **Mettez les étapes de séquence entre guillemets** pour préserver les caractères spéciaux :
   ```yaml
   steps:
     - "open:3,3,3,3,3,3,3,3|2.0s"
   ```
4. **Validez les noms** - évitez les caractères interdits
5. **Redémarrez la GUI** pour recharger les changements
6. **Conservez des sauvegardes** avant toute modification importante

## Validation

La GUI et la CLI valident automatiquement :
- Les noms de poses/séquences (caractères interdits)
- La syntaxe YAML à l'enregistrement
- La longueur du tableau de positions (doit être 8)

Les noms invalides sont rejetés avec un message d'erreur indiquant les caractères interdits.

## Licence

Copyright 2026 AmazingHand Control Contributors

Sous licence Apache License, Version 2.0
