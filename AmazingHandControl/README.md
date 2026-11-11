# AmazingHandControl

Python GUI and command-line tools for the **SCS0009 serial-bus servo** version of AmazingHand: calibration, pose presets, sequences, live control and telemetry.

## Install and run

```bash
pip install -r requirements.txt
python amazing_hand_gui.py        # GUI
python amazing_hand_cmd.py --help # CLI
```

The GUI exposes per-finger control, Open/Close/Center All, speed, pose management, sequences, telemetry charts and a servo feedback table. The CLI can list/apply poses and play sequences.

## Documentation

The complete user tutorial has moved to the central tutorial tree:

- [SCS0009 desktop GUI and CLI](../tutorials/zh-hans/04-desktop/scs0009.md)
- [SCS0009 hardware and wiring](../tutorials/zh-hans/01-hardware/scs0009.md)
- [SCS0009 tuning](../tutorials/zh-hans/06-servo-tuning/scs0009.md)

Until the central tree is translated, the original English user manual remains at [`docs/en/user_manual.md`](docs/en/user_manual.md).

Developer/reference documents remain in this module:

- [Configuration format](docs/zh-hans/CONFIG_FORMAT.md)
- [SCS0009 protocol memory table](docs/zh-hans/scs_servo_protocol.md)
- [Design changes and calibration notes](docs/zh-hans/CHANGES.md)
- [Requirements and acceptance tests](docs/zh-hans/REQUIREMENTS.md)

## Languages

Module reference docs are available in 11 languages under [`docs/`](docs/).
