English | [简体中文](README_CN.md)

<div align="center">

# SCS0009 Servo Debug Tool

**An FTServo debug tool built for Feetech SCS0009 servos (potentiometer feedback)**

> ⚠️ **Compatibility:** this tool currently supports Feetech SCS0009 servos only (SCS series, potentiometer position feedback, 10-bit resolution 0–1023). The register table, the `.xdat` parameter format and the baud rate table are all specific to the SCS0009.

> 📜 **Copyright:** this tool is developed and maintained by JUXI_Technology and released under the MIT license (see [LICENSE](LICENSE)). The FT debugger, xdat parameter backup/restore and cross-platform support are original implementations.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Ubuntu%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![GUI](https://img.shields.io/badge/GUI-PySide6-orange)

[Features](#-features) · [Interface](#-interface-overview) · [Quick start](#-quick-start) · [Usage](#-usage-steps) · [Notes](#-notes) · [Troubleshooting](#-troubleshooting)

</div>

---

## ✨ Features

| Feature | Description |
| ---- | ---- |
| Automatic port detection | Detects USB serial ports and filters out virtual devices |
| Cross-platform | Windows / Ubuntu / macOS |
| Language toggle | Switch between Chinese and English in the UI; the choice is remembered |
| Serial connection | Manual or automatic port selection, 8 baud rates (38400–1M) |
| Servo scan | Scans IDs 1–254 and lists the servos that are online |
| Register read | Reads all 44 registers (EEPROM + SRAM) |
| Register table | 5 columns (address / register / value / area / read-write); clicking a row selects it |
| Position control | Target position and speed; prompts you to disable torque when the move finishes |
| Baud rate | Changes the servo baud rate, rolling back automatically on failure |
| Factory reset | Restores factory defaults in one click |
| xdat parameters | Save the current EEPROM parameters, or open a backup and restore |

---

## 📚 Detailed guides

### Chinese

| OS | Guide |
|----|-------|
| Windows | [Windows 使用教程](docs/zh-hans/Windows.md) |
| Linux | [Linux 使用教程](docs/zh-hans/Linux.md) |
| macOS | [macOS 使用教程](docs/zh-hans/macOS.md) |

### English

| OS | Guide |
|----|-------|
| Windows | [Windows Guide](docs/en/Windows.md) |
| Linux | [Linux Guide](docs/en/Linux.md) |
| macOS | [macOS Guide](docs/en/macOS.md) |

---

## 🖥️ Interface overview

The main window is a single panel (the FT debugger):

```
┌─────────────────────────────────────────────────────────────┐
│  SCS0009 Servo Debug Tool              [中文 / Chinese]      │  ← top bar
├─────────────────────────────────────────────────────────────┤
│  🔌 Serial     [Port▾][🔄][Baud▾][Connect] [🔴 Disconnected] │
│  🎯 Servo      [🔍Scan][Servo▾][Read params][Read status]    │
│                ┌ Scanned servo list ┐                        │
│  📋 Registers  Address|Register|Value|Area|R/W  (44 regs)    │
│  🎯 Position   Target|Speed|Move|Torque ON|OFF | Status      │
│  🔧 Baud/Reset New baud|Set baud|Factory reset               │
│  📁 xdat (EEPROM only)  Save current|Open xdat|Restore       │
│  📜 Log                                                      │
└─────────────────────────────────────────────────────────────┘
```

- **Top bar**: application title and language toggle.
- **🔌 Serial**: pick a port and baud rate, connect or disconnect.
- **🎯 Servo**: scan, select a servo, read parameters or status.
- **📋 Registers**: all 44 registers in 5 columns; clicking a row fills in the write address automatically.
- **🎯 Position**: target position and speed; the status bar prompts you to disable torque when the move completes.
- **🔧 Baud rate / Factory reset**: change the baud rate (rolls back on failure) or restore factory defaults.
- **📁 xdat parameters (EEPROM only)**: save the current servo parameters, open a backup, restore.

---

## 🚀 Quick start

> Full per-OS guides are in [📚 Detailed guides](#-detailed-guides). The essentials are below.

### Windows

1. Install [Python 3.10+](https://www.python.org/downloads/) (tick **Add to PATH**)
2. Create a virtual environment and install the dependencies:

```bash
cd SCS0009_ServoController
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> ⚠️ **Create the virtual environment only once.** Re-running `python -m venv .venv` resets/overwrites the existing environment and wipes the installed dependencies. After that, you only need to `activate` it.

3. Check the environment and launch:

```bash
python setup.py
python -m src.gui.factory_calibration_tool
```

4. Confirm the port number in Device Manager (e.g. `COM3`) and select it in the top bar. To specify the port manually:

```bash
python -m src.gui.factory_calibration_tool --port COM3
```

### Linux (Ubuntu / Debian)

1. Install CJK fonts and dependencies:

```bash
sudo apt install python3-venv fonts-noto-cjk fonts-noto-color-emoji
```

2. **⚠️ Grant serial port access (dialout group)** — required:

```bash
sudo usermod -a -G dialout $USER
# log out and back in for this to take effect
```

3. Create the virtual environment, install dependencies, launch:

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup.py
python -m src.gui.factory_calibration_tool
```

> ⚠️ Create the virtual environment only once. Re-running `python3 -m venv .venv` overwrites the existing environment and wipes installed dependencies. After that, only `source .venv/bin/activate` is needed.

4. The serial device is `/dev/ttyUSB0` or `/dev/ttyACM0`. To specify it manually:

```bash
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

### macOS

1. Install Python with Homebrew:

```bash
brew install python
```

2. Create the virtual environment, install dependencies, launch:

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup.py
python -m src.gui.factory_calibration_tool
```

> ⚠️ Create the virtual environment only once. Re-running `python3 -m venv .venv` overwrites the existing environment. After that, only `source .venv/bin/activate` is needed.

3. **⚠️ Port naming**: on macOS use `/dev/cu.usbserial-*` (**recommended, non-blocking**) rather than `/dev/tty.*`. To list them:

```bash
ls /dev/cu.*
```

To specify manually:

```bash
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

### Command line

```bash
# List available serial ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch on a specific port
python -m src.gui.factory_calibration_tool --port <port>
```

---

## 📖 Usage steps

### 1. Connect and detect servos

1. Connect the arm's control board through a USB-to-serial adapter and power the servos.
2. Open the GUI, choose the port in the "🔌 Serial" area (or click `🔄` to refresh) and set the baud rate (1M by default).
3. Click **Connect**. The status shows `🟢 Connected`.

> If the port is reported as busy, make sure no other program (a serial monitor, a previous instance of this tool) is holding it.

### 2. Scan for servos

1. Click **🔍 Scan** to detect servos with IDs 1–254.
2. Results appear live in the servo list, with model names.
3. Click a row in the list to fill the "Servo" dropdown.

### 3. Read parameters

1. With a servo selected, click **📖 Read parameters** to read all 44 registers one by one.
2. The table shows 5 columns (address / register / value / area / read-write), colour-coded for EPROM / SRAM / DEFAULT.
3. The log area shows the result for each register, including the reason for any failure.

### 4. Modify / write parameters

1. Click the register row you want to change — the write address, length and value fields fill in automatically.
2. Edit the value and click **✏️ Write**.
3. The tool unlocks the EEPROM, writes, then re-locks it.
4. A dialog reports the result: "✅ Written successfully" or "❌ Write failed", with the reason.

### 5. Change the servo ID

1. Find the "Servo ID" row (address 0x05) in the register table and click it.
2. Change the value to the new ID and click **✏️ Write**.
3. The tool unlocks, writes address 5, then re-locks.

> ⚠️ Before changing an ID, make sure this is the only servo on the bus, to avoid an ID conflict.

### 6. Position control

1. In the "🎯 Position" area, **drag the slider** to set the target position (0–1023, the 10-bit resolution of the potentiometer); the numeric box follows. You can also type a value directly.
2. Click **▶ Move**. The servo starts moving and the status bar shows "Moving...".
3. When the move completes it shows "✅ Move complete — please disable torque". Click **⏹ Torque OFF**.

### 7. Baud rate / factory reset

- **Change baud rate**: pick a new rate (38400 – 1000000 bps) in the "🔧 Baud rate / Factory reset" area and click **🔧 Set baud rate**. The tool switches its own serial baud rate and verifies with a ping, rolling back automatically on failure.
- **Factory reset**: click **🔄 Factory reset**. The servo returns to its defaults (ID=1, baud rate=1000000) and must be scanned again.

### 8. Back up and restore xdat parameters

In the "📁 xdat parameters (EEPROM only)" area:

1. **💾 Save current servo**: writes the selected servo's EEPROM parameters to an xdat file, as a backup.
2. After changing parameters, if you want to revert:
3. **📂 Open xdat**: load the backup file.
4. **📤 Restore to servo**: write the backup back into the servo's EEPROM.

---

## ⚠️ Notes

1. **Safety first**: writing parameters persists them to EEPROM. Before writing, make sure the power supply is stable and the arm cannot hit a person or an object.
2. **Power**: the SoARM 101 standard version recommends DC 5V 5A; the Pro version recommends DC 12V 5A. Insufficient power causes missed steps or communication failures.
3. **Exclusive access**: on Windows a serial port is held exclusively — two programs cannot use the same port at once. Do not use this tool while another program (such as a serial monitor) has the port open.
4. **Linux permissions**: accessing `/dev/ttyUSB*` / `/dev/ttyACM*` requires your user to be in the `dialout` group — see the [Linux guide](docs/en/Linux.md).
5. **macOS port naming**: use `/dev/cu.*` (non-blocking) rather than `/dev/tty.*` (blocking, can hang) — see the [macOS guide](docs/en/macOS.md).
6. **Hot-plugging**: after unplugging the USB device the tool tries to reconnect; plug it back in and click `🔄` to refresh the port list.
7. **Over-temperature / over-voltage protection**: the tool monitors voltage and temperature and warns above 60 °C. If a servo runs hot repeatedly, stop and let it cool.
8. **Writes are irreversible**: writing to EEPROM overwrites the previous value with no undo. Back up first with "Save current servo".
9. **ID change risk**: the tool reports an error if a write or verification fails, but in rare cases a servo can become unreachable. If that happens, try "Factory reset", which sets the ID back to 1.
10. **Encoding**: if emoji appear garbled in a Windows console, set `PYTHONIOENCODING=utf-8` before running the command-line tool. Linux and macOS are natively UTF-8 and are usually unaffected.

---

## 🛠️ Troubleshooting

| Symptom | Likely cause | Fix |
| ---- | ---- | ---- |
| Cannot open the port / port busy | Another program is using it | Close the serial monitor or other program, or switch ports and restart the tool |
| No servos found | Insufficient power / wrong wiring / wrong baud rate | Check power and wiring; confirm the servos are at 1M baud |
| Reading parameters fails | Port busy / servo not responding | Close other programs; reconnect; check the address is correct |
| Temperature rises quickly | Excessive load or a stalled motor | Check for mechanical binding; lower the speed/acceleration |
| Servo missing after an ID change | ID conflict or a failed write | Factory reset, then scan again |

---

## 📁 Directory structure

```
SCS0009_ServoController/
├── docs/                    # Per-OS guides, one folder per language
│   └── <lang>/              # en, zh-hans, zh-hant, de, es, fr, it, ja, ko, pt-br, pt-pt
│       ├── Windows.md       # (same filenames in every language)
│       ├── Linux.md
│       └── macOS.md
├── src/
│   ├── gui/                  # PySide6 GUI
│   │   ├── factory_calibration_tool.py   # Main window (FT debugger + language toggle)
│   │   ├── ft_debugger.py                # FT debugger panel (register R/W, xdat backup)
│   │   ├── theme_utils.py                # Light theme
│   │   └── language_dialog.py            # Language selection dialog
│   ├── xdat_utils.py         # xdat parameter file I/O
│   ├── i18n*.py / i18n_translations/     # Chinese/English internationalization
│   └── port_utils.py         # Serial port detection
├── scservo_sdk/              # FTServo servo communication SDK
├── requirements.txt
└── setup.py                  # Environment check script
```
