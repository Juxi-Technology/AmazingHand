[English](../en/REQUIREMENTS.md) | [Deutsch](../de/REQUIREMENTS.md) | Español | [Français](../fr/REQUIREMENTS.md) | [Italiano](../it/REQUIREMENTS.md) | [日本語](../ja/REQUIREMENTS.md) | [한국어](../ko/REQUIREMENTS.md) | [Português (BR)](../pt-br/REQUIREMENTS.md) | [Português (PT)](../pt-pt/REQUIREMENTS.md) | [简体中文](../zh-hans/REQUIREMENTS.md) | [繁體中文](../zh-hant/REQUIREMENTS.md)

# AmazingHandGUI — Requisitos y criterios de aceptación

Este documento recoge los requisitos funcionales y los criterios de aceptación
derivados de la implementación actual. Cada requisito hace referencia al/los
archivo(s) fuente donde se implementa el comportamiento.

---

## 1. Gestión de la conexión

### FR-CONN-1: Selección del puerto serie
La GUI ofrece un cuadro combinado que lista los puertos serie detectados automáticamente.

| AC | Criterio |
|----|-----------|
| 1.1 | En Linux aparecen los dispositivos `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`; si no existe ninguno, se listan `/dev/ttyACM0` y `/dev/ttyUSB0` como alternativas. |
| 1.2 | En Windows se listan `COM1`–`COM20`. |
| 1.3 | El valor por defecto coincide con el específico de la plataforma de `config.yaml` (`/dev/ttyACM0` o `COM9`). |

### FR-CONN-2: Selección de la velocidad en baudios
Un cuadro combinado ofrece opciones de velocidad en baudios configurables.

| AC | Criterio |
|----|-----------|
| 2.1 | Las opciones proceden de `config.yaml` → `serial.baudrate_options` (por defecto `[9600, 115200, 1000000]`). |
| 2.2 | La selección por defecto es `1000000`. |
| 2.3 | El desplegable está deshabilitado mientras hay conexión. |

### FR-CONN-3: Conectar / Desconectar
Los botones Conectar y Desconectar gestionan la conexión serie y el par de los servos.

| AC | Criterio |
|----|-----------|
| 3.1 | Conectar abre el puerto serie, habilita el par en los servos 1–8, deshabilita los controles Conectar/puerto/velocidad en baudios y habilita Desconectar. |
| 3.2 | Desconectar deshabilita el par en los 8 servos, vuelve a habilitar Conectar/puerto/velocidad en baudios y deshabilita Desconectar. |
| 3.3 | Un fallo de conexión muestra un error en la barra de estado y en el registro; la GUI permanece desconectada. |

### FR-CONN-4: Conexión automática al arrancar
La GUI intenta conectarse automáticamente 100 ms después de lanzarse.

| AC | Criterio |
|----|-----------|
| 4.1 | Se llama a `connect_controller()` mediante `root.after(100, …)` durante la inicialización. |

### FR-CONN-5: Conexión por CLI
La CLI se conecta mediante los argumentos `--port` y `--baudrate`.

| AC | Criterio |
|----|-----------|
| 5.1 | `--port` y `--baudrate` sobrescriben los valores por defecto. |
| 5.2 | El par se habilita en los 8 servos al conectar. |
| 5.3 | El par se deshabilita al salir (incluido Ctrl+C mediante un bloque `finally`). |
| 5.4 | `--list` **no** abre una conexión de hardware. |

---

## 2. Control de los dedos

### FR-FING-1: Cuatro widgets de dedo
Se muestran cuatro controles de dedo: Anular, Medio, Índice y Pulgar — cada uno con 2 servos.

| AC | Criterio |
|----|-----------|
| 1.1 | Se renderizan exactamente 4 widgets `FingerControl` con nombres que coinciden con los pares de servo de `config.yaml`: Anular (5,6), Medio (3,4), Índice (1,2), Pulgar (7,8). |

### FR-FING-2: Modo Auto (base + side)
El modo Auto ofrece un deslizador vertical de cerrar/abrir y otro horizontal lateral.

| AC | Criterio |
|----|-----------|
| 2.1 | Deslizador vertical: 0° (abierto) a 110° (cerrado); arriba = cerrado, abajo = abierto. |
| 2.2 | Deslizador horizontal: −40° a +40°. |
| 2.3 | Mover cualquiera de los deslizadores envía posiciones interpoladas (mediante `compute_auto_positions`) a ambos servos. |

### FR-FING-3: Modo Raw
El modo Raw muestra dos deslizadores verticales independientes (uno por servo).

| AC | Criterio |
|----|-----------|
| 3.1 | Seleccionar Raw oculta los deslizadores Auto y muestra dos deslizadores verticales por servo (−40 a 110). |
| 3.2 | La casilla Mimic se deshabilita y se desmarca; el botón Centrar se deshabilita. |
| 3.3 | Cambiar de modo sincroniza los valores en ambos sentidos (auto ↔ raw mediante `decompose_servo_positions`). |

### FR-FING-4: Control de velocidad
Cada dedo tiene un cuadro combinado de velocidad (1–6).

| AC | Criterio |
|----|-----------|
| 4.1 | El rango va de `speeds.min` (1) a `speeds.max` (6), por defecto `speeds.default` (3). |
| 4.2 | La velocidad se envía mediante `write_goal_speed()` por servo antes de los comandos de posición. |

### FR-FING-5: Modo Mimic
Los cambios de cerrar/abrir en un dedo que imita se propagan a todos los demás dedos con Mimic habilitado.

| AC | Criterio |
|----|-----------|
| 5.1 | Habilitar Mimic en A y B hace que los cambios del deslizador cerrar/abrir de A se reflejen en B y viceversa. |
| 5.2 | Mimic solo se aplica en modo Auto; cambiar a Raw lo deshabilita. |

### FR-FING-6: Botón Centrar
Restablece el desplazamiento lateral a 0°.

| AC | Criterio |
|----|-----------|
| 6.1 | Al hacer clic en Centrar se pone `side_var` a 0 y se dispara una actualización de posición. |
| 6.2 | Centrar está deshabilitado en modo Raw. |

### FR-FING-7: Rueda del ratón en el deslizador de posición
La rueda de desplazamiento ajusta la posición ±5°.

| AC | Criterio |
|----|-----------|
| 7.1 | Rueda hacia arriba → +5° (cerrar), rueda hacia abajo → −5° (abrir), limitado a los topes. |

### FR-FING-8: Indicador LED de actividad
Cada dedo muestra un LED de estado.

| AC | Criterio |
|----|-----------|
| 8.1 | En movimiento (indicador moving = true) → verde parpadeante a intervalos de ~350 ms. |
| 8.2 | Bloqueado (error objetivo-vs-posición ≥ 8° y sin movimiento) → rojo fijo. |
| 8.3 | Inactivo → gris. |

---

## 3. Control por teclado

### FR-KEY-1: Selección de dedo
Las teclas 1–4 seleccionan el dedo activo.

| AC | Criterio |
|----|-----------|
| 1.1 | 1 = Anular, 2 = Medio, 3 = Índice, 4 = Pulgar. |
| 1.2 | La barra de estado muestra el nombre del dedo seleccionado. |

### FR-KEY-2: Movimiento con las teclas de flecha
Las teclas de flecha mueven el dedo seleccionado.

| AC | Criterio |
|----|-----------|
| 2.1 | Arriba = cerrar (aumentar la posición), Abajo = abrir (disminuir). |
| 2.2 | Derecha = aumentar el desplazamiento lateral, Izquierda = disminuir. |

### FR-KEY-3: Modificadores de precisión
El tamaño del paso varía según la tecla modificadora.

| AC | Criterio |
|----|-----------|
| 3.1 | Sin modificador: 1° (preciso). |
| 3.2 | Shift: 5° (normal). |
| 3.3 | Ctrl: 10° (rápido). |
| 3.4 | La barra de estado muestra el nombre del modo y el ángulo resultante. |

### FR-KEY-4: Acciones rápidas
Atajos de una sola tecla para acciones habituales.

| AC | Criterio |
|----|-----------|
| 4.1 | Q = cerrar del todo a 110°. |
| 4.2 | E = abrir del todo a 0°. |
| 4.3 | C = centrar el lateral a 0°. |

---

## 4. Controles globales

### FR-GLOB-1: Abrir todo
Pone todos los dedos totalmente abiertos.

| AC | Criterio |
|----|-----------|
| 1.1 | Todos los `pos_var` → 0, todos los `side_var` → 0, posiciones enviadas al hardware. |

### FR-GLOB-2: Cerrar todo
Pone todos los dedos totalmente cerrados.

| AC | Criterio |
|----|-----------|
| 2.1 | Todos los `pos_var` → 110, todos los `side_var` → 0, posiciones enviadas. |

### FR-GLOB-3: Centrar todo
Restablece todos los desplazamientos laterales.

| AC | Criterio |
|----|-----------|
| 3.1 | Todos los `side_var` → 0, posiciones enviadas. |

### FR-GLOB-4: Velocidad global
Un desplegable fija de una vez las velocidades de todos los dedos.

| AC | Criterio |
|----|-----------|
| 4.1 | Seleccionar un valor actualiza el cuadro combinado de velocidad de cada dedo. |
| 4.2 | La velocidad se limita a [1, 6]. |

---

## 5. Gestión de poses

### FR-POSE-1: Guardar pose
El usuario introduce un nombre y guarda las posiciones actuales de los 8 servos.

| AC | Criterio |
|----|-----------|
| 1.1 | Las posiciones de los 4 dedos (8 valores) se capturan mediante `get_positions()`. |
| 1.2 | El nombre se valida con `validate_name()` antes de guardar. |
| 1.3 | Si tiene éxito: el desplegable se refresca (ordenado), el campo se vacía y la barra de estado lo confirma. |
| 1.4 | Un nombre inválido o vacío muestra un cuadro de diálogo de error. |

### FR-POSE-2: Aplicar pose
Seleccionar una pose y hacer clic en Aplicar lleva la mano a esa pose.

| AC | Criterio |
|----|-----------|
| 2.1 | Las 8 posiciones se aplican a todos los widgets de dedo. |
| 2.2 | Las posiciones de los servos se envían al hardware. |
| 2.3 | El retardo se estima a partir de la distancia de movimiento y la velocidad; la finalización de la pose se registra tras ese retardo con una comparación objetivo vs. real. |

### FR-POSE-3: Eliminar pose
Elimina la pose seleccionada tras confirmación.

| AC | Criterio |
|----|-----------|
| 3.1 | Un cuadro de diálogo sí/no pide confirmación. |
| 3.2 | Al confirmar: se elimina la pose de la configuración, se guarda el YAML y se refresca el desplegable. |
| 3.3 | Si no queda ninguna pose, el desplegable muestra `<no poses>`. |

### FR-POSE-4: Validación de nombres
Los nombres se validan para evitar corromper el YAML.

| AC | Criterio |
|----|-----------|
| 4.1 | Vacío / solo espacios → rechazado. |
| 4.2 | Más de 50 caracteres → rechazado. |
| 4.3 | Contiene `: { } [ ] , & * # ? \| - < > = ! % @ \` " '` → rechazado. |
| 4.4 | Contiene caracteres de control (ASCII < 32) → rechazado. |
| 4.5 | Espacios al principio/final → rechazado. |

---

## 6. Gestión de secuencias

### FR-SEQ-1: Reproductor de secuencias (ventana principal)
Selección por desplegable, casilla Loop, botones Reproducir / Pausa / Detener.

| AC | Criterio |
|----|-----------|
| 1.1 | El desplegable lista todas las secuencias guardadas (o `<no sequences>`). |
| 1.2 | La casilla Loop habilita la repetición continua. |
| 1.3 | Reproducir inicia la secuencia en un hilo en segundo plano. |
| 1.4 | Pausa alterna pausa/reanudación; el texto del botón cambia entre "⏸ Pausa" y "▶ Reanudar". |
| 1.5 | Detener pone `stop_sequence = True`; el hilo de la secuencia termina. |

### FR-SEQ-2: Motor de ejecución de secuencias
Las secuencias se ejecutan en un hilo en segundo plano con esperas interrumpibles.

| AC | Criterio |
|----|-----------|
| 2.1 | Los pasos de pose analizan el formato `"pose_name:s1,s2,...,s8\|delay"`. |
| 2.2 | Los pasos `SLEEP:duration` pausan sin comandos de hardware. |
| 2.3 | Si no hay retardo explícito: espera automática = `15.0 − (avg_speed − 1) × 2.4` segundos. |
| 2.4 | Las esperas se ejecutan en incrementos de 0.1 s, comprobando las banderas de detención/pausa en cada tic. |
| 2.5 | En modo bucle, un intervalo de 0.5 s separa las iteraciones. |
| 2.6 | Los nombres de pose desconocidos se omiten con un aviso. |
| 2.7 | Los botones Reproducir/Pausa/Detener alternan su estado habilitado/deshabilitado durante la ejecución. |

### FR-SEQ-3: Diálogo del gestor de secuencias
Diálogo de dos paneles al que se accede con el botón "🔧 Gestionar".

| AC | Criterio |
|----|-----------|
| 3.1 | Panel izquierdo: lista de las secuencias guardadas con botones Ejecutar, Editar y Eliminar. |
| 3.2 | Doble clic ejecuta la secuencia una vez (sin bucle) sin cerrar el diálogo. |
| 3.3 | Editar carga los pasos en el constructor y rellena de antemano el campo del nombre. |

### FR-SEQ-4: Constructor de secuencias
Panel derecho para construir secuencias a partir de poses.

| AC | Criterio |
|----|-----------|
| 4.1 | Se listan las poses disponibles; doble clic añade un paso con la velocidad/retardo actuales. |
| 4.2 | Cuadros numéricos de velocidad por dedo (1–6); "⬇ Copiar desde la UI" importa las velocidades de la ventana principal. |
| 4.3 | El campo de retardo añade el sufijo `\|delay` a los pasos de pose. |
| 4.4 | "⏱ Retardo" inserta un paso independiente `SLEEP:Xs`. |
| 4.5 | ↑/↓ reordena, ➖ elimina, 🗑 borra todo. |
| 4.6 | "💾 Guardar secuencia" valida el nombre, guarda y refresca los desplegables. |
| 4.7 | "▶ Ejecutar" ejecuta la secuencia construida sin guardar ni cerrar el diálogo. |

### FR-SEQ-5: Validación de la entrada de retardo
Los valores flotantes inválidos en el campo de retardo se gestionan sin errores.

| AC | Criterio |
|----|-----------|
| 5.1 | Un retardo no numérico equivale a ningún retardo (el paso se añade sin `\|delay`). |
| 5.2 | Un retardo no numérico en SLEEP muestra "Invalid delay value" en la barra de estado. |

---

## 7. Monitorización de servos

### FR-MON-1: Recopilación de telemetría en segundo plano
Un hilo demonio sondea los 8 servos a ~10 Hz.

| AC | Criterio |
|----|-----------|
| 1.1 | El hilo duerme 0.1 s entre iteraciones. |
| 1.2 | Métricas recopiladas por servo: posición, carga, temperatura, voltaje, velocidad, indicador de movimiento, estado, objetivo. |
| 1.3 | Una lectura fallida repite el último valor conocido para mantener sincronizados los arrays. |
| 1.4 | Los datos de realimentación se actualizan bajo `feedback_lock` de forma atómica. |

### FR-MON-2: Visualización del gráfico
Gráfico de Matplotlib embebido en el panel derecho.

| AC | Criterio |
|----|-----------|
| 2.1 | Métricas seleccionables: Posición, Objetivo vs Actual, Par, Velocidad, Temperatura, Voltaje, En movimiento. |
| 2.2 | El desplegable "Servos" alterna cuáles de las 8 trazas son visibles (con ✓ Todos / ✕ Ninguno). |
| 2.3 | El redibujado del gráfico se limita a intervalos de ≥100 ms. |
| 2.4 | Sin métricas seleccionadas → mensaje "Select at least one metric". |
| 2.5 | Sin datos → mensaje "Waiting for data...". |

### FR-MON-3: Modos del gráfico
Dos modos: Multi-Servo y Scope.

| AC | Criterio |
|----|-----------|
| 3.1 | El modo Scope muestra un selector "Scope Servo" para centrarse en un único servo. |
| 3.2 | Multi-Servo oculta el selector Scope Servo. |

### FR-MON-4: Zoom y desplazamiento del gráfico
Cuatro deslizadores para controlar la vista.

| AC | Criterio |
|----|-----------|
| 4.1 | Y-Zoom: 0.2× a 5.0×, por defecto 1.1×. |
| 4.2 | Y-Pan: −3.0 a +3.0, por defecto 0.0. |
| 4.3 | Time-Zoom: 10 % a 100 % de los datos disponibles. |
| 4.4 | Time-Pan: 0 % (más antiguo) a 100 % (más reciente). |
| 4.5 | Todos los deslizadores disparan redibujados del gráfico con antirrebote. |

### FR-MON-5: Modo rodante
Limita el gráfico a los últimos N puntos de datos.

| AC | Criterio |
|----|-----------|
| 5.1 | Cuando está habilitado y los datos superan `max_data_points` (100), se descartan las muestras más antiguas. |
| 5.2 | Deshabilitar el modo rodante conserva todos los datos recopilados. |

### FR-MON-6: Pausar / Reanudar / Borrar gráfico

| AC | Criterio |
|----|-----------|
| 6.1 | Pausar detiene los redibujados del gráfico; la recopilación de telemetría continúa. |
| 6.2 | Borrar restablece todos los arrays de datos y el zoom/desplazamiento a sus valores por defecto. |

### FR-MON-7: Panel de realimentación
Tabla de rejilla que muestra la telemetría en vivo de todos los servos.

| AC | Criterio |
|----|-----------|
| 7.1 | Columnas: S1–S8. Filas: Objetivo, Posición, Velocidad, Par, Voltaje, Corriente, Temperatura, Estado, En movimiento. |
| 7.2 | Valores formateados por `format_feedback_value()`: posición `X.XX°`, velocidad `X.X°/s`, voltaje `X.XX V`, temperatura `X.X °C`, corriente `X mA`, carga `X.X %`, estado `0xHH`, en movimiento `Yes/No`. |
| 7.3 | Solo se actualizan las celdas modificadas (caché de diferencias). |
| 7.4 | La actualización se limita a intervalos de ≥50 ms. |

---

## 8. Configuración

### FR-CFG-1: Carga de la configuración de la aplicación
`config.yaml` se carga con valores por defecto para todas las claves ausentes.

| AC | Criterio |
|----|-----------|
| 1.1 | Archivo ausente → se usa la configuración por defecto completa. |
| 1.2 | Las claves ausentes se completan con los valores por defecto (fusión de dos niveles). |
| 1.3 | Fallo de análisis → se devuelven los valores por defecto, con el error impreso en stdout. |

### FR-CFG-2: Asignación de servos
Los IDs de servo por dedo se definen en `config.yaml` → `servos`.

| AC | Criterio |
|----|-----------|
| 2.1 | La configuración define pointer=[1,2], middle=[3,4], ring=[5,6], thumb=[7,8]. |
| 2.2 | `all_ids` = [1,2,3,4,5,6,7,8]. |

### FR-CFG-3: Límites de ángulo

| AC | Criterio |
|----|-----------|
| 3.1 | `servo_min` = −40, `servo_max` = 110, `base_min` = 0, `base_max` = 110, `side_min` = −40, `side_max` = 40. |
| 3.2 | Todos los rangos de los deslizadores derivan de estos valores. |

### FR-CFG-4: Extremos de Auto
Puntos finales de la interpolación bilineal para el cálculo del desplazamiento lateral.

| AC | Criterio |
|----|-----------|
| 4.1 | `left_open`, `right_open`, `left_closed`, `right_closed`, `center_open`, `center_closed` son configurables. |
| 4.2 | `compute_auto_positions()` los usa para la interpolación. |

### FR-CFG-5: Configuración de velocidad

| AC | Criterio |
|----|-----------|
| 5.1 | `speeds.default` = 3, `speeds.min` = 1, `speeds.max` = 6. |

---

## 9. Herramienta CLI

### FR-CLI-1: Listar poses y secuencias
`--list` imprime todas las poses y secuencias sin abrir una conexión.

| AC | Criterio |
|----|-----------|
| 1.1 | La salida muestra el recuento de poses, cada nombre con sus posiciones. |
| 1.2 | La salida muestra el recuento de secuencias, cada nombre con el número de pasos y detalles. |
| 1.3 | No se abre ninguna conexión serie. |

### FR-CLI-2: Aplicar pose
`--pose NAME` envía una pose guardada al hardware.

| AC | Criterio |
|----|-----------|
| 2.1 | Posiciones cargadas desde la configuración; velocidad por defecto 3 aplicada a todos los servos. |
| 2.2 | Pose desconocida → error + `sys.exit(1)`. |

### FR-CLI-3: Reproducir secuencia
`--sequence NAME` reproduce una secuencia; `--loop` la repite hasta Ctrl+C.

| AC | Criterio |
|----|-----------|
| 3.1 | Las velocidades y el retardo se analizan a partir de la cadena del paso. |
| 3.2 | Los pasos `SLEEP` pausan sin comandos de hardware. |
| 3.3 | Sin retardo explícito → espera automática = `15.0 − (avg_speed − 1) × 2.4` segundos. |
| 3.4 | SIGINT pone `stop_flag` para una interrupción limpia. |
| 3.5 | Secuencia desconocida → salida con error. |
| 3.6 | Secuencia vacía → salida con error. |
| 3.7 | Las poses desconocidas dentro de una secuencia se omiten con un WARNING. |

### FR-CLI-4: Análisis de pasos
`parse_step()` maneja varios formatos.

| AC | Criterio |
|----|-----------|
| 4.1 | `SLEEP:2.0s` → espera de 2.0 s. |
| 4.2 | `open:3,3,...\|2.0s` → pose "open" con velocidades y retardo de 2.0 s. |
| 4.3 | `open` (nombre desnudo) → pose con velocidades por defecto, sin retardo. |
| 4.4 | Las velocidades de menos de 8 se rellenan con 3; las de más se truncan. |
| 4.5 | El sufijo de duración `s` / `S` se elimina. |

### FR-CLI-5: Acciones mutuamente excluyentes
`--list`, `--pose` y `--sequence` son mutuamente excluyentes.

| AC | Criterio |
|----|-----------|
| 5.1 | Pasar varias acciones → salida distinta de cero. |
| 5.2 | `--loop` sin `--sequence` → error. |

### FR-CLI-6: Sobrescritura del archivo de configuración
`--config PATH` usa un archivo YAML alternativo.

| AC | Criterio |
|----|-----------|
| 6.1 | Archivo ausente → error + `sys.exit(1)`. |

---

## 10. Persistencia de datos

### FR-DATA-1: Archivo de configuración YAML
Las poses y las secuencias se guardan en `data/hand_config.yaml`.

| AC | Criterio |
|----|-----------|
| 1.1 | El archivo usa formato YAML con las claves de nivel superior `poses` y `sequences`. |

### FR-DATA-2: Cargar la configuración

| AC | Criterio |
|----|-----------|
| 2.1 | Archivo ausente → `{'poses': {}, 'sequences': {}}`. |
| 2.2 | Archivo vacío → claves rellenadas automáticamente. |
| 2.3 | YAML malformado → estructura vacía, error impreso en stdout. |

### FR-DATA-3: Guardar la configuración con arrays en línea
Las posiciones se guardan en estilo de flujo mediante posprocesado con expresiones regulares.

| AC | Criterio |
|----|-----------|
| 3.1 | El archivo contiene el estilo `positions: [v1, v2, …, v8]`. |
| 3.2 | Los valores negativos se conservan en el formato en línea. |
| 3.3 | Devuelve `True` si tiene éxito, `False` en caso de error. |

### FR-DATA-4: Creación automática del directorio de datos

| AC | Criterio |
|----|-----------|
| 4.1 | El directorio `data/` se crea si no existe antes de escribir. |

### FR-DATA-5: Integridad del ciclo completo
Los datos escritos por la GUI pueden leerse con la CLI y viceversa.

| AC | Criterio |
|----|-----------|
| 5.1 | Las poses, las posiciones negativas y los pasos de secuencia sobreviven a un ciclo guardar-en-GUI → leer-en-CLI. |

---

## 11. Gestión de errores

### FR-ERR-1: Error de conexión
Las conexiones fallidas no hacen caer la aplicación.

| AC | Criterio |
|----|-----------|
| 1.1 | La barra de estado muestra "Connection failed: …"; `connected` sigue siendo `False`. |

### FR-ERR-2: Velocidad en baudios no válida

| AC | Criterio |
|----|-----------|
| 2.1 | Velocidad en baudios no numérica → la barra de estado muestra "Invalid baudrate". |

### FR-ERR-3: Recuperación del hilo de monitorización

| AC | Criterio |
|----|-----------|
| 3.1 | Un fallo de lectura de un solo servo no hace caer el hilo. |
| 3.2 | Los errores se imprimen en stdout. |

### FR-ERR-4: Degradación del indicador de movimiento

| AC | Criterio |
|----|-----------|
| 4.1 | Tras 3 fallos consecutivos de `read_moving`, la supervisión se desactiva con un mensaje en el registro. |
| 4.2 | Se pasa de `sync_read_moving` a lecturas por servo tras el primer fallo de sincronización. |

### FR-ERR-5: Avisos de finalización de pose

| AC | Criterio |
|----|-----------|
| 5.1 | Un error objetivo vs. real > 5° dispara un aviso ⚠ en el registro. |
| 5.2 | El tiempo de espera de movimiento (6.0 s) dispara un aviso de timeout si los servos nunca dejan de moverse. |

### FR-ERR-6: Configuración ausente (CLI)

| AC | Criterio |
|----|-----------|
| 6.1 | Archivo de configuración ausente → mensaje de error + `sys.exit(1)`. |

### FR-ERR-7: Secuencia vacía / no válida

| AC | Criterio |
|----|-----------|
| 7.1 | Pasos de secuencia vacíos → `sys.exit(1)`. |
| 7.2 | Poses desconocidas en la secuencia → omitidas con WARNING. |

---

## 12. Disposición de la interfaz

### FR-UI-1: Estructura de la ventana

| AC | Criterio |
|----|-----------|
| 1.1 | El título incluye la versión: "AmazingHand Controller v0.8". |
| 1.2 | Geometría inicial: 1920×1200. |
| 1.3 | Un `PanedWindow` horizontal separa el panel izquierdo (controles) y el derecho (gráfico). |

### FR-UI-2: Panel izquierdo

| AC | Criterio |
|----|-----------|
| 2.1 | Fila 1: Anular, Medio, Índice (3 dedos en horizontal). |
| 2.2 | Fila 2: Pulgar (derecha) + controles apilados (Conexión, Global, Pose, Secuencia). |
| 2.3 | El registro de ejecución va debajo de los controles, en un divisor vertical redimensionable. |

### FR-UI-3: Barra de estado

| AC | Criterio |
|----|-----------|
| 3.1 | Se actualiza al conectar, desconectar, seleccionar dedo, cambiar velocidad, en operaciones de pose y ante errores. |

### FR-UI-4: Registro de ejecución

| AC | Criterio |
|----|-----------|
| 4.1 | Los mensajes van precedidos de una marca de tiempo `[HH:MM:SS.mmm]`. |
| 4.2 | Se desplaza automáticamente hasta la última entrada. |
| 4.3 | Los mensajes también se imprimen en stdout. |

### FR-UI-5: Tooltips

| AC | Criterio |
|----|-----------|
| 5.1 | Aparece una ventana emergente amarilla tras 500 ms de hover, situada abajo a la derecha del widget. |
| 5.2 | Desaparece al salir el ratón o al pulsar un botón. |

### FR-UI-6: Panel derecho (área del gráfico)

| AC | Criterio |
|----|-----------|
| 6.1 | `PanedWindow` vertical: gráfico arriba (mín. 200 px), realimentación abajo (mín. 150 px). |
| 6.2 | Deslizadores de tiempo debajo del gráfico; deslizadores Y a la derecha. |

### FR-UI-7: Ayuda de la CLI

| AC | Criterio |
|----|-----------|
| 7.1 | `--help` sale con 0 y muestra todas las opciones. |

### FR-UI-8: Argumentos de línea de comandos de la GUI

| AC | Criterio |
|----|-----------|
| 8.1 | `--port` sobrescribe el puerto serie por defecto. |
| 8.2 | `--baudrate` sobrescribe la velocidad en baudios por defecto (1000000). |

---

## Resumen de cobertura de tests

| Archivo de test | Ámbito | Recuento |
|-----------|-------|-------|
| `tests/test_hand_logic.py` | `load_app_config` (6), `servo_mapping` (3), `angle_limits` (1), `auto_extremes` (2), `speed_config` (1), `default_serial_port` (2), `ensure_data_dir` (2), `load_pose_definitions` (3), `compute_auto_positions` (6), `decompose_servo_positions` (5), `coerce_numeric` (11), `coerce_angle_degrees` (6), `coerce_bool` (6), `load_to_percent` (7), `estimate_current_from_load` (5), `format_feedback_value` (12), `get_time_window_indices` (8), `angle_rad` (3) | 89 |
| `tests/test_gui_utils.py` | `validate_name` (21), `clamp` (8), `load_config` (6), `save_config` (6) | 41 + 10 parametrizados |
| `tests/test_cmd.py` | `angle_rad` (8), `parse_step` (11), `cmd_list` (4), `load_config` (2), `apply_pose` (6), `_interruptible_sleep` (2), `auto_wait` (3), `mutual_exclusion` (1), `config_override` (2) | 41 |
| `tests/test_integration.py` | `cmd_pose` e2e (5), `cmd_sequence` e2e (6), ciclo completo de configuración (3) | 14 |
| `tests/test_system.py` | Subproceso de la CLI: `--help` (5), `--list` (9), opciones de `--help` (3), rutas de error (5) | 22 |
| `tests/test_system_hardware.py` | Hardware real: conexión (2), conexión por CLI (2), aplicación de pose (3), velocidad (2), telemetría (6), secuencia (2), recuperación de errores (1), movimiento (2), desconexión (1) — **requiere el flag `--hardware`** | 21 |
| **Total (sin hardware)** | **217 tests** |
| **Total (con hardware)** | **238 tests** |
