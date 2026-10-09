[English](../en/Windows.md) | [Deutsch](../de/Windows.md) | Español | [Français](../fr/Windows.md) | [Italiano](../it/Windows.md) | [日本語](../ja/Windows.md) | [한국어](../ko/Windows.md) | [Português (BR)](../pt-br/Windows.md) | [Português (PT)](../pt-pt/Windows.md) | [简体中文](../zh-hans/Windows.md) | [繁體中文](../zh-hant/Windows.md)

# Herramienta de depuración del servo SCS0009 — Guía para Windows

Para Windows 10 / 11. Cubre desde la instalación hasta la depuración completa del servo.

> ⚠️ **Compatibilidad: esta herramienta actualmente solo admite servos Feetech SCS0009 (serie SCS, realimentación de posición por potenciómetro, resolución de 10 bits 0-1023)**. La tabla de registros y el formato xdat están diseñados para el Feetech SCS0009; no se garantizan otras marcas/modelos.

---

## 1. Requisitos

| Dependencia | Versión | Notas |
|-----------|---------|-------|
| Python | >= 3.8 | se recomienda 3.10+, descárgalo desde [python.org](https://www.python.org/downloads/) |
| PySide6 | >= 6.0 | framework de GUI |
| pyserial | >= 3.5 | comunicación serie |
| SO | Win10 / Win11 | cualquier edición |

## 2. Instalar Python

1. Visita <https://www.python.org/downloads/>
2. Descarga el instalador de Python 3.10+
3. **Marca "Add Python to PATH"** durante la instalación (si no, python no se encontrará en el terminal)

Verifica:

```bash
python --version
```

## 3. Instalar dependencias

Instálalas en un entorno virtual para no contaminar el Python del sistema:

```bash
cd SCS0009_ServoController
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> ⚠️ **Crea el entorno virtual solo UNA VEZ**. Volver a ejecutarlo restablecerá/sobrescribirá el entorno (borrando las dependencias instaladas). Después, basta con activarlo (`activate`) cada vez.

> El prompt mostrará `(.venv)` tras la activación.

## 4. Comprobar el entorno

```bash
python setup.py
```

`[OK] 环境检查通过，可以运行项目` significa que el entorno está listo.

## 5. Conectar el hardware

1. Enchufa el adaptador USB a serie (CH340 / CP2102)
2. Conecta el controlador de servos (placa de control del brazo robótico)
3. Alimenta los servos (estándar DC 5V 5A, Pro DC 12V 5A)

Comprueba el puerto COM en el Administrador de dispositivos (`Win+X` → Administrador de dispositivos):

```
Ports (COM & LPT)
  └─ USB-SERIAL CH340 (COM3)     ← your servo port
```

> **Anota el número de COM** para seleccionarlo al arrancar.

## 6. Lanzar la GUI

```bash
python -m src.gui.factory_calibration_tool
```

O especifica el puerto:

```bash
python -m src.gui.factory_calibration_tool --port COM3
```

Lista los puertos disponibles:

```bash
python -m src.gui.factory_calibration_tool --list-ports
```

## 7. Flujo de trabajo de la interfaz

> Diseño de un solo panel. Aparece una barra de desplazamiento automáticamente cuando la ventana es demasiado baja; se estira para ajustarse al maximizar.

### 7.1 Conexión serie

- Selecciona el puerto y la velocidad en baudios (por defecto 1M), haz clic en **Conectar**
- El estado muestra `🟢 Connected`

### 7.2 Escanear servos

- Haz clic en **Escanear servos** para detectar los servos en línea (ID 1-254)
- Los resultados aparecen en la lista de servos en tiempo real (con el modelo)
- Haz clic en una fila de la lista → rellena automáticamente el desplegable de servo

### 7.3 Lectura/escritura de parámetros

- **Leer parámetros**: lee los 44 registros (EEPROM + SRAM); el registro muestra los resultados en vivo
- **Tabla de parámetros**: 5 columnas (Dirección/Registro/Valor/Memoria/Acceso), con colores según EEPROM/SRAM/DEFAULT
- **Vinculación al seleccionar fila**: haz clic en una fila → rellena automáticamente "Write Address", "Length" y "Value"
- **Escribir**: modifica el valor y luego haz clic en escribir; la herramienta desbloquea/escribe/bloquea la EEPROM automáticamente
- **Aviso de resultado de escritura**: verde "✅ Written successfully" si tiene éxito, rojo "❌ Write failed" (con el motivo) si falla

### 7.4 Control de posición

- **Deslizador**: arrástralo para ajustar la posición objetivo (0-1023); el cuadro de valor se actualiza en vivo
- **Cuadro de valor**: escribe la posición objetivo directamente; el deslizador lo sigue
- Tras el movimiento, el estado muestra "move complete, please turn off torque"

### 7.5 Velocidad en baudios / Restablecimiento de fábrica

- **Cambiar velocidad en baudios**: selecciona 38400-1000000 bps, reversión automática si falla
- **Restablecimiento de fábrica**: restaura los valores de fábrica (ID=1, baud=1M); hay que volver a escanear

### 7.6 Parámetros xdat (solo EEPROM)

1. `💾 Guardar servo actual`: guarda los parámetros EEPROM del servo actual en un archivo xdat (copia de seguridad)
2. `📂 Abrir xdat`: carga un archivo de copia de seguridad
3. `📤 Restaurar en el servo`: vuelve a escribir la copia de seguridad en el servo

## 8. Solución de problemas

| Problema | Solución |
|---------|----------|
| Sin puerto serie | Comprueba el controlador en el Administrador de dispositivos; prueba otro puerto USB; instala el controlador CH340 |
| Puerto en uso | Cierra los monitores serie; reinicia la herramienta |
| Texto chino en blanco | El sistema tiene Microsoft YaHei; instala una fuente CJK si se rompe |
| Servo no encontrado | Comprueba la alimentación/el cableado; confirma 1M de velocidad en baudios |
| Escritura fallida | Comprueba la alimentación y la conexión del servo; confirma que el registro es escribible |
| PermissionError al abrir el puerto | Asegúrate de que ningún otro proceso retiene el puerto COM |

## 9. Línea de comandos (opcional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port COM3
```
