[English](../en/scs_servo_protocol.md) | [Deutsch](../de/scs_servo_protocol.md) | Español | [Français](../fr/scs_servo_protocol.md) | [Italiano](../it/scs_servo_protocol.md) | [日本語](../ja/scs_servo_protocol.md) | [한국어](../ko/scs_servo_protocol.md) | [Português (BR)](../pt-br/scs_servo_protocol.md) | [Português (PT)](../pt-pt/scs_servo_protocol.md) | [简体中文](../zh-hans/scs_servo_protocol.md) | [繁體中文](../zh-hant/scs_servo_protocol.md)

# Servo SCSCL con potenciómetro – Descripción de la tabla de memoria

## Tabla de contenidos

- [Servo SCSCL con potenciómetro – Descripción de la tabla de memoria](#servo-scscl-con-potenciómetro--descripción-de-la-tabla-de-memoria)
- [1. Protocolo de comunicación del servo](#1-protocolo-de-comunicación-del-servo)
- [2. Definición de la tabla de memoria del servo](#2-definición-de-la-tabla-de-memoria-del-servo)
  - [2.1 Información de versión](#21-información-de-versión)
  - [2.2 Configuración EPROM](#22-configuración-eprom)
  - [2.3 Control SRAM](#23-control-sram)
  - [2.4 Realimentación SRAM](#24-realimentación-sram)
  - [2.5 Parámetros de fábrica](#25-parámetros-de-fábrica)
- [3. Descripción de bytes especiales](#3-descripción-de-bytes-especiales)
  - [3.1 Fase del servo](#31-fase-del-servo)
  - [3.2 Estado del servo](#32-estado-del-servo)
  - [3.3 Condiciones de descarga](#33-condiciones-de-descarga)
  - [3.4 Condiciones de alarma del LED](#34-condiciones-de-alarma-del-led)

---

## 1. Protocolo de comunicación del servo

El servo usa el **protocolo personalizado FT-SCS**.  

- Velocidad en baudios por defecto: **1 Mbps o 500 kbps**
- Capa física: **bus único TTL**
- Bits de datos: **8**
- Paridad: **ninguna**
- Bits de parada: **1**
- Rango de baudios configurable: **38 400 ~ 1 Mbps (500 k)**
- Dirección de comunicación (ID) por defecto: **1**

Referencia del protocolo:  
[Protocolo personalizado FT-SCS](http://doc.feetech.cn/#/tiaozhunlujingft?srcType=FT-SCS-Protocol-41ad23fe8a244712ba160b93)

---

## 2. Definición de la tabla de memoria del servo

> Si una dirección de función usa un valor de 2 bytes, el **byte alto** se guarda en la **dirección inferior** y el **byte bajo** en la **dirección superior** (big-endian dentro de la tabla).

---

### 2.1 Información de versión

| Address DEC | Address HEX | Nombre de función       | Bytes | Default | Access | Range | Unit | Descripción                            |
|-------------|-------------|-------------------------|-------|---------|--------|-------|------|----------------------------------------|
| 0           | 0x00        | Versión principal del firmware | 1     | –       | R      |       |      |                                        |
| 1           | 0x01        | Versión secundaria del firmware | 1     | –       | R      |       |      |                                        |
| 2           | 0x02        | END                     | 1     | 1       | R      |       |      | `1` indica almacenamiento big-endian   |
| 3           | 0x03        | Versión principal del servo | 1     | –       | R      |       |      |                                        |
| 4           | 0x04        | Versión secundaria del servo | 1     | –       | R      |       |      |                                        |

---

### 2.2 Configuración EPROM

| Address DEC | Address HEX | Nombre de función            | Bytes | Default | Access | Range       | Unit  | Descripción                                                                                                                                         |
|-------------|-------------|-------------------------------|-------|---------|--------|-------------|-------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 5           | 0x05        | ID del servo                  | 1     | 1       | R/W   | 0 ~ 253     | ID    | ID principal única en el bus                                                                                                                        |
| 6           | 0x06        | Velocidad en baudios          | 1     | 0       | R/W   | 0 ~ 7       | –     | 0–7 representan la velocidad en baudios: 1000000(0), 500000(1), 250000(2), 128000(3), 115200(4), 76800(5), 57600(6), 38400(7)                        |
| 7           | 0x07        | Sin definir                   | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 8           | 0x08        | Nivel de retorno de estado    | 1     | 1       | R/W   | 0 ~ 1       | –     | 0: solo READ y PING devuelven estado; 1: todos los comandos devuelven paquetes de estado                                                             |
| 9           | 0x09        | Límite de ángulo mínimo       | 2     | 20      | R/W   | 0 ~ 1023    | steps | Ángulo de funcionamiento mínimo; debe ser menor que el ángulo máximo. Si **min angle = max angle = 0** → modo motor (rotación continua)             |
| 11          | 0x0B        | Límite de ángulo máximo       | 2     | 1003    | R/W   | 1 ~ 1023    | steps | Ángulo de funcionamiento máximo; debe ser mayor que el ángulo mínimo. Si **min angle = max angle = 0** → modo motor                                 |
| 13          | 0x0D        | Límite de temperatura máxima  | 1     | 70      | R/W   | 0 ~ 100     | °C    |                                                                                                                                                     |
| 14          | 0x0E        | Voltaje de entrada máximo     | 1     | –       | R/W   | 0 ~ 254     | 0.1 V | Si **max input voltage = min input voltage = 0**, la realimentación de voltaje está deshabilitada                                                   |
| 15          | 0x0F        | Voltaje de entrada mínimo     | 1     | 40      | R/W   | 0 ~ 254     | 0.1 V | Si **max input voltage = min input voltage = 0**, la realimentación de voltaje está deshabilitada                                                   |
| 16          | 0x10        | Par máximo                    | 2     | 1000    | R/W   | 0 ~ 1000    | 0.1%  | Al arrancar, este valor se copia a la dirección 48 (límite de par)                                                                                  |
| 18          | 0x12        | Fase                          | 1     | –       | R/W   | 0 ~ 254     | –     | Byte de función especial; no modificar salvo necesidad concreta                                                                                     |
| 19          | 0x13        | Condiciones de descarga       | 1     | –       | R/W   | 0 ~ 254     | –     | Cada bit habilita/deshabilita una protección correspondiente (ver [3.3](#33-condiciones-de-descarga))                                             |
| 20          | 0x14        | Condiciones de alarma del LED | 1     | –       | R/W   | 0 ~ 254     | –     | Cada bit habilita/deshabilita el parpadeo del LED para una alarma dada (ver [3.4](#34-condiciones-de-alarma-del-led))                              |
| 21          | 0x15        | Ganancia P del bucle de posición | 1  | –       | R/W   | 0 ~ 254     | –     | Ganancia proporcional para el control de posición                                                                                                   |
| 22          | 0x16        | Ganancia D del bucle de posición | 1  | –       | R/W   | 0 ~ 254     | –     | Ganancia derivativa para el control de posición                                                                                                     |
| 23          | 0x17        | Sin definir                   | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 24          | 0x18        | Par mínimo de arranque        | 1     | –       | R/W   | 0 ~ 254     | 0.1%  | Salida de par mínima necesaria para iniciar el movimiento                                                                                           |
| 25          | 0x19        | Sin definir                   | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 26          | 0x1A        | Banda muerta directa          | 1     | 1       | R/W   | 0 ~ 16      | steps | La unidad más pequeña es un ángulo de resolución mínimo                                                                                             |
| 27          | 0x1B        | Banda muerta inversa          | 1     | 1       | R/W   | 0 ~ 16      | steps | La unidad más pequeña es un ángulo de resolución mínimo                                                                                             |
| 28 ~ 36     | 0x1C ~ 0x24 | Sin definir                   | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 37          | 0x25        | Par de retención              | 1     | 20      | R/W   | 0 ~ 254     | 1%    | Salida de par tras dispararse la protección de sobrecarga; p. ej. 20 = 20% del par máximo                                                          |
| 38          | 0x26        | Tiempo de protección          | 1     | 200     | R/W   | 0 ~ 254     | 10 ms | Tiempo que la carga supera el par de sobrecarga antes de que se dispare la protección; 200 = 2 s, máx. ≈ 2.5 s                                      |
| 39          | 0x24        | Par de sobrecarga             | 1     | 80      | R/W   | 0 ~ 254     | 1%    | Par umbral para iniciar el temporizador de protección de sobrecarga; 80 = 80% del par máximo                                                        |

---

### 2.3 Control SRAM

| Address DEC | Address HEX | Nombre de función | Bytes | Default | Access | Range                | Unit   | Descripción                                                                                                                                                            |
|-------------|-------------|-----------------|-------|---------|--------|----------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 40          | 0x28        | Interruptor de par | 1  | 0       | R/W   | 0 ~ 2                | –      | 0: par desactivado / libre; 1: par activado; 2: modo amortiguación                                                                                                     |
| 41          | 0x29        | Sin definir     | 1     | –       | R/W   | –                    | –      | –                                                                                                                                                                      |
| 42          | 0x2A        | Posición objetivo | 2    | 0       | R/W   | 0 ~ 1023             | steps  | Cada paso es un ángulo de resolución mínimo; control de posición absoluta. El valor máximo corresponde al ángulo efectivo máximo                                        |
| 44          | 0x2C        | Tiempo de recorrido | 2  | 0       | R/W   | 0 ~ 9999 / -1000~1000| 1 ms / 0.1% | Tiempo desde la posición actual hasta la posición objetivo cuando **run speed = 0**. En modo motor, esto fija el ciclo de trabajo (duty) de la salida PWM; el bit 10 es el bit de dirección |
| 46          | 0x2E        | Velocidad de recorrido | 2 | Factory default max speed | R/W | 0 ~ 1000        | steps/s| Pasos por segundo (velocidad de movimiento)                                                                                                                            |
| 48          | 0x30        | Indicador de bloqueo | 1  | 1       | R/W   | 0 ~ 1                | –      | 0: desbloquea la escritura en EPROM, los valores escritos en direcciones EPROM se almacenan tras apagar; 1: bloquea la escritura en EPROM, los valores escritos en direcciones EPROM **no** se almacenan        |
| 49 ~ 56     | 0x32~0x36   | Sin definir     | 1     |         |        |                      |        | –                                                                                                                                                                      |

---

### 2.4 Realimentación SRAM

| Address DEC | Address HEX | Nombre de función | Bytes | Default | Access | Range | Unit   | Descripción                                                                                                                                                        |
|-------------|-------------|-------------------|-------|---------|--------|-------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 56          | 0x38        | Posición actual   | 2     | –       | R      | –     | steps  | Posición actual en pasos; cada paso es un ángulo de resolución mínimo. Modo de posición absoluta; el valor máximo corresponde al ángulo efectivo máximo             |
| 58          | 0x3A        | Velocidad actual  | 2     | –       | R      | –     | steps/s| Velocidad actual del motor en pasos por segundo                                                                                                                    |
| 60          | 0x3C        | Carga actual      | 2     | –       | R      | –     | 0.1%   | Ciclo de trabajo de la salida de control actual que acciona el motor; el bit 10 es el bit de dirección                                                             |
| 62          | 0x3E        | Voltaje actual    | 1     | –       | R      | –     | 0.1 V  | Voltaje de alimentación actual del servo                                                                                                                           |
| 63          | 0x3F        | Temperatura actual | 1    | –       | R      | –     | °C     | Temperatura interna actual del servo                                                                                                                               |
| 64          | 0x40        | Indicador de escritura asíncrona | 1 | 0    | R      | –     | –      | Indicador usado cuando se emplean comandos de escritura asíncrona                                                                                                 |
| 65          | 0x41        | Estado del servo  | 1     | 0       | R      | –     | –      | Los bits puestos a 1 indican el/los error(es) correspondiente(s) (ver [3.2](#32-estado-del-servo))                                                                |
| 66          | 0x42        | Indicador de movimiento | 1  | 0       | R      | –     | –      | 1 mientras el servo se mueve; 0 cuando ha alcanzado el objetivo y se ha detenido; permanece 0 si no se da una nueva posición objetivo                             |

---

### 2.5 Parámetros de fábrica

| Address DEC | Address HEX | Nombre de función            | Bytes | Default | Access | Range | Unit | Descripción |
|-------------|-------------|--------------------------------|-------|---------|--------|-------|------|-------------|
| 78          | 0x4E        | Paso máximo en modo PWM        | 1     | 20      | R      | –     | –    | –           |
| 79          | 0x50        | Umbral de velocidad de movimiento × 50 | 1 | 1  | R      | –     | –    | –           |
| 80          | 0x51        | DTs (ms)                      | 1     | 20      | R      | –     | –    | –           |
| 81          | 0x52        | Límite de velocidad mínima × 50 | 1   | 1       | R      | –     | –    | –           |
| 82          | 0x53        | Límite de velocidad máxima × 50 | 1   | –       | R      | –     | –    | –           |
| 83          | 0x54        | Aceleración                   | 1     | 20      | R      | –     | –    | –           |

---

## 3. Descripción de bytes especiales

---

### 3.1 Fase del servo

**Bits / peso: descripción**

- **BIT0 (1)**: Fase de la dirección de accionamiento  
  - 0: dirección normal  
  - 1: dirección invertida
- **BIT1 (2)**: –––
- **BIT2 (4)**: –––
- **BIT3 (8)**: Modo velocidad  
  - 0: velocidad = 0 significa parada  
  - 1: velocidad = 0 significa velocidad máxima
- **BIT4 (16)**: –––
- **BIT5 (32)**: Fase PWM  
  - 0: en fase  
  - 1: invertida
- **BIT6 (64)**: Modo voltaje  
  - 0: detección de baja tensión de 1.5 k  
  - 1: detección de alta tensión de 1 k
- **BIT7 (128)**: –––

> Si se ponen varios bits a la vez, el **valor de fase** es la **suma** de los valores de todos los bits puestos.

---

### 3.2 Estado del servo

**Estado del servo: 0 = normal, 1 = fallo**

**Bits / peso: descripción**

- **BIT0 (1)**: Estado de voltaje  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Estado de temperatura  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Estado de carga  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Si hay varias condiciones de fallo presentes, el **valor de estado** es la **suma** de los valores de bit correspondientes.  
> Ejemplo: sobretensión/subtensión y sobretemperatura → estado = 4 + 1 = **5**.

---

### 3.3 Condiciones de descarga

**Condiciones de descarga: 0 = deshabilitado, 1 = habilitado**  
("Descarga" = el par se desactiva como protección.)

**Bits / peso: descripción**

- **BIT0 (1)**: Protección de voltaje  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Protección de sobretemperatura  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Protección de sobrecarga  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Si se ponen varios bits, el **valor de condición de descarga** es la **suma** de los valores de bit.  
> Ejemplo: protección de voltaje + protección de sobretemperatura habilitadas → valor de descarga = 4 + 1 = **5**.

---

### 3.4 Condiciones de alarma del LED

**Condiciones de alarma del LED: 0 = apagada, 1 = encendida**

**Bits / peso: descripción**

- **BIT0 (1)**: Alarma de voltaje  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Alarma de sobretemperatura  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Alarma de sobrecarga  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Si se ponen varios bits, el **valor de condición de alarma del LED** es la **suma** de los valores de bit.  
> Ejemplo: alarma de voltaje + alarma de sobretemperatura habilitadas → valor de alarma = 4 + 1 = **5**.
