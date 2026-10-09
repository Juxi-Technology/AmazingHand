[English](../en/Windows_Tutorial.md) | [Deutsch](../de/Windows_Tutorial.md) | Español | [Français](../fr/Windows_Tutorial.md) | [Italiano](../it/Windows_Tutorial.md) | [日本語](../ja/Windows_Tutorial.md) | [한국어](../ko/Windows_Tutorial.md) | [Português (BR)](../pt-br/Windows_Tutorial.md) | [Português (PT)](../pt-pt/Windows_Tutorial.md) | [简体中文](../zh-hans/Windows_Tutorial.md) | [繁體中文](../zh-hant/Windows_Tutorial.md)

# Tutorial de seguimiento de manos de AmazingHand (mano diestra) · Windows

Este tutorial cubre el Demo oficial de AmazingHand (la mano diestra de Pollen Robotics) con scripts de despliegue en un solo clic.
Ejecuta los scripts en orden numérico. **Todos los scripts están en `Demo\Windows_Deploy_Scripts\`: haz doble clic para ejecutarlos.**

---

## Índice

1. [Preparación del hardware](#1-preparación-del-hardware)
2. [Configuración del entorno (script 1)](#2-configuración-del-entorno-script-1)
3. [Cableado](#3-cableado)
4. [Configuración del puerto serie (script 2)](#4-configuración-del-puerto-serie-script-2)
5. [Despliegue del código (script 3)](#5-despliegue-del-código-script-3)
6. [Ejecutar el demo (script 4)](#6-ejecutar-el-demo-script-4)
7. [Limpieza del proyecto (script 0)](#7-limpieza-del-proyecto-script-0)
8. [Solución de problemas y notas](#8-solución-de-problemas-y-notas)
9. [Estructura del código](#9-estructura-del-código)

---

## 1. Preparación del hardware

| Elemento | Requisito |
|---|---|
| Mano diestra | Derecha / Izquierda / Ambas |
| Placa controladora de servos | Externa, USB al PC |
| Alimentación | **Al menos 5V 4A** (solo con USB no basta, usa una fuente de alimentación externa) |
| Cámara | Integrada o webcam USB |

> Los archivos del modelo (URDF, etc.) pueden verse o descargarse en [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e).

---

## 2. Configuración del entorno (script 1)

**Haz doble clic en `1-Install_Env.bat`**: automáticamente:

1. **Comprueba las herramientas de compilación de MSVC** (cl.exe), necesarias para compilar Rust. Si faltan, instala
   Visual Studio 2022 Build Tools con la carga de trabajo «Desktop development with C++» y vuelve a abrir el terminal.
2. **Instala Rust** (rustup + toolchain estable-msvc)
3. **Configura el mirror tuna de cargo** (`C:\Users\<you>\.cargo\config.toml`) para acelerar las descargas de crates
4. **Instala uv** (gestor de paquetes de Python)
5. **Instala dora-cli 0.5.0** (`cargo install`; la primera compilación tarda ~10–20 min, ten paciencia)
6. **Instala el paquete pip dora-rs** (opcional; también se instala en el venv durante el despliegue)

> **Importante**: **cierra y vuelve a abrir el terminal** después del script para que las variables de entorno surtan efecto.
> Las descargas pueden ir lentas según tu red; espera, no interrumpas.

### Instalación manual (si el script no es utilizable)

- **Rust**: <https://www.rust-lang.org/tools/install> — usa rustup-init.exe, toolchain MSVC por defecto.
  - PATH: añade `%USERPROFILE%\.cargo\bin`
- **uv**: PowerShell: `irm https://astral.sh/uv/install.ps1 | iex`
  - PATH: añade `%USERPROFILE%\.local\bin`
- **dora-cli**: `cargo install dora-cli --version 0.5.0`

### Mirror tuna de cargo (config.toml)

```
[source.crates-io]
replace-with = "tuna"

[source.tuna]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[registries.tuna]
index = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[http]
check-revoke = false
```

> Usa el **índice sparse** (el de arriba), NO el mirror de tipo repositorio git: el mirror git primero descarga ~1 GB de índice y a menudo se queda colgado en `Updating 'tuna' index`.

---

## 3. Cableado

- Conecta la placa controladora de servos al PC por USB, **aliméntala con una fuente externa de 5V 4A**
- Localiza el puerto: **Device Manager → Ports (COM & LPT)**, por ejemplo `COM11`

---

## 4. Configuración del puerto serie (script 2)

**Haz doble clic en `2-Setup_Serial.bat`** (la lógica está en `2-Setup_Serial.ps1`):

1. "Connect the driver board" → pulsa Enter para escanear
2. Se listan los puertos COM detectados (con los nombres de dispositivo)
3. Un solo puerto: pulsa Enter para confirmar; varios: escribe el índice
4. Escribe `--serialport` en los 3 archivos yml de dataflow y el puerto por defecto en `AHControl\src\main.rs`
5. Los archivos originales se guardan como copia de seguridad con la extensión `.bak`

> Si vuelves a conectar el cable USB, el número de COM puede cambiar: vuelve a ejecutar este script.

---

## 5. Despliegue del código (script 3)

**Haz doble clic en `3-Deploy_Demo.bat`** — automáticamente:

1. Inicia el daemon de dora (`dora up`)
2. Crea un venv de Python 3.12 (`uv venv --python 3.12`)
3. Activa el venv
4. Compila el nodo Rust AHControl (`cargo build --release`, ~10 min la primera vez)
5. Sincroniza las dependencias de AHSimulation y HandTracking (`uv sync`)
6. Instala a la fuerza mediapipe==0.10.14 (escollo conocido, mecanismo de reserva)

> Despliega una sola vez. Si lo vuelves a ejecutar, preguntará si quieres reconstruir el venv.

---

## 6. Ejecutar el demo (script 4)

**Haz doble clic en `4-Run_Demo.bat`** — menú interactivo:

```
============================================
  Select a run mode:
============================================
   1 - Simulation (webcam hand tracking)
   2 - Real hardware
   q - Quit
============================================
Enter number [1/2/q]:
```

- **1**: Simulación: los gestos de la webcam controlan dos manos simuladas
- **2**: Hardware real: submenú para mano derecha / izquierda / ambas

```
============================================
  Real hardware - select the hand:
============================================
   1 - Right hand
   2 - Left hand
   3 - Both hands
   b - Back to main menu
============================================
```

A continuación ejecuta `dora build` + `dora run`. Se abre una ventana de cámara; haz gestos con la mano para mover la(s) mano(s) en tiempo real. **Ctrl+C para detener**. Cuando termina el dataflow, pulsa Enter para volver al menú y elegir otro modo, o `q` para salir.

> En la primera ejecución, Windows puede pedir permiso para la cámara; haz clic en «Allow».

---

## 7. Limpieza del proyecto (script 0)

**Haz doble clic en `0-Cleanup_Project.bat`** y escribe `Y` para confirmar:

1. Detiene el daemon de dora
2. Elimina los 3 entornos virtuales (`.venv`)
3. Elimina la salida de compilación de Rust (`Demo\target`)
4. Elimina `__pycache__`, las copias de seguridad `.bak`, los logs y `Demo\out` (logs de dora)
5. **Restaura el puerto por defecto** (`--serialport /dev/ttyACM0`) y elimina los restos de COM de esta máquina

> Después de la limpieza puedes copiar toda la carpeta `AmazingHand-main` a otra máquina: queda limpia y portable.
> En la nueva máquina, solo tienes que ejecutar 1 → 2 → 3 → 4 en orden.

---

## 8. Solución de problemas y notas

### 8.1 cargo se queda colgado en `Updating 'tuna' index`

- Causa: el mirror está configurado en **modo repositorio git** (`.../git/crates.io-index.git`); la primera ejecución descarga más de 1 GB de índice
- Solución: configura `C:\Users\<you>\.cargo\config.toml` con el **índice sparse** (véase 2.3) o vuelve a ejecutar `1-Install_Env.bat`

### 8.2 mediapipe sin el submódulo solutions / instalación rota

```bat
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- Ejecútalo dentro del venv activado (en la carpeta `Demo`)
- `3-Deploy_Demo.bat` ya lo hace como mecanismo de reserva

### 8.3 discrepancia de versión de dora (mensaje v0.8.0 frente a v0.7.0)

- Síntoma: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Causa: la versión de dora-cli difiere de la de dora-node-api. **Ambas deben ser 0.5.0**
  - Comprobación: `dora --version` debería mostrar `dora-cli 0.5.0` y `dora-message: 0.8.0`
  - Solución: `cargo install dora-cli --version 0.5.0 --force`
  - `1-Install_Env.bat` ahora detecta automáticamente las versiones antiguas e instala a la fuerza la 0.5.0

### 8.4 Fallo de carga del modelo de MuJoCo / mediapipe (rutas en chino)

- Síntoma: `ParseXML: Error opening file '...\scene.xml'` o `Can't find file: ...\.tflite`
- Causa: los cargadores C++ de MuJoCo 3.x / mediapipe fallan con **rutas absolutas que contienen caracteres no ASCII (chinos)** (por ejemplo, `D:\Claude工作区\...`)
- Este proyecto ya incluye correcciones:
  - `AHSimulation\AHSimulation\mj_mink_*.py` cambia el directorio de trabajo antes de cargar
  - `HandTracking\mediapipe_patch.py` usa rutas cortas 8.3 + rutas relativas
- **No elimines estos archivos de corrección**

### 8.5 Permiso de cámara

- Primera ejecución: elige «Allow»
- Settings → Privacy → Camera → permitir aplicaciones de escritorio

### 8.6 El número de puerto cambia cada vez

- Después de volver a conectar el USB, el número de COM puede cambiar: vuelve a ejecutar `2-Setup_Serial.bat`

### 8.7 Falta OpenCV

```bat
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(en la carpeta `HandTracking`, con el venv activado)

---

## 9. Estructura del código

### Carpeta Demo

| Ruta | Descripción |
|---|---|
| `AHControl` | Nodo Rust que controla los servos. Punto de entrada: `src/main.rs` |
| `AHSimulation` | Nodo Python: simulación MuJoCo + cinemática inversa (mink) |
| `HandTracking` | Nodo Python: seguimiento de manos con MediaPipe |
| `dataflow_*.yml` | Definiciones de dataflow de dora (grafo de nodos) |
| `Windows_Deploy_Scripts` | Este paquete de scripts |

### Archivos dataflow

| Archivo | Finalidad |
|---|---|
| `dataflow_tracking_simu.yml` | Simulación: gestos de la webcam → manos simuladas |
| `dataflow_tracking_real_right.yml` | Mano derecha real |
| `dataflow_tracking_real_left.yml` | Mano izquierda real |
| `dataflow_tracking_real_2hands.yml` | Ambas manos reales (la misma placa controladora) |

### Principio del dataflow

```
Webcam → HandTracking (MediaPipe hand detection)
              ↓ hand keypoints
         AHSimulation (MuJoCo simulation + IK)
              ↓ joint target angles
         AHControl (serial → servo driver board → hand)
```

### Ubicaciones de la configuración del puerto

- La línea `args:` de los 3 archivos `dataflow_tracking_real_*.yml`: `--serialport COMxx`
- `AHControl\src\main.rs` `default_value = "COMxx"` (valor por defecto de serialport)
- `AHControl\config\*.toml`: modelo de servo, IDs, offsets (normalmente no hace falta cambiarlos)
