English | [Deutsch](../de/Windows.md) | [Español](../es/Windows.md) | [Français](../fr/Windows.md) | [Italiano](../it/Windows.md) | [日本語](../ja/Windows.md) | [한국어](../ko/Windows.md) | [Português (BR)](../pt-br/Windows.md) | [Português (PT)](../pt-pt/Windows.md) | [简体中文](../zh-hans/Windows.md) | [繁體中文](../zh-hant/Windows.md)

# SCS0009 Servo Debug Tool — Windows Guide

For Windows 10 / 11. Covers installation to full servo debugging.

> ⚠️ **Compatibility: This tool currently supports only Feetech SCS0009 servos (SCS series, potentiometer position feedback, 10-bit resolution 0-1023)**. Register table and xdat format are designed for Feetech SCS0009; other brands/models are not guaranteed.

---

## 1. Requirements

| Dependency | Version | Notes |
|-----------|---------|-------|
| Python | >= 3.8 | 3.10+ recommended, download from [python.org](https://www.python.org/downloads/) |
| PySide6 | >= 6.0 | GUI framework |
| pyserial | >= 3.5 | Serial communication |
| OS | Win10 / Win11 | Any edition |

## 2. Install Python

1. Visit <https://www.python.org/downloads/>
2. Download Python 3.10+ installer
3. **Check "Add Python to PATH"** during install (otherwise python won't be found in terminal)

Verify:

```bash
python --version
```

## 3. Install Dependencies

Install in a virtual environment to avoid polluting system Python:

```bash
cd SCS0009_ServoController
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> ⚠️ **Create the virtual environment only ONCE**. Re-running it will reset/overwrite the environment (clearing installed deps). After that, just `activate` it each time.

> The prompt will show `(.venv)` after activation.

## 4. Check Environment

```bash
python setup.py
```

`[OK] 环境检查通过，可以运行项目` means the environment is ready.

## 5. Connect Hardware

1. Plug in the USB-to-serial adapter (CH340 / CP2102)
2. Connect the servo controller (robot arm control board)
3. Power the servos (DC 5V 5A standard, DC 12V 5A Pro)

Check the COM port in Device Manager (`Win+X` → Device Manager):

```
Ports (COM & LPT)
  └─ USB-SERIAL CH340 (COM3)     ← your servo port
```

> **Note the COM number** to select it when starting.

## 6. Launch GUI

```bash
python -m src.gui.factory_calibration_tool
```

Or specify the port:

```bash
python -m src.gui.factory_calibration_tool --port COM3
```

List available ports:

```bash
python -m src.gui.factory_calibration_tool --list-ports
```

## 7. Interface Workflow

> Single-panel layout. A scroll bar appears automatically when the window is too short; it stretches to fit when maximized.

### 7.1 Serial Connection

- Select port and baud rate (default 1M), click **Connect**
- Status shows `🟢 Connected`

### 7.2 Scan Servos

- Click **Scan Servos** to detect online servos (ID 1-254)
- Results show in the servo list in real time (with model)
- Click a row in the list → auto-fills the servo dropdown

### 7.3 Parameter Read/Write

- **Read Params**: reads all 44 registers (EEPROM + SRAM), log shows results live
- **Parameter Table**: 5 columns (Address/Register/Value/Memory/Access), color-coded by EEPROM/SRAM/DEFAULT
- **Row Select Linkage**: click a row → auto-fills "Write Address", "Length", "Value"
- **Write**: modify value then click write; tool auto-unlocks/writes/locks EEPROM
- **Write Result Popup**: green "✅ Written successfully" on success, red "❌ Write failed" (with reason) on failure

### 7.4 Position Control

- **Slider**: drag to adjust target position (0-1023), value box updates live
- **Value box**: type target position directly, slider follows
- After movement, status shows "move complete, please turn off torque"

### 7.5 Baud Rate / Factory Reset

- **Change Baud Rate**: select 38400-1000000 bps, auto-rollback on failure
- **Factory Reset**: restore factory defaults (ID=1, baud=1M), rescan needed

### 7.6 xdat Params (EEPROM only)

1. `💾 Save Current Servo`: save current servo EEPROM params to xdat file (backup)
2. `📂 Open xdat`: load a backup file
3. `📤 Restore to Servo`: write the backup back to the servo

## 8. Troubleshooting

| Problem | Solution |
|---------|----------|
| No serial port | Check driver in Device Manager; try another USB port; install CH340 driver |
| Port in use | Close serial monitors; restart the tool |
| Chinese text blank | System has Microsoft YaHei; install CJK font if broken |
| Servo not found | Check power/wiring; confirm 1M baud |
| Write failed | Check servo power and connection; confirm register is writable |
| PermissionError opening port | Ensure no other process holds the COM port |

## 9. Command Line (Optional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port COM3
```
