[English](../en/CHANGES.md) | [Deutsch](../de/CHANGES.md) | [Español](../es/CHANGES.md) | [Français](../fr/CHANGES.md) | Italiano | [日本語](../ja/CHANGES.md) | [한국어](../ko/CHANGES.md) | [Português (BR)](../pt-br/CHANGES.md) | [Português (PT)](../pt-pt/CHANGES.md) | [简体中文](../zh-hans/CHANGES.md) | [繁體中文](../zh-hant/CHANGES.md)

# AmazingHand Controller · Registro delle modifiche e motivazioni

Cosa è stato modificato rispetto al progetto originale, perché e quale sia il risultato effettivo.

Progetto originale: `Betatester777/AmazingHandControl` (GUI + CLI in Python per l'AmazingHand)
Hardware: JuxiTechnology AmazingHand (8× servo Feetech SCS0009, feedback del potenziometro) — **entrambe le mani supportate**, selezionate all'avvio

---

## Indice

1. [Ricalibrazione del sistema di angoli](#1-ricalibrazione-del-sistema-di-angoli)
2. [Pulsanti globali: pilotare posizioni raw esatte](#2-pulsanti-globali-pilotare-posizioni-raw-esatte)
3. [Nuovo pulsante Posizione intermedia](#3-nuovo-pulsante-posizione-intermedia)
4. [GUI e CLI in disaccordo (il bug principale)](#4-gui-e-cli-in-disaccordo-il-bug-principale)
5. [Correzioni ai dati delle pose](#5-correzioni-ai-dati-delle-pose)
6. [Riproduttore di sequenze: temporizzazione e diagnostica](#6-riproduttore-di-sequenze-temporizzazione-e-diagnostica)
7. [Nuova riga della posizione raw nel Feedback dei servo](#7-nuova-riga-della-posizione-raw-nel-feedback-dei-servo)
8. [**Supporto per mano sinistra e destra**](#8-supporto-per-mano-sinistra-e-destra)
9. [Rilevamento automatico della porta seriale](#9-rilevamento-automatico-della-porta-seriale)
10. [Riferimento di configurazione](#10-riferimento-di-configurazione)
11. [Risultati misurati](#11-risultati-misurati)
12. [Riepilogo file per file](#12-riepilogo-file-per-file)

---

## 1. Ricalibrazione del sistema di angoli

### 1.1 Limiti di angolo: `0..110` → `-75..75`

L'originale era calibrato su `0° = aperto, 110° = chiuso`. La corsa effettiva di questa mano cade in `-75..75`, quindi tutto è stato ricalibrato.

**`data/config.yaml`**

| Chiave | Prima | Dopo |
|---|---|---|
| `servo_min` / `servo_max` | -40 / 110 | **-75 / 75** |
| `base_min` / `base_max` | 0 / 110 | **-75 / 75** |
| `side_min` / `side_max` | -40 / 40 | **-35 / 35** |
| `left_open` | `[32, -40]` | **`[32, -35]`** |
| `right_open` | `[-40, 32]` | **`[-35, 32]`** |
| `left_closed` / `right_closed` | `[110, 110]` | **`[75, 75]`** |
| `center_closed` | `[110, 110]` | **`[75, 75]`** |

**Tutte e 19 le pose sono state riscalate**, ad es. `open` da `[0]*8` a `[-35]*8`, `close` da `[110]*8` a `[75]*8`.

### 1.2 Divaricazione laterale: `±40°` → `±35°`

Lo slider laterale normalizza con `u = |side_offset| / |side_min|`, quindi modificare solo il limite **non** cambia di quanto si divaricano davvero le dita — riscala soltanto lo slider. Per cambiare la divaricazione fisica bisogna modificare anche `auto_extremes`. Con entrambi modificati:

| | Prima (±40) | Dopo (±35) |
|---|---|---|
| Intervallo dello slider | −40 … +40 | −35 … +35 |
| Tutto aperto, all'estremo laterale | `(32, -40)`, divaricazione **72°** | `(32, -35)`, divaricazione **67°** |

### 1.3 Allineamento al riferimento del produttore

La demo Arduino del produttore (`Amazing_RHand_Demo.ino`) converte così:

```c
float Step = 0.293; // 300°/1024
sc.RegWritePos(1, MiddlePos[0] + Pos_1 / Step, 0, Speed);
```

E rustypot 1.4.2 (`src/servo/feetech/scs0009.rs`):

```rust
fn to_raw(value: f64) -> i16 {
    let a = (1024.0 * value / (300.0_f64.to_radians()) + 511.0) as i16;
    a.to_be()
}
```

**Conclusione: entrambe le parti usano la stessa scala in gradi** (0,29297°/passo, fondo scala 300°, raw 0–1023) — non c'è errore di rapporto. L'unica differenza sistematica è il punto zero:

- rustypot centra sempre su raw **511**
- il firmware del produttore usa un valore di calibrazione per servo, `MiddlePos = {451, 571, 451, 571, 451, 571, 451, 571}`

Differiscono di **±60 raw = ±17.6°**. È esattamente ciò a cui pone rimedio il pulsante "Middle position" descritto più avanti.

---

## 2. Pulsanti globali: pilotare posizioni raw esatte

### 2.1 Il problema

L'originale `open_all()` / `close_all()` aveva angoli hard-coded:

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

Quei valori provengono dalla **vecchia scala di calibrazione** (0 = aperto, 110 = chiuso). Dopo la ricalibrazione a `-35 / 75`:

- `open_all` impostava 0° → converte in raw **511**, cioè all'incirca il centro meccanico — le dita non si aprivano mai
- `close_all` impostava 110° → limitato da `base_max = 75`, quindi arrivava solo a 75, mentre l'etichetta continuava a mostrare 110°

### 2.2 La correzione: un percorso diretto verso la posizione raw

Il percorso degli angoli passa per il modello di interpolazione `base/side`, che non può centrare esattamente un valore raw arbitrario (vedi sezione 4). Perciò i pulsanti globali hanno ricevuto un percorso che scrive direttamente le posizioni raw dei servo.

**Un dettaglio implementativo importante:** questo *non* usa `sync_write_raw_goal_position` di rustypot. Leggendo il sorgente generato dalle macro si vede che l'API raw scrive `values.to_le_bytes()` direttamente sul filo, mentre l'API che converte applica prima `to_be()`:

```rust
fn to_raw(value: f64) -> i16 { let a = (...) as i16; a.to_be() }
// sync_write_raw_*: values.iter().map(|v| v.to_le_bytes())   <- no to_be
```

Passando `451` verrebbe quindi emesso `0xC301` (49921). Il codice usa invece `sync_write_goal_position` (radianti) e risolve per i radianti che cadono **esattamente** sul valore raw desiderato, prendendo il punto medio di ogni passo raw per evitare errori di troncamento.

### 2.3 Obiettivi raw dei tre pulsanti

Aggiunto `raw_positions` a `data/config.yaml` (indice 0 → ID servo 1):

```yaml
raw_positions:
  open:   [260, 760, 260, 760, 260, 760, 260, 760]
  close:  [760, 260, 760, 260, 760, 260, 760, 260]
  middle: [451, 571, 451, 571, 451, 571, 451, 571]
```

| Pulsante | Azione | Raw degli ID servo 1–8 |
|---|---|---|
| ✋ Open All | completamente esteso | 260, 760, 260, 760, 260, 760, 260, 760 |
| ✊ Close All | completamente chiuso | 760, 260, 760, 260, 760, 260, 760, 260 |
| ⊙ Center All | ricentraggio laterale (nessuna modifica di apertura/chiusura) | — |
| **Middle position** | **ritorno al centro calibrato** | 451, 571, 451, 571, 451, 571, 451, 571 |

> ⚠️ `raw_positions` sono **valori di calibrazione per mano**. Il commento del produttore stesso recita *"replace values by your calibration results"* — rimisurate dopo aver scambiato mani o servo.

### 2.4 Il compromesso con la sincronizzazione degli slider

Gli obiettivi raw aggirano il modello `base/side`, quindi non hanno un equivalente esatto nello slider. Dopo l'esecuzione di un pulsante, gli slider vengono impostati all'intero più vicino:

| Posizione | Lo slider mostra |
|---|---|
| open | base = −73, side = 0 |
| close | base = +73, side = 0 |
| middle | base = −17, side = 0 |

Il costo: toccare uno slider in seguito sposta la mano fino a ~1 unità raw (0,3°) dal bersaglio. È deliberato — centrare esattamente la posizione calibrata conta di più.

---

## 3. Nuovo pulsante Posizione intermedia

Posto a destra di `✋ Open All` / `✊ Close All` / `⊙ Center All`. Riporta la mano al **centro meccanico calibrato dal produttore** (raw 451/571).

**Perché è necessario:** il punto medio tra `open_all` e `close_all` *non* è il centro meccanico. Il centro del produttore è `MiddlePos`, che dista ±60 raw (±17.6°) da raw 511. Dopo l'accensione si desidera uno zero ben definito e ripetibile.

---

## 4. GUI e CLI in disaccordo (il bug principale)

### 4.1 Sintomo

**La stessa posa produce un movimento della mano diverso se applicata con `✓ Apply` della GUI oppure con `--pose` della CLI.**

### 4.2 Causa principale

La GUI applicava le pose attraverso:

```
set_positions(p1, p2)  →  decompose into (base, side), stored in the sliders
                       →  get_positions() recomputes via compute_auto_positions() in Auto mode
```

Ma `compute_auto_positions` **non** è l'inversa esatta di `decompose_servo_positions` (il suo centro e i suoi estremi sono valori empirici). L'`apply_pose()` della CLI invia i valori direttamente.

Misurato: **12 pose su 19 erano distorte**, fino a 32°:

| Posa | Memorizzato | La GUI inviava davvero | Scostamento |
|---|---|---|---|
| `ring_close` | Ring `(75, -35)` | Ring `(43, -5)` | **32° / 30°** |
| `middle_close` | Middle `(75, -35)` | Middle `(43, -5)` | **32° / 30°** |
| `pointer_close` | Pointer `(75, -35)` | Pointer `(43, -5)` | **32° / 30°** |
| `thumb_close` | Thumb `(75, -35)` | Thumb `(43, -5)` | **32° / 30°** |
| `wave1` | `(-75, -3)` | `(-75, 9)` | 12° |
| `hifive` | Thumb `(-75, -3)` | Thumb `(-75, 9)` | 12° |
| `greeting` | Ring `(-18, -57)` | Ring `(-10, -68)` | 8° / 11° |
| `victory` | Middle `(-68, -9)` | Middle `(-75, 1)` | 7° / 10° |
| `paper` | Pointer `(-52, -22)` | Pointer `(-59, -16)` | 7° / 6° |
| `ok` | Pointer `(36, 46)` | Pointer `(38, 43)` | 2° / 3° |

**Lo schema:** le pose simmetriche in cui ogni dito ha `pos1 == pos2` (`open` `close` `stone` `two` `scissors` `one` `three`) tornano esatte. Ogni posa asimmetrica che coinvolge divaricazione laterale deriva.

### 4.3 Correzione

Aggiunta `_send_exact_positions()`, che invia gli angoli direttamente ai servo nell'ordine di `SERVO_PAIRS` (equivalente all'`apply_pose` della CLI). Entrambi i punti di ingresso delle pose ora la usano:

- il pulsante `✓ Apply` in Gestione pose
- `_apply_pose_from_config()` — il riproduttore di sequenze e l'elenco delle pose

Gli slider vengono comunque aggiornati da `set_positions()` per la visualizzazione, ma **non decidono più cosa viene inviato**.

### 4.4 Risultato

Dopo la correzione, **tutte e 19 le pose soddisfano `stored == GUI-sent == CLI-sent`**.

**Effetto collaterale:** i gesti reali nella GUI cambiano, specialmente quelli asimmetrici. È l'effetto voluto della correzione.

---

## 5. Correzioni ai dati delle pose

### 5.1 Quattro pose `*_close` erano scritte in modo errato

```yaml
# Before — target finger (75, -35)
ring_close:    [75, -35, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, -35, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, -35, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, -35]
```

`(75, -35)` si scompone in `base = 20, side = -55` (fuori intervallo) — cioè *"curvato solo al 27%, ruotato a fondo verso sinistra"*, non "chiudi questo dito". Come in `close` e `one`, la forma corretta è `(75, 75)`:

```yaml
# After — target finger fully closed (75, 75), others stay open (-35, -35)
ring_close:    [75, 75, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, 75, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, 75, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, 75]
```

Verificato per scomposizione: il dito bersaglio ha `base = 75` (completamente chiuso), `side = 0` (non sbilanciato da nessun lato).

**Impatto:** la sequenza `finger_roll`, che usa queste quattro pose, solo ora è un vero "arrotola ogni dito a turno".

### 5.2 Il pollice in `greeting` / `paper`

Entrambe avevano originariamente il pollice a `(75, 75)` (completamente chiuso). Per `paper` (布, un palmo aperto e piatto) un pollice chiuso è palesemente sbagliato.

`greeting` è stata inizialmente modificata in `(-75, -3)` (riutilizzando il pollice divaricato di `hifive`), ma i test sull'hardware hanno mostrato che quel passo richiedeva al pollice una corsa di **150°**, che non entra in 1,0 s (vedi 6.3). Stato finale:

```yaml
greeting: [-18, -57, -32, -32, -70, -7, -35, -35]   # thumb (-35, -35), same as open
paper:    [-19, -56, -34, -34, -52, -22, -75, -3]   # keeps the splayed thumb (flat palm)
```

Questo separa i due gesti: `greeting` è un saluto con la mano, in cui il pollice si apre semplicemente in modo naturale; `paper` è un palmo piatto, in cui il pollice si divarica.

---

## 6. Riproduttore di sequenze: temporizzazione e diagnostica

### 6.1 Correzione dei falsi avvisi "non ha raggiunto il bersaglio"

Eseguendo `demo` sull'hardware si sono prodotti tre falsi allarmi:

```
⚠ Pose #42 'greeting': Servos did not reach target! Max error: 52°
```

**Causa principale:** `_log_pose_completion` sottraeva due array che erano in **ordini diversi**.

- `monitor_servos()` scrive la sua cache in **ordine di ID servo**: `latest_actual_positions[servo_id - 1] = ...` (indice 0 = ID1 = Pointer)
- i `target_positions` passati sono un array di posa, in **ordine dei widget** Ring / Middle / Pointer / Thumb (indice 0 = Ring = ID5)

Quindi sottraeva la lettura del Pointer dal bersaglio del Ring.

**Prova** (ricalcolata dal log misurato):

```
target (widget order)   : [-18, -57, -32, -32, -70, -7, -75, -3]
actual (servo-ID order) : [-68.85, -6.74, -33.69, -31.35, -18.46, -54.79, -74.12, -3.22]
compared as-is          -> max error 52°      <-- what the old code did
target reordered        : [-70, -7, -32, -32, -18, -57, -75, -3]
compared in servo order -> max error 2.21°    <-- actually spot on
```

**Correzione:** aggiunte `pose_to_servo_order()` / `servo_to_pose_order()`, applicate prima del confronto; il `current` stampato viene riconvertito in modo che `target` e `current` si allineino colonna per colonna nel log.

### 6.2 Correzione di quando viene eseguito il controllo di raggiungimento

L'originale controllava dopo un **intervallo fisso di 2000 ms** dall'invio:

```python
self.root.after(2000, lambda ...: self._log_pose_completion(...))
```

Ma i passi della sequenza attendono solo 1,0 s, quindi quando il controllo veniva eseguito il passo successivo era già stato inviato — la lettura appartiene necessariamente al movimento *successivo*:

```
25.388  Pose #40 'ok'      sent
26.782  Pose #41 'victory' sent        <- already moved on
27.742  Pose #40 'ok'      checked -> reading is mid-way to victory
```

**Correzione:**

1. `_apply_pose_from_config` ha guadagnato un parametro `check_after`. Un clic su `✓ Apply` per una singola posa resta invariato (2,0 s, poi attesa dell'arresto del movimento); la riproduzione della sequenza passa **il ritardo proprio del passo**, cosicché il controllo cade sul confine del passo (ritardo − 100 ms) e non attende più la fine del movimento.
2. Aggiunta una **protezione da superamento**: `_log_pose_start` registra `current_pose_id`; se nel frattempo un comando più recente ha preso il sopravvento, il controllo di raggiungimento viene saltato e il log mostra `current=<superseded>`.

### 6.3 Regolazione dei ritardi di sequenza

**Velocità efficace** ricavata a ritroso dal log dell'hardware (la velocità 3 è nominalmente 172°/s):

| Posa | Corsa | Errore a 0,9 s | Velocità efficace implicita |
|---|---|---|---|
| `ok` | 110° | 0.5° | 121.7°/s (71% del nominale) |
| `victory` | 110° | 1.0° | 121.1°/s (70%) |
| `greeting` | 132° | 7.0° | 138.9°/s (81%) |

> Sotto carico la velocità reale è solo circa il **70%** di quella nominale. È il numero che conta quando si scelgono i ritardi.

**Modifiche a `demo`:**

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

- `greeting` 1,0 s → **1,5 s**: quel passo percorre 132° (il secondo servo del Ring) e non può concludersi in 1,0 s
- **nuovo `close` finale**: così `demo` termina con la mano chiusa, il che rende anche pulito il loop
- durata totale 7,0 s → **9,5 s**

### 6.4 `wave`: limitare l'oscillazione laterale a ±30°

L'originale `wave_r` / `wave_l` implicava un `side` di **±36** (oltre il limite di ±35, quindi veniva limitato a 35).

Risolvendo `side = base − pos1`, `base = (pos1 + pos2) / 2` si ottiene `pos1 = base − side`, `pos2 = base + side`. Mantenendo `base = −39` e riducendo `side` a ±30:

```yaml
wave_r: [-9, -69, -9, -69, -9, -69, -69, -9]     # was [-3, -75, -3, -75, -3, -75, -75, -3]
wave_l: [-69, -9, -69, -9, -69, -9, -9, -69]     # was [-75, -3, -75, -3, -75, -3, -3, -75]
```

Verificato: `wave_r` ha side `[-30, -30, -30, +30]`, e `wave_l` è il suo speculare dito per dito.

**Effetto collaterale (atteso):** anche la corsa di ogni oscillazione scende da 40°/72° a **34°/60°**. L'onda è complessivamente più stretta, il che non fa che ampliare il margine di temporizzazione.

---

## 7. Nuova riga della posizione raw nel Feedback dei servo

Una riga **`Current (0-1023)`** è posta direttamente sotto `Position (°)`, e mostra la posizione raw del servo in tempo reale.

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

**Compromesso:** nessuna lettura seriale aggiuntiva. Il valore raw deriva dalla posizione che il thread di monitoraggio ha **già** letto, quindi il ciclo di polling non raddoppia il traffico seriale. La precisione è stata verificata in modo esaustivo: **2048 combinazioni (raw 0–1023 × servo pari/dispari) tornano senza alcun errore**.

**Uso:** confrontare direttamente con la calibrazione del produttore — `open` dovrebbe leggere `260 / 760` in alternanza, `middle` dovrebbe leggere `451 / 571`.

> Il nome della riga porta un prefisso di intervallo per distinguerla dall'esistente `Current (mA)` (assorbimento stimato).

---

## 8. Supporto per mano sinistra e destra

### 8.1 Il produttore fornisce due firmware

Il produttore fornisce una demo Arduino separata per ciascuna mano, con parametri completamente diversi:

| | Destra `Amazing_RHand_Demo` | Sinistra `Amazing_LHand_Demo` |
|---|---|---|
| ID servo | **1–8** | **11–18** |
| Dito → ID | index `1,2` / middle `3,4` / ring `5,6` / thumb `7,8` | **ring `11,12` / middle `13,14` / index `15,16` / thumb `17,18`** |
| `MiddlePos` centrale | `[451, 571, 451, 571, …]` | `[571, 451, 571, 451, …]` |

Il tutorial di debug lo dice chiaramente: *"a single hand uses 8 servos; the right hand's IDs must be set to 1-8, and the left hand's to 11-18."*

Si noti che la numerazione della mano sinistra procede **in ordine inverso** (ring per primo) — coerentemente con la sua disposizione meccanica speculare.

### 8.2 Perché cambiare gli ID non basta

Gli ID sono solo il primo livello. Tra le due mani restano due differenze fisiche, e trascurarne una sola distorce i gesti.

#### Differenza 1: un offset di montaggio di 35.16°

Entrambe le mani usano **lo stesso valore di gesto più il proprio `MiddlePos`**:

```c
// Right
#define MiddlePos {451, 571, ...}
Move_Index(-35, 35)  →  ID1 = 451 + (-35)/0.293 = 331.5

// Left
#define MiddlePos {571, 451, ...}
Move_Index(-35, 35)  →  ID15 = 571 + (-35)/0.293 = 451.5
```

Lo stesso gesto "open" cade su valori raw diversi su ciascuna mano. Convertito nello spazio degli angoli di questo programma, differiscono di **120 raw = 35.16°**.

#### Differenza 2: i due servo di un dito sono scambiati

```c
// Right Victory                      // Left Victory
Move_Index (-15, 65);                Move_Index (-65, 15);
Move_Middle(-65, 15);                Move_Middle(-15, 65);
```

Per dito, `(a, b) → (-b, -a)`; in valori di posa ciò significa **scambiare i due numeri di ogni dito**.

Se lo si trascura, la **direzione della divaricazione si inverte** — il sintomo è un segno di vittoria che fa collassare le due dita mentre le dita che dovrebbero stare insieme si divaricano.

> Un facile fraintendimento: in `Perfect` i valori di index e middle sono **identici** su entrambe le mani (`(50,-50)`, `(0,0)`), e solo il pollice differisce. Quindi la regola non è "scambia index e middle" ma un `(-b,-a)` per dito — che per le coppie simmetriche è l'identità.

### 8.3 Implementazione

**Entrambe le mani condividono un unico `hand_config.yaml`.** Le pose memorizzate sono sempre in **ordine mano destra**; la mano sinistra converte in uscita e al ritorno, quindi non c'è una seconda libreria di pose da mantenere.

La conversione risiede in `hand_logic.py`:

| Funzione | Scopo |
|---|---|
| `resolve_hand_config(app_config, hand)` | Sovrappone `hands.<name>` alla configurazione di primo livello (mano destra) |
| `servo_pairs()` / `servo_ids()` | I `(servo1_id, servo2_id)` di quella mano per dito / tutti gli ID servo in ordine crescente |
| `hand_angle_offset()` / `hand_mirrors_pose()` | Leggono i due parametri di differenza della mano |
| `adapt_pose_for_hand(positions, mirror)` | Scambia `(pos1, pos2)` di ogni dito. **Lo scambio è l'inversa di se stesso**, quindi la stessa funzione converte all'applicazione e riconverte al salvataggio |

**Integrata in:**

- GUI: applicazione della posa (il pulsante `✓ Apply` e la riproduzione di sequenza), e salvataggio di una posa
- CLI: `--pose` / `--sequence`

**Gli obiettivi raw dei tre pulsanti globali** sono configurati per mano e non passano per questa conversione (`raw_positions` è scritto sotto `hands.left`).

### 8.4 Utilizzo

La GUI chiede prima di aprirsi:

```
  AmazingHand — which hand?
    1 = right hand  (servo IDs 1-8)
    2 = left hand   (servo IDs 11-18)
  Enter 1 or 2 [1]:
  LEFT hand — servo IDs 11-18
    Ring (11, 12)  Middle (13, 14)  Pointer (15, 16)  Thumb (17, 18)
    middle position raw: [571, 451, 571, 451, 571, 451, 571, 451]
```

Premendo Invio si usa il valore `hand:` di `config.yaml`. Per saltare la richiesta:

```bash
python amazing_hand_gui.py --hand left
python amazing_hand_cmd.py --pose victory --hand left
```

### 8.5 Lista di controllo per il primo utilizzo della mano sinistra

In `hands.left.raw_positions`, solo **middle** è il valore predefinito del produttore (`571, 451`); `open` e `close` sono stati derivati dalla demo del produttore:

| Pulsante | Raw mano sinistra | Origine |
|---|---|---|
| Middle position | `571, 451, …` | Predefinito del produttore |
| Open All | `380, 642, …` | Derivato: lo stesso gesto dell'Open All della mano destra, applicato al `MiddlePos` sinistro |
| Close All | `880, 142, …` | Idem |

**Verificarli in quest'ordine la prima volta che si collega la mano sinistra:**

1. Premere **Middle position** e confermare che la riga `Current (0-1023)` legga `571, 451, 571, 451, …`
2. Premere **Open All** / **Close All** — la corsa deve raggiungere le battute senza bloccarsi
3. Provare `victory` (index e middle che si aprono a V), `greeting` (tre dita insieme), `ok` (le punte di pollice e indice che si toccano)

Se qualcosa non va:

| Sintomo | Modifica |
|---|---|
| Middle position legge un valore errato | `hands.left.raw_positions.middle` |
| Direzione della divaricazione invertita | impostare `hands.left.mirror_pose` su `false` |
| Corsa troppo corta o troppo lunga | `hands.left.raw_positions.open` / `close` |

### 8.6 Se la vostra mano sinistra è numerata 1-8

Alcuni rinumerano i servo della mano sinistra da 1 a 8. In tal caso va modificato solo `hands.left.servos`:

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

> `angle_offset` e `mirror_pose` **non cambiano** — descrivono la costruzione meccanica, non la numerazione degli ID. Vale comunque anche l'inversione dei servo pari, perché la coppia di ogni dito mantiene "ID dispari per primo".

---

## 9. Rilevamento automatico della porta seriale

### 9.1 Il problema

L'originale aveva un elenco di porte Windows hard-coded da `COM1` a `COM20`:

```python
available_ports = [f'COM{i}' for i in range(1, 21)]
```

Ma un adattatore può capitare su qualsiasi numero di porta (su questa macchina è stato misurato `COM243`). Il risultato: **la vostra porta è semplicemente assente dal menu a tendina**, e la connessione automatica ripiega su un valore predefinito configurato che non esiste, fallendo con "the system cannot find the file specified".

### 9.2 Correzione

Aggiunta `available_serial_ports()`, con ripiego a stadi:

1. `list_ports.comports()` di pyserial (usato quando installato — informazioni più ricche)
2. Windows senza pyserial: lettura della chiave di registro `HARDWARE\DEVICEMAP\SERIALCOMM` (**solo libreria standard**, nessuna nuova dipendenza)
3. Linux/macOS: glob di `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`, `/dev/cu.usb*`
4. Solo se tutto quanto sopra fallisce, ripiego sull'elenco di candidati originale

Le porte sono ordinate in modo **naturale**, quindi `COM2` precede `COM10`.

### 9.3 Modifiche di supporto

- Il menu a tendina è passato da `readonly` a **modificabile** — si può digitare una porta quando il rilevamento la manca
- Se il valore predefinito configurato non è presente, la GUI **parte sulla prima porta che esiste davvero** invece di tentare un valore predefinito assente
- **Un `--port` esplicito non viene mai sovrascritto** da quel ripiego (tracciato tramite `port_was_explicit`)

---

## 10. Riferimento di configurazione

### `data/config.yaml`

I campi di primo livello `servos` / `auto_extremes` / `raw_positions` descrivono la **mano destra** e fungono da valori predefiniti; `hands.<name>` li sovrappone chiave per chiave.

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

`auto_extremes` è **condiviso** da entrambe le mani — lo slider laterale si comporta allo stesso modo nello spazio delle pose; una mano speculare semplicemente si divarica dall'altro lato sul piano fisico.

### `data/hand_config.yaml`

Gli 8 valori di una posa sono ordinati **Ring, Middle, Pointer, Thumb** (coppie di servo `(5,6) (3,4) (1,2) (7,8)`), **non** per ID servo.

**Questo file è condiviso da entrambe le mani ed è sempre memorizzato in ordine mano destra.** La mano sinistra scambia la coppia di ogni dito al momento dell'applicazione, e la riscambia al salvataggio.

> ⚠️ La docstring in cima a `amazing_hand_cmd.py` afferma "index 0→servo1 … 7→servo8". Quel commento è **errato**; l'ordinamento sopra è ciò che il codice fa realmente.

---

## 11. Risultati misurati

### Precisione di raggiungimento (dopo le correzioni)

| Posa | Bersaglio | Effettivo | Errore massimo |
|---|---|---|---|
| `open` | tutti −35 | −36.6 … −33.4 | ≤1.6° |
| `close` | tutti 75 | 74.7 … 75.3 | ≤0.3° |
| `ok` | — | — | 0.5° |
| `victory` | — | — | 1.0° |
| `greeting` | — | — | 2.2° |

### Controlli di conversione

```
raw -> degrees -> raw: 2048 combinations, zero error
open    raw [260, 760] -> back [260, 760]
middle  raw [451, 571] -> back [451, 571]
close   raw [760, 260] -> back [760, 260]
```

### Problemi noti ancora aperti

- **`ok` e `victory` in `demo` non hanno quasi margine di temporizzazione** (+0,01 s in base alla velocità misurata). Al momento passano solo perché la tolleranza < 5° li intercetta. Un calo della tensione della batteria, una variazione di temperatura o una mano leggermente più rigida potrebbero farli sforare. Portare entrambi i ritardi da 1,0 s a 1,2 s è il prossimo passo ovvio.
- **`scissors` è identico byte per byte a `two`**, e **`stone` è identico byte per byte a `close`**. Semanticamente va bene (scissors = due dita, stone = pugno) ma è letteralmente duplicato, e non è stato ripulito.
- **Gli slider conservano ancora un errore di rappresentazione di ~0,3°** rispetto agli obiettivi raw (vedi 2.4).
- **`config.yaml` e il `default_config` di `hand_logic.py` sono disallineati.** Quest'ultimo porta ancora la scala originale (`servo_min: -40` ecc.); viene usato solo quando `config.yaml` manca. Il test `test_hand_logic.py::TestAngleLimits::test_defaults` verifica esattamente quei vecchi valori predefiniti.

---

## 12. Riepilogo file per file

| File | Modifiche |
|---|---|
| `hand_logic.py` | Nuove costanti di conversione SCS0009; `raw_to_degrees` / `raw_to_radians` / `degrees_to_raw` / `pose_to_servo_order` / `servo_to_pose_order`; formato di visualizzazione `raw_position`; valori predefiniti `raw_positions`; **supporto delle mani** (`HAND_NAMES` / `DEFAULT_HAND_SERVOS` / `resolve_hand_config` / `servo_pairs` / `servo_ids` / `hand_angle_offset` / `hand_mirrors_pose` / `adapt_pose_for_hand`); **`available_serial_ports()`**; I/O del file di configurazione passato a **UTF-8** (prima usava il default GBK di Windows e andava in crash sui commenti non ASCII) |
| `amazing_hand_gui.py` | Nuovi `_apply_raw_hand_position` / `middle_all` / `_send_exact_positions`; riscritti `open_all` / `close_all` / `_apply_pose_from_config` / `_log_pose_completion`; nuovo pulsante **Middle position**; nuova riga della posizione raw nel Feedback dei servo; `self.app_config` promosso ad attributo di istanza; rimossi il non utilizzato `latest_goal_positions` e unificato l'ordine di scrittura di `feedback_data['goal']`; **selezione della mano all'avvio + `--hand`**; **8 `range(1,9)` hard-coded sostituiti con gli ID reali della mano**; il titolo della finestra mostra la mano attiva; offset di angolo e conversione speculare integrati in ogni percorso delle pose; **il menu a tendina delle porte ora elenca le porte rilevate e accetta input digitato** |
| `amazing_hand_cmd.py` | Nuovo `--hand`; `connect` / `apply_pose` / `wait_for_motion` / torque-off-on-exit ora usano gli ID reali della mano; i percorsi di posa e sequenza applicano l'offset di angolo e la conversione speculare; lettura della configurazione passata a UTF-8 |
| `data/config.yaml` | Ricalibrati `limits` / `auto_extremes`; aggiunto `raw_positions`; aggiunti `hand` e un blocco di override `hands.left` |
| `data/hand_config.yaml` | Tutte e 19 le pose riscalate; corrette le quattro pose `*_close`; corretto il pollice di `greeting` / `paper`; oscillazione di `wave_r` / `wave_l` ridotta a ±30; `demo` ha ricevuto un ritardo `greeting` più lungo e un nuovo passo di chiusura |
| `pyproject.toml` | Corretto `build-backend` (`setuptools.backends.legacy:build` → `setuptools.build_meta`) |

### Glossario

| Termine | Significato |
|---|---|
| **Auto mode** | Due slider — "base" (apri/chiudi) e "side" (laterale) — pilotano indirettamente i due servo di un dito |
| **Raw mode** | Entrambi gli angoli dei servo di un dito sono controllati direttamente |
| **base** | Quantità di apertura/chiusura, `(pos1 + pos2) / 2` |
| **side** | Scostamento laterale, `base − pos1` |
| **raw** | Unità di posizione interna del servo: 0–1023 su 300°, centro 511 |
| **MiddlePos** | Calibrazione centrale per servo del firmware del produttore; differisce tra le mani (vedi 8.1) |
| **angle_offset** | L'offset di montaggio di 35.16° tra le mani (vedi 8.2) |
| **mirror_pose** | Lo scambio della coppia di servo per dito della mano sinistra (vedi 8.2) |
