[English](../en/scs_servo_protocol.md) | [Deutsch](../de/scs_servo_protocol.md) | [Español](../es/scs_servo_protocol.md) | Français | [Italiano](../it/scs_servo_protocol.md) | [日本語](../ja/scs_servo_protocol.md) | [한국어](../ko/scs_servo_protocol.md) | [Português (BR)](../pt-br/scs_servo_protocol.md) | [Português (PT)](../pt-pt/scs_servo_protocol.md) | [简体中文](../zh-hans/scs_servo_protocol.md) | [繁體中文](../zh-hant/scs_servo_protocol.md)

# Servo SCSCL à potentiomètre – Description de la table de mémoire

## Table des matières

- [Servo SCSCL à potentiomètre – Description de la table de mémoire](#servo-scscl-à-potentiomètre--description-de-la-table-de-mémoire)
- [1. Protocole de communication du servo](#1-protocole-de-communication-du-servo)
- [2. Définition de la table de mémoire du servo](#2-définition-de-la-table-de-mémoire-du-servo)
  - [2.1 Informations de version](#21-informations-de-version)
  - [2.2 Configuration EPROM](#22-configuration-eprom)
  - [2.3 Contrôle SRAM](#23-contrôle-sram)
  - [2.4 Retour d'information SRAM](#24-retour-dinformation-sram)
  - [2.5 Paramètres d'usine](#25-paramètres-dusine)
- [3. Description des octets spéciaux](#3-description-des-octets-spéciaux)
  - [3.1 Phase du servo](#31-phase-du-servo)
  - [3.2 État du servo](#32-état-du-servo)
  - [3.3 Conditions de décharge](#33-conditions-de-décharge)
  - [3.4 Conditions d'alarme LED](#34-conditions-dalarme-led)

---

## 1. Protocole de communication du servo

Le servo utilise le **protocole personnalisé FT-SCS**.  

- Débit par défaut : **1 Mbps ou 500 kbps**
- Couche physique : **TTL bus unique**
- Bits de données : **8**
- Parité : **aucune**
- Bits d'arrêt : **1**
- Plage de débit configurable : **38 400 ~ 1 Mbps (500 k)**
- Adresse de communication par défaut (ID) : **1**

Référence du protocole :  
[Protocole personnalisé FT-SCS](http://doc.feetech.cn/#/tiaozhunlujingft?srcType=FT-SCS-Protocol-41ad23fe8a244712ba160b93)

---

## 2. Définition de la table de mémoire du servo

> Si une adresse de fonction utilise une valeur sur 2 octets, l'**octet de poids fort** est stocké à l'**adresse inférieure**, et l'**octet de poids faible** à l'**adresse supérieure** (big-endian au sein de la table).

---

### 2.1 Informations de version

| Address DEC | Address HEX | Nom de la fonction      | Bytes | Default | Access | Range | Unit | Description |
|-------------|-------------|-------------------------|-------|---------|--------|-------|------|-------------|
| 0           | 0x00        | Version majeure du firmware | 1 | – | R | | | |
| 1           | 0x01        | Version mineure du firmware | 1 | – | R | | | |
| 2           | 0x02        | END                     | 1     | 1       | R      |       |      | `1` indique un stockage big-endian |
| 3           | 0x03        | Version majeure du servo | 1 | – | R | | | |
| 4           | 0x04        | Version mineure du servo | 1 | – | R | | | |

---

### 2.2 Configuration EPROM

| Address DEC | Address HEX | Nom de la fonction            | Bytes | Default | Access | Range       | Unit  | Description |
|-------------|-------------|-------------------------------|-------|---------|--------|-------------|-------|-------------|
| 5           | 0x05        | ID du servo                   | 1     | 1       | R/W   | 0 ~ 253     | ID    | Identifiant principal unique sur le bus |
| 6           | 0x06        | Débit                         | 1     | 0       | R/W   | 0 ~ 7       | –     | 0–7 représentent le débit : 1000000(0), 500000(1), 250000(2), 128000(3), 115200(4), 76800(5), 57600(6), 38400(7) |
| 7           | 0x07        | Non défini                    | 1     | –       | R/W   | –           | –     | – |
| 8           | 0x08        | Niveau de retour d'état       | 1     | 1       | R/W   | 0 ~ 1       | –     | 0 : seules les commandes READ et PING renvoient un état ; 1 : toutes les commandes renvoient des paquets d'état |
| 9           | 0x09        | Limite d'angle minimale       | 2     | 20      | R/W   | 0 ~ 1023    | steps | Angle de fonctionnement minimal ; doit être inférieur à l'angle maximal. Si **min angle = max angle = 0** → mode moteur (rotation continue) |
| 11          | 0x0B        | Limite d'angle maximale       | 2     | 1003    | R/W   | 1 ~ 1023    | steps | Angle de fonctionnement maximal ; doit être supérieur à l'angle minimal. Si **min angle = max angle = 0** → mode moteur |
| 13          | 0x0D        | Limite de température maximale | 1    | 70      | R/W   | 0 ~ 100     | °C    | |
| 14          | 0x0E        | Tension d'entrée maximale     | 1     | –       | R/W   | 0 ~ 254     | 0.1 V | Si **max input voltage = min input voltage = 0**, le retour de tension est désactivé |
| 15          | 0x0F        | Tension d'entrée minimale     | 1     | 40      | R/W   | 0 ~ 254     | 0.1 V | Si **max input voltage = min input voltage = 0**, le retour de tension est désactivé |
| 16          | 0x10        | Couple maximal                | 2     | 1000    | R/W   | 0 ~ 1000    | 0.1%  | À la mise sous tension, cette valeur est copiée à l'adresse 48 (limite de couple) |
| 18          | 0x12        | Phase                         | 1     | –       | R/W   | 0 ~ 254     | –     | Octet de fonction spéciale ; ne pas modifier sans besoin précis |
| 19          | 0x13        | Conditions de décharge        | 1     | –       | R/W   | 0 ~ 254     | –     | Chaque bit active/désactive une protection correspondante (voir [3.3](#33-conditions-de-décharge)) |
| 20          | 0x14        | Conditions d'alarme LED       | 1     | –       | R/W   | 0 ~ 254     | –     | Chaque bit active/désactive le clignotement de la LED pour une alarme donnée (voir [3.4](#34-conditions-dalarme-led)) |
| 21          | 0x15        | Gain P de la boucle de position | 1   | –       | R/W   | 0 ~ 254     | –     | Gain proportionnel pour la régulation de position |
| 22          | 0x16        | Gain D de la boucle de position | 1   | –       | R/W   | 0 ~ 254     | –     | Gain dérivé pour la régulation de position |
| 23          | 0x17        | Non défini                    | 1     | –       | R/W   | –           | –     | – |
| 24          | 0x18        | Couple de démarrage minimal   | 1     | –       | R/W   | 0 ~ 254     | 0.1%  | Couple de sortie minimal nécessaire pour démarrer le mouvement |
| 25          | 0x19        | Non défini                    | 1     | –       | R/W   | –           | –     | – |
| 26          | 0x1A        | Zone morte avant              | 1     | 1       | R/W   | 0 ~ 16      | steps | La plus petite unité est un angle de résolution minimale |
| 27          | 0x1B        | Zone morte arrière            | 1     | 1       | R/W   | 0 ~ 16      | steps | La plus petite unité est un angle de résolution minimale |
| 28 ~ 36     | 0x1C ~ 0x24 | Non défini                    | 1     | –       | R/W   | –           | –     | – |
| 37          | 0x25        | Couple de maintien            | 1     | 20      | R/W   | 0 ~ 254     | 1%    | couple de sortie après déclenchement de la protection contre la surcharge ; ex. 20 = 20 % du couple max |
| 38          | 0x26        | Temps de protection           | 1     | 200     | R/W   | 0 ~ 254     | 10 ms | Durée pendant laquelle la charge dépasse le couple de surcharge avant le déclenchement de la protection ; 200 = 2 s, max ≈ 2.5 s |
| 39          | 0x24        | Couple de surcharge           | 1     | 80      | R/W   | 0 ~ 254     | 1%    | Couple seuil pour démarrer la temporisation de la protection contre la surcharge ; 80 = 80 % du couple max |

---

### 2.3 Contrôle SRAM

| Address DEC | Address HEX | Nom de la fonction | Bytes | Default | Access | Range                | Unit   | Description |
|-------------|-------------|-----------------|-------|---------|--------|----------------------|--------|-------------|
| 40          | 0x28        | Interrupteur de couple | 1 | 0  | R/W   | 0 ~ 2                | –      | 0 : couple coupé / libre ; 1 : couple activé ; 2 : mode amortissement |
| 41          | 0x29        | Non défini      | 1     | –       | R/W   | –                    | –      | – |
| 42          | 0x2A        | Position cible  | 2     | 0       | R/W   | 0 ~ 1023             | steps  | Chaque pas correspond à un angle de résolution minimale ; commande de position absolue. La valeur maximale correspond à l'angle effectif maximal |
| 44          | 0x2C        | Temps de course | 2     | 0       | R/W   | 0 ~ 9999 / -1000~1000 | 1 ms / 0.1% | Temps de la position actuelle à la position cible lorsque **run speed = 0**. En mode moteur, définit le rapport cyclique PWM de sortie ; le bit 10 est le bit de direction |
| 46          | 0x2E        | Vitesse de course | 2   | Factory default max speed | R/W | 0 ~ 1000      | steps/s | Pas par seconde (vitesse de déplacement) |
| 48          | 0x30        | Drapeau de verrouillage | 1 | 1 | R/W | 0 ~ 1          | –      | 0 : déverrouille l'écriture EEPROM, les valeurs écrites aux adresses EEPROM sont conservées après mise hors tension ; 1 : verrouille l'écriture EEPROM, les valeurs écrites aux adresses EEPROM ne sont **pas** conservées |
| 49 ~ 56     | 0x32~0x36   | Non défini      | 1     |         |        |                      |        | – |

---

### 2.4 Retour d'information SRAM

| Address DEC | Address HEX | Nom de la fonction | Bytes | Default | Access | Range | Unit   | Description |
|-------------|-------------|-------------------|-------|---------|--------|-------|--------|-------------|
| 56          | 0x38        | Position actuelle  | 2     | –       | R      | –     | steps  | Position actuelle en pas ; chaque pas correspond à un angle de résolution minimale. Mode position absolue ; la valeur maximale correspond à l'angle effectif maximal |
| 58          | 0x3A        | Vitesse actuelle   | 2     | –       | R      | –     | steps/s | Vitesse actuelle du moteur en pas par seconde |
| 60          | 0x3C        | Charge actuelle    | 2     | –       | R      | –     | 0.1%   | Rapport cyclique de sortie de commande actuel pilotant le moteur ; le bit 10 est le bit de direction |
| 62          | 0x3E        | Tension actuelle   | 1     | –       | R      | –     | 0.1 V  | Tension d'alimentation actuelle du servo |
| 63          | 0x3F        | Température actuelle | 1   | –       | R      | –     | °C     | Température interne actuelle du servo |
| 64          | 0x40        | Drapeau d'écriture asynchrone | 1 | 0 | R   | –     | –      | Drapeau utilisé lorsque des commandes d'écriture asynchrones sont employées |
| 65          | 0x41        | État du servo      | 1     | 0       | R      | –     | –      | Les bits à 1 indiquent l'erreur ou les erreurs correspondantes (voir [3.2](#32-état-du-servo)) |
| 66          | 0x42        | Drapeau de mouvement | 1   | 0       | R      | –     | –      | 1 tant que le servo se déplace ; 0 lorsqu'il a atteint la cible et s'est arrêté ; reste à 0 si aucune nouvelle position cible n'est donnée |

---

### 2.5 Paramètres d'usine

| Address DEC | Address HEX | Nom de la fonction | Bytes | Default | Access | Range | Unit | Description |
|-------------|-------------|----------------|-------|---------|--------|-------|------|-------------|
| 78          | 0x4E        | Pas maximal en mode PWM | 1 | 20 | R | – | – | – |
| 79          | 0x50        | Seuil de vitesse de déplacement × 50 | 1 | 1 | R | – | – | – |
| 80          | 0x51        | DTs (ms)       | 1     | 20      | R      | –     | –    | – |
| 81          | 0x52        | Limite de vitesse min × 50 | 1 | 1 | R | – | – | – |
| 82          | 0x53        | Limite de vitesse max × 50 | 1 | – | R | – | – | – |
| 83          | 0x54        | Accélération   | 1     | 20      | R      | –     | –    | – |

---

## 3. Description des octets spéciaux

---

### 3.1 Phase du servo

**Bits / poids : description**

- **BIT0 (1)** : Phase de sens d'entraînement  
  - 0 : sens normal  
  - 1 : sens inversé
- **BIT1 (2)** : –––
- **BIT2 (4)** : –––
- **BIT3 (8)** : Mode vitesse  
  - 0 : vitesse = 0 signifie arrêt  
  - 1 : vitesse = 0 signifie vitesse maximale
- **BIT4 (16)** : –––
- **BIT5 (32)** : Phase PWM  
  - 0 : en phase  
  - 1 : inversée
- **BIT6 (64)** : Mode tension  
  - 0 : détection basse tension 1.5 k  
  - 1 : détection haute tension 1 k
- **BIT7 (128)** : –––

> Si plusieurs bits sont définis en même temps, la **valeur de phase** est la **somme** des valeurs de tous les bits définis.

---

### 3.2 État du servo

**État du servo : 0 = normal, 1 = défaut**

**Bits / poids : description**

- **BIT0 (1)** : État de tension  
- **BIT1 (2)** : –––  
- **BIT2 (4)** : État de température  
- **BIT3 (8)** : –––  
- **BIT4 (16)** : –––  
- **BIT5 (32)** : État de charge  
- **BIT6 (64)** : –––  
- **BIT7 (128)** : –––  

> Si plusieurs conditions de défaut sont présentes, la **valeur d'état** est la **somme** des valeurs de bit correspondantes.  
> Exemple : surtension/sous-tension et surchauffe → état = 4 + 1 = **5**.

---

### 3.3 Conditions de décharge

**Conditions de décharge : 0 = désactivé, 1 = activé**  
(« Décharge » = le couple est coupé en guise de protection.)

**Bits / poids : description**

- **BIT0 (1)** : Protection de tension  
- **BIT1 (2)** : –––  
- **BIT2 (4)** : Protection contre la surchauffe  
- **BIT3 (8)** : –––  
- **BIT4 (16)** : –––  
- **BIT5 (32)** : Protection contre la surcharge  
- **BIT6 (64)** : –––  
- **BIT7 (128)** : –––  

> Si plusieurs bits sont définis, la **valeur de condition de décharge** est la **somme** des valeurs de bit.  
> Exemple : protection de tension + protection contre la surchauffe activées → valeur de décharge = 4 + 1 = **5**.

---

### 3.4 Conditions d'alarme LED

**Conditions d'alarme LED : 0 = désactivé, 1 = activé**

**Bits / poids : description**

- **BIT0 (1)** : Alarme de tension  
- **BIT1 (2)** : –––  
- **BIT2 (4)** : Alarme de surchauffe  
- **BIT3 (8)** : –––  
- **BIT4 (16)** : –––  
- **BIT5 (32)** : Alarme de surcharge  
- **BIT6 (64)** : –––  
- **BIT7 (128)** : –––  

> Si plusieurs bits sont définis, la **valeur de condition d'alarme LED** est la **somme** des valeurs de bit.  
> Exemple : alarme de tension + alarme de surchauffe activées → valeur d'alarme = 4 + 1 = **5**.
