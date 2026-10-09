[English](../en/REQUIREMENTS.md) | [Deutsch](../de/REQUIREMENTS.md) | [Español](../es/REQUIREMENTS.md) | [Français](../fr/REQUIREMENTS.md) | Italiano | [日本語](../ja/REQUIREMENTS.md) | [한국어](../ko/REQUIREMENTS.md) | [Português (BR)](../pt-br/REQUIREMENTS.md) | [Português (PT)](../pt-pt/REQUIREMENTS.md) | [简体中文](../zh-hans/REQUIREMENTS.md) | [繁體中文](../zh-hant/REQUIREMENTS.md)

# AmazingHandGUI — Requisiti e criteri di accettazione

Questo documento raccoglie i requisiti funzionali e i criteri di accettazione
derivati dall'implementazione attuale. Ogni requisito fa riferimento al file
(o ai file) sorgente in cui il comportamento è implementato.

---

## 1. Gestione della connessione

### FR-CONN-1: Selezione della porta seriale
La GUI fornisce una casella combinata che elenca le porte seriali rilevate automaticamente.

| AC | Criterio |
|----|-----------|
| 1.1 | Su Linux compaiono i dispositivi `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`; se non ne esiste nessuno, `/dev/ttyACM0` e `/dev/ttyUSB0` sono elencati come ripieghi. |
| 1.2 | Su Windows sono elencati `COM1`–`COM20`. |
| 1.3 | Il valore predefinito corrisponde al valore specifico della piattaforma presente in `config.yaml` (`/dev/ttyACM0` o `COM9`). |

### FR-CONN-2: Selezione del baud rate
Una casella combinata offre opzioni di baud rate configurabili.

| AC | Criterio |
|----|-----------|
| 2.1 | Le opzioni provengono da `config.yaml` → `serial.baudrate_options` (predefinito `[9600, 115200, 1000000]`). |
| 2.2 | La selezione predefinita è `1000000`. |
| 2.3 | Il menu a tendina è disabilitato mentre la connessione è attiva. |

### FR-CONN-3: Connetti / Disconnetti
I pulsanti Connetti e Disconnetti gestiscono la connessione seriale e la coppia dei servo.

| AC | Criterio |
|----|-----------|
| 3.1 | Connetti apre la porta seriale, attiva la coppia sui servo 1–8, disabilita i controlli Connetti/porta/baud e abilita Disconnetti. |
| 3.2 | Disconnetti disattiva la coppia su tutti gli 8 servo, riabilita Connetti/porta/baud e disabilita Disconnetti. |
| 3.3 | Un errore di connessione mostra un messaggio di errore nella barra di stato e nel log; la GUI resta disconnessa. |

### FR-CONN-4: Connessione automatica all'avvio
La GUI tenta di connettersi automaticamente 100 ms dopo l'avvio.

| AC | Criterio |
|----|-----------|
| 4.1 | `connect_controller()` viene chiamata tramite `root.after(100, …)` durante l'inizializzazione. |

### FR-CONN-5: Connessione via CLI
La CLI si connette tramite gli argomenti `--port` e `--baudrate`.

| AC | Criterio |
|----|-----------|
| 5.1 | `--port` e `--baudrate` sovrascrivono i valori predefiniti. |
| 5.2 | Alla connessione la coppia viene attivata su tutti gli 8 servo. |
| 5.3 | All'uscita la coppia viene disattivata (anche con Ctrl+C, tramite il blocco `finally`). |
| 5.4 | `--list` **non** apre una connessione hardware. |

---

## 2. Controllo delle dita

### FR-FING-1: Quattro widget per le dita
Sono mostrati quattro controlli per le dita: Anulare, Medio, Indice, Pollice — ciascuno con 2 servo.

| AC | Criterio |
|----|-----------|
| 1.1 | Vengono renderizzati esattamente 4 widget `FingerControl`, con nomi corrispondenti alle coppie di servo di `config.yaml`: Anulare (5,6), Medio (3,4), Indice (1,2), Pollice (7,8). |

### FR-FING-2: Modalità Auto (base + side)
La modalità Auto fornisce uno slider verticale di chiusura/apertura e uno slider orizzontale da lato a lato.

| AC | Criterio |
|----|-----------|
| 2.1 | Slider verticale: da 0° (aperto) a 110° (chiuso); in alto = chiuso, in basso = aperto. |
| 2.2 | Slider orizzontale: da −40° a +40°. |
| 2.3 | Spostando uno dei due slider si inviano posizioni interpolate (tramite `compute_auto_positions`) a entrambi i servo. |

### FR-FING-3: Modalità Raw
La modalità Raw mostra due slider verticali indipendenti (uno per servo).

| AC | Criterio |
|----|-----------|
| 3.1 | Selezionando Raw si nascondono gli slider Auto e si mostrano due slider verticali per servo (−40 a 110). |
| 3.2 | La casella Mimic è disabilitata e deselezionata; il pulsante Centra è disabilitato. |
| 3.3 | Il cambio di modalità sincronizza i valori in modo bidirezionale (auto ↔ raw tramite `decompose_servo_positions`). |

### FR-FING-4: Controllo della velocità
Ogni dito dispone di una casella combinata di velocità (1–6).

| AC | Criterio |
|----|-----------|
| 4.1 | L'intervallo va da `speeds.min` (1) a `speeds.max` (6), predefinito `speeds.default` (3). |
| 4.2 | La velocità viene inviata tramite `write_goal_speed()` per ciascun servo prima dei comandi di posizione. |

### FR-FING-5: Modalità Mimic
Le variazioni di chiusura/apertura su un dito che imita vengono propagate a tutte le altre dita con Mimic abilitato.

| AC | Criterio |
|----|-----------|
| 5.1 | Abilitando Mimic su A e B, le variazioni dello slider di chiusura/apertura di A si riflettono su B e viceversa. |
| 5.2 | Mimic si applica solo in modalità Auto; passando a Raw viene disabilitato. |

### FR-FING-6: Pulsante Centra
Reimposta a 0° lo scostamento laterale.

| AC | Criterio |
|----|-----------|
| 6.1 | Facendo clic su Centra si imposta `side_var` a 0 e si attiva un aggiornamento di posizione. |
| 6.2 | Centra è disabilitato in modalità Raw. |

### FR-FING-7: Rotella del mouse sullo slider di posizione
La rotella di scorrimento regola la posizione di ±5°.

| AC | Criterio |
|----|-----------|
| 7.1 | Scorrimento verso l'alto → +5° (chiusura), verso il basso → −5° (apertura), limitato ai valori ammessi. |

### FR-FING-8: Indicatore LED di attività
Ogni dito mostra un LED di stato.

| AC | Criterio |
|----|-----------|
| 8.1 | In movimento (flag di movimento = true) → verde lampeggiante a intervalli di ~350 ms. |
| 8.2 | Bloccato (errore obiettivo-vs-posizione ≥ 8° e non in movimento) → rosso fisso. |
| 8.3 | Inattivo → grigio. |

---

## 3. Controllo da tastiera

### FR-KEY-1: Selezione del dito
I tasti 1–4 selezionano il dito attivo.

| AC | Criterio |
|----|-----------|
| 1.1 | 1 = Anulare, 2 = Medio, 3 = Indice, 4 = Pollice. |
| 1.2 | La barra di stato mostra il nome del dito selezionato. |

### FR-KEY-2: Movimento con i tasti freccia
I tasti freccia muovono il dito selezionato.

| AC | Criterio |
|----|-----------|
| 2.1 | Su = chiusura (aumenta la posizione), Giù = apertura (diminuisce). |
| 2.2 | Destra = aumenta lo scostamento laterale, Sinistra = lo diminuisce. |

### FR-KEY-3: Modificatori di precisione
La dimensione del passo varia in base al tasto modificatore.

| AC | Criterio |
|----|-----------|
| 3.1 | Nessun modificatore: 1° (preciso). |
| 3.2 | Shift: 5° (normale). |
| 3.3 | Ctrl: 10° (veloce). |
| 3.4 | La barra di stato mostra il nome della modalità e l'angolo risultante. |

### FR-KEY-4: Azioni rapide
Scorciatoie a tasto singolo per azioni comuni.

| AC | Criterio |
|----|-----------|
| 4.1 | Q = chiude completamente a 110°. |
| 4.2 | E = apre completamente a 0°. |
| 4.3 | C = centra il lato a 0°. |

---

## 4. Controlli globali

### FR-GLOB-1: Apri tutto
Imposta tutte le dita completamente aperte.

| AC | Criterio |
|----|-----------|
| 1.1 | Tutti i `pos_var` → 0, tutti i `side_var` → 0, posizioni inviate all'hardware. |

### FR-GLOB-2: Chiudi tutto
Imposta tutte le dita completamente chiuse.

| AC | Criterio |
|----|-----------|
| 2.1 | Tutti i `pos_var` → 110, tutti i `side_var` → 0, posizioni inviate. |

### FR-GLOB-3: Centra tutto
Reimposta tutti gli scostamenti laterali.

| AC | Criterio |
|----|-----------|
| 3.1 | Tutti i `side_var` → 0, posizioni inviate. |

### FR-GLOB-4: Velocità globale
Un menu a tendina imposta in una sola volta le velocità di tutte le dita.

| AC | Criterio |
|----|-----------|
| 4.1 | Selezionando un valore si aggiorna ogni casella combinata di velocità per dito. |
| 4.2 | La velocità è limitata a [1, 6]. |

---

## 5. Gestione delle pose

### FR-POSE-1: Salva posa
L'utente inserisce un nome e salva le posizioni correnti degli 8 servo.

| AC | Criterio |
|----|-----------|
| 1.1 | Le posizioni di tutte e 4 le dita (8 valori) vengono acquisite tramite `get_positions()`. |
| 1.2 | Il nome viene convalidato tramite `validate_name()` prima del salvataggio. |
| 1.3 | In caso di successo: il menu a tendina si aggiorna (ordinato), il campo si svuota, la barra di stato conferma. |
| 1.4 | Un nome non valido o vuoto mostra una finestra di messaggio di errore. |

### FR-POSE-2: Applica posa
Selezionando una posa e facendo clic su Apply la mano si sposta su quella posa.

| AC | Criterio |
|----|-----------|
| 2.1 | Le 8 posizioni vengono applicate a tutti i widget delle dita. |
| 2.2 | Le posizioni dei servo vengono inviate all'hardware. |
| 2.3 | Il ritardo è stimato dalla distanza di movimento e dalla velocità; il completamento della posa viene registrato nel log dopo tale ritardo con confronto tra obiettivo ed effettivo. |

### FR-POSE-3: Elimina posa
Rimuove la posa selezionata dopo conferma.

| AC | Criterio |
|----|-----------|
| 3.1 | Una finestra di messaggio sì/no chiede conferma. |
| 3.2 | Dopo la conferma: la posa viene rimossa dalla configurazione, lo YAML viene salvato, il menu a tendina si aggiorna. |
| 3.3 | Se non restano pose, il menu a tendina mostra `<no poses>`. |

### FR-POSE-4: Convalida dei nomi
I nomi vengono convalidati per prevenire la corruzione dello YAML.

| AC | Criterio |
|----|-----------|
| 4.1 | Vuoto / solo spazi → rifiutato. |
| 4.2 | Più di 50 caratteri → rifiutato. |
| 4.3 | Contiene `: { } [ ] , & * # ? \| - < > = ! % @ \` " '` → rifiutato. |
| 4.4 | Contiene caratteri di controllo (ASCII < 32) → rifiutato. |
| 4.5 | Spazi iniziali/finali → rifiutato. |

---

## 6. Gestione delle sequenze

### FR-SEQ-1: Riproduttore di sequenze (finestra principale)
Selezione da menu a tendina, casella Loop, pulsanti Play / Pausa / Stop.

| AC | Criterio |
|----|-----------|
| 1.1 | Il menu a tendina elenca tutte le sequenze salvate (o `<no sequences>`). |
| 1.2 | La casella Loop abilita la ripetizione continua. |
| 1.3 | Play avvia la sequenza in un thread in background. |
| 1.4 | Pausa alterna pausa/ripresa; il testo del pulsante passa tra "⏸ Pause" e "▶ Riprendi". |
| 1.5 | Stop imposta `stop_sequence = True`; il thread della sequenza termina. |

### FR-SEQ-2: Motore di esecuzione delle sequenze
Le sequenze vengono eseguite in un thread in background con attese interrompibili.

| AC | Criterio |
|----|-----------|
| 2.1 | I passi di posa analizzano il formato `"pose_name:s1,s2,...,s8\|delay"`. |
| 2.2 | I passi `SLEEP:duration` mettono in pausa senza comandi hardware. |
| 2.3 | Se non c'è un ritardo esplicito: attesa automatica = `15.0 − (avg_speed − 1) × 2.4` secondi. |
| 2.4 | Le attese vengono eseguite a incrementi di 0,1 s, controllando a ogni tick i flag di stop/pausa. |
| 2.5 | In modalità loop, un intervallo di 0,5 s separa le iterazioni. |
| 2.6 | I nomi di posa sconosciuti vengono saltati con un avviso. |
| 2.7 | I pulsanti Play/Pausa/Stop alternano lo stato abilitato/disabilitato durante l'esecuzione. |

### FR-SEQ-3: Finestra di dialogo del gestore sequenze
Finestra di dialogo a due pannelli, accessibile tramite il pulsante "🔧 Gestisci".

| AC | Criterio |
|----|-----------|
| 3.1 | Pannello sinistro: listbox delle sequenze salvate con i pulsanti Esegui, Modifica ed Elimina. |
| 3.2 | Un doppio clic esegue la sequenza una volta (senza loop) senza chiudere la finestra di dialogo. |
| 3.3 | Modifica carica i passi nel costruttore, precompilando il campo del nome. |

### FR-SEQ-4: Costruttore di sequenze
Pannello destro per costruire sequenze a partire dalle pose.

| AC | Criterio |
|----|-----------|
| 4.1 | Le pose disponibili sono elencate; un doppio clic aggiunge un passo con la velocità/il ritardo correnti. |
| 4.2 | Campi numerici di velocità per dito (1–6); "⬇ Copia dall'interfaccia" importa le velocità della finestra principale. |
| 4.3 | Il campo del ritardo aggiunge il suffisso `\|delay` ai passi di posa. |
| 4.4 | "⏱ Ritardo" inserisce un passo `SLEEP:Xs` autonomo. |
| 4.5 | ↑/↓ riordinano, ➖ rimuove, 🗑 cancella tutto. |
| 4.6 | "💾 Salva sequenza" convalida il nome, salva, aggiorna i menu a tendina. |
| 4.7 | "▶ Esegui" esegue la sequenza costruita senza salvarla né chiudere la finestra di dialogo. |

### FR-SEQ-5: Convalida dell'input del ritardo
I valori float non validi nel campo del ritardo vengono gestiti senza problemi.

| AC | Criterio |
|----|-----------|
| 5.1 | Un ritardo non numerico equivale a nessun ritardo (il passo viene aggiunto senza `\|delay`). |
| 5.2 | Un ritardo SLEEP non numerico mostra "Invalid delay value" nella barra di stato. |

---

## 7. Monitoraggio dei servo

### FR-MON-1: Raccolta della telemetria in background
Un thread daemon interroga tutti gli 8 servo a circa 10 Hz.

| AC | Criterio |
|----|-----------|
| 1.1 | Il thread dorme 0,1 s tra un'iterazione e l'altra. |
| 1.2 | Metriche raccolte per servo: posizione, carico, temperatura, tensione, velocità, flag di movimento, stato, obiettivo. |
| 1.3 | Una lettura fallita ripete l'ultimo valore noto per mantenere gli array sincronizzati. |
| 1.4 | I dati di feedback vengono aggiornati in modo atomico sotto `feedback_lock`. |

### FR-MON-2: Visualizzazione del grafico
Grafico Matplotlib incorporato nel pannello destro.

| AC | Criterio |
|----|-----------|
| 2.1 | Metriche selezionabili: Posizione, Obiettivo vs Corrente, Coppia, Velocità, Temperatura, Tensione, In movimento. |
| 2.2 | Il menu a tendina "Servos" attiva/disattiva quali delle 8 tracce sono visibili (con ✓ Tutti / ✕ Nessuno). |
| 2.3 | I ridisegni del grafico sono limitati a intervalli di ≥100 ms. |
| 2.4 | Nessuna metrica selezionata → messaggio "Select at least one metric". |
| 2.5 | Nessun dato → messaggio "Waiting for data...". |

### FR-MON-3: Modalità del grafico
Due modalità: Multi-Servo e Scope.

| AC | Criterio |
|----|-----------|
| 3.1 | La modalità Scope mostra un selettore "Scope Servo" per concentrarsi su un singolo servo. |
| 3.2 | Multi-Servo nasconde il selettore Scope Servo. |

### FR-MON-4: Zoom e panoramica del grafico
Quattro slider per controllare la vista.

| AC | Criterio |
|----|-----------|
| 4.1 | Y-Zoom: da 0.2× a 5.0×, predefinito 1.1×. |
| 4.2 | Y-Pan: da −3.0 a +3.0, predefinito 0.0. |
| 4.3 | Time-Zoom: dal 10 % al 100 % dei dati disponibili. |
| 4.4 | Time-Pan: dallo 0 % (più vecchio) al 100 % (più recente). |
| 4.5 | Tutti gli slider attivano ridisegni del grafico con debounce. |

### FR-MON-5: Modalità scorrevole
Limita il grafico agli ultimi N punti dati.

| AC | Criterio |
|----|-----------|
| 5.1 | Quando è abilitata e i dati superano `max_data_points` (100), i campioni più vecchi vengono scartati. |
| 5.2 | Disabilitando la modalità scorrevole si conservano tutti i dati raccolti. |

### FR-MON-6: Pausa / Riprendi / Cancella grafico

| AC | Criterio |
|----|-----------|
| 6.1 | Pausa arresta i ridisegni del grafico; la raccolta della telemetria continua. |
| 6.2 | Cancella reimposta tutti gli array di dati e lo zoom/pan ai valori predefiniti. |

### FR-MON-7: Pannello di feedback
Tabella a griglia che mostra la telemetria in tempo reale di tutti i servo.

| AC | Criterio |
|----|-----------|
| 7.1 | Colonne: S1–S8. Righe: Obiettivo, Posizione, Velocità, Coppia, Tensione, Corrente, Temperatura, Stato, In movimento. |
| 7.2 | Valori formattati da `format_feedback_value()`: posizione `X.XX°`, velocità `X.X°/s`, tensione `X.XX V`, temperatura `X.X °C`, corrente `X mA`, carico `X.X %`, stato `0xHH`, movimento `Yes/No`. |
| 7.3 | Vengono aggiornate solo le celle modificate (cache dei differenziali). |
| 7.4 | L'aggiornamento è limitato a ≥50 ms tra una modifica e l'altra. |

---

## 8. Configurazione

### FR-CFG-1: Caricamento della configurazione dell'applicazione
`config.yaml` viene caricato con valori predefiniti per tutte le chiavi mancanti.

| AC | Criterio |
|----|-----------|
| 1.1 | File mancante → viene usata la configurazione predefinita completa. |
| 1.2 | Le chiavi mancanti vengono unite dai valori predefiniti (merge a due livelli). |
| 1.3 | Errore di analisi → vengono restituiti i valori predefiniti, l'errore viene stampato su stdout. |

### FR-CFG-2: Mappatura dei servo
Gli ID dei servo per dito sono definiti in `config.yaml` → `servos`.

| AC | Criterio |
|----|-----------|
| 2.1 | La configurazione definisce pointer=[1,2], middle=[3,4], ring=[5,6], thumb=[7,8]. |
| 2.2 | `all_ids` = [1,2,3,4,5,6,7,8]. |

### FR-CFG-3: Limiti di angolo

| AC | Criterio |
|----|-----------|
| 3.1 | `servo_min` = −40, `servo_max` = 110, `base_min` = 0, `base_max` = 110, `side_min` = −40, `side_max` = 40. |
| 3.2 | Tutti gli intervalli degli slider derivano da questi valori. |

### FR-CFG-4: Estremi di Auto
Punti finali dell'interpolazione bilineare per il calcolo dello scostamento laterale.

| AC | Criterio |
|----|-----------|
| 4.1 | `left_open`, `right_open`, `left_closed`, `right_closed`, `center_open`, `center_closed` sono configurabili. |
| 4.2 | `compute_auto_positions()` li usa per l'interpolazione. |

### FR-CFG-5: Configurazione della velocità

| AC | Criterio |
|----|-----------|
| 5.1 | `speeds.default` = 3, `speeds.min` = 1, `speeds.max` = 6. |

---

## 9. Strumento CLI

### FR-CLI-1: Elenca pose e sequenze
`--list` stampa tutte le pose e le sequenze senza aprire una connessione.

| AC | Criterio |
|----|-----------|
| 1.1 | L'output mostra il numero di pose, ciascun nome con le sue posizioni. |
| 1.2 | L'output mostra il numero di sequenze, ciascun nome con il numero di passi e i dettagli. |
| 1.3 | Non viene aperta alcuna connessione seriale. |

### FR-CLI-2: Applica posa
`--pose NAME` invia una posa salvata all'hardware.

| AC | Criterio |
|----|-----------|
| 2.1 | Le posizioni vengono caricate dalla configurazione; la velocità predefinita 3 è applicata a tutti i servo. |
| 2.2 | Posa sconosciuta → errore + `sys.exit(1)`. |

### FR-CLI-3: Riproduci sequenza
`--sequence NAME` riproduce una sequenza; `--loop` la ripete fino a Ctrl+C.

| AC | Criterio |
|----|-----------|
| 3.1 | Velocità e ritardo vengono analizzati dalla stringa del passo. |
| 3.2 | I passi `SLEEP` mettono in pausa senza comandi hardware. |
| 3.3 | Nessun ritardo esplicito → attesa automatica = `15.0 − (avg_speed − 1) × 2.4` secondi. |
| 3.4 | SIGINT imposta `stop_flag` per un'interruzione pulita. |
| 3.5 | Sequenza sconosciuta → uscita con errore. |
| 3.6 | Sequenza vuota → uscita con errore. |
| 3.7 | Le pose sconosciute all'interno di una sequenza vengono saltate con un WARNING. |

### FR-CLI-4: Analisi dei passi
`parse_step()` gestisce più formati.

| AC | Criterio |
|----|-----------|
| 4.1 | `SLEEP:2.0s` → attesa di 2.0 s. |
| 4.2 | `open:3,3,...\|2.0s` → posa "open" con velocità e ritardo di 2.0 s. |
| 4.3 | `open` (nome semplice) → posa con velocità predefinite, senza ritardo. |
| 4.4 | Le velocità più corte di 8 vengono completate con 3; quelle più lunghe troncate. |
| 4.5 | Il suffisso di durata `s` / `S` viene rimosso. |

### FR-CLI-5: Azioni mutuamente esclusive
`--list`, `--pose` e `--sequence` sono mutuamente esclusivi.

| AC | Criterio |
|----|-----------|
| 5.1 | Passando più azioni → uscita con codice diverso da zero. |
| 5.2 | `--loop` senza `--sequence` → errore. |

### FR-CLI-6: Sostituzione del file di configurazione
`--config PATH` usa un file YAML alternativo.

| AC | Criterio |
|----|-----------|
| 6.1 | File mancante → errore + `sys.exit(1)`. |

---

## 10. Persistenza dei dati

### FR-DATA-1: File di configurazione YAML
Le pose e le sequenze sono memorizzate in `data/hand_config.yaml`.

| AC | Criterio |
|----|-----------|
| 1.1 | Il file usa il formato YAML con le chiavi di primo livello `poses` e `sequences`. |

### FR-DATA-2: Carica configurazione

| AC | Criterio |
|----|-----------|
| 2.1 | File mancante → `{'poses': {}, 'sequences': {}}`. |
| 2.2 | File vuoto → chiavi popolate automaticamente. |
| 2.3 | YAML malformato → struttura vuota, errore stampato su stdout. |

### FR-DATA-3: Salva configurazione con array inline
Le posizioni vengono salvate in stile flow tramite post-elaborazione con espressioni regolari.

| AC | Criterio |
|----|-----------|
| 3.1 | Il file contiene lo stile `positions: [v1, v2, …, v8]`. |
| 3.2 | I valori negativi vengono conservati nel formato inline. |
| 3.3 | Restituisce `True` in caso di successo, `False` in caso di errore. |

### FR-DATA-4: Creazione automatica della directory dei dati

| AC | Criterio |
|----|-----------|
| 4.1 | La directory `data/` viene creata se non esiste prima della scrittura. |

### FR-DATA-5: Integrità del round-trip
I dati scritti dalla GUI possono essere letti dalla CLI e viceversa.

| AC | Criterio |
|----|-----------|
| 5.1 | Pose, posizioni negative e passi di sequenza sopravvivono a un round-trip salvataggio-GUI → lettura-CLI. |

---

## 11. Gestione degli errori

### FR-ERR-1: Errore di connessione
Le connessioni fallite non fanno crashare l'applicazione.

| AC | Criterio |
|----|-----------|
| 1.1 | La barra di stato mostra "Connection failed: …"; `connected` resta `False`. |

### FR-ERR-2: Baud rate non valido

| AC | Criterio |
|----|-----------|
| 2.1 | Baud rate non numerico → la barra di stato mostra "Invalid baudrate". |

### FR-ERR-3: Recupero del thread di monitoraggio

| AC | Criterio |
|----|-----------|
| 3.1 | Un singolo errore di lettura di un servo non fa crashare il thread. |
| 3.2 | Gli errori vengono stampati su stdout. |

### FR-ERR-4: Degrado del flag di movimento

| AC | Criterio |
|----|-----------|
| 4.1 | Dopo 3 errori consecutivi di `read_moving`, la supervisione viene disabilitata con un messaggio nel log. |
| 4.2 | Passa da `sync_read_moving` a letture per servo al primo errore di sincronizzazione. |

### FR-ERR-5: Avvisi di completamento della posa

| AC | Criterio |
|----|-----------|
| 5.1 | Un errore obiettivo vs effettivo > 5° attiva un avviso ⚠ nel log. |
| 5.2 | Un timeout di movimento (6.0 s) attiva un avviso di timeout se i servo non smettono mai di muoversi. |

### FR-ERR-6: Configurazione mancante (CLI)

| AC | Criterio |
|----|-----------|
| 6.1 | File di configurazione mancante → messaggio di errore + `sys.exit(1)`. |

### FR-ERR-7: Sequenza vuota / non valida

| AC | Criterio |
|----|-----------|
| 7.1 | Passi di sequenza vuoti → `sys.exit(1)`. |
| 7.2 | Pose sconosciute nella sequenza → saltate con WARNING. |

---

## 12. Layout dell'interfaccia

### FR-UI-1: Struttura della finestra

| AC | Criterio |
|----|-----------|
| 1.1 | Il titolo include la versione: "AmazingHand Controller v0.8". |
| 1.2 | Geometria iniziale: 1920×1200. |
| 1.3 | Un `PanedWindow` orizzontale separa i pannelli sinistro (controlli) e destro (grafico). |

### FR-UI-2: Pannello sinistro

| AC | Criterio |
|----|-----------|
| 2.1 | Riga 1: Anulare, Medio, Indice (3 dita in orizzontale). |
| 2.2 | Riga 2: Pollice (a destra) + controlli impilati (Connessione, Globale, Posa, Sequenza). |
| 2.3 | Il log di esecuzione sotto i controlli, in un separatore verticale ridimensionabile. |

### FR-UI-3: Barra di stato

| AC | Criterio |
|----|-----------|
| 3.1 | Si aggiorna alla connessione, alla disconnessione, alla selezione di un dito, al cambio di velocità, durante le operazioni di posa e in caso di errori. |

### FR-UI-4: Log di esecuzione

| AC | Criterio |
|----|-----------|
| 4.1 | I messaggi sono prefissati da un timestamp `[HH:MM:SS.mmm]`. |
| 4.2 | Scorrimento automatico fino all'ultima voce. |
| 4.3 | I messaggi vengono anche stampati su stdout. |

### FR-UI-5: Tooltip

| AC | Criterio |
|----|-----------|
| 5.1 | Un popup giallo compare dopo 500 ms di passaggio del mouse, posizionato in basso a destra del widget. |
| 5.2 | Scompare all'uscita del mouse o alla pressione di un pulsante. |

### FR-UI-6: Pannello destro (area del grafico)

| AC | Criterio |
|----|-----------|
| 6.1 | `PanedWindow` verticale: grafico in alto (min 200 px), feedback in basso (min 150 px). |
| 6.2 | Slider del tempo sotto il grafico; slider Y a destra. |

### FR-UI-7: Guida della CLI

| AC | Criterio |
|----|-----------|
| 7.1 | `--help` termina con 0 e mostra tutte le opzioni. |

### FR-UI-8: Argomenti della riga di comando della GUI

| AC | Criterio |
|----|-----------|
| 8.1 | `--port` sostituisce la porta seriale predefinita. |
| 8.2 | `--baudrate` sostituisce il baud rate predefinito (1000000). |

---

## Riepilogo della copertura dei test

| File di test | Ambito | Numero |
|-----------|-------|-------|
| `tests/test_hand_logic.py` | `load_app_config` (6), `servo_mapping` (3), `angle_limits` (1), `auto_extremes` (2), `speed_config` (1), `default_serial_port` (2), `ensure_data_dir` (2), `load_pose_definitions` (3), `compute_auto_positions` (6), `decompose_servo_positions` (5), `coerce_numeric` (11), `coerce_angle_degrees` (6), `coerce_bool` (6), `load_to_percent` (7), `estimate_current_from_load` (5), `format_feedback_value` (12), `get_time_window_indices` (8), `angle_rad` (3) | 89 |
| `tests/test_gui_utils.py` | `validate_name` (21), `clamp` (8), `load_config` (6), `save_config` (6) | 41 + 10 parametrizzati |
| `tests/test_cmd.py` | `angle_rad` (8), `parse_step` (11), `cmd_list` (4), `load_config` (2), `apply_pose` (6), `_interruptible_sleep` (2), `auto_wait` (3), `mutual_exclusion` (1), `config_override` (2) | 41 |
| `tests/test_integration.py` | `cmd_pose` end-to-end (5), `cmd_sequence` end-to-end (6), round-trip della configurazione (3) | 14 |
| `tests/test_system.py` | Sottoprocesso della CLI: `--help` (5), `--list` (9), opzioni di `--help` (3), percorsi di errore (5) | 22 |
| `tests/test_system_hardware.py` | Hardware reale: connessione (2), connessione via CLI (2), applicazione di una posa (3), velocità (2), telemetria (6), sequenza (2), recupero dagli errori (1), movimento (2), disconnessione (1) — **richiede il flag `--hardware`** | 21 |
| **Totale (senza hardware)** | **217 test** |
| **Totale (con hardware)** | **238 test** |
