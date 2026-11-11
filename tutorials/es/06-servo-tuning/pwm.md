---
title: "Protocolo, comandos y calibración de los servos PWM"
description: "Versión PWM de AmazingHand: gestos compatibles, calibración del firmware, protocolo serie, referencia de comandos, ajuste fino de parámetros de gestos y preguntas frecuentes."
version: pwm
---

# Protocolo, comandos y calibración de los servos PWM

Esta página cubre el protocolo serie, los comandos, la calibración y el ajuste fino de parámetros del firmware PWM. Para el cableado, consulta [Cableado PWM](../01-hardware/pwm.md); para el flasheo, [Inicio rápido PWM](../02-quick-start/pwm.md); para el control de escritorio/web, [Aplicación de escritorio PWM](../04-desktop/pwm.md) / [Control web PWM](../03-web-control/pwm.md).

> Los siguientes comandos se ejecutan en el directorio `AmazingHand-PWM/` del repositorio. Código fuente del firmware: [`firmware/AmazingHand_Serial/`](../../../AmazingHand-PWM/firmware/AmazingHand_Serial/).

## 1. Resumen de comandos y gestos

Las primeras 11 filas son comandos de gestos; las demás son comandos de control directo, selección de lado, repetición, parada y prueba de enlace.

| Gesto/comando | Comando | Descripción |
|------|------|------|
| Piedra | 0x01 | Piedra-papel-tijera: todos los dedos cerrados |
| Tijera | 0x02 | Piedra-papel-tijera: índice + medio extendidos en V |
| Papel | 0x03 | Piedra-papel-tijera: todos los dedos abiertos |
| Pulgar arriba | 0x04 | Pulgar levantado, el resto cerrado |
| Burla 1 | 0x05 | Agitar el índice («no, no, no») |
| Burla 2 | 0x06 | Anular extendido y oscilando (sustituye al meñique) |
| Abrir | 0x07 | Todos los dedos abiertos |
| Puño | 0x08 | Todos los dedos cerrados |
| OK | 0x09 | Gesto OK |
| Pellizcar | 0x0A | Gesto de pellizco |
| Señalar | 0x0C | Índice extendido haciendo el gesto de «señalar» |
| Control directo | 0xF0 | Controlar directamente el ángulo de los 8 servos |
| Seleccionar mano | 0xF1 | Cambiar entre modo mano izquierda/derecha |
| Repetir | 0xFE | Repetir el último gesto |
| Detener | 0xFF | Terminar inmediatamente el gesto actual |
| NOP | 0x00 | Prueba de enlace |

> Nota: el comando 0x0B está desactivado (el antiguo «pulgar abajo» se solapaba con el gesto «pulgar arriba» y se eliminó).

---

## 2. Calibración del firmware (opcional, recomendada la primera vez)

La posición central y la anchura de pulso de los servos deben calibrarse según el mecanismo real; se pueden modificar directamente en el código fuente del firmware:

- Edita `middle_pos[8]` y `min_pw/mid_pw/max_pw[8]` al principio de `components/hand_servo/hand_servo.c`.

Tras la calibración hay que volver a compilar y flashear.

---

## 3. Protocolo de comunicación serie

### 3.1 Capa física

| Parámetro | Valor |
|------|-----|
| Interfaz | USB Serial (UART0) |
| Velocidad en baudios | **115200** |
| Bits de datos | 8 |
| Bit de paridad | Ninguno (None) |
| Bits de parada | 1 |
| Control de flujo | Ninguno |

### 3.2 Formato de trama

#### PC → ESP32 (trama de comando)

```
┌────────┬────────┬──────────┬────────────────┬──────────┐
│  0xAA  │ CMD_ID │ DATA_LEN │ DATA[0 .. N-1] │ CHECKSUM │
│ 1 Byte │ 1 Byte │  1 Byte  │    N Bytes     │  1 Byte  │
└────────┴────────┴──────────┴────────────────┴──────────┘
 帧头      命令ID    数据长度      数据负载         校验和
```

- **Cabecera de trama**: fija `0xAA`, marca el inicio de una trama
- **CMD_ID**: número de comando (ver [Referencia de comandos](#4-referencia-de-comandos))
- **DATA_LEN**: número de bytes de la carga útil de datos (0-8; las tramas con más de 8 no son válidas)
- **DATA**: carga útil de datos; la longitud la determina DATA_LEN
- **CHECKSUM**: `CMD_ID ^ DATA_LEN ^ DATA[0] ^ ... ^ DATA[N-1]` (verificación XOR)

> Si DATA_LEN = 0, entonces CHECKSUM = CMD_ID.

#### ESP32 → PC (trama de respuesta)

```
┌────────┬────────┬────────┬──────────┐
│  0xBB  │ CMD_ID │ STATUS │ CHECKSUM │
│ 1 Byte │ 1 Byte │ 1 Byte │  1 Byte  │
└────────┴────────┴────────┴──────────┘
 帧头      命令ID    状态码    校验和
```

- **Cabecera de trama**: fija `0xBB`
- **CMD_ID**: número de comando original
- **STATUS**: código de estado (ver la tabla siguiente)
- **CHECKSUM**: `CMD_ID ^ STATUS`

#### Códigos de estado

| STATUS | Significado | Descripción |
|--------|------|------|
| 0x00 | OK | Comando aceptado; empieza la ejecución |
| 0x01 | Comando no válido | CMD_ID no está en la tabla de comandos |
| 0x02 | Error de parámetro | Longitud o contenido de datos incorrectos |
| 0x03 | Ocupado | Gesto en ejecución; no se aceptan comandos nuevos por ahora |
| 0x10 | Completado | Gesto terminado |

### 3.3 Secuencia de comunicación

```
主机                          ESP32
 │                              │
 │──── [AA 01 00 01] ────────→│  发送"石头"命令
 │                              │
 │←─── [BB 01 00 01] ─────────│  ACK: 命令已接受
 │                              │
 │                      (执行手势中)
 │                              │
 │←─── [BB 01 10 11] ─────────│  完成: 手势执行完毕
 │                              │
 │──── [AA 02 00 02] ────────→│  发送"剪刀"命令
 │                              │
 │←─── [BB 02 00 02] ─────────│  ACK
 │                              │
```

### 3.4 Detener gesto y tiempo de espera de trama

- Enviar `[AA FF 00 FF]` interrumpe en cualquier momento el gesto en ejecución
- Si el ESP32 no recibe una trama completa en 200 ms, la descarta automáticamente (para evitar una desincronización permanente por pérdida de bytes)
- Las tramas con suma de verificación incorrecta se descartan silenciosamente; el software de PC debe implementar reenvío con tiempo de espera

### 3.5 Modo mano izquierda/derecha

Por defecto, modo mano derecha. Envía `[AA F1 01 02 F2]` para cambiar a la mano izquierda y `[AA F1 01 01 F1]` para volver a la mano derecha. La mano izquierda/derecha afecta a la dirección de movimiento del pulgar (gestos con pulgar como piedra/tijera/pulgar arriba/OK/pellizcar).

---

## 4. Referencia de comandos

### 4.1 Comandos de gestos (0x01–0x0A, 0x0C)

Estos comandos no necesitan carga útil de datos (DATA_LEN=0); el ESP32 ejecuta el gesto correspondiente en cuanto los recibe.

| Comando | Trama HEX | Respuesta | Descripción |
|------|--------|------|------|
| Piedra | `AA 01 00 01` | `BB 01 00 01` → `BB 01 10 11` | Todos los dedos cerrados |
| Tijera | `AA 02 00 02` | `BB 02 00 02` → `BB 02 10 12` | Índice + medio extendidos |
| Papel | `AA 03 00 03` | `BB 03 00 03` → `BB 03 10 13` | Todos los dedos abiertos |
| Pulgar arriba | `AA 04 00 04` | `BB 04 00 04` → `BB 04 10 14` | Pulgar levantado |
| Burla 1 | `AA 05 00 05` | `BB 05 00 05` → `BB 05 10 15` | Agitar el índice (unos 2,5 s) |
| Burla 2 | `AA 06 00 06` | `BB 06 00 06` → `BB 06 10 16` | Anular oscilando (unos 2,5 s) |
| Abrir | `AA 07 00 07` | `BB 07 00 07` → `BB 07 10 17` | Todos los dedos abiertos |
| Puño | `AA 08 00 08` | `BB 08 00 08` → `BB 08 10 18` | Todos los dedos cerrados |
| OK | `AA 09 00 09` | `BB 09 00 09` → `BB 09 10 19` | Gesto OK |
| Pellizcar | `AA 0A 00 0A` | `BB 0A 00 0A` → `BB 0A 10 1A` | Gesto de pellizco |
| Señalar | `AA 0C 00 0C` | `BB 0C 00 0C` → `BB 0C 10 1C` | Índice extendido haciendo el gesto de «señalar» |

### 4.2 Comando de control directo (0xF0)

Controla directamente el ángulo de los 8 servos; los 8 bytes de datos corresponden a los servos 1-8 y cada byte va de 0 a 180.

**Ejemplo: todos los servos a la posición central (90°)**

```
发送: AA F0 08 5A 5A 5A 5A 5A 5A 5A 5A F8
       │  │  │  └── 8 个 0x5A (90°) ──┘  │
       │  │  │                            └── CHECKSUM
       │  │  └── DATA_LEN = 8
       │  └── CMD_DIRECT_DRIVE
       └── 帧头
```

Suma de verificación = `F0 ^ 08 ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A` = `F8`

> Los 8 bytes 0x5A iguales se anulan por pares con XOR y dan 0x00; al final `0xF0 ^ 0x08 ^ 0x00 = 0xF8`

**Ejemplo: índice abierto (servo 1=170°, servo 2=10°), el resto centrado (90°)**

```
发送: AA F0 08 AA 0A 5A 5A 5A 5A 5A 5A 58
               └─170°  └─10°
```

### 4.3 Seleccionar mano (0xF1)

1 byte de datos: `0x01` = mano derecha, `0x02` = mano izquierda.

```
设右手: AA F1 01 01 F1
设左手: AA F1 01 02 F2
```

### 4.4 Comandos de control

| Comando | Trama HEX | Descripción |
|------|--------|------|
| NOP | `AA 00 00 00` | Prueba de enlace; responde inmediatamente `BB 00 00 00` |
| Repetir | `AA FE 00 FE` | Repite el último gesto |
| Detener | `AA FF 00 FF` | Termina inmediatamente el gesto actual |

### 4.5 Resumen de respuestas

Al recibir un comando no válido (por ejemplo, el comando inexistente 0xFC):

```
发送: AA FC 00 FC
响应: BB FC 01 FD    （STATUS=0x01 无效命令）
```

> Verificación de la suma: `FC ^ 00 = FC`, respuesta `FC ^ 01 = FD`

---

## 5. Ajuste fino de los parámetros de gestos

### 5.1 Ubicación de los parámetros

El desfase angular de cada gesto se define con macros `#define`; **no hace falta cambiar el código lógico**, solo los valores.

- **Versión ESP-IDF**: zona «parámetros de gestos (ajustables por el usuario)» al principio de `components/hand_gestures/hand_gestures.c`

### 5.2 Significado de los parámetros

```c
// Ejemplo: gesto de piedra
#define ROCK_IDX_OFF1    70    // desfase de la articulación 1 del índice
#define ROCK_IDX_OFF2   -70    // desfase de la articulación 2 del índice
```

- **Valor positivo = flexión/cierre**, **valor negativo = extensión/apertura**
- Cada dedo tiene 2 desfases, relativos a `middle_pos` (90° por defecto)
- Estructura diferencial: dos servos uno al lado del otro con ejes colineales; el giro en el mismo sentido produce splay lateral y el giro en sentidos opuestos produce flexión; la suma de los dos ángulos de desfase corresponde al splay y la diferencia a la flexión.

### 5.3 Pasos de ajuste

1. Localiza la macro `#define` del gesto correspondiente
2. Modifica el valor (aumentar → mayor amplitud; reducir → menor amplitud)
3. Vuelve a compilar y flashear, y prueba el resultado con la aplicación de escritorio
4. Ajusta repetidamente hasta que el movimiento sea natural

---

## 6. Preguntas frecuentes

### P1: ¿La aplicación de escritorio no puede conectarse al puerto serie?

1. Confirma que el ESP32 está conectado al PC por Type-C
2. Comprueba que el número de COM del Administrador de dispositivos coincida con el seleccionado en la GUI
3. Confirma la velocidad de 115200
4. Desconecta otros programas que ocupen el puerto serie

### P2: ¿No hay respuesta al enviar comandos?

1. Envía primero `AA 00 00 00` (NOP); deberías recibir `BB 00 00 00`
2. Confirma que el firmware está flasheado y que el chip destino es ESP32-S3
3. Comprueba el cableado (¿GND comparte masa?)

### P3: ¿La amplitud del gesto no es correcta o la dirección está invertida?

Entra en el ajuste fino de parámetros de gestos (ver [sección 5](#5-ajuste-fino-de-los-parámetros-de-gestos)) y ajusta la macro correspondiente.

### P4: ¿Qué gestos afecta el modo mano izquierda/derecha?

Los gestos **con pulgar** como piedra/tijera/pulgar arriba/OK/pellizcar; tras cambiar de mano, la dirección del espejo del pulgar cambia.

### P5: ¿Los dedos se atascan y no se extienden?

Todos los gestos de contracción despliegan primero toda la mano y luego la cierran automáticamente, para evitar que los dedos queden bloqueados por el gesto anterior. Si aun así se atascan, revisa el montaje mecánico o reduce la amplitud de contracción.

## Páginas relacionadas

- [Cableado, GPIO y alimentación PWM](../01-hardware/pwm.md)
- [Inicio rápido PWM](../02-quick-start/pwm.md)
- [Aplicación de escritorio PWM](../04-desktop/pwm.md)
- [Seguimiento de manos PWM](../05-hand-tracking/pwm.md)
- [FAQ](../08-faq/faq.md)
