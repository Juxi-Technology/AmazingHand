---
title: "Contrôle web PWM"
description: "Contrôle web de la version à servos PWM d'AmazingHand : connexion ESP32-S3, bascule de driver, différences avec SCS0009, calibration des angles et questions fréquentes."
version: pwm
---

# Contrôle web PWM

Cette page est la description **spécifique à la version PWM (ESP32-S3)** du contrôle web. Pour l'interface générale, le démarrage, les poses prédéfinies et la téléopération caméra, voir [Vue d'ensemble du contrôle web](README.md).

## Matériel et flashage

- Câblage, GPIO, alimentation et modèle de servo : [Câblage, GPIO et alimentation PWM](../01-hardware/pwm.md).
- Flashage du firmware (ESP-IDF ou bin précompilé) : [Démarrage rapide PWM](../02-quick-start/pwm.md).
- PC hôte ↔ ESP32 fixe **115200 8N1** ; les servos eux-mêmes n'ont pas de débit.

## Connexion web

1. Dans la liste « Driver » en haut, choisissez **PWM (ESP32-S3)**
2. Cliquez sur **Add port…** et sélectionnez le port USB de l'ESP32-S3
3. Cliquez sur **Connect** : la page effectue automatiquement le handshake (NOP), envoie le choix gauche/droite et revient au milieu
4. Pilotez ensuite avec les curseurs, les poses prédéfinies et la téléopération caméra ; les titres des doigts affichent **CH 1/2 …** (numéro de canal PWM)

![Mode PWM : sélection du driver en haut et affichage des canaux CH](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-port-bar.png)

![Panneau de contrôle manuel en mode PWM : titres des doigts affichant les canaux CH, bouton de couple masqué](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-manual.png)

## Différences avec la version SCS0009

| Élément | Version à bus série SCS0009 | Version à servos PWM |
|------|----------------|--------|
| Débit du port série | 1,000,000 | **115,200** |
| Carte de commande | Carte de commande de bus USB | ESP32-S3 + carte d'adaptation PWM |
| Couple | Peut être activé/relâché | **Aucun** (le firmware n'a pas de commande de couple ; le bouton est masqué) |
| Arrêt d'urgence | Relâche tout le couple | Envoie `0xFF` pour interrompre le geste ; les servos restent alimentés et gardent leur position |
| Vitesse | Prend un paramètre de vitesse | Les trames de pilotage direct n'ont pas de paramètre de vitesse |
| Retour d'information | Position/température/tension/vitesse | **Aucun retour** ; blocage ou perte de pas non détectable |
| Main gauche/droite | ID de servos différents | Le même groupe de canaux ; envoie `0xF1` pour basculer (affecte surtout les gestes du firmware ; les poses de la page utilisent le mapping de chaque main) |

## Calibration des angles

La page convertit les valeurs de pose en 8 angles de 0–180°, avec cette formule par défaut :

```
angle = 90 + dir × scale × valeur de pose + offset
```

- Pour chaque doigt, le premier canal utilise `dir = -1`, le second `dir = +1`
- Par défaut `scale = 1`, `offset = 0`, c'est-à-dire que l'angle de l'axe du servo est repris directement en miroir
- Lorsque `mirror_pose` est vrai, échangez d'abord les deux valeurs de pose de chaque doigt (activé pour les deux mains dans ce dépôt)

Si sur la machine réelle la direction est inversée ou le milieu décalé, éditez `pwm.calibration` dans [`config.json`](../../../Amazinghand-web-io/config.json) :

```jsonc
"pwm": {
  "calibration": {
    "right": {
      "pointer": { "scale": 1.0, "offset_deg": [0, 0] }
    }
  }
}
```

- Direction inversée : passez le `scale` du doigt concerné à `-1`
- Décalage du milieu : ajustez `offset_deg` (séparément pour les deux canaux)
- Procédure doigt par doigt : retour au milieu → déplacez un seul doigt → observez la direction/le milieu → modifiez `scale`/`offset_deg` → rechargez la page et réessayez

## Questions fréquentes

- **Échec de connexion / ESP32 sans réponse** : vérifiez que le débit est 115200, que le port COM sélectionné est celui de l'ESP32, l'alimentation 5V/3A et la masse commune ; l'ouverture du port série peut réinitialiser l'ESP32, la page réessaie automatiquement le NOP
- **Servos immobiles ou vibrants** : vérifiez d'abord que les servos sont des servos numériques 333 Hz (PTK 7452 MG-D ou équivalent) et que l'alimentation suffit ; le SG90 nécessite une modification du firmware
- **Direction inversée** : passez le `scale` du doigt concerné à `-1`
- **Milieu incorrect** : ajustez l'`offset_deg` du canal concerné
- **Message « occupé (geste en cours) »** : le firmware exécute un geste intégré ; attendez la fin ou appuyez sur l'arrêt d'urgence (`0xFF`)
- **Scanner les servos** : `tools/scan_servos.py` ne s'applique qu'aux SCS0009 ; pour PWM, utilisez `AmazingHand-PWM/tools/serial_test.py` ou la page web

---

## Pages associées

- [Protocole et calibration PWM](../06-servo-tuning/pwm.md)
- [Outil de bureau PWM](../04-desktop/pwm.md)
- [Démarrage rapide PWM](../02-quick-start/pwm.md)
