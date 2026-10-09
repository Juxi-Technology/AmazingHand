[English](../en/Linux_Tutorial.md) | [Deutsch](../de/Linux_Tutorial.md) | Español | [Français](../fr/Linux_Tutorial.md) | [Italiano](../it/Linux_Tutorial.md) | [日本語](../ja/Linux_Tutorial.md) | [한국어](../ko/Linux_Tutorial.md) | [Português (BR)](../pt-br/Linux_Tutorial.md) | [Português (PT)](../pt-pt/Linux_Tutorial.md) | [简体中文](../zh-hans/Linux_Tutorial.md) | [繁體中文](../zh-hant/Linux_Tutorial.md)

# Tutorial de seguimiento de manos de AmazingHand (mano diestra) · Linux (Ubuntu)

Este tutorial cubre el Demo oficial de AmazingHand (la mano diestra de Pollen Robotics) con scripts de despliegue en un solo clic.
Ejecuta los scripts en orden numérico. **Todos los scripts están en `Demo/Linux_Deploy_Scripts/`: ejecuta `./script` desde un terminal.**

---

## Índice

1. [Preparación del hardware](#1-preparación-del-hardware)
2. [Conceder permisos a los scripts (importante)](#2-conceder-permisos-a-los-scripts-importante)
3. [Configuración del entorno (script 1)](#3-configuración-del-entorno-script-1)
4. [Cableado](#4-cableado)
5. [Configuración del puerto serie (script 2)](#5-configuración-del-puerto-serie-script-2)
6. [Despliegue del código (script 3)](#6-despliegue-del-código-script-3)
7. [Ejecutar el demo (script 4)](#7-ejecutar-el-demo-script-4)
8. [Limpieza del proyecto (script 0)](#8-limpieza-del-proyecto-script-0)
9. [Solución de problemas y notas](#9-solución-de-problemas-y-notas)
10. [Estructura del código](#10-estructura-del-código)

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

## 2. Conceder permisos a los scripts (importante)

**Cuando los scripts se copian de Windows o de un ZIP a Linux, se pierde el permiso de ejecución (`+x`)**: al ejecutarlos directamente aparece
`Permission denied`. **Ejecuta esto una vez antes del primer uso:**

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
chmod +x *.sh
```

Después, cada script puede ejecutarse con `./script`. O bien combínalo:

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts" && chmod +x *.sh && ./1-Install_Env.sh
```

> Consejo: para mover la carpeta `AmazingHand-main` a Linux conservando los permisos, empaquétala con **tar**:
> `tar czf AmazingHand-main.tar.gz AmazingHand-main`, o simplemente ejecuta `chmod +x *.sh` una vez después de descomprimirla.

---

## 3. Configuración del entorno (script 1)

Desde la carpeta de scripts, ejecuta (después del `chmod +x` del paso 2):

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
./1-Install_Env.sh
```

Automáticamente:

1. **Instala Rust** (rustup + toolchain estable)
2. **Configura el mirror tuna de cargo** (`~/.cargo/config.toml`) para acelerar las descargas de crates
3. **Instala uv** (gestor de paquetes de Python)
4. **Instala dora-cli 0.5.0** (`cargo install`; la primera compilación tarda ~10–20 min, ten paciencia). Las versiones antiguas de dora se detectan automáticamente y se reemplazan a la fuerza.
5. **Instala el paquete pip dora-rs** (opcional)

> **Importante**: **cierra y vuelve a abrir el terminal** después del script para que las variables de entorno surtan efecto.
> Si alguna versión aparece vacía, añade a `~/.bashrc`:
>
> ```bash
> export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
> ```

### Instalación manual (si el script no es utilizable)

- **Rust**:
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```
- **uv**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **dora-cli**:
  ```bash
  cargo install dora-cli --version 0.5.0
  ```

### Mirror tuna de cargo (~/.cargo/config.toml)

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

## 4. Cableado

- Conecta la placa controladora de servos al PC por USB, **aliméntala con una fuente externa de 5V 4A**
- Localiza el puerto:
  ```bash
  ls /dev/ttyUSB* /dev/ttyACM*
  ```
  Normalmente `/dev/ttyACM0`

---

## 5. Configuración del puerto serie (script 2)

**Ejecuta `./2-Setup_Serial.sh`**:

1. "Connect the driver board" → pulsa Enter para escanear
2. Se listan los puertos serie detectados (`/dev/ttyACM*` / `/dev/ttyUSB*`)
3. Un solo puerto: pulsa Enter para confirmar; varios: escribe el índice
4. Escribe `--serialport` en los 3 archivos yml de dataflow y el puerto por defecto en `AHControl/src/main.rs`
5. **Configura los permisos del puerto serie automáticamente**:
   ```bash
   sudo chmod 666 /dev/ttyACM0
   ```
   Recomendado: añade el usuario actual al grupo dialout (evita volver a introducir la contraseña; cierra y vuelve a iniciar sesión para aplicarlo):
   ```bash
   sudo usermod -aG dialout $USER
   ```

> Si `ls /dev/ttyUSB* /dev/ttyACM*` no encuentra nada dentro de una VM, conecta el dispositivo USB a la máquina virtual en los ajustes de la VM.

---

## 6. Despliegue del código (script 3)

**Ejecuta `./3-Deploy_Demo.sh`** — automáticamente:

1. Inicia el daemon de dora (`dora up`)
2. Crea un venv de Python 3.12 (`uv venv --python 3.12`)
3. Activa el venv
4. Compila el nodo Rust AHControl (`cargo build --release`, ~10 min la primera vez)
5. Sincroniza las dependencias de AHSimulation y HandTracking (`uv sync`)
6. Instala a la fuerza mediapipe==0.10.14 (escollo conocido, mecanismo de reserva)

> Despliega una sola vez. Si lo vuelves a ejecutar, preguntará si quieres reconstruir el venv.

---

## 7. Ejecutar el demo (script 4)

**Ejecuta `./4-Run_Demo.sh`** — menú interactivo:

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

> El escritorio de Linux necesita permiso de cámara (Ubuntu: Settings → Privacy → Camera). Asegúrate de que ninguna otra aplicación esté usando la cámara. Problemas de cámara en la VM: consulta [9.6](#96-permiso-de-cámara--cámara-de-máquina-virtual-que-no-funciona).

---

## 8. Limpieza del proyecto (script 0)

**Ejecuta `./0-Cleanup_Project.sh`** y escribe `Y` para confirmar:

1. Detiene el daemon de dora
2. Elimina los 3 entornos virtuales (`.venv`)
3. Elimina la salida de compilación de Rust (`Demo/target`)
4. Elimina `__pycache__`, las copias de seguridad `.bak`, los logs y `Demo/out` (logs de dora)
5. **Restaura el puerto por defecto** (`--serialport /dev/ttyACM0`) y elimina los restos del puerto de esta máquina

> Después de la limpieza puedes copiar toda la carpeta `AmazingHand-main` a otra máquina: queda limpia y portable.
> En la nueva máquina, solo tienes que ejecutar 1 → 2 → 3 → 4 en orden.

---

## 9. Solución de problemas y notas

### 9.1 `Permission denied` (el script no tiene permiso de ejecución)

- Síntoma: `bash: ./1-Install_Env.sh: Permission denied`
- Causa: el script perdió el bit de ejecución al copiarlo de Windows / un ZIP
- Solución:
  ```bash
  chmod +x *.sh
  ```
  Después, ejecútalo con `./script` (no con `bash script`).

### 9.2 cargo se queda colgado en `Updating 'tuna' index`

- Causa: el mirror está configurado en **modo repositorio git** (`.../git/crates.io-index.git`); la primera ejecución descarga más de 1 GB de índice
- Solución: configura `~/.cargo/config.toml` con el **índice sparse** (véase 3.2) o vuelve a ejecutar `1-Install_Env.sh`

### 9.3 mediapipe sin el submódulo solutions / instalación rota

```bash
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- Ejecútalo dentro del venv activado (en la carpeta `Demo`)
- `3-Deploy_Demo.sh` ya lo hace como mecanismo de reserva

### 9.4 discrepancia de versión de dora (mensaje v0.8.0 frente a v0.7.0)

- Síntoma: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Causa: la versión de dora-cli difiere de la de dora-node-api. **Ambas deben ser 0.5.0**
  - Comprobación: `dora --version` debería mostrar `dora-cli 0.5.0` y `dora-message: 0.8.0`
  - `1-Install_Env.sh` ahora detecta automáticamente las versiones antiguas e instala a la fuerza la 0.5.0

**Si queda un dora antiguo (por ejemplo, 0.4.1) en el sistema, límpialo primero:**

```bash
# 1. Find where the old dora is
which dora
ls -la ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora 2>/dev/null

# 2. Delete the found old versions (adjust paths; there may be several)
rm -f ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora

# 3. Force-install 0.5.0 (goes to ~/.cargo/bin)
cargo install dora-cli --version 0.5.0 --force

# 4. Verify (should print dora-cli 0.5.0 / dora-message: 0.8.0)
dora --version
```

> Si `dora --version` sigue mostrando una versión antigua, hay otra copia antigua escondida en algún lugar del PATH: usa `which dora` para encontrarla y eliminarla, y asegúrate de que `~/.cargo/bin` aparezca pronto en el PATH.

### 9.5 Permiso denegado en el puerto serie

```bash
sudo chmod 666 /dev/ttyACM*
```

- Volver a conectar el cable puede restablecer los permisos
- Solución permanente: `sudo usermod -aG dialout $USER`, cerrar y volver a iniciar sesión

### 9.6 Permiso de cámara / Cámara de máquina virtual que no funciona

**Máquina física**:
- Ubuntu: Settings → Privacy → Camera → permitir aplicaciones
- Asegúrate de que ninguna otra aplicación (la app de Cámara, Zoom, etc.) esté usando la webcam

**Cámara de máquina virtual (VMware) que no funciona**:

Síntomas: `open VIDEOIO(V4L2:/dev/video0): can't open camera by index` o `select() timeout`;
`/dev/video0` existe y `v4l2-ctl` captura fotogramas, pero `cap.read()` de OpenCV sigue devolviendo `ret = False`.

Diagnóstico y solución (en orden):

1. **Redirige la cámara a la VM**: Menu → VM → Removable Devices → Camera → Connect
2. **Cambia la versión del controlador USB (la solución más eficaz en VMware)**:
   - VM → Settings → **USB Controller** → alterna entre `USB 2.0` / `USB 3.1`
   - **Reinicia la VM** después de cambiar
3. Comprueba que el dispositivo existe:
   ```bash
   ls -l /dev/video0
   sudo usermod -aG video $USER   # add to video group, log out/in
   ```
4. Comprueba que la cámara puede generar fotogramas con v4l2 (si es así, el controlador está bien y el problema es de compatibilidad con OpenCV):
   ```bash
   v4l2-ctl --device=/dev/video0 --set-fmt-video=width=640,height=480,pixelformat=MJPG --stream-mmap --stream-count=1 --stream-to=/tmp/frame.jpg
   ls -l /tmp/frame.jpg   # tens to hundreds of KB = stream works
   ```

### 9.7 El número de puerto cambia cada vez

- Después de volver a conectar el USB, el nombre del dispositivo puede cambiar: vuelve a ejecutar `2-Setup_Serial.sh`

### 9.8 Falta OpenCV

```bash
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(en la carpeta `HandTracking`, con el venv activado)

---

## 10. Estructura del código

### Carpeta Demo

| Ruta | Descripción |
|---|---|
| `AHControl` | Nodo Rust que controla los servos. Punto de entrada: `src/main.rs` |
| `AHSimulation` | Nodo Python: simulación MuJoCo + cinemática inversa (mink) |
| `HandTracking` | Nodo Python: seguimiento de manos con MediaPipe |
| `dataflow_*.yml` | Definiciones de dataflow de dora (grafo de nodos) |
| `Linux_Deploy_Scripts` | Este paquete de scripts |

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

- La línea `args:` de los 3 archivos `dataflow_tracking_real_*.yml`: `--serialport /dev/ttyACMx`
- `AHControl/src/main.rs` `default_value = "/dev/ttyACM0"` (valor por defecto de serialport)
- `AHControl/config/*.toml`: modelo de servo, IDs, offsets (normalmente no hace falta cambiarlos)
