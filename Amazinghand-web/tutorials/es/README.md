[Deutsch](../de/README.md) | [English](../en/README.md) | Español | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (Brasil)](../pt-br/README.md) | [Português (Portugal)](../pt-pt/README.md) | [简体中文](../zh-hans/README.md) | [繁體中文](../zh-hant/README.md)

# Control web de AmazingHand

Controla la mano diestra AmazingHand desde el navegador — **mano izquierda o derecha**, con dos formas de gobernarla:

- **Manual** — 8 deslizadores de servo + 19 poses predefinidas + vuelta al centro con un clic
- **Teleoperación por cámara** — MediaPipe se ejecuta localmente en el navegador y mapea tu mano sobre los dedos en tiempo real (el vídeo nunca sale de la máquina)
- **Interfaz bilingüe** — cambia entre chino e inglés en la esquina superior derecha; el navegador recuerda tu elección

El mapa de servos, la biblioteca de poses y las fórmulas de conversión coinciden con
[AmazingHandControl](https://github.com/pollen-robotics/AmazingHand) (la GUI oficial).

---

## Inicio rápido

Abre una terminal y entra en la carpeta Amazinghand-web:

```bash
pip install -r requirements.txt

python server.py --no-connect   # recomendado: arranca el servidor, elige el puerto en la página (no se mueve nada)

# python server.py                # detecta el puerto serie automáticamente y conecta
# python server.py --port COM9    # usa un puerto concreto
# python server.py --hand left    # habilita solo la mano izquierda
# python server.py --dry-run      # sin puerto serie, solo la interfaz
```

Después abre **http://localhost:8000** en un navegador.

### Elegir el puerto serie en la página

En la parte superior de la página hay una barra de puerto:

```
Port  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [Refresh]  [Connect]  [Disconnect]  Connected to COM3
```

- El desplegable lista todos los puertos serie de la máquina. Los chips USB-serie habituales (CH34x / CP210x / FTDI …) van marcados con **★** y se ordenan primero
- **Refresh** vuelve a escanear (úsalo tras conectar la placa)
- **Connect** abre el puerto seleccionado; la mano vuelve al centro justo después
- **Disconnect** libera el par primero, para que los servos no se queden bloqueados donde están
- Para cambiar de puerto, elige el nuevo y pulsa Connect — el puerto antiguo se cierra por ti

> **`--no-connect` está pensado para este flujo**: el servidor arranca sin tocar ningún puerto serie,
> así que no puede coger el equivocado y dar un tirón a la mano. Quita el flag si quieres que conecte al arrancar.

Los registros serie van a `server.log` (si lo lanzas mediante un `.bat`, la ventana se abre y se cierra en un parpadeo — lee el archivo en su lugar).

### Comprobación del cableado

Lista los IDs de servo que encuentra y los comprueba mano a mano contra `config.json`.

```bash
python tools/scan_servos.py --port COM9
```

Sustituye COM9 por tu puerto real.

---

## Mapa de servos

Fuente: `DEFAULT_HAND_SERVOS` en `AmazingHandControl/hand_logic.py` y
`docs/zh-hans/CONFIG_FORMAT.md`.

| Dedo | ID mano derecha | ID mano izquierda |
|---|---|---|
| Anular | 5, 6 | 11, 12 |
| Medio | 3, 4 | 13, 14 |
| Índice | 1, 2 | 15, 16 |
| Pulgar | 7, 8 | 17, 18 |

### Los dos servos de un dedo hacen trabajos distintos ⚠️

```
servo1 (ID impar)  = eje de flexión   abierto ↔ cerrado
servo2 (ID par)    = eje de splay     dedos juntos ↔ separados
```

La interfaz muestra exactamente estos dos ejes. **«El dedo no se abre / no se cierra» significa que el eje de splay no se mueve** —
una V tipo tijera sale de un splay del índice de `+17` y un splay del medio de `−30` (uno positivo, uno negativo).

Se combinan en el bus:

```
servo1 = flexión + splay
servo2 = flexión − splay
```

Rango (derivado de las 19 poses oficiales más el centro):

| Eje | Rango | Significado |
|---|---|---|
| Flexión | −50 ~ +90 | abierto (negativo) ↔ cerrado (positivo) |
| Splay | −45 ~ +45 | juntos (negativo) ↔ separados (positivo) |

**Dos reglas de ID** (equivocarse quema servos o invierte el movimiento):

1. **Los IDs impares son el primer servo de un dedo, los pares el segundo.** Cierto en ambas manos
   (la izquierda 11/12, 13/14 … también alternan). El segundo servo va **montado al revés**, así que niégalo en la conversión.
2. **La mano izquierda no es 9–16, es 11–18, numerada empezando por el anular.** Cablearla como 1–8 en secuencia siempre está mal.

![Both_Hands-IDs](../../Both_Hands-IDs.jpg)

---

## Conversión

Idéntico a `apply_pose()` en `AmazingHandControl` (verificado pose a pose):

```
1) cuando mirror_pose es true, primero intercambia los dos valores de servo de cada dedo
2) servo_deg = (ID impar ? +1 : -1) × (valor de pose − angle_offset_deg)
```

| Mano | angle_offset_deg | mirror_pose |
|---|---|---|
| Derecha | `0` | **sí** ⚠️ |
| Izquierda | `-35.16` | sí |

`-35.16°` es el desfase físico de medio diente de las bocinas del servo de la mano izquierda respecto a la derecha, tomado de la config oficial.

> **Sobre `mirror_pose` — esta versión difiere de la oficial**
>
> En la referencia oficial solo la mano izquierda es `true`. **El módulo de la mano derecha de esta versión también tiene sus
> pares de servos montados al revés**, así que la mano derecha también es `true`.
>
> El intercambio solo invierte el **splay**, nunca la flexión: `base = (a+b)/2` no cambia al intercambiar, mientras que
> `side = (a−b)/2` cambia de signo. Así que si el splay de una mano sale reflejado, este es el primer interruptor que hay que revisar.

El array de pose siempre son 8 valores en el orden **`[ring, middle, index, thumb]`**, dos por dedo —
idéntico byte a byte al `data/hand_config.yaml` oficial, así que puedes compararlos directamente.

### Ejemplos resueltos

| Pose | Derecha | Izquierda |
|---|---|---|
| `open` `[-35]*8` | ID5 **−35** / ID6 **+35** | ID11 **+0.16** / ID12 **−0.16** |
| `close` `[75]*8` | ID5 **+75** / ID6 **−75** | ID11 **+110.16** / ID12 **−110.16** |
| middle `[-17.578]*8` | ID5 **−17.58** / ID6 **+17.58** | ID11 **+17.58** / ID12 **−17.58** |

> **Fíjate en que el `close` de la mano izquierda necesita ±110.16°**, muy por encima del de la derecha. Por eso `config.json`
> fija el límite en **±120°** (el rango completo del SCS0009 es de unos ±150°). Un límite de ±90 recortaría el puño de la mano izquierda.

---

## Poses predefinidas (19)

| Pose | Descripción | Pose | Descripción |
|---|---|---|---|
| `open` | Abierta | `wave1` | Saludo |
| `close` / `stone` | Puño | `wave_r` / `wave_l` | Deslizar a la derecha / izquierda |
| `ok` | OK | `ring_close` | Solo el anular |
| `greeting` | Saludo | `middle_close` | Solo el medio |
| `victory` / `two` / `scissors` | Victoria / Dos | `pointer_close` | Solo el índice |
| `paper` | Papel | `thumb_close` | Solo el pulgar |
| `one` / `three` | Uno / Tres | `hifive` | Choca esos cinco |

Para cambiar una pose, edita la sección `poses` de `config.json`; las claves coinciden con los nombres del YAML oficial.

### La izquierda y la derecha pueden usar valores distintos

Dentro de una pose, `positions` es **compartido por ambas manos**. Si una mano necesita un conjunto distinto por
diferencias de montaje mecánico, añade una clave `right` o `left` a esa entrada y anulará a `positions`:

```jsonc
"close": {
  "label": "Puño",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // compartido por ambas manos
  "right":     [ ... 8 valores ... ]                // opcional: solo la mano derecha
}
```

---

## Dos modos

| Modo | Comportamiento |
|---|---|
| **Mano derecha** | Envía solo a los 8 servos de la mano derecha |
| **Mano izquierda** | Envía solo a los 8 servos de la mano izquierda (espejo + desfase de −35.16° aplicados automáticamente) |

Una mano a la vez. Ambas manos están en el mismo bus; cambia con **Target** en la parte superior.
El cambio no molesta a la otra mano — mantiene su pose donde está.

---

## Teleoperación por cámara

Los landmarks de mano de MediaPipe se ejecutan localmente en el navegador (recursos en `web/mediapipe/`, con capacidad offline).
Los 21 landmarks se convierten en valores de pose para 4 dedos y se transmiten a la mano seleccionada.

### 1. Captura tres poses primero

Arranca la cámara, luego pon la mano en la pose y pulsa el botón de captura de esa pose (aproximadamente 1 segundo de promedio).
El orden da igual; pulsa otra vez el mismo botón para volver a capturar. **El estado solo se pone en verde cuando las tres están capturadas** —
no se envía nada antes de eso, así que la mano se queda en el centro.

| Botón | Pose | Aporta |
|---|---|---|
| ① Spread | Dedos estirados y separados, pulgar apuntando hacia fuera | El extremo "estirado" de la flexión + el extremo "separado" del splay |
| ② Together | Dedos estirados y juntos, pulgar pegado al índice | El extremo "juntos" del splay |
| ③ Fist | Haz un puño, pulgar recogido hacia la palma | El extremo "cerrado" de la flexión |

### 2. Cada eje es una recta que pasa por dos puntos medidos

Tanto la flexión como el splay usan **dos extremos medidos para definir una recta**:

```
t        = (medido − extremoA) / (extremoB − extremoA)      // acotado a 0..1
objetivo = A.objetivo + (B.objetivo − A.objetivo) × t
```

La ventaja: **el signo de la medición de cada dedo se absorbe automáticamente** — así que no hay
ninguna casilla de "invertir este dedo" que marcar. (El índice y el anular están en lados opuestos de la línea central, y
la cadena de articulaciones del pulgar es distinta, así que sus direcciones son de verdad opuestas — dos extremos medidos lo absorben.)

Los objetivos de los extremos están en la sección `camera` de `config.json`:

| Eje | Extremos | Anular | Medio | Índice |
|---|---|---|---|---|
| Flexión | estirado → puño | −50 → 90 | −50 → 90 | −50 → 90 |
| Splay | juntos → separados | −45 → +45 | 0 → 0 | +45 → −45 |

Ambos extremos del splay son 0 para el dedo medio (no se mueve de lado).

### 3. El pulgar solo flexiona ⚠️

La CMC del pulgar es una **articulación en silla de montar (oponible)**, y su flexión se acopla estrechamente con la abducción —
con el pulgar pegado al índice ya está en una posición de splay, así que el "cero de flexión" medido ahí está contaminado.
Fuérzalo a dos ejes y los dos salen mal.

Así que el pulgar **solo flexiona; su splay es siempre 0** (sus dos servos reciben el mismo valor). Las dos
poses de referencia que necesita son la ① (apuntando hacia fuera) y la ③ (apuntando hacia la palma) — no hay nada extra que capturar.

### 4. El splay se desvanece a medida que el dedo se cierra

El splay final se escala por:

```
side = side_measured × (1 − curl)
```

`splayDeg` es la proyección de la dirección MCP→PIP sobre el eje lateral de la palma, y la flexión del dedo
**rota exactamente alrededor de ese eje** — pasado cierto grado de curvatura, la proyección cambia de signo y el
"separado" medido salta de golpe al otro extremo.

Sin el desvanecimiento, ese salto viaja a través de `servo2 = flexion − splay` y arrastra el **servo de ID par**
hacia atrás. (El ID impar recibe `flexion + splay`, así que se mueve igual, solo que más rápido — no se nota.)
El síntoma es "a medio camino del puño, los servos 12 y 16 se invierten de repente" — el 12 es el servo de
splay del anular izquierdo y el 16 el del índice izquierdo, precisamente los dos cuyos objetivos de splay no son cero.

Con el desvanecimiento, el splay es **exactamente 0** a curvatura completa por muy loca que se vuelva la medición.
Y un puño debería ser con los dedos juntos de todas formas.

### 5. Colores del esqueleto

| Dedo | Color |
|---|---|
| Pulgar | naranja |
| Índice | rojo |
| Medio | azul |
| Anular | amarillo |
| Meñique | gris apagado |
| Huesos de la palma | gris neutro |

El meñique no se usa para el mapeo de gestos, pero su **MCP base (landmark 17) define el sistema de coordenadas de la palma de la mano derecha**, así que no se puede simplemente descartar.

### Guía rápida de ajuste

| Qué quieres cambiar | Dónde |
|---|---|
| Valores objetivo de los ejes | sección `camera` de `config.json` |
| **El splay de izquierda y derecha va en sentidos opuestos** | pon esa mano a `-1` en `camera.side_sign` (`1` = sin cambios) |
| Suavidad | `SMOOTH` en `tracking.js` (por defecto 0.35; más bajo es más estable pero con más retardo) |
| Con qué rapidez se registra una curvatura | vuelve a capturar las tres poses |

`side_sign` se aplica a la mano que esté seleccionada en **Target**. Cámbialo y recarga la página —
no hace falta reiniciar el servidor:

```jsonc
"side_sign": { "right": 1, "left": -1 }   // invierte todo el eje de splay en la mano izquierda
```

La flexión no se ve afectada por `side_sign`.

---

## Estructura del proyecto

```
Amazinghand-web/
├── config.json          mapa de servos / biblioteca de poses / secuencias / límites (generado desde el YAML oficial)
├── server.py            backend: serie + archivos estáticos + WebSocket
├── requirements.txt
├── README.md            inglés
├── tutorials/           de · en · es · fr · it · ja · ko · pt-br · pt-pt · zh-hans · zh-hant
├── tools/
│   └── scan_servos.py   escanea el bus en busca de servos y comprueba sus IDs
└── web/
    ├── index.html · app.js · tracking.js · style.css
    ├── i18n.js          textos de la interfaz (diccionario chino/inglés + el conmutador de arriba a la derecha)
    └── mediapipe/       recursos de MediaPipe (empaquetados localmente, offline, ~42 MB)
```

Protocolo frontend/backend:

```jsonc
// frontend → backend   target: "left" | "right"
{ "cmd": "ports" }                                  // volver a escanear los puertos serie
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
{ "type": "error", "msg": "fallo al conectar COM_FAKE: el sistema no encuentra el archivo especificado." }
```

---

## Seguridad

| Elemento | Descripción |
|---|---|
| **Límites de pose** | ±120° (`limits` en `config.json`); las 19 poses verificadas para mantenerse dentro |
| **Deduplicación de cambios** | los cambios por debajo de 0.5° no se envían, así no se inunda el bus con ruido |
| **Limitación de escritura** | mínimo 20 ms entre escrituras |
| **Parada de emergencia (E-stop)** | el botón rojo de la interfaz libera todos los servos a la vez |
| **Protección al salir** | el par se libera automáticamente con Ctrl+C |
| **Depuración de una sola mano** | `--hand left/right` |

---

## Solución de problemas

**El movimiento está invertido** → comprueba que el cableado siga el orden "primero el ID impar"; en la mano izquierda confirma también `angle_offset_deg = -35.16`.

**El puño de la mano izquierda es demasiado pequeño / los servos zumban** → probablemente el límite siga en ±90; comprueba que `config.json` tenga ±120.

**Un dedo no se mueve / "expected N motors, found M"** → ejecuta `tools/scan_servos.py`; los IDs de la mano izquierda son los más fáciles de cablear mal.

**La posición central está desviada** → el valor central `-17.578125` se convierte desde el valor bruto oficial 451/571.
Para calibrar contra tu propio montaje, edita `middle.positions` en `config.json`.

**El seguimiento de cámara tiembla** → iluminación uniforme, palma mirando a la cámara. `SMOOTH` en `tracking.js`
(por defecto 0.35) — más alto es más suave pero con más retardo.

**Los gestos de cámara están mal / un dedo no sigue** → mira la sección de Teleoperación por cámara de arriba. Comprueba tres cosas primero:

1. **¿Están capturadas las tres poses?** — el estado debe estar en verde; no se envía nada antes de eso y la mano se queda en el centro
2. **Una dirección invertida significa que esa pose se capturó al revés** — solo vuelve a capturar ese botón, sin tocar el código
3. **El pulgar no debería hacer splay** — solo flexiona, ver la sección 3 de arriba

**Un servo se invierte de golpe a medio puño** → ese servo debería tener un **ID par** (el eje de splay, p. ej. mano izquierda 12 / 16).
Normalmente el splay se desvanece a 0 con la curvatura y nunca salta; si ves esto, la línea `side *= (1 - curl)` de
`tracking.js` no está surtiendo efecto, o `curl` no se está calculando.
