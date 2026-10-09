[English](../en/macOS.md) | [Deutsch](../de/macOS.md) | Español | [Français](../fr/macOS.md) | [Italiano](../it/macOS.md) | [日本語](../ja/macOS.md) | [한국어](../ko/macOS.md) | [Português (BR)](../pt-br/macOS.md) | [Português (PT)](../pt-pt/macOS.md) | [简体中文](../zh-hans/macOS.md) | [繁體中文](../zh-hant/macOS.md)

# Herramienta de depuración del servo SCS0009 — Guía para macOS

Para macOS 11 (Big Sur) y posteriores. Puntos clave: nomenclatura de los puertos serie (`cu.*` vs `tty.*`), controladores USB.

> ⚠️ **Compatibilidad: esta herramienta actualmente solo admite servos Feetech SCS0009 (serie SCS, realimentación de posición por potenciómetro, resolución de 10 bits 0-1023)**. La tabla de registros y el formato xdat están diseñados para el Feetech SCS0009; no se garantizan otras marcas/modelos.

---

## 1. Requisitos

| Dependencia | Versión |
|-----------|---------|
| Python | >= 3.8 (se recomienda 3.10+, vía Homebrew) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| SO | macOS 11+ (Apple Silicon / Intel) |

## 2. Instalar Python

Se recomienda vía Homebrew:

```bash
# Install Homebrew if missing
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

Verifica:

```bash
python3 --version
```

## 3. Instalar dependencias

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Crea el entorno virtual solo UNA VEZ**. Volver a ejecutarlo restablecerá/sobrescribirá el entorno (borrando las dependencias instaladas). Después, basta con `source .venv/bin/activate`.

## 4. ⚠️ Nomenclatura serie de macOS [Clave]

macOS coloca los dispositivos serie USB en `/dev` con **dos convenciones de nombres**:

| Prefijo | Significado | Utilizable |
|--------|---------|--------|
| `/dev/tty.usbserial-*` | estilo módem (bloqueante) | puede colgarse, no recomendado |
| `/dev/cu.usbserial-*` | estilo call/terminal (**no bloqueante**) | ✅ recomendado |

**Encuentra tu puerto:**

```bash
ls /dev/cu.*
```

Salida típica:

```
/dev/cu.usbserial-0001      # CP2102 / FTDI
/dev/cu.usbmodem141101      # onboard USB serial (Arduino/ESP32)
/dev/cu.wchusbserial1420    # CH340
```

> La herramienta prefiere automáticamente los dispositivos `cu.*`. Si especificas un puerto manualmente, usa `cu.` y no `tty.`.

## 5. Controladores USB

Los chips más habituales (CH340, CP2102, FTDI) tienen controladores integrados en macOS. Si el dispositivo no se reconoce:

```bash
system_profiler SPUSBDataType | grep -A5 -i "serial\|CH340\|CP210"
```

- **CH340**: los lotes más antiguos necesitan el controlador oficial de WCH
- En general, basta con que `ls /dev/cu.*` muestre el dispositivo

## 6. Comprobar el entorno

```bash
python setup.py
```

## 7. Lanzar la GUI

```bash
python -m src.gui.factory_calibration_tool
```

Especifica el puerto:

```bash
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 8. Flujo de trabajo de la interfaz

> Diseño de un solo panel. Aparece una barra de desplazamiento automáticamente cuando la ventana es demasiado baja; se estira para ajustarse al maximizar.

### 8.1 Conexión serie
Selecciona el puerto y la velocidad en baudios (por defecto 1M) y haz clic en **Conectar**.

### 8.2 Escanear servos
Haz clic en **Escanear servos** (ID 1-254); haz clic en una fila de la lista para rellenar automáticamente el desplegable.

### 8.3 Lectura/escritura de parámetros
- Lee los 44 registros; la selección de una fila rellena dirección/longitud/valor
- Escribe con desbloqueo/escritura/bloqueo automáticos; se muestra un aviso de éxito/fallo

### 8.4 Control de posición
Arrastra el deslizador (0-1023) o escribe un valor; aviso de movimiento completado para desactivar el par.

### 8.5 Velocidad en baudios / Restablecimiento de fábrica
Cambia la velocidad en baudios (reversión automática si falla), restablecimiento de fábrica.

### 8.6 Parámetros xdat (solo EEPROM)
Guardar servo actual → abrir copia de seguridad → restaurar en el servo.

## 9. Solución de problemas

| Problema | Solución |
|---------|----------|
| Puerto con `tty.` se cuelga | Usa el prefijo `cu.` en su lugar |
| Dispositivo no encontrado | `ls /dev/cu.*`; vuelve a enchufar; `system_profiler SPUSBDataType` |
| Interfaz china en blanco | El PingFang del sistema suele bastar; instala Noto Sans CJK si se rompe |
| Problema de permisos | macOS normalmente no necesita permisos extra; permite el acceso al terminal si se solicita |
| Falla la activación del venv | `source .venv/bin/activate` (no `.bat`) |
| Error de compilación en Apple Silicon | Python 3.10+ es nativo; evita un Python antiguo bajo Rosetta |

## 10. Línea de comandos (opcional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 11. Consejos

- **El nombre del puerto cambia**: los nombres `cu.*` pueden variar según el puerto USB; selecciónalo en el desplegable en cada arranque
- **Suspensión**: macOS puede suspenderse y perder el puerto serie; mantén el equipo despierto mientras lo usas
- **Permiso de privacidad**: si te pide "acceso a discos extraíbles", concédelo
