# Visual Gesture Commands — Usage Tutorial

This module provides **host-side control tools**: after connecting to the ESP32, click buttons or run commands on your computer to make the dexterous hand perform gestures.

> Applies to: ESP32-S3 + 8-channel PWM servos (differential drive). See the [User manual](user_manual.md) for firmware flashing.

## 1. Running Options

| Method | Requirements | Best for |
|------|------|------|
| **Run from source** (recommended) | 64-bit Python 3.12 + pyserial | All features, including hand tracking |
| Package your own exe | PyInstaller | Distribution without installing Python (see Section 5) |

## 2. Running from Source

### Install dependencies

Run in the module root directory (`AmazingHand-PWM/`):

```bash
# Basic dependencies (pyserial)
pip install -r tools/requirements.txt

# Run this only if you need hand tracking (automatically creates tools/tracking_env and installs mediapipe)
tools/setup_tracking.bat
```

> mediapipe 0.10.14 only ships a 64-bit Windows wheel, so you must use **64-bit Python 3.12**.

### Launch the GUI

```bash
# Any Python with pyserial
python tools/hand_gui.py

# Or use the tracking environment (includes mediapipe)
tools/tracking_env/Scripts/python tools/hand_gui.py
```

### Using the GUI

1. **Select the serial port**: choose the ESP32's COM port from the drop-down at the top (check Device Manager).
2. **Click "Connect"**: the status light turns green, the log shows "connected", and a NOP link test is sent automatically.
3. **Gesture commands**: click "Rock / Scissors / Paper / Thumbs Up / OK / Pinch / Point / Open / Fist" and the dexterous hand performs the gesture.
4. **Left/right hand**: tick "Right hand" / "Left hand" to switch (the thumb's mirror direction differs).
5. **Direct servo control**: drag the 8 sliders to control each servo's angle in real time (0–180°).
6. **Finger differential control**: two sliders per finger—
   - **Bend ◀▶ Extend**: bend or extend the finger (range -70 to +70).
   - **Swing right ◀▶ Swing left**: swing the finger left/right (range 60 to 120, 90 = neutral).
7. **Repeat / Stop**: repeat the last gesture / abort immediately.
8. **Communication log**: shows sent and received frames and responses in real time at the bottom.

### Built-in hand tracking in the GUI

The GUI includes a hand-tracking panel (the camera follows your hand's motion):

1. After connecting the serial port, scroll to the "Hand Tracking (MediaPipe camera)" panel.
2. Select the camera index (default 0) and click **"Start Tracking"**.
3. Put your hand in the camera view; the dexterous hand follows the bend/extend motion.

> Tracking requires mediapipe to be installed by `tools/setup_tracking.bat`; only the GUI launched from source has the tracking feature.

## 3. Command-Line Testing (tools/serial_test.py)

Run in the module root directory:

```bash
# Link test (confirm the connection works first)
python tools/serial_test.py COM3 nop

# Gestures
python tools/serial_test.py COM3 rock         # Rock
python tools/serial_test.py COM3 thumbs_up    # Thumbs up
python tools/serial_test.py COM3 index        # Point
python tools/serial_test.py COM3 open         # Open
python tools/serial_test.py COM3 close        # Fist

# Single-servo direct drive
python tools/serial_test.py COM3 servo 1 90   # Servo 1 → 90°

# Center all
python tools/serial_test.py COM3 mid

# Set left/right hand
python tools/serial_test.py COM3 hand L
python tools/serial_test.py COM3 hand R

# Sweep / self-test
python tools/serial_test.py COM3 sweep 1      # Sweep servo 1
python tools/serial_test.py COM3 test         # Test every servo one by one
```

## 4. FAQ

| Symptom | Solution |
|------|------|
| Servos do not move | Check the power supply (dedicated 5V 3A), the COM port, and the wiring |
| No response / servos jerk after opening the serial port | Confirm the baud rate is 115200; the GUI sends a NOP handshake first when connecting |
| No camera image | Grant camera permission (Settings → Privacy → Camera) |
| Hand pose is mirrored | Tick the opposite left/right hand |
| Tracking does not respond | Make sure you launched with the Python from `tools\tracking_env` and that mediapipe installed successfully |

## 5. Packaging Your Own exe (Optional)

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole --name "AmazingHand控制台" tools/hand_gui.py
```

The packaged build does not include hand tracking (mediapipe resources are fairly large); use the source method if you need tracking.

> See the [User manual](user_manual.md) for the full protocol and command reference.
