# Hand Tracking — Usage Tutorial (PWM Servo Edition)

This module provides **lightweight hand tracking**: MediaPipe is built into the GUI; the camera detects hand landmarks and maps them to the 8 PWM servo channels in real time.

> Pipeline: camera → MediaPipe hand skeleton → four-finger bend/extend angles → ESP32 → PWM servos
>
> Applies to: ESP32-S3 + 8-channel PWM servos. See the [User manual](user_manual.md) for firmware flashing.

> The official demo that requires full IK (MuJoCo + dora + Rust) is not distributed with this module; this tutorial only covers the GUI's built-in tracking that ships with the module.

## 1. Prerequisites

1. **Hardware**: ESP32-S3 + 8 PWM servos powered up, USB connected, and a working camera.
2. **Firmware**: already flashed (see the [User manual](user_manual.md)).
3. **Python**: 64-bit Python 3.12 (mediapipe 0.10.14 only ships 64-bit wheels).

## 2. Installing Tracking Dependencies

Run in the module root directory (`AmazingHand-PWM/`):

```bash
tools/setup_tracking.bat
```

The script automatically: locates 64-bit Python → creates the `tools/tracking_env` virtual environment → installs `tools/requirements-tracking.txt` (mediapipe 0.10.14, numpy<2, scipy, opencv, Pillow, pyserial) → verifies mediapipe.

> You can also install manually:
> ```bash
> D:/Python312-64bit/python.exe -m pip install -r tools/requirements-tracking.txt
> ```

## 3. Running

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

1. Select the ESP32's COM port at the top → click "Connect".
2. Scroll to the "Hand Tracking (MediaPipe camera)" panel.
3. Select the camera index (default 0) → click "Start Tracking".
4. Put your hand in the frame; the dexterous hand follows the bend/extend motion; click "Stop Tracking" to finish.

## 4. How It Works and Its Limitations

- MediaPipe 0.10.14 extracts 3D vectors for the four fingertips (in hand coordinates).
- `tips_to_angles()` in `hand_tracking.py` maps each finger to a differential angle:
  - flex (bend/extend): uses the z component for the three fingers and the y component for the thumb;
  - base (left/right swing): fixed at 90 (left/right swing is not implemented yet).
- The GUI applies built-in EMA smoothing (alpha=0.4) + 60 ms throttling to reduce jitter.

Limitations: there is no IK, so precision is lower than the full MuJoCo + dora pipeline; it is intended for demos and quick start-up.

## 5. Switching Left/Right Hand

Tick "Right hand" / "Left hand" at the top of the GUI. The thumb's mirror direction differs between the two; if it looks reversed, tick the other side and test.

## 6. FAQ

| Symptom | Solution |
|------|------|
| Servos do not move at all | Check the power supply (5V 3A), the COM port, and the wiring; confirm the firmware is flashed |
| No camera image | Grant camera permission (Settings → Privacy → Camera) |
| Hand does not follow / lags | Ensure good lighting, keep the whole hand in frame, and move more slowly with larger motions |
| Hand pose mirrored / thumb direction reversed | Tick the opposite left/right hand |
| Cannot find the serial port after changing USB ports | Re-select the COM port in the GUI |
| mediapipe missing error on startup | Launch with `tools\tracking_env\Scripts\python`, or re-run `tools/setup_tracking.bat` |

## 7. Full IK / SCS0009 Bus Servos

- The full IK pipeline (camera → MediaPipe → MuJoCo + mink IK → AHControl → ESP32) comes from a separate dora demo project and is not part of this module; if you need it, use the original delivery package or the MediaPipe project.
- SCS0009 bus servos are supported by the repository's `Amazinghand-web/` and `AmazingHandControl/`.

## Directory Overview

| Path | Contents |
|------|------|
| `tools/hand_gui.py` | Tkinter host application (gestures, direct drive, differential control, built-in tracking) |
| `tools/hand_tracking.py` | MediaPipe hand tracking and angle mapping |
| `tools/setup_tracking.bat` | Creates `tools/tracking_env` and installs the tracking dependencies |
| `tools/requirements-tracking.txt` | Tracking dependency list |
| `tools/serial_test.py` | Command-line serial testing |
