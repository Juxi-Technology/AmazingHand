[Deutsch](../de/README.md) | [English](../en/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | Italiano | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (Brasil)](../pt-br/README.md) | [Português (Portugal)](../pt-pt/README.md) | [简体中文](../zh-hans/README.md) | [繁體中文](../zh-hant/README.md)

# AmazingHand Web Control

Pilota la mano robotica AmazingHand direttamente dal browser — **mano destra o sinistra**, con due modi per comandarla:

- **Manuale** — 8 slider per i servo + 19 pose predefinite + ritorno alla posizione centrale con un clic
- **Teleoperazione con la camera** — MediaPipe gira localmente nel browser e mappa la tua mano sulle dita in tempo reale (il video non lascia mai la macchina)
- **Interfaccia bilingue** — passa da cinese a inglese nell'angolo in alto a destra; la scelta viene ricordata dal browser

La mappa dei servo, la libreria di pose e le formule di conversione sono allineate a
[AmazingHandControl](https://github.com/pollen-robotics/AmazingHand) (la GUI ufficiale).

---

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

Poi apri **http://localhost:8000** in un browser.

### Selezionare la porta seriale nella pagina

In cima alla pagina c'è una barra degli strumenti: prima scegli il driver, poi la porta seriale:

```
Driver  [SCS0009 bus ▾]  Port  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [Refresh]  [Connect]  [Disconnect]  Connected to COM3
```

- Il menu a tendina **Driver**: **bus SCS0009** (servo bus ufficiali, predefinito) o **PWM (ESP32-S3)** (vedi [Versione con servo PWM](#versione-con-servo-pwm-esp32-s3-a-pilotaggio-diretto))
- Il menu a tendina della porta elenca tutte le porte seriali presenti sulla macchina. I chip USB-seriale più comuni (CH34x / CP210x / FTDI …) sono contrassegnati con **★** e ordinati per primi
- **Refresh** esegue una nuova scansione (usalo dopo aver collegato la scheda)
- **Connect** apre la porta selezionata; subito dopo la mano torna in posizione centrale
- **Disconnect** disattiva prima la coppia, così i servo non restano bloccati dove si trovano (la versione PWM non ha comandi di coppia, vedi la spiegazione sotto)
- Per cambiare porta, seleziona quella nuova e fai clic su Connect — la vecchia porta viene chiusa automaticamente

> **`--no-connect` è pensato proprio per questo flusso**: il server si avvia senza toccare alcuna porta seriale,
> quindi non può prenderne una sbagliata e far sobbalzare la mano. Togli il flag se vuoi che si connetta all'avvio.

I log seriali finiscono in `server.log` (se avvii tramite un file `.bat`, la finestra scompare in un lampo — leggi direttamente il file).

### Verifica del cablaggio

Elenca gli ID dei servo trovati e li verifica mano per mano confrontandoli con `config.json`.

```bash
python tools/scan_servos.py --port COM9
```

Sostituisci COM9 con la tua porta effettiva.

> Questo strumento vale solo per i **servo bus SCS0009**. Per la verifica del cablaggio della versione PWM, vedi la sezione seguente, oppure usa `AmazingHand-PWM/tools/serial_test.py` o la pagina web.

---

## Versione con servo PWM (ESP32-S3 a pilotaggio diretto)

La pagina web supporta due tipi di hardware: i servo bus SCS0009 ufficiali e 8 servo PWM con ESP32-S3. Nella versione PWM è l'ESP32-S3 a generare direttamente gli 8 segnali PWM; il computer invia solo comandi via seriale e **non serve alcuna scheda driver di bus**.

### Hardware e cablaggio

| Voce | Modello |
|------|---------|
| MCU | Scheda di sviluppo ESP32-S3 (Youxin YX-ESP32-S3 o equivalente) |
| Servo | 8 servo PWM — il firmware è tarato per **servo digitali PTK 7452 MG-D (333 Hz)** |
| Scheda adattatrice | Scheda adattatrice per servo PWM |
| Alimentazione | 5 V / 3 A, con massa comune tra scheda adattatrice ed ESP32 |

> Il servo è dichiarato 4,5 kg·cm a 7,4 V; con l'alimentazione 5 V/3 A usata qui, aspettati circa 2,8–3 kg·cm.

Canali PWM → GPIO:

| Canale | GPIO | Giunto | Canale | GPIO | Giunto |
|------|------|------|------|------|------|
| PWM1 | 4 | Giunto 1 dell'indice | PWM5 | 15 | Giunto 1 dell'anulare |
| PWM2 | 5 | Giunto 2 dell'indice | PWM6 | 16 | Giunto 2 dell'anulare |
| PWM3 | 6 | Giunto 1 del medio | PWM7 | 17 | Giunto 1 del pollice |
| PWM4 | 7 | Giunto 2 del medio | PWM8 | 18 | Giunto 2 del pollice |

> ⚠️ I comuni servo analogici a 50 Hz come l'SG90 non possono sostituire direttamente il firmware a 333 Hz. Per cambiare modello di servo bisogna modificare insieme `LEDC_FREQ` e la taratura della larghezza d'impulso e verificare di nuovo.

> Il cablaggio è identico per entrambe le mani: in ogni coppia di dita il servo destro è il canale dispari e il sinistro il pari; l'indice è sempre CH1/2. Le differenze sinistra/destra sono solo nel codice.

### Caricare il firmware

Codice sorgente e file precompilati del firmware sono in [`AmazingHand-PWM/`](../../../AmazingHand-PWM/README.md):

```bash
# metodo 1: ESP-IDF (v5.x / v6.x)
cd AmazingHand-PWM/firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor

# metodo 2: bin precompilato (richiede esptool)
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  AmazingHand-PWM/firmware/prebuilt/amazinghand_pwm.bin
```

All'accensione la seriale stampa:

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

### Connessione dalla pagina web

1. Nel menu **Driver** in alto seleziona **PWM (ESP32-S3)**
2. Fai clic su **Add port…** e seleziona la porta USB dell'ESP32-S3
3. Fai clic su **Connect**: la pagina esegue automaticamente l'handshake (NOP), invia la scelta della mano e torna alla posizione centrale
4. Poi controlla con gli slider, le pose predefinite e la teleoperazione con la camera; il titolo delle dita mostra **CH 1/2 …** (numero di canale PWM)

### Differenze rispetto alla versione SCS0009

| Voce | Versione bus SCS0009 | Versione PWM |
|------|----------------------|--------------|
| Baudrate seriale | 1,000,000 | **115,200** |
| Scheda driver | Scheda driver bus USB | ESP32-S3 + scheda adattatrice PWM |
| Coppia | Attivabile/rilasciabile | **Nessuna** (il firmware non ha comandi di coppia, il pulsante viene nascosto) |
| Arresto di emergenza | Rilascia tutta la coppia | Invia `0xFF` per interrompere il gesto; i servo restano alimentati e mantengono la posizione |
| Velocità | Supporta il parametro di velocità | I frame in pilotaggio diretto non hanno parametro di velocità |
| Retroazione | Lettura di posizione/temperatura/tensione/velocità | **Nessuna lettura**; blocco o perdita di passi non rilevabili |
| Mano destra/sinistra | ID servo diversi | Stessi canali, si cambia con `0xF1` (influenza soprattutto i gesti del firmware; le pose della pagina usano la mappatura della rispettiva mano) |

### Calibrazione degli angoli

La pagina converte i valori di posa in 8 angoli da 0 a 180°, con la formula predefinita:

```
angle = 90 + dir × scale × valore di posa + offset
```

- Per ogni dito il primo canale ha `dir = -1`, il secondo `dir = +1`
- Per impostazione predefinita `scale = 1` e `offset = 0`, cioè si rispecchia direttamente l'angolo dell'asse del servo
- La mano sinistra applica prima `mirror_pose`, scambiando i due valori di posa di ogni dito

Se sulla macchina reale la direzione è opposta o il centro è sfalsato, modifica `pwm.calibration` in [`config.json`](../../../Amazinghand-web-io/config.json):

```jsonc
"pwm": {
  "calibration": {
    "right": {
      "pointer": { "scale": 1.0, "offset_deg": [0, 0] }
    }
  }
}
```

- Direzione opposta: imposta `scale` del dito corrispondente a `-1`
- Offset del centro: regola `offset_deg` (separatamente per i due canali)
- Procedura dito per dito: torna al centro → trascina un singolo dito → osserva direzione/centro → modifica `scale`/`offset_deg` → ricarica la pagina e riprova

### Domande frequenti

- **Connessione fallita / ESP32 non risponde**: verifica che il baudrate sia 115200, che sia selezionata la porta COM dell'ESP32, che l'alimentazione sia 5 V/3 A e che ci sia massa comune; all'apertura della porta l'ESP32 può resettarsi e la pagina ritenta automaticamente il NOP
- **I servo non si muovono o tremano**: verifica prima che i servo siano digitali a 333 Hz (PTK 7452 MG-D o equivalenti) e che l'alimentazione sia sufficiente; l'SG90 richiede una modifica del firmware
- **Direzione invertita**: imposta `scale` del dito corrispondente a `-1`
- **Centro sbagliato**: regola `offset_deg` del canale corrispondente
- **Messaggio «occupato (gesto in corso)»**: il firmware sta eseguendo un gesto integrato; attendi che finisca o premi l'arresto di emergenza (`0xFF`)
- **Scansione dei servo**: `tools/scan_servos.py` vale solo per SCS0009; per il PWM usa `AmazingHand-PWM/tools/serial_test.py` o la pagina web

---

## Mappa dei servo

Fonte: `DEFAULT_HAND_SERVOS` in `AmazingHandControl/hand_logic.py` e
`docs/zh-hans/CONFIG_FORMAT.md`.

| Dito | ID mano destra | ID mano sinistra |
|---|---|---|
| Anulare | 5, 6 | 11, 12 |
| Medio | 3, 4 | 13, 14 |
| Indice | 1, 2 | 15, 16 |
| Pollice | 7, 8 | 17, 18 |

### I due servo di un dito svolgono compiti diversi ⚠️

```
servo1 (ID dispari) = asse di flessione      aperto ↔ chiuso
servo2 (ID pari)    = asse di divaricazione  dita unite ↔ separate
```

L'interfaccia mostra esattamente questi due assi. **«Il dito non si divarica / non si chiude» significa che l'asse di divaricazione (splay) non si sta muovendo** —
una V a forbice deriva da uno splay dell'indice `+17` e uno splay del medio `−30` (uno positivo, uno negativo).

Sul bus vengono combinati:

```
servo1 = flessione + divaricazione
servo2 = flessione − divaricazione
```

Intervallo (derivato dalle 19 pose ufficiali più la posizione centrale):

| Asse | Intervallo | Significato |
|---|---|---|
| Flessione | −50 ~ +90 | aperto (negativo) ↔ chiuso (positivo) |
| Divaricazione | −45 ~ +45 | unite (negativo) ↔ separate (positivo) |

**Due regole sugli ID** (sbagliarle brucia i servo o inverte il movimento):

1. **Gli ID dispari sono il primo servo di un dito, quelli pari il secondo.** Vale su entrambe le mani
   (anche a sinistra 11/12, 13/14 … si alternano). Il secondo servo è **montato al contrario**, quindi va negato nella conversione.
2. **La mano sinistra non è 9–16, ma 11–18, numerata a partire dall'anulare.** Cablarla come 1–8 in sequenza è sempre sbagliato.

![Both_Hands-IDs](../../Both_Hands-IDs.jpg)

---

## Conversione

Identica a `apply_pose()` in `AmazingHandControl` (verificata posa per posa):

```
1) quando mirror_pose è true, scambia prima i due valori di servo di ogni dito
2) servo_deg = (ID dispari ? +1 : -1) × (valore di posa − angle_offset_deg)
```

| Mano | angle_offset_deg | mirror_pose |
|---|---|---|
| Destra | `0` | **sì** ⚠️ |
| Sinistra | `-35.16` | sì |

`-35.16°` è lo scostamento fisico di mezzo slot dei corni dei servo della mano sinistra rispetto alla destra, ricavato dalla configurazione ufficiale.

> **A proposito di `mirror_pose` — questa build differisce da quella ufficiale**
>
> Nel riferimento ufficiale solo la mano sinistra è `true`. **Anche il modulo della mano destra di questa
> build ha le coppie di servo montate al contrario**, quindi pure la destra è `true`.
>
> Lo scambio inverte solo la **divaricazione**, mai la flessione: `base = (a+b)/2` resta invariato con uno
> scambio, mentre `side = (a−b)/2` cambia segno. Quindi se la divaricazione di una mano risulta speculare,
> questo è il primo parametro da controllare.

L'array delle pose è sempre di 8 valori nell'ordine **`[ring, middle, index, thumb]`**, due per dito —
identico byte per byte all'ufficiale `data/hand_config.yaml`, così puoi confrontarli direttamente.

### Esempi svolti

| Posa | Destra | Sinistra |
|---|---|---|
| `open` `[-35]*8` | ID5 **−35** / ID6 **+35** | ID11 **+0.16** / ID12 **−0.16** |
| `close` `[75]*8` | ID5 **+75** / ID6 **−75** | ID11 **+110.16** / ID12 **−110.16** |
| middle `[-17.578]*8` | ID5 **−17.58** / ID6 **+17.58** | ID11 **+17.58** / ID12 **−17.58** |

> **Nota che il `close` della mano sinistra richiede ±110.16°**, ben oltre quello della destra. Per questo `config.json`
> imposta il limite a **±120°** (la gamma completa dell'SCS0009 è di circa ±150°). Un limite di ±90 taglierebbe il pugno della mano sinistra.

---

## Pose predefinite (19)

| Posa | | Posa | |
|---|---|---|---|
| `open` | Aperto | `wave1` | Ciao |
| `close` / `stone` | Pugno | `wave_r` / `wave_l` | Scorri a destra / a sinistra |
| `ok` | OK | `ring_close` | Solo anulare |
| `greeting` | Saluto | `middle_close` | Solo medio |
| `victory` / `two` / `scissors` | Vittoria / Due | `pointer_close` | Solo indice |
| `paper` | Carta | `thumb_close` | Solo pollice |
| `one` / `three` | Uno / Tre | `hifive` | Batti il cinque |

Per modificare una posa, aggiorna la sezione `poses` di `config.json`; le chiavi corrispondono ai nomi nello YAML ufficiale.

### Destra e sinistra possono usare valori diversi

All'interno di una posa, `positions` è **condiviso da entrambe le mani**. Se una mano necessita di un set diverso
a causa di differenze nell'assemblaggio meccanico, aggiungi una chiave `right` o `left` a quella voce e questa sostituisce `positions`:

```jsonc
"close": {
  "label": "Fist",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // condiviso da entrambe le mani
  "right":     [ ... 8 valori ... ]                 // opzionale: solo mano destra
}
```

---

## Due modalità

| Modalità | Comportamento |
|---|---|
| **Mano destra** | Invia solo agli 8 servo della mano destra |
| **Mano sinistra** | Invia solo agli 8 servo della mano sinistra (specchiatura + offset di −35.16° applicati automaticamente) |

Una mano alla volta. Entrambe le mani sono sullo stesso bus; cambia con **Target** in alto.
Il cambio non disturba l'altra mano — mantiene la posa in cui si trova.

---

## Teleoperazione con la camera

I landmark della mano di MediaPipe girano localmente nel browser (asset in `web/mediapipe/`, funzionano offline).
I 21 landmark vengono convertiti in valori di posa per 4 dita e inviati in streaming alla mano selezionata.

### 1. Acquisisci prima tre pose

Avvia la camera, poi metti la mano nella posa e fai clic sul pulsante di acquisizione di quella posa (circa 1 secondo di media).
L'ordine non conta; fai di nuovo clic sullo stesso pulsante per riacquisire. **Lo stato diventa verde solo quando tutte e tre sono acquisite** —
prima di allora non viene inviato nulla, quindi la mano resta in posizione centrale.

| Pulsante | Posa | Fornisce |
|---|---|---|
| ① Divaricate | Dita dritte e divaricate, pollice rivolto verso l'esterno | L'estremo «dritto» della flessione + l'estremo «divaricato» della divaricazione |
| ② Unite | Dita dritte e unite, pollice contro l'indice | L'estremo «unite» della divaricazione |
| ③ Pugno | Chiudi a pugno, pollice piegato verso il palmo | L'estremo «chiuso» della flessione |

### 2. Ogni asse è una retta passante per due punti misurati

Sia la flessione sia la divaricazione usano **due estremi misurati per definire una retta**:

```
t      = (measured − endpointA) / (endpointB − endpointA)      // limitato a 0..1
target = A.target + (B.target − A.target) × t
```

Il vantaggio: **il segno della misura di ogni dito viene assorbito automaticamente** — quindi non c'è
alcuna casella «inverti questo dito» da spuntare. (Indice e anulare stanno su lati opposti della linea centrale, e
la catena articolare del pollice è diversa, quindi le loro direzioni sono davvero opposte — due estremi misurati lo assorbono.)

I target degli estremi si trovano nella sezione `camera` di `config.json`:

| Asse | Estremi | Anulare | Medio | Indice |
|---|---|---|---|---|
| Flessione | dritto → pugno | −50 → 90 | −50 → 90 | −50 → 90 |
| Divaricazione | unite → divaricate | −45 → +45 | 0 → 0 | +45 → −45 |

Entrambi gli estremi della divaricazione sono 0 per il dito medio (non oscilla lateralmente).

### 3. Il pollice si flette soltanto ⚠️

Il CMC del pollice è un'**articolazione a sella (opponibile)**, e la sua flessione si accoppia strettamente con l'abduzione —
con il pollice accostato all'indice si è già in una posizione di divaricazione, quindi lo «zero di flessione»
misurato lì è contaminato. Forzandolo su due assi, entrambi risultano sbagliati.

Quindi il pollice **si flette soltanto; la sua divaricazione è sempre 0** (entrambi i suoi servo ricevono lo stesso valore). Le due
pose di riferimento che gli servono sono la ① (rivolto verso l'esterno) e la ③ (rivolto verso il palmo) — non serve acquisire altro.

### 4. La divaricazione si annulla man mano che il dito si piega

La divaricazione finale viene scalata per:

```
side = side_measured × (1 − curl)
```

`splayDeg` è la proiezione della direzione MCP→PIP sull'asse laterale del palmo, e la flessione del dito
**ruota esattamente attorno a quell'asse** — oltre una certa curvatura la proiezione cambia segno e la
«divaricazione» misurata scatta all'improvviso verso l'estremo opposto.

Senza l'attenuazione, quello scatto passa attraverso `servo2 = flessione − divaricazione` e trascina il **servo con ID pari**
in inversione. (L'ID dispari riceve `flessione + divaricazione`, quindi si muove nello stesso verso, solo più velocemente — non si nota.)
Il sintomo è «a metà strada verso il pugno, i servo 12 e 16 si invertono all'improvviso» — il 12 è il servo di
divaricazione dell'anulare sinistro e il 16 quello dell'indice sinistro, esattamente i due con target di divaricazione non nulli.

Con l'attenuazione, la divaricazione è **esattamente 0** a curvatura completa, per quanto selvaggia diventi la misura.
E poi un pugno dovrebbe comunque avere le dita unite.

### 5. Colori dello scheletro

| Dito | Colore |
|---|---|
| Pollice | arancione |
| Indice | rosso |
| Medio | blu |
| Anulare | giallo |
| Mignolo | grigio tenue |
| Ossa del palmo | grigio neutro |

Il mignolo non viene usato per la mappatura dei gesti, ma il suo **MCP di base (landmark 17) definisce il sistema di
coordinate del palmo della mano destra**, quindi non può essere semplicemente scartato.

### Promemoria per la regolazione

| Cosa vuoi cambiare | Dove |
|---|---|
| Valori target degli assi | sezione `camera` di `config.json` |
| **La divaricazione di sinistra e destra va in versi opposti** | imposta quella mano a `-1` in `camera.side_sign` (`1` = invariato) |
| Fluidità | `SMOOTH` in `tracking.js` (predefinito 0.35; più basso è più stabile ma più lento) |
| Quanto rapidamente viene rilevata una curvatura | riacquisisci le tre pose |

`side_sign` si applica alla mano selezionata sotto **Target**. Modificalo e ricarica la pagina —
non serve riavviare il server:

```jsonc
"side_sign": { "right": 1, "left": -1 }   // inverti l'intero asse di divaricazione sulla mano sinistra
```

La flessione non è influenzata da `side_sign`.

---

## Struttura del progetto

```
Amazinghand-web/
├── config.json          mappa dei servo / libreria di pose / sequenze / limiti (generati dallo YAML ufficiale)
├── server.py            backend: seriale + file statici + WebSocket
├── requirements.txt
├── README.md            inglese
├── tutorials/           de · en · es · fr · it · ja · ko · pt-br · pt-pt · zh-hans · zh-hant
├── tools/
│   └── scan_servos.py   scansiona il bus cercando i servo e ne verifica gli ID
└── web/
    ├── index.html · app.js · tracking.js · style.css
    ├── i18n.js          stringhe dell'interfaccia (dizionario cinese/inglese + switch in alto a destra)
    └── mediapipe/       asset MediaPipe (inclusi localmente, offline, ~42 MB)
```

Protocollo frontend/backend:

```jsonc
// frontend → backend   target: "left" | "right"
{ "cmd": "ports" }                                  // nuova scansione delle porte seriali
{ "cmd": "connect",    "port": "COM3" }
{ "cmd": "disconnect" }
{ "cmd": "target", "target": "left" }
{ "cmd": "set",    "target": "left", "angles": { "pointer": [0, 0], ... } }
{ "cmd": "pose",   "target": "left", "name": "close" }
{ "cmd": "middle", "target": "left" }
{ "cmd": "torque", "target": "left", "on": true }
{ "cmd": "stop" }

// backend → frontend
{ "type": "state", "hands": {...}, "poses": {...}, "positions": {...},
  "axes": {...}, "camera": {...}, "target": "left",
  "limits": {...}, "port": { "available": [...], "current": "COM3", "connected": true } }
{ "type": "ports" | "connected" | "disconnected", "ports": [...], ... }
{ "type": "error", "msg": "connect COM_FAKE failed: the system cannot find the file specified." }
```

---

## Sicurezza

| Voce | |
|---|---|
| **Limiti di posa** | ±120° (`limits` in `config.json`); tutte e 19 le pose verificate per restare all'interno |
| **Deduplicazione delle modifiche** | le variazioni inferiori a 0.5° non vengono inviate, così il bus non viene inondato di rumore |
| **Throttling in scrittura** | minimo 20 ms tra una scrittura e l'altra |
| **Arresto di emergenza** | il pulsante rosso nell'interfaccia rilascia tutti i servo in una volta |
| **Protezione all'uscita** | la coppia viene rilasciata automaticamente su Ctrl+C |
| **Debug su una sola mano** | `--hand left/right` |

---

## Risoluzione dei problemi

**Il movimento è invertito** → controlla che il cablaggio rispetti «prima gli ID dispari»; sulla mano sinistra verifica anche `angle_offset_deg = -35.16`.

**Il pugno della mano sinistra è troppo piccolo / i servo ronzano** → probabilmente il limite è ancora ±90; controlla che `config.json` riporti ±120.

**Un dito non si muove / «expected N motors, found M»** → esegui `tools/scan_servos.py`; gli ID della mano sinistra sono i più facili da cablare male.

**La posizione centrale è fuori posto** → il valore centrale `-17.578125` è convertito dal raw ufficiale 451/571.
Per calibrare sul tuo assemblaggio, modifica `middle.positions` in `config.json`.

**Il tracking della camera è instabile** → illuminazione uniforme, palmo rivolto verso la camera. `SMOOTH` in `tracking.js`
(predefinito 0.35) — più alto è più fluido ma più lento.

**Gesti della camera sbagliati / un dito non segue** → vedi la sezione Teleoperazione con la camera qui sopra. Controlla prima tre cose:

1. **Sono state acquisite tutte e tre le pose?** — lo stato deve essere verde; prima di allora non viene inviato nulla e la mano resta in posizione centrale
2. **Una direzione invertita significa che quella posa è stata acquisita al contrario** — basta riacquisire quel singolo pulsante, nessuna modifica al codice
3. **Il pollice non deve divaricarsi** — si flette soltanto, vedi la sezione 3 qui sopra

**Un servo si inverte di colpo a metà strada verso il pugno** → quel servo dovrebbe avere un **ID pari** (l'asse di divaricazione, ad es. sinistra 12 / 16).
Normalmente la divaricazione si annulla con la curvatura e non salta mai; se vedi questo comportamento, la riga `side *= (1 - curl)` in
`tracking.js` non sta avendo effetto, oppure `curl` non viene calcolato.
