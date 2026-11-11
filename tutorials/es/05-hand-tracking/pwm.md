---
title: "Seguimiento de manos PWM (MediaPipe integrado en la GUI)"
description: "Seguimiento de manos de la versión con servos PWM de AmazingHand: MediaPipe integrado en la GUI, instalación de dependencias, ejecución, principio y limitaciones, preguntas frecuentes."
version: pwm
---

# Seguimiento de manos PWM (MediaPipe integrado en la GUI)

> Los siguientes comandos se ejecutan en el directorio `AmazingHand-PWM/` del repositorio.

Esta página describe el seguimiento de manos de la **versión con servos PWM**: la GUI integra MediaPipe, la cámara reconoce los landmarks de la mano y los mapea en tiempo real a los 8 servos PWM. La cadena completa dora + MuJoCo IK pertenece al Demo oficial de SCS0009; consulta [Seguimiento de manos SCS0009](scs0009.md).

> Cadena: cámara → esqueleto de la mano de MediaPipe → ángulos de flexión/extensión de los cuatro dedos → ESP32 → servos PWM
>
> Aplicable a: ESP32-S3 + 8 servos PWM. Flasheo del firmware: [Inicio rápido PWM](../02-quick-start/pwm.md); protocolo: [Protocolo y calibración PWM](../06-servo-tuning/pwm.md).

> El Demo oficial que requiere IK completa (MuJoCo + dora + Rust) no se distribuye con este módulo; este tutorial solo describe el seguimiento integrado en la GUI que incluye el módulo.

## 1. Requisitos previos

1. **Hardware**: ESP32-S3 + 8 servos PWM alimentados, USB conectado y cámara disponible.
2. **Firmware**: ya flasheado (ver [Inicio rápido PWM](../02-quick-start/pwm.md)).
3. **Python**: Python 3.12 de 64 bits (mediapipe 0.10.14 solo ofrece wheel de 64 bits).

## 2. Instalar las dependencias de seguimiento

En la raíz del módulo (`AmazingHand-PWM/`) ejecuta:

```bash
tools/setup_tracking.bat
```

El script hará automáticamente: localizar Python de 64 bits → crear el entorno virtual `tools/tracking_env` → instalar `tools/requirements-tracking.txt` (mediapipe 0.10.14, numpy<2, scipy, opencv, Pillow, pyserial) → verificar mediapipe.

> También puedes instalarlo manualmente (con Python 3.12 de 64 bits):
> ```bash
> python -m pip install -r tools/requirements-tracking.txt
> ```

## 3. Ejecutar

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

1. Elige el puerto COM del ESP32 en la parte superior → pulsa «Conectar».
2. Desplázate hasta el panel «Seguimiento de manos (cámara MediaPipe)».
3. Elige el número de cámara (0 por defecto) → pulsa «Iniciar seguimiento».
4. Pon la mano en el campo de visión; la mano seguirá la flexión/extensión; pulsa «Detener seguimiento» para terminar.

![Panel de seguimiento de manos integrado en la GUI: selección de cámara, inicio del seguimiento e indicaciones de estado](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-tracking.png)

## 4. Principio y limitaciones

- MediaPipe 0.10.14 extrae los vectores 3D de las puntas de los 4 dedos (sistema de coordenadas de la mano).
- `tips_to_angles()` de `hand_tracking.py` mapea cada dedo a un ángulo diferencial:
  - flex (flexión/extensión): los tres dedos usan la componente z; el pulgar usa la componente y;
  - base (balanceo lateral): fijo en 90 (el balanceo lateral aún no está implementado).
- Estos son **ejes de control**; al enviarlos, el programa los combina en los ángulos de los dos servos de cada dedo (mismo sentido = splay, sentidos opuestos = flexión).
- La GUI integra suavizado EMA (alpha=0.4) + limitación a 60 ms para reducir el temblor.

Limitación: no hay IK, así que la precisión es inferior a la de la cadena completa MuJoCo + dora; adecuado para demostraciones e inicio rápido.

### Calibración de parámetros

- `FLEX_SCALE` / `THUMB_FLEX_GAIN` al final de `hand_tracking.py` controlan la amplitud y la dirección de la flexión (consulta el archivo para los valores actuales del código).
- El balanceo lateral aún no está implementado y `base` está fijo en 90; si necesitas balanceo lateral, usa el Demo oficial dora de SCS0009.
- Los cambios surten efecto al reiniciar la GUI.

## 5. Cambiar de mano izquierda/derecha

Marca «Derecha» / «Izquierda» en la parte superior de la GUI. Tras el cambio, la dirección del espejo del pulgar es distinta; si ves que está invertida, marca el otro lado y prueba.

## 6. Preguntas frecuentes

| Síntoma | Solución |
|------|------|
| Los servos no se mueven en absoluto | Comprueba la alimentación (5 V 3 A), el puerto COM y el cableado; confirma que el firmware esté flasheado |
| La cámara no muestra imagen | Concede permiso de cámara (Configuración → Privacidad → Cámara) |
| La mano no sigue / va lenta | Buena iluminación, mano completamente en el encuadre, movimientos más lentos y amplios |
| La forma de la mano sale invertida / el pulgar va al revés | Marca la mano izquierda/derecha contraria |
| Tras cambiar el puerto USB no se encuentra el puerto serie | Vuelve a seleccionar el puerto COM en la GUI |
| Al arrancar indica que falta mediapipe | Inicia con `tools\tracking_env\Scripts\python` o vuelve a ejecutar `tools/setup_tracking.bat` |

## 7. IK completa / servos de bus SCS0009

- La cadena IK completa (cámara → MediaPipe → MuJoCo + mink IK → AHControl → ESP32) procede de un proyecto dora Demo independiente y no está en este módulo; si la necesitas, usa el paquete de entrega original o el proyecto MediaPipe.
- Los servos de bus SCS0009 están soportados por `Amazinghand-web/` y `AmazingHandControl/` del repositorio.

## Descripción de directorios

| Ruta | Contenido |
|------|------|
| `tools/hand_gui.py` | Aplicación Tkinter (gestos, control directo, diferencial, seguimiento integrado) |
| `tools/hand_tracking.py` | Seguimiento de manos con MediaPipe y mapeo de ángulos |
| `tools/setup_tracking.bat` | Crea `tools/tracking_env` e instala las dependencias de seguimiento |
| `tools/requirements-tracking.txt` | Lista de dependencias de seguimiento |
| `tools/serial_test.py` | Prueba del puerto serie por línea de comandos |
