[English](../en/CHANGES.md) | [Deutsch](../de/CHANGES.md) | Español | [Français](../fr/CHANGES.md) | [Italiano](../it/CHANGES.md) | [日本語](../ja/CHANGES.md) | [한국어](../ko/CHANGES.md) | [Português (BR)](../pt-br/CHANGES.md) | [Português (PT)](../pt-pt/CHANGES.md) | [简体中文](../zh-hans/CHANGES.md) | [繁體中文](../zh-hant/CHANGES.md)

# AmazingHand Controller · Registro de cambios y justificación

Qué se cambió respecto al proyecto original, por qué, y cuál es el resultado real.

Proyecto original: `Betatester777/AmazingHandControl` (GUI de Python + CLI para el AmazingHand)
Hardware: JuxiTechnology AmazingHand (8× servos Feetech SCS0009, realimentación por potenciómetro) — **compatibles ambas manos**, se selecciona al arrancar

---

## Contenido

1. [Recalibración del sistema de ángulos](#1-recalibración-del-sistema-de-ángulos)
2. [Botones globales: llevar a posiciones raw exactas](#2-botones-globales-llevar-a-posiciones-raw-exactas)
3. [Nuevo botón de posición media](#3-nuevo-botón-de-posición-media)
4. [La GUI y la CLI no coinciden (el error central)](#4-la-gui-y-la-cli-no-coinciden-el-error-central)
5. [Correcciones de los datos de poses](#5-correcciones-de-los-datos-de-poses)
6. [Reproductor de secuencias: temporización y diagnóstico](#6-reproductor-de-secuencias-temporización-y-diagnóstico)
7. [Nueva fila de posición raw en la realimentación de servos](#7-nueva-fila-de-posición-raw-en-la-realimentación-de-servos)
8. [**Compatibilidad con mano izquierda y derecha**](#8-compatibilidad-con-mano-izquierda-y-derecha)
9. [Detección automática del puerto serie](#9-detección-automática-del-puerto-serie)
10. [Referencia de configuración](#10-referencia-de-configuración)
11. [Resultados medidos](#11-resultados-medidos)
12. [Resumen archivo por archivo](#12-resumen-archivo-por-archivo)

---

## 1. Recalibración del sistema de ángulos

### 1.1 Límites de ángulo: `0..110` → `-75..75`

El original estaba calibrado como `0° = abierto, 110° = cerrado`. El recorrido real de esta mano cae dentro de `-75..75`, así que se recalibró todo.

**`data/config.yaml`**

| Clave | Antes | Después |
|---|---|---|
| `servo_min` / `servo_max` | -40 / 110 | **-75 / 75** |
| `base_min` / `base_max` | 0 / 110 | **-75 / 75** |
| `side_min` / `side_max` | -40 / 40 | **-35 / 35** |
| `left_open` | `[32, -40]` | **`[32, -35]`** |
| `right_open` | `[-40, 32]` | **`[-35, 32]`** |
| `left_closed` / `right_closed` | `[110, 110]` | **`[75, 75]`** |
| `center_closed` | `[110, 110]` | **`[75, 75]`** |

**Las 19 poses se reescalaron**, p. ej. `open` de `[0]*8` a `[-35]*8`, `close` de `[110]*8` a `[75]*8`.

### 1.2 Apertura lateral: `±40°` → `±35°`

El deslizador lateral se normaliza con `u = |side_offset| / |side_min|`, así que cambiar solo el límite **no** cambia cuánto se abren realmente los dedos — solo reescala el deslizador. Para cambiar la apertura física también hay que cambiar `auto_extremes`. Con ambos cambiados:

| | Antes (±40) | Después (±35) |
|---|---|---|
| Rango del deslizador | −40 … +40 | −35 … +35 |
| Totalmente abierto, en el extremo lateral | `(32, -40)`, apertura **72°** | `(32, -35)`, apertura **67°** |

### 1.3 Coincidencia con la referencia del fabricante

El demo de Arduino del fabricante (`Amazing_RHand_Demo.ino`) convierte así:

```c
float Step = 0.293; // 300°/1024
sc.RegWritePos(1, MiddlePos[0] + Pos_1 / Step, 0, Speed);
```

Y rustypot 1.4.2 (`src/servo/feetech/scs0009.rs`):

```rust
fn to_raw(value: f64) -> i16 {
    let a = (1024.0 * value / (300.0_f64.to_radians()) + 511.0) as i16;
    a.to_be()
}
```

**Conclusión: ambos lados usan la misma escala de grados** (0.29297°/paso, 300° de escala completa, raw 0–1023) — no hay error de proporción. La única diferencia sistemática es el punto cero:

- rustypot siempre centra en raw **511**
- el firmware del fabricante usa un valor de calibración por servo, `MiddlePos = {451, 571, 451, 571, 451, 571, 451, 571}`

Difieren en **±60 raw = ±17.6°**. Eso es exactamente lo que aborda el botón «Middle position» de más abajo.

---

## 2. Botones globales: llevar a posiciones raw exactas

### 2.1 El problema

Los `open_all()` / `close_all()` originales tenían ángulos codificados a mano:

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

Esos valores proceden de la **escala de calibración antigua** (0 = abierto, 110 = cerrado). Tras recalibrar a `-35 / 75`:

- `open_all` fijaba 0° → convertido a raw **511**, es decir, aproximadamente el centro mecánico — los dedos nunca se abrían
- `close_all` fijaba 110° → recortado por `base_max = 75`, de modo que solo llegaba a 75, mientras la etiqueta seguía mostrando 110°

### 2.2 La solución: una ruta directa a la posición raw

La ruta de ángulos pasa por el modelo de interpolación `base/side`, que no puede alcanzar con exactitud un valor raw arbitrario (ver la sección 4). Por eso los botones globales recibieron una ruta que escribe directamente posiciones de servo raw.

**Un detalle de implementación importante:** esto *no* usa `sync_write_raw_goal_position` de rustypot. Al leer el código generado por macros se ve que la API raw escribe `values.to_le_bytes()` directamente en el bus, mientras que la API que convierte aplica antes `to_be()`:

```rust
fn to_raw(value: f64) -> i16 { let a = (...) as i16; a.to_be() }
// sync_write_raw_*: values.iter().map(|v| v.to_le_bytes())   <- no to_be
```

Por tanto, pasar `451` emitiría `0xC301` (49921). En su lugar, el código usa `sync_write_goal_position` (radianes) y despeja los radianes que caen **exactamente** en el valor raw objetivo, tomando el punto medio de cada paso raw para evitar el error de truncamiento.

### 2.3 Objetivos raw de los tres botones

Se añadió `raw_positions` a `data/config.yaml` (índice 0 → ID de servo 1):

```yaml
raw_positions:
  open:   [260, 760, 260, 760, 260, 760, 260, 760]
  close:  [760, 260, 760, 260, 760, 260, 760, 260]
  middle: [451, 571, 451, 571, 451, 571, 451, 571]
```

| Botón | Acción | IDs de servo 1–8 raw |
|---|---|---|
| ✋ Abrir todo | totalmente extendido | 260, 760, 260, 760, 260, 760, 260, 760 |
| ✊ Cerrar todo | totalmente cerrado | 760, 260, 760, 260, 760, 260, 760, 260 |
| ⊙ Centrar todo | recentrado lateral (no cambia abrir/cerrar) | — |
| **Posición media** | **volver al centro calibrado** | 451, 571, 451, 571, 451, 571, 451, 571 |

> ⚠️ `raw_positions` son **valores de calibración por mano**. El propio comentario del fabricante es *"replace values by your calibration results"* — vuelve a medir tras cambiar de mano o de servos.

### 2.4 El compromiso de la sincronización con los deslizadores

Los objetivos raw se saltan el modelo `base/side`, por lo que no tienen un equivalente exacto en los deslizadores. Tras ejecutar un botón, los deslizadores se fijan al entero más próximo:

| Posición | El deslizador muestra |
|---|---|
| open | base = −73, side = 0 |
| close | base = +73, side = 0 |
| middle | base = −17, side = 0 |

El coste: tocar un deslizador después desplaza la mano hasta ~1 unidad raw (0.3°) respecto al objetivo. Es deliberado — acertar exactamente la posición calibrada importa más.

---

## 3. Nuevo botón de posición media

Situado a la derecha de `✋ Abrir todo` / `✊ Cerrar todo` / `⊙ Centrar todo`. Devuelve la mano al **centro mecánico calibrado por el fabricante** (raw 451/571).

**Por qué hace falta:** el punto medio entre `open_all` y `close_all` *no* es el centro mecánico. El centro del fabricante es `MiddlePos`, que está a ±60 raw (±17.6°) de raw 511. Tras el encendido quieres un cero bien definido y repetible.

---

## 4. La GUI y la CLI no coinciden (el error central)

### 4.1 Síntoma

**La misma pose produce un movimiento de la mano distinto al aplicarla con `✓ Apply` de la GUI frente a `--pose` de la CLI.**

### 4.2 Causa raíz

La GUI aplicaba las poses a través de:

```
set_positions(p1, p2)  →  decompose into (base, side), stored in the sliders
                       →  get_positions() recomputes via compute_auto_positions() in Auto mode
```

Pero `compute_auto_positions` **no** es la inversa exacta de `decompose_servo_positions` (su centro y sus extremos son valores empíricos). El `apply_pose()` de la CLI envía los valores directamente.

Medido: **12 de 19 poses estaban distorsionadas**, hasta 32°:

| Pose | Almacenada | La GUI enviaba realmente | Desviación |
|---|---|---|---|
| `ring_close` | Anular `(75, -35)` | Anular `(43, -5)` | **32° / 30°** |
| `middle_close` | Medio `(75, -35)` | Medio `(43, -5)` | **32° / 30°** |
| `pointer_close` | Índice `(75, -35)` | Índice `(43, -5)` | **32° / 30°** |
| `thumb_close` | Pulgar `(75, -35)` | Pulgar `(43, -5)` | **32° / 30°** |
| `wave1` | `(-75, -3)` | `(-75, 9)` | 12° |
| `hifive` | Pulgar `(-75, -3)` | Pulgar `(-75, 9)` | 12° |
| `greeting` | Anular `(-18, -57)` | Anular `(-10, -68)` | 8° / 11° |
| `victory` | Medio `(-68, -9)` | Medio `(-75, 1)` | 7° / 10° |
| `paper` | Índice `(-52, -22)` | Índice `(-59, -16)` | 7° / 6° |
| `ok` | Índice `(36, 46)` | Índice `(38, 43)` | 2° / 3° |

**El patrón:** las poses simétricas en las que cada dedo tiene `pos1 == pos2` (`open` `close` `stone` `two` `scissors` `one` `three`) se conservan exactamente en el viaje de ida y vuelta. Todas las poses asimétricas con apertura lateral se desvían.

### 4.3 Solución

Se añadió `_send_exact_positions()`, que envía los ángulos directamente a los servos en el orden de `SERVO_PAIRS` (equivalente al `apply_pose` de la CLI). Ahora ambos puntos de entrada de poses lo usan:

- el botón `✓ Apply` en Gestión de poses
- `_apply_pose_from_config()` — el reproductor de secuencias y la lista de poses

Los deslizadores siguen actualizándose mediante `set_positions()` para mostrarlos, pero **ya no deciden lo que se envía**.

### 4.4 Resultado

Tras la corrección, **las 19 poses cumplen `stored == GUI-sent == CLI-sent`**.

**Efecto secundario:** los gestos reales en la GUI cambian, sobre todo los asimétricos. Ese es el efecto buscado con la corrección.

---

## 5. Correcciones de los datos de poses

### 5.1 Cuatro poses `*_close` estaban mal escritas

```yaml
# Before — target finger (75, -35)
ring_close:    [75, -35, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, -35, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, -35, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, -35]
```

`(75, -35)` se descompone en `base = 20, side = -55` (fuera de rango) — es decir, *"solo un 27% flexionado, girado con fuerza a la izquierda"*, no "cierra este dedo". Igual que en `close` y `one`, la forma correcta es `(75, 75)`:

```yaml
# After — target finger fully closed (75, 75), others stay open (-35, -35)
ring_close:    [75, 75, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, 75, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, 75, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, 75]
```

Verificado por descomposición: el dedo objetivo queda en `base = 75` (totalmente cerrado), `side = 0` (sin desviarse a ningún lado).

**Impacto:** la secuencia `finger_roll`, que usa estas cuatro, solo ahora es un auténtico "gira cada dedo por turno".

### 5.2 El pulgar en `greeting` / `paper`

Ambas tenían originalmente el pulgar en `(75, 75)` (totalmente cerrado). Para `paper` (布, una palma abierta y plana) un pulgar cerrado es claramente incorrecto.

`greeting` se cambió primero a `(-75, -3)` (reutilizando el pulgar abierto de `hifive`), pero las pruebas en hardware mostraron que ese paso necesitaba que el pulgar recorriera **150°**, lo que no cabe en 1.0 s (ver 6.3). Estado final:

```yaml
greeting: [-18, -57, -32, -32, -70, -7, -35, -35]   # thumb (-35, -35), same as open
paper:    [-19, -56, -34, -34, -52, -22, -75, -3]   # keeps the splayed thumb (flat palm)
```

Eso separa los dos gestos: `greeting` es un saludo, donde el pulgar simplemente se abre de forma natural; `paper` es una palma plana, donde el pulgar se abre.

---

## 6. Reproductor de secuencias: temporización y diagnóstico

### 6.1 Corrección de avisos falsos de "no alcanzó el objetivo"

Ejecutar `demo` en hardware produjo tres falsas alarmas:

```
⚠ Pose #42 'greeting': Servos did not reach target! Max error: 52°
```

**Causa raíz:** `_log_pose_completion` restaba dos arrays que estaban en **órdenes distintos**.

- `monitor_servos()` escribe su caché en **orden de ID de servo**: `latest_actual_positions[servo_id - 1] = ...` (índice 0 = ID1 = Índice)
- los `target_positions` que se pasan son un array de pose, en **orden de widgets** Anular / Medio / Índice / Pulgar (índice 0 = Anular = ID5)

Por tanto, restaba la lectura del Índice del objetivo del Anular.

**Evidencia** (recalculando a partir del registro medido):

```
target (widget order)   : [-18, -57, -32, -32, -70, -7, -75, -3]
actual (servo-ID order) : [-68.85, -6.74, -33.69, -31.35, -18.46, -54.79, -74.12, -3.22]
compared as-is          -> max error 52°      <-- what the old code did
target reordered        : [-70, -7, -32, -32, -18, -57, -75, -3]
compared in servo order -> max error 2.21°    <-- actually spot on
```

**Corrección:** se añadieron `pose_to_servo_order()` / `servo_to_pose_order()`, que se aplican antes de comparar; el `current` impreso se convierte de vuelta para que `target` y `current` queden alineados columna a columna en el registro.

### 6.2 Corrección de cuándo se ejecuta la comprobación de alcance

El original comprobaba **2000 ms fijos** después de enviar:

```python
self.root.after(2000, lambda ...: self._log_pose_completion(...))
```

Pero los pasos de secuencia solo esperan 1.0 s, así que para cuando se ejecutaba la comprobación ya se había enviado el paso siguiente — la lectura pertenece necesariamente al movimiento *siguiente*:

```
25.388  Pose #40 'ok'      sent
26.782  Pose #41 'victory' sent        <- already moved on
27.742  Pose #40 'ok'      checked -> reading is mid-way to victory
```

**Corrección:**

1. `_apply_pose_from_config` recibió un parámetro `check_after`. Hacer clic en `✓ Apply` para una pose suelta no cambia (2.0 s, luego espera a que pare el movimiento); la reproducción de secuencias pasa **el propio retardo del paso**, de modo que la comprobación cae en el límite del paso (retardo − 100 ms) y ya no espera al movimiento.
2. Se añadió un **guarda de supersesión**: `_log_pose_start` registra `current_pose_id`; si un comando más reciente ha tomado el relevo, se omite la comprobación de alcance y el registro muestra `current=<superseded>`.

### 6.3 Ajuste de los retardos de secuencia

**Velocidad efectiva** deducida a la inversa del registro de hardware (la velocidad 3 es nominalmente 172°/s):

| Pose | Recorrido | Error a 0.9 s | Velocidad efectiva implícita |
|---|---|---|---|
| `ok` | 110° | 0.5° | 121.7°/s (71% de la nominal) |
| `victory` | 110° | 1.0° | 121.1°/s (70%) |
| `greeting` | 132° | 7.0° | 138.9°/s (81%) |

> Bajo carga, la velocidad real es solo aproximadamente el **70%** de la nominal. Ese es el número que importa al elegir los retardos.

**Cambios en `demo`:**

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

- `greeting` 1.0 s → **1.5 s**: ese paso recorre 132° (el segundo servo del Anular) y no puede terminar en 1.0 s
- **nuevo `close` final**: así `demo` termina con la mano cerrada, lo que además deja el bucle limpio
- duración total 7.0 s → **9.5 s**

### 6.4 `wave`: limitar el balanceo lateral a ±30°

El `wave_r` / `wave_l` original implicaba un `side` de **±36** (más allá del límite de ±35, por lo que se recortaba a 35).

Al despejar `side = base − pos1`, `base = (pos1 + pos2) / 2` se obtiene `pos1 = base − side`, `pos2 = base + side`. Manteniendo `base = −39` y reduciendo `side` a ±30:

```yaml
wave_r: [-9, -69, -9, -69, -9, -69, -69, -9]     # was [-3, -75, -3, -75, -3, -75, -75, -3]
wave_l: [-69, -9, -69, -9, -69, -9, -9, -69]     # was [-75, -3, -75, -3, -75, -3, -3, -75]
```

Verificado: `wave_r` tiene side `[-30, -30, -30, +30]`, y `wave_l` es su espejo por dedo.

**Efecto secundario (esperado):** el recorrido de cada balanceo también baja de 40°/72° a **34°/60°**. La onda es en conjunto más estrecha, lo que solo amplía el margen de temporización.

---

## 7. Nueva fila de posición raw en la realimentación de servos

Justo debajo de `Position (°)` hay una fila **`Current (0-1023)`** que muestra la posición raw del servo en vivo.

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

**Compromiso:** no añade lecturas serie extra. El valor raw se deriva de la posición que el hilo de monitorización **ya** había leído, así que el bucle de sondeo no duplica su tráfico serie. La precisión se verificó de forma exhaustiva: **2048 combinaciones (raw 0–1023 × servo par/impar) van y vuelven sin ningún error**.

**Uso:** compáralo directamente con la calibración del fabricante — `open` debería leer `260 / 760` alternando, `middle` debería leer `451 / 571`.

> El nombre de la fila lleva un prefijo de rango para distinguirla del `Current (mA)` existente (consumo de corriente estimado).

---

## 8. Compatibilidad con mano izquierda y derecha

### 8.1 El fabricante distribuye dos firmwares

El fabricante ofrece un demo de Arduino distinto por mano, con parámetros completamente diferentes:

| | Derecha `Amazing_RHand_Demo` | Izquierda `Amazing_LHand_Demo` |
|---|---|---|
| IDs de servo | **1–8** | **11–18** |
| Dedo → ID | índice `1,2` / medio `3,4` / anular `5,6` / pulgar `7,8` | **anular `11,12` / medio `13,14` / índice `15,16` / pulgar `17,18`** |
| `MiddlePos` central | `[451, 571, 451, 571, …]` | `[571, 451, 571, 451, …]` |

El tutorial de depuración lo dice sin rodeos: *"a single hand uses 8 servos; the right hand's IDs must be set to 1-8, and the left hand's to 11-18."*

Fíjate en que la numeración de la mano izquierda va **al revés** (primero el anular) — coincidiendo con su disposición mecánica reflejada.

### 8.2 Por qué cambiar los IDs no es suficiente

Los IDs son solo la primera capa. Quedan dos diferencias físicas entre las manos, y omitir cualquiera de las dos distorsiona los gestos.

#### Diferencia 1: un desplazamiento de montaje de 35.16°

Ambas manos usan **el mismo valor de gesto más su propio `MiddlePos`**:

```c
// Right
#define MiddlePos {451, 571, ...}
Move_Index(-35, 35)  →  ID1 = 451 + (-35)/0.293 = 331.5

// Left
#define MiddlePos {571, 451, ...}
Move_Index(-35, 35)  →  ID15 = 571 + (-35)/0.293 = 451.5
```

El mismo gesto "abierto" cae en valores raw distintos en cada mano. Convertidos al espacio de ángulos de este programa, difieren en **120 raw = 35.16°**.

#### Diferencia 2: los dos servos de un dedo están intercambiados

```c
// Right Victory                      // Left Victory
Move_Index (-15, 65);                Move_Index (-65, 15);
Move_Middle(-65, 15);                Move_Middle(-15, 65);
```

Por dedo, `(a, b) → (-b, -a)`; en valores de pose eso significa **intercambiar los dos números de cada dedo**.

Si se pasa por alto, **la dirección de apertura se invierte** — el síntoma es una señal de victoria que colapsa sus dos dedos mientras los que deberían estar juntos se separan.

> Una lectura fácil equivocada: en `Perfect` los valores de índice y medio son **idénticos** en ambas manos (`(50,-50)`, `(0,0)`), y solo cambia el pulgar. Así que la regla no es "intercambia índice y medio" sino un `(-b,-a)` por dedo — que es la identidad para pares simétricos.

### 8.3 Implementación

**Ambas manos comparten un único `hand_config.yaml`.** Las poses almacenadas están siempre en **orden de mano derecha**; la mano izquierda convierte a la salida y a la vuelta, así que no hay una segunda biblioteca de poses que mantener.

La conversión vive en `hand_logic.py`:

| Función | Propósito |
|---|---|
| `resolve_hand_config(app_config, hand)` | Superpone `hands.<name>` sobre la configuración de nivel superior (mano derecha) |
| `servo_pairs()` / `servo_ids()` | Los `(servo1_id, servo2_id)` por dedo de esa mano / todos los IDs de servo en orden ascendente |
| `hand_angle_offset()` / `hand_mirrors_pose()` | Leen los dos parámetros de diferencia de la mano |
| `adapt_pose_for_hand(positions, mirror)` | Intercambia el `(pos1, pos2)` de cada dedo. **Intercambiar es su propia inversa**, así que la misma función convierte al aplicar y vuelve a convertir al guardar |

**Conectado en:**

- GUI: aplicación de poses (el botón `✓ Apply` y la reproducción de secuencias), y el guardado de una pose
- CLI: `--pose` / `--sequence`

**Los objetivos raw de los tres botones globales** se configuran por mano y no pasan por esta conversión (`raw_positions` se escribe bajo `hands.left`).

### 8.4 Uso

La GUI pregunta antes de abrir:

```
  AmazingHand — which hand?
    1 = right hand  (servo IDs 1-8)
    2 = left hand   (servo IDs 11-18)
  Enter 1 or 2 [1]:
  LEFT hand — servo IDs 11-18
    Ring (11, 12)  Middle (13, 14)  Pointer (15, 16)  Thumb (17, 18)
    middle position raw: [571, 451, 571, 451, 571, 451, 571, 451]
```

Pulsar Intro usa el valor `hand:` de `config.yaml`. Para saltarse el aviso:

```bash
python amazing_hand_gui.py --hand left
python amazing_hand_cmd.py --pose victory --hand left
```

### 8.5 Lista de comprobación inicial para la mano izquierda

En `hands.left.raw_positions`, solo **middle** es el valor por defecto del fabricante (`571, 451`); `open` y `close` se derivaron del demo del fabricante:

| Botón | Raw mano izquierda | Origen |
|---|---|---|
| Posición media | `571, 451, …` | Valor por defecto del fabricante |
| Abrir todo | `380, 642, …` | Derivado: el mismo gesto que "Abrir todo" de la mano derecha, aplicado al `MiddlePos` izquierdo |
| Cerrar todo | `880, 142, …` | Igual |

**Compruébalos en este orden la primera vez que conectes la mano izquierda:**

1. Pulsa **Posición media** y confirma que la fila `Current (0-1023)` lee `571, 451, 571, 451, …`
2. Pulsa **Abrir todo** / **Cerrar todo** — el recorrido debe llegar a los topes sin atascarse
3. Prueba `victory` (índice y medio se abren en V), `greeting` (tres dedos juntos), `ok` (las puntas del pulgar y el índice se tocan)

Si algo va mal:

| Síntoma | Cambio |
|---|---|
| La posición media lee mal | `hands.left.raw_positions.middle` |
| Dirección de apertura invertida | pon `hands.left.mirror_pose` a `false` |
| Recorrido demasiado corto o demasiado largo | `hands.left.raw_positions.open` / `close` |

### 8.6 Si tu mano izquierda está numerada 1-8

Algunas personas renumeran los servos de la mano izquierda a 1–8. En ese caso solo hay que cambiar `hands.left.servos`:

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

> `angle_offset` y `mirror_pose` **no cambian** — describen el montaje mecánico, no la numeración de IDs. La inversión de los servos pares sigue aplicándose también, porque el par de cada dedo conserva "primero el ID impar".

---

## 9. Detección automática del puerto serie

### 9.1 El problema

El original codificaba a mano la lista de puertos de Windows como `COM1`–`COM20`:

```python
available_ports = [f'COM{i}' for i in range(1, 21)]
```

Pero un adaptador puede caer en cualquier número de puerto (en esta máquina se midió `COM243`). El resultado: **tu puerto simplemente no aparece en el desplegable**, y la conexión automática recurre a un valor por defecto configurado que no existe, fallando con "the system cannot find the file specified".

### 9.2 Solución

Se añadió `available_serial_ports()`, con reservas por etapas:

1. `list_ports.comports()` de pyserial (se usa si está instalado — la información más completa)
2. Windows sin pyserial: leer la clave del registro `HARDWARE\DEVICEMAP\SERIALCOMM` (**solo biblioteca estándar**, sin dependencias nuevas)
3. Linux/macOS: glob `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`, `/dev/cu.usb*`
4. Solo si todo lo anterior falla, recurrir a la lista de candidatos original

Los puertos se ordenan de forma **natural**, así que `COM2` va antes que `COM10`.

### 9.3 Cambios de apoyo

- El desplegable pasó de `readonly` a **editable** — puedes escribir un puerto cuando la detección no lo encuentra
- Si el valor por defecto configurado no está presente, la GUI **arranca en el primer puerto que existe realmente** en lugar de intentar un valor por defecto que no está ahí
- **Un `--port` explícito nunca se sobrescribe** por esa reserva (se controla con `port_was_explicit`)

---

## 10. Referencia de configuración

### `data/config.yaml`

El `servos` / `auto_extremes` / `raw_positions` de nivel superior describen la **mano derecha** y sirven como valores por defecto; `hands.<name>` los superpone clave a clave.

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

`auto_extremes` es **compartido** por ambas manos — el deslizador lateral se comporta igual en el espacio de poses; una mano reflejada simplemente se abre al otro lado físicamente.

### `data/hand_config.yaml`

Los 8 valores de una pose están ordenados **Anular, Medio, Índice, Pulgar** (pares de servo `(5,6) (3,4) (1,2) (7,8)`), **no** por ID de servo.

**Este archivo lo comparten ambas manos y siempre se almacena en orden de mano derecha.** La mano izquierda intercambia el par de cada dedo al aplicar, y lo vuelve a intercambiar al guardar.

> ⚠️ El docstring al principio de `amazing_hand_cmd.py` afirma "index 0→servo1 … 7→servo8". Ese comentario es **incorrecto**; el orden de arriba es lo que el código hace realmente.

---

## 11. Resultados medidos

### Precisión de alcance (tras las correcciones)

| Pose | Objetivo | Real | Error máx. |
|---|---|---|---|
| `open` | todos −35 | −36.6 … −33.4 | ≤1.6° |
| `close` | todos 75 | 74.7 … 75.3 | ≤0.3° |
| `ok` | — | — | 0.5° |
| `victory` | — | — | 1.0° |
| `greeting` | — | — | 2.2° |

### Comprobaciones de conversión

```
raw -> degrees -> raw: 2048 combinations, zero error
open    raw [260, 760] -> back [260, 760]
middle  raw [451, 571] -> back [451, 571]
close   raw [760, 260] -> back [760, 260]
```

### Problemas pendientes conocidos

- **`ok` y `victory` en `demo` no tienen casi margen de temporización** (+0.01 s según la velocidad medida). Actualmente pasan solo porque la tolerancia de < 5° los atrapa. Una caída de la tensión de la batería, un cambio de temperatura o una mano un poco más rígida podrían hacerlos fallar. Subir ambos retardos de 1.0 s a 1.2 s es el siguiente paso obvio.
- **`scissors` es byte a byte idéntica a `two`**, y **`stone` es byte a byte idéntica a `close`**. Semánticamente está bien (scissors = dos dedos, stone = puño) pero literalmente duplicadas, y no se han limpiado.
- **Los deslizadores aún conservan un error de representación de ~0.3°** frente a los objetivos raw (ver 2.4).
- **`config.yaml` y el `default_config` de `hand_logic.py` están desincronizados.** Este último aún lleva la escala original (`servo_min: -40`, etc.); solo se usa cuando falta `config.yaml`. El test `test_hand_logic.py::TestAngleLimits::test_defaults` comprueba exactamente esos valores por defecto antiguos.

---

## 12. Resumen archivo por archivo

| Archivo | Cambios |
|---|---|
| `hand_logic.py` | Nuevas constantes de conversión de SCS0009; `raw_to_degrees` / `raw_to_radians` / `degrees_to_raw` / `pose_to_servo_order` / `servo_to_pose_order`; formato de visualización `raw_position`; valores por defecto de `raw_positions`; **compatibilidad con las manos** (`HAND_NAMES` / `DEFAULT_HAND_SERVOS` / `resolve_hand_config` / `servo_pairs` / `servo_ids` / `hand_angle_offset` / `hand_mirrors_pose` / `adapt_pose_for_hand`); **`available_serial_ports()`**; la E/S del archivo de configuración pasó a **UTF-8** (usaba el valor por defecto GBK de Windows y fallaba con comentarios no ASCII) |
| `amazing_hand_gui.py` | Nuevos `_apply_raw_hand_position` / `middle_all` / `_send_exact_positions`; reescritura de `open_all` / `close_all` / `_apply_pose_from_config` / `_log_pose_completion`; nuevo botón **Posición media**; nueva fila de posición raw en la realimentación de servos; `self.app_config` promovido a atributo de instancia; eliminado el `latest_goal_positions` sin usar y unificado el orden de escritura de `feedback_data['goal']`; **selección de mano al arrancar + `--hand`**; **8 `range(1,9)` codificados a mano sustituidos por los IDs reales de la mano**; el título de la ventana muestra la mano activa; desplazamiento de ángulo y conversión de espejo conectados en todas las rutas de pose; **el desplegable de puertos ahora lista los puertos detectados y acepta entrada escrita** |
| `amazing_hand_cmd.py` | Nuevo `--hand`; `connect` / `apply_pose` / `wait_for_motion` / desconexión-al-salir ahora usan los IDs reales de la mano; las rutas de pose y secuencia aplican el desplazamiento de ángulo y la conversión de espejo; la lectura de configuración pasó a UTF-8 |
| `data/config.yaml` | `limits` / `auto_extremes` recalibrados; añadido `raw_positions`; añadidos `hand` y un bloque de sobrescritura `hands.left` |
| `data/hand_config.yaml` | Las 19 poses reescaladas; las cuatro poses `*_close` corregidas; el pulgar de `greeting` / `paper` corregido; balanceo de `wave_r` / `wave_l` estrechado a ±30; `demo` recibió un retardo de `greeting` más largo y un nuevo paso de cierre |
| `pyproject.toml` | Corregido `build-backend` (`setuptools.backends.legacy:build` → `setuptools.build_meta`) |

### Glosario

| Término | Significado |
|---|---|
| **Modo Auto** | Dos deslizadores — "base" (abrir/cerrar) y "side" (lateral) — controlan indirectamente los dos servos de un dedo |
| **Modo Raw** | Los dos ángulos de servo de un dedo se controlan directamente |
| **base** | Grado de apertura/cierre, `(pos1 + pos2) / 2` |
| **side** | Desplazamiento lateral, `base − pos1` |
| **raw** | Unidad de posición interna del servo: 0–1023 sobre 300°, centro 511 |
| **MiddlePos** | Calibración central por servo del firmware del fabricante; difiere entre manos (ver 8.1) |
| **angle_offset** | El desplazamiento de montaje de 35.16° entre manos (ver 8.2) |
| **mirror_pose** | El intercambio del par de servos por dedo de la mano izquierda (ver 8.2) |
