[English](../en/Windows.md) | [Deutsch](../de/Windows.md) | [Español](../es/Windows.md) | Français | [Italiano](../it/Windows.md) | [日本語](../ja/Windows.md) | [한국어](../ko/Windows.md) | [Português (BR)](../pt-br/Windows.md) | [Português (PT)](../pt-pt/Windows.md) | [简体中文](../zh-hans/Windows.md) | [繁體中文](../zh-hant/Windows.md)

# Outil de débogage du servo SCS0009 — Guide pour Windows

Pour Windows 10 / 11. Couvre de l'installation jusqu'au débogage complet du servo.

> ⚠️ **Compatibilité : cet outil ne prend en charge pour l'instant que les servos Feetech SCS0009 (série SCS, retour de position par potentiomètre, résolution 10 bits 0-1023)**. La table des registres et le format xdat sont conçus pour le Feetech SCS0009 ; les autres marques/modèles ne sont pas garantis.

---

## 1. Prérequis

| Dépendance | Version | Remarques |
|-----------|---------|-------|
| Python | >= 3.8 | 3.10+ recommandé, à télécharger sur [python.org](https://www.python.org/downloads/) |
| PySide6 | >= 6.0 | Framework d'interface graphique |
| pyserial | >= 3.5 | Communication série |
| OS | Win10 / Win11 | Toute édition |

## 2. Installer Python

1. Rendez-vous sur <https://www.python.org/downloads/>
2. Téléchargez l'installateur Python 3.10+
3. **Cochez « Add Python to PATH »** pendant l'installation (sinon python ne sera pas trouvé dans le terminal)

Vérifiez :

```bash
python --version
```

## 3. Installer les dépendances

Installez dans un environnement virtuel pour éviter de polluer le Python système :

```bash
cd SCS0009_ServoController
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> ⚠️ **Ne créez l'environnement virtuel qu'UNE seule fois**. Le relancer réinitialiserait/écraserait l'environnement (ce qui effacerait les dépendances installées). Ensuite, il suffit de l'`activate` à chaque fois.

> L'invite affichera `(.venv)` après l'activation.

## 4. Vérifier l'environnement

```bash
python setup.py
```

`[OK] 环境检查通过，可以运行项目` signifie que l'environnement est prêt.

## 5. Connecter le matériel

1. Branchez l'adaptateur USB-série (CH340 / CP2102)
2. Connectez le contrôleur de servos (carte de commande du bras robotisé)
3. Alimentez les servos (DC 5V 5A standard, DC 12V 5A Pro)

Vérifiez le port COM dans le Gestionnaire de périphériques (`Win+X` → Gestionnaire de périphériques) :

```
Ports (COM & LPT)
  └─ USB-SERIAL CH340 (COM3)     ← your servo port
```

> **Notez le numéro COM** afin de le sélectionner au démarrage.

## 6. Lancer l'interface graphique

```bash
python -m src.gui.factory_calibration_tool
```

Ou spécifiez le port :

```bash
python -m src.gui.factory_calibration_tool --port COM3
```

Lister les ports disponibles :

```bash
python -m src.gui.factory_calibration_tool --list-ports
```

## 7. Déroulement de l'interface

> Disposition à panneau unique. Une barre de défilement apparaît automatiquement lorsque la fenêtre est trop courte ; elle s'étire pour s'adapter en mode agrandi.

### 7.1 Connexion série

- Sélectionnez le port et le débit (1M par défaut), puis cliquez sur **Connecter**
- L'état affiche `🟢 Connected`

### 7.2 Analyser les servos

- Cliquez sur **Analyser les servos** pour détecter les servos en ligne (ID 1-254)
- Les résultats s'affichent en temps réel dans la liste des servos (avec le modèle)
- Cliquez sur une ligne de la liste → remplit automatiquement la liste déroulante des servos

### 7.3 Lecture/écriture des paramètres

- **Lire les paramètres** : lit les 44 registres (EEPROM + SRAM), le journal affiche les résultats en direct
- **Table des paramètres** : 5 colonnes (Adresse/Registre/Valeur/Mémoire/Accès), colorées selon EEPROM/SRAM/DEFAULT
- **Liaison par sélection de ligne** : cliquez sur une ligne → remplit automatiquement « Adresse d'écriture », « Longueur » et « Valeur »
- **Écrire** : modifiez la valeur puis cliquez sur écrire ; l'outil déverrouille/écrit/verrouille automatiquement l'EEPROM
- **Popup de résultat d'écriture** : verte « ✅ Written successfully » en cas de succès, rouge « ❌ Write failed » (avec la raison) en cas d'échec

### 7.4 Contrôle de position

- **Curseur** : faites-le glisser pour régler la position cible (0-1023), la zone de valeur se met à jour en direct
- **Zone de valeur** : saisissez directement la position cible, le curseur suit
- Après le mouvement, l'état affiche « move complete, please turn off torque »

### 7.5 Débit / Réinitialisation d'usine

- **Modifier le débit** : sélectionnez 38400-1000000 bps, retour arrière automatique en cas d'échec
- **Réinitialisation d'usine** : restaure les valeurs d'usine (ID=1, débit=1M), une nouvelle analyse est nécessaire

### 7.6 Paramètres xdat (EEPROM uniquement)

1. `💾 Enregistrer le servo actuel` : enregistre les paramètres EEPROM du servo actuel dans un fichier xdat (sauvegarde)
2. `📂 Ouvrir xdat` : charge un fichier de sauvegarde
3. `📤 Restaurer sur le servo` : réécrit la sauvegarde dans le servo

## 8. Dépannage

| Problème | Solution |
|---------|----------|
| Aucun port série | Vérifiez le pilote dans le Gestionnaire de périphériques ; essayez un autre port USB ; installez le pilote CH340 |
| Port déjà utilisé | Fermez les moniteurs série ; redémarrez l'outil |
| Texte chinois vide | Le système dispose de Microsoft YaHei ; installez une police CJK si l'affichage est cassé |
| Servo introuvable | Vérifiez l'alimentation/câblage ; confirmez le débit 1M |
| Échec d'écriture | Vérifiez l'alimentation et la connexion du servo ; confirmez que le registre est accessible en écriture |
| PermissionError à l'ouverture du port | Assurez-vous qu'aucun autre processus n'occupe le port COM |

## 9. Ligne de commande (facultatif)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port COM3
```
