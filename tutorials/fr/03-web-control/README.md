---
title: "Contrôle web AmazingHand"
description: "Vue d'ensemble du contrôle web AmazingHand : démarrage, bascule de driver, barre de port série, contrôle manuel, téléopération caméra et conception de sécurité."
version: both
---

# Contrôle web AmazingHand

Pilotez la main dextre AmazingHand depuis un navigateur, en **mode main gauche / main droite**, avec deux façons d'opérer :

- **Contrôle manuel** — 8 curseurs de servo + 19 poses prédéfinies + retour au milieu en un clic
- **Téléopération caméra interactive** — MediaPipe s'exécute localement dans le navigateur, reconnaît les gestes de la main et les projette en temps réel sur les doigts (la vidéo ne quitte jamais la machine)
- **Bascule chinois/anglais** — dans le coin supérieur droit ; le choix est mémorisé par le navigateur, la langue est conservée à la prochaine ouverture

> Cette page est la **description générale du contrôle web**. Pour le mapping/conversion spécifique SCS0009, voir [Contrôle web SCS0009](scs0009.md) ; pour le câblage/flashage/calibration spécifiques PWM, voir [Contrôle web PWM](pwm.md).

## Démarrage rapide

Ouvrez un terminal et placez-vous dans le dossier Amazinghand-web :

```bash
pip install -r requirements.txt

python server.py --no-connect   # recommandé : démarrez d'abord le serveur, choisissez le port dans la page (ne touche pas aux servos)

# python server.py                # détecte et connecte automatiquement le port série
# python server.py --port COM9    # spécifie le port série
# python server.py --hand left    # active uniquement la main gauche
# python server.py --driver pwm   # utilise la version à servos PWM ESP32-S3
# python server.py --dry-run      # aucun port série, vérifie seulement l'interface
```

Ouvrez **http://localhost:8000** dans le navigateur.

Vous pouvez aussi utiliser directement le frontend statique (Web Serial, sans serveur Python) :

- En ligne : <https://juxi-technology.github.io/AmazingHand/Amazinghand-web-io/> (Chrome / Edge)
- En local : à la racine du dépôt, exécutez `python -m http.server 8099`, puis ouvrez <http://localhost:8099/Amazinghand-web-io/>

### Choisir le port série dans la page

En haut de la page se trouve une barre d'outils : choisissez d'abord le driver, puis le port :

```
Driver  [SCS0009 bus ▾]  Port  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [Refresh]  [Connect]  [Disconnect]  Connected to COM3
```

- Liste **Driver** : **Bus SCS0009** (servos de bus officiels, par défaut) ou **PWM (ESP32-S3)** (voir [Contrôle web PWM](pwm.md))
- La liste déroulante énumère tous les ports série de la machine ; les puces USB-série courantes (CH34x / CP210x / FTDI, etc.) sont marquées **★** et placées en tête
- **Refresh** relance le scan (à utiliser après avoir branché la carte)
- **Connect** ouvre le port sélectionné ; la main revient automatiquement au milieu après connexion
- **Disconnect** relâche d'abord le couple avant de déconnecter, pour que les servos ne restent pas figés en place (la version PWM n'a pas de commande de couple, voir plus bas)
- Pour changer de port, sélectionnez le nouveau et cliquez sur « Connect » ; l'ancien port est fermé automatiquement

> **Le déploiement statique (GitHub Pages) n'a pas de serveur Python** : pour des raisons de confidentialité, le navigateur ne peut pas énumérer silencieusement les ports série et ne voit que les appareils que vous avez autorisés. Cliquez alors sur **Add port…** et choisissez la carte dans la fenêtre du navigateur ; le comportement « lister tous les ports locaux » ci-dessus ne s'applique qu'au mode serveur `server.py`.

![Haut de la page web : sélection du driver, barre d'outils du port série et bascule gauche/droite](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-port-bar.png)

> **`--no-connect` est conçu pour ce flux** : au démarrage, il lance seulement le serveur sans toucher au port série,
> donc la main ne s'agite pas à cause d'une mauvaise connexion automatique. Retirez ce paramètre pour qu'il se connecte automatiquement au démarrage.

Les journaux série sont écrits dans `server.log` (au lancement par double-clic sur le .bat, la fenêtre disparaît aussitôt ; consultez ce fichier).

### Vérification du câblage

Liste les ID de servos détectés et les vérifie main par main par rapport à `config.json`.

```bash
python tools/scan_servos.py --port COM9
```

Remplacez COM9 par votre numéro de port réel.

> Cet outil ne s'applique qu'aux **servos à bus SCS0009**. Pour la vérification du câblage de la version PWM, voir [Contrôle web PWM](pwm.md), ou utilisez `AmazingHand-PWM/tools/serial_test.py`.

---

## Poses prédéfinies (19)

![Panneau de contrôle manuel : curseurs des quatre doigts, 19 poses prédéfinies et boutons d'action](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-manual.png)

| Pose | Description | Pose | Description |
|---|---|---|---|
| `open` | Ouverte | `wave1` | Salut |
| `close` / `stone` | Poing | `wave_r` / `wave_l` | Balayage droite / gauche |
| `ok` | OK | `ring_close` | Annulaire seul |
| `greeting` | Salutation | `middle_close` | Majeur seul |
| `victory` / `two` / `scissors` | Victoire / Deux | `pointer_close` | Index seul |
| `paper` | Feuille | `thumb_close` | Pouce seul |
| `one` / `three` | Un / Trois | `hifive` | High five |

Pour modifier vous-même les poses, éditez la section `poses` de `config.json` ; les noms de clés correspondent aux noms du YAML officiel.

### Gauche et droite peuvent avoir des valeurs de pose différentes

Les `positions` d'une pose sont **partagées par les deux mains**. Si une main a besoin d'un autre jeu de valeurs à cause de différences d'assemblage mécanique,
ajoutez simplement une clé `right` ou `left` dans la même entrée ; elle remplace `positions` :

```jsonc
"close": {
  "label": "Poing",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // partagé par les deux mains
  "right":     [ ... 8 valeurs ... ]                // facultatif : main droite uniquement
}
```

---

## Deux modes

| Mode | Comportement |
|---|---|
| **Main droite** | N'envoie que les 8 servos de la main droite |
| **Main gauche** | N'envoie que les 8 servos de la main gauche (SCS0009 applique automatiquement le miroir et le décalage de −35.16° ; PWM utilise le mapping des canaux de la main gauche) |

Une seule main est contrôlée à la fois ; basculez avec **Target** en haut. Le changement n'affecte pas l'autre main, qui conserve sa pose sur place. Les deux mains SCS0009 peuvent partager le même bus ; en PWM, chaque main est contrôlée par un ESP32-S3 distinct.

---

## Téléopération caméra interactive

MediaPipe exécute localement dans le navigateur les points de repère de main (ressources dans `Amazinghand-web/web/mediapipe/`, disponibles hors ligne ; la page détecte aussi en priorité `Amazinghand-web-io/mediapipe/`),
puis convertit les 21 points de repère en valeurs de pose pour les 4 doigts et les envoie en temps réel à la main sélectionnée.

![Panneau caméra : démarrage, affichage du squelette, capture des trois poses et zone d'état](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-camera.png)

### 1. Capturez d'abord trois poses

Après avoir démarré la caméra, placez la main dans une pose et cliquez sur le bouton correspondant pour capturer une fois (moyenne sur environ 1 seconde).
L'ordre est libre ; en cas d'erreur, recliquez sur le même bouton pour recapturer. **Le statut ne passe au vert qu'une fois les trois captures terminées** ;
avant cela, rien n'est envoyé et la main reste en position médiane.

| Bouton | Pose | Fournit |
|---|---|---|
| ① Tendus et écartés | Doigts tendus et écartés, pouce vers l'extérieur | Extrémité « tendu » de la flexion + extrémité « écarté » de l'écartement |
| ② Tendus et serrés | Doigts tendus et serrés, pouce contre l'index | Extrémité « serré » de l'écartement |
| ③ Poing | Poing serré, pouce replié contre la paume | Extrémité « fermé » de la flexion |

### 2. Chaque axe est une droite définie par deux points mesurés

Flexion et écartement utilisent tous deux **deux extrémités mesurées pour définir une droite** :

```
t      = (valeur mesurée − extrémitéA) / (extrémitéB − extrémitéA)      // borné à 0..1
cible  = A.cible + (B.cible − A.cible) × t
```

L'avantage est que **le sens positif/négatif des mesures de chaque doigt est absorbé automatiquement** — inutile donc de prévoir un commutateur
du type « inverser tel doigt » (l'index et l'annulaire sont de part et d'autre de l'axe central, et la chaîne d'articulations du pouce diffère : leurs directions sont bien opposées,
mais deux extrémités mesurées les alignent automatiquement).

Les valeurs cibles des extrémités se trouvent dans la section `camera` de `config.json` :

| Axe | Extrémités | Annulaire | Majeur | Index |
|---|---|---|---|---|
| Flexion | tendu → poing | −50 → 90 | −50 → 90 | −50 → 90 |
| Écartement | serré → écarté | −45 → +45 | 0 → 0 | +45 → −45 |

Les deux extrémités d'écartement du majeur valent 0 (il ne s'écarte pas latéralement).

### 3. Le pouce ne fait que fléchir ⚠️

Le CMC du pouce est une **articulation en selle (opposable)** ; sa flexion et son écartement sont très fortement couplés — lorsque le pouce est contre l'index, il est déjà en
position d'écartement, et le « zéro de flexion » mesuré à ce moment est faussé. Le forcer sur deux axes donne deux axes imprécis.

Le pouce **ne fait donc que fléchir, son écartement reste toujours à 0** (la quantité différentielle d'écartement de ses deux servos est 0). Les deux poses de référence dont il a besoin sont
① (vers l'extérieur) et ③ (vers la paume) ; aucune capture supplémentaire n'est nécessaire.

### 4. L'écartement diminue avec la flexion

L'écartement final est atténué selon la formule :

```
side = side_measured × (1 − curl)
```

`splayDeg` est la projection de la direction MCP→PIP sur l'axe transversal de la paume, et la flexion du doigt **tourne précisément autour de cet axe** —
au-delà d'un certain angle, cette projection bascule et le « degré d'ouverture » saute brusquement de l'autre côté.

Sans cette atténuation, ce saut entraînerait, via `servo2 = flexion − écartement`, une inversion du **servo d'ID pair**
(l'ID impair reçoit `flexion + écartement`, dont la variation est de sens opposé, donc moins visible).
Le symptôme est « à mi-poings, les servos 12 et 16 se retournent brusquement » — 12 est le second servo de l'annulaire gauche,
16 le second servo de l'index gauche, précisément les deux entraînés par la composante d'écartement non nulle.

Avec l'atténuation, l'écartement est **toujours à 0** au poing serré, quelle que soit l'absurdité de la mesure. Et un poing, de toute façon, doit avoir les doigts serrés.

### 5. Couleurs du squelette

| Doigt | Couleur |
|---|---|
| Pouce | orange |
| Index | rouge |
| Majeur | bleu |
| Annulaire | jaune |
| Auriculaire | gris sombre |
| Os de la paume | gris neutre |

L'auriculaire ne participe pas au mapping des gestes, mais son **MCP de base (point 17) sert à définir le repère de la paume de la main droite** ; il ne faut donc pas le supprimer.

### Aide-mémoire de réglage

| Ce que vous voulez changer | Où modifier |
|---|---|
| Valeurs cibles des axes | section `camera` de `config.json` |
| **Sens d'écartement opposé entre gauche et droite** | passez la main concernée à `-1` dans `camera.side_sign` (`1` = inchangé) |
| Niveau de lissage | `SMOOTH` dans `tracking.js` (défaut 0.35 ; plus petit = plus stable mais plus lent) |
| Vitesse de détection de la flexion | recapturez les trois poses |

`side_sign` s'applique à la main sélectionnée sous **Target** ; rechargez la page après modification, sans redémarrer le serveur :

```jsonc
"side_sign": { "right": 1, "left": -1 }   // inverse tout l'axe d'écartement pour la main gauche
```

La flexion n'est pas affectée par `side_sign`.

---

## Structure du projet

```
Amazinghand-web-io/          Frontend (statique, déployable séparément)
├── index.html
├── app.js                   Interface, bascule de driver, poses et UI caméra
├── io.js                    Backend SCS0009 Web Serial
├── pwm.js                   Backend PWM Web Serial
├── common.js                Configuration partagée, conversion des poses et limites
├── ws.js                    Backend WebSocket (mode serveur Python)
├── tracking.js              Suivi caméra MediaPipe
├── i18n.js                  Textes chinois/anglais
├── config.json              Driver, mapping des servos, bibliothèque de poses, paramètres caméra
└── tools/pwm_protocol_test.mjs

Amazinghand-web/
├── server.py                Serveur HTTP + WebSocket + port série
├── requirements.txt
├── tools/scan_servos.py     Scanne le bus SCS0009 et vérifie les ID
└── web/mediapipe/           Ressources MediaPipe (hors ligne, environ 42 MB)
```

Protocole frontend/backend :

```jsonc
// frontend → backend   target: "left" | "right"
{ "cmd": "ports" }                                  // relance le scan des ports série
{ "cmd": "driver", "driver": "pwm" }                // scs0009 | pwm
{ "cmd": "connect",    "port": "COM3" }
{ "cmd": "disconnect" }
{ "cmd": "target", "target": "left" }
{ "cmd": "set",    "target": "left", "angles": { "pointer": [0, 0], ... } }
{ "cmd": "pose",   "target": "left", "name": "close" }
{ "cmd": "middle", "target": "left" }
{ "cmd": "torque", "target": "left", "on": true }   // SCS0009 uniquement
{ "cmd": "stop" }

// backend → frontend
{ "type": "state", "hands": {...}, "poses": {...}, "positions": {...},
  "axes": {...}, "camera": {...}, "target": "left", "driver": "scs0009",
  "capabilities": { "torque": true, "speed": true }, "pwm": {...},
  "limits": {...}, "port": { "available": [...], "current": "COM3", "connected": true } }
{ "type": "ports" | "connected" | "disconnected", "ports": [...], ... }
{ "type": "error", "msg": "连接 COM_FAKE 失败：系统找不到指定的文件。" }
```

---

## Conception de sécurité

| Élément | Description |
|---|---|
| **Limites de pose** | Valeur de pose ±120° (`limits` dans `config.json`) ; les 19 poses ont été vérifiées comme restant dans les limites |
| **Déduplication des changements** | Les variations < 0.5° ne sont pas envoyées, pour éviter de saturer le bus de bruit |
| **Limitation des écritures** | Intervalle minimal SCS0009 20ms ; pilotage direct PWM environ 30ms |
| **Arrêt d'urgence** | SCS0009 : relâche tout le couple ; PWM : envoie `0xFF` pour interrompre le geste, les servos restent alimentés et gardent leur position |
| **Protection à la sortie** | SCS0009 : Ctrl+C coupe le couple ; PWM : après déconnexion du port série, les servos gardent leur position |
| **Débogage d'une seule main** | `--hand left/right` |

---

## Questions fréquentes

**Reconnaissance caméra imprécise** → éclairage uniforme, paume face à la caméra. Dans `tracking.js`, `SMOOTH` (défaut 0.35) plus grand = plus lisse mais plus lent.

**Gestes caméra incorrects, un doigt ne suit pas** → vérifiez d'abord que les trois poses sont capturées (statut vert) ; si un sens est inversé, recapturez la pose concernée ; le pouce ne fait que fléchir et ne participe pas à l'écartement.

**Un servo se retourne brusquement à mi-poings** → vérifiez que l'écartement s'atténue jusqu'à 0 avec la flexion (`side *= (1 - curl)`) et que le signe/l'amplitude de la commande d'écartement ne sont pas anormaux.

**Problème de sens/ID/position médiane SCS0009** → voir [Contrôle web SCS0009](scs0009.md) et [Débogage et calibration SCS0009](../06-servo-tuning/scs0009.md).

**Problème de connexion/débit/calibration PWM** → voir [Contrôle web PWM](pwm.md).

**Autres questions** → [FAQ](../08-faq/faq.md).
