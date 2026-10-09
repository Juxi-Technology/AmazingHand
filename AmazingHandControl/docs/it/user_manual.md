[English](../en/user_manual.md) | [Deutsch](../de/user_manual.md) | [Español](../es/user_manual.md) | [Français](../fr/user_manual.md) | Italiano | [日本語](../ja/user_manual.md) | [한국어](../ko/user_manual.md) | [Português (BR)](../pt-br/user_manual.md) | [Português (PT)](../pt-pt/user_manual.md) | [简体中文](../zh-hans/user_manual.md) | [繁體中文](../zh-hant/user_manual.md)

# AmazingHand Controller – Manuale utente

> **Versione:** 2026-03-22  
> **Si applica a:** `amazing_hand_gui.py` (GUI), `amazing_hand_cmd.py` (CLI)

---

## 1. Introduzione

Il controller GUI AmazingHand offre monitoraggio in tempo reale e controllo manuale di una mano robotica a otto servo azionata da attuatori Feetech SCS0009. L'interfaccia è suddivisa in pannelli per il controllo delle dita, la gestione globale, la visualizzazione della telemetria e la registrazione delle attività. Questa guida vi accompagna nell'installazione, nella navigazione e nei flussi di lavoro più comuni.

> **Suggerimento:** tenete aperto questo manuale mentre usate la GUI. I tooltip integrati nell'applicazione ripetono le stesse descrizioni quando passate il puntatore sui controlli.

![AmazingHand hardware with controller connected](../en/screenshots/hand_overview.png)

---

## 2. Lista di controllo per l'avvio rapido

1. **Installare le dipendenze** (una volta per ambiente):
   ```bash
   python -m pip install -r requirements.txt
   ```
2. **Alimentare l'hardware:** collegare l'alimentazione a 5 V alla catena dei servo e inserire l'adattatore seriale USB.
3. **Avviare la GUI:**
   ```bash
   python amazing_hand_gui.py
   ```
4. **Connettersi al controller:** scegliere la **Porta** seriale (ad es. `COM9`) e fare clic su **▶ Connect**.
5. **Verificare la telemetria:** cercare gli aggiornamenti in tempo reale nel grafico e nella tabella di feedback.

---

## 3. Panoramica della schermata

```
+--------------------------------------------------------------------------------+
|                              AmazingHand Controller                            |
+---------------------------+-----------------------------------------------+----+
| Finger Controls           | Chart Controls & Telemetry Plot                    |
| (Ring – Middle – Pointer) | (Display menu, chart canvas)                       |
+---------------------------+-----------------------------------------------+----+
| Control Stack             | Thumb finger   | Feedback Table (Servo Metrics)    |
| (Connection, Global, Pose,| control        | (Goal, Position, Load, etc.)      |
|  Sequence)                |                |                                   |
+---------------------------+                                                    |
| Execution Log & Status    |                                                    |
+--------------------------------------------------------------------------------+
```

![Main window overview highlighting the major panels](../en/screenshots/mainscreen.png)

### 3.1 I pannelli in breve

| Pannello | Posizione | Scopo |
|-------|----------|---------|
| **Comandi delle dita** | A sinistra, in alto (3 dita) + in basso a destra (Pollice) | Slider individuali e selettori di velocità per ogni coppia di dita. Include indicatori mimic e LED di stato per dito. |
| **Blocco di controllo destro** | A sinistra, in basso a destra | Impostazioni di connessione, controlli globali, gestione delle pose e riproduttore di sequenze. |
| **Pannello di telemetria** | A destra | Grafici in tempo reale con slider di zoom/panoramica e una tabella di feedback configurabile. |
| **Log di esecuzione** | In basso | Flusso di messaggi di stato, avvisi e avanzamento delle sequenze. |

---

## 4. Guida dettagliata dei pannelli

### 4.1 Pannello di controllo delle dita (colonna sinistra)

Ogni widget del dito controlla una coppia di servo (posizione + scostamento laterale):

- **Interruttore di modalità:** passa tra **Auto** (slider base + scostamento) e **Raw** (obiettivi di servo diretti).
- **LED di stato:** grigio (inattivo), verde (in movimento), rosso (blocco potenziale, in base al carico rispetto all'obiettivo).
- **Slider di posizione:** 0–110° (da aperto a chiuso). La rotella del mouse regola di 1°; il trascinamento è rapido.
- **Slider laterale:** ±40° per le regolazioni laterali. Lo slider laterale del Pollice è **invertito** in modo che la direzione fisica corrisponda all'orientamento anatomico della mano — trascinando verso destra il pollice si muove in direzione positiva rispetto al suo montaggio hardware.
- **Selettore di velocità:** menu a tendina 1–6 che controlla la velocità di movimento di entrambi i servo della coppia del dito.
- **Casella Mimic:** riproduce i movimenti di chiusura/apertura di un dito sorgente per un movimento coordinato in modalità Auto.

**Modalità delle dita: Auto vs Raw**

- **La modalità Auto** (predefinita) mostra lo slider di chiusura/apertura, lo slider di scostamento laterale, il menu a tendina della velocità e il pulsante di centratura. La GUI combina quei due valori degli slider in comandi per i servo usando gli estremi calibrati memorizzati in `data/hand_config.yaml`, così la coppia segue pose naturali delle dita senza calcoli manuali sui servo. Il Mimic resta attivo qui — abilitatelo su più dita per pilotarle in sincrono con qualunque dito stiate regolando.
- **La modalità Raw** sostituisce i controlli Auto con due slider verticali etichettati per servo. Spostateli per comandare direttamente gli angoli dei servo sottostanti quando si testano i finecorsa, si convalida la calibrazione o si diagnosticano problemi di leveraggio. Il pulsante di centratura e la casella mimic sono disabilitati perché Raw aggira la logica di miscelazione automatica; le scorciatoie da tastiera funzionano comunque, con Su/Giù che pilotano il servo 1 e Sinistra/Destra il servo 2. Raw usa l'ultimo valore di velocità selezionato, quindi impostate le velocità prima di cambiare modalità se vi serve una velocità di movimento specifica.

**Come la modalità Auto calcola gli obiettivi dei servo**

- Il valore dello slider di chiusura/apertura viene limitato a `limits.base_min/base_max`, poi normalizzato (`t = base / base_max`) per interpolare tra le pose aperto e chiuso di `auto_extremes` per ciascun lato del dito.
- Lo slider di scostamento laterale viene limitato a `limits.side_min/side_max` e convertito in un fattore di miscelazione (`u`). Gli scostamenti negativi interpolano dalla posa centrale verso `left_open`/`left_closed`; quelli positivi interpolano verso gli estremi del lato destro.
- Senza scostamento laterale, entrambi i servo ricevono semplicemente il valore dello slider di base. Gli obiettivi finali dei servo vengono limitati a `limits.servo_min/servo_max` prima di essere inviati, mantenendo i movimenti entro limiti di sicurezza calibrati.

Le scorciatoie da tastiera integrano gli slider (documentate al §5.2).

![Finger control panel with per-finger sliders and status indicators](../en/screenshots/finger_control_frame.png)

### 4.2 Blocco dei controlli globali (a destra del pannello delle dita)

1. **Connessione:** selezione di porta e baud rate (entrambi i menu a tendina sono disabilitati quando connessi), pulsanti connetti/disconnetti. La barra di stato in basso segnala successi o errori.
2. **Controlli globali:**
   - **Open All / Close All / Center All** – si applicano istantaneamente a ogni dito.
   - **Menu a tendina Global Speed** – imposta i selettori di velocità di ogni dito su un valore comune (1–6).
3. **Gestione delle pose:** consente di salvare, caricare, applicare ed eliminare le pose memorizzate in `data/hand_config.yaml`.
   - Layout: `Pose: [dropdown]  ✓ Apply  🗑 Delete  Name: [entry]  ➕ Add New`
   - **🗑 Delete** rimuove definitivamente la posa selezionata (viene mostrata una finestra di conferma).
4. **Riproduttore di sequenze:** consente di selezionare ed eseguire animazioni multi-passo, con loop opzionale. Si accede alla finestra del gestore sequenze tramite **🔧 Manage**.

![Connection, global controls, pose management, and sequence player stack](../en/screenshots/control_frame.png)

### 4.3 Pannello di telemetria e feedback (colonna destra)

- **Riga dei controlli:**
  - Mette in pausa/riprende gli aggiornamenti del grafico.
  - Interruttore della finestra scorrevole.
  - Selezione delle metriche (posizione, carico, velocità, temperatura, tensione, flag di movimento).
  - Commutatore di modalità (Multi-Servo vs Scope) con selettore del servo per quest'ultima.
  - Menu a tendina di visibilità dei servo con gli ausili "All/None/Clear".
  
![Display mode, metric selection, and scope controls](../en/screenshots/chart_mode_controls.png)

![Display menu for choosing telemetry metrics](../en/screenshots/chart_select_display_values.png)

![Servo visibility menu with quick actions](../en/screenshots/chart_servos_selection.png)

#### Modalità del grafico

- **Multi-Servo** (predefinita) mantiene sul grafico ogni traccia dei servo abilitati. Usare il menu a tendina **Servos** per attivare/disattivare rapidamente i gruppi e confrontare movimento o carico tra le dita.
- **Scope** attiva il selettore **Scope Servo**, permettendo di concentrarsi su un singolo canale pur continuando a usare le stesse caselle delle metriche. Combinare questa modalità con il menu di visibilità dei servo (ad es. nascondere tutto, poi riabilitare il servo in scope) per ottenere una vista in stile oscilloscopio senza altre tracce.
- Indipendentemente dalla modalità, la tabella di telemetria continua a mostrare tutti i servo, così da poter correlare il grafico in focus con l'istantanea più ampia dei dati.
- **Area del grafico:** grafico Matplotlib che mostra la telemetria selezionata. Zoom tramite slider:
  - **Y Zoom / Pan:** ridimensionamento e spostamento verticale.
  - **Time Zoom / Pan:** focus sulla cronologia recente o sui campioni più vecchi.
- **Tabella di feedback:** griglia scorrevole che riepiloga i valori Goal, Position, Speed, Load, Voltage, Temperature, Status e Moving per ciascun servo.

![Chart controls with zoom/pan sliders and telemetry traces](../en/screenshots/chart_frame.png)

![Feedback table showing live servo metrics](../en/screenshots/feedback_frame.png)

### 4.4 Log di esecuzione e barra di stato

Collocato sotto il pannello delle dita, il log registra le operazioni in ordine cronologico. La barra di stato mostra l'ultima azione o l'ultimo avviso.

![Execution log and current status bar](../en/screenshots/log_and_last_action_frame.png)

---

## 5. Utilizzo della mano

### 5.1 Connessione all'hardware

1. Alimentare i servo e collegare l'adattatore USB.
2. Avviare la GUI e confermare che si selezioni automaticamente la **Porta** corretta (`COM*` su Windows o `/dev/tty*` su Linux/macOS).
3. Fare clic su **▶ Connect**. In caso di successo cambiano gli stati dei pulsanti e si aggiorna la barra di stato.
4. Se la connessione fallisce, controllare i cavi, l'alimentazione e l'assegnazione della porta.

### 5.2 Controllo manuale e scorciatoie

- Selezionare un dito con i tasti **1–4** (1 = Anulare, 2 = Medio, 3 = Indice, 4 = Pollice).
- **Tasti freccia:** Su/Giù regolano la posizione; Sinistra/Destra regolano lo scostamento laterale.
- Tenendo premuto **Shift** la dimensione del passo si moltiplica per 5; **Ctrl** per 10.
- **Q / E:** chiudono / aprono completamente il dito selezionato.
- **C:** centra lo scostamento laterale.
- Gli slider sullo schermo rispecchiano l'input da tastiera in tempo reale.

![Manual finger control panel with keyboard shortcut overlay](../en/screenshots/manual_finger_control_frame.png)

![Example of fully closing a finger using controls](../en/screenshots/close_finger.png)

![Example of lateral movement adjustment](../en/screenshots/move_finger.png)

### 5.3 Impostazione delle velocità

- Il menu a tendina della velocità per dito (1 = lento, 6 = veloce) controlla la velocità dei servo.
- Il selettore **Global Speed** sincronizza le velocità di tutte le dita.
- Osservare le variazioni di velocità nella tabella di feedback (riga `Speed`) durante il movimento.

### 5.4 Applicazione ed eliminazione delle pose

1. Disporre le posizioni delle dita usando gli slider o le scorciatoie da tastiera.
2. In **Pose Management**, digitare un nome univoco e fare clic su **➕ Add New**.
3. Per applicare, selezionare la posa dal menu a tendina e fare clic su **✓ Apply**.
4. Per eliminare, selezionare la posa dal menu a tendina e fare clic su **🗑 Delete**. Una finestra di conferma impedisce la rimozione accidentale.

> Le pose memorizzano solo le posizioni dei servo; le velocità vengono determinate a runtime dalle impostazioni della GUI.

### 5.5 Costruzione ed esecuzione delle sequenze

1. Fare clic su **🔧 Manage** nel riproduttore di sequenze.
2. Nella finestra di dialogo:
   - Usare l'elenco **Available Poses** per aggiungere passi (doppio clic o premere **➕ Add**).
   - Regolare le velocità per dito tramite i campi numerici e impostare ritardi opzionali per i passi.
   - Inserire intervalli di pausa dedicati usando **⏱ Delay**.
   - Riordinare i passi con i pulsanti ↑/↓.
   - Inserire un nome e fare clic su **💾 Save Sequence**.
   - Fare clic su **▶ Execute** per provare senza salvare.
3. Tornati alla finestra principale, selezionare la sequenza e premere **▶ Play**. Abilitare **Loop** per la riproduzione continua.

> Le definizioni delle sequenze risiedono in `data/hand_config.yaml` sotto la chiave `sequences`. I loop sono controllati lato runtime, non nello YAML.

![Sequence manager dialog with available poses and sequence builder](../en/screenshots/sequences_editor.png)

### 5.6 Monitoraggio della telemetria

- Assicurarsi che le metriche desiderate siano spuntate nel menu **Display**.
- Usare gli slider di zoom/panoramica per concentrarsi sui segmenti di interesse.
- Passare il puntatore sugli elementi del grafico (interazioni standard di Matplotlib) per ispezionare i valori.
- La tabella di feedback si aggiorna in modo asincrono; le celle evidenziate indicano modifiche recenti.
- Se il grafico diventa congestionato, fare clic su **⌫ Clear** per azzerare i dati raccolti.

---

## 6. Interfaccia a riga di comando (`amazing_hand_cmd.py`)

La CLI consente di applicare pose e riprodurre sequenze direttamente da un terminale senza avviare la GUI. Legge lo stesso file `data/hand_config.yaml`.

### 6.1 Utilizzo di base

```bash
# List all saved poses and sequences
python amazing_hand_cmd.py --list

# Apply a single pose
python amazing_hand_cmd.py --pose open
python amazing_hand_cmd.py --pose close

# Play a sequence once
python amazing_hand_cmd.py --sequence demo

# Play a sequence in a loop (Ctrl+C to stop)
python amazing_hand_cmd.py --sequence wave --loop
```

### 6.2 Opzioni

| Opzione | Predefinito | Descrizione |
|--------|---------|-------------|
| `--pose NAME` | – | Applica la posa indicata e poi esce |
| `--sequence NAME` | – | Riproduce la sequenza indicata e poi esce |
| `--list` | – | Elenca tutte le pose e le sequenze |
| `--loop` | off | Ripete la sequenza in continuazione fino a Ctrl+C |
| `--port PORT` | `/dev/ttyACM0` (Linux) / `COM9` (Win) | Sostituzione della porta seriale |
| `--baudrate N` | `1000000` | Sostituzione del baud rate |
| `--config PATH` | `data/hand_config.yaml` | Percorso di un file di configurazione alternativo |

### 6.3 Note

- La coppia viene **attivata** alla connessione e **disattivata** all'uscita, così i servo si rilasciano al termine dello script.
- Le velocità e i ritardi per passo si comportano esattamente come nel riproduttore di sequenze della GUI.
- Il flag `--loop` può essere usato solo insieme a `--sequence`.

---

## 7. Risoluzione dei problemi

| Sintomo | Azione consigliata |
|---------|-----------------| 
| **No serial ports listed** | Ricollegare l'adattatore USB, installare i driver o riavviare la GUI. |
| **Connect button greyed out** | Già connessi; fare clic prima su **⏹ Disconnect**. |
| **Sluggish UI during resizing** | Le ottimizzazioni delle prestazioni (ridimensionamento con debounce, ridisegni limitati) riducono al minimo il problema, ma chiudere finestre non necessarie può aiutare. |
| **Sequence does not move all fingers** | Controllare le velocità per passo e assicurarsi che ogni posa contenga tutti e otto i valori dei servo. |
| **Blocked indicator persists** | Ispezionare eventuali ostruzioni meccaniche; lo stato di blocco viene attivato quando obiettivo e posizione differiscono in modo significativo senza movimento. |

---

## 8. Appendice

### 8.1 Struttura dei file

```
AmazingHandControl/
├── amazing_hand_gui.py          # GUI application
├── amazing_hand_cmd.py          # CLI tool
├── data/hand_config.yaml        # Poses & sequences
├── data/config.yaml             # Application settings
├── docs/<lang>/user_manual.md        # This document
├── docs/<lang>/CONFIG_FORMAT.md      # YAML config file reference
├── docs/en/screenshots/              # PNG captures embedded in this manual
├── docs/<lang>/scs_servo_protocol.md # SCS servo protocol reference
└── README.md                    # Quick reference
```

### 8.2 Link utili

- [AmazingHand (progetto ufficiale)](https://github.com/pollen-robotics/AmazingHand)
- [Strumento di debug dei servo Feetech](https://github.com/Robot-Maker-SAS/FeetechServo/tree/main/feetech%20debug%20tool%20master/FD1.9.8.2)
- [Tutorial per l'identificazione dei servo](https://www.robot-maker.com/forum/tutorials/article/168-brancher-et-controler-le-servomoteur-feetech-sts3032-360/)

---

## 9. Cronologia delle revisioni

| Data | Autore | Note |
|------|--------|-------|
| 2026-03-22 | Ingo | Aggiunta la sezione sulla CLI (`amazing_hand_cmd.py`); aggiornata la versione del manuale. |
| 2026-03-21 | Ingo | Aggiornamento del layout dei pannelli: scambio Ring/Pointer, Pollice spostato a destra, blocco dei controlli spostato a sinistra. Slider laterale del Pollice invertito. Aggiunto il pulsante di eliminazione della posa tra Apply e Name. I menu a tendina Port e Baudrate ora sono bloccati quando connessi. Le scorciatoie da tastiera 1–4 ora mappano Anulare/Medio/Indice/Pollice. |
| 2025-11-25 | Ingo | Aggiunta una galleria di screenshot ampliata, spiegazioni delle modalità del grafico e presentazioni dei pannelli aggiornate. |
| 2025-11-25 | Ingo | Manuale iniziale che copre i pannelli dell'interfaccia, i flussi di lavoro e l'uso della telemetria. |
