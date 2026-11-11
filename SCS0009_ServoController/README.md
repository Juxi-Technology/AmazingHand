# SCS0009_ServoController

PySide6 debug tool for **Feetech SCS0009** serial-bus servos: scan the bus, read/write all 44 registers, move servos, change baud rate, factory reset and back up/restore EEPROM parameters as `.xdat`.

## Install and run

```bash
pip install -r requirements.txt
python -m src.gui.factory_calibration_tool
```

Connect the USB serial adapter, select the port, scan servo IDs and use the register/position panels.

## Documentation

The complete user tutorial has moved to the central tutorial tree:

- [SCS0009 servo tuning and calibration](../tutorials/zh-hans/06-servo-tuning/scs0009.md)
- [SCS0009 wiring and IDs](../tutorials/zh-hans/01-hardware/scs0009.md)

Until the central tree is translated, the original English guides remain under [`docs/en/`](docs/en/) for reference; the zh-hans pages are redirect stubs to the central tutorial.

## License

MIT — see [LICENSE](LICENSE).
