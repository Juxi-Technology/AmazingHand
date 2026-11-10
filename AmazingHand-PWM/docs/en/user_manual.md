# Dexterous Hand Serial Control — User Manual

## Table of Contents

1. [Overview](#1-overview)
2. [Hardware Wiring](#2-hardware-wiring)
3. [Firmware Build and Flashing](#3-firmware-build-and-flashing)
4. [Serial Communication Protocol](#4-serial-communication-protocol)
5. [Command Reference](#5-command-reference)
6. [Host Software Tutorial](#6-host-software-tutorial)
7. [Gesture Tracking](#7-gesture-tracking)
8. [Gesture Parameter Tuning](#8-gesture-parameter-tuning)
9. [FAQ](#9-faq)

---

## 1. Overview

This firmware runs on an **ESP32-S3** development board and uses PWM signals to control 8 servos that drive the dexterous hand through gestures. A host (PC / Raspberry Pi / another MCU) sends binary frame commands over a USB serial port; the ESP32 parses them, performs the corresponding gesture, and returns a response.

The project provides two firmware implementations:

| Firmware | Directory | Features |
|------|------|------|
| **ESP-IDF Edition** (recommended) | `firmware/AmazingHand_Serial/` | Component-based project structure, dual FreeRTOS tasks, production-ready |

> Both firmware implementations share the **same serial protocol** and the **same command set**, and their gesture parameters can be cross-referenced.

### Supported Gestures (11 Gesture Commands)

| Gesture | Command | Description |
|------|------|------|
| Rock | 0x01 | Rock-paper-scissors: all fingers clenched |
| Scissors | 0x02 | Rock-paper-scissors: index and middle fingers extended in a V shape |
| Paper | 0x03 | Rock-paper-scissors: all fingers extended |
| Thumbs Up | 0x04 | Thumb raised, the other fingers clenched |
| Taunt 1 | 0x05 | Wag the index finger ("no, no, no") |
| Taunt 2 | 0x06 | Ring finger extended and wiggled (in place of the little finger) |
| Open | 0x07 | All fingers extended |
| Fist | 0x08 | All fingers closed |
| OK | 0x09 | OK gesture |
| Pinch | 0x0A | Pinch gesture |
| Point | 0x0C | Index finger extended in a pointing motion |
| Direct Drive | 0xF0 | Directly control the angles of the 8 servos |
| Set Hand Side | 0xF1 | Switch between left-hand and right-hand modes |
| Repeat | 0xFE | Repeat the previous gesture |
| Stop | 0xFF | Immediately abort the current gesture |
| NOP | 0x00 | Link test |

> Note: Command 0x0B is disabled (the former "Thumbs Down" gesture duplicated Thumbs Up and has been removed).

---

## 2. Hardware Wiring

### Compatible Hardware

| Item | Model |
|------|------|
| Main controller | **ESP32-S3** development board (Youxin YX-ESP32-S3 or equivalent) |
| Servos | 8-channel PWM **digital** servos (PTK 7452 MG-D or equivalent, 333 Hz) |
| Adapter board | PWM servo adapter board |

> ⚠️ 50 Hz analog servos such as the SG90 are **not** drop-in replacements for the 333 Hz firmware. Changing the servo model requires updating `LEDC_FREQ` and the pulse-width calibration, then revalidating.

The ESP32-S3 development board has two Type-C ports:
- **Built-in USB Serial/JTAG**: connects directly to the USB controller built into the ESP32-S3 chip
- **External FT232**: communicates through an FT232 USB-to-serial chip

> Either port can be used for serial communication; choose one. Select the corresponding serial device name on the host.

### Servos → Adapter Board

Plug the 3-pin connectors of the 8 servos into the adapter board's servo 1-8 pin headers according to their ID numbers.

### Adapter Board → ESP32-S3

| Adapter Board | ESP32-S3 GPIO | Description |
|--------|-------------|------|
| PWM1 | **4** | Index finger joint 1 |
| PWM2 | **5** | Index finger joint 2 |
| PWM3 | **6** | Middle finger joint 1 |
| PWM4 | **7** | Middle finger joint 2 |
| PWM5 | **15** | Ring finger joint 1 |
| PWM6 | **16** | Ring finger joint 2 |
| PWM7 | **17** | Thumb joint 1 |
| PWM8 | **18** | Thumb joint 2 |
| 5V | 5V | Power supply (fed from the adapter board) |
| GND | GND | **Common ground is mandatory; connect at least one wire** |

> The left and right hands share the same GPIO mapping. When "left hand" mode is selected, the firmware mirrors the thumb's direction of motion within the gestures; the pin assignments do not change.

### Power Supply

The adapter board has two sets of 5V/GND power terminals:
- One set is wired to a Type-C cable and connects to a **5V 3A** power adapter
- The other set supplies the ESP32-S3's **5V** pin (the development board then does not need power through its own Type-C port)

---

## 3. Firmware Build and Flashing

### 3.1 ESP-IDF Edition (Recommended)

> **Warning: path requirements**: The ESP-IDF build does not support Chinese characters in paths. Make sure the project path consists entirely of English characters (including the user folder and parent directories).


#### Project Structure

```
firmware/AmazingHand_Serial/
├── CMakeLists.txt              # Top-level project configuration
├── sdkconfig.defaults          # Default Kconfig configuration
├── main/
│   ├── CMakeLists.txt
│   └── main.c                  # FreeRTOS dual tasks + initialization (glue layer)
└── components/
    ├── hand_servo/             # Servo driver (LEDC PWM + calibration data)
    ├── hand_gestures/          # Gesture parameter macros + gesture functions + left/right-hand control
    └── hand_protocol/          # Serial frame parsing + command dispatch
```

#### Build Environment

- ESP-IDF **v6.x** (recommended) or v5.x
- Target chip: **ESP32-S3**
- `idf.py` environment variables configured

#### Build and Flash

```bash
cd firmware/AmazingHand_Serial

# 1. Set the target chip (first time, or after changing chips)
idf.py set-target esp32s3

# 2. Build
idf.py build

# 3. Flash (Windows: use the COM port, e.g. COM3)
idf.py -p COM3 flash

# 4. Serial monitor (optional, baud rate 115200)
idf.py -p COM3 monitor
```

> After modifying any source under `components/` or `main/`, simply re-run `idf.py build && idf.py -p COM3 flash`.

### 3.3 Calibration (Optional, Recommended for First Use)

The servo center positions and pulse widths must be calibrated for the actual mechanism. There are two methods:

- **ESP-IDF Edition**: edit `middle_pos[8]` (line 40) and `min_pw/mid_pw/max_pw[8]` (lines 45-47) in `components/hand_servo/hand_servo.c`

After calibration, rebuild and re-flash the firmware.

---

## 4. Serial Communication Protocol

### 4.1 Physical Layer

| Parameter | Value |
|------|-----|
| Interface | USB Serial (UART0) |
| Baud rate | **115200** |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Flow control | None |

### 4.2 Frame Format

#### Host → ESP32 (Command Frame)

```
┌────────┬────────┬──────────┬────────────────┬──────────┐
│  0xAA  │ CMD_ID │ DATA_LEN │ DATA[0 .. N-1] │ CHECKSUM │
│ 1 Byte │ 1 Byte │  1 Byte  │    N Bytes     │  1 Byte  │
└────────┴────────┴──────────┴────────────────┴──────────┘
  Header   Cmd ID   Data Len       Payload    Checksum
```

- **Frame header**: fixed `0xAA`, marks the start of a frame
- **CMD_ID**: command number (see [Command Reference](#5-command-reference))
- **DATA_LEN**: number of bytes in the data payload (0-8; frames longer than 8 bytes are invalid)
- **DATA**: data payload; its length is determined by DATA_LEN
- **CHECKSUM**: `CMD_ID ^ DATA_LEN ^ DATA[0] ^ ... ^ DATA[N-1]` (XOR checksum)

> If DATA_LEN = 0, then CHECKSUM = CMD_ID.

#### ESP32 → Host (Response Frame)

```
┌────────┬────────┬────────┬──────────┐
│  0xBB  │ CMD_ID │ STATUS │ CHECKSUM │
│ 1 Byte │ 1 Byte │ 1 Byte │  1 Byte  │
└────────┴────────┴────────┴──────────┘
  Header   Cmd ID   Status   Checksum
```

- **Frame header**: fixed `0xBB`
- **CMD_ID**: original command number
- **STATUS**: status code (see the table below)
- **CHECKSUM**: `CMD_ID ^ STATUS`

#### Status Codes

| STATUS | Meaning | Description |
|--------|------|------|
| 0x00 | OK | Command accepted; execution started |
| 0x01 | Invalid command | CMD_ID is not in the command table |
| 0x02 | Parameter error | Data length or content is incorrect |
| 0x03 | Busy | A gesture is executing; new commands are temporarily rejected |
| 0x10 | Complete | Gesture execution finished |

### 4.3 Communication Timing

```
Host                          ESP32
 │                              │
 │──── [AA 01 00 01] ────────→│  Send "Rock" command
 │                              │
 │←─── [BB 01 00 01] ─────────│  ACK: command accepted
 │                              │
 │                      (executing gesture)
 │                              │
 │←─── [BB 01 10 11] ─────────│  Complete: gesture finished
 │                              │
 │──── [AA 02 00 02] ────────→│  Send "Scissors" command
 │                              │
 │←─── [BB 02 00 02] ─────────│  ACK
 │                              │
```

### 4.4 Stopping Gestures & Frame Timeout

- Sending `[AA FF 00 FF]` interrupts the currently executing gesture at any time
- If the ESP32 does not receive a complete frame within 200 ms, it automatically discards it (preventing a lost byte from causing permanent desynchronization)
- Frames with a mismatched checksum are silently discarded; the host should implement timeout-based retransmission

### 4.5 Left/Right Hand Mode

Right-hand mode is the default. Send `[AA F1 01 02 F2]` to switch to the left hand, and `[AA F1 01 01 F1]` to switch back to the right hand. The hand side affects the thumb's direction of motion (in gestures that involve the thumb, such as Rock, Scissors, Thumbs Up, OK, and Pinch).

---

## 5. Command Reference

### 5.1 Gesture Commands (0x01-0x0A, 0x0C)

These commands require no data payload (DATA_LEN=0); the ESP32 executes the corresponding gesture immediately upon receipt.

| Command | HEX Frame | Response | Description |
|------|--------|------|------|
| Rock | `AA 01 00 01` | `BB 01 00 01` → `BB 01 10 11` | All fingers clenched |
| Scissors | `AA 02 00 02` | `BB 02 00 02` → `BB 02 10 12` | Index and middle fingers extended |
| Paper | `AA 03 00 03` | `BB 03 00 03` → `BB 03 10 13` | All fingers extended |
| Thumbs Up | `AA 04 00 04` | `BB 04 00 04` → `BB 04 10 14` | Thumb raised |
| Taunt 1 | `AA 05 00 05` | `BB 05 00 05` → `BB 05 10 15` | Wag the index finger (about 2.5 s) |
| Taunt 2 | `AA 06 00 06` | `BB 06 00 06` → `BB 06 10 16` | Wiggle the ring finger (about 2.5 s) |
| Open | `AA 07 00 07` | `BB 07 00 07` → `BB 07 10 17` | All fingers extended |
| Fist | `AA 08 00 08` | `BB 08 00 08` → `BB 08 10 18` | All fingers closed |
| OK | `AA 09 00 09` | `BB 09 00 09` → `BB 09 10 19` | OK gesture |
| Pinch | `AA 0A 00 0A` | `BB 0A 00 0A` → `BB 0A 10 1A` | Pinch gesture |
| Point | `AA 0C 00 0C` | `BB 0C 00 0C` → `BB 0C 10 1C` | Index finger extended in a pointing motion |

### 5.2 Direct Drive Command (0xF0)

Directly control the angles of the 8 servos. The 8 data bytes correspond to servos 1-8 respectively; each byte ranges from 0 to 180.

**Example: center all servos (90°)**

```
Send: AA F0 08 5A 5A 5A 5A 5A 5A 5A 5A F8
       │  │  │  └── 8 × 0x5A (90°) ──┘  │
       │  │  │                            └── CHECKSUM
       │  │  └── DATA_LEN = 8
       │  └── CMD_DIRECT_DRIVE
       └── Frame header
```

Checksum = `F0 ^ 08 ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A` = `F8`

> The eight identical 0x5A bytes XOR in pairs to 0x00; the final result is `0xF0 ^ 0x08 ^ 0x00 = 0xF8`

**Example: index finger extended (servo 1 = 170°, servo 2 = 10°), all others centered (90°)**

```
Send: AA F0 08 AA 0A 5A 5A 5A 5A 5A 5A 58
               └─170°  └─10°
```

### 5.3 Set Left/Right Hand (0xF1)

One data byte: `0x01` = right hand, `0x02` = left hand.

```
Set right hand: AA F1 01 01 F1
Set left hand:  AA F1 01 02 F2
```

### 5.4 Control Commands

| Command | HEX Frame | Description |
|------|--------|------|
| NOP | `AA 00 00 00` | Link test; returns `BB 00 00 00` immediately |
| Repeat | `AA FE 00 FE` | Repeat the previous gesture |
| Stop | `AA FF 00 FF` | Immediately abort the current gesture |

### 5.5 Response Quick Reference

When an invalid command is received (using the nonexistent command 0xFC as an example):

```
Send:     AA FC 00 FC
Response: BB FC 01 FD    (STATUS=0x01 invalid command)
```

> Checksum verification: `FC ^ 00 = FC`; for the response, `FC ^ 01 = FD`

---

## 6. Host Software Tutorial

The module's `tools/` directory provides two host-side tools:

| Tool | File | Type | Purpose |
|------|------|------|------|
| **GUI** | `tools/hand_gui.py` / packaged exe | Visual | Perform gestures with buttons, direct-drive with sliders, logging |
| **Command-line test** | `tools/serial_test.py` | Scriptable | Send gestures / single-servo commands / sweeps; automated testing |

> Both only require `pyserial`. Install with: `pip install -r tools/requirements.txt`

### 6.1 Visual GUI (Recommended)

#### Run from Source (Recommended)

```bash
# 1. Install dependencies
pip install -r tools/requirements.txt

# 2. Run
python tools/hand_gui.py
```

> If you need an exe that runs without Python installed, you can package one yourself with PyInstaller (see [Usage Tutorial](gui_usage.md), Section 5).

#### GUI Usage Steps

1. **Select the serial port**: choose the COM port corresponding to the ESP32 in the drop-down at the top (check Windows Device Manager)
2. **Click "Connect"**: the status light turns green, the log area shows "Connected", and a NOP link test is sent automatically
3. **Gesture commands**: click the "Rock", "Scissors", "Paper", "Thumbs Up", "OK", etc. buttons, and the robotic hand performs the corresponding gesture
4. **Left/right hand**: check "Right Hand" / "Left Hand" to switch the thumb's mirror direction
5. **Servo direct drive**: drag the 8 sliders to control each servo's angle in real time (0-180°)
6. **Finger differential control** (recommended): each finger has two sliders — **Bend/Extend** drives the finger's two servos differentially in opposite directions (bending and extending), while **Swing Right/Swing Left** drives them in the same direction to swing the finger. The two degrees of freedom are independent and updated synchronously
7. **Repeat / Stop**: repeat the previous gesture / immediately abort the current gesture
8. **Communication log**: shows sent/received frames and response status in real time at the bottom

### Finger Differential Control

Each finger is **driven differentially by two servos**, giving two orthogonal degrees of freedom:

| Slider | Function | Mechanical Effect |
|--------|------|----------|
| **Bend ◀▶ Extend** | The two servos rotate in opposite directions (differential) | The finger bends or extends |
| **Swing Right ◀▶ Swing Left** | The two servos rotate in the same direction | The finger swings left or right |

- The **Bend/Extend** slider ranges from -70 to +70 (0 = neutral, +70 = fully extended, -70 = fully bent)
- The **left/right swing** slider ranges from 60 to 120 (90 = neutral, 60 = swing right, 120 = swing left)
- Servo angle = `swing ± bend`; both servos are updated **synchronously** and a direct-drive command is sent

> Example (index finger, GPIO4/5): with the bend slider at +70 and the swing at 90 → servo 4 = 160°, servo 5 = 20° (fully extended); with bend at -70 → servo 4 = 20°, servo 5 = 160° (fully bent).

### 6.2 Scripted Testing (serial_test.py)

#### Command-Line Usage

```bash
# Show help
python tools/serial_test.py

# Link test
python tools/serial_test.py COM3 nop

# Send a gesture
python tools/serial_test.py COM3 rock        # Rock
python tools/serial_test.py COM3 thumbs_up    # Thumbs Up
python tools/serial_test.py COM3 index        # Point
python tools/serial_test.py COM3 open         # Open
python tools/serial_test.py COM3 close        # Fist

# Direct-drive a single servo
python tools/serial_test.py COM3 servo 1 90   # Servo 1 → 90°

# Center all servos
python tools/serial_test.py COM3 mid

# Set left/right hand
python tools/serial_test.py COM3 hand L       # Left hand
python tools/serial_test.py COM3 hand R       # Right hand

# Sweep / self-test
python tools/serial_test.py COM3 sweep 1      # Sweep servo 1
python tools/serial_test.py COM3 test         # Test each servo in turn
```

#### Interactive Mode

```bash
python tools/serial_test.py COM3
```

This enters a REPL where you can type shorthand commands directly (e.g. `servo 3 180`, `rock`, `mid`, `quit`).

### 6.3 Manual Testing with a Serial Terminal (Optional)

**CoolTerm** (macOS/Windows/Linux):

1. Open CoolTerm, `Options` → set the baud rate to 115200, 8N1
2. `Connection` → `Send String` → select `Hex`
3. Enter `AA 01 00 01` → Send → the robotic hand performs "Rock"
4. Watch the response area display `BB 01 00 01 ... BB 01 10 11`

**SerialTool** (macOS):

```bash
brew install serialtool
echo -ne '\xAA\x01\x00\x01' > /dev/cu.usbserial-0001
```

### 6.4 Python Control Script (Custom Development)

```python
#!/usr/bin/env python3
"""Dexterous hand serial control - Python host example"""
import serial
import time

SERIAL_PORT = "/dev/cu.usbserial-0001"  # Change this to the actual port
BAUD_RATE   = 115200

# Command definitions (match the firmware command set)
CMD = {
    "nop":       0x00,
    "rock":      0x01,
    "scissors":  0x02,
    "paper":     0x03,
    "thumbs_up": 0x04,
    "taunt1":    0x05,
    "taunt2":    0x06,
    "open":      0x07,
    "close":     0x08,
    "ok":        0x09,
    "pinch":     0x0A,
    "index":     0x0C,
    "direct":    0xF0,
    "set_side":  0xF1,
    "repeat":    0xFE,
    "stop":      0xFF,
}

def calc_checksum(cmd_id, data=b""):
    """Compute the XOR checksum (CMD ^ LEN ^ DATA[0..N])"""
    result = cmd_id ^ len(data)
    for b in data:
        result ^= b
    return result & 0xFF

def send_command(ser, cmd_id, data=b""):
    """Send a command frame and return (ack_status, completion_status)"""
    data_len = len(data)
    checksum = calc_checksum(cmd_id, data)
    frame = bytes([0xAA, cmd_id, data_len]) + data + bytes([checksum])
    ser.write(frame)
    print(f"Send: {frame.hex(' ').upper()}")

def read_response(ser, timeout=1.0):
    """Read one response frame [0xBB CMD STATUS CKSUM]"""
    ser.timeout = timeout
    while True:
        b = ser.read(1)
        if not b:
            return None
        if b[0] == 0xBB:
            buf = ser.read(3)
            if len(buf) == 3:
                expected = buf[0] ^ buf[1]
                if expected == buf[2]:
                    return bytes([0xBB]) + buf
    return None

def set_side(ser, side):
    """Set the hand side: side='R' for right hand, side='L' for left hand"""
    val = 0x01 if side.upper() == 'R' else 0x02
    send_command(ser, CMD["set_side"], bytes([val]))

def direct_drive(ser, angles):
    """Direct-drive the 8 servos: angles is a list of eight 0-180 values"""
    data = bytes([min(180, max(0, a)) for a in angles[:8]])
    send_command(ser, CMD["direct"], data)

# ===== Usage example =====
if __name__ == "__main__":
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(1)  # Wait for the ESP32 to finish resetting

    # 1. Link test
    print("=== NOP link test ===")
    send_command(ser, CMD["nop"])

    # 2. Rock-paper-scissors game
    print("\n=== Rock-paper-scissors: Rock → Scissors → Paper ===")
    for name in ["rock", "scissors", "paper"]:
        send_command(ser, CMD[name])
        time.sleep(0.5)

    # 3. Thumbs Up gesture
    print("\n=== Thumbs Up ===")
    send_command(ser, CMD["thumbs_up"])

    # 4. Stop test
    print("\n=== Stop test ===")
    send_command(ser, CMD["taunt1"])  # Start wagging the index finger
    time.sleep(0.3)
    send_command(ser, CMD["stop"])    # Stop immediately

    # 5. Direct-drive mode: center all servos
    print("\n=== Direct drive: center all ===")
    direct_drive(ser, [90] * 8)

    ser.close()
```

---

## 7. Gesture Tracking

Use a **camera to recognize the hand in real time** and drive the dexterous hand's finger bend/extend and left/right swing motions. Based on the official AmazingHand hand-tracking algorithm (MediaPipe 21-point landmarks + 3D world-coordinate rotation).

### 7.1 How It Works

- The camera points at the palm → MediaPipe detects 21 hand landmarks
- A local hand coordinate system is constructed, and the 3D vectors of the four fingertips are computed
- Fingertip vectors → (flex, base) differential parameters for each finger → sent to the servos via the existing direct-drive protocol

### 7.2 Environment Requirements

Gesture tracking requires **64-bit Python + mediapipe 0.10.14** (the older solutions API; only it provides 3D world coordinates):

| Dependency | Version |
|------|------|
| Python | 64-bit 3.12 |
| mediapipe | 0.10.14 |
| numpy | <2.0 |
| scipy | >=1.9 |
| opencv-python | >=4.10 |
| Pillow | >=10.0 |

> **Note**: The current default environment is 32-bit Python, which cannot install mediapipe. Install a separate 64-bit Python 3.12 (for example in `D:\Python312-64` on the D drive; it coexists fully with the existing 32-bit installation without conflict).

### 7.3 One-Click Setup

1. Install 64-bit Python 3.12 (download the 64-bit installer from [python.org](https://www.python.org/downloads/) and install it to `D:\Python312-64`)
2. Run **`tools/setup_tracking.bat`** in the module root directory
   - Automatically locates 64-bit Python
   - Creates the `tools/tracking_env` virtual environment
   - Installs mediapipe 0.10.14 and other dependencies
   - Verifies the installation

### 7.4 Usage Steps

1. Launch the GUI with the tracking environment:
   ```
   tools/tracking_env/Scripts/python tools/hand_gui.py
   ```
2. Connect the serial port (select the COM port corresponding to the ESP32)
3. In the "Gesture Tracking" panel, select the camera index (default 0)
4. Click **"Start Tracking"** → the camera image appears in the panel
5. Aim your palm at the camera:
   - **Bend/extend your fingers** → the corresponding fingers of the dexterous hand bend/extend
   - **Turn your palm left/right** → the dexterous hand's fingers swing left/right
6. Click **"Stop Tracking"** to finish

> If no hand is detected, the panel shows "No hand detected"; once a hand is detected, it shows "Hand detected: Right/Left".

### 7.5 Parameter Calibration

The mapping coefficients are at the bottom of `hand_tracking.py` (`FLEX_SCALE` / `BASE_SCALE`):

```python
FLEX_SCALE = 80.0    # Fingertip z component → bend/extend (flex)
BASE_SCALE = 30.0    # Fingertip x component → left/right swing (base)
```

If the bend/extend range is insufficient or the direction is reversed, adjust `FLEX_SCALE`; if the left/right swing range is insufficient or the direction is reversed, adjust `BASE_SCALE` (the sign controls the direction).

---

## 8. Gesture Parameter Tuning

### 8.1 Parameter Locations

Each gesture's angle offsets are defined with `#define` macros. **No logic code needs to change** — only the values.

- **ESP-IDF Edition**: the "Gesture Parameters (User-Adjustable)" section at the top of `components/hand_gestures/hand_gestures.c`

### 8.2 Parameter Meaning

```c
// Example: Rock gesture
#define ROCK_IDX_OFF1    70    // Index finger joint 1 offset
#define ROCK_IDX_OFF2   -70    // Index finger joint 2 offset
```

- **Positive values = bend/close**, **negative values = extend/open**
- Each finger has 2 offsets, relative to `middle_pos` (default 90°)
- Differential structure: the difference between the two servo offsets produces extension/contraction, while their common-mode component produces left/right deflection

### 8.3 Tuning Steps

1. Find the `#define` macros for the corresponding gesture
2. Change the values (increase → greater range; decrease → smaller range)
3. Rebuild and re-flash, then test the result with the host software
4. Fine-tune repeatedly until the motion looks natural

---

## 9. FAQ

### Q1: The host cannot connect to the serial port?

1. Confirm that the ESP32 is connected to the computer via Type-C
2. Check that the COM port number in Device Manager matches the one selected in the GUI
3. Confirm the baud rate is 115200
4. Close any other software that is using the serial port

### Q2: No response after sending a command?

1. First send `AA 00 00 00` (NOP); you should receive `BB 00 00 00`
2. Confirm that the firmware has been flashed and the target chip is ESP32-S3
3. Check the wiring (whether GND is properly common-grounded)

### Q3: The gesture range is wrong or the direction is reversed?

Go to gesture parameter tuning (see [Section 8](#8-gesture-parameter-tuning)) and adjust the corresponding macros.

### Q4: Which gestures does left/right hand mode affect?

Gestures that involve the thumb, such as Rock, Scissors, Thumbs Up, OK, and Pinch — switching the hand side mirrors the thumb's direction.

### Q5: A finger is stuck and cannot extend?

Before executing any contraction-type gesture, the firmware automatically "opens the whole hand first, then closes it" to prevent fingers from being blocked by the previous gesture. If a finger still gets stuck, check the mechanical assembly or reduce the contraction range.
