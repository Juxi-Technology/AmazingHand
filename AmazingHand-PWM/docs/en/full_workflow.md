# AmazingHand PWM Dexterous Hand — Full Workflow Tutorial

> From **host-side gesture commands** to **hand tracking** — an end-to-end tutorial.
> Applicable hardware: ESP32-S3 + 8-channel PWM servos (differential drive).
>
> Version: 2026-08-20 · Matching firmware: ESP-IDF componentized version (`AmazingHand_Serial`)

---

## Chapter 0 Tutorial Navigation

This tutorial is organized **in sequential order**. First figure out which route you want to take, then jump to the corresponding chapters.

| Route | Purpose | Prerequisites | Chapters |
|------|------|----------|------|
| **A. Host-side gesture commands** | Click buttons / type commands to make the dexterous hand perform gestures (rock/scissors/paper/thumbs up…) | Python + flashed firmware | Chapters 1-4 |
| **B. GUI built-in hand tracking** | Camera follows hand movements and the hand reproduces them in real time (simplified, no IK) | A + 64-bit Python + mediapipe | Chapters 1-4 + 5.1 |
| **C. dora official IK tracking** | Official full pipeline: camera → IK → 8 joint angles → servos (full version) | A + Rust + uv + dora | Separate project, not included in this module |

**Recommended routes**:
- First time using it → take **A** and first confirm that the firmware and wiring are working.
- Want a quick camera-following demo → take **B** (lightweight, a few minutes to install).
- Need formal, complete tracking → use the dora Demo from the original delivery package (not included in this module).

The hardware is shared across this module; the environment for routes A/B only needs Python + pyserial + mediapipe.

---

## Chapter 1 Environment Setup

Install in the order given. **Routes A/B only need Section 1.1; Route C additionally needs Section 1.2.**

### 1.1 Host PC Environment (Required for Routes A/B)

#### ① 64-bit Python 3.12

> **64-bit is mandatory**. mediapipe 0.10.14 only provides 64-bit Windows wheels; it cannot be installed on 32-bit;
> this is also a common cause of the GUI crashing immediately when double-clicked.

- Recommended installation path: `D:\Python312-64bit` (this path already exists on this machine).
- During installation, check **Add to PATH**.
- Verify (64-bit):

```bash
py -3.12-64 -c "import sys; print('64bit' if sys.maxsize > 2**32 else '32bit')"
# Output: 64bit
```

#### ② Install Host Dependencies

From the module root:

```bash
pip install -r tools/requirements.txt     # only pyserial
```

#### ③ Additional Tracking Dependencies (for Route B)

Run from the project root:

```bash
tools/setup_tracking.bat
```

It automatically: locates 64-bit Python → creates the `tools/tracking_env` virtual environment → installs `tools/requirements-tracking.txt`
(mediapipe==0.10.14, numpy<2, scipy, opencv, Pillow, pyserial) → verifies mediapipe.

> Or install manually:
> ```bash
> D:/Python312-64bit/python.exe -m pip install -r tools/requirements-tracking.txt
> ```

### 1.2 dora Official IK Environment (Separate Project, Not Included in This Module)

This module only includes the GUI's built-in lightweight tracking (Route B). The complete dora + MuJoCo IK pipeline Demo is not distributed with this module; if you need it:

- Use `02_hand_tracking/Demo` from the original delivery package, or
- Refer to MediaPipe / dora Demo projects outside this repository.

This section and Section 5.2 below are for reference only for users who have the original Demo; users of this module can skip them.

---

## Chapter 2 Hardware Wiring

### 2.1 Hardware List

| Hardware | Description |
|------|------|
| ESP32-S3 development board | YX-ESP32-S3 or equivalent |
| 8-channel PWM servos | Analog servos, differential drive |
| Servo adapter board | Servos → 8-channel PWM output |
| Dedicated 5V power supply | **At least 5V 3A**; servos draw large transient currents |
| USB data cable | ESP32-S3 Type-C → PC |
| Camera | Built-in or USB camera (for tracking) |

### 2.2 GPIO Mapping

Adapter board PWM1-8 → ESP32-S3 GPIO:

| Adapter board | GPIO | Finger |
|--------|------|------|
| PWM1 | 4 | Index finger joint 1 |
| PWM2 | 5 | Index finger joint 2 |
| PWM3 | 6 | Middle finger joint 1 |
| PWM4 | 7 | Middle finger joint 2 |
| PWM5 | 15 | Ring finger joint 1 |
| PWM6 | 16 | Ring finger joint 2 |
| PWM7 | 17 | Thumb joint 1 |
| PWM8 | 18 | Thumb joint 2 |

> **Left and right hands share the same GPIO set**. Left/right hand is switched in software (Chapter 4); no rewiring is needed.

### 2.3 Power Requirements

- Use a **dedicated 5V power supply** for the servos (at least 3A); do not rely on USB power alone.
- Transient current surges from the servos may reset the ESP32 (symptom: the ESP32 reboots repeatedly). In that case, **power-cycle** the ESP32.

### 2.4 Wiring Steps

1. 8 servo channels → adapter board PWM1-8
2. Adapter board → corresponding ESP32-S3 GPIOs (table above)
3. ESP32-S3 Type-C → PC
4. Connect the camera to the PC (for tracking)

> For detailed wiring/circuit diagrams, see the `ESP32开发板电路图/` directory.

---

## Chapter 3 Prerequisite: Firmware Flashing

> For the servos to respond, the firmware must be flashed first. The firmware is located in `firmware/AmazingHand_Serial/`.

### 3.1 ESP-IDF Build (Recommended)

Open the `AmazingHand_Serial` project with Espressif IDE:

1. Set the target chip (first time only):
   ```
   idf.py set-target esp32s3
   ```
2. Build:
   ```
   idf.py build
   ```
3. Flash (on Windows, use the COM port, e.g. COM3):
   ```
   idf.py -p COM3 flash
   ```

### 3.2 Verification After Flashing

Serial monitor (baud rate **115200**):

```
idf.py -p COM3 monitor
```

You should see the boot log:

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

> The serial baud rate is already configured uniformly by the firmware/scripts (115200); customers do not need to set it manually.

> Note: devices are usually delivered with the firmware already flashed; this step is only needed for new firmware or re-flashing.

---

## Chapter 4 First Run: Host-Side Gesture Commands

> Prerequisites: firmware flashed (Chapter 3), ESP32 powered, serial cable connected. First check Device Manager to confirm the COM port.

### 4.1 GUI Visualization (Recommended)

#### Option A: Run the Packaged exe

If you have already packaged an exe yourself with PyInstaller (see Section 5 of the [Usage Tutorial](gui_usage.md)), you can also run it by double-clicking; the packaged version does not include tracking — tracking requires running from source.

#### Option B: Run from Source

```bash
# From the project root; first activate the tracking environment (with mediapipe) or use any Python with pyserial
tools/tracking_env/Scripts/python tools/hand_gui.py
```

#### GUI Usage Steps

1. **Select the serial port**: choose the ESP32's COM port from the drop-down at the top.
2. **Click "Connect"**: the status light turns green, the log shows "connected", and a NOP link test is sent automatically.
3. **Gesture commands**: click "Rock", "Scissors", "Paper", "Thumbs Up", "OK", "Pinch", "Point", etc., and the hand performs the gesture.
4. **Left/right hand**: check "Right Hand"/"Left Hand" to switch the thumb mirror direction.
5. **Direct servo drive**: drag the 8 sliders to control individual servo angles in real time (0-180°).
6. **Finger differential control** (recommended): two progress bars per finger — "Bend ◀▶ Extend" for reverse differential motion and "Swing Right ◀▶ Swing Left" for same-direction swinging. The two degrees of freedom are independent and driven synchronously.
7. **Repeat/Stop**: repeat the last gesture / interrupt immediately.
8. **Communication log**: displays sent/received frames and responses in real time at the bottom.

### 4.2 Command-Line Test (serial_test.py)

From the project root:

```bash
# Link test (first confirm communication works)
python tools/serial_test.py COM3 nop

# Gestures
python tools/serial_test.py COM3 rock         # rock
python tools/serial_test.py COM3 thumbs_up    # thumbs up
python tools/serial_test.py COM3 index        # point
python tools/serial_test.py COM3 open         # open
python tools/serial_test.py COM3 close        # fist

# Direct single-servo drive
python tools/serial_test.py COM3 servo 1 90   # servo 1 → 90°

# Center all servos
python tools/serial_test.py COM3 mid

# Set left/right hand
python tools/serial_test.py COM3 hand L
python tools/serial_test.py COM3 hand R

# Sweep / self-test
python tools/serial_test.py COM3 sweep 1      # sweep servo 1
python tools/serial_test.py COM3 test         # test all servos one by one
```

### 4.3 Verification

- After clicking a gesture, the servos should perform the corresponding action; the serial log returns `ACK` and `DONE`.
- Response codes: `0x00=OK`, `0x01=invalid command`, `0x02=parameter error`, `0x03=busy`, `0x10=done`.
- If the servos do not move at all: see the FAQ in Chapter 6 (check power/serial port first).

> For a complete quick reference of gesture commands and the serial protocol, see Chapter 7.

---

## Chapter 5 Advanced Tutorial: Hand Tracking

> Prerequisites: Chapters 1-4 completed (firmware flashed, serial control working, camera ready).
> There are two paths in this chapter; choose one.

### 5.1 GUI Built-in Tracking (Lightweight Version)

**Suitable for**: quick demos without installing dora. Camera → directly mapped to differential servos, no IK.

#### Prerequisites

- 64-bit Python + `tools/setup_tracking.bat` (Section 1.1).
- A working camera.

#### Running

```bash
# From the project root, start the GUI with the tracking environment
tools/tracking_env/Scripts/python tools/hand_gui.py
```

1. Select the serial port → "Connect".
2. Scroll to the "Hand Tracking (MediaPipe Camera)" panel.
3. Select the camera number (default 0) → click "Start Tracking".
4. Put your hand in the frame; the hand follows finger bending/straightening.

#### How It Works

- mediapipe 0.10.14 extracts 3D vectors of the four fingertips (in the hand coordinate system).
- `tips_to_angles()` in `hand_tracking.py` maps each finger to differential angles:
  - flex (bend/straighten): the three fingers use the z component, the thumb uses the y component;
  - base (left/right swing): fixed at 90 (left/right swing not implemented yet).
- The GUI has built-in EMA smoothing (alpha=0.4) + 60 ms throttling to avoid jitter.

#### Limitations

- **No IK**: fingertips are mapped directly to angles, so accuracy is lower than the official pipeline.
- **Left/right swing deferred**: base is fixed at 90; no left/right swinging.
- Suitable for demos/prototypes; for production use, 5.2 is recommended.

### 5.2 dora Official IK Tracking (Separate Project)

The complete pipeline is provided by a separate dora Demo: camera → mediapipe → MuJoCo+mink IK → 8 joint angles → AHControl (Rust) → ESP32 → PWM servos.

That Demo (including `AHControl`, `AHSimulation`, `HandTracking`, `dataflow_*_pwm.yml`, and one-click scripts) is not distributed with this module; if needed, use `02_hand_tracking/Demo` from the original delivery package. For the tracking feature included in this module, see 5.1.

---

## Chapter 6 FAQ (During Operation)

> This section lists only the problems **most likely to be encountered during use and that you can solve yourself**. Use the symptoms to locate the cause quickly.

### 6.1 Servos Do Not Move at All

Troubleshoot in order:

1. **Power**: Are the servos connected to a dedicated power supply (5V 3A or higher)? With USB power alone, the servos may not move or the ESP32 may reboot repeatedly. → Power-cycle the ESP32.
2. **Serial port**: Is the COM port correct? Check Device Manager → Ports (COM & LPT) for the port corresponding to the ESP32. Is another program (such as a serial terminal) occupying it? → Close the occupying program.
3. **Wiring**: Are adapter board PWM1-8 connected to the correct GPIOs? Are the servo signal wires plugged in firmly?

### 6.2 No Camera Image

- On first run, Windows prompts for camera permission → click "Allow".
- If you previously chose "No": Settings → Privacy & security → Camera → Allow desktop apps to access the camera, then run again.

### 6.3 Camera Image Present but Hand Does Not Follow / Follows Sluggishly

- Make sure the camera is **facing** your hand directly, lighting is adequate, and your hand is fully visible in the frame.
- Move more slowly and with larger motions. If movements are too fast or too small, tracking may not keep up.
- Did the fingers move in the 3D simulation window?
  - **Yes**: the tracking pipeline is working; the problem is with the servos/serial port — see 6.1.
  - **No**: the tracking node did not detect the hand; adjust your pose/lighting and try again.

### 6.4 Hand Pose Inverted / Thumb Direction Reversed

- Is the left/right hand selected incorrectly? Select the corresponding hand type in the run menu.
- In the host GUI, check "Right Hand"/"Left Hand" to switch.

### 6.5 Left/Right Hand Switch Does Not Take Effect

- After checking "Right Hand"/"Left Hand" at the top of the GUI, the next gesture/direct-drive command immediately uses the corresponding mapping.
- In the web version, switch it under "Control Target" at the top; the page sends `0xF1` to select the side.
- If you are using the separate dora Demo, you need to run `dora build` again after switching the hand type.

### 6.6 Screen Freezes / Log Stops Mid-Run

- The camera may be occupied by another application (video conference, another script); close it and try again.
- Or press `Ctrl+C` to stop, then run it again.

### 6.7 Cannot Find the Serial Port After Changing USB Port / Restarting the Computer

- The COM port number may have changed. Confirm the new COM number in Device Manager, then select that serial port again in the GUI or web page.

### 6.8 Still Not Working?

- Send a screenshot of the communication log at the bottom of the GUI or the serial port status on the web page to the maintainer, and explain: at which step, what operation, and what symptom you saw.
- Key information: whether the serial port is connected, and whether a `BB` response was received (`0x00` OK / `0x10` done).

---

## Chapter 7 Command Quick Reference (Appendix)

> For the complete protocol description, see `user_manual.md` in the same directory. This chapter provides quick-reference tables.

### 7.1 Gesture Commands

| Gesture | HEX | ACK | DONE |
|------|-----|-----|------|
| NOP | `AA 00 00 00` | `BB 00 00 00` | — |
| Rock | `AA 01 00 01` | `BB 01 00 01` | `BB 01 10 11` |
| Scissors | `AA 02 00 02` | `BB 02 00 02` | `BB 02 10 12` |
| Paper | `AA 03 00 03` | `BB 03 00 03` | `BB 03 10 13` |
| Thumbs Up | `AA 04 00 04` | `BB 04 00 04` | `BB 04 10 14` |
| Taunt 1 (index-finger wag) | `AA 05 00 05` | `BB 05 00 05` | `BB 05 10 15` |
| Taunt 2 (ring finger) | `AA 06 00 06` | `BB 06 00 06` | `BB 06 10 16` |
| Open | `AA 07 00 07` | `BB 07 00 07` | `BB 07 10 17` |
| Fist | `AA 08 00 08` | `BB 08 00 08` | `BB 08 10 18` |
| OK | `AA 09 00 09` | `BB 09 00 09` | `BB 09 10 19` |
| Pinch | `AA 0A 00 0A` | `BB 0A 00 0A` | `BB 0A 10 1A` |
| Point | `AA 0C 00 0C` | `BB 0C 00 0C` | `BB 0C 10 1C` |

### 7.2 Control Commands

| Command | HEX | Description |
|------|-----|------|
| Repeat | `AA FE 00 FE` | Repeat the last gesture |
| Stop | `AA FF 00 FF` | Interrupt immediately |
| Set right hand | `AA F1 01 01 F1` | — |
| Set left hand | `AA F1 01 02 F2` | — |
| Direct drive | `AA F0 08 [8×angle] CKSUM` | 8-byte angles |

### 7.3 Frame Format

```
Frame header (0xAA) + Command (CMD) + Length (LEN) + Data (DATA) + Checksum (CKSUM)
CKSUM = CMD ^ LEN ^ DATA[0] ^ ... ^ DATA[N-1]
Response: Frame header (0xBB) + CMD + STATUS + (CMD^STATUS)
```

### 7.4 Host-Side Tools

| Tool | Command | Purpose |
|------|------|------|
| GUI | `tools/tracking_env/Scripts/python tools/hand_gui.py` | Visual gestures + direct drive + differential + tracking |
| Packaged exe (optional) | Package `tools/hand_gui.py` with PyInstaller | Python-free visualization (no tracking) |
| Command line | `python tools/serial_test.py COMx <cmd>` | Automated testing |

### 7.5 Tracking Dataflow Files (PWM Version)

| Purpose | File |
|------|------|
| Left-hand PWM tracking | `dataflow_tracking_real_left_pwm.yml` |
| Right-hand PWM tracking | `dataflow_tracking_real_right_pwm.yml` |
| Left-hand PWM configuration | `AHControl/config/l_hand_pwm.toml` |
| Right-hand PWM configuration | `AHControl/config/r_hand_pwm.toml` |
