---
title: "Descripción general de los tutoriales de AmazingHand"
description: "Punto de entrada unificado a los tutoriales de AmazingHand: selección de producto, cableado de hardware, inicio rápido, control web, aplicación de escritorio, seguimiento de manos, depuración de servos y FAQ para las versiones con servos de bus serie SCS0009 y con servos PWM."
version: both
---

# Tutoriales de AmazingHand

AmazingHand es una mano diestra humanoide de código abierto e imprimible en 3D: 4 dedos, 8 grados de libertad y todos los accionamientos integrados en la mano, con un peso total de unos 400 g. Actualmente se ofrecen dos soluciones de hardware; la estructura mecánica de la mano es idéntica, pero cambian los servos, la placa controladora y el método de comunicación.

## Elige primero la versión

| Elemento de comparación | Versión con bus serie SCS0009 | Versión con servos PWM |
|--------|--------------------|------------|
| Escenario recomendado | Control preciso de ángulos, lectura de datos, integración con SO-ARM101 / LeRobot para adquisición y entrenamiento de datos | Demostraciones independientes, interacción por gestos, inicio rápido en web/escritorio |
| Servos | Servos de bus serie Feetech SCS0009 ×8 | Servos PWM **digitales** PTK 7452 MG-D ×8 |
| Parámetros del servo | 2,3 kg·cm a 6 V, 300° controlables, precisión de 0,293° | 4,5 kg·cm a 7,4 V (con alimentación de 5 V, unos 2,8–3 kg·cm), 180°±10°, 333 Hz |
| Realimentación de posición/temperatura/voltaje | ✅ Compatible | ❌ Sin lectura, no permite detectar bloqueos ni pérdida de pasos |
| Controlador principal | Sin placa integrada; el PC/Raspberry Pi se conecta directamente a través de la placa controladora de bus | Firmware integrado en ESP32-S3 |
| Alimentación | Entrada de 7–12 V (DC5521) a la placa controladora | 5 V / 3 A o más, masa común obligatoria |
| Comunicación | Protocolo de bus a 1.000.000 baudios | Puerto serie PC↔ESP32 a **115200** (los servos no tienen velocidad en baudios) |
| ID de servo | Debe configurarse: mano derecha 1–8, mano izquierda 11–18 | No se configura ID; canales fijos CH1–CH8: índice 1/2, medio 3/4, anular 5/6, pulgar 7/8 |
| Firmware | No requiere flasheo | Requiere compilar con ESP-IDF o flashear directamente el bin precompilado |

> Si necesitas **lectura de posición, precisión o adquisición de datos de entrenamiento para LeRobot**, elige SCS0009; si solo necesitas **demostraciones independientes, interacción por gestos y un inicio rápido**, elige PWM.

Consulta la comparación completa y la guía de selección en [Comparación de versiones](00-product/version-comparison.md).

## Navegación por modo de uso

| Modo de uso | Versión con bus serie SCS0009 | Versión con servos PWM |
|----------|--------------------|------------|
| Inicio rápido | [Inicio rápido SCS0009](02-quick-start/scs0009.md) | [Inicio rápido PWM](02-quick-start/pwm.md) |
| Control web | [Control web SCS0009](03-web-control/scs0009.md) | [Control web PWM](03-web-control/pwm.md) |
| Aplicación de escritorio / CLI | [GUI y CLI SCS0009](04-desktop/scs0009.md) | [Aplicación de escritorio PWM](04-desktop/pwm.md) |
| Seguimiento de manos | [Demo oficial SCS0009](05-hand-tracking/scs0009.md) | [Seguimiento PWM GUI / dora](05-hand-tracking/pwm.md) |
| Depuración y calibración de servos | [Depuración y calibración SCS0009](06-servo-tuning/scs0009.md) | [Protocolo y calibración PWM](06-servo-tuning/pwm.md) |
| Arduino / desarrollo secundario | [Arduino Nano](07-arduino/arduino-nano.md) · [Código de ejemplo](07-arduino/examples.md) | Igual (estructura mecánica compartida) |

Consulta la descripción general del control web (cambio de controlador, barra de puerto serie, descripción de la interfaz) en [README de control web](03-web-control/README.md).

## Antes de empezar

- [Información del producto](00-product/product-info.md) — parámetros, posicionamiento, recursos
- [Comparación de versiones y selección](00-product/version-comparison.md) — diferencias completas entre las dos soluciones de hardware
- [Descripción general del hardware](01-hardware/overview.md) — estructura, CAD, montaje, impresión 3D
- [Cableado SCS0009](01-hardware/scs0009.md) / [Cableado PWM](01-hardware/pwm.md)
- [Instalación del kit de cámara](01-hardware/camera-kit.md)
- [Descargas y recursos](00-product/downloads.md)

## Avisos de seguridad

- La fuente de alimentación externa de los servos y el ESP32/placa controladora deben compartir **masa común**.
- Antes del primer encendido, coloca la mano en la posición central e instala las bocinas del servo en esa posición para evitar que lleguen al final del recorrido.
- Conecta **solo un conjunto** de hardware SCS0009 o PWM a la vez; no los mezcles.
- Los servos PWM no tienen realimentación de posición; la parada de emergencia solo puede abortar el gesto y no permite leer ni liberar el par como en los servos de bus.

## Languages

[简体中文](../zh-hans/README.md) | [English](../en/README.md) | [Deutsch](../de/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (BR)](../pt-br/README.md) | [Português (PT)](../pt-pt/README.md) | [繁體中文](../zh-hant/README.md)
