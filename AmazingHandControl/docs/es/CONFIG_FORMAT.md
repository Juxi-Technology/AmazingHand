[English](../en/CONFIG_FORMAT.md) | [Deutsch](../de/CONFIG_FORMAT.md) | Español | [Français](../fr/CONFIG_FORMAT.md) | [Italiano](../it/CONFIG_FORMAT.md) | [日本語](../ja/CONFIG_FORMAT.md) | [한국어](../ko/CONFIG_FORMAT.md) | [Português (BR)](../pt-br/CONFIG_FORMAT.md) | [Português (PT)](../pt-pt/CONFIG_FORMAT.md) | [简体中文](../zh-hans/CONFIG_FORMAT.md) | [繁體中文](../zh-hant/CONFIG_FORMAT.md)

# Formato de configuración de la mano (YAML)

Este documento describe los archivos de configuración YAML que usa AmazingHand.

| Archivo | Propósito |
|------|---------|
| `data/hand_config.yaml` | Poses y secuencias (creados/editados por la GUI y la CLI) |
| `data/config.yaml` | Ajustes de la aplicación (puerto serie, límites de servo, velocidades, rutas) |

---

## `data/config.yaml` – Ajustes de la aplicación

Lo carga la GUI al iniciarse. Si falta el archivo, se usan los valores por defecto integrados.
La CLI usa los mismos valores por defecto (sobrescribibles con `--port` / `--baudrate`).

### Estructura completa

```yaml
# Serial port settings
serial:
  port_windows: COM9          # Default port on Windows
  port_linux: /dev/ttyACM0   # Default port on Linux/macOS
  baudrate: 1000000           # Default baud rate
  baudrate_options: [9600, 115200, 1000000]  # Shown in GUI dropdown

# Servo assignments — [servo1_id, servo2_id] per finger
# servo1 (odd ID)  = position axis (open/close)
# servo2 (even ID) = side axis (left/right)
servos:
  ring:    [1, 2]
  middle:  [3, 4]
  pointer: [5, 6]
  thumb:   [7, 8]
  all_ids: [1, 2, 3, 4, 5, 6, 7, 8]

# Servo angle limits (degrees)
limits:
  servo_min: -40   # Absolute minimum for any servo command
  servo_max: 110   # Absolute maximum for any servo command
  base_min: 0      # Open/close slider minimum
  base_max: 110    # Open/close slider maximum
  side_min: -40    # Left/right slider minimum
  side_max: 40     # Left/right slider maximum

# Movement speeds (1–6 scale, where 6 is fastest)
speeds:
  default: 3
  min: 1
  max: 6

# Auto-mode blending extremes — [servo1_deg, servo2_deg]
# Used to interpolate combined position+side values in Auto mode
auto_extremes:
  left_open:    [32, -40]
  right_open:   [-40, 32]
  left_closed:  [110, 110]
  right_closed: [110, 110]
  center_open:  [0, 0]
  center_closed: [110, 110]

# File paths (relative to project root)
paths:
  poses_sequences_file: data/hand_config.yaml
```

### Notas
- Todas las claves son opcionales — las claves ausentes recurren a los valores por defecto integrados que se muestran arriba.
- **No** guardes poses ni secuencias aquí; esas van en `data/hand_config.yaml`.
- Reinicia la GUI después de editar este archivo para que los cambios surtan efecto.

---

## `data/hand_config.yaml` – Poses y secuencias

Creado y editado por la GUI y la CLI. Compartido entre ambas herramientas.

### Estructura YAML

```yaml
poses:
  <pose_name>:
    positions: [pos1, pos2, pos3, pos4, pos5, pos6, pos7, pos8]

sequences:
  <sequence_name>:
    steps:
      - "<pose_name>:speed1,speed2,...,speed8|delay"
      - "SLEEP:duration"
```

## Poses

Cada pose define una posición completa de la mano con 8 valores de servo.

### Formato
```yaml
poses:
  pose_name:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
```

### Array de posiciones
- **8 valores** que representan las posiciones de los servos en grados
- **Asignación de servos**:
  - Servo 1: posición del dedo índice (0=abierto, 110=cerrado)
  - Servo 2: lateral del dedo índice (-20=izquierda, 0=centro, +20=derecha)
  - Servo 3: posición del dedo medio
  - Servo 4: lateral del dedo medio
  - Servo 5: posición del dedo anular
  - Servo 6: lateral del dedo anular
  - Servo 7: posición del pulgar
  - Servo 8: lateral del pulgar

- **Rango del deslizador Abrir/Cerrar**: 0-110° por dedo (0=abierto, 110=cerrado)
- **Rango del deslizador lateral**: -40° (izquierda) a +40° (derecha)
- **Valores de servo almacenados**: como el YAML guarda los valores combinados (base ± side), espera que los comandos de servo reales caigan aproximadamente entre -40° y 150°
- **Nota**: los servos con número par (2,4,6,8) tienen los ángulos invertidos en el hardware

### Reglas de nombres
- Se permiten letras, números y guiones bajos
- **Caracteres prohibidos**: `: { } [ ] , & * # ? | - < > = ! % @ \` " '`
- Máximo 50 caracteres
- Distingue mayúsculas y minúsculas

### Ejemplo
```yaml
poses:
  open:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
  close:
    positions: [110, 0, 110, 0, 110, 0, 110, 0]
  peace:
    positions: [0, 0, 110, 0, 0, 0, 0, 0]
```

## Secuencias

Las secuencias definen animaciones de varios pasos con velocidades y retardos por servo individuales.

### Formato
```yaml
sequences:
  sequence_name:
    steps:
      - "pose_name:speed1,speed2,speed3,speed4,speed5,speed6,speed7,speed8|delay"
      - "SLEEP:duration"
```

### Formato de paso

**Pose con velocidades individuales y retardo:**
```
"pose_name:s1,s2,s3,s4,s5,s6,s7,s8|delay"
```
- `pose_name`: nombre de la pose que se ejecuta
- `s1-s8`: velocidad individual de cada servo (1-6, donde 6 es la más rápida)
- `delay`: tiempo de espera tras completarse el movimiento (p. ej., `2.0s`)

**Pose con velocidades por defecto:**
```
"pose_name:3,3,3,3,3,3,3,3|2.0s"
```

**Sleep/pausa:**
```
"SLEEP:1.5s"
```
- Pausa durante la duración especificada sin mover los servos

### Valores de velocidad
- Rango: 1 (la más lenta) a 6 (la más rápida)
- Controla la velocidad de movimiento del servo
- Cada servo puede tener una velocidad distinta en un paso

### Control de bucle
- El ajuste de bucle **NO** se guarda en el YAML
- Se controla con una casilla de verificación en el reproductor de secuencias de la GUI
- Permite una reproducción flexible sin editar el YAML

### Ejemplo
```yaml
sequences:
  demo:
    steps:
      - "open:3,3,3,3,3,3,3,3|2.0s"
      - "close:3,3,3,3,3,3,3,3|2.0s"
      - "open:3,3,3,3,3,3,3,3|1.0s"
  
  wave:
    steps:
      - "open:5,5,5,5,5,5,5,5|0.5s"
      - "SLEEP:0.3s"
      - "close:5,5,5,5,5,5,5,5|0.5s"
      - "SLEEP:0.3s"
```

## Gestión de poses y secuencias

### Mediante la GUI (`amazing_hand_gui.py`)

**Poses:**
1. Coloca los dedos con los deslizadores o el teclado
2. Introduce un nombre en el campo "Name:"
3. Haz clic en "➕ Add New" para guardar

**Secuencias:**
1. Haz clic en el botón "Manage" de la sección Sequence Player
2. Construye la secuencia en el diálogo:
   - Selecciona poses y velocidades
   - Añade retardos entre pasos
   - Reordena con los botones ↑/↓
3. Introduce el nombre de la secuencia y haz clic en "💾 Save"

**Ejecución:**
- Selecciona la secuencia del desplegable
- Marca "Loop" si quieres reproducción continua
- Haz clic en "▶ Play"

### Mediante la CLI (`amazing_hand_cmd.py`)

**Listar todas las poses y secuencias:**
```bash
python amazing_hand_cmd.py --list
```

**Ejecutar una pose:**
```bash
python amazing_hand_cmd.py --pose open
```

**Ejecutar una secuencia:**
```bash
python amazing_hand_cmd.py --sequence demo
```

**Ejecutar con bucle:**
```bash
python amazing_hand_cmd.py --sequence wave --loop
```

**Usar una configuración alternativa:**
```bash
python amazing_hand_cmd.py --pose open --config /path/to/hand_config.yaml
```

## Edición manual

Puedes editar `data/hand_config.yaml` directamente:

1. **Respeta la sintaxis YAML** - la indentación debe ser consistente (2 o 4 espacios)
2. **Usa el formato de array en línea** para las posiciones:
   ```yaml
   positions: [0, 0, 0, 0, 0, 0, 0, 0]
   ```
3. **Entrecomilla los pasos de secuencia** para conservar los caracteres especiales:
   ```yaml
   steps:
     - "open:3,3,3,3,3,3,3,3|2.0s"
   ```
4. **Valida los nombres** - evita los caracteres prohibidos
5. **Reinicia la GUI** para recargar los cambios
6. **Haz copias de seguridad** antes de ediciones importantes

## Validación

La GUI y la CLI validan automáticamente:
- Nombres de poses/secuencias (caracteres prohibidos)
- Sintaxis YAML al guardar
- Longitud del array de posiciones (debe ser 8)

Los nombres inválidos se rechazan con un mensaje de error que muestra los caracteres prohibidos.

## Licencia

Copyright 2026 AmazingHand Control Contributors

Con licencia Apache License, Version 2.0
