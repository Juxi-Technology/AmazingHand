---
title: "Domande frequenti (FAQ)"
description: "Raccolta delle domande frequenti su AmazingHand generale, SCS0009, PWM, controllo web, applicazione desktop e tracciamento delle mani."
version: both
---

# Domande frequenti (FAQ)

## Generale

**Devo scegliere SCS0009 o PWM?**
Se servono retroazione di posizione, precisione e acquisizione dati LeRobot/SO-ARM101 scegli SCS0009; per dimostrazioni autonome, interazione gestuale e avvio rapido con web/desktop scegli PWM. Dettagli in [Confronto tra versioni](../00-product/version-comparison.md).

**Posso collegare entrambe le soluzioni di servo contemporaneamente?**
No. Alimentazione, protocollo e firmware sono diversi; collegare una sola soluzione alla volta.

**Posso accendere la mano direttamente?**
Prima della prima accensione porta la mano in posizione centrale e installa i bracci dei servo in posizione centrale; l'alimentazione esterna e la scheda driver/ESP32 devono avere massa comune.

**Posso cambiare modello di servo?**
La versione SCS0009 usa servo bus; il firmware della versione PWM è calibrato per PTK 7452 MG-D (servo digitale a 333 Hz). Servo analogici a 50 Hz come l'SG90 non possono sostituire direttamente la versione PWM; è necessario modificare `LEDC_FREQ` e la calibrazione della larghezza d'impulso.

## Versione bus seriale SCS0009

**Direzione del movimento invertita** → controlla se il cablaggio rispetta «prima gli ID dispari»; per la mano sinistra verifica `angle_offset_deg = -35.16`.

**Ampiezza del pugno della mano sinistra insufficiente / servo che ronzano** → controlla che il limite di `config.json` sia stato portato a ±120° (il valore predefinito ±90 taglia il pugno della mano sinistra).

**Un dito non si muove / messaggio «attesi N motori, rilevati M»** → esegui `tools/scan_servos.py`; gli ID della mano sinistra sono i più facili da cablare male (11–18, non 9–16).

**Posizione centrale sbagliata** → il valore centrale `-17.578125` corrisponde al raw ufficiale 451/571; per calibrare sul proprio assemblaggio modifica `middle.positions` di `config.json`.

**Come si imposta l'ID del servo?** → usa lo [strumento di debug SCS0009](../06-servo-tuning/scs0009.md) per scansionare e modificare l'ID; mano destra 1–8, mano sinistra 11–18.

**Linux non apre la seriale** → aggiungi l'utente corrente al gruppo `dialout` e riconnettiti.

**È possibile leggere posizione/temperatura/tensione?** → Sì, SCS0009 supporta la lettura di posizione, velocità, tensione e temperatura; la tabella di memoria del protocollo è in [`scs_servo_protocol.md`](../../../AmazingHandControl/docs/zh-hans/scs_servo_protocol.md).

## Versione con servo PWM

**Connessione fallita / ESP32 non risponde** → verifica il baudrate 115200, la porta COM dell'ESP32, l'alimentazione 5V/3A e la massa comune; all'apertura della seriale l'ESP32 può resettarsi e la pagina ritenta automaticamente il NOP.

**I servo non si muovono o tremano** → verifica che siano servo digitali a 333 Hz (PTK 7452 MG-D o equivalenti) e che l'alimentazione sia sufficiente; l'SG90 richiede una modifica del firmware.

**Direzione invertita** → in `pwm.calibration` di `config.json` del web imposta `scale` del dito corrispondente a `-1`.

**Posizione centrale sbagliata** → regola `offset_deg` del canale corrispondente; dettagli in [Protocollo, comandi e calibrazione PWM](../06-servo-tuning/pwm.md).

**Messaggio «occupato (gesto in corso)»** → il firmware sta eseguendo un gesto integrato; attendi il completamento o invia lo stop (`0xFF`).

**La versione PWM ha retroazione?** → Nessuna lettura di posizione/temperatura/tensione, impossibile rilevare blocco o perdita di passi.

**I servo PWM hanno un baudrate?** → Il servo stesso no; la seriale PC↔ESP32 è fissa a 115200 8N1.

**Posso testare con solo alcuni servo collegati?** → Sì. I canali non collegati possono restare vuoti senza influire sugli altri; attenzione a isolare i connettori vuoti.

**La telecamera mostra immagini ma la mano non segue / risposta lenta** → luce uniforme, palmo a circa 40–80 cm dall'obiettivo e rivolto verso di esso; chiudi gli altri programmi che occupano la telecamera; verifica che la seriale sia connessa. Per i parametri di tracciamento della GUI vedi [Tracciamento delle mani PWM](../05-hand-tracking/pwm.md).

**Il cambio mano destra/sinistra non ha effetto** → il firmware cambia mano sinistra/destra con `0xF1` (viene inviato automaticamente alla connessione web); questa impostazione influenza soprattutto la direzione del pollice nei gesti integrati del firmware, mentre le pose della pagina usano la mappatura della rispettiva mano in base al target di controllo corrente.

**L'immagine di tracciamento si blocca / il log si ferma** → ferma il tracciamento e riavvialo; se ancora non risponde chiudi e riapri la GUI e verifica che la telecamera non sia occupata da altri programmi.

**Dopo aver cambiato porta USB non trovo la seriale** → controlla in Gestione dispositivi il nuovo numero COM e, nella GUI o nella pagina web, fai clic su «aggiorna» e riseleziona.

## Controllo web

**Modello non caricato / caricamento del tracciamento con telecamera fallito** → verifica che la pagina sia servita da un servizio locale (non aperta direttamente con `file://`) e che il percorso delle risorse MediaPipe sia accessibile; il tutorial locale ha già corretto il routing MediaPipe lato server. Se il problema persiste controlla nella Console/Network del browser gli errori 404 o di permesso.

**Riconoscimento della telecamera impreciso** → luce uniforme, palmo rivolto verso l'obiettivo; in `tracking.js` un `SMOOTH` (predefinito 0.35) più alto rende il movimento più fluido ma più lento.

**Un dito non segue** → riacquisisci le tre pose; se la direzione è invertita riacquisisci la posa corrispondente; il pollice si flette soltanto e non partecipa alla divaricazione.

**A metà pugno un servo si inverte** → la divaricazione dovrebbe annullarsi con la curvatura fino a 0 (`side *= (1 - curl)`); controlla che segno e ampiezza del valore di controllo della divaricazione non siano anomali.

**Come si cambia il driver nel web?** → nel menu a tendina «Driver» in alto seleziona SCS0009 o PWM; per PWM è necessario selezionare la seriale 115200; dettagli in [Panoramica del controllo web](../03-web-control/README.md).

## Applicazione desktop

**La GUI SCS0009 non elenca le porte seriali** → ricollega l'adattatore USB, installa il driver o riavvia la GUI; su Linux controlla `dialout`.

**Il pulsante Connect è in grigio** → è già connesso, fai prima clic su Disconnect.

**La sequenza non aziona tutte le dita** → controlla la velocità di ogni passaggio e assicurati che ogni posa contenga i valori di tutti gli 8 servo.

**L'indicatore di blocco resta attivo** → controlla eventuali inceppamenti meccanici; se la differenza tra target e posizione reale è grande e non c'è movimento, scatta il rilevamento di blocco.

**All'avvio della GUI PWM viene segnalato mediapipe mancante** → avvia con il Python di `tools/tracking_env`, oppure riesegui `tools/setup_tracking.bat`.

## Tracciamento delle mani

**mediapipe manca del sottomodulo solutions** → installa `mediapipe==0.10.14` e verifica che Python 3.12 sia a 64 bit.

**Versione di dora incompatibile** → allinea la versione di dora secondo `pyproject.toml` e i log; pulisci e reinstalla.

**Caricamento del modello fallito (percorsi con caratteri cinesi)** → metti progetto/modelli in percorsi completamente in inglese.

**La telecamera non mostra immagini / permessi** → consenti i permessi della telecamera di sistema; nella macchina virtuale serve il pass-through USB della telecamera.

**Qual è la differenza tra la demo ufficiale SCS0009 e il tracciamento della GUI PWM?** → SCS0009 usa la catena completa dora + MuJoCo IK; la versione PWM offre il tracciamento leggero con MediaPipe integrato nella GUI, la demo dora non è inclusa nel modulo. Dettagli in [Tracciamento delle mani SCS0009](../05-hand-tracking/scs0009.md) / [Tracciamento delle mani PWM](../05-hand-tracking/pwm.md).

## Altro

- [Confronto tra versioni e scelta](../00-product/version-comparison.md)
- [Panoramica hardware](../01-hardware/overview.md)
- [Download e risorse](../00-product/downloads.md)
