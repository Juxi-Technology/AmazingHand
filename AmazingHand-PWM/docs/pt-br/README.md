# AmazingHand PWM Servo Edition — Início rápido

Controle o AmazingHand com um **ESP32-S3 e 8 servos PWM**. Os manuais completos estão nesta pasta `docs/`.

## Hardware

| Item | Modelo |
|------|-------|
| Controlador | Placa de desenvolvimento ESP32-S3 (YX-ESP32-S3 ou equivalente) |
| Servos | 8 servos PWM — firmware calibrado para **servos digitais PTK 7452 MG-D (333 Hz)** |
| Adaptador | Placa breakout para servos PWM |
| Alimentação | 5 V / 3 A, aterramento comum com o ESP32 |

> O SG90 e outros servos analógicos de 50 Hz **não** são substitutos diretos do firmware de 333 Hz.

| Canal | GPIO | Articulação | Canal | GPIO | Articulação |
|---------|------|-------|---------|------|-------|
| PWM1 | 4 | Indicador 1 | PWM5 | 15 | Anelar 1 |
| PWM2 | 5 | Indicador 2 | PWM6 | 16 | Anelar 2 |
| PWM3 | 6 | Médio 1 | PWM7 | 17 | Polegar 1 |
| PWM4 | 7 | Médio 2 | PWM8 | 18 | Polegar 2 |

## 1. Gravar o firmware

Com o ESP-IDF:

```bash
cd firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

Com a imagem pré-compilada e o `esptool`:

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  firmware/prebuilt/amazinghand_pwm.bin
```

A porta serial opera a **115200-8N1** e imprime um banner de inicialização.

## 2. Controlar a mão

GUI de desktop:

```bash
pip install -r tools/requirements.txt
python tools/hand_gui.py
```

O rastreamento por câmera precisa do ambiente extra criado por `tools/setup_tracking.bat`; em seguida:

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

Controle web: abra a página `Amazinghand-web-io/` do repositório (ou execute `Amazinghand-web/server.py --driver pwm`), selecione o driver **PWM (ESP32-S3)**, escolha a porta serial do ESP32 e conecte.

## 3. Documentação completa

| Documento | Conteúdo |
|----------|----------|
| [`../en/user_manual.md`](../en/user_manual.md) / [`../zh-hans/用户手册.md`](../zh-hans/用户手册.md) | Protocolo, referência de comandos, fiação, calibração, FAQ |
| [`../en/full_workflow.md`](../en/full_workflow.md) / [`../zh-hans/全流程使用教程.md`](../zh-hans/全流程使用教程.md) | Fluxo de trabalho completo |
| [`../en/gui_usage.md`](../en/gui_usage.md) / [`../zh-hans/使用教程.md`](../zh-hans/使用教程.md) | GUI e ferramenta de teste serial |
| [`../en/hand_tracking.md`](../en/hand_tracking.md) / [`../zh-hans/手势追踪教程.md`](../zh-hans/手势追踪教程.md) | Rastreamento de mãos com MediaPipe |

## 4. Problemas comuns

- **Sem resposta**: verifique os 115200 baud, a porta COM do ESP32, a alimentação de 5 V / 3 A e o aterramento comum. A página repete automaticamente o handshake NOP.
- **O servo não se move / treme**: verifique se o servo é um servo digital de 333 Hz e se a alimentação é adequada.
- **Direção invertida**: defina o `scale` do dedo correspondente como `-1` em `Amazinghand-web-io/config.json`, em `pwm.calibration`.
- **Posição central desalinhada**: ajuste o `offset_deg` desse canal.
- **Status ocupado**: o firmware está executando um gesto interno; aguarde ou envie stop (`0xFF`).
