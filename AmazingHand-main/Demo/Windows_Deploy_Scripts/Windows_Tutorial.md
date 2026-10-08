# AmazingHand Dexterous Hand Hand-Tracking · Windows Tutorial

This tutorial covers the AmazingHand (Pollen Robotics dexterous hand) official Demo with one-click deploy scripts.
Run the scripts in numbered order. **All scripts are in `Demo\Windows_Deploy_Scripts\` — double-click to run.**

---

## Contents

1. [Hardware Preparation](#1-hardware-preparation)
2. [Environment Setup (Script 1)](#2-environment-setup-script-1)
3. [Wiring](#3-wiring)
4. [Serial Port Setup (Script 2)](#4-serial-port-setup-script-2)
5. [Code Deploy (Script 3)](#5-code-deploy-script-3)
6. [Run the Demo (Script 4)](#6-run-the-demo-script-4)
7. [Project Cleanup (Script 0)](#7-project-cleanup-script-0)
8. [Troubleshooting & Notes](#8-troubleshooting--notes)
9. [Code Structure](#9-code-structure)

---

## 1. Hardware Preparation

| Item | Requirement |
|---|---|
| Dexterous hand | Right / Left / Both |
| Servo driver board | External, USB to PC |
| Power | **At least 5V 4A** (USB alone is not enough, use an external PSU) |
| Camera | Built-in or USB webcam |

> Model files (URDF etc.) can be viewed/downloaded at [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e).

---

## 2. Environment Setup (Script 1)

**Double-click `1-Install_Env.bat`** — it automatically:

1. **Checks MSVC build tools** (cl.exe) — required to compile Rust. If missing, install
   Visual Studio 2022 Build Tools with the "Desktop development with C++" workload, then reopen the terminal.
2. **Installs Rust** (rustup + stable-msvc toolchain)
3. **Configures the cargo tuna mirror** (`C:\Users\<you>\.cargo\config.toml`) to speed up crate downloads
4. **Installs uv** (Python package manager)
5. **Installs dora-cli 0.5.0** (`cargo install`, first compile takes ~10–20 min, be patient)
6. **Installs the dora-rs pip package** (optional; it is also installed into the venv during deploy)

> **Important**: **Close and reopen the terminal** after the script so the environment variables take effect.
> Downloads may be slow depending on your network — wait, don't interrupt.

### Manual install (if the script is not usable)

- **Rust**: <https://www.rust-lang.org/tools/install> — use rustup-init.exe, default MSVC toolchain.
  - PATH: add `%USERPROFILE%\.cargo\bin`
- **uv**: PowerShell: `irm https://astral.sh/uv/install.ps1 | iex`
  - PATH: add `%USERPROFILE%\.local\bin`
- **dora-cli**: `cargo install dora-cli --version 0.5.0`

### cargo tuna mirror (config.toml)

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

> Use the **sparse index** (above), NOT the git-repo mirror — the git mirror first downloads ~1 GB of index and often hangs at `Updating 'tuna' index`.

---

## 3. Wiring

- Connect the servo driver board to the PC with USB, **power it with an external 5V 4A supply**
- Find the port: **Device Manager → Ports (COM & LPT)**, e.g. `COM11`

---

## 4. Serial Port Setup (Script 2)

**Double-click `2-Setup_Serial.bat`** (logic is in `2-Setup_Serial.ps1`):

1. "Connect the driver board" → press Enter to scan
2. Detected COM ports are listed (with device names)
3. Single port: press Enter to confirm; multiple: type the index
4. It writes `--serialport` into the 3 dataflow yml files and the default port into `AHControl\src\main.rs`
5. Original files are backed up as `.bak`

> If you replug the USB cable, the COM number may change — re-run this script.

---

## 5. Code Deploy (Script 3)

**Double-click `3-Deploy_Demo.bat`** — it automatically:

1. Starts the dora daemon (`dora up`)
2. Creates a Python 3.12 venv (`uv venv --python 3.12`)
3. Activates the venv
4. Builds the AHControl Rust node (`cargo build --release`, ~10 min first time)
5. Syncs AHSimulation and HandTracking deps (`uv sync`)
6. Force-installs mediapipe==0.10.14 (known pitfall, fallback)

> Deploy once. Re-running asks whether to rebuild the venv.

---

## 6. Run the Demo (Script 4)

**Double-click `4-Run_Demo.bat`** — interactive menu:

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

- **1**: Simulation — webcam gestures drive two simulated hands
- **2**: Real hardware — submenu for right / left / both hands

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

It then runs `dora build` + `dora run`. A camera window opens; make hand gestures to move the hand(s) in real time. **Ctrl+C to stop**. After the dataflow ends, press Enter to return to the menu and choose another mode or `q` to quit.

> On first run, Windows may ask for camera permission — click "Allow".

---

## 7. Project Cleanup (Script 0)

**Double-click `0-Cleanup_Project.bat`**, type `Y` to confirm:

1. Stops the dora daemon
2. Deletes the 3 virtual envs (`.venv`)
3. Deletes the Rust build output (`Demo\target`)
4. Deletes `__pycache__`, `.bak` backups, logs, and `Demo\out` (dora logs)
5. **Restores the default port** (`--serialport /dev/ttyACM0`), removing this machine's COM residue

> After cleanup you can copy the whole `AmazingHand-main` folder to another machine — clean and portable.
> On the new machine just run 1 → 2 → 3 → 4 in order.

---

## 8. Troubleshooting & Notes

### 8.1 cargo stuck at `Updating 'tuna' index`

- Cause: mirror configured as **git-repo mode** (`.../git/crates.io-index.git`), first run downloads 1 GB+ index
- Fix: set `C:\Users\<you>\.cargo\config.toml` to the **sparse index** (see 2.3), or re-run `1-Install_Env.bat`

### 8.2 mediapipe missing solutions submodule / broken install

```bat
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- Run inside the activated venv (in the `Demo` folder)
- `3-Deploy_Demo.bat` already does this as a fallback

### 8.3 dora version mismatch (message v0.8.0 vs v0.7.0)

- Symptom: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Cause: dora-cli version differs from dora-node-api. **Must both be 0.5.0**
  - Check: `dora --version` should print `dora-cli 0.5.0` and `dora-message: 0.8.0`
  - Fix: `cargo install dora-cli --version 0.5.0 --force`
  - `1-Install_Env.bat` now auto-detects old versions and force-installs 0.5.0

### 8.4 MuJoCo / mediapipe model load failure (Chinese paths)

- Symptom: `ParseXML: Error opening file '...\scene.xml'` or `Can't find file: ...\.tflite`
- Cause: MuJoCo 3.x / mediapipe C++ loaders fail on **absolute paths containing non-ASCII (Chinese) characters** (e.g. `D:\Claude工作区\...`)
- This project already includes fixes:
  - `AHSimulation\AHSimulation\mj_mink_*.py` switches working directory before loading
  - `HandTracking\mediapipe_patch.py` uses 8.3 short paths + relative paths
- **Do not delete these fix files**

### 8.5 Camera permission

- First run: choose "Allow"
- Settings → Privacy → Camera → allow desktop apps

### 8.6 Port number changes each time

- After replugging USB the COM number may change — re-run `2-Setup_Serial.bat`

### 8.7 Missing OpenCV

```bat
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(in the `HandTracking` folder, venv activated)

---

## 9. Code Structure

### Demo folder

| Path | Description |
|---|---|
| `AHControl` | Rust node controlling the servos. Entry: `src/main.rs` |
| `AHSimulation` | Python node: MuJoCo simulation + inverse kinematics (mink) |
| `HandTracking` | Python node: MediaPipe hand tracking |
| `dataflow_*.yml` | dora dataflow definitions (node graph) |
| `Windows_Deploy_Scripts` | This script pack |

### dataflow files

| File | Purpose |
|---|---|
| `dataflow_tracking_simu.yml` | Simulation: webcam gestures → simulated hands |
| `dataflow_tracking_real_right.yml` | Real right hand |
| `dataflow_tracking_real_left.yml` | Real left hand |
| `dataflow_tracking_real_2hands.yml` | Real both hands (same driver board) |

### Dataflow principle

```
Webcam → HandTracking (MediaPipe hand detection)
              ↓ hand keypoints
         AHSimulation (MuJoCo simulation + IK)
              ↓ joint target angles
         AHControl (serial → servo driver board → hand)
```

### Port config locations

- The `args:` line of the 3 `dataflow_tracking_real_*.yml` files: `--serialport COMxx`
- `AHControl\src\main.rs` `default_value = "COMxx"` (serialport default)
- `AHControl\config\*.toml`: servo model, IDs, offsets (usually no change needed)
