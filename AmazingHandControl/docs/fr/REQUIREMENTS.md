[English](../en/REQUIREMENTS.md) | [Deutsch](../de/REQUIREMENTS.md) | [Español](../es/REQUIREMENTS.md) | Français | [Italiano](../it/REQUIREMENTS.md) | [日本語](../ja/REQUIREMENTS.md) | [한국어](../ko/REQUIREMENTS.md) | [Português (BR)](../pt-br/REQUIREMENTS.md) | [Português (PT)](../pt-pt/REQUIREMENTS.md) | [简体中文](../zh-hans/REQUIREMENTS.md) | [繁體中文](../zh-hant/REQUIREMENTS.md)

# AmazingHandGUI — Exigences et critères d'acceptation

Ce document recense les exigences fonctionnelles et les critères d'acceptation
issus de l'implémentation actuelle. Chaque exigence référence le ou les
fichiers sources où le comportement est implémenté.

---

## 1. Gestion de la connexion

### FR-CONN-1 : Sélection du port série
La GUI fournit une liste déroulante énumérant les ports série détectés automatiquement.

| AC | Critère |
|----|-----------|
| 1.1 | Sous Linux, les périphériques `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*` apparaissent ; s'il n'en existe aucun, `/dev/ttyACM0` et `/dev/ttyUSB0` sont listés comme replis. |
| 1.2 | Sous Windows, `COM1`–`COM20` sont listés. |
| 1.3 | La valeur par défaut correspond à la valeur propre à la plateforme issue de `config.yaml` (`/dev/ttyACM0` ou `COM9`). |

### FR-CONN-2 : Sélection du débit
Une liste déroulante propose des options de débit configurables.

| AC | Critère |
|----|-----------|
| 2.1 | Les options proviennent de `config.yaml` → `serial.baudrate_options` (par défaut `[9600, 115200, 1000000]`). |
| 2.2 | La sélection par défaut est `1000000`. |
| 2.3 | La liste déroulante est désactivée lorsque la connexion est établie. |

### FR-CONN-3 : Connecter / Déconnecter
Les boutons Connecter et Déconnecter gèrent la connexion série et le couple des servos.

| AC | Critère |
|----|-----------|
| 3.1 | Connecter ouvre le port série, active le couple sur les servos 1–8, désactive les contrôles Connecter/port/débit et active Déconnecter. |
| 3.2 | Déconnecter désactive le couple sur les 8 servos, réactive Connecter/port/débit et désactive Déconnecter. |
| 3.3 | Un échec de connexion affiche une erreur dans la barre d'état et dans le journal ; la GUI reste déconnectée. |

### FR-CONN-4 : Connexion automatique au démarrage
La GUI tente de se connecter automatiquement 100 ms après le lancement.

| AC | Critère |
|----|-----------|
| 4.1 | `connect_controller()` est appelée via `root.after(100, …)` pendant l'initialisation. |

### FR-CONN-5 : Connexion via la CLI
La CLI se connecte via les arguments `--port` et `--baudrate`.

| AC | Critère |
|----|-----------|
| 5.1 | `--port` et `--baudrate` remplacent les valeurs par défaut. |
| 5.2 | Le couple est activé sur les 8 servos à la connexion. |
| 5.3 | Le couple est désactivé à la sortie (y compris Ctrl+C via un bloc `finally`). |
| 5.4 | `--list` n'ouvre **pas** de connexion matérielle. |

---

## 2. Contrôle des doigts

### FR-FING-1 : Quatre widgets de doigt
Quatre contrôles de doigt sont affichés : Annulaire, Majeur, Index, Pouce — chacun avec 2 servos.

| AC | Critère |
|----|-----------|
| 1.1 | Exactement 4 widgets `FingerControl` sont rendus, avec des noms correspondant aux paires de servos de `config.yaml` : Annulaire (5,6), Majeur (3,4), Index (1,2), Pouce (7,8). |

### FR-FING-2 : Mode Auto (base + side)
Le mode Auto offre un curseur vertical de fermeture/ouverture et un curseur horizontal latéral.

| AC | Critère |
|----|-----------|
| 2.1 | Curseur vertical : 0° (ouvert) à 110° (fermé) ; haut = fermé, bas = ouvert. |
| 2.2 | Curseur horizontal : −40° à +40°. |
| 2.3 | Déplacer l'un ou l'autre curseur envoie des positions interpolées (via `compute_auto_positions`) aux deux servos. |

### FR-FING-3 : Mode Raw
Le mode Raw affiche deux curseurs verticaux indépendants (un par servo).

| AC | Critère |
|----|-----------|
| 3.1 | Sélectionner Raw masque les curseurs Auto et affiche deux curseurs verticaux par servo (−40 à 110). |
| 3.2 | La case à cocher Mimic est désactivée et décochée ; le bouton de centrage est désactivé. |
| 3.3 | Changer de mode synchronise les valeurs dans les deux sens (auto ↔ raw via `decompose_servo_positions`). |

### FR-FING-4 : Contrôle de la vitesse
Chaque doigt dispose d'une liste déroulante de vitesse (1–6).

| AC | Critère |
|----|-----------|
| 4.1 | La plage va de `speeds.min` (1) à `speeds.max` (6), par défaut `speeds.default` (3). |
| 4.2 | La vitesse est envoyée via `write_goal_speed()` par servo avant les commandes de position. |

### FR-FING-5 : Mode Mimic
Les changements de fermeture/ouverture sur un doigt qui imite sont propagés à tous les autres doigts dont Mimic est activé.

| AC | Critère |
|----|-----------|
| 5.1 | Activer Mimic sur A et B fait que les changements du curseur fermeture/ouverture de A se répercutent sur B et inversement. |
| 5.2 | Mimic ne s'applique qu'en mode Auto ; passer en Raw le désactive. |

### FR-FING-6 : Bouton de centrage
Réinitialise le décalage latéral à 0°.

| AC | Critère |
|----|-----------|
| 6.1 | Cliquer sur Centrer met `side_var` à 0 et déclenche une mise à jour de position. |
| 6.2 | Centrer est désactivé en mode Raw. |

### FR-FING-7 : Molette de souris sur le curseur de position
La molette de défilement ajuste la position de ±5°.

| AC | Critère |
|----|-----------|
| 7.1 | Molette vers le haut → +5° (fermer), molette vers le bas → −5° (ouvrir), borné aux limites. |

### FR-FING-8 : Indicateur LED d'activité
Chaque doigt affiche une LED d'état.

| AC | Critère |
|----|-----------|
| 8.1 | En mouvement (drapeau moving = true) → vert clignotant à intervalles d'environ 350 ms. |
| 8.2 | Bloqué (erreur cible-vs-position ≥ 8° et sans mouvement) → rouge fixe. |
| 8.3 | Inactif → gris. |

---

## 3. Contrôle au clavier

### FR-KEY-1 : Sélection du doigt
Les touches 1–4 sélectionnent le doigt actif.

| AC | Critère |
|----|-----------|
| 1.1 | 1 = Annulaire, 2 = Majeur, 3 = Index, 4 = Pouce. |
| 1.2 | La barre d'état affiche le nom du doigt sélectionné. |

### FR-KEY-2 : Déplacement avec les touches fléchées
Les touches fléchées déplacent le doigt sélectionné.

| AC | Critère |
|----|-----------|
| 2.1 | Haut = fermer (augmenter la position), Bas = ouvrir (diminuer). |
| 2.2 | Droite = augmenter le décalage latéral, Gauche = diminuer. |

### FR-KEY-3 : Modificateurs de précision
La taille du pas varie selon la touche modificatrice.

| AC | Critère |
|----|-----------|
| 3.1 | Aucun modificateur : 1° (précis). |
| 3.2 | Shift : 5° (normal). |
| 3.3 | Ctrl : 10° (rapide). |
| 3.4 | La barre d'état affiche le nom du mode et l'angle résultant. |

### FR-KEY-4 : Actions rapides
Des raccourcis à une seule touche pour les actions courantes.

| AC | Critère |
|----|-----------|
| 4.1 | Q = fermer complètement à 110°. |
| 4.2 | E = ouvrir complètement à 0°. |
| 4.3 | C = centrer le latéral à 0°. |

---

## 4. Contrôles globaux

### FR-GLOB-1 : Tout ouvrir
Met tous les doigts complètement ouverts.

| AC | Critère |
|----|-----------|
| 1.1 | Tous les `pos_var` → 0, tous les `side_var` → 0, positions envoyées au matériel. |

### FR-GLOB-2 : Tout fermer
Met tous les doigts complètement fermés.

| AC | Critère |
|----|-----------|
| 2.1 | Tous les `pos_var` → 110, tous les `side_var` → 0, positions envoyées. |

### FR-GLOB-3 : Tout centrer
Réinitialise tous les décalages latéraux.

| AC | Critère |
|----|-----------|
| 3.1 | Tous les `side_var` → 0, positions envoyées. |

### FR-GLOB-4 : Vitesse globale
Une liste déroulante fixe d'un coup les vitesses de tous les doigts.

| AC | Critère |
|----|-----------|
| 4.1 | Sélectionner une valeur met à jour chaque liste déroulante de vitesse par doigt. |
| 4.2 | La vitesse est bornée à [1, 6]. |

---

## 5. Gestion des poses

### FR-POSE-1 : Enregistrer une pose
L'utilisateur saisit un nom et enregistre les positions actuelles des 8 servos.

| AC | Critère |
|----|-----------|
| 1.1 | Les positions des 4 doigts (8 valeurs) sont capturées via `get_positions()`. |
| 1.2 | Le nom est validé via `validate_name()` avant l'enregistrement. |
| 1.3 | En cas de succès : la liste déroulante est rafraîchie (triée), le champ est vidé, la barre d'état confirme. |
| 1.4 | Un nom invalide ou vide affiche une boîte de dialogue d'erreur. |

### FR-POSE-2 : Appliquer une pose
Sélectionner une pose et cliquer sur Appliquer amène la main à cette pose.

| AC | Critère |
|----|-----------|
| 2.1 | Les 8 positions sont appliquées à tous les widgets de doigt. |
| 2.2 | Les positions des servos sont envoyées au matériel. |
| 2.3 | Le délai est estimé à partir de la distance de mouvement et de la vitesse ; la fin de pose est journalisée après ce délai avec une comparaison cible vs réel. |

### FR-POSE-3 : Supprimer une pose
Supprime la pose sélectionnée après confirmation.

| AC | Critère |
|----|-----------|
| 3.1 | Une boîte de dialogue oui/non demande confirmation. |
| 3.2 | Après confirmation : la pose est supprimée de la configuration, le YAML est enregistré, la liste déroulante est rafraîchie. |
| 3.3 | S'il ne reste aucune pose, la liste déroulante affiche `<no poses>`. |

### FR-POSE-4 : Validation des noms
Les noms sont validés pour éviter de corrompre le YAML.

| AC | Critère |
|----|-----------|
| 4.1 | Vide / uniquement des espaces → rejeté. |
| 4.2 | Plus de 50 caractères → rejeté. |
| 4.3 | Contient `: { } [ ] , & * # ? \| - < > = ! % @ \` " '` → rejeté. |
| 4.4 | Contient des caractères de contrôle (ASCII < 32) → rejeté. |
| 4.5 | Espaces en début/fin → rejeté. |

---

## 6. Gestion des séquences

### FR-SEQ-1 : Lecteur de séquences (fenêtre principale)
Sélection par liste déroulante, case à cocher Loop, boutons Lecture / Pause / Arrêt.

| AC | Critère |
|----|-----------|
| 1.1 | La liste déroulante énumère toutes les séquences enregistrées (ou `<no sequences>`). |
| 1.2 | La case à cocher Loop active la répétition continue. |
| 1.3 | Lecture démarre la séquence dans un thread d'arrière-plan. |
| 1.4 | Pause alterne pause/reprise ; le texte du bouton bascule entre "⏸ Pause" et "▶ Reprendre". |
| 1.5 | Arrêt met `stop_sequence = True` ; le thread de la séquence se termine. |

### FR-SEQ-2 : Moteur d'exécution des séquences
Les séquences s'exécutent dans un thread d'arrière-plan avec des attentes interruptibles.

| AC | Critère |
|----|-----------|
| 2.1 | Les étapes de pose analysent le format `"pose_name:s1,s2,...,s8\|delay"`. |
| 2.2 | Les étapes `SLEEP:duration` mettent en pause sans commande matérielle. |
| 2.3 | S'il n'y a pas de délai explicite : attente automatique = `15.0 − (avg_speed − 1) × 2.4` secondes. |
| 2.4 | Les attentes s'exécutent par incréments de 0.1 s, en vérifiant les drapeaux d'arrêt/pause à chaque tic. |
| 2.5 | En mode boucle, un intervalle de 0.5 s sépare les itérations. |
| 2.6 | Les noms de pose inconnus sont ignorés avec un avertissement. |
| 2.7 | Les boutons Lecture/Pause/Arrêt alternent leur état activé/désactivé pendant l'exécution. |

### FR-SEQ-3 : Boîte de dialogue du gestionnaire de séquences
Boîte de dialogue à deux panneaux, accessible via le bouton "🔧 Gérer".

| AC | Critère |
|----|-----------|
| 3.1 | Panneau gauche : liste des séquences enregistrées avec les boutons Exécuter, Modifier et Supprimer. |
| 3.2 | Un double-clic exécute la séquence une fois (sans boucle) sans fermer la boîte de dialogue. |
| 3.3 | Modifier charge les étapes dans le constructeur et préremplit le champ du nom. |

### FR-SEQ-4 : Constructeur de séquences
Panneau droit pour construire des séquences à partir de poses.

| AC | Critère |
|----|-----------|
| 4.1 | Les poses disponibles sont listées ; un double-clic ajoute une étape avec la vitesse/le délai actuels. |
| 4.2 | Zones numériques de vitesse par doigt (1–6) ; "⬇ Copier depuis l'interface" importe les vitesses de la fenêtre principale. |
| 4.3 | Le champ de délai ajoute le suffixe `\|delay` aux étapes de pose. |
| 4.4 | "⏱ Délai" insère une étape `SLEEP:Xs` autonome. |
| 4.5 | ↑/↓ réordonnent, ➖ supprime, 🗑 efface tout. |
| 4.6 | "💾 Enregistrer la séquence" valide le nom, enregistre, rafraîchit les listes déroulantes. |
| 4.7 | "▶ Exécuter" exécute la séquence construite sans l'enregistrer ni fermer la boîte de dialogue. |

### FR-SEQ-5 : Validation de la saisie du délai
Les valeurs flottantes invalides dans le champ de délai sont gérées sans erreur.

| AC | Critère |
|----|-----------|
| 5.1 | Un délai non numérique équivaut à aucun délai (l'étape est ajoutée sans `\|delay`). |
| 5.2 | Un délai SLEEP non numérique affiche "Invalid delay value" dans la barre d'état. |

---

## 7. Surveillance des servos

### FR-MON-1 : Collecte de télémétrie en arrière-plan
Un thread démon interroge les 8 servos à environ 10 Hz.

| AC | Critère |
|----|-----------|
| 1.1 | Le thread dort 0.1 s entre les itérations. |
| 1.2 | Métriques collectées par servo : position, charge, température, tension, vitesse, drapeau de mouvement, état, cible. |
| 1.3 | Une lecture échouée répète la dernière valeur connue pour garder les tableaux synchronisés. |
| 1.4 | Les données de retour sont mises à jour sous `feedback_lock` de manière atomique. |

### FR-MON-2 : Affichage du graphique
Graphique Matplotlib intégré dans le panneau droit.

| AC | Critère |
|----|-----------|
| 2.1 | Métriques sélectionnables : Position, Cible vs Actuel, Couple, Vitesse, Température, Tension, En mouvement. |
| 2.2 | La liste déroulante "Servos" active/désactive lesquelles des 8 courbes sont visibles (avec ✓ Tous / ✕ Aucun). |
| 2.3 | Les redessins du graphique sont limités à des intervalles de ≥100 ms. |
| 2.4 | Aucune métrique sélectionnée → message "Select at least one metric". |
| 2.5 | Aucune donnée → message "Waiting for data...". |

### FR-MON-3 : Modes du graphique
Deux modes : Multi-Servo et Scope.

| AC | Critère |
|----|-----------|
| 3.1 | Le mode Scope affiche un sélecteur "Scope Servo" pour se concentrer sur un seul servo. |
| 3.2 | Multi-Servo masque le sélecteur Scope Servo. |

### FR-MON-4 : Zoom et panoramique du graphique
Quatre curseurs pour contrôler la vue.

| AC | Critère |
|----|-----------|
| 4.1 | Y-Zoom : 0.2× à 5.0×, par défaut 1.1×. |
| 4.2 | Y-Pan : −3.0 à +3.0, par défaut 0.0. |
| 4.3 | Time-Zoom : 10 % à 100 % des données disponibles. |
| 4.4 | Time-Pan : 0 % (le plus ancien) à 100 % (le plus récent). |
| 4.5 | Tous les curseurs déclenchent des redessins de graphique anti-rebond. |

### FR-MON-5 : Mode glissant
Limite le graphique aux N derniers points de données.

| AC | Critère |
|----|-----------|
| 5.1 | Lorsqu'il est activé et que les données dépassent `max_data_points` (100), les échantillons les plus anciens sont supprimés. |
| 5.2 | Désactiver le mode glissant conserve toutes les données collectées. |

### FR-MON-6 : Pause / Reprise / Effacement du graphique

| AC | Critère |
|----|-----------|
| 6.1 | Pause arrête les redessins du graphique ; la collecte de télémétrie continue. |
| 6.2 | Effacer réinitialise tous les tableaux de données et le zoom/panoramique aux valeurs par défaut. |

### FR-MON-7 : Panneau de retour
Tableau en grille affichant la télémétrie en direct de tous les servos.

| AC | Critère |
|----|-----------|
| 7.1 | Colonnes : S1–S8. Lignes : Cible, Position, Vitesse, Couple, Tension, Courant, Température, État, En mouvement. |
| 7.2 | Valeurs formatées par `format_feedback_value()` : position `X.XX°`, vitesse `X.X°/s`, tension `X.XX V`, température `X.X °C`, courant `X mA`, charge `X.X %`, état `0xHH`, en mouvement `Yes/No`. |
| 7.3 | Seules les cellules modifiées sont mises à jour (cache de différences). |
| 7.4 | Le rafraîchissement est limité à ≥50 ms entre les mises à jour. |

---

## 8. Configuration

### FR-CFG-1 : Chargement de la configuration de l'application
`config.yaml` est chargé avec des valeurs par défaut pour toutes les clés absentes.

| AC | Critère |
|----|-----------|
| 1.1 | Fichier absent → configuration par défaut complète utilisée. |
| 1.2 | Les clés absentes sont fusionnées depuis les valeurs par défaut (fusion à deux niveaux). |
| 1.3 | Échec d'analyse → les valeurs par défaut sont renvoyées, l'erreur est imprimée sur stdout. |

### FR-CFG-2 : Correspondance des servos
Les ID de servo par doigt sont définis dans `config.yaml` → `servos`.

| AC | Critère |
|----|-----------|
| 2.1 | La configuration définit pointer=[1,2], middle=[3,4], ring=[5,6], thumb=[7,8]. |
| 2.2 | `all_ids` = [1,2,3,4,5,6,7,8]. |

### FR-CFG-3 : Limites d'angle

| AC | Critère |
|----|-----------|
| 3.1 | `servo_min` = −40, `servo_max` = 110, `base_min` = 0, `base_max` = 110, `side_min` = −40, `side_max` = 40. |
| 3.2 | Toutes les plages des curseurs dérivent de ces valeurs. |

### FR-CFG-4 : Extrêmes de Auto
Points d'extrémité de l'interpolation bilinéaire pour le calcul du décalage latéral.

| AC | Critère |
|----|-----------|
| 4.1 | `left_open`, `right_open`, `left_closed`, `right_closed`, `center_open`, `center_closed` sont configurables. |
| 4.2 | `compute_auto_positions()` les utilise pour l'interpolation. |

### FR-CFG-5 : Configuration de la vitesse

| AC | Critère |
|----|-----------|
| 5.1 | `speeds.default` = 3, `speeds.min` = 1, `speeds.max` = 6. |

---

## 9. Outil CLI

### FR-CLI-1 : Lister les poses et les séquences
`--list` imprime toutes les poses et séquences sans ouvrir de connexion.

| AC | Critère |
|----|-----------|
| 1.1 | La sortie affiche le nombre de poses, chaque nom avec ses positions. |
| 1.2 | La sortie affiche le nombre de séquences, chaque nom avec le nombre d'étapes et les détails. |
| 1.3 | Aucune connexion série n'est ouverte. |

### FR-CLI-2 : Appliquer une pose
`--pose NAME` envoie une pose enregistrée au matériel.

| AC | Critère |
|----|-----------|
| 2.1 | Positions chargées depuis la configuration ; vitesse par défaut 3 appliquée à tous les servos. |
| 2.2 | Pose inconnue → erreur + `sys.exit(1)`. |

### FR-CLI-3 : Jouer une séquence
`--sequence NAME` joue une séquence ; `--loop` la répète jusqu'à Ctrl+C.

| AC | Critère |
|----|-----------|
| 3.1 | Les vitesses et le délai sont analysés à partir de la chaîne de l'étape. |
| 3.2 | Les étapes `SLEEP` mettent en pause sans commande matérielle. |
| 3.3 | Pas de délai explicite → attente automatique = `15.0 − (avg_speed − 1) × 2.4` secondes. |
| 3.4 | SIGINT définit `stop_flag` pour une interruption propre. |
| 3.5 | Séquence inconnue → sortie avec erreur. |
| 3.6 | Séquence vide → sortie avec erreur. |
| 3.7 | Les poses inconnues au sein d'une séquence sont ignorées avec un WARNING. |

### FR-CLI-4 : Analyse des étapes
`parse_step()` gère plusieurs formats.

| AC | Critère |
|----|-----------|
| 4.1 | `SLEEP:2.0s` → attente de 2.0 s. |
| 4.2 | `open:3,3,...\|2.0s` → pose "open" avec vitesses et délai de 2.0 s. |
| 4.3 | `open` (nom seul) → pose avec vitesses par défaut, sans délai. |
| 4.4 | Les vitesses de moins de 8 sont complétées par 3 ; celles de plus de 8 sont tronquées. |
| 4.5 | Le suffixe de durée `s` / `S` est supprimé. |

### FR-CLI-5 : Actions mutuellement exclusives
`--list`, `--pose` et `--sequence` sont mutuellement exclusifs.

| AC | Critère |
|----|-----------|
| 5.1 | Passer plusieurs actions → sortie non nulle. |
| 5.2 | `--loop` sans `--sequence` → erreur. |

### FR-CLI-6 : Remplacement du fichier de configuration
`--config PATH` utilise un autre fichier YAML.

| AC | Critère |
|----|-----------|
| 6.1 | Fichier absent → erreur + `sys.exit(1)`. |

---

## 10. Persistance des données

### FR-DATA-1 : Fichier de configuration YAML
Les poses et les séquences sont stockées dans `data/hand_config.yaml`.

| AC | Critère |
|----|-----------|
| 1.1 | Le fichier utilise le format YAML avec les clés de premier niveau `poses` et `sequences`. |

### FR-DATA-2 : Charger la configuration

| AC | Critère |
|----|-----------|
| 2.1 | Fichier absent → `{'poses': {}, 'sequences': {}}`. |
| 2.2 | Fichier vide → clés renseignées automatiquement. |
| 2.3 | YAML malformé → structure vide, erreur imprimée sur stdout. |

### FR-DATA-3 : Enregistrer la configuration avec des tableaux en ligne
Les positions sont enregistrées en style flow via un post-traitement par expression régulière.

| AC | Critère |
|----|-----------|
| 3.1 | Le fichier contient le style `positions: [v1, v2, …, v8]`. |
| 3.2 | Les valeurs négatives sont conservées au format en ligne. |
| 3.3 | Renvoie `True` en cas de succès, `False` en cas d'erreur. |

### FR-DATA-4 : Création automatique du répertoire de données

| AC | Critère |
|----|-----------|
| 4.1 | Le répertoire `data/` est créé s'il n'existe pas avant l'écriture. |

### FR-DATA-5 : Intégrité de l'aller-retour
Les données écrites par la GUI peuvent être lues par la CLI et inversement.

| AC | Critère |
|----|-----------|
| 5.1 | Les poses, les positions négatives et les étapes de séquence survivent à un aller-retour enregistrement-GUI → lecture-CLI. |

---

## 11. Gestion des erreurs

### FR-ERR-1 : Erreur de connexion
Les connexions échouées ne font pas planter l'application.

| AC | Critère |
|----|-----------|
| 1.1 | La barre d'état affiche "Connection failed: …" ; `connected` reste `False`. |

### FR-ERR-2 : Débit invalide

| AC | Critère |
|----|-----------|
| 2.1 | Débit non numérique → la barre d'état affiche "Invalid baudrate". |

### FR-ERR-3 : Récupération du thread de supervision

| AC | Critère |
|----|-----------|
| 3.1 | Un échec de lecture d'un seul servo ne fait pas planter le thread. |
| 3.2 | Les erreurs sont imprimées sur stdout. |

### FR-ERR-4 : Dégradation de l'indicateur de mouvement

| AC | Critère |
|----|-----------|
| 4.1 | Après 3 échecs consécutifs de `read_moving`, la supervision est désactivée avec un message dans le journal. |
| 4.2 | Passe de `sync_read_moving` à des lectures par servo dès le premier échec de synchronisation. |

### FR-ERR-5 : Avertissements de fin de pose

| AC | Critère |
|----|-----------|
| 5.1 | Une erreur cible vs réel > 5° déclenche un avertissement ⚠ dans le journal. |
| 5.2 | Un délai d'attente de mouvement (6.0 s) déclenche un avertissement de timeout si les servos ne s'arrêtent jamais de bouger. |

### FR-ERR-6 : Configuration manquante (CLI)

| AC | Critère |
|----|-----------|
| 6.1 | Fichier de configuration absent → message d'erreur + `sys.exit(1)`. |

### FR-ERR-7 : Séquence vide / invalide

| AC | Critère |
|----|-----------|
| 7.1 | Étapes de séquence vides → `sys.exit(1)`. |
| 7.2 | Poses inconnues dans la séquence → ignorées avec WARNING. |

---

## 12. Disposition de l'interface

### FR-UI-1 : Structure de la fenêtre

| AC | Critère |
|----|-----------|
| 1.1 | Le titre inclut la version : "AmazingHand Controller v0.8". |
| 1.2 | Géométrie initiale : 1920×1200. |
| 1.3 | Un `PanedWindow` horizontal sépare les panneaux gauche (contrôles) et droit (graphique). |

### FR-UI-2 : Panneau gauche

| AC | Critère |
|----|-----------|
| 2.1 | Ligne 1 : Annulaire, Majeur, Index (3 doigts en travers). |
| 2.2 | Ligne 2 : Pouce (à droite) + contrôles empilés (Connexion, Global, Pose, Séquence). |
| 2.3 | Le journal d'exécution sous les contrôles, dans un séparateur vertical redimensionnable. |

### FR-UI-3 : Barre d'état

| AC | Critère |
|----|-----------|
| 3.1 | Se met à jour à la connexion, à la déconnexion, à la sélection d'un doigt, au changement de vitesse, lors des opérations de pose et en cas d'erreurs. |

### FR-UI-4 : Journal d'exécution

| AC | Critère |
|----|-----------|
| 4.1 | Les messages sont préfixés par un horodatage `[HH:MM:SS.mmm]`. |
| 4.2 | Défilement automatique jusqu'à la dernière entrée. |
| 4.3 | Les messages sont aussi imprimés sur stdout. |

### FR-UI-5 : Infobulles

| AC | Critère |
|----|-----------|
| 5.1 | Une infobulle jaune apparaît après 500 ms de survol, positionnée en bas à droite du widget. |
| 5.2 | Disparaît au départ de la souris ou à l'appui sur un bouton. |

### FR-UI-6 : Panneau droit (zone de graphique)

| AC | Critère |
|----|-----------|
| 6.1 | `PanedWindow` vertical : graphique en haut (min 200 px), retour en bas (min 150 px). |
| 6.2 | Curseurs de temps sous le graphique ; curseurs Y à droite. |

### FR-UI-7 : Aide de la CLI

| AC | Critère |
|----|-----------|
| 7.1 | `--help` se termine avec 0 et affiche toutes les options. |

### FR-UI-8 : Arguments de ligne de commande de la GUI

| AC | Critère |
|----|-----------|
| 8.1 | `--port` remplace le port série par défaut. |
| 8.2 | `--baudrate` remplace le débit par défaut (1000000). |

---

## Résumé de la couverture des tests

| Fichier de test | Périmètre | Nombre |
|-----------|-------|-------|
| `tests/test_hand_logic.py` | `load_app_config` (6), `servo_mapping` (3), `angle_limits` (1), `auto_extremes` (2), `speed_config` (1), `default_serial_port` (2), `ensure_data_dir` (2), `load_pose_definitions` (3), `compute_auto_positions` (6), `decompose_servo_positions` (5), `coerce_numeric` (11), `coerce_angle_degrees` (6), `coerce_bool` (6), `load_to_percent` (7), `estimate_current_from_load` (5), `format_feedback_value` (12), `get_time_window_indices` (8), `angle_rad` (3) | 89 |
| `tests/test_gui_utils.py` | `validate_name` (21), `clamp` (8), `load_config` (6), `save_config` (6) | 41 + 10 paramétrés |
| `tests/test_cmd.py` | `angle_rad` (8), `parse_step` (11), `cmd_list` (4), `load_config` (2), `apply_pose` (6), `_interruptible_sleep` (2), `auto_wait` (3), `mutual_exclusion` (1), `config_override` (2) | 41 |
| `tests/test_integration.py` | `cmd_pose` de bout en bout (5), `cmd_sequence` de bout en bout (6), aller-retour de configuration (3) | 14 |
| `tests/test_system.py` | Sous-processus de la CLI : `--help` (5), `--list` (9), options de `--help` (3), chemins d'erreur (5) | 22 |
| `tests/test_system_hardware.py` | Matériel réel : connexion (2), connexion via la CLI (2), application de pose (3), vitesse (2), télémétrie (6), séquence (2), récupération d'erreur (1), mouvement (2), déconnexion (1) — **nécessite l'option `--hardware`** | 21 |
| **Total (sans matériel)** | **217 tests** |
| **Total (avec matériel)** | **238 tests** |
