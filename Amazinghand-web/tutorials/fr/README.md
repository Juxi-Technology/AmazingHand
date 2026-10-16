[Deutsch](../de/README.md) | [English](../en/README.md) | [Español](../es/README.md) | Français | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (Brasil)](../pt-br/README.md) | [Português (Portugal)](../pt-pt/README.md) | [简体中文](../zh-hans/README.md) | [繁體中文](../zh-hant/README.md)

# Contrôle web AmazingHand

Pilotez la main dextre AmazingHand depuis un navigateur — **main gauche ou droite**, avec deux façons de la commander :

- **Manuel** — 8 curseurs de servo + 19 poses prédéfinies + retour au milieu en un clic
- **Téléopération caméra** — MediaPipe s'exécute localement dans le navigateur et projette votre main sur les doigts en temps réel (la vidéo ne quitte jamais la machine)
- **Interface bilingue** — basculez entre chinois et anglais dans le coin supérieur droit ; le navigateur mémorise le choix

La table des servos, la bibliothèque de poses et les formules de conversion sont alignées sur
[AmazingHandControl](https://github.com/pollen-robotics/AmazingHand) (l'interface officielle).

---

## Démarrage rapide

Ouvrez un terminal et placez-vous dans le dossier Amazinghand-web :

```bash
pip install -r requirements.txt

python server.py --no-connect   # recommandé : démarrez le serveur, choisissez le port dans la page (rien ne bouge)

# python server.py                # détecte automatiquement le port série et se connecte
# python server.py --port COM9    # utilise un port précis
# python server.py --hand left    # active uniquement la main gauche
# python server.py --dry-run      # aucun port série, interface uniquement
```

Ouvrez ensuite **http://localhost:8000** dans un navigateur.

### Choisir le port série dans la page

Le haut de la page comporte une barre de ports :

```
Port  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [Refresh]  [Connect]  [Disconnect]  Connected to COM3
```

- La liste déroulante énumère tous les ports série de la machine. Les puces USB-série courantes (CH34x / CP210x / FTDI …) sont marquées **★** et placées en tête
- **Refresh** relance le scan (à utiliser après avoir branché la carte)
- **Connect** ouvre le port sélectionné ; la main revient au milieu juste après
- **Disconnect** relâche d'abord le couple, pour que les servos ne restent pas verrouillés en place
- Pour changer de port, il suffit de sélectionner le nouveau et de cliquer sur Connect — l'ancien port est fermé automatiquement

> **`--no-connect` est conçu pour ce flux** : le serveur démarre sans toucher à aucun port série,
> il ne peut donc pas attraper le mauvais et faire sursauter la main. Retirez l'option si vous voulez qu'il se connecte au démarrage.

Les journaux série vont dans `server.log` (si vous lancez via un `.bat`, la fenêtre disparaît aussitôt — lisez plutôt le fichier).

### Vérification du câblage

Liste les ID de servos détectés et les vérifie main par main par rapport à `config.json`.

```bash
python tools/scan_servos.py --port COM9
```

Remplacez COM9 par votre port réel.

---

## Mapping des servos

Source : `DEFAULT_HAND_SERVOS` dans `AmazingHandControl/hand_logic.py` et
`docs/zh-hans/CONFIG_FORMAT.md`.

| Doigt | ID main droite | ID main gauche |
|---|---|---|
| Annulaire | 5, 6 | 11, 12 |
| Majeur | 3, 4 | 13, 14 |
| Index | 1, 2 | 15, 16 |
| Pouce | 7, 8 | 17, 18 |

### Les deux servos d'un doigt ont des rôles distincts ⚠️

```
servo1 (ID impair) = axe de flexion    ouvert ↔ fermé
servo2 (ID pair)   = axe d'écartement  doigts serrés ↔ doigts écartés
```

L'interface affiche exactement ces deux axes. **« Le doigt ne s'écarte pas / ne se referme pas » signifie que l'axe d'écartement ne bouge pas** —
un V en ciseau vient de l'écartement de l'index `+17` et de celui du majeur `−30` (un positif, un négatif).

Ils sont combinés sur le bus :

```
servo1 = flexion + écartement
servo2 = flexion − écartement
```

Plage (déduite des 19 poses officielles plus le milieu) :

| Axe | Plage | Signification |
|---|---|---|
| Flexion | −50 ~ +90 | ouvert (négatif) ↔ fermé (positif) |
| Écartement | −45 ~ +45 | serré (négatif) ↔ écarté (positif) |

**Deux règles sur les ID** (s'y tromper grille des servos ou inverse le mouvement) :

1. **Les ID impairs sont le premier servo d'un doigt, les ID pairs le second.** Vrai sur les deux mains
   (à gauche, 11/12, 13/14 … alternent aussi). Le second servo est **monté à l'envers**, il faut donc lui mettre un signe − dans la conversion.
2. **La main gauche n'est pas en 9–16, mais en 11–18, numérotée annulaire en premier.** La câbler en 1–8 à la suite est toujours faux.

![Both_Hands-IDs](../../Both_Hands-IDs.jpg)

---

## Conversion

Identique à `apply_pose()` dans `AmazingHandControl` (vérifié pose par pose) :

```
1) lorsque mirror_pose vaut true, échangez d'abord les deux valeurs de servo de chaque doigt
2) servo_deg = (ID impair ? +1 : -1) × (valeur de pose − angle_offset_deg)
```

| Main | angle_offset_deg | mirror_pose |
|---|---|---|
| Droite | `0` | **oui** ⚠️ |
| Gauche | `-35.16` | oui |

`-35.16°` est le décalage physique d'un demi-crant des palonniers de servo de la main gauche par rapport à la droite, tiré de la configuration officielle.

> **À propos de `mirror_pose` — cette version diffère de l'officielle**
>
> Dans la référence officielle, seule la main gauche est à `true`. **Le module de main droite de cette version
> a lui aussi ses paires de servos montées à l'envers**, donc la main droite est également à `true`.
>
> L'échange n'inverse que l'**écartement**, jamais la flexion : `base = (a+b)/2` est inchangé par un échange, tandis que
> `side = (a−b)/2` change de signe. Donc si l'écartement d'une main ressort en miroir, c'est le premier interrupteur à vérifier.

Le tableau de pose comporte toujours 8 valeurs dans l'ordre **`[annulaire, majeur, index, pouce]`**, deux par doigt —
identique octet pour octet au `data/hand_config.yaml` officiel, ce qui permet de les comparer directement.

### Exemples concrets

| Pose | Droite | Gauche |
|---|---|---|
| `open` `[-35]*8` | ID5 **−35** / ID6 **+35** | ID11 **+0.16** / ID12 **−0.16** |
| `close` `[75]*8` | ID5 **+75** / ID6 **−75** | ID11 **+110.16** / ID12 **−110.16** |
| milieu `[-17.578]*8` | ID5 **−17.58** / ID6 **+17.58** | ID11 **+17.58** / ID12 **−17.58** |

> **À noter que le `close` de la main gauche demande ±110.16°**, bien au-delà de la droite. C'est pourquoi `config.json`
> fixe la limite à **±120°** (la plage complète du SCS0009 est d'environ ±150°). Une limite à ±90 rognerait le poing de la main gauche.

---

## Poses prédéfinies (19)

| Pose | | Pose | |
|---|---|---|---|
| `open` | Ouverte | `wave1` | Salut |
| `close` / `stone` | Poing | `wave_r` / `wave_l` | Balayage droite / gauche |
| `ok` | OK | `ring_close` | Annulaire seul |
| `greeting` | Salutation | `middle_close` | Majeur seul |
| `victory` / `two` / `scissors` | Victoire / Deux | `pointer_close` | Index seul |
| `paper` | Feuille | `thumb_close` | Pouce seul |
| `one` / `three` | Un / Trois | `hifive` | High five |

Pour modifier une pose, éditez la section `poses` de `config.json` ; les clés correspondent aux noms du YAML officiel.

### La gauche et la droite peuvent utiliser des valeurs différentes

Dans une pose, `positions` est **partagé par les deux mains**. Si une main a besoin d'un jeu différent à cause de
différences d'assemblage mécanique, ajoutez une clé `right` ou `left` à cette entrée et elle remplace `positions` :

```jsonc
"close": {
  "label": "Fist",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // partagé par les deux mains
  "right":     [ ... 8 valeurs ... ]                // optionnel : main droite uniquement
}
```

---

## Deux modes

| Mode | Comportement |
|---|---|
| **Main droite** | Envoie uniquement aux 8 servos de la main droite |
| **Main gauche** | Envoie uniquement aux 8 servos de la main gauche (miroir + décalage de −35.16° appliqués automatiquement) |

Une seule main à la fois. Les deux mains sont sur le même bus ; changez de main avec **Target** en haut.
Le changement ne perturbe pas l'autre main — elle conserve sa pose sur place.

---

## Téléopération caméra

Les points de repère de main (landmarks) MediaPipe s'exécutent localement dans le navigateur (ressources sous `web/mediapipe/`, utilisables hors ligne).
Les 21 landmarks sont convertis en valeurs de pose pour 4 doigts et envoyés en flux à la main sélectionnée.

### 1. Capturez d'abord trois poses

Lancez la caméra, puis placez votre main dans la pose voulue et cliquez sur le bouton de capture correspondant (environ 1 seconde de moyennage).
L'ordre n'a pas d'importance ; recliquez sur le même bouton pour recapturer. **Le statut ne passe au vert qu'une fois les trois enregistrées** —
rien n'est envoyé avant, la main reste donc au milieu.

| Bouton | Pose | Fournit |
|---|---|---|
| ① Écartés | Doigts tendus et écartés, pouce pointé vers l'extérieur | L'extrémité « tendu » de la flexion + l'extrémité « écarté » de l'écartement |
| ② Serrés | Doigts tendus et serrés, pouce contre l'index | L'extrémité « serré » de l'écartement |
| ③ Poing | Serrez le poing, pouce replié vers la paume | L'extrémité « fermé » de la flexion |

### 2. Chaque axe est une droite définie par deux points mesurés

Flexion et écartement utilisent tous deux **deux extrémités mesurées pour définir une droite** :

```
t      = (valeur mesurée − extrémitéA) / (extrémitéB − extrémitéA)      // borné à 0..1
cible  = A.cible + (B.cible − A.cible) × t
```

Le gain : **le signe de la mesure de chaque doigt est absorbé automatiquement** — il n'y a donc aucune case
« inverser ce doigt » à cocher. (L'index et l'annulaire sont de part et d'autre de l'axe central, et la chaîne
d'articulations du pouce diffère, donc leurs directions sont bel et bien opposées — deux extrémités mesurées les absorbent.)

Les cibles des extrémités se trouvent dans la section `camera` de `config.json` :

| Axe | Extrémités | Annulaire | Majeur | Index |
|---|---|---|---|---|
| Flexion | tendu → poing | −50 → 90 | −50 → 90 | −50 → 90 |
| Écartement | serré → écarté | −45 → +45 | 0 → 0 | +45 → −45 |

Les deux extrémités d'écartement valent 0 pour le majeur (il ne s'écarte pas latéralement).

### 3. Le pouce ne fait que fléchir ⚠️

Le CMC du pouce est une **articulation en selle (opposable)**, et sa flexion est fortement couplée à l'abduction —
pouce replié contre l'index, il est déjà dans une position d'écartement, donc la « flexion zéro » mesurée là est faussée.
Le forcer sur deux axes et les deux ressortent faux.

Le pouce ne fait donc **que fléchir ; son écartement est toujours à 0** (ses deux servos reçoivent la même valeur). Les deux
poses de référence dont il a besoin sont ① (pointé vers l'extérieur) et ③ (pointé vers la paume) — rien de plus à capturer.

### 4. L'écartement s'estompe à mesure que le doigt se replie

L'écartement final est mis à l'échelle par :

```
side = side_measured × (1 − curl)
```

`splayDeg` est la projection de la direction MCP→PIP sur l'axe latéral de la paume, et la flexion du doigt
**tourne précisément autour de cet axe** — au-delà d'un certain repli, la projection change de signe et l'« écartement »
mesuré bascule soudainement à l'autre extrémité.

Sans cette atténuation, ce basculement se propage via `servo2 = flexion − écartement` et entraîne le **servo d'ID pair**
en marche arrière. (L'ID impair reçoit `flexion + écartement`, il part donc dans le même sens, juste plus vite — c'est invisible.)
Le symptôme est « à mi-chemin du poing, les servos 12 et 16 se mettent soudain à l'envers » — 12 est le servo d'écartement
de l'annulaire gauche et 16 celui de l'index gauche, précisément les deux dont les cibles d'écartement sont non nulles.

Avec l'atténuation, l'écartement est **exactement 0** au repli complet, quelle que soit la folie de la mesure.
Et un poing, de toute façon, c'est des doigts serrés.

### 5. Couleurs du squelette

| Doigt | Couleur |
|---|---|
| Pouce | orange |
| Index | rouge |
| Majeur | bleu |
| Annulaire | jaune |
| Auriculaire | gris sombre |
| Os de la paume | gris neutre |

L'auriculaire ne sert pas à la reconnaissance des gestes, mais son **MCP de base (landmark 17) définit le repère de la paume
de la main droite**, on ne peut donc pas simplement le supprimer.

### Aide-mémoire de réglage

| Ce que vous voulez changer | Où |
|---|---|
| Valeurs cibles des axes | section `camera` de `config.json` |
| **L'écartement gauche et droite va en sens opposé** | passez cette main à `-1` dans `camera.side_sign` (`1` = inchangé) |
| Fluidité | `SMOOTH` dans `tracking.js` (défaut 0.35 ; plus bas = plus stable mais plus retardé) |
| Vitesse à laquelle un repli est détecté | recapturez les trois poses |

`side_sign` s'applique à la main sélectionnée sous **Target**. Modifiez-le et rechargez la page —
aucun redémarrage du serveur nécessaire :

```jsonc
"side_sign": { "right": 1, "left": -1 }   // inverse tout l'axe d'écartement sur la main gauche
```

La flexion n'est pas affectée par `side_sign`.

---

## Arborescence du projet

```
Amazinghand-web/
├── config.json          mapping des servos / bibliothèque de poses / séquences / limites (généré depuis le YAML officiel)
├── server.py            backend : série + fichiers statiques + WebSocket
├── requirements.txt
├── README.md            anglais (document d'origine)
├── tutorials/           de · en · es · fr · it · ja · ko · pt-br · pt-pt · zh-hans · zh-hant
├── tools/
│   └── scan_servos.py   scanne le bus à la recherche de servos et vérifie leurs ID
└── web/
    ├── index.html · app.js · tracking.js · style.css
    ├── i18n.js          chaînes de l'interface (dictionnaire chinois/anglais + le sélecteur en haut à droite)
    └── mediapipe/       ressources MediaPipe (embarquées localement, hors ligne, ~42 MB)
```

Protocole frontend/backend :

```jsonc
// du frontend vers le backend   target: "left" | "right"
{ "cmd": "ports" }                                  // relance le scan des ports série
{ "cmd": "connect",    "port": "COM3" }
{ "cmd": "disconnect" }
{ "cmd": "target", "target": "left" }
{ "cmd": "set",    "target": "left", "angles": { "pointer": [0, 0], ... } }
{ "cmd": "pose",   "target": "left", "name": "close" }
{ "cmd": "middle", "target": "left" }
{ "cmd": "torque", "target": "left", "on": true }
{ "cmd": "stop" }

// du backend vers le frontend
{ "type": "state", "hands": {...}, "poses": {...}, "positions": {...},
  "axes": {...}, "camera": {...}, "target": "left",
  "limits": {...}, "port": { "available": [...], "current": "COM3", "connected": true } }
{ "type": "ports" | "connected" | "disconnected", "ports": [...], ... }
{ "type": "error", "msg": "connect COM_FAKE failed: the system cannot find the file specified." }
```

---

## Sécurité

| Élément | |
|---|---|
| **Limites de pose** | ±120° (`limits` dans `config.json`) ; les 19 poses ont été vérifiées pour rester dans les limites |
| **Déduplication des changements** | les variations inférieures à 0.5° ne sont pas envoyées, pour ne pas saturer le bus de bruit |
| **Limitation des écritures** | minimum 20 ms entre deux écritures |
| **Arrêt d'urgence** | le bouton rouge de l'interface relâche tous les servos d'un coup |
| **Protection à la sortie** | le couple est relâché automatiquement sur Ctrl+C |
| **Débogage main unique** | `--hand left/right` |

---

## Dépannage

**Le mouvement est inversé** → vérifiez que le câblage respecte « ID impair en premier » ; sur la main gauche, confirmez aussi `angle_offset_deg = -35.16`.

**Le poing de la main gauche est trop petit / les servos sifflent** → la limite est probablement encore à ±90 ; vérifiez que `config.json` est bien à ±120.

**Un doigt ne bouge pas / « expected N motors, found M »** → lancez `tools/scan_servos.py` ; les ID de la main gauche sont les plus faciles à mal câbler.

**La position médiane est décalée** → la valeur médiane `-17.578125` est convertie depuis le brut officiel 451/571.
Pour l'étalonner sur votre propre assemblage, éditez `middle.positions` dans `config.json`.

**Le suivi caméra saccade** → éclairage uniforme, paume face à la caméra. `SMOOTH` dans `tracking.js`
(défaut 0.35) — plus haut = plus lisse mais plus retardé.

**Les gestes caméra sont erronés / un doigt ne suit pas** → voir la section Téléopération caméra ci-dessus. Vérifiez d'abord trois choses :

1. **Les trois poses sont-elles capturées ?** — le statut doit être vert ; rien n'est envoyé avant, et la main reste au milieu
2. **Une direction inversée signifie que cette pose a été capturée à l'envers** — recapturez simplement ce bouton, aucun changement de code
3. **Le pouce ne doit pas s'écarter** — il ne fait que fléchir, voir la section 3 ci-dessus

**Un servo bascule en marche arrière à mi-chemin du poing** → ce servo devrait avoir un **ID pair** (l'axe d'écartement, p. ex. main gauche 12 / 16).
Normalement l'écartement s'estompe jusqu'à 0 avec le repli et ne saute jamais ; si vous constatez cela, la ligne `side *= (1 - curl)` de
`tracking.js` ne prend pas effet, ou bien `curl` n'est pas calculé.
