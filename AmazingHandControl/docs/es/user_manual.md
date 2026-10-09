[English](../en/user_manual.md) | [Deutsch](../de/user_manual.md) | Español | [Français](../fr/user_manual.md) | [Italiano](../it/user_manual.md) | [日本語](../ja/user_manual.md) | [한국어](../ko/user_manual.md) | [Português (BR)](../pt-br/user_manual.md) | [Português (PT)](../pt-pt/user_manual.md) | [简体中文](../zh-hans/user_manual.md) | [繁體中文](../zh-hant/user_manual.md)

# AmazingHand Controller – Manual del usuario

> **Versión:** 2026-03-22  
> **Se aplica a:** `amazing_hand_gui.py` (GUI), `amazing_hand_cmd.py` (CLI)

---

## 1. Introducción

La GUI del AmazingHand Controller ofrece monitorización en tiempo real y control manual de una mano robótica de ocho servos accionada por actuadores Feetech SCS0009. La interfaz se divide en paneles para el control de los dedos, la gestión global, la visualización de la telemetría y el registro de actividad. Esta guía te acompaña por la instalación, la navegación y los flujos de trabajo habituales.

> **Consejo:** Mantén este manual abierto mientras usas la GUI. Los tooltips integrados en la aplicación repiten las mismas descripciones cuando pasas el ratón por encima de los controles.

![AmazingHand hardware with controller connected](../en/screenshots/hand_overview.png)

---

## 2. Lista de inicio rápido

1. **Instala las dependencias** (una vez por entorno):
   ```bash
   python -m pip install -r requirements.txt
   ```
2. **Alimenta el hardware:** conecta la fuente de 5 V a la cadena de servos y enchufa el adaptador serie USB.
3. **Lanza la GUI:**
   ```bash
   python amazing_hand_gui.py
   ```
4. **Conéctate al controlador:** elige el **Puerto** serie (p. ej., `COM9`) y haz clic en **▶ Conectar**.
5. **Verifica la telemetría:** busca actualizaciones en vivo en el gráfico y la tabla de realimentación.

---

## 3. Vista general de la pantalla

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

### 3.1 Los paneles de un vistazo

| Panel | Ubicación | Propósito |
|-------|----------|---------|
| **Controles de dedo** | Izquierda, arriba (3 dedos) + abajo a la derecha (Pulgar) | Deslizadores individuales y selectores de velocidad para cada par de dedo. Incluye indicadores de mimic y LED de estado por dedo. |
| **Pila de control derecha** | Izquierda, abajo a la derecha | Ajustes de conexión, controles globales, gestión de poses y reproductor de secuencias. |
| **Panel de telemetría** | Derecha | Gráficos en tiempo real con deslizadores de zoom/desplazamiento y una tabla de realimentación configurable. |
| **Registro de ejecución** | Abajo | Flujo de mensajes de estado, avisos y progreso de las secuencias. |

---

## 4. Guía detallada de los paneles

### 4.1 Panel de control de dedos (columna izquierda)

Cada widget de dedo controla un par de servos (posición + desplazamiento lateral):

- **Conmutador de modo:** alterna entre **Auto** (deslizadores base + desplazamiento) y **Raw** (objetivos de servo directos).
- **LED de estado:** gris (inactivo), verde (en movimiento), rojo (bloqueo potencial, según carga vs. objetivo).
- **Deslizador de posición:** 0–110° (abierto a cerrado). La rueda del ratón ajusta de 1° en 1°; al arrastrar se ajusta con rapidez.
- **Deslizador lateral:** ±40° para ajustes laterales. El deslizador lateral del pulgar está **invertido** para que la dirección física coincida con la orientación anatómica de la mano — arrastrar a la derecha mueve el pulgar en sentido positivo respecto a su montaje de hardware.
- **Selector de velocidad:** desplegable 1–6 que controla la velocidad de movimiento de ambos servos del par del dedo.
- **Casilla Mimic:** refleja los movimientos de cerrar/abrir desde un dedo de origen para un movimiento coordinado mientras está en modo Auto.

**Modos de dedo: Auto vs Raw**

- **Modo Auto** (por defecto) expone el deslizador de cerrar/abrir, el deslizador de desplazamiento lateral, el desplegable de velocidad y el botón de centrar. La GUI combina esos dos valores de deslizador en comandos de servo usando los extremos calibrados almacenados en `data/hand_config.yaml`, de modo que el par sigue poses naturales de dedo sin cálculos manuales de servo. Mimic sigue activo aquí — habilítalo en varios dedos para moverlos en sincronía con el dedo que estés ajustando.
- **Modo Raw** sustituye los controles Auto por dos deslizadores verticales etiquetados por servo. Muévelos para comandar directamente los ángulos de servo subyacentes cuando pruebes los topes finales, valides la calibración o diagnostiques problemas de la mecánica. El botón de centrar y la casilla Mimic se deshabilitan porque Raw se salta la lógica de mezcla automática; los atajos de teclado siguen funcionando, con Arriba/Abajo controlando el servo 1 e Izquierda/Derecha controlando el servo 2. Raw usa el último valor de velocidad seleccionado, así que fija las velocidades antes de cambiar de modo si necesitas una tasa de movimiento concreta.

**Cómo calcula el modo Auto los objetivos de servo**

- El valor del deslizador de cerrar/abrir se limita a `limits.base_min/base_max` y luego se normaliza (`t = base / base_max`) para interpolar entre las poses abierta y cerrada de `auto_extremes` para cada lado del dedo.
- El deslizador de desplazamiento lateral se limita a `limits.side_min/side_max` y se convierte en un factor de mezcla (`u`). Los desplazamientos negativos interpolan desde la pose central hacia `left_open`/`left_closed`; los desplazamientos positivos interpolan hacia los extremos del lado derecho.
- Sin desplazamiento lateral, ambos servos reciben simplemente el valor del deslizador base. Los objetivos finales de los servos se limitan a `limits.servo_min/servo_max` antes de emitirse, manteniendo los movimientos dentro de los límites seguros calibrados.

Los atajos de teclado complementan los deslizadores (documentados en §5.2).

![Finger control panel with per-finger sliders and status indicators](../en/screenshots/finger_control_frame.png)

### 4.2 Pila de control global (a la derecha del panel de dedos)

1. **Conexión:** selección de puerto y velocidad en baudios (ambos desplegables están deshabilitados mientras hay conexión), botones de conectar/desconectar. La barra de estado de abajo informa del éxito o de los errores.
2. **Controles globales:**
   - **Abrir todo / Cerrar todo / Centrar todo** – se aplican a todos los dedos al instante.
   - **Desplegable de velocidad global** – fija los selectores de velocidad por dedo a un valor común (1–6).
3. **Gestión de poses:** guarda, carga, aplica y elimina poses almacenadas en `data/hand_config.yaml`.
   - Disposición: `Pose: [desplegable]  ✓ Aplicar  🗑 Eliminar  Nombre: [campo]  ➕ Añadir nuevo`
   - **🗑 Eliminar** elimina la pose seleccionada de forma permanente (se muestra un diálogo de confirmación).
4. **Reproductor de secuencias:** selecciona y ejecuta animaciones de varios pasos, con bucle opcional. Accede al diálogo del gestor de secuencias con **🔧 Gestionar**.

![Connection, global controls, pose management, and sequence player stack](../en/screenshots/control_frame.png)

### 4.3 Panel de telemetría y realimentación (columna derecha)

- **Fila de controles:**
  - Pausar/reanudar las actualizaciones del gráfico.
  - Conmutador de ventana rodante.
  - Selección de métrica (posición, carga, velocidad, temperatura, voltaje, indicador de movimiento).
  - Conmutador de modo (Multi-Servo vs. Scope) con selector de servo para el segundo.
  - Desplegable de visibilidad de servos con ayudas "Todas/Ninguna/Limpiar".
  
![Display mode, metric selection, and scope controls](../en/screenshots/chart_mode_controls.png)

![Display menu for choosing telemetry metrics](../en/screenshots/chart_select_display_values.png)

![Servo visibility menu with quick actions](../en/screenshots/chart_servos_selection.png)

#### Modos del gráfico

- **Multi-Servo** (por defecto) mantiene en el gráfico todas las trazas de servos habilitadas. Usa el desplegable **Servos** para activar/desactivar grupos rápidamente y comparar movimiento o carga entre dedos.
- **Scope** activa el selector **Scope Servo**, que te permite centrarte en un único canal mientras sigues usando las mismas casillas de métricas. Combina este modo con el menú de visibilidad de servos (p. ej., ocultar todos y luego volver a habilitar el servo del scope) para obtener una vista tipo osciloscopio sin otras trazas.
- Independientemente del modo, la tabla de telemetría sigue mostrando todos los servos, para que puedas correlacionar el gráfico enfocado con la instantánea de datos más amplia.
- **Área del gráfico:** gráfico de Matplotlib que muestra la telemetría seleccionada. Zoom mediante deslizadores:
  - **Y Zoom / Pan:** escalado y desplazamiento vertical.
  - **Time Zoom / Pan:** enfoque en el historial reciente o en muestras más antiguas.
- **Tabla de realimentación:** rejilla desplazable que resume Objetivo, Posición, Velocidad, Carga, Voltaje, Temperatura, Estado e indicadores de movimiento de cada servo.

![Chart controls with zoom/pan sliders and telemetry traces](../en/screenshots/chart_frame.png)

![Feedback table showing live servo metrics](../en/screenshots/feedback_frame.png)

### 4.4 Registro de ejecución y barra de estado

Situado debajo del panel de dedos, el registro anota las operaciones en orden cronológico. La barra de estado muestra la última acción o aviso.

![Execution log and current status bar](../en/screenshots/log_and_last_action_frame.png)

---

## 5. Manejo de la mano

### 5.1 Conexión al hardware

1. Alimenta los servos y conecta el adaptador USB.
2. Lanza la GUI y confirma que se autoselecciona el **Puerto** correcto (`COM*` en Windows o `/dev/tty*` en Linux/macOS).
3. Haz clic en **▶ Conectar**. Si funciona, cambian los estados de los botones y se actualiza la barra de estado.
4. Si la conexión falla, revisa el cableado, la alimentación y la asignación de puerto.

### 5.2 Control manual y atajos

- Selecciona un dedo con las teclas **1–4** (1 = Anular, 2 = Medio, 3 = Índice, 4 = Pulgar).
- **Teclas de flecha:** Arriba/Abajo ajustan la posición; Izquierda/Derecha ajustan el desplazamiento lateral.
- Mantener **Shift** multiplica el tamaño del paso por 5; **Ctrl** lo multiplica por 10.
- **Q / E:** cierran / abren del todo el dedo seleccionado.
- **C:** centra el desplazamiento lateral.
- Los deslizadores en pantalla reflejan la entrada de teclado en tiempo real.

![Manual finger control panel with keyboard shortcut overlay](../en/screenshots/manual_finger_control_frame.png)

![Example of fully closing a finger using controls](../en/screenshots/close_finger.png)

![Example of lateral movement adjustment](../en/screenshots/move_finger.png)

### 5.3 Ajuste de velocidades

- El desplegable de velocidad por dedo (1 = lento, 6 = rápido) controla la velocidad de los servos.
- El selector **Velocidad global** sincroniza las velocidades de todos los dedos.
- Observa los cambios de velocidad en la tabla de realimentación (fila **Velocidad**) durante el movimiento.

### 5.4 Aplicar y eliminar poses

1. Coloca las posiciones de los dedos con los deslizadores o los atajos de teclado.
2. En **Gestión de poses**, escribe un nombre único y haz clic en **➕ Añadir nuevo**.
3. Para aplicar, selecciona la pose en el desplegable y haz clic en **✓ Aplicar**.
4. Para eliminar, selecciona la pose en el desplegable y haz clic en **🗑 Eliminar**. Un diálogo de confirmación evita el borrado accidental.

> Las poses guardan solo posiciones de servo; las velocidades las determinan los ajustes de la GUI en tiempo de ejecución.

### 5.5 Construir y ejecutar secuencias

1. Haz clic en **🔧 Gestionar** en el Reproductor de secuencias.
2. En el diálogo:
   - Usa la lista **Poses disponibles** para añadir pasos (doble clic o pulsa **➕ Añadir**).
   - Ajusta las velocidades por dedo con los cuadros numéricos y fija retardos opcionales por paso.
   - Inserta intervalos de espera dedicados con **⏱ Retardo**.
   - Reordena los pasos con los botones ↑/↓.
   - Introduce un nombre y haz clic en **💾 Guardar secuencia**.
   - Haz clic en **▶ Ejecutar** para probar sin guardar.
3. De vuelta en la ventana principal, selecciona la secuencia y pulsa **▶ Reproducir**. Habilita **Loop** para reproducción continua.

> Las definiciones de secuencias están en `data/hand_config.yaml` bajo la clave `sequences`. Los bucles se controlan en tiempo de ejecución, no en el YAML.

![Sequence manager dialog with available poses and sequence builder](../en/screenshots/sequences_editor.png)

### 5.6 Monitorizar la telemetría

- Asegúrate de que las métricas deseadas están marcadas en el menú **Display**.
- Usa los deslizadores de zoom/desplazamiento para centrarte en los segmentos de interés.
- Pasa el ratón por encima de los elementos del gráfico (interacciones estándar de Matplotlib) para consultar los valores.
- La tabla de realimentación se actualiza de forma asíncrona; las celdas resaltadas indican cambios recientes.
- Si el gráfico se satura, haz clic en **⌫ Limpiar** para restablecer los datos recogidos.

---

## 6. Interfaz de línea de comandos (`amazing_hand_cmd.py`)

La CLI te permite aplicar poses y reproducir secuencias directamente desde un terminal sin lanzar la GUI. Lee el mismo archivo `data/hand_config.yaml`.

### 6.1 Uso básico

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

### 6.2 Opciones

| Opción | Por defecto | Descripción |
|--------|---------|-------------|
| `--pose NAME` | – | Aplica la pose indicada y sale |
| `--sequence NAME` | – | Reproduce la secuencia indicada y sale |
| `--list` | – | Lista todas las poses y secuencias |
| `--loop` | desactivado | Repite la secuencia continuamente hasta Ctrl+C |
| `--port PORT` | `/dev/ttyACM0` (Linux) / `COM9` (Win) | Sobrescribe el puerto serie |
| `--baudrate N` | `1000000` | Sobrescribe la velocidad en baudios |
| `--config PATH` | `data/hand_config.yaml` | Ruta a un archivo de configuración alternativo |

### 6.3 Notas

- El par se **habilita** al conectar y se **deshabilita** al salir, para que los servos se relajen al terminar el script.
- Las velocidades y los retardos por paso se comportan igual que en el reproductor de secuencias de la GUI.
- El flag `--loop` solo puede usarse junto con `--sequence`.

---

## 7. Solución de problemas

| Síntoma | Acción sugerida |
|---------|-----------------| 
| **No se lista ningún puerto serie** | Vuelve a enchufar el adaptador USB, instala los controladores o reinicia la GUI. |
| **El botón Conectar está en gris** | Ya estás conectado; haz clic primero en **⏹ Desconectar**. |
| **Interfaz lenta al redimensionar** | Las optimizaciones de rendimiento (redimensionado con antirrebote, redibujados limitados) lo minimizan, pero cerrar ventanas innecesarias puede ayudar. |
| **La secuencia no mueve todos los dedos** | Comprueba las velocidades de cada paso y asegúrate de que cada pose contiene los ocho valores de servo. |
| **El indicador de bloqueo persiste** | Inspecciona posibles obstrucciones mecánicas; el estado de bloqueo se dispara cuando el objetivo y la posición difieren mucho sin que haya movimiento. |

---

## 8. Apéndice

### 8.1 Estructura de archivos

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

### 8.2 Enlaces útiles

- [AmazingHand (proyecto oficial)](https://github.com/pollen-robotics/AmazingHand)
- [Feetech Servo Debug Tool](https://github.com/Robot-Maker-SAS/FeetechServo/tree/main/feetech%20debug%20tool%20master/FD1.9.8.2)
- [Tutorial de identificación de servos](https://www.robot-maker.com/forum/tutorials/article/168-brancher-et-controler-le-servomoteur-feetech-sts3032-360/)

---

## 9. Historial de revisiones

| Fecha | Autor | Notas |
|------|--------|-------|
| 2026-03-22 | Ingo | Se añadió la sección de la CLI (`amazing_hand_cmd.py`); actualización de la versión del manual. |
| 2026-03-21 | Ingo | Actualización de la disposición de paneles: intercambio Anular/Índice, Pulgar movido a la derecha, pila de control movida a la izquierda. Deslizador lateral del pulgar invertido. Botón de eliminar pose añadido entre Aplicar y Nombre. Los desplegables de Puerto y Velocidad en baudios ahora se bloquean mientras hay conexión. El atajo de teclado 1–4 ahora asigna Anular/Medio/Índice/Pulgar. |
| 2025-11-25 | Ingo | Se añadió una galería de capturas ampliada, explicaciones de los modos del gráfico y recorridos de paneles renovados. |
| 2025-11-25 | Ingo | Manual inicial que cubre los paneles de la interfaz, los flujos de trabajo y el uso de la telemetría. |
