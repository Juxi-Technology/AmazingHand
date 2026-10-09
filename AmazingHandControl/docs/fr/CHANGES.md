[English](../en/CHANGES.md) | [Deutsch](../de/CHANGES.md) | [Español](../es/CHANGES.md) | Français | [Italiano](../it/CHANGES.md) | [日本語](../ja/CHANGES.md) | [한국어](../ko/CHANGES.md) | [Português (BR)](../pt-br/CHANGES.md) | [Português (PT)](../pt-pt/CHANGES.md) | [简体中文](../zh-hans/CHANGES.md) | [繁體中文](../zh-hant/CHANGES.md)

# AmazingHand Controller · Journal des modifications et justifications

Ce qui a été modifié par rapport au projet d'origine, pourquoi, et quel est le résultat réel.

Projet d'origine : `Betatester777/AmazingHandControl` (GUI Python + CLI pour l'AmazingHand)
Matériel : JuxiTechnology AmazingHand (8× servos Feetech SCS0009, retour par potentiomètre) — **les deux mains prises en charge**, sélectionnées au démarrage

---

## Contenu

1. [Recalibrage du système d'angles](#1-recalibrage-du-système-dangles)
2. [Boutons globaux : piloter des positions raw exactes](#2-boutons-globaux--piloter-des-positions-raw-exactes)
3. [Nouveau bouton de position médiane](#3-nouveau-bouton-de-position-médiane)
4. [La GUI et la CLI divergent (le bug central)](#4-la-gui-et-la-cli-divergent-le-bug-central)
5. [Corrections des données de poses](#5-corrections-des-données-de-poses)
6. [Lecteur de séquences : temporisation et diagnostics](#6-lecteur-de-séquences--temporisation-et-diagnostics)
7. [Nouvelle ligne de position raw dans le retour des servos](#7-nouvelle-ligne-de-position-raw-dans-le-retour-des-servos)
8. [**Prise en charge des mains gauche et droite**](#8-prise-en-charge-des-mains-gauche-et-droite)
9. [Détection automatique du port série](#9-détection-automatique-du-port-série)
10. [Référence de configuration](#10-référence-de-configuration)
11. [Résultats mesurés](#11-résultats-mesurés)
12. [Résumé fichier par fichier](#12-résumé-fichier-par-fichier)

---

## 1. Recalibrage du système d'angles

### 1.1 Limites d'angle : `0..110` → `-75..75`

L'original était calibré sur `0° = ouvert, 110° = fermé`. La course réelle de cette main se situe dans `-75..75`, donc tout a été recalibré.

**`data/config.yaml`**

| Clé | Avant | Après |
|---|---|---|
| `servo_min` / `servo_max` | -40 / 110 | **-75 / 75** |
| `base_min` / `base_max` | 0 / 110 | **-75 / 75** |
| `side_min` / `side_max` | -40 / 40 | **-35 / 35** |
| `left_open` | `[32, -40]` | **`[32, -35]`** |
| `right_open` | `[-40, 32]` | **`[-35, 32]`** |
| `left_closed` / `right_closed` | `[110, 110]` | **`[75, 75]`** |
| `center_closed` | `[110, 110]` | **`[75, 75]`** |

**Les 19 poses ont toutes été remises à l'échelle**, par ex. `open` de `[0]*8` à `[-35]*8`, `close` de `[110]*8` à `[75]*8`.

### 1.2 Écart latéral : `±40°` → `±35°`

Le curseur latéral se normalise avec `u = |side_offset| / |side_min|`, donc modifier la limite seule ne change **pas** l'amplitude réelle d'écartement des doigts — cela ne fait que remettre le curseur à l'échelle. Pour modifier l'écartement physique, il faut aussi changer `auto_extremes`. Avec les deux modifiés :

| | Avant (±40) | Après (±35) |
|---|---|---|
| Plage du curseur | −40 … +40 | −35 … +35 |
| Ouverture complète, à l'extrême latéral | `(32, -40)`, écart **72°** | `(32, -35)`, écart **67°** |

### 1.3 Concordance avec la référence du fabricant

La démo Arduino du fabricant (`Amazing_RHand_Demo.ino`) convertit ainsi :

```c
float Step = 0.293; // 300°/1024
sc.RegWritePos(1, MiddlePos[0] + Pos_1 / Step, 0, Speed);
```

Et rustypot 1.4.2 (`src/servo/feetech/scs0009.rs`) :

```rust
fn to_raw(value: f64) -> i16 {
    let a = (1024.0 * value / (300.0_f64.to_radians()) + 511.0) as i16;
    a.to_be()
}
```

**Conclusion : les deux côtés utilisent la même échelle en degrés** (0.29297°/pas, pleine échelle 300°, raw 0–1023) — il n'y a aucune erreur de rapport. La seule différence systématique est le point zéro :

- rustypot centre toujours sur raw **511**
- le firmware du fabricant utilise une valeur de calibration par servo, `MiddlePos = {451, 571, 451, 571, 451, 571, 451, 571}`

Ils diffèrent de **±60 raw = ±17.6°**. C'est exactement ce que corrige le bouton « Middle position » ci-dessous.

---

## 2. Boutons globaux : piloter des positions raw exactes

### 2.1 Le problème

Les fonctions d'origine `open_all()` / `close_all()` avaient des angles codés en dur :

```python
def open_all(self):
    for finger in self.fingers:
        finger.pos_var.set(0)      # hard-coded 0
        finger.side_var.set(0)
        ...
def close_all(self):
    for finger in self.fingers:
        finger.pos_var.set(110)    # hard-coded 110
```

Ces valeurs proviennent de l'**ancienne échelle de calibration** (0 = ouvert, 110 = fermé). Après recalibrage sur `-35 / 75` :

- `open_all` réglait 0° → converti en raw **511**, soit à peu près le milieu mécanique — les doigts ne s'ouvraient jamais
- `close_all` réglait 110° → borné par `base_max = 75`, il n'atteignait donc que 75, tandis que le libellé indiquait toujours 110°

### 2.2 La correction : un chemin direct vers la position raw

Le chemin par angle passe par le modèle d'interpolation `base/side`, qui ne peut pas atteindre exactement une valeur raw arbitraire (voir section 4). Les boutons globaux ont donc reçu un chemin qui écrit directement les positions raw des servos.

**Un détail d'implémentation important :** cela n'utilise *pas* `sync_write_raw_goal_position` de rustypot. La lecture du source généré par macro montre que l'API raw écrit `values.to_le_bytes()` directement sur le bus, tandis que l'API de conversion applique d'abord `to_be()` :

```rust
fn to_raw(value: f64) -> i16 { let a = (...) as i16; a.to_be() }
// sync_write_raw_*: values.iter().map(|v| v.to_le_bytes())   <- no to_be
```

Passer `451` émettrait donc `0xC301` (49921). À la place, le code utilise `sync_write_goal_position` (radians) et résout les radians qui tombent **exactement** sur la valeur raw cible, en prenant le milieu de chaque pas raw pour éviter l'erreur de troncature.

### 2.3 Cibles raw des trois boutons

Ajout de `raw_positions` à `data/config.yaml` (index 0 → ID de servo 1) :

```yaml
raw_positions:
  open:   [260, 760, 260, 760, 260, 760, 260, 760]
  close:  [760, 260, 760, 260, 760, 260, 760, 260]
  middle: [451, 571, 451, 571, 451, 571, 451, 571]
```

| Bouton | Action | IDs de servo 1–8 (raw) |
|---|---|---|
| ✋ Open All | entièrement étendus | 260, 760, 260, 760, 260, 760, 260, 760 |
| ✊ Close All | entièrement fermés | 760, 260, 760, 260, 760, 260, 760, 260 |
| ⊙ Center All | recentrage latéral (sans changement d'ouverture/fermeture) | — |
| **Position médiane** | **retour au milieu calibré** | 451, 571, 451, 571, 451, 571, 451, 571 |

> ⚠️ Les `raw_positions` sont des **valeurs de calibration propres à chaque main**. Le commentaire du fabricant lui-même est *« replace values by your calibration results »* — remesurez après avoir changé de main ou de servo.

### 2.4 Le compromis de la synchronisation des curseurs

Les cibles raw contournent le modèle `base/side`, elles n'ont donc pas d'équivalent exact en curseur. Après l'action d'un bouton, les curseurs sont réglés à l'entier le plus proche :

| Position | Affichage du curseur |
|---|---|
| open | base = −73, side = 0 |
| close | base = +73, side = 0 |
| middle | base = −17, side = 0 |

Le coût : toucher un curseur par la suite déplace la main de jusqu'à environ 1 unité raw (0.3°) par rapport à la cible. C'est délibéré — atteindre exactement la position calibrée importe davantage.

---

## 3. Nouveau bouton de position médiane

Placé à droite de `✋ Open All` / `✊ Close All` / `⊙ Center All`. Il ramène la main au **milieu mécanique calibré par le fabricant** (raw 451/571).

**Pourquoi il est nécessaire :** le point milieu entre `open_all` et `close_all` n'est *pas* le milieu mécanique. Le milieu du fabricant est `MiddlePos`, situé à ±60 raw (±17.6°) de raw 511. Après la mise sous tension, vous voulez un zéro bien défini et reproductible.

---

## 4. La GUI et la CLI divergent (le bug central)

### 4.1 Symptôme

**La même pose produit un mouvement de main différent selon qu'elle est appliquée avec `✓ Apply` de la GUI ou `--pose` de la CLI.**

### 4.2 Cause racine

La GUI appliquait les poses via :

```
set_positions(p1, p2)  →  decompose into (base, side), stored in the sliders
                       →  get_positions() recomputes via compute_auto_positions() in Auto mode
```

Mais `compute_auto_positions` n'est **pas** l'inverse exact de `decompose_servo_positions` (son centre et ses extrêmes sont des valeurs empiriques). La fonction `apply_pose()` de la CLI envoie les valeurs directement.

Mesuré : **12 poses sur 19 étaient déformées**, de jusqu'à 32° :

| Pose | Stocké | Réellement envoyé par la GUI | Écart |
|---|---|---|---|
| `ring_close` | Annulaire `(75, -35)` | Annulaire `(43, -5)` | **32° / 30°** |
| `middle_close` | Majeur `(75, -35)` | Majeur `(43, -5)` | **32° / 30°** |
| `pointer_close` | Index `(75, -35)` | Index `(43, -5)` | **32° / 30°** |
| `thumb_close` | Pouce `(75, -35)` | Pouce `(43, -5)` | **32° / 30°** |
| `wave1` | `(-75, -3)` | `(-75, 9)` | 12° |
| `hifive` | Pouce `(-75, -3)` | Pouce `(-75, 9)` | 12° |
| `greeting` | Annulaire `(-18, -57)` | Annulaire `(-10, -68)` | 8° / 11° |
| `victory` | Majeur `(-68, -9)` | Majeur `(-75, 1)` | 7° / 10° |
| `paper` | Index `(-52, -22)` | Index `(-59, -16)` | 7° / 6° |
| `ok` | Index `(36, 46)` | Index `(38, 43)` | 2° / 3° |

**Le schéma :** les poses symétriques où chaque doigt a `pos1 == pos2` (`open` `close` `stone` `two` `scissors` `one` `three`) font l'aller-retour exactement. Toutes les poses asymétriques impliquant un écartement latéral dérivent.

### 4.3 Correction

Ajout de `_send_exact_positions()`, qui envoie les angles directement aux servos dans l'ordre de `SERVO_PAIRS` (équivalent à `apply_pose` de la CLI). Les deux points d'entrée de poses l'utilisent désormais :

- le bouton `✓ Apply` dans Gestion des poses
- `_apply_pose_from_config()` — le lecteur de séquences et la liste de poses

Les curseurs sont toujours mis à jour par `set_positions()` pour l'affichage, mais **ne décident plus de ce qui est envoyé**.

### 4.4 Résultat

Après la correction, **les 19 poses satisfont `stored == GUI-sent == CLI-sent`**.

**Effet secondaire :** les gestes réels dans la GUI changent, en particulier les gestes asymétriques. C'est l'effet recherché de la correction.

---

## 5. Corrections des données de poses

### 5.1 Quatre poses `*_close` étaient mal écrites

```yaml
# Before — target finger (75, -35)
ring_close:    [75, -35, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, -35, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, -35, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, -35]
```

`(75, -35)` se décompose en `base = 20, side = -55` (hors plage) — ce qui signifie *« seulement 27 % fléchi, fortement décalé à gauche »*, et non « fermer ce doigt ». En cohérence avec `close` et `one`, la forme correcte est `(75, 75)` :

```yaml
# After — target finger fully closed (75, 75), others stay open (-35, -35)
ring_close:    [75, 75, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, 75, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, 75, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, 75]
```

Vérifié par décomposition : doigt cible `base = 75` (entièrement fermé), `side = 0` (ni d'un côté ni de l'autre).

**Impact :** la séquence `finger_roll`, qui utilise ces quatre poses, n'est désormais réellement un « roulement de chaque doigt l'un après l'autre ».

### 5.2 Le pouce dans `greeting` / `paper`

Les deux avaient à l'origine le pouce à `(75, 75)` (entièrement fermé). Pour `paper` (布, une paume ouverte et plate), un pouce fermé est manifestement faux.

`greeting` a d'abord été modifié en `(-75, -3)` (en réutilisant le pouce écarté de `hifive`), mais les tests matériels ont montré que cette étape nécessitait un débattement du pouce de **150°**, ce qui ne tient pas en 1.0 s (voir 6.3). État final :

```yaml
greeting: [-18, -57, -32, -32, -70, -7, -35, -35]   # thumb (-35, -35), same as open
paper:    [-19, -56, -34, -34, -52, -22, -75, -3]   # keeps the splayed thumb (flat palm)
```

Cela distingue les deux gestes : `greeting` est un salut, où le pouce s'ouvre simplement de façon naturelle ; `paper` est une paume plate, où le pouce s'écarte.

---

## 6. Lecteur de séquences : temporisation et diagnostics

### 6.1 Correction des faux avertissements « n'a pas atteint la cible »

L'exécution de `demo` sur le matériel a produit trois fausses alertes :

```
⚠ Pose #42 'greeting': Servos did not reach target! Max error: 52°
```

**Cause racine :** `_log_pose_completion` soustrayait deux tableaux qui étaient dans des **ordres différents**.

- `monitor_servos()` écrit son cache dans l'**ordre des ID de servo** : `latest_actual_positions[servo_id - 1] = ...` (index 0 = ID1 = Index)
- les `target_positions` transmises sont un tableau de pose, dans l'**ordre des widgets** Annulaire / Majeur / Index / Pouce (index 0 = Annulaire = ID5)

Il soustrayait donc la lecture de l'Index de la cible de l'Annulaire.

**Preuve** (recalcul à partir du journal mesuré) :

```
target (widget order)   : [-18, -57, -32, -32, -70, -7, -75, -3]
actual (servo-ID order) : [-68.85, -6.74, -33.69, -31.35, -18.46, -54.79, -74.12, -3.22]
compared as-is          -> max error 52°      <-- what the old code did
target reordered        : [-70, -7, -32, -32, -18, -57, -75, -3]
compared in servo order -> max error 2.21°    <-- actually spot on
```

**Correction :** ajout de `pose_to_servo_order()` / `servo_to_pose_order()`, appliquées avant la comparaison ; le `current` imprimé est reconverti pour que `target` et `current` s'alignent colonne par colonne dans le journal.

### 6.2 Correction du moment où la vérification d'atteinte s'exécute

L'original vérifiait après un délai **fixe de 2000 ms** après l'envoi :

```python
self.root.after(2000, lambda ...: self._log_pose_completion(...))
```

Mais les étapes de séquence n'attendent que 1.0 s, donc au moment où la vérification s'exécutait, l'étape suivante avait déjà été envoyée — la lecture appartient nécessairement au mouvement *suivant* :

```
25.388  Pose #40 'ok'      sent
26.782  Pose #41 'victory' sent        <- already moved on
27.742  Pose #40 'ok'      checked -> reading is mid-way to victory
```

**Correction :**

1. `_apply_pose_from_config` a reçu un paramètre `check_after`. Un clic sur `✓ Apply` pour une pose unique reste inchangé (2.0 s, puis attente de l'arrêt du mouvement) ; la lecture de séquence passe **le délai propre à l'étape**, de sorte que la vérification tombe sur la frontière de l'étape (délai − 100 ms) et n'attend plus la fin du mouvement.
2. Ajout d'une **garde de remplacement** : `_log_pose_start` enregistre `current_pose_id` ; si une commande plus récente a pris le relais entre-temps, la vérification d'atteinte est ignorée et le journal affiche `current=<superseded>`.

### 6.3 Réglage des délais de séquence

**Vitesse effective** recalculée à rebours à partir du journal matériel (la vitesse 3 est nominalement 172°/s) :

| Pose | Débattement | Erreur à 0.9 s | Vitesse effective implicite |
|---|---|---|---|
| `ok` | 110° | 0.5° | 121.7°/s (71 % du nominal) |
| `victory` | 110° | 1.0° | 121.1°/s (70 %) |
| `greeting` | 132° | 7.0° | 138.9°/s (81 %) |

> En charge, la vitesse réelle n'atteint qu'environ **70 %** du nominal. C'est ce chiffre qui compte au moment de choisir les délais.

**Modifications de `demo` :**

```yaml
  demo:
    steps:
    - open:3,3,3,3,3,3,3,3|2.0s
    - close:6,6,6,6,6,6,6,6|2.0s
    - ok:3,3,3,3,3,3,3,3|1.0s
    - victory:3,3,3,3,3,3,3,3|1.0s
    - greeting:3,3,3,3,3,3,3,3|1.5s      # was 1.0s
    - close:6,6,6,6,6,6,6,6|2.0s         # new: settle back into a fist
```

- `greeting` 1.0 s → **1.5 s** : cette étape parcourt 132° (deuxième servo de l'Annulaire) et ne peut pas se terminer en 1.0 s
- **nouveau `close` final** : ainsi `demo` se termine main fermée, ce qui rend aussi la boucle propre
- durée totale 7.0 s → **9.5 s**

### 6.4 `wave` : limiter le balancement latéral à ±30°

Le `wave_r` / `wave_l` d'origine impliquait un `side` de **±36** (au-delà de la limite ±35, donc il était borné à 35).

En résolvant `side = base − pos1`, `base = (pos1 + pos2) / 2`, on obtient `pos1 = base − side`, `pos2 = base + side`. En gardant `base = −39` et en réduisant `side` à ±30 :

```yaml
wave_r: [-9, -69, -9, -69, -9, -69, -69, -9]     # was [-3, -75, -3, -75, -3, -75, -75, -3]
wave_l: [-69, -9, -69, -9, -69, -9, -9, -69]     # was [-75, -3, -75, -3, -75, -3, -3, -75]
```

Vérifié : `wave_r` a pour side `[-30, -30, -30, +30]`, et `wave_l` en est le miroir doigt par doigt.

**Effet secondaire (attendu) :** le débattement de chaque balancement passe aussi de 40°/72° à **34°/60°**. La vague est globalement plus étroite, ce qui ne fait qu'élargir la marge de temporisation.

---

## 7. Nouvelle ligne de position raw dans le retour des servos

Une ligne **`Current (0-1023)`** se trouve juste en dessous de `Position (°)`, affichant la position raw du servo en direct.

```
1. Goal (°)
2. Position (°)
3. Current (0-1023)      <== new
4. Speed (°/s)
5. Torque (%)
6. Voltage (V)
7. Current (mA)
8. Temperature (°C)
9. Status
10. Moving
```

**Compromis :** aucune lecture série supplémentaire. La valeur raw est dérivée de la position que le thread de supervision a **déjà** lue, de sorte que la boucle d'interrogation ne double pas son trafic série. La précision a été vérifiée de manière exhaustive : **2048 combinaisons (raw 0–1023 × servo impair/pair) font l'aller-retour sans aucune erreur**.

**Utilisation :** comparez directement à la calibration du fabricant — `open` doit afficher `260 / 760` en alternance, `middle` doit afficher `451 / 571`.

> Le nom de la ligne comporte un préfixe de plage pour le distinguer du `Current (mA)` existant (courant consommé estimé).

---

## 8. Prise en charge des mains gauche et droite

### 8.1 Le fabricant fournit deux firmwares

Le fabricant fournit une démo Arduino distincte par main, avec des paramètres totalement différents :

| | Droite `Amazing_RHand_Demo` | Gauche `Amazing_LHand_Demo` |
|---|---|---|
| IDs de servo | **1–8** | **11–18** |
| Doigt → ID | index `1,2` / majeur `3,4` / annulaire `5,6` / pouce `7,8` | **annulaire `11,12` / majeur `13,14` / index `15,16` / pouce `17,18`** |
| `MiddlePos` central | `[451, 571, 451, 571, …]` | `[571, 451, 571, 451, …]` |

Le tutoriel de débogage indique clairement : *« une seule main utilise 8 servos ; les ID de la main droite doivent être réglés sur 1-8, et ceux de la main gauche sur 11-18. »*

Notez que la numérotation de la main gauche est **inversée** (l'annulaire en premier) — ce qui correspond à sa disposition mécanique en miroir.

### 8.2 Pourquoi changer les ID ne suffit pas

Les ID ne sont que la première couche. Deux différences physiques subsistent entre les mains, et en négliger une seule déforme les gestes.

#### Différence 1 : un décalage de montage de 35.16°

Les deux mains utilisent **la même valeur de geste plus leur propre `MiddlePos`** :

```c
// Right
#define MiddlePos {451, 571, ...}
Move_Index(-35, 35)  →  ID1 = 451 + (-35)/0.293 = 331.5

// Left
#define MiddlePos {571, 451, ...}
Move_Index(-35, 35)  →  ID15 = 571 + (-35)/0.293 = 451.5
```

Le même geste « open » tombe sur des valeurs raw différentes sur chaque main. Converti dans l'espace d'angles de ce programme, ils diffèrent de **120 raw = 35.16°**.

#### Différence 2 : les deux servos d'un doigt sont permutés

```c
// Right Victory                      // Left Victory
Move_Index (-15, 65);                Move_Index (-65, 15);
Move_Middle(-65, 15);                Move_Middle(-15, 65);
```

Par doigt, `(a, b) → (-b, -a)` ; en valeurs de pose, cela signifie **permuter les deux nombres de chaque doigt**.

Oubliez cela et la **direction d'écartement s'inverse** — le symptôme est un signe V qui replie ses deux doigts tandis que les doigts qui devraient être joints s'écartent.

> Une erreur de lecture facile : dans `Perfect`, les valeurs de l'index et du majeur sont **identiques** sur les deux mains (`(50,-50)`, `(0,0)`), et seul le pouce diffère. La règle n'est donc pas « permuter index et majeur » mais un `(-b,-a)` par doigt — qui est l'identité pour les paires symétriques.

### 8.3 Mise en œuvre

**Les deux mains partagent un seul `hand_config.yaml`.** Les poses stockées sont toujours dans l'**ordre de la main droite** ; la main gauche convertit à l'aller et au retour, il n'y a donc pas de seconde bibliothèque de poses à maintenir.

La conversion réside dans `hand_logic.py` :

| Fonction | Rôle |
|---|---|
| `resolve_hand_config(app_config, hand)` | Superpose `hands.<name>` sur la configuration de premier niveau (main droite) |
| `servo_pairs()` / `servo_ids()` | Les `(servo1_id, servo2_id)` de cette main par doigt / tous les ID de servo par ordre croissant |
| `hand_angle_offset()` / `hand_mirrors_pose()` | Lisent les deux paramètres de différence de la main |
| `adapt_pose_for_hand(positions, mirror)` | Permute les `(pos1, pos2)` de chaque doigt. **La permutation est son propre inverse**, donc la même fonction convertit à l'application et reconvertit à l'enregistrement |

**Intégré dans :**

- GUI : application de pose (le bouton `✓ Apply` et la lecture de séquence), et enregistrement d'une pose
- CLI : `--pose` / `--sequence`

**Les cibles raw des trois boutons globaux** sont configurées par main et ne passent pas par cette conversion (`raw_positions` est écrit sous `hands.left`).

### 8.4 Utilisation

La GUI demande avant de s'ouvrir :

```
  AmazingHand — which hand?
    1 = right hand  (servo IDs 1-8)
    2 = left hand   (servo IDs 11-18)
  Enter 1 or 2 [1]:
  LEFT hand — servo IDs 11-18
    Ring (11, 12)  Middle (13, 14)  Pointer (15, 16)  Thumb (17, 18)
    middle position raw: [571, 451, 571, 451, 571, 451, 571, 451]
```

Appuyer sur Entrée utilise la valeur `hand:` de `config.yaml`. Pour ignorer l'invite :

```bash
python amazing_hand_gui.py --hand left
python amazing_hand_cmd.py --pose victory --hand left
```

### 8.5 Liste de vérification initiale pour la main gauche

Dans `hands.left.raw_positions`, seul **middle** est la valeur par défaut du fabricant (`571, 451`) ; `open` et `close` ont été dérivés de la démo du fabricant :

| Bouton | Raw main gauche | Source |
|---|---|---|
| Position médiane | `571, 451, …` | Valeur par défaut du fabricant |
| Open All | `380, 642, …` | Dérivé : le même geste que Open All de la main droite, appliqué au `MiddlePos` gauche |
| Close All | `880, 142, …` | Idem |

**Vérifiez-les dans cet ordre la première fois que vous connectez la main gauche :**

1. Appuyez sur **Position médiane** et confirmez que la ligne `Current (0-1023)` affiche `571, 451, 571, 451, …`
2. Appuyez sur **Open All** / **Close All** — le débattement doit atteindre les butées sans caler
3. Essayez `victory` (index et majeur ouverts en V), `greeting` (trois doigts joints), `ok` (les bouts du pouce et de l'index qui se touchent)

Si quelque chose ne va pas :

| Symptôme | Modification |
|---|---|
| La position médiane est fausse | `hands.left.raw_positions.middle` |
| Direction d'écartement inversée | réglez `hands.left.mirror_pose` sur `false` |
| Débattement trop court ou trop long | `hands.left.raw_positions.open` / `close` |

### 8.6 Si votre main gauche est numérotée 1-8

Certaines personnes renumérotent les servos de la main gauche en 1–8. Dans ce cas, seul `hands.left.servos` doit être modifié :

```yaml
hands:
  left:
    servos:
      # Renumbered following the vendor's left-hand order: ring first
      ring:    [1, 2]
      middle:  [3, 4]
      pointer: [5, 6]
      thumb:   [7, 8]
      all_ids: [1, 2, 3, 4, 5, 6, 7, 8]
```

> `angle_offset` et `mirror_pose` **ne changent pas** — ils décrivent la construction mécanique, et non la numérotation des ID. L'inversion des servos pairs s'applique toujours également, car la paire de chaque doigt conserve « l'ID impair en premier ».

---

## 9. Détection automatique du port série

### 9.1 Le problème

L'original codait en dur la liste des ports Windows de `COM1` à `COM20` :

```python
available_ports = [f'COM{i}' for i in range(1, 21)]
```

Mais un adaptateur peut se retrouver sur n'importe quel numéro de port (cette machine a mesuré `COM243`). Résultat : **votre port est tout simplement absent de la liste déroulante**, et la connexion automatique retombe sur une valeur par défaut configurée qui n'existe pas, échouant avec « the system cannot find the file specified ».

### 9.2 Correction

Ajout de `available_serial_ports()`, avec repli par étapes :

1. `list_ports.comports()` de pyserial (utilisé s'il est installé — informations les plus riches)
2. Windows sans pyserial : lecture de la clé de registre `HARDWARE\DEVICEMAP\SERIALCOMM` (**bibliothèque standard uniquement**, aucune nouvelle dépendance)
3. Linux/macOS : glob `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`, `/dev/cu.usb*`
4. Uniquement si tout ce qui précède échoue, repli sur la liste de candidats d'origine

Les ports sont triés de manière **naturelle**, donc `COM2` vient avant `COM10`.

### 9.3 Changements associés

- La liste déroulante est passée de `readonly` à **modifiable** — vous pouvez saisir un port lorsque la détection le manque
- Si la valeur par défaut configurée n'est pas présente, la GUI **démarre sur le premier port qui existe réellement** au lieu d'essayer une valeur par défaut absente
- **Un `--port` explicite n'est jamais écrasé** par ce repli (suivi via `port_was_explicit`)

---

## 10. Référence de configuration

### `data/config.yaml`

Les `servos` / `auto_extremes` / `raw_positions` de premier niveau décrivent la **main droite** et servent de valeurs par défaut ; `hands.<name>` les superpose clé par clé.

```yaml
hand: right           # active hand: right | left (the GUI asks; --hand skips it)

limits:
  servo_min: -75      # absolute lower travel limit
  servo_max: 75       # absolute upper travel limit
  base_min: -75       # open/close slider range (-75 = fully open)
  base_max: 75        #                          ( 75 = fully closed)
  side_min: -35       # left/right slider range
  side_max: 35

auto_extremes:        # servo positions at the side slider's extremes — right hand
  left_open:  [32, -35]
  right_open: [-35, 32]
  left_closed:  [75, 75]
  right_closed: [75, 75]

raw_positions:        # global buttons' raw targets — right hand (index 0 → servo ID 1)
  open:   [260, 760, ...]
  close:  [760, 260, ...]
  middle: [451, 571, ...]

hands:
  left:               # overrides for the left hand; only list what differs
    servos:
      ring:    [11, 12]
      middle:  [13, 14]
      pointer: [15, 16]
      thumb:   [17, 18]
    raw_positions:    # index 0 → servo ID 11
      open:   [380, 642, ...]
      close:  [880, 142, ...]
      middle: [571, 451, ...]
    angle_offset: -35.16   # mounting offset (see 8.2)
    mirror_pose: true      # per-finger servo swap (see 8.2)
```

`auto_extremes` est **partagé** par les deux mains — le curseur latéral se comporte de la même manière dans l'espace des poses ; une main en miroir s'écarte simplement dans l'autre sens physiquement.

### `data/hand_config.yaml`

Les 8 valeurs d'une pose sont ordonnées **Annulaire, Majeur, Index, Pouce** (paires de servos `(5,6) (3,4) (1,2) (7,8)`), et **non** par ID de servo.

**Ce fichier est partagé par les deux mains et toujours stocké dans l'ordre de la main droite.** La main gauche permute la paire de chaque doigt à l'application, et permute en retour à l'enregistrement.

> ⚠️ La docstring en tête de `amazing_hand_cmd.py` prétend « index 0→servo1 … 7→servo8 ». Ce commentaire est **faux** ; l'ordre ci-dessus est ce que le code fait réellement.

---

## 11. Résultats mesurés

### Précision d'atteinte (après les corrections)

| Pose | Cible | Réel | Erreur max |
|---|---|---|---|
| `open` | tous −35 | −36.6 … −33.4 | ≤1.6° |
| `close` | tous 75 | 74.7 … 75.3 | ≤0.3° |
| `ok` | — | — | 0.5° |
| `victory` | — | — | 1.0° |
| `greeting` | — | — | 2.2° |

### Vérifications de conversion

```
raw -> degrees -> raw: 2048 combinations, zero error
open    raw [260, 760] -> back [260, 760]
middle  raw [451, 571] -> back [451, 571]
close   raw [760, 260] -> back [760, 260]
```

### Problèmes connus restants

- **`ok` et `victory` dans `demo` n'ont presque aucune marge de temporisation** (+0.01 s selon la vitesse mesurée). Ils passent actuellement uniquement parce que la tolérance < 5° les rattrape. Une baisse de la tension de batterie, un changement de température ou une main légèrement plus rigide pourrait les faire échouer. Augmenter les deux délais de 1.0 s à 1.2 s est l'étape suivante évidente.
- **`scissors` est identique octet pour octet à `two`**, et **`stone` est identique octet pour octet à `close`**. Sémantiquement acceptable (scissors = deux doigts, stone = poing) mais littéralement dupliqué, et non nettoyé.
- **Les curseurs conservent une erreur de représentation d'environ 0.3°** par rapport aux cibles raw (voir 2.4).
- **`config.yaml` et le `default_config` de `hand_logic.py` sont désynchronisés.** Ce dernier porte encore l'échelle d'origine (`servo_min: -40` etc.) ; il n'est utilisé que lorsque `config.yaml` est absent. Le test `test_hand_logic.py::TestAngleLimits::test_defaults` vérifie exactement ces anciennes valeurs par défaut.

---

## 12. Résumé fichier par fichier

| Fichier | Modifications |
|---|---|
| `hand_logic.py` | Nouvelles constantes de conversion SCS0009 ; `raw_to_degrees` / `raw_to_radians` / `degrees_to_raw` / `pose_to_servo_order` / `servo_to_pose_order` ; format d'affichage `raw_position` ; valeurs par défaut de `raw_positions` ; **prise en charge des mains** (`HAND_NAMES` / `DEFAULT_HAND_SERVOS` / `resolve_hand_config` / `servo_pairs` / `servo_ids` / `hand_angle_offset` / `hand_mirrors_pose` / `adapt_pose_for_hand`) ; **`available_serial_ports()`** ; E/S du fichier de configuration passées en **UTF-8** (il utilisait la valeur par défaut GBK de Windows et plantait sur les commentaires non ASCII) |
| `amazing_hand_gui.py` | Nouveaux `_apply_raw_hand_position` / `middle_all` / `_send_exact_positions` ; réécriture de `open_all` / `close_all` / `_apply_pose_from_config` / `_log_pose_completion` ; nouveau bouton **Position médiane** ; nouvelle ligne de position raw dans le retour des servos ; `self.app_config` promu en attribut d'instance ; suppression du `latest_goal_positions` inutilisé et unification de l'ordre d'écriture de `feedback_data['goal']` ; **sélection de la main au démarrage + `--hand`** ; **8 `range(1,9)` codés en dur remplacés par les ID réels de la main** ; le titre de la fenêtre affiche la main active ; décalage d'angle et conversion miroir intégrés dans chaque chemin de pose ; **la liste déroulante des ports énumère désormais les ports détectés et accepte la saisie** |
| `amazing_hand_cmd.py` | Nouveau `--hand` ; `connect` / `apply_pose` / `wait_for_motion` / coupure du couple à la sortie utilisent désormais les ID réels de la main ; les chemins de pose et de séquence appliquent le décalage d'angle et la conversion miroir ; lecture de la configuration passée en UTF-8 |
| `data/config.yaml` | `limits` / `auto_extremes` recalibrés ; ajout de `raw_positions` ; ajout de `hand` et d'un bloc de surcharge `hands.left` |
| `data/hand_config.yaml` | Les 19 poses remises à l'échelle ; les quatre poses `*_close` corrigées ; le pouce de `greeting` / `paper` corrigé ; le balancement `wave_r` / `wave_l` réduit à ±30 ; `demo` a reçu un délai `greeting` plus long et une nouvelle étape de fermeture |
| `pyproject.toml` | `build-backend` corrigé (`setuptools.backends.legacy:build` → `setuptools.build_meta`) |

### Glossaire

| Terme | Signification |
|---|---|
| **Mode Auto** | Deux curseurs — « base » (ouverture/fermeture) et « side » (latéral) — pilotent indirectement les deux servos d'un doigt |
| **Mode Raw** | Les deux angles de servo d'un doigt sont contrôlés directement |
| **base** | Quantité d'ouverture/fermeture, `(pos1 + pos2) / 2` |
| **side** | Décalage latéral, `base − pos1` |
| **raw** | L'unité de position interne du servo : 0–1023 sur 300°, centre 511 |
| **MiddlePos** | La calibration du milieu par servo du firmware du fabricant ; diffère entre les mains (voir 8.1) |
| **angle_offset** | Le décalage de montage de 35.16° entre les mains (voir 8.2) |
| **mirror_pose** | La permutation de paire de servos par doigt de la main gauche (voir 8.2) |
