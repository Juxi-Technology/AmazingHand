[English](../en/Linux.md) | [Deutsch](../de/Linux.md) | Español | [Français](../fr/Linux.md) | [Italiano](../it/Linux.md) | [日本語](../ja/Linux.md) | [한국어](../ko/Linux.md) | [Português (BR)](../pt-br/Linux.md) | [Português (PT)](../pt-pt/Linux.md) | [简体中文](../zh-hans/Linux.md) | [繁體中文](../zh-hant/Linux.md)

# Herramienta de depuración del servo SCS0009 — Guía para Linux

Para Ubuntu / Debian / otras distribuciones habituales. Puntos clave: permisos del puerto serie (dialout), detección del dispositivo USB a serie.

> ⚠️ **Compatibilidad: esta herramienta actualmente solo admite servos Feetech SCS0009 (serie SCS, realimentación de posición por potenciómetro, resolución de 10 bits 0-1023)**. La tabla de registros y el formato xdat están diseñados para el Feetech SCS0009; no se garantizan otras marcas/modelos.

---

## 1. Requisitos

| Dependencia | Versión |
|-----------|---------|
| Python | >= 3.8 (se recomienda 3.10+) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| SO | Ubuntu 20.04+ / Debian 11+ |

Fuentes chinas (necesarias para la interfaz en chino):

```bash
sudo apt install fonts-noto-cjk
```

Fuentes de iconos emoji (para ✅⚠️ etc. en los registros):

```bash
sudo apt install fonts-noto-color-emoji
```

## 2. Instalar las dependencias de Python

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Crea el entorno virtual solo UNA VEZ**. Volver a ejecutarlo restablecerá/sobrescribirá el entorno (borrando las dependencias instaladas). Después, basta con `source .venv/bin/activate`.

> Si pip informa de "externally-managed-environment", usa un venv o `pip install --break-system-packages -r requirements.txt`.

## 3. ⚠️ Permiso del puerto serie (dialout) [Obligatorio]

Por defecto, los usuarios normales **no pueden acceder** a `/dev/ttyUSB*` / `/dev/ttyACM*`. Añade tu usuario al grupo `dialout`:

```bash
sudo usermod -a -G dialout $USER
```

**Cierra la sesión y vuelve a entrar** (o reinicia). Verifica:

```bash
groups
# output should include dialout
```

> Algunas distribuciones usan `uucp` (Arch) o `tty`.

## 4. Identificar el dispositivo serie USB

Tras enchufarlo:

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Salida típica:

```
/dev/ttyUSB0   # CH340 / CP2102 / PL2303
/dev/ttyACM0   # native USB serial (Arduino/ESP32 onboard)
```

## 5. Comprobar el entorno

```bash
python setup.py
```

## 6. Lanzar la GUI

```bash
python -m src.gui.factory_calibration_tool
```

Especifica el puerto:

```bash
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

> Si solo existe un puerto, la herramienta lo usa directamente.

## 7. Flujo de trabajo de la interfaz

> Diseño de un solo panel. Aparece una barra de desplazamiento automáticamente cuando la ventana es demasiado baja; se estira para ajustarse al maximizar.

### 7.1 Conexión serie
Selecciona el puerto y la velocidad en baudios (por defecto 1M) y haz clic en **Conectar**.

### 7.2 Escanear servos
Haz clic en **Escanear servos** (ID 1-254); haz clic en una fila de la lista para rellenar automáticamente el desplegable.

### 7.3 Lectura/escritura de parámetros
- Lee los 44 registros (EEPROM + SRAM); la selección de una fila rellena dirección/longitud/valor
- Escribe con desbloqueo/escritura/bloqueo automáticos; se muestra un aviso de éxito/fallo

### 7.4 Control de posición
Arrastra el deslizador (0-1023) o escribe un valor; aviso de movimiento completado para desactivar el par.

### 7.5 Velocidad en baudios / Restablecimiento de fábrica
Cambia la velocidad en baudios (reversión automática si falla), restablecimiento de fábrica.

### 7.6 Parámetros xdat (solo EEPROM)
Guardar servo actual → abrir copia de seguridad → restaurar en el servo.

## 8. Solución de problemas

| Problema | Solución |
|---------|----------|
| **Permission denied: /dev/ttyUSB0** | No estás en el grupo dialout, ver la sección 3; o `sudo chmod 666 /dev/ttyUSB0` (temporal) |
| Sin puerto serie | `ls /dev/ttyUSB* /dev/ttyACM*`; `lsusb` para confirmar el dispositivo |
| El nombre del dispositivo cambia | la numeración de ttyUSB depende del orden de conexión; usa una regla udev o selecciónalo en cada arranque |
| Interfaz china en blanco | Instala `fonts-noto-cjk` |
| Los emoji aparecen como cajas | Instala `fonts-noto-color-emoji` |
| Falla `pip install` | Usa un venv; o `--break-system-packages` |
| La aplicación no arranca | Comprueba `python3 --version`; `pip list` para las dependencias |

## 9. Línea de comandos (opcional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

## 10. Avanzado: nombre de dispositivo fijo con udev (opcional)

Crea `/etc/udev/rules.d/99-servo.rules` para fijar el nombre del dispositivo por ID de USB:

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyServo"
```

Después, `ls -l /dev/ttyServo`. Obtén el ID del fabricante con `lsusb`.
