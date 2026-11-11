---
title: "Cableado, GPIO y alimentación PWM"
description: "AmazingHand versión con servos PWM: ESP32-S3, 8 canales PWM, mapeo de GPIO, alimentación y descripción del modelo de servo."
version: pwm
---

# Cableado, GPIO y alimentación PWM

En la versión PWM, el ESP32-S3 genera directamente las 8 señales PWM y el PC solo necesita enviar comandos por el puerto serie USB.

## Lista de hardware

| Elemento | Especificación |
|------|------|
| Controlador principal | Placa de desarrollo ESP32-S3 (Youxin YX-ESP32-S3 o similar) |
| Servos | Servos PWM **digitales** PTK 7452 MG-D ×8 (333 Hz) |
| Placa adaptadora | Placa adaptadora para servos PWM (8 zócalos de 3 pines 3P + 5V/GND) |
| Alimentación | 5 V / 3 A o más; la placa adaptadora y el ESP32 deben compartir masa común |

> El servo es nominalmente de 4,5 kg·cm a 7,4 V; con la alimentación de 5 V de esta solución, el par real es de unos 2,8–3 kg·cm.
>
> ⚠️ Los servos analógicos de 50 Hz como el SG90 no pueden sustituir directamente el firmware de 333 Hz; para cambiar de modelo hay que modificar a la vez `LEDC_FREQ` y la calibración de anchura de pulso.

## Canal → GPIO → dedo

| Canal | GPIO | Articulación | Canal | GPIO | Articulación |
|------|------|------|------|------|------|
| PWM1 / CH1 | 4 | Índice, articulación 1 | PWM5 / CH5 | 15 | Anular, articulación 1 |
| PWM2 / CH2 | 5 | Índice, articulación 2 | PWM6 / CH6 | 16 | Anular, articulación 2 |
| PWM3 / CH3 | 6 | Medio, articulación 1 | PWM7 / CH7 | 17 | Pulgar, articulación 1 |
| PWM4 / CH4 | 7 | Medio, articulación 2 | PWM8 / CH8 | 18 | Pulgar, articulación 2 |

- El cableado es idéntico en ambas manos; el índice siempre es CH1/2.
- En cada par de dedos, el servo derecho usa el canal impar y el izquierdo el par.
- El número de canal lo fija el firmware; no hace falta configurar ID de servo.

## Pasos de cableado

1. Conecta los conectores 3P de los 8 servos a las filas de pines de servo 1–8 de la placa adaptadora.
2. Conecta PWM1–PWM8 de la placa adaptadora a los GPIO 4, 5, 6, 7, 15, 16, 17 y 18 del ESP32-S3.
3. Conecta 5V/GND de la placa adaptadora a una fuente externa de 5 V/3 A.
4. Lleva otro par 5V/GND desde la placa adaptadora al ESP32-S3; **la masa debe ser común**.
5. Orden de cables del conector 3P del servo: marrón/negro GND, rojo V+, naranja/blanco/amarillo señal; conéctalos según la serigrafía de la placa adaptadora y no los inviertas.

## Alimentación y seguridad

- Con los 8 servos moviéndose a la vez la corriente es elevada; se recomienda 5 V/3 A o más y no depender solo de la alimentación USB.
- Antes del primer encendido, coloca la mano en la posición central e instala las bocinas del servo a 90°.
- Los canales no conectados pueden quedarse libres sin afectar a los demás; aísla los conectores vacíos.
- Abrir el puerto serie puede reiniciar el ESP32; el firmware vuelve automáticamente a la posición central.

## Siguientes pasos

- [Inicio rápido PWM](../02-quick-start/pwm.md) (flashear el firmware + GUI/web)
- [Protocolo y calibración PWM](../06-servo-tuning/pwm.md)
- [Control web](../03-web-control/pwm.md)
