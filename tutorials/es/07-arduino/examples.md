---
title: "Ejemplos de Arduino y Python"
description: "Ejemplos oficiales de Arduino/Python de AmazingHand: biblioteca SCServo, herramienta de depuración Feetech, modos de cableado del TTL Linker, puerto serie de Arduino Uno/Mega y scripts básicos de Python."
version: scs0009
---

# Ejemplos de Arduino y Python

Esta página recopila los ejemplos oficiales y los puntos clave de cableado de `AmazingHand-main/ArduinoExample/` y `AmazingHand-main/PythonExample/`.

## Ejemplos de Arduino

### Preparación

- Instala la biblioteca **SCServo** en el Administrador de bibliotecas de Arduino IDE.
- Usa la herramienta de depuración Feetech FD para configurar el ID de servo (`feetech debug tool`).
- Entre Arduino y TTL Linker, **conecta RX/TX de forma cruzada**.

### Modo Link: modificar el ID de servo

1. Carga primero el ejemplo `Blink` en Arduino.
2. Cablea según el modo Link y abre el software Feetech para modificar el ID.

![Cableado del modo Link](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Link-mode.jpg)

![Instalación de la biblioteca SCServo](../../assets/robot-arms/amazing-hand/arduino-extension/SCServo.jpg)

### Modo Control: Arduino controla los servos

Tras cargar un programa propio, cablea según el modo Control:

![Cableado del modo Control](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Control-mode.jpg)

- **Arduino Uno** (solo tiene un puerto serie): usa un puerto serie por software/pines específicos según la figura.
- **Arduino Mega**: usa **RX1 / TX1 (19 / 18)**.

![Cableado del puerto serie de Uno](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Uno.jpg)

![Cableado del puerto serie de Mega](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Mega.jpg)

> El número de pines, la versión de la biblioteca y la dirección del TTL Linker dependen de la serigrafía real de la placa; antes de cambiar el ID, confirma la alimentación del bus y la masa común.

## Ejemplos de Python

`AmazingHand-main/PythonExample/` ofrece 4 scripts básicos:

| Script | Función |
|------|------|
| `AmazingHand_Demo.py` | Demostración básica de una mano: conectar al bus y ejecutar movimientos |
| `AmazingHand_Demo_Both.py` | Demostración con ambas manos |
| `AmazingHand_FingerTest.py` | Prueba de un solo dedo |
| `AmazingHand_Hand_FingerMiddlePos.py` | Calibración de la posición central del dedo |

Antes de usarlos:

1. Configura el ID de servo con el software Feetech (derecha 1–8, izquierda 11–18).
2. Instala `pyserial`, modifica el nombre del puerto serie/velocidad en baudios según el script y ejecútalo.
3. Confirma que la alimentación externa de los servos esté conectada y comparta masa común con la placa controladora de bus.

> Estos son los ejemplos básicos oficiales; para una GUI/CLI más completa, consulta [Aplicación de escritorio SCS0009](../04-desktop/scs0009.md); para el cableado TTL y la posición central, [Depuración y calibración de servos SCS0009](../06-servo-tuning/scs0009.md).

## Ubicación del código fuente

- [`AmazingHand-main/ArduinoExample/`](../../../AmazingHand-main/ArduinoExample/)
- [`AmazingHand-main/PythonExample/`](../../../AmazingHand-main/PythonExample/)
