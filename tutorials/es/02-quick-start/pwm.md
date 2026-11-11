---
title: "Inicio rápido con PWM"
description: "Ruta de inicio más corta para la versión con servos PWM de AmazingHand: cableado, flasheo del firmware, control por GUI de escritorio o web y primeros movimientos."
version: pwm
---

# Inicio rápido con PWM

Para la versión ESP32-S3 + 8 servos PWM. Consulta los enlaces de cada capítulo para la explicación completa.

## 1. Cableado

- Conecta los 8 servos PWM a los servos 1–8 de la placa adaptadora según su numeración.
- Conecta PWM1–8 de la placa adaptadora a los GPIO 4, 5, 6, 7, 15, 16, 17 y 18 del ESP32-S3.
- Conecta 5V/GND de la placa adaptadora a una fuente de 5 V/3 A y comparte masa común con el ESP32.
- Cableado detallado: [Cableado, GPIO y alimentación PWM](../01-hardware/pwm.md).

> Los servos deben ser **servos digitales PTK 7452 MG-D (333 Hz)** o equivalentes; los servos analógicos de 50 Hz como el SG90 no se pueden sustituir directamente.

## 2. Flashear el firmware

### Opción A: bin precompilado (recomendado)

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  AmazingHand-PWM/firmware/prebuilt/amazinghand_pwm.bin
```

### Opción B: compilar con ESP-IDF

```bash
cd AmazingHand-PWM/firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

Estructura del proyecto de firmware:

```text
firmware/AmazingHand_Serial/
├── main/main.c                  Tareas FreeRTOS, cola de comandos e inicialización
└── components/
    ├── hand_servo/              Controlador LEDC PWM y calibración de servos
    ├── hand_gestures/           Macros de parámetros de gestos y funciones de gestos
    └── hand_protocol/           Análisis de tramas serie y distribución de comandos
```

> ESP-IDF no admite rutas con caracteres chinos: tanto el directorio del proyecto como el del usuario deben usar solo inglés; se recomienda ESP-IDF v5.x / v6.x y elegir **ESP32-S3** como chip destino.

Al encender, el puerto serie debería imprimir:

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

## 3. Conectar la PC

| Método | Acceso |
|------|------|
| GUI de escritorio | [Aplicación de escritorio PWM](../04-desktop/pwm.md): `python AmazingHand-PWM/tools/hand_gui.py` |
| Control web | [Control web PWM](../03-web-control/pwm.md): elige el controlador **PWM (ESP32-S3)** y el puerto serie 115200 |
| Prueba por línea de comandos | `python AmazingHand-PWM/tools/serial_test.py COM3 nop` |

## 4. Primeros movimientos

1. Al conectar, el firmware vuelve primero a la posición central (90°); confirma que no hay ruidos extraños ni agarrotamiento.
2. Con el deslizador de un solo dedo, comprueba uno a uno la dirección y la posición central.
3. Prueba después poses de pequeño recorrido como «Abrir / Puño».
4. Si la dirección está invertida o el centro desviado, ajústalo según [Protocolo y calibración PWM](../06-servo-tuning/pwm.md).

## Siguientes pasos

- [Protocolo y calibración PWM](../06-servo-tuning/pwm.md)
- [Seguimiento de manos PWM](../05-hand-tracking/pwm.md)
- [Comparación de versiones y selección](../00-product/version-comparison.md)
