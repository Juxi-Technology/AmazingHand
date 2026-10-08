# AmazingHand Dexterous Hand Hand-Tracking · Linux (Ubuntu) Tutorial

This tutorial covers the AmazingHand (Pollen Robotics dexterous hand) official Demo with one-click deploy scripts.
Run the scripts in numbered order. **All scripts are in `Demo/Linux_Deploy_Scripts/` — execute `./script` from a terminal.**

---

## Contents

1. [Hardware Preparation](#1-hardware-preparation)
2. [Grant Script Permissions (Important)](#2-grant-script-permissions-important)
3. [Environment Setup (Script 1)](#3-environment-setup-script-1)
4. [Wiring](#4-wiring)
5. [Serial Port Setup (Script 2)](#5-serial-port-setup-script-2)
6. [Code Deploy (Script 3)](#6-code-deploy-script-3)
7. [Run the Demo (Script 4)](#7-run-the-demo-script-4)
8. [Project Cleanup (Script 0)](#8-project-cleanup-script-0)
9. [Troubleshooting & Notes](#9-troubleshooting--notes)
10. [Code Structure](#10-code-structure)

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

## 2. Grant Script Permissions (Important)

**When scripts are copied from Windows or a zip to Linux, the execute permission (`+x`) is lost** — running them directly gives
`Permission denied`. **Run this once before the first use:**

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
chmod +x *.sh
```

Then each script can be run with `./script`. Or combine it:

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts" && chmod +x *.sh && ./1-Install_Env.sh
```

> Tip: To move the `AmazingHand-main` folder to Linux while keeping permissions, package with **tar**:
> `tar czf AmazingHand-main.tar.gz AmazingHand-main`, or simply run `chmod +x *.sh` once after unpacking.

---

## 3. Environment Setup (Script 1)

From the script folder, run (after the `chmod +x` in step 2):

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
./1-Install_Env.sh
```

It automatically:

1. **Installs Rust** (rustup + stable toolchain)
2. **Configures the cargo tuna mirror** (`~/.cargo/config.toml`) to speed up crate downloads
3. **Installs uv** (Python package manager)
4. **Installs dora-cli 0.5.0** (`cargo install`, first compile takes ~10–20 min, be patient). Old dora versions are auto-detected and force-replaced.
5. **Installs the dora-rs pip package** (optional)

> **Important**: **Close and reopen the terminal** after the script so the environment variables take effect.
> If any version shows empty, add to `~/.bashrc`:
>
> ```bash
> export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
> ```

### Manual install (if the script is not usable)

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

### cargo tuna mirror (~/.cargo/config.toml)

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

## 4. Wiring

- Connect the servo driver board to the PC with USB, **power it with an external 5V 4A supply**
- Find the port:
  ```bash
  ls /dev/ttyUSB* /dev/ttyACM*
  ```
  Usually `/dev/ttyACM0`

---

## 5. Serial Port Setup (Script 2)

**Run `./2-Setup_Serial.sh`**:

1. "Connect the driver board" → press Enter to scan
2. Detected serial ports are listed (`/dev/ttyACM*` / `/dev/ttyUSB*`)
3. Single port: press Enter to confirm; multiple: type the index
4. It writes `--serialport` into the 3 dataflow yml files and the default port into `AHControl/src/main.rs`
5. **Configures serial permissions automatically**:
   ```bash
   sudo chmod 666 /dev/ttyACM0
   ```
   Recommended: add the current user to the dialout group (avoids re-entering password; log out/in to apply):
   ```bash
   sudo usermod -aG dialout $USER
   ```

> If `ls /dev/ttyUSB* /dev/ttyACM*` finds nothing inside a VM, connect the USB device to the VM in the VM settings.

---

## 6. Code Deploy (Script 3)

**Run `./3-Deploy_Demo.sh`** — it automatically:

1. Starts the dora daemon (`dora up`)
2. Creates a Python 3.12 venv (`uv venv --python 3.12`)
3. Activates the venv
4. Builds the AHControl Rust node (`cargo build --release`, ~10 min first time)
5. Syncs AHSimulation and HandTracking deps (`uv sync`)
6. Force-installs mediapipe==0.10.14 (known pitfall, fallback)

> Deploy once. Re-running asks whether to rebuild the venv.

---

## 7. Run the Demo (Script 4)

**Run `./4-Run_Demo.sh`** — interactive menu:

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

> The Linux desktop needs camera permission (Ubuntu: Settings → Privacy → Camera). Make sure the camera is not used by another app. VM camera issues: see [9.6](#96-camera-permission--virtual-machine-camera-not-working).

---

## 8. Project Cleanup (Script 0)

**Run `./0-Cleanup_Project.sh`**, type `Y` to confirm:

1. Stops the dora daemon
2. Deletes the 3 virtual envs (`.venv`)
3. Deletes the Rust build output (`Demo/target`)
4. Deletes `__pycache__`, `.bak` backups, logs, and `Demo/out` (dora logs)
5. **Restores the default port** (`--serialport /dev/ttyACM0`), removing this machine's port residue

> After cleanup you can copy the whole `AmazingHand-main` folder to another machine — clean and portable.
> On the new machine just run 1 → 2 → 3 → 4 in order.

---

## 9. Troubleshooting & Notes

### 9.1 `Permission denied` (script has no execute permission)

- Symptom: `bash: ./1-Install_Env.sh: Permission denied`
- Cause: the script lost its execute bit when copied from Windows / a zip
- Fix:
  ```bash
  chmod +x *.sh
  ```
  Then run with `./script` (not `bash script`).

### 9.2 cargo stuck at `Updating 'tuna' index`

- Cause: mirror configured as **git-repo mode** (`.../git/crates.io-index.git`), first run downloads 1 GB+ index
- Fix: set `~/.cargo/config.toml` to the **sparse index** (see 3.2), or re-run `1-Install_Env.sh`

### 9.3 mediapipe missing solutions submodule / broken install

```bash
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- Run inside the activated venv (in the `Demo` folder)
- `3-Deploy_Demo.sh` already does this as a fallback

### 9.4 dora version mismatch (message v0.8.0 vs v0.7.0)

- Symptom: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Cause: dora-cli version differs from dora-node-api. **Must both be 0.5.0**
  - Check: `dora --version` should print `dora-cli 0.5.0` and `dora-message: 0.8.0`
  - `1-Install_Env.sh` now auto-detects old versions and force-installs 0.5.0

**If an old dora (e.g. 0.4.1) is left on the system, clean it up first:**

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

> If `dora --version` still shows an old version, another old copy is hiding somewhere in PATH — use `which dora` to find and remove it, and make sure `~/.cargo/bin` is early in PATH.

### 9.5 Serial port permission denied

```bash
sudo chmod 666 /dev/ttyACM*
```

- Replugging may reset permissions
- Permanent fix: `sudo usermod -aG dialout $USER`, log out/in

### 9.6 Camera permission / Virtual machine camera not working

**Real machine**:
- Ubuntu: Settings → Privacy → Camera → allow apps
- Make sure no other app (Camera app, Zoom, etc.) is using the webcam

**Virtual machine (VMware) camera not working**:

Symptoms: `open VIDEOIO(V4L2:/dev/video0): can't open camera by index` or `select() timeout`;
`/dev/video0` exists and `v4l2-ctl` captures frames, but OpenCV `cap.read()` keeps returning `ret = False`.

Troubleshoot and fix (in order):

1. **Forward the camera into the VM**: Menu → VM → Removable Devices → Camera → Connect
2. **Switch the USB controller version (most effective VMware fix)**:
   - VM → Settings → **USB Controller** → switch between `USB 2.0` / `USB 3.1`
   - **Restart the VM** after switching
3. Verify the device exists:
   ```bash
   ls -l /dev/video0
   sudo usermod -aG video $USER   # add to video group, log out/in
   ```
4. Verify the camera can actually produce frames with v4l2 (if yes, driver is fine and the issue is OpenCV compatibility):
   ```bash
   v4l2-ctl --device=/dev/video0 --set-fmt-video=width=640,height=480,pixelformat=MJPG --stream-mmap --stream-count=1 --stream-to=/tmp/frame.jpg
   ls -l /tmp/frame.jpg   # tens to hundreds of KB = stream works
   ```

### 9.7 Port number changes each time

- After replugging USB the device name may change — re-run `2-Setup_Serial.sh`

### 9.8 Missing OpenCV

```bash
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(in the `HandTracking` folder, venv activated)

---

## 10. Code Structure

### Demo folder

| Path | Description |
|---|---|
| `AHControl` | Rust node controlling the servos. Entry: `src/main.rs` |
| `AHSimulation` | Python node: MuJoCo simulation + inverse kinematics (mink) |
| `HandTracking` | Python node: MediaPipe hand tracking |
| `dataflow_*.yml` | dora dataflow definitions (node graph) |
| `Linux_Deploy_Scripts` | This script pack |

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

- The `args:` line of the 3 `dataflow_tracking_real_*.yml` files: `--serialport /dev/ttyACMx`
- `AHControl/src/main.rs` `default_value = "/dev/ttyACM0"` (serialport default)
- `AHControl/config/*.toml`: servo model, IDs, offsets (usually no change needed)
