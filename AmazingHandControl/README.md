English | [简体中文](README_CN.md)

# AmazingHand Python Tools

Python GUI and command-line tools to control the [AmazingHand](https://github.com/pollen-robotics/AmazingHand) robot by Pollen Robotics, using 8× Feetech SCS0009 servos over a serial bus controller.

> **Both hands are supported.** At startup you pick right (servo IDs 1-8) or left (servo IDs 11-18); `--hand` skips the prompt. Pose presets are shared between hands — each hand carries its own servo mapping, mounting offset and raw targets in `data/config.yaml`. See [Hand selection](#hand-selection).

---

## Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Calibration](#calibration)
- [Running the GUI](#running-the-gui-amazing_hand_guipy)- [Running the CLI](#running-the-cli-amazing_hand_cmdpy)
- [Configuration](#configuration)
- [Poses and Sequences](#poses-and-sequences)
- [Testing](#testing)
- [Servo ID Configuration](#servo-id-configuration)

---

## Project Structure

```
amazing_hand_gui.py   – Main GUI application
amazing_hand_cmd.py   – Command-line interface
hand_logic.py         – Shared business logic (no UI dependencies)
pyproject.toml        – Package metadata, dependencies, pytest config
data/
  config.yaml         – App settings (serial ports, limits, raw position targets)
  hand_config.yaml    – Saved poses and sequences
docs/
  REQUIREMENTS.md     – Requirements & acceptance criteria
  user_manual.md      – User manual
  CONFIG_FORMAT.md    – Config file format reference
  scs_servo_protocol.md – SCS0009 register reference
  CHANGES.md          – Changelog: what was changed vs. the original, and why
  优化说明.md          – Same document, in Chinese
tests/
  test_hand_logic.py      – Unit tests for hand_logic (155 tests)
  test_gui_utils.py       – Unit tests for GUI utilities (51 tests)
  test_cmd.py             – Unit tests for CLI (42 tests)
  test_integration.py     – Integration tests (14 tests)
  test_system.py          – System tests via subprocess (22 tests)
  test_system_hardware.py – Hardware tests (33 tests, requires --hardware)
  test_cmd_hardware.py    – CMD hardware tests (21 tests, requires --hardware)
```

## Requirements

- Python 3.10 or newer (Tkinter must be included for the GUI)
- External 5 V power supply for the eight servos
- USB serial bus adapter and driver installed on your computer

## Installation

Install with pip (recommended — uses `pyproject.toml`):

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

For development and testing:

```bash
pip install -r requirements-dev.txt
```

---

## Calibration

The servo angle system, pose presets and the middle position all depend on the physical hand. Everything lives in `data/config.yaml` — no code changes are needed to re-calibrate.

### Hand selection

The two hands use different servos and different mechanics, so pick one before the GUI opens:

```
  AmazingHand — which hand?
    1 = right hand  (servo IDs 1-8)
    2 = left hand   (servo IDs 11-18)
  Enter 1 or 2 [1]:
  LEFT hand — servo IDs 11-18
    Ring (11, 12)  Middle (13, 14)  Pointer (15, 16)  Thumb (17, 18)
    middle position raw: [571, 451, 571, 451, 571, 451, 571, 451]
```

Or skip the prompt:

```bash
python amazing_hand_gui.py --hand left
python amazing_hand_cmd.py --pose victory --hand left
```

Omitting `--hand` uses the `hand:` value in `data/config.yaml`.

**Why a hand is not just a set of IDs.** Beyond the servo numbering (right 1-8, left 11-18, with the left hand's fingers numbered in mirrored order — ring first), the left hand differs in two mechanical ways, both handled automatically:

| | Right | Left |
|---|---|---|
| Servo IDs | 1-8 | 11-18 |
| Finger → ID | index `1,2` / middle `3,4` / ring `5,6` / thumb `7,8` | ring `11,12` / middle `13,14` / index `15,16` / thumb `17,18` |
| Vendor `MiddlePos` | `[451, 571, …]` | `[571, 451, …]` |
| Mounting offset | 0° | **−35.16°** (`hands.left.angle_offset`) |
| Per-finger servo pair | `(a, b)` | **`(b, a)`** (`hands.left.mirror_pose`) |

Skip either of the last two and gestures come out wrong: the mounting offset shifts every finger by 35°, and without the pair swap a spread gesture inverts (a V-sign collapses, an open hand splays).

`data/hand_config.yaml` is **shared** and always stored in right-hand order; the left hand's conversion is applied on the way out and inverted again when saving.

**Calibrating a new hand.** Start from the values in `hands.left` as a template, then verify in this order:

1. Press **Middle position** and check the `Current (0-1023)` row reads the expected raw values
2. Press **Open All** / **Close All** — travel should reach the mechanical stops without stalling
3. Try a spread gesture (`victory` opens into a V, `greeting` brings three fingers together)

If something is off, the knob to turn is:

| Symptom | Change |
|---|---|
| Middle position reads wrong | `hands.<name>.raw_positions.middle` |
| Spread direction inverted | `hands.<name>.mirror_pose` |
| Travel too short / too far | `hands.<name>.raw_positions.open` / `close` |

### Angle convention

The GUI and CLI work in **degrees**, mapped to the servo's internal raw position by the rustypot driver:

```
raw = 1024 × angle / 300° + 511        (0.29297°/step, raw range 0–1023)
```

| Angle | Meaning |
|---|---|
| **−35°** | fully open (extended) |
| **0°** | neutral, fingers lightly curled |
| **+75°** | fully closed (fist) |

Even-numbered servo IDs are **inverted** relative to odd ones, so a single pose value drives both servos of a finger in opposite directions. You do not need to handle this yourself — it is applied automatically.

### Limits

```yaml
limits:
  servo_min: -75      # absolute travel limits for any servo command
  servo_max: 75
  base_min: -75       # open/close slider range
  base_max: 75
  side_min: -35       # left/right slider range
  side_max: 35
```

`side_min`/`side_max` control the *lateral* spread. They are normalised (`u = |side_offset| / |side_min|`), so changing them alone rescales the slider without changing the physical spread. To actually change how far the fingers splay, update `auto_extremes` as well.

### Raw position targets

The three global position buttons drive the servos to **exact raw values** rather than going through the angle model:

```yaml
raw_positions:              # index 0 -> servo ID 1 ... index 7 -> servo ID 8
  open:   [260, 760, 260, 760, 260, 760, 260, 760]
  close:  [760, 260, 760, 260, 760, 260, 760, 260]
  middle: [451, 571, 451, 571, 451, 571, 451, 571]
```

- `open` / `close` — the mechanical end stops. Measure these by driving the servos with the vendor's Feetech debug tool.
- `middle` — the **calibrated mechanical middle** (`MiddlePos` in the vendor's Arduino demo). This is *not* the midpoint of open and close: it sits ±60 raw (±17.6°) away from raw 511.

> These are per-hand values. The vendor's own comment is *"replace values by your calibration results"*.

**How to verify:** the Servo Feedback panel has a `Current (0-1023)` row showing the live raw position. Press **Middle position** and check the row reads `451, 571, 451, 571, …`.

### Keyboard / slider shortcut summary

| Control | Range |
|---|---|
| Open/close slider (vertical) | −75 … +75 |
| Left/right slider (horizontal) | −35 … +35 |
| Speed | 1 (slow) … 6 (fast) |

Speeds are passed to the servo as rad/s via the driver, so the 1–6 scale roughly maps to 57–344 °/s. Under load the real speed is about **70 %** of that — worth remembering when choosing sequence delays.

---

## Running the GUI (`amazing_hand_gui.py`)

If installed with pip:

```bash
amazing-hand-gui
amazing-hand-gui --port /dev/ttyUSB0
```

Or run directly:

```bash
python amazing_hand_gui.py
python amazing_hand_gui.py --port /dev/ttyUSB0
```

The port dropdown is populated from the ports actually present on this machine (via pyserial, or the Windows registry as a fallback), so adapters on high COM numbers show up. It is editable, so you can type a port directly. If the configured default isn't plugged in, the GUI starts on the first real port instead; pass `--port` to pin one explicitly.

### Features

- Per-finger sliders for open/close and left/right, in **Auto** (base + side) or **Raw** (direct servo angles) mode
- Per-finger Open / Close / Center buttons
- Per-finger speed selection (1–6) with a global speed sync dropdown
- Keyboard shortcuts for quick precise movements
- **Global position buttons**: Open All, Close All, Center All, and Middle position
- Pose and sequence management using `data/hand_config.yaml`
- Delete saved poses directly from the GUI (🗑 Delete button)
- Live servo telemetry charts (position, load, temperature, voltage)
- Servo Feedback table, including live **raw** position (0–1023) for calibration checks

### Keyboard Controls

- **1-4**: Select finger (Ring, Middle, Pointer, Thumb)
- **Arrow Keys**: Move selected finger
  - Up/Down: Close/Open
  - Left/Right: Move laterally
- **Modifiers**:
  - Normal: 1° per keypress (precise)
  - Shift: 5° per keypress (normal)
  - Ctrl: 10° per keypress (fast)
- **Quick Actions**:
  - Q: Fully close selected finger
  - E: Fully open selected finger
  - C: Center left/right position

### Global Controls

| Button | Open/close | Left/right |
|---|---|---|
| ✋ **Open All** | every finger to raw `open` | centred |
| ✊ **Close All** | every finger to raw `close` | centred |
| ⊙ **Center All** | unchanged | centred |
| ⊙ **Middle position** | every finger to raw `middle` | — |

**Global Speed** dropdown (1–6) instantly applies the chosen speed to all finger controls, keeping per-finger sliders in sync.

The three raw-value buttons (`Open All`, `Close All`, `Middle position`) bypass the angle model, so the sliders afterwards show the *nearest representable* value rather than an exact one. Touching a slider will move the hand by up to ~0.3° from the raw target — that is the deliberate trade-off for hitting the calibrated positions exactly.

> Known caveat: `Center All` does not skip fingers that are in **Raw** mode, so it will overwrite manually-set raw angles. The per-finger `⊙ Center` button does skip them.

---

## Running the CLI (`amazing_hand_cmd.py`)

A standalone command-line tool for applying poses and playing sequences without the GUI. It reads the same `data/hand_config.yaml` used by the GUI, and sends **exactly** the stored pose values — identical to what the GUI sends.

### Linux: serial port access

The USB serial adapter typically appears as `/dev/ttyACM0` (Waveshare / CDC-ACM) or `/dev/ttyUSB0` (FTDI / CH340).

Find it with:
```bash
ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
# or
dmesg | grep -E 'ttyACM|ttyUSB' | tail -5
```

If you get a **Permission denied** error, add your user to the `dialout` group and log out/in:
```bash
sudo usermod -aG dialout $USER
```

### If installed with pip

```bash
amazing-hand-cmd --list
amazing-hand-cmd --pose open
amazing-hand-cmd --sequence demo --loop
amazing-hand-cmd --pose open --speed 6
# Override port if needed:
amazing-hand-cmd --pose open --port /dev/ttyUSB0
```

### Run directly

```bash
python amazing_hand_cmd.py --list
python amazing_hand_cmd.py --pose open
python amazing_hand_cmd.py --pose close --speed 6
python amazing_hand_cmd.py --sequence demo
python amazing_hand_cmd.py --sequence wave --loop
python amazing_hand_cmd.py --port /dev/ttyUSB0 --pose open
python amazing_hand_cmd.py --list --config /path/to/hand_config.yaml
```

### Options

| Option | Default | Description |
|---|---|---|
| `--pose NAME` | – | Apply the named pose |
| `--sequence NAME` | – | Play the named sequence |
| `--list` | – | List all poses and sequences |
| `--loop` | off | Loop sequence until Ctrl+C |
| `--speed N` | `3` | Servo speed 1 (slow) … 6 (fast) |
| `--port PORT` | `/dev/ttyACM0` (Linux) / `COM9` (Win) | Serial port |
| `--baudrate N` | `1000000` | Baud rate |
| `--config PATH` | `data/hand_config.yaml` | Alternative config file |
| `--hand {right,left}` | `config.yaml`'s `hand` | Hand to drive (right = IDs 1-8, left = IDs 11-18) |

Torque is automatically disabled on all servos when the script exits (including Ctrl+C).

> The CLI has no `--config` equivalent for `data/config.yaml`; it is always loaded from the project directory.

---

## Configuration

### `data/config.yaml`

| Section | Purpose |
|---|---|
| `serial` | Default port per platform, baud rate, baud rate options |
| `servos` | Servo ID pairs per finger |
| `limits` | Angle ranges for servos and the two sliders |
| `speeds` | Default / min / max on the 1–6 speed scale |
| `auto_extremes` | Servo positions at the left/right extremes of the side slider |
| `raw_positions` | Exact raw targets for the global position buttons |
| `paths` | Location of the poses/sequences file |

### Servo ↔ finger mapping

| Finger | Servo IDs | Pose array indices |
|---|---|---|
| Pointer | 1, 2 | 4, 5 |
| Middle | 3, 4 | 2, 3 |
| Ring | 5, 6 | 0, 1 |
| Thumb | 7, 8 | 6, 7 |

**Pose arrays are ordered Ring, Middle, Pointer, Thumb — not by servo ID.** This is the single easiest thing to get wrong when editing `hand_config.yaml` by hand.

> The docstring at the top of `amazing_hand_cmd.py` claims "index 0→servo1 … 7→servo8". That comment is **incorrect**; the table above reflects what the code actually does.

---

## Poses and Sequences

All poses and sequences are stored in `data/hand_config.yaml`. The GUI creates the file automatically if it is missing.

### Saving Poses

1. Position fingers using sliders or keyboard shortcuts
2. Enter a name in the "Name:" field
3. Click "➕ Add New" in the Pose Management section

Speeds only affect how the sliders move; saved poses store the 8 servo positions only.

### Loading / Deleting Poses

- Select from the dropdown and click **✓ Apply** to move the hand to that pose
- Click **🗑 Delete** (right of Apply) to permanently remove the selected pose after confirmation

### Sequence Management

1. Click "🔧 Manage" in the Sequence Player to open the sequence manager
2. **Saved Sequences** (left panel)
   - View, execute, edit, or delete existing sequences
   - Double-click or click "▶ Execute" to run a saved entry once
3. **Sequence Builder** (right panel)
   - Double-click poses from "Available Poses" to add them as steps
   - Choose individual servo speeds and delays per step; steps are stored as `"pose:s1,s2,...,s8|delay"`
   - Use ↑/↓ to reorder steps, or insert a pause with the "⏱ Delay" button
   - Enter a name and click "💾 Save Sequence"; use "▶ Execute" to test without saving
4. Back in the main window, use the **Loop** checkbox for continuous playback

### Step format

```
pose_name:speed1,speed2,...,speed8|delay
```

- `speed1..speed8` — one speed (1–6) per servo, in pose order
- `delay` — how long to wait before the next step, e.g. `0.6s`. **Optional**; when omitted the GUI falls back to a fixed auto-wait.
- A standalone pause is written as `SLEEP:1.0s` (no comma-separated speeds)

**Choosing delays.** The driver reports when servos stop moving, but sequence playback uses fixed delays. Budget roughly `travel_degrees / (speed × 57.3 × 0.7)` seconds and leave headroom — moves longer than ~130° at speed 3 need more than 1.0 s on a loaded hand.

### YAML format example

```yaml
poses:
  open:
    positions: [-35, -35, -35, -35, -35, -35, -35, -35]
  close:
    positions: [75, 75, 75, 75, 75, 75, 75, 75]
  ring_close:                 # Ring closed, everything else open
    positions: [75, 75, -35, -35, -35, -35, -35, -35]

sequences:
  demo:
    steps:
      - "open:3,3,3,3,3,3,3,3|2.0s"
      - "close:6,6,6,6,6,6,6,6|2.0s"
      - "ok:3,3,3,3,3,3,3,3|1.0s"
      - "victory:3,3,3,3,3,3,3,3|1.0s"
      - "greeting:3,3,3,3,3,3,3,3|1.5s"
      - "close:6,6,6,6,6,6,6,6|2.0s"
  wave:
    steps:
      - "open:6,6,6,6,6,6,6,6|0.8s"
      - "wave_r:5,5,5,5,5,5,5,5|0.6s"
      - "wave_l:5,5,5,5,5,5,5,5|0.6s"
      - "open:5,5,5,5,5,5,5,5|0.8s"
  finger_roll:
    steps:
      - "open:6,6,6,6,6,6,6,6|0.5s"
      - "ring_close:5,5,5,5,5,5,5,5|0.6s"
      - "open:5,5,5,5,5,5,5,5|0.5s"
      - "middle_close:5,5,5,5,5,5,5,5|0.6s"
      - "open:5,5,5,5,5,5,5,5|0.5s"
```

Loop behavior is handled at runtime (GUI checkbox) and is not stored in YAML.

---

## Testing

The project includes 284 unit / integration / system tests plus 54 hardware tests.

### Run all tests (no hardware required)

```bash
pytest
```

### Run GUI + CLI hardware tests (requires connected servos)

```bash
pytest tests/test_system_hardware.py --hardware --port /dev/ttyACM0
pytest tests/test_cmd_hardware.py --hardware --port /dev/ttyACM0
# or both at once:
pytest tests/test_system_hardware.py tests/test_cmd_hardware.py --hardware
```

`test_system_hardware.py` verifies connection, pose apply, telemetry reads, individual finger open/close/wave, speed control, sequence execution, and movement detection.

`test_cmd_hardware.py` verifies the CLI layer end-to-end: pose positions, speed parameter, sequence steps, `wait_for_motion`, `--list` output, and torque disable.

See `docs/REQUIREMENTS.md` for the full requirements and acceptance criteria.

> Note: the non-hardware tests assert the **fallback defaults** in `hand_logic.py`, which still carry the original −40…110 scale. `data/config.yaml` overrides them at runtime, so the tests pass regardless of your calibration — but they do not validate your live settings.

---

## Servo ID Configuration

Tutorial for configuring servo IDs with Feetech software and the serial bus driver:
<https://www.robot-maker.com/forum/tutorials/article/168-brancher-et-controler-le-servomoteur-feetech-sts3032-360/>

Feetech software download:
<https://github.com/Robot-Maker-SAS/FeetechServo>

---

## Credits

Original project by [Betatester777](https://github.com/Betatester777/AmazingHandControl).
Hardware and reference firmware by [Pollen Robotics](https://github.com/pollen-robotics/AmazingHand).
