English | [Deutsch](../de/Linux.md) | [Español](../es/Linux.md) | [Français](../fr/Linux.md) | [Italiano](../it/Linux.md) | [日本語](../ja/Linux.md) | [한국어](../ko/Linux.md) | [Português (BR)](../pt-br/Linux.md) | [Português (PT)](../pt-pt/Linux.md) | [简体中文](../zh-hans/Linux.md) | [繁體中文](../zh-hant/Linux.md)

# SCS0009 Servo Debug Tool — Linux Guide

For Ubuntu / Debian / other mainstream distros. Key points: serial permissions (dialout), USB-to-serial device detection.

> ⚠️ **Compatibility: This tool currently supports only Feetech SCS0009 servos (SCS series, potentiometer position feedback, 10-bit resolution 0-1023)**. Register table and xdat format are designed for Feetech SCS0009; other brands/models are not guaranteed.

---

## 1. Requirements

| Dependency | Version |
|-----------|---------|
| Python | >= 3.8 (3.10+ recommended) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| OS | Ubuntu 20.04+ / Debian 11+ |

Chinese fonts (required for the Chinese UI):

```bash
sudo apt install fonts-noto-cjk
```

Emoji icon fonts (for ✅⚠️ etc. in logs):

```bash
sudo apt install fonts-noto-color-emoji
```

## 2. Install Python Dependencies

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Create the virtual environment only ONCE**. Re-running it will reset/overwrite the environment (clearing installed deps). After that, just `source .venv/bin/activate`.

> If pip reports "externally-managed-environment", use a venv or `pip install --break-system-packages -r requirements.txt`.

## 3. ⚠️ Serial Permission (dialout) [Required]

By default, normal users **cannot access** `/dev/ttyUSB*` / `/dev/ttyACM*`. Add your user to the `dialout` group:

```bash
sudo usermod -a -G dialout $USER
```

**Log out and back in** (or reboot). Verify:

```bash
groups
# output should include dialout
```

> Some distros use `uucp` (Arch) or `tty`.

## 4. Identify USB Serial Device

After plugging in:

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Typical output:

```
/dev/ttyUSB0   # CH340 / CP2102 / PL2303
/dev/ttyACM0   # native USB serial (Arduino/ESP32 onboard)
```

## 5. Check Environment

```bash
python setup.py
```

## 6. Launch GUI

```bash
python -m src.gui.factory_calibration_tool
```

Specify port:

```bash
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

> If only one port exists, the tool uses it directly.

## 7. Interface Workflow

> Single-panel layout. A scroll bar appears automatically when the window is too short; it stretches to fit when maximized.

### 7.1 Serial Connection
Select port and baud rate (default 1M), click **Connect**.

### 7.2 Scan Servos
Click **Scan Servos** (ID 1-254); click a list row to auto-fill the dropdown.

### 7.3 Parameter Read/Write
- Read all 44 registers (EEPROM + SRAM), point-select linkage fills address/length/value
- Write with auto-unlock/write/lock; success/failure popup shown

### 7.4 Position Control
Drag slider (0-1023) or type value; move-complete prompt to turn off torque.

### 7.5 Baud Rate / Factory Reset
Change baud rate (auto-rollback on failure), factory reset.

### 7.6 xdat Params (EEPROM only)
Save current servo → open backup → restore to servo.

## 8. Troubleshooting

| Problem | Solution |
|---------|----------|
| **Permission denied: /dev/ttyUSB0** | Not in dialout group, see section 3; or `sudo chmod 666 /dev/ttyUSB0` (temporary) |
| No serial port | `ls /dev/ttyUSB* /dev/ttyACM*`; `lsusb` to confirm device |
| Device name changes | ttyUSB numbering depends on plug order; use a udev rule or select each launch |
| Chinese UI blank | Install `fonts-noto-cjk` |
| Emoji shows boxes | Install `fonts-noto-color-emoji` |
| pip install fails | Use venv; or `--break-system-packages` |
| App won't start | Check `python3 --version`; `pip list` for dependencies |

## 9. Command Line (Optional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

## 10. Advanced: udev Fixed Device Name (Optional)

Create `/etc/udev/rules.d/99-servo.rules` to fix the device name by USB ID:

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyServo"
```

Then `ls -l /dev/ttyServo`. Get vendor ID with `lsusb`.
