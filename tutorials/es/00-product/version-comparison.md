---
title: "Comparación y selección entre las versiones SCS0009 y PWM"
description: "Comparación completa de las dos soluciones de hardware de AmazingHand: servos, realimentación, controlador principal, alimentación, comunicación, ID/canales, firmware y escenarios de uso."
version: both
---

# Comparación y selección entre las versiones SCS0009 y PWM

La estructura de la mano de AmazingHand es la misma, pero existen dos soluciones de servos. La elección depende principalmente de si necesitas **realimentación de posición, control preciso de ángulos y adquisición de datos**.

## Conclusión rápida

- **Elige SCS0009**: si necesitas lectura de posición/temperatura/voltaje, ángulos precisos e integración con el brazo SO-ARM101 para adquisición y entrenamiento de datos con LeRobot.
- **Elige PWM**: para demostraciones independientes, interacción por gestos e inicio rápido en web/escritorio, sin necesidad de realimentación.
- **No los mezcles**: conecta solo un conjunto de hardware a la vez; la alimentación, el protocolo y el firmware son distintos.

## Comparación completa

| Elemento de comparación | Versión con bus serie SCS0009 | Versión con servos PWM |
|--------|--------------------|------------|
| Motivo recomendado | Control preciso de ángulos + lectura de datos; se puede integrar con el brazo SO-ARM101 para entrenamiento con LeRobot | Demostraciones independientes, interacción por gestos, inicio rápido |
| Modelo de servo | Servos de bus serie Feetech SCS0009 ×8 | Servos PWM **digitales** PTK 7452 MG-D ×8 |
| Parámetros del servo | 2,3 kg·cm a 6 V, 300° controlables, precisión de 0,293° | 4,5 kg·cm a 7,4 V (con alimentación de 5 V en esta solución, unos 2,8–3 kg·cm), 180°±10°, refresco de 333 Hz |
| Realimentación de posición/temperatura/voltaje/velocidad | ✅ Lectura compatible | ❌ Sin lectura, no permite detectar bloqueos ni pérdida de pasos |
| Controlador principal | Sin placa integrada; PC/Raspberry Pi conectado directamente a través de la placa controladora de bus | Firmware integrado en ESP32-S3 |
| Concentrador | Placa controladora de servos + concentrador de bus serie de 9 vías | Placa adaptadora PWM (8 zócalos de 3 pines 3P + 5V/GND) |
| Alimentación | Entrada de 7–12 V (DC5521) a la placa controladora; servos nominales de 6 V | 5 V / 3 A o más; la placa adaptadora y el ESP32 deben compartir masa común |
| Velocidad en baudios | **1.000.000** | Los servos no tienen velocidad en baudios; puerto serie PC↔ESP32 a **115200 8N1** |
| ID de servo | Debe configurarse: mano derecha 1–8, mano izquierda 11–18 | No se configura ID; canales fijos CH1–CH8 (índice 1/2, medio 3/4, anular 5/6, pulgar 7/8), cableado idéntico en ambas manos |
| Enlace de comunicación | PC → placa controladora → bus → 8 servos | PC → puerto serie USB 115200 → ESP32 → 8 canales PWM |
| Formato de comandos | Protocolo de bus Feetech, envío directo de ángulos | Tramas binarias: gestos `0x01–0x0A / 0x0C`, control directo `0xF0`, mano izquierda/derecha `0xF1`, NOP `0x00`, repetir `0xFE`, detener `0xFF` |
| Firmware | Ninguno (no requiere flasheo) | Requiere compilar con ESP-IDF o flashear directamente el `amazinghand_pwm.bin` precompilado |
| Mano izquierda/derecha | IDs de servo distintos (derecha 1–8, izquierda 11–18) | Mismo grupo de canales, mapeo por código + selección de lado con `0xF1` |
| Liberación de par | Admite activar/liberar el par | No admitido; la parada de emergencia solo aborta el gesto y los servos siguen alimentados manteniendo la posición |
| Control de velocidad | Admite parámetro de velocidad | Las tramas de control directo no tienen parámetro de velocidad |

## Puntos clave de la versión SCS0009

- Cada servo tiene un ID único; mano derecha 1–8, mano izquierda 11–18. Tras cambiar el cableado o un servo, hay que volver a configurar el ID.
- Usa un bus serie y admite lectura de posición, velocidad, voltaje y temperatura; adecuado para control en bucle cerrado y adquisición de datos.
- El PC/Raspberry Pi controla directamente a través de la placa controladora de bus USB, sin firmware MCU adicional.
- Entrada de 7–12 V a la placa controladora de bus (servos de nivel 6 V); asegúrate de compartir masa común con la placa controladora.
- Adecuado para flujos de entrenamiento que necesitan realimentación articular, como SO-ARM101 y LeRobot.

## Puntos clave de la versión PWM

- Usa **servos digitales PTK 7452 MG-D** (333 Hz, 500–2500 µs); no se pueden sustituir directamente por servos analógicos de 50 Hz como el SG90.
- El servo es nominalmente de 4,5 kg·cm a 7,4 V; en esta solución, con alimentación de 5 V/3 A, el par real es de unos 2,8–3 kg·cm.
- El ESP32-S3 genera 8 canales PWM y la PC solo necesita enviar comandos por el puerto serie USB a 115200.
- No hay realimentación de posición; no se pueden leer ángulos, temperatura ni voltaje, ni detectar bloqueos/pérdida de pasos.
- Ambas manos comparten el mismo grupo de canales; en cada par de dedos, el servo derecho es el canal impar y el izquierdo el par, y el índice siempre es CH1/2.
- Requiere flashear el firmware; el repositorio ofrece un bin precompilado y también se puede compilar con ESP-IDF.
- Adecuado para demostraciones independientes, interacción por gestos e inicio rápido en web/escritorio; no es adecuado para entrenamientos LeRobot que dependan de realimentación.

## Siguientes pasos

- [Inicio rápido SCS0009](../02-quick-start/scs0009.md)
- [Inicio rápido PWM](../02-quick-start/pwm.md)
- [Descripción general del hardware](../01-hardware/overview.md)
- [Descargas y recursos](downloads.md)
