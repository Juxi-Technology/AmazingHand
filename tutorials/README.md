# AmazingHand Tutorials

Central user documentation for the AmazingHand dexterous hand, covering both hardware versions:

- **SCS0009 serial-bus servo version**
- **PWM servo version (ESP32-S3 + 8 PWM channels)**

The tutorial is organized by **usage method** — hardware setup, quick start, web control, desktop tools, hand tracking, servo tuning, Arduino examples and FAQ — with a separate page for each servo version inside each chapter.

## Languages

| Language | Entry |
|----------|-------|
| 简体中文 (`zh-hans`) | [中文教程](./zh-hans/README.md) |
| English (`en`) | [English tutorials](./en/README.md) |
| Deutsch (`de`) | [Deutsche Anleitung](./de/README.md) |
| Español (`es`) | [Tutoriales en español](./es/README.md) |
| Français (`fr`) | [Tutoriels français](./fr/README.md) |
| Italiano (`it`) | [Tutorial in italiano](./it/README.md) |
| 日本語 (`ja`) | [日本語チュートリアル](./ja/README.md) |
| 한국어 (`ko`) | [한국어 튜토리얼](./ko/README.md) |
| Português (Brasil) (`pt-br`) | [Tutoriais em português (BR)](./pt-br/README.md) |
| Português (Portugal) (`pt-pt`) | [Tutoriais em português (PT)](./pt-pt/README.md) |
| 繁體中文 (`zh-hant`) | [繁體中文教學](./zh-hant/README.md) |

All language folders mirror the same directory and file structure, so a translated page keeps the same relative path under its language folder. Every language uses the **same image assets** in [`assets/`](./assets/); do not copy images into language folders.

## Structure

```
tutorials/
├── README.md                 # this language index
├── assets/                   # images shared by all languages
└── <lang>/                   # de, en, es, fr, it, ja, ko, pt-br, pt-pt, zh-hans, zh-hant
    ├── README.md             # overview and navigation
    ├── 00-product/           # product info, version comparison, downloads
    ├── 01-hardware/          # mechanical, wiring, camera kit
    ├── 02-quick-start/       # shortest path for each servo version
    ├── 03-web-control/       # browser control
    ├── 04-desktop/           # Python/Tkinter desktop tools
    ├── 05-hand-tracking/     # MediaPipe / dora tracking
    ├── 06-servo-tuning/      # protocol, calibration, debug tools
    ├── 07-arduino/           # Arduino Nano and examples
    └── 08-faq/               # consolidated FAQ
```

## Deploying to wiki-documents

`wiki-documents` expects tutorial pages under `docs/content/<lang>/tutorials/robot-arms/amazing-hand/` and shared images under `docs/public/images/tutorials/robot-arms/amazing-hand/`. English is the default locale, so its pages go to `docs/content/tutorials/robot-arms/amazing-hand/` (no `en/` segment).

Mapping from this repository:

- Copy `tutorials/<lang>/*` into the matching content directory; for English use `docs/content/tutorials/robot-arms/amazing-hand/` instead of `docs/content/en/...`.
- Copy `tutorials/assets/robot-arms/amazing-hand/` once into `docs/public/images/tutorials/robot-arms/amazing-hand/`. Do not duplicate images per language.
- In the copied Markdown, rewrite the relative image prefix to the wiki public path:

```bash
find docs/content/tutorials/robot-arms/amazing-hand \
     docs/content/*/tutorials/robot-arms/amazing-hand \
     -name '*.md' -exec sed -i \
     's#../../assets/robot-arms/amazing-hand/#/images/tutorials/robot-arms/amazing-hand/#g' {} +
```

The repository copies keep relative image paths so the tutorials also render directly on GitHub; the rewrite is only needed for the wiki deployment.

## Source modules

The tutorials are the user-facing documentation for:

- [`../AmazingHand-main/`](../AmazingHand-main/) — original design, CAD, firmware and demos
- [`../Amazinghand-web/`](../Amazinghand-web/) and [`../Amazinghand-web-io/`](../Amazinghand-web-io/) — web control
- [`../AmazingHandControl/`](../AmazingHandControl/) — SCS0009 Python GUI/CLI
- [`../SCS0009_ServoController/`](../SCS0009_ServoController/) — SCS0009 servo debug tool
- [`../AmazingHand-PWM/`](../AmazingHand-PWM/) — PWM firmware, desktop GUI and tools
