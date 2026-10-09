[English](../en/scs_servo_protocol.md) | Deutsch | [Español](../es/scs_servo_protocol.md) | [Français](../fr/scs_servo_protocol.md) | [Italiano](../it/scs_servo_protocol.md) | [日本語](../ja/scs_servo_protocol.md) | [한국어](../ko/scs_servo_protocol.md) | [Português (BR)](../pt-br/scs_servo_protocol.md) | [Português (PT)](../pt-pt/scs_servo_protocol.md) | [简体中文](../zh-hans/scs_servo_protocol.md) | [繁體中文](../zh-hant/scs_servo_protocol.md)

# Potentiometer-SCSCL-Servo – Speichertabellenbeschreibung

## Inhaltsverzeichnis

- [Potentiometer-SCSCL-Servo – Speichertabellenbeschreibung](#potentiometer-scscl-servo--speichertabellenbeschreibung)
- [1. Servo-Kommunikationsprotokoll](#1-servo-kommunikationsprotokoll)
- [2. Definition der Servo-Speichertabelle](#2-definition-der-servo-speichertabelle)
  - [2.1 Versionsinformationen](#21-versionsinformationen)
  - [2.2 EPROM-Konfiguration](#22-eprom-konfiguration)
  - [2.3 SRAM-Steuerung](#23-sram-steuerung)
  - [2.4 SRAM-Rückmeldung](#24-sram-rückmeldung)
  - [2.5 Werksparameter](#25-werksparameter)
- [3. Beschreibung spezieller Bytes](#3-beschreibung-spezieller-bytes)
  - [3.1 Servo-Phase](#31-servo-phase)
  - [3.2 Servo-Status](#32-servo-status)
  - [3.3 Entlastungsbedingungen](#33-entlastungsbedingungen)
  - [3.4 LED-Alarmbedingungen](#34-led-alarmbedingungen)

---

## 1. Servo-Kommunikationsprotokoll

Der Servo verwendet das **FT-SCS-Custom-Protokoll**.  

- Standard-Baudrate: **1 Mbps oder 500 kbps**
- Physikalische Schicht: **TTL-Einzelbus**
- Datenbits: **8**
- Parität: **keine**
- Stoppbits: **1**
- Konfigurierbarer Baudbereich: **38 400 ~ 1 Mbps (500 k)**
- Standard-Kommunikationsadresse (ID): **1**

Protokollreferenz:  
[FT-SCS-Custom-Protokoll](http://doc.feetech.cn/#/tiaozhunlujingft?srcType=FT-SCS-Protocol-41ad23fe8a244712ba160b93)

---

## 2. Definition der Servo-Speichertabelle

> Wenn eine Funktionsadresse einen 2-Byte-Wert verwendet, wird das **höherwertige Byte** an der **niedrigeren Adresse** gespeichert und das **niedrigere Byte** an der **höheren Adresse** (Big-Endian innerhalb der Tabelle).

---

### 2.1 Versionsinformationen

| Address DEC | Address HEX | Funktionsname           | Bytes | Default | Access | Range | Unit | Beschreibung                            |
|-------------|-------------|-------------------------|-------|---------|--------|-------|------|----------------------------------------|
| 0           | 0x00        | Firmware-Hauptversion   | 1     | –       | R      |       |      |                                        |
| 1           | 0x01        | Firmware-Nebenversion   | 1     | –       | R      |       |      |                                        |
| 2           | 0x02        | END                     | 1     | 1       | R      |       |      | `1` bedeutet Big-Endian-Speicherung    |
| 3           | 0x03        | Servo-Hauptversion      | 1     | –       | R      |       |      |                                        |
| 4           | 0x04        | Servo-Nebenversion      | 1     | –       | R      |       |      |                                        |

---

### 2.2 EPROM-Konfiguration

| Address DEC | Address HEX | Funktionsname                 | Bytes | Default | Access | Range       | Unit  | Beschreibung                                                                                                                                        |
|-------------|-------------|-------------------------------|-------|---------|--------|-------------|-------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 5           | 0x05        | Servo-ID                      | 1     | 1       | R/W   | 0 ~ 253     | ID    | Eindeutige Haupt-ID auf dem Bus                                                                                                                     |
| 6           | 0x06        | Baudrate                      | 1     | 0       | R/W   | 0 ~ 7       | –     | 0–7 stehen für Baud: 1000000(0), 500000(1), 250000(2), 128000(3), 115200(4), 76800(5), 57600(6), 38400(7)                                           |
| 7           | 0x07        | Nicht definiert               | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 8           | 0x08        | Status-Rückgabeebene          | 1     | 1       | R/W   | 0 ~ 1       | –     | 0: nur READ und PING geben Status zurück; 1: alle Befehle geben Statuspakete zurück                                                                 |
| 9           | 0x09        | Minimaler Winkelgrenzwert     | 2     | 20      | R/W   | 0 ~ 1023    | steps | Minimaler Betriebswinkel; muss kleiner als der maximale Winkel sein. Wenn **min angle = max angle = 0** → Motor-(Dauerrotations-)Modus              |
| 11          | 0x0B        | Maximaler Winkelgrenzwert     | 2     | 1003    | R/W   | 1 ~ 1023    | steps | Maximaler Betriebswinkel; muss größer als der minimale Winkel sein. Wenn **min angle = max angle = 0** → Motor-Modus                                |
| 13          | 0x0D        | Maximaler Temperaturgrenzwert | 1     | 70      | R/W   | 0 ~ 100     | °C    |                                                                                                                                                     |
| 14          | 0x0E        | Maximale Eingangsspannung     | 1     | –       | R/W   | 0 ~ 254     | 0.1 V | Wenn **max input voltage = min input voltage = 0**, ist die Spannungsrückmeldung deaktiviert                                                        |
| 15          | 0x0F        | Minimale Eingangsspannung     | 1     | 40      | R/W   | 0 ~ 254     | 0.1 V | Wenn **max input voltage = min input voltage = 0**, ist die Spannungsrückmeldung deaktiviert                                                        |
| 16          | 0x10        | Maximales Drehmoment          | 2     | 1000    | R/W   | 0 ~ 1000    | 0.1%  | Beim Einschalten wird dieser Wert an Adresse 48 (Drehmomentgrenze) kopiert                                                                          |
| 18          | 0x12        | Phase                         | 1     | –       | R/W   | 0 ~ 254     | –     | Spezielles Funktionsbyte; ohne konkreten Bedarf nicht ändern                                                                                        |
| 19          | 0x13        | Entlastungsbedingungen        | 1     | –       | R/W   | 0 ~ 254     | –     | Jedes Bit aktiviert/deaktiviert einen entsprechenden Schutz (siehe [3.3](#33-entlastungsbedingungen))                                              |
| 20          | 0x14        | LED-Alarmbedingungen          | 1     | –       | R/W   | 0 ~ 254     | –     | Jedes Bit aktiviert/deaktiviert das LED-Blinken für einen bestimmten Alarm (siehe [3.4](#34-led-alarmbedingungen))                                 |
| 21          | 0x15        | P-Verstärkung des Positionsregelkreises | 1 | –  | R/W   | 0 ~ 254     | –     | Proportionalverstärkung für die Positionsregelung                                                                                                   |
| 22          | 0x16        | D-Verstärkung des Positionsregelkreises | 1 | –  | R/W   | 0 ~ 254     | –     | Differenzialverstärkung für die Positionsregelung                                                                                                   |
| 23          | 0x17        | Nicht definiert               | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 24          | 0x18        | Minimales Anlaufdrehmoment    | 1     | –       | R/W   | 0 ~ 254     | 0.1%  | Minimaler Drehmomentausgang, der zum Starten der Bewegung erforderlich ist                                                                          |
| 25          | 0x19        | Nicht definiert               | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 26          | 0x1A        | Vorwärts-Totband              | 1     | 1       | R/W   | 0 ~ 16      | steps | Kleinste Einheit ist ein minimaler Auflösungswinkel                                                                                                 |
| 27          | 0x1B        | Rückwärts-Totband             | 1     | 1       | R/W   | 0 ~ 16      | steps | Kleinste Einheit ist ein minimaler Auflösungswinkel                                                                                                 |
| 28 ~ 36     | 0x1C ~ 0x24 | Nicht definiert               | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 37          | 0x25        | Haltedrehmoment               | 1     | 20      | R/W   | 0 ~ 254     | 1%    | Drehmomentausgang nach Auslösung des Überlastschutzes; z. B. 20 = 20% des maximalen Drehmoments                                                    |
| 38          | 0x26        | Schutzzeit                    | 1     | 200     | R/W   | 0 ~ 254     | 10 ms | Zeit, in der die Last das Überlastdrehmoment überschreitet, bevor der Schutz auslöst; 200 = 2 s, max. ≈ 2.5 s                                        |
| 39          | 0x24        | Überlastdrehmoment            | 1     | 80      | R/W   | 0 ~ 254     | 1%    | Schwellendrehmoment zum Starten des Überlastschutz-Timers; 80 = 80% des maximalen Drehmoments                                                       |

---

### 2.3 SRAM-Steuerung

| Address DEC | Address HEX | Funktionsname   | Bytes | Default | Access | Range                | Unit   | Beschreibung                                                                                                                                                           |
|-------------|-------------|-----------------|-------|---------|--------|----------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 40          | 0x28        | Drehmomentschalter | 1  | 0       | R/W   | 0 ~ 2                | –      | 0: Drehmoment aus / frei; 1: Drehmoment an; 2: Dämpfungsmodus                                                                                                          |
| 41          | 0x29        | Nicht definiert | 1     | –       | R/W   | –                    | –      | –                                                                                                                                                                      |
| 42          | 0x2A        | Zielposition    | 2     | 0       | R/W   | 0 ~ 1023             | steps  | Jeder Schritt ist ein minimaler Auflösungswinkel; absolute Positionssteuerung. Der maximale Wert entspricht dem maximalen effektiven Winkel                             |
| 44          | 0x2C        | Laufzeit        | 2     | 0       | R/W   | 0 ~ 9999 / -1000~1000| 1 ms / 0.1% | Zeit von der aktuellen Position zur Zielposition, wenn **run speed = 0**. Im Motor-Modus legt dies den PWM-Ausgangstastgrad fest; Bit 10 ist das Richtungsbit             |
| 46          | 0x2E        | Laufgeschwindigkeit | 2 | Factory default max speed | R/W | 0 ~ 1000           | steps/s| Schritte pro Sekunde (Bewegungsgeschwindigkeit)                                                                                                                        |
| 48          | 0x30        | Sperrflag       | 1     | 1       | R/W   | 0 ~ 1                | –      | 0: EPROM-Schreiben entsperren, in EPROM-Adressen geschriebene Werte werden nach dem Ausschalten gespeichert; 1: EPROM-Schreiben sperren, in EPROM-Adressen geschriebene Werte werden **nicht** gespeichert        |
| 49 ~ 56     | 0x32~0x36   | Nicht definiert | 1     |         |        |                      |        | –                                                                                                                                                                      |

---

### 2.4 SRAM-Rückmeldung

| Address DEC | Address HEX | Funktionsname     | Bytes | Default | Access | Range | Unit   | Beschreibung                                                                                                                                                       |
|-------------|-------------|-------------------|-------|---------|--------|-------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 56          | 0x38        | Aktuelle Position | 2     | –       | R      | –     | steps  | Aktuelle Position in Schritten; jeder Schritt ist ein minimaler Auflösungswinkel. Absoluter Positionsmodus; der maximale Wert entspricht dem maximalen effektiven Winkel   |
| 58          | 0x3A        | Aktuelle Geschwindigkeit | 2 | –  | R      | –     | steps/s| Aktuelle Motorgeschwindigkeit in Schritten pro Sekunde                                                                                                             |
| 60          | 0x3C        | Aktuelle Last     | 2     | –       | R      | –     | 0.1%   | Aktueller Steuerausgangs-Tastgrad, der den Motor antreibt; Bit 10 ist das Richtungsbit                                                                              |
| 62          | 0x3E        | Aktuelle Spannung | 1     | –       | R      | –     | 0.1 V  | Aktuelle Versorgungsspannung des Servos                                                                                                                             |
| 63          | 0x3F        | Aktuelle Temperatur | 1   | –       | R      | –     | °C     | Aktuelle interne Servotemperatur                                                                                                                                    |
| 64          | 0x40        | Asynchrones Schreibflag | 1 | 0    | R      | –     | –      | Flag, das bei asynchronen Schreibbefehlen verwendet wird                                                                                                           |
| 65          | 0x41        | Servo-Status      | 1     | 0       | R      | –     | –      | Auf 1 gesetzte Bits zeigen den/die entsprechenden Fehler an (siehe [3.2](#32-servo-status))                                                                        |
| 66          | 0x42        | Bewegungsflag     | 1     | 0       | R      | –     | –      | 1, solange sich der Servo bewegt; 0, wenn er das Ziel erreicht und angehalten hat; bleibt 0, wenn keine neue Zielposition vorgegeben wird                           |

---

### 2.5 Werksparameter

| Address DEC | Address HEX | Funktionsname                  | Bytes | Default | Access | Range | Unit | Beschreibung |
|-------------|-------------|--------------------------------|-------|---------|--------|-------|------|-------------|
| 78          | 0x4E        | Maximaler Schritt im PWM-Modus | 1     | 20      | R      | –     | –    | –            |
| 79          | 0x50        | Bewegungsgeschwindigkeits-Schwelle × 50 | 1 | 1   | R      | –     | –    | –            |
| 80          | 0x51        | DTs (ms)                       | 1     | 20      | R      | –     | –    | –            |
| 81          | 0x52        | Minimaler Geschwindigkeitsgrenzwert × 50 | 1 | 1 | R    | –     | –    | –            |
| 82          | 0x53        | Maximaler Geschwindigkeitsgrenzwert × 50 | 1 | – | R    | –     | –    | –            |
| 83          | 0x54        | Beschleunigung                 | 1     | 20      | R      | –     | –    | –            |

---

## 3. Beschreibung spezieller Bytes

---

### 3.1 Servo-Phase

**Bits / Gewicht: Beschreibung**

- **BIT0 (1)**: Antriebsrichtungsphase  
  - 0: normale Richtung  
  - 1: umgekehrte Richtung
- **BIT1 (2)**: –––
- **BIT2 (4)**: –––
- **BIT3 (8)**: Geschwindigkeitsmodus  
  - 0: Geschwindigkeit = 0 bedeutet Stopp  
  - 1: Geschwindigkeit = 0 bedeutet maximale Geschwindigkeit
- **BIT4 (16)**: –––
- **BIT5 (32)**: PWM-Phase  
  - 0: gleichphasig  
  - 1: invertiert
- **BIT6 (64)**: Spannungsmodus  
  - 0: 1.5 k Niederspannungserfassung  
  - 1: 1 k Hochspannungserfassung
- **BIT7 (128)**: –––

> Wenn mehrere Bits gleichzeitig gesetzt sind, ist der **Phasenwert** die **Summe** der Werte aller gesetzten Bits.

---

### 3.2 Servo-Status

**Servo-Status: 0 = normal, 1 = Fehler**

**Bits / Gewicht: Beschreibung**

- **BIT0 (1)**: Spannungsstatus  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Temperaturstatus  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Laststatus  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Wenn mehrere Fehlerbedingungen vorliegen, ist der **Statuswert** die **Summe** der entsprechenden Bitwerte.  
> Beispiel: Über-/Unterspannung und Übertemperatur → Status = 4 + 1 = **5**.

---

### 3.3 Entlastungsbedingungen

**Entlastungsbedingungen: 0 = deaktiviert, 1 = aktiviert**  
(„Unload" = das Drehmoment wird als Schutz abgeschaltet.)

**Bits / Gewicht: Beschreibung**

- **BIT0 (1)**: Spannungsschutz  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Übertemperaturschutz  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Überlastschutz  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Wenn mehrere Bits gesetzt sind, ist der **Entlastungsbedingungswert** die **Summe** der Bitwerte.  
> Beispiel: Spannungsschutz + Übertemperaturschutz aktiviert → Entlastungswert = 4 + 1 = **5**.

---

### 3.4 LED-Alarmbedingungen

**LED-Alarmbedingungen: 0 = aus, 1 = ein**

**Bits / Gewicht: Beschreibung**

- **BIT0 (1)**: Spannungsalarm  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Übertemperaturalarm  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Überlastalarm  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Wenn mehrere Bits gesetzt sind, ist der **LED-Alarmbedingungswert** die **Summe** der Bitwerte.  
> Beispiel: Spannungsalarm + Übertemperaturalarm aktiviert → Alarmwert = 4 + 1 = **5**.
