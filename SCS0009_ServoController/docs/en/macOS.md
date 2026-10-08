# SCS0009 Servo Debug Tool — macOS Guide

For macOS 11 (Big Sur) and later. Key points: serial naming (`cu.*` vs `tty.*`), USB drivers.

> ⚠️ **Compatibility: This tool currently supports only Feetech SCS0009 servos (SCS series, potentiometer position feedback, 10-bit resolution 0-1023)**. Register table and xdat format are designed for Feetech SCS0009; other brands/models are not guaranteed.

---

## 1. Requirements

| Dependency | Version |
|-----------|---------|
| Python | >= 3.8 (3.10+ recommended, via Homebrew) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| OS | macOS 11+ (Apple Silicon / Intel) |

## 2. Install Python

Recommended via Homebrew:

```bash
# Install Homebrew if missing
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

Verify:

```bash
python3 --version
```

## 3. Install Dependencies

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Create the virtual environment only ONCE**. Re-running it will reset/overwrite the environment (clearing installed deps). After that, just `source .venv/bin/activate`.


## 4. ⚠️ macOS Serial Naming [Key]

macOS places USB serial devices under `/dev` with **two naming conventions**:

| Prefix | Meaning | Usable |
|--------|---------|--------|
| `/dev/tty.usbserial-*` | modem style (blocking) | can hang, not recommended |
| `/dev/cu.usbserial-*` | call/terminal style (**non-blocking**) | ✅ recommended |

**Find your port:**

```bash
ls /dev/cu.*
```

Typical output:

```
/dev/cu.usbserial-0001      # CP2102 / FTDI
/dev/cu.usbmodem141101      # onboard USB serial (Arduino/ESP32)
/dev/cu.wchusbserial1420    # CH340
```

> The tool auto-prefers `cu.*` devices. If specifying a port manually, use `cu.` not `tty.`.

## 5. USB Drivers

Most common chips (CH340, CP2102, FTDI) have built-in macOS drivers. If the device is not recognized:

```bash
system_profiler SPUSBDataType | grep -A5 -i "serial\|CH340\|CP210"
```

- **CH340**: older batches need the WCH official driver
- Generally, `ls /dev/cu.*` showing the device is enough

## 6. Check Environment

```bash
python setup.py
```

## 7. Launch GUI

```bash
python -m src.gui.factory_calibration_tool
```

Specify port:

```bash
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 8. Interface Workflow

> Single-panel layout. A scroll bar appears automatically when the window is too short; it stretches to fit when maximized.

### 8.1 Serial Connection
Select port and baud rate (default 1M), click **Connect**.

### 8.2 Scan Servos
Click **Scan Servos** (ID 1-254); click a list row to auto-fill the dropdown.

### 8.3 Parameter Read/Write
- Read all 44 registers, point-select linkage fills address/length/value
- Write with auto-unlock/write/lock; success/failure popup shown

### 8.4 Position Control
Drag slider (0-1023) or type value; move-complete prompt to turn off torque.

### 8.5 Baud Rate / Factory Reset
Change baud rate (auto-rollback on failure), factory reset.

### 8.6 xdat Params (EEPROM only)
Save current servo → open backup → restore to servo.

## 9. Troubleshooting

| Problem | Solution |
|---------|----------|
| Port with `tty.` hangs | Use the `cu.` prefix instead |
| Device not found | `ls /dev/cu.*`; replug; `system_profiler SPUSBDataType` |
| Chinese UI blank | System PingFang is usually fine; install Noto Sans CJK if broken |
| Permission issue | macOS generally needs no extra permission; allow terminal access if prompted |
| Venv activation fails | `source .venv/bin/activate` (not `.bat`) |
| Apple Silicon build error | Python 3.10+ is native; avoid Rosetta old Python |

## 10. Command Line (Optional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 11. Tips

- **Port name changes**: `cu.*` names may vary with different USB ports; select in the dropdown each launch
- **Sleep**: macOS may sleep and drop the serial; keep awake while operating
- **Privacy permission**: if asked to "access removable disks", allow it
