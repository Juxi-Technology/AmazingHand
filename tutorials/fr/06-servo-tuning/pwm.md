---
title: "Protocole, commandes et calibration des servos PWM"
description: "Version PWM AmazingHand : gestes pris en charge, calibration du firmware, protocole série, référence des commandes, réglage fin des paramètres de gestes et questions fréquentes."
version: pwm
---

# Protocole, commandes et calibration des servos PWM

Cette page couvre le protocole série, les commandes, la calibration et le réglage fin des paramètres du firmware PWM. Câblage : [Câblage PWM](../01-hardware/pwm.md) ; flashage : [Démarrage rapide PWM](../02-quick-start/pwm.md) ; contrôle bureau/web : [Outil de bureau PWM](../04-desktop/pwm.md) / [Contrôle web PWM](../03-web-control/pwm.md).

> Les commandes suivantes s'exécutent dans le répertoire `AmazingHand-PWM/` du dépôt. Code source du firmware : [`firmware/AmazingHand_Serial/`](../../../AmazingHand-PWM/firmware/AmazingHand_Serial/).

## 1. Aperçu des commandes et gestes

Les 11 premières lignes sont des commandes de gestes ; les autres sont des commandes de pilotage direct, de sélection du côté, de répétition, d'arrêt et de test de liaison.

| Geste/commande | Commande | Description |
|------|------|------|
| Pierre | 0x01 | Pierre-papier-ciseaux : tous les doigts serrés |
| Ciseaux | 0x02 | Pierre-papier-ciseaux : index + majeur tendus en V |
| Feuille | 0x03 | Pierre-papier-ciseaux : tous les doigts ouverts |
| Pouce levé | 0x04 | Pouce levé, les autres doigts serrés |
| Taquinerie 1 | 0x05 | Remuer l'index (« non non non ») |
| Taquinerie 2 | 0x06 | Annulaire tendu et agité (remplace l'auriculaire) |
| Ouvrir | 0x07 | Tous les doigts ouverts |
| Poing | 0x08 | Tous les doigts fermés |
| OK | 0x09 | Geste OK |
| Pincement | 0x0A | Geste de pincement |
| Pointage | 0x0C | Index tendu pour un geste de « pointage » |
| Pilotage direct | 0xF0 | Contrôle direct de l'angle des 8 voies de servos |
| Définir main gauche/droite | 0xF1 | Bascule entre mode main gauche et main droite |
| Répétition | 0xFE | Rejoue le dernier geste |
| Arrêt | 0xFF | Termine immédiatement le geste en cours |
| NOP | 0x00 | Test de liaison |

> Note : la commande 0x0B est désactivée (l'ancien « pouce vers le bas », qui faisait doublon avec « Pouce levé », a été supprimé).

---

## 2. Calibration du firmware (facultatif, recommandé à la première utilisation)

La position centrale et la largeur d'impulsion des servos doivent être calibrées selon le mécanisme réel ; la modification se fait directement dans le code source du firmware :

- Éditez `middle_pos[8]` et `min_pw/mid_pw/max_pw[8]` en tête de `components/hand_servo/hand_servo.c`.

Après calibration, recompilez et reflashez.

---

## 3. Protocole de communication série

### 3.1 Couche physique

| Paramètre | Valeur |
|------|-----|
| Interface | USB Serial (UART0) |
| Débit | **115200** |
| Bits de données | 8 |
| Parité | Aucune (None) |
| Bits d'arrêt | 1 |
| Contrôle de flux | Aucun |

### 3.2 Format des trames

#### Hôte → ESP32 (trame de commande)

```
┌────────┬────────┬──────────┬────────────────┬──────────┐
│  0xAA  │ CMD_ID │ DATA_LEN │ DATA[0 .. N-1] │ CHECKSUM │
│ 1 Byte │ 1 Byte │  1 Byte  │    N Bytes     │  1 Byte  │
└────────┴────────┴──────────┴────────────────┴──────────┘
  En-tête   ID cmd   Longueur      Charge utile      Somme de contrôle
```

- **En-tête** : fixe `0xAA`, marque le début d'une trame
- **CMD_ID** : numéro de commande (voir [Référence des commandes](#4-référence-des-commandes))
- **DATA_LEN** : nombre d'octets de la charge utile (0-8 ; une trame dépassant 8 est invalide)
- **DATA** : charge utile, dont la longueur est déterminée par DATA_LEN
- **CHECKSUM** : `CMD_ID ^ DATA_LEN ^ DATA[0] ^ ... ^ DATA[N-1]` (contrôle XOR)

> Si DATA_LEN = 0, alors CHECKSUM = CMD_ID.

#### ESP32 → hôte (trame de réponse)

```
┌────────┬────────┬────────┬──────────┐
│  0xBB  │ CMD_ID │ STATUS │ CHECKSUM │
│ 1 Byte │ 1 Byte │ 1 Byte │  1 Byte  │
└────────┴────────┴────────┴──────────┘
  En-tête   ID cmd   Code d'état   Somme de contrôle
```

- **En-tête** : fixe `0xBB`
- **CMD_ID** : numéro de commande d'origine
- **STATUS** : code d'état (voir tableau ci-dessous)
- **CHECKSUM** : `CMD_ID ^ STATUS`

#### Codes d'état

| STATUS | Signification | Description |
|--------|------|------|
| 0x00 | OK | Commande acceptée, exécution commencée |
| 0x01 | Commande invalide | CMD_ID absent de la table des commandes |
| 0x02 | Erreur de paramètre | Longueur ou contenu des données incorrect |
| 0x03 | Occupé | Geste en cours d'exécution, nouvelles commandes temporairement refusées |
| 0x10 | Terminé | Exécution du geste terminée |

### 3.3 Chronologie de communication

```
Hôte                          ESP32
 │                              │
 │──── [AA 01 00 01] ────────→│  Envoi de la commande « Pierre »
 │                              │
 │←─── [BB 01 00 01] ─────────│  ACK : commande acceptée
 │                              │
 │                      (exécution du geste)
 │                              │
 │←─── [BB 01 10 11] ─────────│  Terminé : geste exécuté
 │                              │
 │──── [AA 02 00 02] ────────→│  Envoi de la commande « Ciseaux »
 │                              │
 │←─── [BB 02 00 02] ─────────│  ACK
 │                              │
```

### 3.4 Arrêt d'un geste et expiration des trames

- Envoyer `[AA FF 00 FF]` interrompt à tout moment le geste en cours
- Si l'ESP32 ne reçoit pas une trame complète dans les 200ms, elle est automatiquement abandonnée (pour éviter une désynchronisation permanente due à un octet perdu)
- Les trames dont la somme de contrôle ne correspond pas sont silencieusement ignorées ; le logiciel hôte doit implémenter une retransmission avec timeout

### 3.5 Mode main gauche/droite

Le mode main droite est le mode par défaut. Envoyez `[AA F1 01 02 F2]` pour passer à la main gauche, `[AA F1 01 01 F1]` pour revenir à la main droite. Le côté affecte le sens de mouvement du pouce (gestes contenant le pouce : Pierre/Ciseaux/Pouce levé/OK/Pincement, etc.).

---

## 4. Référence des commandes

### 4.1 Commandes de gestes (0x01–0x0A, 0x0C)

Ces commandes n'ont pas besoin de charge utile (DATA_LEN=0) ; l'ESP32 exécute immédiatement le geste correspondant à réception.

| Commande | Trame HEX | Réponse | Description |
|------|--------|------|------|
| Pierre | `AA 01 00 01` | `BB 01 00 01` → `BB 01 10 11` | Tous les doigts serrés |
| Ciseaux | `AA 02 00 02` | `BB 02 00 02` → `BB 02 10 12` | Index + majeur tendus |
| Feuille | `AA 03 00 03` | `BB 03 00 03` → `BB 03 10 13` | Tous les doigts ouverts |
| Pouce levé | `AA 04 00 04` | `BB 04 00 04` → `BB 04 10 14` | Pouce levé |
| Taquinerie 1 | `AA 05 00 05` | `BB 05 00 05` → `BB 05 10 15` | Remuer l'index (environ 2.5s) |
| Taquinerie 2 | `AA 06 00 06` | `BB 06 00 06` → `BB 06 10 16` | Agiter l'annulaire (environ 2.5s) |
| Ouvrir | `AA 07 00 07` | `BB 07 00 07` → `BB 07 10 17` | Tous les doigts ouverts |
| Poing | `AA 08 00 08` | `BB 08 00 08` → `BB 08 10 18` | Tous les doigts fermés |
| OK | `AA 09 00 09` | `BB 09 00 09` → `BB 09 10 19` | Geste OK |
| Pincement | `AA 0A 00 0A` | `BB 0A 00 0A` → `BB 0A 10 1A` | Geste de pincement |
| Pointage | `AA 0C 00 0C` | `BB 0C 00 0C` → `BB 0C 10 1C` | Index tendu pour un geste de « pointage » |

### 4.2 Commande de pilotage direct (0xF0)

Contrôle direct de l'angle des 8 voies de servos ; les 8 octets de données correspondent aux servos 1-8, chaque octet allant de 0 à 180.

**Exemple : recentrer tous les servos (90°)**

```
Envoi : AA F0 08 5A 5A 5A 5A 5A 5A 5A 5A F8
       │  │  │  └── 8 × 0x5A (90°) ──┘  │
       │  │  │                            └── CHECKSUM
       │  │  └── DATA_LEN = 8
       │  └── CMD_DIRECT_DRIVE
       └── En-tête de trame
```

Somme de contrôle = `F0 ^ 08 ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A` = `F8`

> Les 8 octets 0x5A identiques s'annulent deux à deux par XOR pour donner 0x00 ; le résultat final est `0xF0 ^ 0x08 ^ 0x00 = 0xF8`

**Exemple : index ouvert (servo 1 = 170°, servo 2 = 10°), les autres recentrés (90°)**

```
Envoi : AA F0 08 AA 0A 5A 5A 5A 5A 5A 5A 58
               └─170°  └─10°
```

### 4.3 Définir main gauche/droite (0xF1)

1 octet de données : `0x01` = main droite, `0x02` = main gauche.

```
Main droite : AA F1 01 01 F1
Main gauche : AA F1 01 02 F2
```

### 4.4 Commandes de contrôle

| Commande | Trame HEX | Description |
|------|--------|------|
| NOP | `AA 00 00 00` | Test de liaison, renvoie immédiatement `BB 00 00 00` |
| Répétition | `AA FE 00 FE` | Rejoue le dernier geste |
| Arrêt | `AA FF 00 FF` | Termine immédiatement le geste en cours |

### 4.5 Aide-mémoire des réponses

À réception d'une commande invalide (exemple avec la commande inexistante 0xFC) :

```
Envoi :  AA FC 00 FC
Réponse: BB FC 01 FD    (STATUS=0x01 commande invalide)
```

> Vérification de la somme de contrôle : `FC ^ 00 = FC`, réponse `FC ^ 01 = FD`

---

## 5. Réglage fin des paramètres de gestes

### 5.1 Emplacement des paramètres

Le décalage d'angle de chaque geste est défini par des macros `#define`, **sans modifier le code logique**, seulement les valeurs.

- **Version ESP-IDF** : zone « Paramètres de gestes (réglables par l'utilisateur) » en tête de `components/hand_gestures/hand_gestures.c`

### 5.2 Signification des paramètres

```c
// Exemple : geste Pierre
#define ROCK_IDX_OFF1    70    // décalage de l'articulation 1 de l'index
#define ROCK_IDX_OFF2   -70    // décalage de l'articulation 2 de l'index
```

- **Valeur positive = flexion/serrage**, **valeur négative = extension/ouverture**
- 2 décalages par doigt, relatifs à `middle_pos` (90° par défaut)
- Structure différentielle : deux servos côte à côte, axes colinéaires ; rotation dans le même sens = écartement latéral, rotation en sens inverse = flexion ; la somme des deux décalages correspond à l'écartement, leur différence à la flexion.

### 5.3 Étapes de réglage

1. Trouvez la macro `#define` du geste concerné
2. Modifiez la valeur (augmenter → amplitude plus grande ; diminuer → amplitude plus petite)
3. Recompilez et reflashez, testez le résultat avec le logiciel hôte
4. Affinez par itérations jusqu'à un mouvement naturel

---

## 6. Questions fréquentes

### Q1 : Le logiciel hôte ne se connecte pas au port série ?

1. Confirmez que l'ESP32 est connecté au PC via Type-C
2. Vérifiez que le numéro COM du gestionnaire de périphériques correspond à celui choisi dans la GUI
3. Confirmez le débit 115200
4. Déconnectez les autres logiciels occupant le port série

### Q2 : Aucune réaction après envoi d'une commande ?

1. Envoyez d'abord `AA 00 00 00` (NOP) ; vous devez recevoir `BB 00 00 00`
2. Confirmez que le firmware est flashé et que la puce cible est ESP32-S3
3. Vérifiez le câblage (masse commune GND)

### Q3 : Amplitude ou sens du geste incorrect ?

Allez dans le réglage fin des paramètres de gestes (voir [section 5](#5-réglage-fin-des-paramètres-de-gestes)) et ajustez la macro correspondante.

### Q4 : Quels gestes sont affectés par le mode main gauche/droite ?

Les gestes **contenant le pouce** comme Pierre/Ciseaux/Pouce levé/OK/Pincement ; après bascule, le sens du miroir du pouce change.

### Q5 : Un doigt reste bloqué et ne se déploie pas ?

Avant chaque geste de contraction, tous les gestes de fermeture déploient d'abord toute la main puis la referment, pour éviter qu'un doigt soit bloqué par le geste précédent. S'il reste bloqué, vérifiez l'assemblage mécanique ou réduisez l'amplitude de contraction.

## Pages associées

- [Câblage, GPIO et alimentation PWM](../01-hardware/pwm.md)
- [Démarrage rapide PWM](../02-quick-start/pwm.md)
- [Outil de bureau PWM](../04-desktop/pwm.md)
- [Suivi de main PWM](../05-hand-tracking/pwm.md)
- [FAQ](../08-faq/faq.md)
