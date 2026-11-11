---
title: "Descripción general del hardware: estructura, CAD y montaje"
description: "Estructura mecánica, CAD/STL/STEP, montaje e impresión 3D de AmazingHand."
version: both
---

# Descripción general del hardware

Las dos soluciones de servos comparten la misma estructura mecánica de la mano; las diferencias están en el modelo de servo, la placa controladora y el cableado. Antes de montar la mano, confirma la versión elegida.

## Estructura mecánica

- 4 dedos, 2 grados de libertad cada uno: flexión/extensión + abducción/aducción.
- Cada dedo está accionado por dos servos mediante un mecanismo paralelo de accionamiento diferencial; todos los servos van montados en la mano.
- Carcasa, eslabones y falanges blandas impresos en 3D; la mano completa pesa unos 400 g.
- La interfaz de muñeca original se adapta a la Orbita 3D de Reachy 2 y también se puede adaptar a otros brazos robóticos.

## CAD y modelos

- Archivos STL / STEP: [`AmazingHand-main/cad/`](../../../AmazingHand-main/cad/)
- Documentación en línea de Onshape y URDF: consulta el capítulo de CAD en [`AmazingHand-main/README_CN.md`](../../../AmazingHand-main/README_CN.md).

## Montaje e impresión 3D

- [PDF de la guía de montaje](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [PDF de recomendaciones de impresión 3D](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [PDF de descripción general de AmazingHand](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)

> Antes de montar, coloca la mano en la posición central e instala las bocinas del servo en esa posición; las bocinas/estriados y los recorridos de los dos tipos de servo son distintos y no se pueden mezclar.

## Cableado de las dos soluciones

| Versión | Guía de cableado y alimentación |
|------|----------------|
| Bus serie SCS0009 | [Cableado, ID y alimentación SCS0009](scs0009.md) |
| PWM (ESP32-S3) | [Cableado, GPIO y alimentación PWM](pwm.md) |
| Kit de cámara | [Instalación del kit de cámara](camera-kit.md) |

## Siguientes pasos

- [Comparación de versiones y selección](../00-product/version-comparison.md)
- [Inicio rápido: SCS0009](../02-quick-start/scs0009.md) · [Inicio rápido: PWM](../02-quick-start/pwm.md)
