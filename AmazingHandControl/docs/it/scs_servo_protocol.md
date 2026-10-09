[English](../en/scs_servo_protocol.md) | [Deutsch](../de/scs_servo_protocol.md) | [Español](../es/scs_servo_protocol.md) | [Français](../fr/scs_servo_protocol.md) | Italiano | [日本語](../ja/scs_servo_protocol.md) | [한국어](../ko/scs_servo_protocol.md) | [Português (BR)](../pt-br/scs_servo_protocol.md) | [Português (PT)](../pt-pt/scs_servo_protocol.md) | [简体中文](../zh-hans/scs_servo_protocol.md) | [繁體中文](../zh-hant/scs_servo_protocol.md)

# Servo SCSCL con potenziometro – Descrizione della tabella di memoria

## Indice

- [Servo SCSCL con potenziometro – Descrizione della tabella di memoria](#servo-scscl-con-potenziometro--descrizione-della-tabella-di-memoria)
- [1. Protocollo di comunicazione del servo](#1-protocollo-di-comunicazione-del-servo)
- [2. Definizione della tabella di memoria del servo](#2-definizione-della-tabella-di-memoria-del-servo)
  - [2.1 Informazioni sulla versione](#21-informazioni-sulla-versione)
  - [2.2 Configurazione EPROM](#22-configurazione-eprom)
  - [2.3 Controllo SRAM](#23-controllo-sram)
  - [2.4 Feedback SRAM](#24-feedback-sram)
  - [2.5 Parametri di fabbrica](#25-parametri-di-fabbrica)
- [3. Descrizione dei byte speciali](#3-descrizione-dei-byte-speciali)
  - [3.1 Fase del servo](#31-fase-del-servo)
  - [3.2 Stato del servo](#32-stato-del-servo)
  - [3.3 Condizioni di sgancio](#33-condizioni-di-sgancio)
  - [3.4 Condizioni di allarme LED](#34-condizioni-di-allarme-led)

---

## 1. Protocollo di comunicazione del servo

Il servo usa il **protocollo personalizzato FT-SCS**.  

- Baud rate predefinito: **1 Mbps o 500 kbps**
- Livello fisico: **bus singolo TTL**
- Bit di dati: **8**
- Parità: **nessuna**
- Bit di stop: **1**
- Intervallo di baud configurabile: **38 400 ~ 1 Mbps (500 k)**
- Indirizzo di comunicazione predefinito (ID): **1**

Riferimento al protocollo:  
[FT-SCS Custom Protocol](http://doc.feetech.cn/#/tiaozhunlujingft?srcType=FT-SCS-Protocol-41ad23fe8a244712ba160b93)

---

## 2. Definizione della tabella di memoria del servo

> Se un indirizzo di funzione usa un valore a 2 byte, il **byte alto** è memorizzato all'**indirizzo più basso**, e il **byte basso** all'**indirizzo più alto** (big-endian all'interno della tabella).

---

### 2.1 Informazioni sulla versione

| Address DEC | Address HEX | Nome funzione           | Bytes | Default | Access | Range | Unit | Descrizione                            |
|-------------|-------------|-------------------------|-------|---------|--------|-------|------|----------------------------------------|
| 0           | 0x00        | Versione principale del firmware | 1     | –       | R      |       |      |                                        |
| 1           | 0x01        | Versione secondaria del firmware | 1     | –       | R      |       |      |                                        |
| 2           | 0x02        | END                     | 1     | 1       | R      |       |      | `1` indica memorizzazione big-endian       |
| 3           | 0x03        | Versione principale del servo | 1     | –       | R      |       |      |                                        |
| 4           | 0x04        | Versione secondaria del servo | 1     | –       | R      |       |      |                                        |

---

### 2.2 Configurazione EPROM

| Address DEC | Address HEX | Nome funzione                 | Bytes | Default | Access | Range       | Unit  | Descrizione                                                                                                                                         |
|-------------|-------------|-------------------------------|-------|---------|--------|-------------|-------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 5           | 0x05        | ID servo                      | 1     | 1       | R/W   | 0 ~ 253     | ID    | ID principale univoco sul bus                                                                                                                           |
| 6           | 0x06        | Baud rate                     | 1     | 0       | R/W   | 0 ~ 7       | –     | 0–7 rappresentano il baud: 1000000(0), 500000(1), 250000(2), 128000(3), 115200(4), 76800(5), 57600(6), 38400(7)                                           |
| 7           | 0x07        | Non definito                  | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 8           | 0x08        | Livello di ritorno dello stato | 1     | 1       | R/W   | 0 ~ 1       | –     | 0: solo READ e PING restituiscono lo stato; 1: tutti i comandi restituiscono pacchetti di stato                                                                          |
| 9           | 0x09        | Limite minimo di angolo       | 2     | 20      | R/W   | 0 ~ 1023    | steps | Angolo operativo minimo; deve essere inferiore all'angolo massimo. Se **angolo min = angolo max = 0** → modalità motore (rotazione continua)                          |
| 11          | 0x0B        | Limite massimo di angolo      | 2     | 1003    | R/W   | 1 ~ 1023    | steps | Angolo operativo massimo; deve essere superiore all'angolo minimo. Se **angolo min = angolo max = 0** → modalità motore                                             |
| 13          | 0x0D        | Limite massimo di temperatura | 1     | 70      | R/W   | 0 ~ 100     | °C    |                                                                                                                                                     |
| 14          | 0x0E        | Tensione di ingresso massima  | 1     | –       | R/W   | 0 ~ 254     | 0.1 V | Se **tensione di ingresso max = tensione di ingresso min = 0**, il feedback di tensione è disabilitato                                                                      |
| 15          | 0x0F        | Tensione di ingresso minima   | 1     | 40      | R/W   | 0 ~ 254     | 0.1 V | Se **tensione di ingresso max = tensione di ingresso min = 0**, il feedback di tensione è disabilitato                                                                      |
| 16          | 0x10        | Coppia massima                | 2     | 1000    | R/W   | 0 ~ 1000    | 0.1%  | All'accensione questo valore viene copiato all'indirizzo 48 (limite di coppia)                                                                                       |
| 18          | 0x12        | Fase                          | 1     | –       | R/W   | 0 ~ 254     | –     | Byte a funzione speciale; non modificare senza una necessità specifica                                                                                          |
| 19          | 0x13        | Condizioni di sgancio         | 1     | –       | R/W   | 0 ~ 254     | –     | Ogni bit abilita/disabilita una protezione corrispondente (vedi [3.3](#33-condizioni-di-sgancio))                                                             |
| 20          | 0x14        | Condizioni di allarme LED     | 1     | –       | R/W   | 0 ~ 254     | –     | Ogni bit abilita/disabilita il lampeggio del LED per un dato allarme (vedi [3.4](#34-condizioni-di-allarme-led))                                                     |
| 21          | 0x15        | Guadagno P dell'anello di posizione | 1     | –       | R/W   | 0 ~ 254     | –     | Guadagno proporzionale per il controllo di posizione                                                                                                              |
| 22          | 0x16        | Guadagno D dell'anello di posizione | 1     | –       | R/W   | 0 ~ 254     | –     | Guadagno derivativo per il controllo di posizione                                                                                                                |
| 23          | 0x17        | Non definito                  | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 24          | 0x18        | Coppia minima di avvio        | 1     | –       | R/W   | 0 ~ 254     | 0.1%  | Coppia minima in uscita necessaria per iniziare il movimento                                                                                                    |
| 25          | 0x19        | Non definito                  | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 26          | 0x1A        | Zona morta in avanti          | 1     | 1       | R/W   | 0 ~ 16      | steps | L'unità più piccola è un angolo minimo di risoluzione                                                                                                       |
| 27          | 0x1B        | Zona morta all'indietro       | 1     | 1       | R/W   | 0 ~ 16      | steps | L'unità più piccola è un angolo minimo di risoluzione                                                                                                       |
| 28 ~ 36     | 0x1C ~ 0x24 | Non definito                  | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 37          | 0x25        | Coppia di mantenimento        | 1     | 20      | R/W   | 0 ~ 254     | 1%    | Coppia in uscita dopo l'attivazione della protezione da sovraccarico; ad es. 20 = 20% della coppia massima                                                                  |
| 38          | 0x26        | Tempo di protezione           | 1     | 200     | R/W   | 0 ~ 254     | 10 ms | Tempo per cui il carico supera la coppia di sovraccarico prima dell'attivazione della protezione; 200 = 2 s, max ≈ 2,5 s                                                          |
| 39          | 0x24        | Coppia di sovraccarico        | 1     | 80      | R/W   | 0 ~ 254     | 1%    | Coppia di soglia per avviare il timer di protezione da sovraccarico; 80 = 80% della coppia massima                                                                 |

---

### 2.3 Controllo SRAM

| Address DEC | Address HEX | Nome funzione   | Bytes | Default | Access | Range                | Unit   | Descrizione                                                                                                                                                            |
|-------------|-------------|-----------------|-------|---------|--------|----------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 40          | 0x28        | Interruttore di coppia   | 1     | 0       | R/W   | 0 ~ 2                | –      | 0: coppia disattivata / libero; 1: coppia attiva; 2: modalità smorzamento                                                                                                                   |
| 41          | 0x29        | Non definito       | 1     | –       | R/W   | –                    | –      | –                                                                                                                                                                      |
| 42          | 0x2A        | Posizione obiettivo   | 2     | 0       | R/W   | 0 ~ 1023             | steps  | Ogni passo è un angolo minimo di risoluzione; controllo di posizione assoluto. Il valore massimo corrisponde all'angolo effettivo massimo                                                |
| 44          | 0x2C        | Tempo di esecuzione    | 2     | 0       | R/W   | 0 ~ 9999 / -1000~1000| 1 ms / 0.1% | Tempo dalla posizione corrente alla posizione obiettivo quando **velocità di esecuzione = 0**. In modalità motore, imposta il duty PWM in uscita; il bit 10 è il bit di direzione                                  |
| 46          | 0x2E        | Velocità di esecuzione       | 2     | Factory default max speed | R/W | 0 ~ 1000           | steps/s| Passi al secondo (velocità di movimento)                                                                                                                                     |
| 48          | 0x30        | Flag di blocco       | 1     | 1       | R/W   | 0 ~ 1                | –      | 0: sblocca la scrittura EPROM, i valori scritti agli indirizzi EPROM vengono memorizzati dopo lo spegnimento; 1: blocca la scrittura EPROM, i valori scritti agli indirizzi EPROM **non** vengono memorizzati        |
| 49 ~ 56     | 0x32~0x36   | Non definito       | 1     |         |        |                      |        | –                                                                                                                                                                      |

---

### 2.4 Feedback SRAM

| Address DEC | Address HEX | Nome funzione     | Bytes | Default | Access | Range | Unit   | Descrizione                                                                                                                                                        |
|-------------|-------------|-------------------|-------|---------|--------|-------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 56          | 0x38        | Posizione corrente  | 2     | –       | R      | –     | steps  | Posizione corrente in passi; ogni passo è un angolo minimo di risoluzione. Modalità posizione assoluta; il valore massimo corrisponde all'angolo effettivo massimo                    |
| 58          | 0x3A        | Velocità corrente     | 2     | –       | R      | –     | steps/s| Velocità corrente del motore in passi al secondo                                                                                                                            |
| 60          | 0x3C        | Carico corrente      | 2     | –       | R      | –     | 0.1%   | Duty cycle corrente dell'uscita di controllo che pilota il motore; il bit 10 è il bit di direzione                                                                                       |
| 62          | 0x3E        | Tensione corrente   | 1     | –       | R      | –     | 0.1 V  | Tensione di alimentazione corrente del servo                                                                                                                                       |
| 63          | 0x3F        | Temperatura corrente | 1   | –       | R      | –     | °C     | Temperatura interna corrente del servo                                                                                                                                 |
| 64          | 0x40        | Flag di scrittura asincrona  | 1     | 0       | R      | –     | –      | Flag usato quando si utilizzano comandi di scrittura asincrona                                                                                                               |
| 65          | 0x41        | Stato del servo      | 1     | 0       | R      | –     | –      | I bit impostati a 1 indicano il/i relativo/i errore/i (vedi [3.2](#32-stato-del-servo))                                                                                       |
| 66          | 0x42        | Flag di movimento     | 1     | 0       | R      | –     | –      | 1 mentre il servo si muove; 0 quando ha raggiunto il bersaglio e si è fermato; resta 0 se non viene fornita una nuova posizione obiettivo                                                   |

---

### 2.5 Parametri di fabbrica

| Address DEC | Address HEX | Nome funzione                  | Bytes | Default | Access | Range | Unit | Descrizione |
|-------------|-------------|--------------------------------|-------|---------|--------|-------|------|-------------|
| 78          | 0x4E        | Passo massimo in modalità PWM  | 1     | 20      | R      | –     | –    | –           |
| 79          | 0x50        | Soglia di velocità di movimento × 50 | 1     | 1       | R      | –     | –    | –           |
| 80          | 0x51        | DTs (ms)                      | 1     | 20      | R      | –     | –    | –           |
| 81          | 0x52        | Limite minimo di velocità × 50 | 1     | 1       | R      | –     | –    | –           |
| 82          | 0x53        | Limite massimo di velocità × 50 | 1     | –       | R      | –     | –    | –           |
| 83          | 0x54        | Accelerazione                  | 1     | 20      | R      | –     | –    | –           |

---

## 3. Descrizione dei byte speciali

---

### 3.1 Fase del servo

**Bit / peso: descrizione**

- **BIT0 (1)**: Fase della direzione di azionamento  
  - 0: direzione normale  
  - 1: direzione invertita
- **BIT1 (2)**: –––
- **BIT2 (4)**: –––
- **BIT3 (8)**: Modalità velocità  
  - 0: velocità = 0 significa stop  
  - 1: velocità = 0 significa velocità massima
- **BIT4 (16)**: –––
- **BIT5 (32)**: Fase PWM  
  - 0: in fase  
  - 1: invertita
- **BIT6 (64)**: Modalità tensione  
  - 0: rilevamento a bassa tensione 1,5 k  
  - 1: rilevamento ad alta tensione 1 k
- **BIT7 (128)**: –––

> Se più bit sono impostati contemporaneamente, il **valore di fase** è la **somma** dei valori di tutti i bit impostati.

---

### 3.2 Stato del servo

**Stato del servo: 0 = normale, 1 = guasto**

**Bit / peso: descrizione**

- **BIT0 (1)**: Stato della tensione  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Stato della temperatura  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Stato del carico  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Se sono presenti più condizioni di guasto, il **valore di stato** è la **somma** dei valori dei bit corrispondenti.  
> Esempio: sovratensione/sottotensione e sovratemperatura → stato = 4 + 1 = **5**.

---

### 3.3 Condizioni di sgancio

**Condizioni di sgancio: 0 = disabilitato, 1 = abilitato**  
("Unload" = la coppia viene disattivata come protezione.)

**Bit / peso: descrizione**

- **BIT0 (1)**: Protezione dalla tensione  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Protezione dalla sovratemperatura  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Protezione dal sovraccarico  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Se più bit sono impostati, il **valore della condizione di sgancio** è la **somma** dei valori dei bit.  
> Esempio: protezione dalla tensione + protezione dalla sovratemperatura abilitate → valore di sgancio = 4 + 1 = **5**.

---

### 3.4 Condizioni di allarme LED

**Condizioni di allarme LED: 0 = spento, 1 = acceso**

**Bit / peso: descrizione**

- **BIT0 (1)**: Allarme di tensione  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Allarme di sovratemperatura  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Allarme di sovraccarico  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Se più bit sono impostati, il **valore della condizione di allarme LED** è la **somma** dei valori dei bit.  
> Esempio: allarme di tensione + allarme di sovratemperatura abilitati → valore di allarme = 4 + 1 = **5**.
