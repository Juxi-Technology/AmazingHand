---
title: "Protocollo, comandi e calibrazione dei servo PWM"
description: "Versione PWM di AmazingHand: gesti supportati, calibrazione del firmware, protocollo seriale, riferimento dei comandi, regolazione fine dei parametri dei gesti e domande frequenti."
version: pwm
---

# Protocollo, comandi e calibrazione dei servo PWM

Questa pagina copre il protocollo seriale del firmware PWM, i comandi, la calibrazione e la regolazione fine dei parametri. Per il cablaggio vedi [Cablaggio PWM](../01-hardware/pwm.md), per il flashing vedi [Avvio rapido PWM](../02-quick-start/pwm.md), per il controllo desktop/web vedi [Applicazione desktop PWM](../04-desktop/pwm.md) / [Controllo web PWM](../03-web-control/pwm.md).

> I seguenti comandi si eseguono nella directory `AmazingHand-PWM/` del repository. Sorgente del firmware: [`firmware/AmazingHand_Serial/`](../../../AmazingHand-PWM/firmware/AmazingHand_Serial/).

## 1. Panoramica di comandi e gesti

Le prime 11 righe sono comandi di gesti; le altre sono comandi di pilotaggio diretto, selezione del lato, ripetizione, arresto e test del collegamento.

| Gesto/comando | Comando | Descrizione |
|------|------|------|
| Sasso | 0x01 | Morra cinese: tutte le dita a pugno |
| Forbici | 0x02 | Morra cinese: indice + medio estesi a formare una V |
| Carta | 0x03 | Morra cinese: tutte le dita aperte |
| Pollice su | 0x04 | Pollice alzato, le altre dita a pugno |
| Beffa 1 | 0x05 | Oscilla l'indice ("no no no") |
| Beffa 2 | 0x06 | L'anulare si estende e oscilla (sostituisce il mignolo) |
| Apri | 0x07 | Tutte le dita aperte |
| Pugno | 0x08 | Tutte le dita chiuse |
| OK | 0x09 | Gesto OK |
| Pizzico | 0x0A | Gesto di pizzico |
| Indica | 0x0C | L'indice si estende per fare il gesto di "indicare" |
| Pilotaggio diretto | 0xF0 | Controllo diretto dell'angolo degli 8 servo |
| Imposta mano destra/sinistra | 0xF1 | Cambia la modalità mano sinistra/destra |
| Ripeti | 0xFE | Ripete l'esecuzione dell'ultimo gesto |
| Stop | 0xFF | Termina immediatamente il gesto corrente |
| NOP | 0x00 | Test del collegamento |

> Nota: il comando 0x0B è disattivato (l'originale "pollice in giù" era ripetuto con "pollice su" ed è stato rimosso).

---

## 2. Calibrazione del firmware (opzionale, consigliata al primo uso)

La posizione centrale e la larghezza d'impulso dei servo vanno calibrate in base al meccanismo reale e possono essere modificate direttamente nel sorgente del firmware:

- Modifica `middle_pos[8]` e `min_pw/mid_pw/max_pw[8]` all'inizio di `components/hand_servo/hand_servo.c`.

Dopo la calibrazione è necessario ricompilare e riflashare.

---

## 3. Protocollo di comunicazione seriale

### 3.1 Livello fisico

| Parametro | Valore |
|------|-----|
| Interfaccia | USB Serial (UART0) |
| Baudrate | **115200** |
| Bit di dati | 8 |
| Bit di parità | Nessuno (None) |
| Bit di stop | 1 |
| Controllo di flusso | Nessuno |

### 3.2 Formato dei frame

#### Host → ESP32 (frame di comando)

```
┌────────┬────────┬──────────┬────────────────┬──────────┐
│  0xAA  │ CMD_ID │ DATA_LEN │ DATA[0 .. N-1] │ CHECKSUM │
│ 1 Byte │ 1 Byte │  1 Byte  │    N Bytes     │  1 Byte  │
└────────┴────────┴──────────┴────────────────┴──────────┘
 intestazione  ID comando  lunghezza dati  payload dati  checksum
```

- **Intestazione**: fissa `0xAA`, identifica l'inizio di un frame
- **CMD_ID**: numero del comando (vedi [Riferimento dei comandi](#4-riferimento-dei-comandi))
- **DATA_LEN**: numero di byte del payload (0-8; i frame superiori a 8 non sono validi)
- **DATA**: payload dei dati, lunghezza determinata da DATA_LEN
- **CHECKSUM**: `CMD_ID ^ DATA_LEN ^ DATA[0] ^ ... ^ DATA[N-1]` (verifica XOR)

> Se DATA_LEN = 0, allora CHECKSUM = CMD_ID.

#### ESP32 → Host (frame di risposta)

```
┌────────┬────────┬────────┬──────────┐
│  0xBB  │ CMD_ID │ STATUS │ CHECKSUM │
│ 1 Byte │ 1 Byte │ 1 Byte │  1 Byte  │
└────────┴────────┴────────┴──────────┘
 intestazione  ID comando  codice di stato  checksum
```

- **Intestazione**: fissa `0xBB`
- **CMD_ID**: numero del comando originale
- **STATUS**: codice di stato (vedi tabella sotto)
- **CHECKSUM**: `CMD_ID ^ STATUS`

#### Codici di stato

| STATUS | Significato | Descrizione |
|--------|------|------|
| 0x00 | OK | Comando accettato, esecuzione avviata |
| 0x01 | Comando non valido | CMD_ID non presente nella tabella dei comandi |
| 0x02 | Errore di parametro | Lunghezza o contenuto dei dati non corretto |
| 0x03 | Occupato | Gesto in esecuzione, non accetta nuovi comandi per ora |
| 0x10 | Completato | Esecuzione del gesto terminata |

### 3.3 Sequenza di comunicazione

```
Host                          ESP32
 │                              │
 │──── [AA 01 00 01] ────────→│  Invio del comando "Sasso"
 │                              │
 │←─── [BB 01 00 01] ─────────│  ACK: comando accettato
 │                              │
 │                      (esecuzione del gesto)
 │                              │
 │←─── [BB 01 10 11] ─────────│  Completato: esecuzione del gesto terminata
 │                              │
 │──── [AA 02 00 02] ────────→│  Invio del comando "Forbici"
 │                              │
 │←─── [BB 02 00 02] ─────────│  ACK
 │                              │
```

### 3.4 Stop del gesto e timeout dei frame

- Inviando `[AA FF 00 FF]` è possibile interrompere in qualsiasi momento il gesto in esecuzione
- Se l'ESP32 non completa la ricezione di un frame entro 200 ms lo scarta automaticamente (per evitare una perdita di sincronizzazione permanente dovuta a byte persi)
- I frame con checksum non corrispondente vengono scartati silenziosamente; il PC host deve implementare il reinvio con timeout

### 3.5 Modalità mano destra/sinistra

Modalità mano destra predefinita. Invia `[AA F1 01 02 F2]` per passare alla mano sinistra, `[AA F1 01 01 F1]` per tornare alla mano destra. La mano destra/sinistra influenza la direzione di movimento del pollice (gesti Sasso/Forbici/Pollice su/OK/Pizzico ecc. che coinvolgono il pollice).

---

## 4. Riferimento dei comandi

### 4.1 Comandi dei gesti (0x01–0x0A, 0x0C)

Questi comandi non richiedono payload (DATA_LEN=0); l'ESP32 esegue immediatamente il gesto corrispondente.

| Comando | Frame HEX | Risposta | Descrizione |
|------|--------|------|------|
| Sasso | `AA 01 00 01` | `BB 01 00 01` → `BB 01 10 11` | Tutte le dita a pugno |
| Forbici | `AA 02 00 02` | `BB 02 00 02` → `BB 02 10 12` | Indice + medio estesi |
| Carta | `AA 03 00 03` | `BB 03 00 03` → `BB 03 10 13` | Tutte le dita aperte |
| Pollice su | `AA 04 00 04` | `BB 04 00 04` → `BB 04 10 14` | Pollice alzato |
| Beffa 1 | `AA 05 00 05` | `BB 05 00 05` → `BB 05 10 15` | Oscilla l'indice (circa 2,5 s) |
| Beffa 2 | `AA 06 00 06` | `BB 06 00 06` → `BB 06 10 16` | Oscilla l'anulare (circa 2,5 s) |
| Apri | `AA 07 00 07` | `BB 07 00 07` → `BB 07 10 17` | Tutte le dita aperte |
| Pugno | `AA 08 00 08` | `BB 08 00 08` → `BB 08 10 18` | Tutte le dita chiuse |
| OK | `AA 09 00 09` | `BB 09 00 09` → `BB 09 10 19` | Gesto OK |
| Pizzico | `AA 0A 00 0A` | `BB 0A 00 0A` → `BB 0A 10 1A` | Gesto di pizzico |
| Indica | `AA 0C 00 0C` | `BB 0C 00 0C` → `BB 0C 10 1C` | L'indice si estende per fare il gesto di "indicare" |

### 4.2 Comando di pilotaggio diretto (0xF0)

Controllo diretto dell'angolo degli 8 servo; gli 8 byte di dati corrispondono ai servo 1-8, con valore di ciascun byte da 0 a 180.

**Esempio: tutti i servo in posizione centrale (90°)**

```
Invio: AA F0 08 5A 5A 5A 5A 5A 5A 5A 5A F8
       │  │  │  └── 8 × 0x5A (90°) ──┘  │
       │  │  │                            └── CHECKSUM
       │  │  └── DATA_LEN = 8
       │  └── CMD_DIRECT_DRIVE
       └── intestazione
```

Checksum = `F0 ^ 08 ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A` = `F8`

> 8 valori 0x5A uguali, XOR a due a due, danno 0x00; alla fine `0xF0 ^ 0x08 ^ 0x00 = 0xF8`

**Esempio: indice aperto (servo1=170°, servo2=10°), gli altri in posizione centrale (90°)**

```
Invio: AA F0 08 AA 0A 5A 5A 5A 5A 5A 5A 58
               └─170°  └─10°
```

### 4.3 Impostazione mano destra/sinistra (0xF1)

1 byte di dati: `0x01` = mano destra, `0x02` = mano sinistra.

```
Imposta mano destra: AA F1 01 01 F1
Imposta mano sinistra: AA F1 01 02 F2
```

### 4.4 Comandi di controllo

| Comando | Frame HEX | Descrizione |
|------|--------|------|
| NOP | `AA 00 00 00` | Test del collegamento, restituisce immediatamente `BB 00 00 00` |
| Ripeti | `AA FE 00 FE` | Ripete l'esecuzione dell'ultimo gesto |
| Stop | `AA FF 00 FF` | Termina immediatamente il gesto corrente |

### 4.5 Riepilogo delle risposte

Alla ricezione di un comando non valido (prendendo come esempio il comando inesistente 0xFC):

```
Invio: AA FC 00 FC
Risposta: BB FC 01 FD    （STATUS=0x01 comando non valido）
```

> Verifica del checksum: `FC ^ 00 = FC`, risposta `FC ^ 01 = FD`

---

## 5. Regolazione fine dei parametri dei gesti

### 5.1 Posizione dei parametri

L'offset angolare di ogni gesto è definito con macro `#define`, **senza modificare il codice logico**, si regolano solo i valori.

- **Versione ESP-IDF**: area "parametri dei gesti (regolabili dall'utente)" all'inizio di `components/hand_gestures/hand_gestures.c`

### 5.2 Significato dei parametri

```c
// Esempio: gesto Sasso
#define ROCK_IDX_OFF1    70    // offset del giunto 1 dell'indice
#define ROCK_IDX_OFF2   -70    // offset del giunto 2 dell'indice
```

- **Valore positivo = flessione/chiusura**, **valore negativo = estensione/apertura**
- 2 offset per ogni dito, rispetto a `middle_pos` (predefinito 90°)
- Struttura differenziale: i due servo sono affiancati con assi collineari; la rotazione nello stesso verso produce la divaricazione laterale, quella in versi opposti produce la flessione; la somma dei due angoli di offset corrisponde alla divaricazione, la differenza alla flessione.

### 5.3 Procedura di regolazione

1. Trova la macro `#define` del gesto corrispondente
2. Modifica il valore (aumentare → ampiezza maggiore; diminuire → ampiezza minore)
3. Ricompila e riflasha, testa il risultato con l'applicazione desktop
4. Regola ripetutamente finché il movimento risulta naturale

---

## 6. Domande frequenti

### D1: Il PC host non si connette alla seriale?

1. Verifica che l'ESP32 sia collegato al PC tramite Type-C
2. Controlla che il numero di porta COM in Gestione dispositivi corrisponda a quello selezionato nella GUI
3. Verifica il baudrate 115200
4. Disconnetti gli altri software che occupano la seriale

### D2: L'invio di un comando non produce risposta?

1. Invia prima `AA 00 00 00` (NOP); dovresti ricevere `BB 00 00 00`
2. Verifica che il firmware sia flashato e che il chip target sia ESP32-S3
3. Controlla il cablaggio (GND in massa comune)

### D3: L'ampiezza del gesto è sbagliata o la direzione è invertita?

Entra nella regolazione fine dei parametri dei gesti (vedi [sezione 5](#5-regolazione-fine-dei-parametri-dei-gesti)) e regola la macro corrispondente.

### D4: Quali gesti sono influenzati dalla modalità mano destra/sinistra?

I gesti **che coinvolgono il pollice** come Sasso/Forbici/Pollice su/OK/Pizzico; dopo il cambio di mano la direzione speculare del pollice cambia.

### D5: Le dita si bloccano e non si estendono?

Prima di ogni gesto di chiusura viene automaticamente eseguito un «prima apri tutta la mano e poi chiudi», per evitare che le dita vengano bloccate dal gesto precedente. Se il blocco persiste, controlla l'assemblaggio meccanico o riduci l'ampiezza di chiusura.

## Pagine correlate

- [Cablaggio, GPIO e alimentazione PWM](../01-hardware/pwm.md)
- [Avvio rapido PWM](../02-quick-start/pwm.md)
- [Applicazione desktop PWM](../04-desktop/pwm.md)
- [Tracciamento delle mani PWM](../05-hand-tracking/pwm.md)
- [FAQ](../08-faq/faq.md)
