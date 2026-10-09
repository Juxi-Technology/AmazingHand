[English](../en/user_manual.md) | [Deutsch](../de/user_manual.md) | [Español](../es/user_manual.md) | Français | [Italiano](../it/user_manual.md) | [日本語](../ja/user_manual.md) | [한국어](../ko/user_manual.md) | [Português (BR)](../pt-br/user_manual.md) | [Português (PT)](../pt-pt/user_manual.md) | [简体中文](../zh-hans/user_manual.md) | [繁體中文](../zh-hant/user_manual.md)

# AmazingHand Controller – Manuel d'utilisation

> **Version :** 2026-03-22  
> **S'applique à :** `amazing_hand_gui.py` (GUI), `amazing_hand_cmd.py` (CLI)

---

## 1. Introduction

L'interface graphique AmazingHand Controller assure le suivi en temps réel et le contrôle manuel d'une main robotisée à huit servos, actionnée par des servomoteurs Feetech SCS0009. L'interface est divisée en panneaux dédiés au contrôle des doigts, à la gestion globale, à la visualisation de la télémétrie et à l'enregistrement de l'activité. Ce guide vous accompagne dans l'installation, la navigation et les flux de travail courants.

> **Astuce :** gardez ce manuel ouvert pendant l'utilisation de la GUI. Les infobulles intégrées à l'application reprennent les mêmes descriptions lorsque vous survolez les commandes.

![AmazingHand hardware with controller connected](../en/screenshots/hand_overview.png)

---

## 2. Liste de démarrage rapide

1. **Installez les dépendances** (une seule fois par environnement) :
   ```bash
   python -m pip install -r requirements.txt
   ```
2. **Alimentez le matériel :** connectez l'alimentation 5 V à la chaîne de servos et branchez l'adaptateur série USB.
3. **Lancez la GUI :**
   ```bash
   python amazing_hand_gui.py
   ```
4. **Connectez-vous au contrôleur :** choisissez le **Port** série (par ex. `COM9`) et cliquez sur **▶ Connecter**.
5. **Vérifiez la télémétrie :** recherchez les mises à jour en direct dans le graphique et le tableau de retour.

---

## 3. Aperçu de l'écran

```
+--------------------------------------------------------------------------------+
|                              AmazingHand Controller                            |
+---------------------------+-----------------------------------------------+----+
| Finger Controls           | Chart Controls & Telemetry Plot                    |
| (Ring – Middle – Pointer) | (Display menu, chart canvas)                       |
+---------------------------+-----------------------------------------------+----+
| Control Stack             | Thumb finger   | Feedback Table (Servo Metrics)    |
| (Connection, Global, Pose,| control        | (Goal, Position, Load, etc.)      |
|  Sequence)                |                |                                   |
+---------------------------+                                                    |
| Execution Log & Status    |                                                    |
+--------------------------------------------------------------------------------+
```

![Main window overview highlighting the major panels](../en/screenshots/mainscreen.png)

### 3.1 Les panneaux en un coup d'œil

| Panneau | Emplacement | Rôle |
|-------|----------|---------|
| **Contrôles des doigts** | À gauche, en haut (3 doigts) + en bas à droite (pouce) | Curseurs individuels et sélecteurs de vitesse pour chaque paire de doigts. Comprend les indicateurs de mimic et les LED d'état par doigt. |
| **Pile de contrôle droite** | À gauche, en bas à droite | Réglages de connexion, contrôles globaux, gestion des poses et lecteur de séquences. |
| **Panneau de télémétrie** | À droite | Graphiques en temps réel avec curseurs de zoom/panoramique et tableau de retour configurable. |
| **Journal d'exécution** | En bas | Flux de messages d'état, d'avertissements et de progression des séquences. |

---

## 4. Guide détaillé des panneaux

### 4.1 Panneau de contrôle des doigts (colonne de gauche)

Chaque widget de doigt contrôle une paire de servos (position + décalage latéral) :

- **Bascule de mode :** permet de passer entre **Auto** (curseurs base + décalage) et **Raw** (cibles de servo directes).
- **LED d'état :** gris (inactif), vert (en mouvement), rouge (blocage potentiel, selon la charge par rapport à la cible).
- **Curseur de position :** 0–110° (de l'ouverture à la fermeture). La molette de la souris ajuste par pas de 1° ; le glissement est réactif.
- **Curseur latéral :** ±40° pour les ajustements latéraux. Le curseur latéral du pouce est **inversé** afin que la direction physique corresponde à l'orientation anatomique de la main — faire glisser vers la droite déplace le pouce dans le sens positif par rapport à son montage matériel.
- **Sélecteur de vitesse :** liste déroulante 1–6 contrôlant la vitesse de déplacement des deux servos de la paire de doigts.
- **Case à cocher Mimic :** reproduit les mouvements de fermeture/ouverture d'un doigt source pour un mouvement coordonné en mode Auto.

**Modes des doigts : Auto vs Raw**

- **Le mode Auto** (par défaut) expose le curseur fermeture/ouverture, le curseur de décalage latéral, la liste déroulante de vitesse et le bouton de centrage. La GUI combine ces deux valeurs de curseur en commandes de servo à l'aide des extrêmes calibrés stockés dans `data/hand_config.yaml`, de sorte que la paire suive des poses de doigt naturelles sans calculs de servo manuels. Mimic reste actif ici — activez-le sur plusieurs doigts pour les entraîner en synchronisation avec le doigt que vous êtes en train d'ajuster.
- **Le mode Raw** remplace les contrôles Auto par deux curseurs verticaux étiquetés par servo. Déplacez-les pour commander directement les angles des servos sous-jacents lors du test des fins de course, de la validation de la calibration ou du diagnostic de problèmes de liaison. Le bouton de centrage et la case à cocher mimic sont désactivés car Raw contourne la logique de mixage automatique ; les raccourcis clavier fonctionnent toujours, Haut/Bas pilotant le servo 1 et Gauche/Droite le servo 2. Raw utilise la dernière valeur de vitesse sélectionnée ; réglez donc les vitesses avant de basculer si vous avez besoin d'une vitesse de mouvement précise.

**Comment le mode Auto calcule les cibles des servos**

- La valeur du curseur fermeture/ouverture est bornée à `limits.base_min/base_max`, puis normalisée (`t = base / base_max`) pour interpoler entre les poses ouverte et fermée définies par `auto_extremes` pour chaque côté du doigt.
- Le curseur de décalage latéral est borné à `limits.side_min/side_max` et converti en facteur de mélange (`u`). Les décalages négatifs interpolent de la pose centrale vers `left_open`/`left_closed` ; les décalages positifs interpolent vers les extrêmes du côté droit.
- Sans décalage latéral, les deux servos reçoivent simplement la valeur du curseur de base. Les cibles finales des servos sont bornées à `limits.servo_min/servo_max` avant d'être émises, ce qui maintient les mouvements dans des limites sûres calibrées.

Les raccourcis clavier complètent les curseurs (documentés au §5.2).

![Finger control panel with per-finger sliders and status indicators](../en/screenshots/finger_control_frame.png)

### 4.2 Pile de contrôle globale (à droite du panneau des doigts)

1. **Connexion :** sélection du port et du débit (les deux listes déroulantes sont désactivées lorsque la connexion est établie), boutons de connexion/déconnexion. La barre d'état en bas indique le succès ou les erreurs.
2. **Contrôles globaux :**
   - **Open All / Close All / Center All** – s'appliquent instantanément à tous les doigts.
   - **Liste déroulante Global Speed** – fixe les sélecteurs de vitesse par doigt à une valeur commune (1–6).
3. **Gestion des poses :** enregistrez, chargez, appliquez et supprimez les poses stockées dans `data/hand_config.yaml`.
   - Disposition : `Pose: [liste déroulante]  ✓ Appliquer  🗑 Supprimer  Nom : [champ]  ➕ Ajouter nouveau`
   - **🗑 Supprimer** supprime définitivement la pose sélectionnée (boîte de dialogue de confirmation affichée).
4. **Lecteur de séquences :** sélectionnez et exécutez des animations multi-étapes, avec boucle facultative. Accédez à la boîte de dialogue du gestionnaire de séquences via **🔧 Gérer**.

![Connection, global controls, pose management, and sequence player stack](../en/screenshots/control_frame.png)

### 4.3 Panneau de télémétrie et de retour (colonne de droite)

- **Ligne de contrôles :**
  - Mettre en pause/reprendre les mises à jour du graphique.
  - Bascule de fenêtre glissante.
  - Sélection des métriques (position, charge, vitesse, température, tension, indicateur de mouvement).
  - Bascule de mode (Multi-Servo vs Scope) avec un sélecteur de servo pour ce dernier.
  - Liste déroulante de visibilité des servos avec les aides « All/None/Clear ».
  
![Display mode, metric selection, and scope controls](../en/screenshots/chart_mode_controls.png)

![Display menu for choosing telemetry metrics](../en/screenshots/chart_select_display_values.png)

![Servo visibility menu with quick actions](../en/screenshots/chart_servos_selection.png)

#### Modes de graphique

- **Multi-Servo** (par défaut) conserve toutes les courbes de servos activées sur le graphique. Utilisez la liste déroulante **Servos** pour activer/désactiver rapidement des groupes et comparer le mouvement ou la charge entre les doigts.
- **Scope** active le sélecteur **Scope Servo**, vous permettant de vous concentrer sur un seul canal tout en utilisant les mêmes cases à cocher de métriques. Combinez ce mode avec le menu de visibilité des servos (par ex. tout masquer, puis réactiver le servo de la sonde) pour obtenir une vue de type oscilloscope sans autres courbes.
- Quel que soit le mode, le tableau de télémétrie continue de présenter tous les servos, ce qui vous permet de corréler le graphique ciblé avec l'instantané de données global.
- **Zone de graphique :** tracé Matplotlib affichant la télémétrie sélectionnée. Zoom via des curseurs :
  - **Y Zoom / Pan :** mise à l'échelle et décalage verticaux.
  - **Time Zoom / Pan :** se concentrer sur l'historique récent ou les échantillons plus anciens.
- **Tableau de retour :** grille défilante récapitulant les valeurs Goal, Position, Speed, Load, Voltage, Temperature, Status et Moving pour chaque servo.

![Chart controls with zoom/pan sliders and telemetry traces](../en/screenshots/chart_frame.png)

![Feedback table showing live servo metrics](../en/screenshots/feedback_frame.png)

### 4.4 Journal d'exécution et barre d'état

Situé sous le panneau des doigts, le journal enregistre les opérations par ordre chronologique. La barre d'état affiche la dernière action ou le dernier avertissement.

![Execution log and current status bar](../en/screenshots/log_and_last_action_frame.png)

---

## 5. Utilisation de la main

### 5.1 Connexion au matériel

1. Alimentez les servos et branchez l'adaptateur USB.
2. Lancez la GUI et vérifiez que le bon **Port** est sélectionné automatiquement (`COM*` sous Windows ou `/dev/tty*` sous Linux/macOS).
3. Cliquez sur **▶ Connecter**. En cas de succès, les états des boutons changent et la barre d'état est mise à jour.
4. Si la connexion échoue, vérifiez le câblage, l'alimentation et l'attribution du port.

### 5.2 Contrôle manuel et raccourcis

- Sélectionnez un doigt avec les touches **1–4** (1 = annulaire, 2 = majeur, 3 = index, 4 = pouce).
- **Touches fléchées :** Haut/Bas ajustent la position ; Gauche/Droite ajustent le décalage latéral.
- Maintenir **Shift** multiplie la taille du pas par 5 ; **Ctrl** la multiplie par 10.
- **Q / E :** ferment/ouvrent complètement le doigt sélectionné.
- **C :** centre le décalage latéral.
- Les curseurs à l'écran reflètent les entrées clavier en temps réel.

![Manual finger control panel with keyboard shortcut overlay](../en/screenshots/manual_finger_control_frame.png)

![Example of fully closing a finger using controls](../en/screenshots/close_finger.png)

![Example of lateral movement adjustment](../en/screenshots/move_finger.png)

### 5.3 Réglage des vitesses

- La liste déroulante de vitesse par doigt (1 = lent, 6 = rapide) contrôle la vitesse des servos.
- Le sélecteur **Global Speed** synchronise les vitesses de tous les doigts.
- Observez les changements de vitesse dans le tableau de retour (ligne `Speed`) pendant le mouvement.

### 5.4 Application et suppression de poses

1. Disposez les positions des doigts à l'aide des curseurs ou des raccourcis clavier.
2. Dans **Gestion des poses**, saisissez un nom unique et cliquez sur **➕ Ajouter nouveau**.
3. Pour appliquer, sélectionnez la pose dans la liste déroulante et cliquez sur **✓ Appliquer**.
4. Pour supprimer, sélectionnez la pose dans la liste déroulante et cliquez sur **🗑 Supprimer**. Une boîte de dialogue de confirmation évite toute suppression accidentelle.

> Les poses ne stockent que les positions des servos ; les vitesses sont déterminées à l'exécution par les réglages de la GUI.

### 5.5 Construction et exécution de séquences

1. Cliquez sur **🔧 Gérer** dans le lecteur de séquences.
2. Dans la boîte de dialogue :
   - Utilisez la liste **Available Poses** pour ajouter des étapes (double-clic ou appui sur **➕ Ajouter**).
   - Ajustez les vitesses par doigt via les zones numériques et définissez des délais d'étape facultatifs.
   - Insérez des intervalles de pause dédiés avec **⏱ Delay**.
   - Réorganisez les étapes avec les boutons ↑/↓.
   - Saisissez un nom et cliquez sur **💾 Enregistrer la séquence**.
   - Cliquez sur **▶ Exécuter** pour tester sans enregistrer.
3. De retour dans la fenêtre principale, sélectionnez la séquence et appuyez sur **▶ Lire**. Activez **Loop** pour une lecture continue.

> Les définitions de séquences résident dans `data/hand_config.yaml`, sous la clé `sequences`. Les boucles sont contrôlées côté exécution, et non dans le YAML.

![Sequence manager dialog with available poses and sequence builder](../en/screenshots/sequences_editor.png)

### 5.6 Suivi de la télémétrie

- Assurez-vous que les métriques souhaitées sont cochées dans le menu **Display**.
- Utilisez les curseurs de zoom/panoramique pour vous concentrer sur les segments d'intérêt.
- Survolez les éléments du graphique (interactions standard de Matplotlib) pour inspecter les valeurs.
- Le tableau de retour se met à jour de manière asynchrone ; les cellules surlignées indiquent des changements récents.
- Si le graphique devient surchargé, cliquez sur **⌫ Effacer** pour réinitialiser les données collectées.

---

## 6. Interface en ligne de commande (`amazing_hand_cmd.py`)

La CLI vous permet d'appliquer des poses et de jouer des séquences directement depuis un terminal, sans lancer la GUI. Elle lit le même fichier `data/hand_config.yaml`.

### 6.1 Utilisation de base

```bash
# List all saved poses and sequences
python amazing_hand_cmd.py --list

# Apply a single pose
python amazing_hand_cmd.py --pose open
python amazing_hand_cmd.py --pose close

# Play a sequence once
python amazing_hand_cmd.py --sequence demo

# Play a sequence in a loop (Ctrl+C to stop)
python amazing_hand_cmd.py --sequence wave --loop
```

### 6.2 Options

| Option | Défaut | Description |
|--------|---------|-------------|
| `--pose NAME` | – | Applique la pose nommée puis quitte |
| `--sequence NAME` | – | Joue la séquence nommée puis quitte |
| `--list` | – | Liste toutes les poses et séquences |
| `--loop` | off | Joue la séquence en boucle jusqu'à Ctrl+C |
| `--port PORT` | `/dev/ttyACM0` (Linux) / `COM9` (Win) | Remplace le port série |
| `--baudrate N` | `1000000` | Remplace le débit |
| `--config PATH` | `data/hand_config.yaml` | Chemin vers un autre fichier de configuration |

### 6.3 Remarques

- Le couple est **activé** à la connexion et **désactivé** à la sortie, afin que les servos se relâchent à la fin du script.
- Les vitesses et délais par étape se comportent de manière identique au lecteur de séquences de la GUI.
- L'option `--loop` ne peut être utilisée qu'avec `--sequence`.

---

## 7. Dépannage

| Symptôme | Action suggérée |
|---------|-----------------| 
| **Aucun port série listé** | Rebranchez l'adaptateur USB, installez les pilotes ou redémarrez la GUI. |
| **Bouton Connecter grisé** | Déjà connecté ; cliquez d'abord sur **⏹ Déconnecter**. |
| **Interface peu réactive lors du redimensionnement** | Les optimisations de performance (redimensionnement temporisé, redessins limités) réduisent ce phénomène, mais fermer les fenêtres inutiles peut aider. |
| **La séquence ne bouge pas tous les doigts** | Vérifiez les vitesses par étape et assurez-vous que chaque pose contient les huit valeurs de servo. |
| **L'indicateur de blocage persiste** | Inspectez les obstructions mécaniques ; l'état bloqué se déclenche lorsque la cible et la position diffèrent sensiblement sans mouvement. |

---

## 8. Annexe

### 8.1 Structure des fichiers

```
AmazingHandControl/
├── amazing_hand_gui.py          # GUI application
├── amazing_hand_cmd.py          # CLI tool
├── data/hand_config.yaml        # Poses & sequences
├── data/config.yaml             # Application settings
├── docs/<lang>/user_manual.md        # This document
├── docs/<lang>/CONFIG_FORMAT.md      # YAML config file reference
├── docs/en/screenshots/              # PNG captures embedded in this manual
├── docs/<lang>/scs_servo_protocol.md # SCS servo protocol reference
└── README.md                    # Quick reference
```

### 8.2 Liens utiles

- [AmazingHand (projet officiel)](https://github.com/pollen-robotics/AmazingHand)
- [Outil de débogage des servos Feetech](https://github.com/Robot-Maker-SAS/FeetechServo/tree/main/feetech%20debug%20tool%20master/FD1.9.8.2)
- [Tutoriel d'identification des servos](https://www.robot-maker.com/forum/tutorials/article/168-brancher-et-controler-le-servomoteur-feetech-sts3032-360/)

---

## 9. Historique des révisions

| Date | Auteur | Remarques |
|------|--------|-------|
| 2026-03-22 | Ingo | Ajout de la section CLI (`amazing_hand_cmd.py`) ; mise à jour de la version du manuel. |
| 2026-03-21 | Ingo | Mise à jour de la disposition des panneaux : échange annulaire/index, pouce déplacé à droite, pile de contrôle déplacée à gauche. Curseur latéral du pouce inversé. Bouton de suppression de pose ajouté entre Appliquer et Nom. Les listes déroulantes Port et Baudrate sont désormais verrouillées pendant la connexion. Le raccourci clavier 1–4 correspond maintenant à annulaire/majeur/index/pouce. |
| 2025-11-25 | Ingo | Ajout d'une galerie de captures d'écran étendue, d'explications sur les modes de graphique et de présentations de panneaux actualisées. |
| 2025-11-25 | Ingo | Manuel initial couvrant les panneaux de l'interface, les flux de travail et l'utilisation de la télémétrie. |
