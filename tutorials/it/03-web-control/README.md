---
title: "Controllo web AmazingHand"
description: "Panoramica del controllo web di AmazingHand: modalità di avvio, selezione del driver, barra della porta seriale, controllo manuale, teleoperazione con telecamera e progettazione della sicurezza."
version: both
---

# Controllo web AmazingHand

Controlla la mano robotica AmazingHand dal browser, **due modalità mano sinistra / mano destra**, due modi di operare:

- **Controllo manuale** — 8 slider per i servo + 19 pose predefinite + ritorno alla posizione centrale con un clic
- **Teleoperazione interattiva con telecamera** — MediaPipe eseguito localmente nel browser riconosce i movimenti della mano e li mappa in tempo reale sulle dita (il video non lascia mai la macchina)
- **Commutazione cinese/inglese** — nell'angolo in alto a destra; la scelta viene memorizzata nel browser e la prossima volta viene mantenuta la lingua precedente

> Questa pagina è la **descrizione generale del controllo web**. Per mappatura/conversione specifiche di SCS0009 vedi [Controllo web SCS0009](scs0009.md); per cablaggio/flashing/calibrazione specifici PWM vedi [Controllo web PWM](pwm.md).

## Avvio rapido

Apri un terminale ed entra nella cartella Amazinghand-web:

```bash
pip install -r requirements.txt

python server.py --no-connect   # consigliato: avvia il server, scegli la porta nella pagina (non muove nulla)

# python server.py                # rileva automaticamente la porta seriale e si connette
# python server.py --port COM9    # usa una porta specifica
# python server.py --hand left    # abilita solo la mano sinistra
# python server.py --driver pwm   # usa i servo PWM dell'ESP32-S3
# python server.py --dry-run      # nessuna porta seriale, solo interfaccia
```

Apri **http://localhost:8000** nel browser.

È anche possibile usare direttamente il frontend statico (Web Serial, senza server Python):

- Online: <https://juxi-technology.github.io/AmazingHand/Amazinghand-web-io/> (Chrome / Edge)
- Locale: dalla radice del repository eseguire `python -m http.server 8099`, aprire <http://localhost:8099/Amazinghand-web-io/>

### Selezionare la porta seriale nella pagina

In cima alla pagina c'è una barra degli strumenti: prima scegli il driver, poi la porta seriale:

```
Driver  [SCS0009 bus ▾]  Port  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [Refresh]  [Connect]  [Disconnect]  Connected to COM3
```

- Menu a tendina **Driver**: **bus SCS0009** (servo bus ufficiali, predefinito) oppure **PWM (ESP32-S3)** (vedi [Controllo web PWM](pwm.md))
- Il menu a tendina della porta elenca tutte le porte seriali presenti sulla macchina. I chip USB-seriale più comuni (CH34x / CP210x / FTDI …) sono contrassegnati con **★** e ordinati per primi
- **Refresh** esegue una nuova scansione (usalo dopo aver collegato la scheda)
- **Connect** apre la porta selezionata; subito dopo la mano torna in posizione centrale
- **Disconnect** disattiva prima la coppia, così i servo non restano bloccati dove si trovano (la versione PWM non ha comandi di coppia, vedi la spiegazione sotto)
- Per cambiare porta, seleziona quella nuova e fai clic su Connect — la vecchia porta viene chiusa automaticamente

> **La distribuzione statica (GitHub Pages) non ha un server Python**: per motivi di privacy il browser non può enumerare silenziosamente le porte seriali e vede solo i dispositivi che hai autorizzato. In questo caso fai clic su **Add port…** e scegli la scheda di controllo nella finestra del browser; il comportamento «elenca tutte le porte seriali della macchina» descritto sopra vale solo per la modalità server `server.py`.

![Parte superiore della pagina web: selezione del driver, barra degli strumenti della porta seriale e commutazione mano destra/sinistra](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-port-bar.png)

> **`--no-connect` serve proprio per questo flusso**: all'avvio avvia solo il server e non tocca alcuna porta seriale,
> quindi non può connettersi alla porta sbagliata e far muovere la mano in modo imprevisto. Se vuoi che si connetta automaticamente all'avvio, rimuovi questo parametro.

I log seriali finiscono in `server.log` (se avvii tramite un file `.bat`, la finestra scompare in un lampo — leggi direttamente il file).

### Verifica del cablaggio

Elenca gli ID dei servo trovati e li verifica mano per mano confrontandoli con `config.json`.

```bash
python tools/scan_servos.py --port COM9
```

Sostituisci COM9 con la tua porta effettiva

> Questo strumento vale solo per i **servo bus SCS0009**. Per la verifica del cablaggio della versione PWM, vedi [Controllo web PWM](pwm.md), oppure usa `AmazingHand-PWM/tools/serial_test.py`.

---

## Pose predefinite (19)

![Pannello di controllo manuale: slider delle quattro dita, 19 pose predefinite e pulsanti di azione](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-manual.png)

| Posa | Descrizione | Posa | Descrizione |
|---|---|---|---|
| `open` | Aperto | `wave1` | Ciao |
| `close` / `stone` | Pugno | `wave_r` / `wave_l` | Scorri a destra / a sinistra |
| `ok` | OK | `ring_close` | Solo anulare |
| `greeting` | Saluto | `middle_close` | Solo medio |
| `victory` / `two` / `scissors` | Vittoria / Due | `pointer_close` | Solo indice |
| `paper` | Carta | `thumb_close` | Solo pollice |
| `one` / `three` | Uno / Tre | `hifive` | Batti il cinque |

Per modificare personalmente una posa, modifica la sezione `poses` di `config.json`; le chiavi corrispondono ai nomi nello YAML ufficiale.

### Mano destra e sinistra possono usare valori di posa diversi

All'interno di una posa, `positions` è **condiviso da entrambe le mani**. Se una mano, a causa di differenze nell'assemblaggio meccanico, necessita di un set diverso,
aggiungi una chiave `right` o `left` a quella voce e questa sostituirà `positions`:

```jsonc
"close": {
  "label": "Pugno",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // condiviso da entrambe le mani
  "right":     [ ... 8 valori ... ]                 // opzionale: solo per la mano destra
}
```

---

## Due modalità

| Modalità | Comportamento |
|---|---|
| **Mano destra** | Invia solo agli 8 servo della mano destra |
| **Mano sinistra** | Invia solo agli 8 servo della mano sinistra (SCS0009 applica automaticamente lo specchiamento e l'offset di −35,16°; PWM usa la mappatura dei canali della mano sinistra)|

Si controlla una mano alla volta; si cambia con «target di controllo» in alto. Il cambio non disturba l'altra mano, che mantiene la posa corrente. Per SCS0009 le due mani possono essere collegate allo stesso bus; per PWM ogni mano è controllata da un ESP32-S3 separato.

---

## Teleoperazione interattiva con telecamera

MediaPipe esegue localmente nel browser i landmark della mano (risorse in `Amazinghand-web/web/mediapipe/`, funzionano offline; la pagina prova anche prima `Amazinghand-web-io/mediapipe/`),
converte i 21 landmark in valori di posa per 4 dita e li invia in streaming alla mano selezionata.

![Pannello della telecamera: avvio, visualizzazione dello scheletro, acquisizione in tre passi delle pose e area di stato](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-camera.png)

### 1. Acquisisci prima tre pose

Dopo aver avviato la telecamera, assumi una posa e fai clic sul pulsante corrispondente per acquisirla (circa 1 secondo di media).
L'ordine non conta; se sbagli, fai clic sullo stesso pulsante per riacquisire. **Lo stato diventa verde solo quando tutte e tre sono acquisite**;
prima di allora non viene inviato nulla e la mano resta in posizione centrale.

| Pulsante | Posa | Fornisce |
|---|---|---|
| ① Dita distese e divaricate | Dita distese e divaricate, pollice rivolto verso l'esterno | L'estremo «disteso» della flessione + l'estremo «divaricato» della divaricazione |
| ② Dita distese e unite | Dita distese e unite, pollice contro l'indice | L'estremo «unite» della divaricazione |
| ③ Pugno | Chiudi a pugno, pollice piegato verso il palmo | L'estremo «chiuso» della flessione |

### 2. Ogni asse è una retta passante per due punti misurati

Sia la flessione sia la divaricazione usano **due estremi misurati per definire una retta**:

```
t      = (measured − endpointA) / (endpointB − endpointA)      // limitato a 0..1
target = A.target + (B.target − A.target) × t
```

Il vantaggio: **il segno della misura di ogni dito viene assorbito automaticamente** — quindi non serve alcun interruttore del tipo «inverti questo
dito» (indice e anulare stanno su lati opposti della linea centrale e la catena articolare del pollice è diversa, quindi le loro direzioni sono davvero opposte,
ma due estremi misurati le assorbono automaticamente).

I target degli estremi si trovano nella sezione `camera` di `config.json`:

| Asse | Estremi | Anulare | Medio | Indice |
|---|---|---|---|---|
| Flessione | disteso → pugno | −50 → 90 | −50 → 90 | −50 → 90 |
| Divaricazione | unite → divaricate | −45 → +45 | 0 → 0 | +45 → −45 |

Entrambi gli estremi della divaricazione sono 0 per il dito medio (non oscilla lateralmente).

### 3. Il pollice si flette soltanto ⚠️

Il CMC del pollice è un'**articolazione a sella (opponibile)** e la sua flessione è strettamente accoppiata all'abduzione — con il pollice accostato
all'indice si è già in una posizione di divaricazione, quindi lo «zero di flessione» misurato lì è contaminato. Forzandolo su due assi, entrambi risultano sbagliati.

Quindi il pollice **si flette soltanto; la sua divaricazione è sempre 0** (la componente differenziale di divaricazione dei due servo è 0). Le due pose
di riferimento che gli servono sono la ① (rivolto verso l'esterno) e la ③ (rivolto verso il palmo); non serve acquisire altro.

### 4. La divaricazione si annulla man mano che il dito si piega

La divaricazione finale viene scalata per:

```
side = side_measured × (1 − curl)
```

`splayDeg` è la proiezione della direzione MCP→PIP sull'asse laterale del palmo, e la flessione del dito **ruota esattamente attorno a quell'asse** — oltre
una certa curvatura la proiezione cambia segno e la «divaricazione» misurata scatta all'improvviso verso l'estremo opposto.

Senza l'attenuazione, questo scatto passa attraverso `servo2 = flessione − divaricazione` e trascina il **servo con ID pari** in inversione
(l'ID dispari riceve `flessione + divaricazione`, quindi la sua variazione va nel verso opposto e si nota meno).
Il sintomo è «a metà pugno, i servo 12 e 16 si invertono improvvisamente» — 12 è il secondo servo dell'anulare sinistro e 16 quello dell'indice sinistro,
proprio i due con componente di divaricazione non nulla.

Con l'attenuazione, la divaricazione è **esattamente 0** a curvatura completa, per quanto selvaggia diventi la misura. E poi un pugno dovrebbe comunque avere le dita unite.

### 5. Colori dello scheletro

| Dito | Colore |
|---|---|
| Pollice | arancione |
| Indice | rosso |
| Medio | blu |
| Anulare | giallo |
| Mignolo | grigio tenue |
| Ossa del palmo | grigio neutro |

Il mignolo non partecipa alla mappatura dei gesti, ma il suo **MCP di base (landmark 17) definisce il sistema di coordinate del palmo della mano destra**, quindi non può essere semplicemente eliminato.

### Promemoria per la regolazione

| Cosa vuoi cambiare | Dove |
|---|---|
| Valori target degli assi | sezione `camera` di `config.json` |
| **La divaricazione di sinistra e destra va in versi opposti** | imposta quella mano a `-1` in `camera.side_sign` (`1` = invariato) |
| Fluidità | `SMOOTH` in `tracking.js` (predefinito 0.35; più basso è più stabile ma più lento) |
| Quanto rapidamente viene rilevata una curvatura | riacquisisci le tre pose |

`side_sign` si applica alla mano selezionata in **«target di controllo»**. Modificalo e ricarica la pagina — non serve riavviare il server:

```jsonc
"side_sign": { "right": 1, "left": -1 }   // inverti l'intero asse di divaricazione sulla mano sinistra
```

La flessione (flexion) non è influenzata da `side_sign`.

---

## Struttura del progetto

```
Amazinghand-web-io/          frontend (statico, distribuibile separatamente)
├── index.html
├── app.js                   interfaccia, selezione del driver, pose e UI della telecamera
├── io.js                    backend SCS0009 Web Serial
├── pwm.js                   backend PWM Web Serial
├── common.js                configurazione condivisa, conversione delle pose e limiti
├── ws.js                    backend WebSocket (modalità server Python)
├── tracking.js              tracciamento con telecamera MediaPipe
├── i18n.js                  testi cinese/inglese
├── config.json              driver, mappatura dei servo, libreria di pose, parametri della telecamera
└── tools/pwm_protocol_test.mjs

Amazinghand-web/
├── server.py                server HTTP + WebSocket + seriale
├── requirements.txt
├── tools/scan_servos.py     scansione del bus SCS0009 e verifica degli ID
└── web/mediapipe/           risorse MediaPipe (offline, circa 42MB)
```

Protocollo frontend/backend:

```jsonc
// frontend → backend   target: "left" | "right"
{ "cmd": "ports" }                                  // nuova scansione delle porte seriali
{ "cmd": "driver", "driver": "pwm" }                // scs0009 | pwm
{ "cmd": "connect",    "port": "COM3" }
{ "cmd": "disconnect" }
{ "cmd": "target", "target": "left" }
{ "cmd": "set",    "target": "left", "angles": { "pointer": [0, 0], ... } }
{ "cmd": "pose",   "target": "left", "name": "close" }
{ "cmd": "middle", "target": "left" }
{ "cmd": "torque", "target": "left", "on": true }   // solo SCS0009
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

## Progettazione della sicurezza

| Voce | Descrizione |
|---|---|
| **Limiti di posa** | Valori di posa ±120° (`limits` di `config.json`); tutte le 19 pose sono state verificate per restare entro i limiti |
| **Deduplicazione delle modifiche** | le variazioni < 0,5° non vengono inviate, per evitare che il bus venga saturato dal rumore |
| **Limitazione della frequenza di scrittura** | intervallo minimo 20 ms per SCS0009; pilotaggio diretto PWM circa 30 ms |
| **Arresto di emergenza** | SCS0009: rilascia tutta la coppia; PWM: invia `0xFF` per interrompere il gesto, i servo restano alimentati e mantengono la posizione |
| **Protezione all'uscita** | SCS0009: Ctrl+C disattiva la coppia; PWM: dopo la disconnessione della seriale i servo mantengono la posizione |
| **Debug con una sola mano** | `--hand left/right` |

---

## Domande frequenti

**Riconoscimento della telecamera impreciso** → luce uniforme, palmo rivolto verso l'obiettivo. In `tracking.js` un `SMOOTH` (predefinito 0.35) più alto rende il movimento più fluido ma più lento.

**Gesti della telecamera sbagliati, un dito non segue** → verifica prima che tutte e tre le pose siano state acquisite (stato verde); se la direzione è invertita riacquisisci la posa corrispondente; il pollice si flette soltanto e non partecipa alla divaricazione.

**A metà pugno un servo si inverte di colpo** → verifica che la divaricazione si annulli con la curvatura fino a 0 (`side *= (1 - curl)`) e che segno/ampiezza del valore di controllo della divaricazione non siano anomali.

**Problemi di direzione/ID/posizione centrale SCS0009** → vedi [Controllo web SCS0009](scs0009.md) e [Messa a punto e calibrazione SCS0009](../06-servo-tuning/scs0009.md).

**Problemi di connessione/baudrate/calibrazione PWM** → vedi [Controllo web PWM](pwm.md).

**Altre domande** → [FAQ](../08-faq/faq.md).
