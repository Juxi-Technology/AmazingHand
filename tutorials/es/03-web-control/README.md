---
title: "Control web de AmazingHand"
description: "Descripción general del control web de AmazingHand: modo de inicio, cambio de controlador, barra de puerto serie, control manual, teleoperación por cámara y diseño de seguridad."
version: both
---

# Control web de AmazingHand

Controla la mano diestra AmazingHand desde el navegador, con **dos modos: mano izquierda / mano derecha** y dos formas de operarla:

- **Control manual** — 8 deslizadores de servo + 19 poses predefinidas + vuelta al centro con un clic
- **Teleoperación interactiva por cámara** — MediaPipe se ejecuta localmente en el navegador, reconoce los movimientos de la mano y los mapea a los dedos en tiempo real (el vídeo no sale de la máquina)
- **Cambio chino/inglés** — se cambia en la esquina superior derecha; el navegador recuerda la elección y la mantiene la próxima vez

> Esta página es la **descripción general del control web**. Para el mapeo/conversión específicos de SCS0009, consulta [Control web SCS0009](scs0009.md); para el cableado/flasheo/calibración específicos de PWM, consulta [Control web PWM](pwm.md).

## Inicio rápido

Abre una terminal y entra en la carpeta Amazinghand-web:

```bash
pip install -r requirements.txt

python server.py --no-connect   # recomendado: arranca primero el servidor y elige el puerto en la página (no toca los servos)

# python server.py                # detecta el puerto serie automáticamente y conecta
# python server.py --port COM9    # especifica el puerto serie
# python server.py --hand left    # habilita solo la mano izquierda
# python server.py --driver pwm   # usa la versión con servos PWM del ESP32-S3
# python server.py --dry-run      # no abre ningún puerto serie, solo valida la interfaz
```

Abre **http://localhost:8000** en el navegador.

También puedes usar directamente el frontend estático (Web Serial, sin servidor Python):

- En línea: <https://juxi-technology.github.io/AmazingHand/Amazinghand-web-io/> (Chrome / Edge)
- Local: ejecuta `python -m http.server 8099` en la raíz del repositorio y abre <http://localhost:8099/Amazinghand-web-io/>

### Elegir el puerto serie en la página

En la parte superior de la página hay una barra de herramientas: primero se elige el controlador y después el puerto:

```
驱动  [SCS0009 总线 ▾]  串口  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [刷新]  [连接]  [断开]  已连接 COM3
```

- Desplegable de controlador: **Bus SCS0009** (servos de bus oficiales, opción por defecto) o **PWM (ESP32-S3)** (ver [Control web PWM](pwm.md))
- El desplegable lista todos los puertos serie de la máquina; los chips USB-serie habituales (CH34x / CP210x / FTDI, etc.) van marcados con **★** y se ordenan primero
- **Actualizar** vuelve a escanear (úsalo tras conectar o desconectar la placa)
- **Conectar** abre el puerto seleccionado; al conectar, la mano vuelve automáticamente al centro
- **Desconectar** libera primero el par y luego desconecta, para que los servos no se queden bloqueados donde están (la versión PWM no tiene comando de par; ver más abajo)
- Para cambiar de puerto, elige el nuevo y pulsa «Conectar» — el puerto antiguo se cierra automáticamente

> **El despliegue estático (GitHub Pages) no tiene servidor Python**: por privacidad, el navegador no puede enumerar los puertos serie en silencio y solo ve los dispositivos que hayas autorizado. En ese caso, pulsa **Añadir puerto…** y elige la placa controladora en el diálogo del navegador; el comportamiento de «listar todos los puertos serie de la máquina» descrito arriba solo se aplica al modo servidor `server.py`.

![Parte superior de la página web: selección de controlador, barra de puerto serie y cambio de mano izquierda/derecha](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-port-bar.png)

> **`--no-connect` está pensado para este flujo**: al arrancar solo inicia el servidor y no toca ningún puerto serie, así que la mano no se mueve por conectar automáticamente el puerto equivocado. Si quieres que conecte al arrancar, quita este parámetro.

Los registros del puerto serie se escriben en `server.log` (si lo lanzas con doble clic en un .bat, la ventana se abre y se cierra en un parpadeo — lee este archivo en su lugar).

### Comprobación del cableado

Lista los IDs de servo encontrados y los comprueba mano a mano contra `config.json`.

```bash
python tools/scan_servos.py --port COM9
```

Sustituye COM9 por tu puerto real.

> Esta herramienta solo se aplica a los **servos de bus SCS0009**. Para revisar el cableado de la versión PWM, consulta [Control web PWM](pwm.md) o usa `AmazingHand-PWM/tools/serial_test.py`.

---

## Poses predefinidas (19)

![Panel de control manual: deslizadores de los cuatro dedos, 19 poses predefinidas y botones de operación](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-manual.png)

| Pose | Descripción | Pose | Descripción |
|---|---|---|---|
| `open` | Abrir | `wave1` | Saludo |
| `close` / `stone` | Puño | `wave_r` / `wave_l` | Balanceo a la derecha / izquierda |
| `ok` | OK | `ring_close` | Solo anular |
| `greeting` | Saludo | `middle_close` | Solo medio |
| `victory` / `two` / `scissors` | Victoria / Dos | `pointer_close` | Solo índice |
| `paper` | Papel | `thumb_close` | Solo pulgar |
| `one` / `three` | Uno / Tres | `hifive` | Choca esos cinco |

Para modificar una pose, edita la sección `poses` de `config.json`; los nombres de las claves coinciden con los del YAML oficial.

### La mano izquierda y la derecha pueden usar valores distintos

Dentro de cada pose, `positions` es **compartido por ambas manos**. Si una mano necesita otro conjunto de valores por diferencias de montaje mecánico, añade una clave `right` o `left` a esa entrada y anulará a `positions`:

```jsonc
"close": {
  "label": "Puño",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // compartido por ambas manos
  "right":     [ ... 8 valores ... ]                // opcional: solo para la mano derecha
}
```

---

## Dos modos

| Modo | Comportamiento |
|---|---|
| **Mano derecha** | Solo envía a los 8 servos de la mano derecha |
| **Mano izquierda** | Solo envía a los 8 servos de la mano izquierda (SCS0009 aplica automáticamente el espejo y el desfase de −35.16°; PWM usa el mapeo de canales de la mano izquierda) |

Se controla una sola mano a la vez; cambia con el «objeto de control» de la parte superior. El cambio no afecta a la otra mano, que mantiene su pose actual. En SCS0009 ambas manos pueden conectarse al mismo bus; en PWM cada mano la controla un ESP32-S3 distinto.

---

## Teleoperación interactiva por cámara

MediaPipe ejecuta localmente en el navegador los landmarks de la mano (recursos en `Amazinghand-web/web/mediapipe/`, disponibles sin conexión; la página también intenta primero `Amazinghand-web-io/mediapipe/`), convierte los 21 landmarks en valores de pose para 4 dedos y los envía en tiempo real a la mano seleccionada.

![Panel de cámara: inicio, visualización del esqueleto, captura de poses en tres pasos y zona de estado](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-camera.png)

### 1. Captura tres poses primero

Arranca la cámara, pon la mano en la pose y pulsa el botón correspondiente para capturarla (aproximadamente 1 segundo de promedio).
El orden da igual; si te equivocas, pulsa el mismo botón para volver a capturar. **El estado solo se pone en verde cuando las tres están capturadas**;
no se envía nada antes de eso y la mano permanece en la posición central sin moverse.

| Botón | Pose | Qué aporta |
|---|---|---|
| ① Estirada y abierta | Dedos estirados y separados, pulgar hacia fuera | El extremo «estirado» de la flexión + el extremo «separado» del splay |
| ② Estirada y cerrada | Dedos estirados y juntos, pulgar pegado al índice | El extremo «junto» del splay |
| ③ Puño | Haz un puño, pulgar pegado a la palma | El extremo «puño» de la flexión |

### 2. Cada eje es una recta definida por dos puntos medidos

Tanto la flexión como el splay usan **dos extremos medidos para definir una recta**:

```
t        = (valor medido − extremoA) / (extremoB − extremoA)      // limitado a 0~1
objetivo = A.objetivo + (B.objetivo − A.objetivo) × t
```

La ventaja es que **el signo de la medición de cada dedo se absorbe automáticamente**, así que no hace falta
ningún interruptor del tipo «invertir este dedo» (el índice y el anular están en lados opuestos del eje central y la cadena de articulaciones del pulgar es distinta, así que sus direcciones son realmente opuestas,
pero los dos extremos medidos lo resuelven automáticamente).

Los objetivos de los extremos están en la sección `camera` de `config.json`:

| Eje | Extremos | Anular | Medio | Índice |
|---|---|---|---|---|
| Flexión | estirado → puño | −50 → 90 | −50 → 90 | −50 → 90 |
| Splay | junto → separado | −45 → +45 | 0 → 0 | +45 → −45 |

Ambos extremos del splay son 0 para el dedo medio (no se mueve de lado).

### 3. El pulgar solo flexiona ⚠️

La CMC del pulgar es una **articulación de oposición (en silla de montar)**, y su flexión está muy acoplada con el splay: con el pulgar pegado al índice ya está
en una posición de splay, así que el «cero de flexión» medido en ese momento está contaminado. Si lo fuerzas a dos ejes, ninguno de los dos sale bien.

Así que el pulgar **solo flexiona; su splay es siempre 0** (la cantidad diferencial de splay de sus dos servos es 0). Las dos poses de referencia que necesita son la ① (hacia fuera) y la ③ (hacia la palma); no hay que capturar nada más.

### 4. El splay se atenúa con la flexión

El splay final se escala según:

```
side = side_measured × (1 − curl)
```

`splayDeg` es la proyección de la dirección MCP→PIP sobre el eje transversal de la palma, y la flexión del dedo **gira precisamente alrededor de ese eje**: a partir de cierto grado de curvatura, la proyección se invierte y la «apertura» salta de golpe al otro extremo.

Sin atenuación, ese salto viaja por `servo2 = flexión − abducción` y arrastra al **servo de ID par** en sentido contrario
(el ID impar recibe `flexión + abducción`, cambia en sentido opuesto y por eso se nota menos).
El síntoma es «a mitad de puño, los servos 12 y 16 se invierten de repente»: el 12 es el segundo servo del anular izquierdo y el 16 el del índice izquierdo, precisamente los dos que se ven arrastrados por el diferencial cuando la componente de splay no es cero.

Con la atenuación, el splay es **siempre 0** al cerrar del todo, por muy disparatada que sea la medición. Y un puño, de todos modos, debería hacerse con los dedos juntos.

### 5. Colores del esqueleto

| Dedo | Color |
|---|---|
| Pulgar | Naranja |
| Índice | Rojo |
| Medio | Azul |
| Anular | Amarillo |
| Meñique | Gris oscuro |
| Huesos de la palma | Gris neutro |

El meñique no participa en el mapeo de gestos, pero su **MCP de la base (landmark 17) define el sistema de coordenadas de la palma de la mano derecha**, así que no se puede eliminar.

### Guía rápida de ajuste

| Qué quieres cambiar | Dónde |
|---|---|
| Valores objetivo de los ejes | sección `camera` de `config.json` |
| **El splay de izquierda y derecha va en sentidos opuestos** | pon esa mano a `-1` en `camera.side_sign` (`1` = sin cambios) |
| Suavidad | `SMOOTH` de `tracking.js` (por defecto 0.35; más bajo es más estable pero más lento) |
| Rapidez con la que se detecta la flexión | vuelve a capturar las tres poses |

`side_sign` se aplica a la mano seleccionada en el «objeto de control»; cámbialo y recarga la página, no hace falta reiniciar el servicio:

```jsonc
"side_sign": { "right": 1, "left": -1 }   // invierte todo el eje de splay en la mano izquierda
```

La flexión no se ve afectada por `side_sign`.

---

## Estructura del proyecto

```
Amazinghand-web-io/          Frontend (estático, desplegable por separado)
├── index.html
├── app.js                   Interfaz, cambio de controlador, UI de poses y cámara
├── io.js                    Backend Web Serial de SCS0009
├── pwm.js                   Backend Web Serial de PWM
├── common.js                Configuración compartida, conversión de poses y límites
├── ws.js                    Backend WebSocket (modo servidor Python)
├── tracking.js              Seguimiento de cámara con MediaPipe
├── i18n.js                  Textos en chino e inglés
├── config.json              Controlador, mapeo de servos, biblioteca de poses, parámetros de cámara
└── tools/pwm_protocol_test.mjs

Amazinghand-web/
├── server.py                Servidor HTTP + WebSocket + puerto serie
├── requirements.txt
├── tools/scan_servos.py     Escanea el bus SCS0009 y verifica los ID
└── web/mediapipe/           Recursos de MediaPipe (offline, ~42MB)
```

Protocolo frontend/backend:

```jsonc
// frontend → backend   target: "left" | "right"
{ "cmd": "ports" }                                  // volver a escanear el puerto serie
{ "cmd": "driver", "driver": "pwm" }                // scs0009 | pwm
{ "cmd": "connect",    "port": "COM3" }
{ "cmd": "disconnect" }
{ "cmd": "target", "target": "left" }
{ "cmd": "set",    "target": "left", "angles": { "pointer": [0, 0], ... } }
{ "cmd": "pose",   "target": "left", "name": "close" }
{ "cmd": "middle", "target": "left" }
{ "cmd": "torque", "target": "left", "on": true }   // solo SCS0009
{ "cmd": "stop" }

// backend → frontend
{ "type": "state", "hands": {...}, "poses": {...}, "positions": {...},
  "axes": {...}, "camera": {...}, "target": "left", "driver": "scs0009",
  "capabilities": { "torque": true, "speed": true }, "pwm": {...},
  "limits": {...}, "port": { "available": [...], "current": "COM3", "connected": true } }
{ "type": "ports" | "connected" | "disconnected", "ports": [...], ... }
{ "type": "error", "msg": "连接 COM_FAKE 失败：系统找不到指定的文件。" }
```

---

## Diseño de seguridad

| Elemento | Descripción |
|---|---|
| **Límites de pose** | Valores de pose ±120° (`limits` de `config.json`); las 19 poses están verificadas para no superarlos |
| **Deduplicación de cambios** | Los cambios < 0.5° no se envían, evitando llenar el bus de ruido |
| **Limitación de escritura** | Intervalo mínimo de 20 ms en SCS0009; control directo PWM de unos 30 ms |
| **Parada de emergencia** | SCS0009: libera todo el par; PWM: envía `0xFF` para abortar el gesto, los servos siguen alimentados manteniendo la posición |
| **Protección al salir** | SCS0009: Ctrl+C desactiva el par; PWM: tras desconectar el puerto serie los servos mantienen la posición |
| **Depuración de una sola mano** | `--hand left/right` |

---

## Preguntas frecuentes

**La cámara reconoce mal** → luz uniforme y palma frente a la cámara. En `tracking.js`, cuanto mayor es `SMOOTH` (por defecto 0.35), más suave pero más lento.

**Los gestos de cámara no son correctos o un dedo no sigue** → confirma primero que las tres poses estén capturadas (estado en verde); si una dirección está invertida, vuelve a capturar la pose correspondiente; el pulgar solo flexiona y no participa en el splay.

**A mitad de puño un servo se invierte de golpe** → comprueba que el splay se atenúe a 0 con la flexión (`side *= (1 - curl)`) y que el signo/magnitud del control de splay no sea anómalo.

**Problemas de dirección/ID/centro en SCS0009** → consulta [Control web SCS0009](scs0009.md) y [Depuración y calibración SCS0009](../06-servo-tuning/scs0009.md).

**Problemas de conexión/velocidad en baudios/calibración en PWM** → consulta [Control web PWM](pwm.md).

**Más preguntas** → [FAQ](../08-faq/faq.md).
