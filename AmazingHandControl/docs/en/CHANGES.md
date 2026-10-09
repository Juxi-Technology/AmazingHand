English | [Deutsch](../de/CHANGES.md) | [Español](../es/CHANGES.md) | [Français](../fr/CHANGES.md) | [Italiano](../it/CHANGES.md) | [日本語](../ja/CHANGES.md) | [한국어](../ko/CHANGES.md) | [Português (BR)](../pt-br/CHANGES.md) | [Português (PT)](../pt-pt/CHANGES.md) | [简体中文](../zh-hans/CHANGES.md) | [繁體中文](../zh-hant/CHANGES.md)

# AmazingHand Controller · Changelog & Rationale

What was changed relative to the original project, why, and what the result actually is.

Original project: `Betatester777/AmazingHandControl` (Python GUI + CLI for the AmazingHand)
Hardware: JuxiTechnology AmazingHand (8× Feetech SCS0009 servos, potentiometer feedback) — **both hands supported**, selected at startup

---

## Contents

1. [Re-calibrating the angle system](#1-re-calibrating-the-angle-system)
2. [Global buttons: driving exact raw positions](#2-global-buttons-driving-exact-raw-positions)
3. [New Middle position button](#3-new-middle-position-button)
4. [GUI and CLI disagreeing (the core bug)](#4-gui-and-cli-disagreeing-the-core-bug)
5. [Pose data corrections](#5-pose-data-corrections)
6. [Sequence player: timing and diagnostics](#6-sequence-player-timing-and-diagnostics)
7. [New raw position row in Servo Feedback](#7-new-raw-position-row-in-servo-feedback)
8. [**Left and right hand support**](#8-left-and-right-hand-support)
9. [Serial port auto-detection](#9-serial-port-auto-detection)
10. [Configuration reference](#10-configuration-reference)
11. [Measured results](#11-measured-results)
12. [File-by-file summary](#12-file-by-file-summary)

---

## 1. Re-calibrating the angle system

### 1.1 Angle limits: `0..110` → `-75..75`

The original was calibrated as `0° = open, 110° = closed`. This hand's actual travel lands in `-75..75`, so everything was re-calibrated.

**`data/config.yaml`**

| Key | Before | After |
|---|---|---|
| `servo_min` / `servo_max` | -40 / 110 | **-75 / 75** |
| `base_min` / `base_max` | 0 / 110 | **-75 / 75** |
| `side_min` / `side_max` | -40 / 40 | **-35 / 35** |
| `left_open` | `[32, -40]` | **`[32, -35]`** |
| `right_open` | `[-40, 32]` | **`[-35, 32]`** |
| `left_closed` / `right_closed` | `[110, 110]` | **`[75, 75]`** |
| `center_closed` | `[110, 110]` | **`[75, 75]`** |

**All 19 poses were re-scaled**, e.g. `open` from `[0]*8` to `[-35]*8`, `close` from `[110]*8` to `[75]*8`.

### 1.2 Lateral spread: `±40°` → `±35°`

The side slider normalises with `u = |side_offset| / |side_min|`, so changing the limit alone does **not** change how far the fingers actually splay — it only rescales the slider. To change the physical spread you must change `auto_extremes` as well. With both changed:

| | Before (±40) | After (±35) |
|---|---|---|
| Slider range | −40 … +40 | −35 … +35 |
| Full open, at the lateral extreme | `(32, -40)`, spread **72°** | `(32, -35)`, spread **67°** |

### 1.3 Matching the vendor's reference

The vendor's Arduino demo (`Amazing_RHand_Demo.ino`) converts like this:

```c
float Step = 0.293; // 300°/1024
sc.RegWritePos(1, MiddlePos[0] + Pos_1 / Step, 0, Speed);
```

And rustypot 1.4.2 (`src/servo/feetech/scs0009.rs`):

```rust
fn to_raw(value: f64) -> i16 {
    let a = (1024.0 * value / (300.0_f64.to_radians()) + 511.0) as i16;
    a.to_be()
}
```

**Conclusion: both sides use the same degree scale** (0.29297°/step, 300° full scale, raw 0–1023) — there is no ratio error. The only systematic difference is the zero point:

- rustypot always centres on raw **511**
- the vendor firmware uses a per-servo calibration value, `MiddlePos = {451, 571, 451, 571, 451, 571, 451, 571}`

They differ by **±60 raw = ±17.6°**. That is exactly what the "Middle position" button below addresses.

---

## 2. Global buttons: driving exact raw positions

### 2.1 The problem

The original `open_all()` / `close_all()` had hard-coded angles:

```python
def open_all(self):
    for finger in self.fingers:
        finger.pos_var.set(0)      # hard-coded 0
        finger.side_var.set(0)
        ...
def close_all(self):
    for finger in self.fingers:
        finger.pos_var.set(110)    # hard-coded 110
```

Those values come from the **old calibration scale** (0 = open, 110 = closed). After re-calibrating to `-35 / 75`:

- `open_all` set 0° → converts to raw **511**, i.e. roughly the mechanical middle — the fingers never opened
- `close_all` set 110° → clamped by `base_max = 75`, so it only reached 75, while the label still read 110°

### 2.2 The fix: a direct raw-position path

The angle path goes through the `base/side` interpolation model, which cannot hit an arbitrary raw value exactly (see section 4). So the global buttons got a path that writes raw servo positions directly.

**One important implementation detail:** this does *not* use rustypot's `sync_write_raw_goal_position`. Reading the macro-generated source shows the raw API writes `values.to_le_bytes()` straight to the wire, while the converting API applies `to_be()` first:

```rust
fn to_raw(value: f64) -> i16 { let a = (...) as i16; a.to_be() }
// sync_write_raw_*: values.iter().map(|v| v.to_le_bytes())   <- no to_be
```

Passing `451` would therefore emit `0xC301` (49921). Instead the code uses `sync_write_goal_position` (radians) and solves for the radians that land **exactly** on the target raw value, taking the midpoint of each raw step to avoid truncation error.

### 2.3 Raw targets for the three buttons

Added `raw_positions` to `data/config.yaml` (index 0 → servo ID 1):

```yaml
raw_positions:
  open:   [260, 760, 260, 760, 260, 760, 260, 760]
  close:  [760, 260, 760, 260, 760, 260, 760, 260]
  middle: [451, 571, 451, 571, 451, 571, 451, 571]
```

| Button | Action | Servo IDs 1–8 raw |
|---|---|---|
| ✋ Open All | fully extended | 260, 760, 260, 760, 260, 760, 260, 760 |
| ✊ Close All | fully closed | 760, 260, 760, 260, 760, 260, 760, 260 |
| ⊙ Center All | lateral re-centre (no change to open/close) | — |
| **Middle position** | **return to the calibrated middle** | 451, 571, 451, 571, 451, 571, 451, 571 |

> ⚠️ `raw_positions` are **per-hand calibration values**. The vendor's own comment is *"replace values by your calibration results"* — re-measure after swapping hands or servos.

### 2.4 The slider-sync trade-off

Raw targets bypass the `base/side` model, so they have no exact slider equivalent. After a button runs, the sliders are set to the nearest integer:

| Position | Slider shows |
|---|---|
| open | base = −73, side = 0 |
| close | base = +73, side = 0 |
| middle | base = −17, side = 0 |

The cost: touching a slider afterwards moves the hand by up to ~1 raw unit (0.3°) away from the target. That is deliberate — hitting the calibrated position exactly matters more.

---

## 3. New Middle position button

Placed to the right of `✋ Open All` / `✊ Close All` / `⊙ Center All`. It returns the hand to the **vendor-calibrated mechanical middle** (raw 451/571).

**Why it is needed:** the midpoint between `open_all` and `close_all` is *not* the mechanical middle. The vendor's middle is `MiddlePos`, which sits ±60 raw (±17.6°) away from raw 511. After power-up you want a well-defined, repeatable zero.

---

## 4. GUI and CLI disagreeing (the core bug)

### 4.1 Symptom

**The same pose produces a different hand motion when applied with the GUI's `✓ Apply` versus the CLI's `--pose`.**

### 4.2 Root cause

The GUI applied poses through:

```
set_positions(p1, p2)  →  decompose into (base, side), stored in the sliders
                       →  get_positions() recomputes via compute_auto_positions() in Auto mode
```

But `compute_auto_positions` is **not** an exact inverse of `decompose_servo_positions` (its centre and extremes are empirical values). The CLI's `apply_pose()` sends the values directly.

Measured: **12 of 19 poses were distorted**, by up to 32°:

| Pose | Stored | GUI actually sent | Deviation |
|---|---|---|---|
| `ring_close` | Ring `(75, -35)` | Ring `(43, -5)` | **32° / 30°** |
| `middle_close` | Middle `(75, -35)` | Middle `(43, -5)` | **32° / 30°** |
| `pointer_close` | Pointer `(75, -35)` | Pointer `(43, -5)` | **32° / 30°** |
| `thumb_close` | Thumb `(75, -35)` | Thumb `(43, -5)` | **32° / 30°** |
| `wave1` | `(-75, -3)` | `(-75, 9)` | 12° |
| `hifive` | Thumb `(-75, -3)` | Thumb `(-75, 9)` | 12° |
| `greeting` | Ring `(-18, -57)` | Ring `(-10, -68)` | 8° / 11° |
| `victory` | Middle `(-68, -9)` | Middle `(-75, 1)` | 7° / 10° |
| `paper` | Pointer `(-52, -22)` | Pointer `(-59, -16)` | 7° / 6° |
| `ok` | Pointer `(36, 46)` | Pointer `(38, 43)` | 2° / 3° |

**The pattern:** symmetric poses where each finger has `pos1 == pos2` (`open` `close` `stone` `two` `scissors` `one` `three`) round-trip exactly. Every asymmetric pose involving lateral spread drifts.

### 4.3 Fix

Added `_send_exact_positions()`, which sends angles straight to the servos in `SERVO_PAIRS` order (equivalent to the CLI's `apply_pose`). Both pose entry points now use it:

- the `✓ Apply` button in Pose Management
- `_apply_pose_from_config()` — the sequence player and pose list

The sliders are still updated by `set_positions()` for display, but **no longer decide what gets sent**.

### 4.4 Result

After the fix, **all 19 poses satisfy `stored == GUI-sent == CLI-sent`**.

**Side effect:** the actual gestures in the GUI change, especially the asymmetric ones. That is the intended effect of the fix.

---

## 5. Pose data corrections

### 5.1 Four `*_close` poses were written wrong

```yaml
# Before — target finger (75, -35)
ring_close:    [75, -35, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, -35, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, -35, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, -35]
```

`(75, -35)` decomposes to `base = 20, side = -55` (out of range) — meaning *"only 27% curled, swung hard left"*, not "close this finger". Matching `close` and `one`, the correct form is `(75, 75)`:

```yaml
# After — target finger fully closed (75, 75), others stay open (-35, -35)
ring_close:    [75, 75, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, 75, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, 75, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, 75]
```

Verified by decomposition: target finger `base = 75` (fully closed), `side = 0` (not off to either side).

**Impact:** the `finger_roll` sequence, which uses these four, is only now a genuine "roll each finger in turn".

### 5.2 The thumb in `greeting` / `paper`

Both originally had the thumb at `(75, 75)` (fully closed). For `paper` (布, an open flat palm) a closed thumb is plainly wrong.

`greeting` was first changed to `(-75, -3)` (reusing `hifive`'s splayed thumb), but hardware testing showed that step needed the thumb to travel **150°**, which does not fit in 1.0 s (see 6.3). Final state:

```yaml
greeting: [-18, -57, -32, -32, -70, -7, -35, -35]   # thumb (-35, -35), same as open
paper:    [-19, -56, -34, -34, -52, -22, -75, -3]   # keeps the splayed thumb (flat palm)
```

That separates the two gestures: `greeting` is a wave, where the thumb just opens naturally; `paper` is a flat palm, where the thumb splays.

---

## 6. Sequence player: timing and diagnostics

### 6.1 Fixing false "did not reach target" warnings

Running `demo` on hardware produced three false alarms:

```
⚠ Pose #42 'greeting': Servos did not reach target! Max error: 52°
```

**Root cause:** `_log_pose_completion` subtracted two arrays that were in **different orders**.

- `monitor_servos()` writes its cache in **servo-ID order**: `latest_actual_positions[servo_id - 1] = ...` (index 0 = ID1 = Pointer)
- the `target_positions` passed in are a pose array, in **widget order** Ring / Middle / Pointer / Thumb (index 0 = Ring = ID5)

So it was subtracting Pointer's reading from Ring's target.

**Evidence** (recomputing from the measured log):

```
target (widget order)   : [-18, -57, -32, -32, -70, -7, -75, -3]
actual (servo-ID order) : [-68.85, -6.74, -33.69, -31.35, -18.46, -54.79, -74.12, -3.22]
compared as-is          -> max error 52°      <-- what the old code did
target reordered        : [-70, -7, -32, -32, -18, -57, -75, -3]
compared in servo order -> max error 2.21°    <-- actually spot on
```

**Fix:** added `pose_to_servo_order()` / `servo_to_pose_order()`, applied before comparing; the printed `current` is converted back so `target` and `current` line up column by column in the log.

### 6.2 Fixing when the reach check runs

The original checked a **fixed 2000 ms** after sending:

```python
self.root.after(2000, lambda ...: self._log_pose_completion(...))
```

But sequence steps only wait 1.0 s, so by the time the check ran the next step had already been sent — the reading necessarily belongs to the *next* motion:

```
25.388  Pose #40 'ok'      sent
26.782  Pose #41 'victory' sent        <- already moved on
27.742  Pose #40 'ok'      checked -> reading is mid-way to victory
```

**Fix:**

1. `_apply_pose_from_config` gained a `check_after` parameter. Clicking `✓ Apply` for a single pose is unchanged (2.0 s, then wait for motion to stop); sequence playback passes **the step's own delay**, so the check lands on the step boundary (delay − 100 ms) and no longer waits for motion.
2. Added a **supersession guard**: `_log_pose_start` records `current_pose_id`; if a newer command has since taken over, the reach check is skipped and the log shows `current=<superseded>`.

### 6.3 Sequence delay tuning

Back-computed **effective speed** from the hardware log (speed 3 is nominally 172°/s):

| Pose | Travel | Error at 0.9 s | Implied effective speed |
|---|---|---|---|
| `ok` | 110° | 0.5° | 121.7°/s (71% of nominal) |
| `victory` | 110° | 1.0° | 121.1°/s (70%) |
| `greeting` | 132° | 7.0° | 138.9°/s (81%) |

> Under load the real speed is only about **70%** of nominal. That is the number that matters when picking delays.

**`demo` changes:**

```yaml
  demo:
    steps:
    - open:3,3,3,3,3,3,3,3|2.0s
    - close:6,6,6,6,6,6,6,6|2.0s
    - ok:3,3,3,3,3,3,3,3|1.0s
    - victory:3,3,3,3,3,3,3,3|1.0s
    - greeting:3,3,3,3,3,3,3,3|1.5s      # was 1.0s
    - close:6,6,6,6,6,6,6,6|2.0s         # new: settle back into a fist
```

- `greeting` 1.0 s → **1.5 s**: that step travels 132° (Ring's second servo) and cannot finish in 1.0 s
- **new final `close`**: so `demo` ends with the hand closed, which also makes looping clean
- total runtime 7.0 s → **9.5 s**

### 6.4 `wave`: limiting the lateral swing to ±30°

The original `wave_r` / `wave_l` implied a `side` of **±36** (beyond the ±35 limit, so it was being clamped to 35).

Solving `side = base − pos1`, `base = (pos1 + pos2) / 2` gives `pos1 = base − side`, `pos2 = base + side`. Keeping `base = −39` and reducing `side` to ±30:

```yaml
wave_r: [-9, -69, -9, -69, -9, -69, -69, -9]     # was [-3, -75, -3, -75, -3, -75, -75, -3]
wave_l: [-69, -9, -69, -9, -69, -9, -9, -69]     # was [-75, -3, -75, -3, -75, -3, -3, -75]
```

Verified: `wave_r` has side `[-30, -30, -30, +30]`, and `wave_l` is its per-finger mirror.

**Side effect (expected):** each swing's travel also drops from 40°/72° to **34°/60°**. The wave is narrower overall, which only widens the timing margin.

---

## 7. New raw position row in Servo Feedback

A **`Current (0-1023)`** row sits directly below `Position (°)`, showing the live raw servo position.

```
1. Goal (°)
2. Position (°)
3. Current (0-1023)      <== new
4. Speed (°/s)
5. Torque (%)
6. Voltage (V)
7. Current (mA)
8. Temperature (°C)
9. Status
10. Moving
```

**Trade-off:** no extra serial reads. The raw value is derived from the position the monitor thread **already** read, so the polling loop does not double its serial traffic. Accuracy was verified exhaustively: **2048 combinations (raw 0–1023 × odd/even servo) round-trip with zero error**.

**Use:** compare directly against the vendor's calibration — `open` should read `260 / 760` alternating, `middle` should read `451 / 571`.

> The row name carries a range prefix to distinguish it from the existing `Current (mA)` (estimated current draw).

---

## 8. Left and right hand support

### 8.1 The vendor ships two firmwares

The vendor provides a separate Arduino demo per hand, with completely different parameters:

| | Right `Amazing_RHand_Demo` | Left `Amazing_LHand_Demo` |
|---|---|---|
| Servo IDs | **1–8** | **11–18** |
| Finger → ID | index `1,2` / middle `3,4` / ring `5,6` / thumb `7,8` | **ring `11,12` / middle `13,14` / index `15,16` / thumb `17,18`** |
| Middle `MiddlePos` | `[451, 571, 451, 571, …]` | `[571, 451, 571, 451, …]` |

The debug tutorial says plainly: *"a single hand uses 8 servos; the right hand's IDs must be set to 1-8, and the left hand's to 11-18."*

Note the left hand's numbering runs **in reverse** (ring first) — matching its mirrored mechanical layout.

### 8.2 Why changing IDs is not enough

IDs are only the first layer. Two physical differences remain between the hands, and missing either one distorts the gestures.

#### Difference 1: a 35.16° mounting offset

Both hands use **the same gesture value plus their own `MiddlePos`**:

```c
// Right
#define MiddlePos {451, 571, ...}
Move_Index(-35, 35)  →  ID1 = 451 + (-35)/0.293 = 331.5

// Left
#define MiddlePos {571, 451, ...}
Move_Index(-35, 35)  →  ID15 = 571 + (-35)/0.293 = 451.5
```

The same "open" gesture lands on different raw values on each hand. Converted into this program's angle space they differ by **120 raw = 35.16°**.

#### Difference 2: the two servos of a finger are swapped

```c
// Right Victory                      // Left Victory
Move_Index (-15, 65);                Move_Index (-65, 15);
Move_Middle(-65, 15);                Move_Middle(-15, 65);
```

Per finger, `(a, b) → (-b, -a)`; in pose values that means **swapping each finger's two numbers**.

Miss this and the **spread direction inverts** — the symptom is a V-sign collapsing its two fingers while the fingers that should be together splay apart.

> An easy misreading: in `Perfect` the index and middle values are **identical** on both hands (`(50,-50)`, `(0,0)`), and only the thumb differs. So the rule is not "swap index and middle" but a per-finger `(-b,-a)` — which is the identity for symmetric pairs.

### 8.3 Implementation

**Both hands share one `hand_config.yaml`.** Stored poses are always in **right-hand order**; the left hand converts on the way out and back, so there is no second pose library to maintain.

The conversion lives in `hand_logic.py`:

| Function | Purpose |
|---|---|
| `resolve_hand_config(app_config, hand)` | Overlays `hands.<name>` onto the top-level (right-hand) config |
| `servo_pairs()` / `servo_ids()` | That hand's `(servo1_id, servo2_id)` per finger / all servo IDs ascending |
| `hand_angle_offset()` / `hand_mirrors_pose()` | Read the hand's two difference parameters |
| `adapt_pose_for_hand(positions, mirror)` | Swaps each finger's `(pos1, pos2)`. **Swapping is its own inverse**, so the same function converts on apply and converts back on save |

**Wired into:**

- GUI: pose application (the `✓ Apply` button and sequence playback), and saving a pose
- CLI: `--pose` / `--sequence`

**The three global buttons' raw targets** are configured per hand and do not go through this conversion (`raw_positions` is written out under `hands.left`).

### 8.4 Usage

The GUI asks before opening:

```
  AmazingHand — which hand?
    1 = right hand  (servo IDs 1-8)
    2 = left hand   (servo IDs 11-18)
  Enter 1 or 2 [1]:
  LEFT hand — servo IDs 11-18
    Ring (11, 12)  Middle (13, 14)  Pointer (15, 16)  Thumb (17, 18)
    middle position raw: [571, 451, 571, 451, 571, 451, 571, 451]
```

Pressing Enter uses the `hand:` value from `config.yaml`. To skip the prompt:

```bash
python amazing_hand_gui.py --hand left
python amazing_hand_cmd.py --pose victory --hand left
```

### 8.5 First-time checklist for the left hand

In `hands.left.raw_positions`, only **middle** is the vendor default (`571, 451`); `open` and `close` were derived from the vendor's demo:

| Button | Left-hand raw | Source |
|---|---|---|
| Middle position | `571, 451, …` | Vendor default |
| Open All | `380, 642, …` | Derived: the same gesture as the right hand's Open All, applied to the left `MiddlePos` |
| Close All | `880, 142, …` | Same |

**Check them in this order the first time you connect the left hand:**

1. Press **Middle position** and confirm the `Current (0-1023)` row reads `571, 451, 571, 451, …`
2. Press **Open All** / **Close All** — travel should reach the stops without stalling
3. Try `victory` (index and middle open into a V), `greeting` (three fingers together), `ok` (thumb and index tips meeting)

If something is off:

| Symptom | Change |
|---|---|
| Middle position reads wrong | `hands.left.raw_positions.middle` |
| Spread direction inverted | set `hands.left.mirror_pose` to `false` |
| Travel too short or too far | `hands.left.raw_positions.open` / `close` |

### 8.6 If your left hand is numbered 1-8

Some people renumber the left hand's servos to 1–8. In that case only `hands.left.servos` needs changing:

```yaml
hands:
  left:
    servos:
      # Renumbered following the vendor's left-hand order: ring first
      ring:    [1, 2]
      middle:  [3, 4]
      pointer: [5, 6]
      thumb:   [7, 8]
      all_ids: [1, 2, 3, 4, 5, 6, 7, 8]
```

> `angle_offset` and `mirror_pose` **do not change** — they describe the mechanical build, not the ID numbering. The even-servo inversion still applies too, because each finger's pair keeps "odd ID first".

---

## 9. Serial port auto-detection

### 9.1 The problem

The original hard-coded the Windows port list to `COM1`–`COM20`:

```python
available_ports = [f'COM{i}' for i in range(1, 21)]
```

But an adapter can land on any port number (this machine measured `COM243`). The result: **your port is simply absent from the dropdown**, and auto-connect falls back to a configured default that does not exist, failing with "the system cannot find the file specified".

### 9.2 Fix

Added `available_serial_ports()`, falling back in stages:

1. pyserial's `list_ports.comports()` (used when installed — richest information)
2. Windows without pyserial: read the registry key `HARDWARE\DEVICEMAP\SERIALCOMM` (**standard library only**, no new dependency)
3. Linux/macOS: glob `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`, `/dev/cu.usb*`
4. Only if all of the above fail, fall back to the original candidate list

Ports are sorted **naturally**, so `COM2` comes before `COM10`.

### 9.3 Supporting changes

- The dropdown changed from `readonly` to **editable** — you can type a port when detection misses it
- If the configured default is not present, the GUI **starts on the first port that actually exists** instead of trying a default that isn't there
- **An explicit `--port` is never overridden** by that fallback (tracked via `port_was_explicit`)

---

## 10. Configuration reference

### `data/config.yaml`

The top-level `servos` / `auto_extremes` / `raw_positions` describe the **right hand** and serve as defaults; `hands.<name>` overlays them key by key.

```yaml
hand: right           # active hand: right | left (the GUI asks; --hand skips it)

limits:
  servo_min: -75      # absolute lower travel limit
  servo_max: 75       # absolute upper travel limit
  base_min: -75       # open/close slider range (-75 = fully open)
  base_max: 75        #                          ( 75 = fully closed)
  side_min: -35       # left/right slider range
  side_max: 35

auto_extremes:        # servo positions at the side slider's extremes — right hand
  left_open:  [32, -35]
  right_open: [-35, 32]
  left_closed:  [75, 75]
  right_closed: [75, 75]

raw_positions:        # global buttons' raw targets — right hand (index 0 → servo ID 1)
  open:   [260, 760, ...]
  close:  [760, 260, ...]
  middle: [451, 571, ...]

hands:
  left:               # overrides for the left hand; only list what differs
    servos:
      ring:    [11, 12]
      middle:  [13, 14]
      pointer: [15, 16]
      thumb:   [17, 18]
    raw_positions:    # index 0 → servo ID 11
      open:   [380, 642, ...]
      close:  [880, 142, ...]
      middle: [571, 451, ...]
    angle_offset: -35.16   # mounting offset (see 8.2)
    mirror_pose: true      # per-finger servo swap (see 8.2)
```

`auto_extremes` is **shared** by both hands — the side slider behaves the same in pose space; a mirrored hand simply splays the other way physically.

### `data/hand_config.yaml`

A pose's 8 values are ordered **Ring, Middle, Pointer, Thumb** (servo pairs `(5,6) (3,4) (1,2) (7,8)`), **not** by servo ID.

**This file is shared by both hands and always stored in right-hand order.** The left hand swaps each finger's pair when applying, and swaps back when saving.

> ⚠️ The docstring at the top of `amazing_hand_cmd.py` claims "index 0→servo1 … 7→servo8". That comment is **wrong**; the ordering above is what the code actually does.

---

## 11. Measured results

### Reach accuracy (after the fixes)

| Pose | Target | Actual | Max error |
|---|---|---|---|
| `open` | all −35 | −36.6 … −33.4 | ≤1.6° |
| `close` | all 75 | 74.7 … 75.3 | ≤0.3° |
| `ok` | — | — | 0.5° |
| `victory` | — | — | 1.0° |
| `greeting` | — | — | 2.2° |

### Conversion checks

```
raw -> degrees -> raw: 2048 combinations, zero error
open    raw [260, 760] -> back [260, 760]
middle  raw [451, 571] -> back [451, 571]
close   raw [760, 260] -> back [760, 260]
```

### Known remaining issues

- **`ok` and `victory` in `demo` have almost no timing margin** (+0.01 s by the measured speed). They currently pass only because the < 5° tolerance catches them. A drop in battery voltage, a temperature change, or a slightly stiffer hand could push them over. Raising both delays from 1.0 s to 1.2 s is the obvious next step.
- **`scissors` is byte-identical to `two`**, and **`stone` is byte-identical to `close`**. Semantically fine (scissors = two fingers, stone = fist) but literally duplicated, and not cleaned up.
- **The sliders still hold a ~0.3° representation error** against raw targets (see 2.4).
- **`config.yaml` and `hand_logic.py`'s `default_config` are out of sync.** The latter still carries the original scale (`servo_min: -40` etc.); it is only used when `config.yaml` is missing. The test `test_hand_logic.py::TestAngleLimits::test_defaults` asserts exactly those old defaults.

---

## 12. File-by-file summary

| File | Changes |
|---|---|
| `hand_logic.py` | New SCS0009 conversion constants; `raw_to_degrees` / `raw_to_radians` / `degrees_to_raw` / `pose_to_servo_order` / `servo_to_pose_order`; `raw_position` display format; `raw_positions` defaults; **hand support** (`HAND_NAMES` / `DEFAULT_HAND_SERVOS` / `resolve_hand_config` / `servo_pairs` / `servo_ids` / `hand_angle_offset` / `hand_mirrors_pose` / `adapt_pose_for_hand`); **`available_serial_ports()`**; config file I/O switched to **UTF-8** (it used the Windows GBK default and crashed on non-ASCII comments) |
| `amazing_hand_gui.py` | New `_apply_raw_hand_position` / `middle_all` / `_send_exact_positions`; rewrote `open_all` / `close_all` / `_apply_pose_from_config` / `_log_pose_completion`; new **Middle position** button; new raw-position row in Servo Feedback; `self.app_config` promoted to an instance attribute; removed the unused `latest_goal_positions` and unified `feedback_data['goal']` write order; **startup hand selection + `--hand`**; **8 hard-coded `range(1,9)` replaced with the hand's real IDs**; window title shows the active hand; angle offset and mirror conversion wired into every pose path; **port dropdown now lists detected ports and accepts typed input** |
| `amazing_hand_cmd.py` | New `--hand`; `connect` / `apply_pose` / `wait_for_motion` / torque-off-on-exit now use the hand's real IDs; pose and sequence paths apply the angle offset and mirror conversion; config read switched to UTF-8 |
| `data/config.yaml` | Re-calibrated `limits` / `auto_extremes`; added `raw_positions`; added `hand` and a `hands.left` override block |
| `data/hand_config.yaml` | All 19 poses re-scaled; the four `*_close` poses corrected; `greeting` / `paper` thumb corrected; `wave_r` / `wave_l` swing narrowed to ±30; `demo` got a longer `greeting` delay and a new closing step |
| `pyproject.toml` | Fixed `build-backend` (`setuptools.backends.legacy:build` → `setuptools.build_meta`) |

### Glossary

| Term | Meaning |
|---|---|
| **Auto mode** | Two sliders — "base" (open/close) and "side" (lateral) — indirectly drive one finger's two servos |
| **Raw mode** | Both of a finger's servo angles are controlled directly |
| **base** | Open/close amount, `(pos1 + pos2) / 2` |
| **side** | Lateral offset, `base − pos1` |
| **raw** | The servo's internal position unit: 0–1023 over 300°, centre 511 |
| **MiddlePos** | The vendor firmware's per-servo middle calibration; differs between hands (see 8.1) |
| **angle_offset** | The 35.16° mounting offset between hands (see 8.2) |
| **mirror_pose** | The left hand's per-finger servo-pair swap (see 8.2) |
