---
title: "Información del producto AmazingHand"
description: "Información del producto AmazingHand: estructura mecánica, dimensiones, carga, las dos soluciones de servos y recursos de código abierto."
version: both
---

# Información del producto AmazingHand

AmazingHand es una mano diestra humanoide de código abierto e imprimible en 3D, orientada a la investigación en inteligencia corpórea, la educación robótica y los prototipos de interacción humano-robot. El cuerpo de la mano es el mismo; actualmente se ofrecen dos soluciones de hardware: **servos de bus serie SCS0009** y **servos PWM (ESP32-S3)**.

## Estructura mecánica

- **4 dedos, 8 grados de libertad**: cada dedo tiene 2 grados de libertad (flexión + abducción) y está accionado por dos servos mediante un mecanismo paralelo de accionamiento diferencial.
- **Accionamientos integrados**: todos los servos van montados en la mano; no hace falta sacar cables hacia el antebrazo.
- **Impresión 3D**: la carcasa y los eslabones se pueden imprimir; la mano completa pesa unos 400 g.
- **Soporte para ambas manos**: se puede usar la mano izquierda o la derecha por separado, o ambas en un robot colaborativo.
- **Interfaz de muñeca**: el diseño original se adapta a la muñeca Orbita 3D de Reachy 2 y también puede adaptarse a otros brazos robóticos.

## Parámetros básicos

| Parámetro | Especificación |
|------|------|
| Peso | Aprox. 0,416 kg |
| Número de dedos | 4 |
| Grados de libertad por dedo | 2 DoF |
| Altura extendida (sin base) | 195 mm |
| Ancho de la palma | 105 mm |
| Grosor de la palma | Aprox. 90 mm |
| Distancia máxima entre índice y pulgar | 180 mm |
| Carga por dedo | Aprox. 0,2 kg |
| Carga máxima con los cuatro dedos cerrados | Aprox. 0,5 kg |

> La carga, el voltaje y los parámetros del servo varían según la versión de servo elegida; consulta la comparación completa en [Comparación de versiones y selección](version-comparison.md).

## Dos soluciones de hardware

| Elemento | Versión con bus serie SCS0009 | Versión con servos PWM |
|------|--------------------|------------|
| Servos | Feetech SCS0009 ×8 | Servos PWM digitales PTK 7452 MG-D ×8 |
| Control | PC/Raspberry Pi + placa controladora de bus | Firmware integrado en ESP32-S3 |
| Realimentación | Lectura de posición/velocidad/voltaje/temperatura | Sin lectura |
| Uso recomendado | Precisión, adquisición de datos, LeRobot / SO-ARM101 | Demostraciones independientes, interacción por gestos, inicio rápido |

## Ecosistema de software

- **Control web**: deslizadores en el navegador, 19 poses predefinidas, teleoperación por cámara con MediaPipe y cambio de controlador SCS0009 / PWM.
- **Aplicación de escritorio**: SCS0009 usa `AmazingHandControl` (GUI Tkinter + CLI); PWM usa `AmazingHand-PWM/tools/hand_gui.py`.
- **Seguimiento de manos**: SCS0009 ofrece el Demo oficial dora + MuJoCo IK; PWM ofrece seguimiento MediaPipe integrado en la GUI.
- **Recursos de código abierto**: CAD, documentación de montaje/impresión y ejemplos de Arduino/Python incluidos en el repositorio.

## Recursos de código abierto

- [PDF de la guía de montaje](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [PDF de recomendaciones de impresión 3D](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [PDF de descripción general de AmazingHand](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [CAD / STL / STEP](../../../AmazingHand-main/cad/)
- [Proyecto upstream oficial (Pollen Robotics)](https://github.com/pollen-robotics/AmazingHand)

## Siguientes pasos

- [Comparación de versiones y selección](version-comparison.md)
- [Descripción general del hardware](../01-hardware/overview.md)
- [Inicio rápido SCS0009](../02-quick-start/scs0009.md)
- [Inicio rápido PWM](../02-quick-start/pwm.md)
