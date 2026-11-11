# Amazinghand-web

Browser control for the AmazingHand dexterous hand, supporting both hardware versions:

- **SCS0009 serial-bus servos** (1,000,000 baud)
- **PWM servos with ESP32-S3** (115,200 baud, 8 direct-drive channels)

The front-end lives in [`../Amazinghand-web-io/`](../Amazinghand-web-io/). `server.py` serves that folder over HTTP and switches the page to a WebSocket backend (`AH_BACKEND = "ws"`); it can also run the serial port server-side with either driver.

## Quick start

```bash
pip install -r requirements.txt

python server.py --no-connect              # start, pick the port in the page
python server.py --driver pwm              # PWM version
python server.py --port COM9 --hand right  # SCS0009, fixed port/hand
python server.py --dry-run                 # UI only, no serial
```

Open <http://localhost:8000>, choose the driver in the top bar, select the serial port and connect.

## Documentation

The complete user tutorials have moved to the central tutorial tree:

- [AmazingHand tutorials (Chinese)](../tutorials/zh-hans/README.md)
- [Web control overview](../tutorials/zh-hans/03-web-control/README.md)
- [SCS0009 web control](../tutorials/zh-hans/03-web-control/scs0009.md)
- [PWM web control](../tutorials/zh-hans/03-web-control/pwm.md)

Developer notes for the front-end (protocol, file map, limitations) are in [`../Amazinghand-web-io/README.md`](../Amazinghand-web-io/README.md).

## Legacy language tutorials

The original module-level translations still exist for reference:

[English](tutorials/en/README.md) · [Deutsch](tutorials/de/README.md) · [Español](tutorials/es/README.md) · [Français](tutorials/fr/README.md) · [Italiano](tutorials/it/README.md) · [日本語](tutorials/ja/README.md) · [한국어](tutorials/ko/README.md) · [Português (Brasil)](tutorials/pt-br/README.md) · [Português (Portugal)](tutorials/pt-pt/README.md) · [简体中文](tutorials/zh-hans/README.md) · [繁體中文](tutorials/zh-hant/README.md)

> The Simplified Chinese entry is a redirect page; use the central tutorial above for the latest content.
