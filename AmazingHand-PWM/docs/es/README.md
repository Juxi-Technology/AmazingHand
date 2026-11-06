# AmazingHand — Edición de servos PWM — Inicio rápido

Controla el AmazingHand con un **ESP32-S3 y 8 servos PWM**. Los manuales completos están en esta carpeta `docs/`.

## Hardware

| Elemento | Modelo |
|------|-------|
| Controlador | placa de desarrollo ESP32-S3 (YX-ESP32-S3 o equivalente) |
| Servos | 8 servos PWM — firmware calibrado para **servos digitales PTK 7452 MG-D (333 Hz)** |
| Adaptador | placa de conexiones (breakout) para servos PWM |
| Alimentación | 5 V / 3 A, masa común con el ESP32 |

> Los servos SG90 y otros servos analógicos de 50 Hz **no** son sustitutos directos del firmware de 333 Hz.

| Canal | GPIO | Articulación | Canal | GPIO | Articulación |
|---------|------|-------|---------|------|-------|
| PWM1 | 4 | Índice 1 | PWM5 | 15 | Anular 1 |
| PWM2 | 5 | Índice 2 | PWM6 | 16 | Anular 2 |
| PWM3 | 6 | Medio 1 | PWM7 | 17 | Pulgar 1 |
| PWM4 | 7 | Medio 2 | PWM8 | 18 | Pulgar 2 |

## 1. Flashear el firmware

Con ESP-IDF:

```bash
cd firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

Con la imagen precompilada y `esptool`:

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  firmware/prebuilt/amazinghand_pwm.bin
```

El puerto serie funciona a **115200-8N1** e imprime un mensaje de inicio.

## 2. Controlar la mano

GUI de escritorio:

```bash
pip install -r tools/requirements.txt
python tools/hand_gui.py
```

El seguimiento por cámara necesita el entorno adicional creado por `tools/setup_tracking.bat`; después:

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

Control web: abre la página `Amazinghand-web-io/` del repositorio (o ejecuta `Amazinghand-web/server.py --driver pwm`), selecciona el controlador **PWM (ESP32-S3)**, elige el puerto serie del ESP32 y conéctate.

## 3. Documentación completa

| Documento | Contenido |
|----------|----------|
| [`../en/user_manual.md`](../en/user_manual.md) / [`../zh-hans/用户手册.md`](../zh-hans/用户手册.md) | Protocolo, referencia de comandos, cableado, calibración, FAQ |
| [`../en/full_workflow.md`](../en/full_workflow.md) / [`../zh-hans/全流程使用教程.md`](../zh-hans/全流程使用教程.md) | Flujo de trabajo completo |
| [`../en/gui_usage.md`](../en/gui_usage.md) / [`../zh-hans/使用教程.md`](../zh-hans/使用教程.md) | GUI y herramienta de prueba serie |
| [`../en/hand_tracking.md`](../en/hand_tracking.md) / [`../zh-hans/手势追踪教程.md`](../zh-hans/手势追踪教程.md) | Seguimiento de manos con MediaPipe |

## 4. Problemas frecuentes

- **Sin respuesta**: comprueba la velocidad de 115200 baudios, el puerto COM del ESP32, la alimentación de 5 V / 3 A y la masa común. La página reintenta automáticamente el handshake NOP.
- **El servo no se mueve / tiembla**: comprueba que el servo sea un servo digital de 333 Hz y que la alimentación sea suficiente.
- **Dirección invertida**: establece `scale` del dedo correspondiente en `-1` en `Amazinghand-web-io/config.json`, bajo `pwm.calibration`.
- **Posición central desviada**: ajusta `offset_deg` para ese canal.
- **Estado «ocupado»**: el firmware está ejecutando un gesto integrado; espera o envía la parada (`0xFF`).
