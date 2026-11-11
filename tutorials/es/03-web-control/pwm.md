---
title: "Control web PWM"
description: "Control web de la versión con servos PWM de AmazingHand: conexión con ESP32-S3, cambio de controlador, diferencias con SCS0009, calibración de ángulos y preguntas frecuentes."
version: pwm
---

# Control web PWM

Esta página es la explicación específica del **control web para la versión PWM (ESP32-S3)**. Para la interfaz común, el modo de inicio, las poses predefinidas y la teleoperación por cámara, consulta [Descripción general del control web](README.md).

## Hardware y flasheo

- Cableado, GPIO, alimentación y modelo de servo: consulta [Cableado, GPIO y alimentación PWM](../01-hardware/pwm.md).
- Flasheo del firmware (ESP-IDF o bin precompilado): consulta [Inicio rápido PWM](../02-quick-start/pwm.md).
- PC↔ESP32 fijo a **115200 8N1**; los servos no tienen velocidad en baudios.

## Conexión web

1. En el desplegable «controlador» de la parte superior, elige **PWM (ESP32-S3)**
2. Pulsa **Añadir puerto…** y selecciona el puerto USB del ESP32-S3
3. Pulsa **Conectar**: la página hace el handshake automáticamente (NOP), envía la elección de mano izquierda/derecha y vuelve a la posición central
4. Después, controla con los deslizadores, las poses predefinidas y la teleoperación por cámara; los títulos de los dedos muestran **CH 1/2 …** (número de canal PWM)

![Modo PWM: selección de controlador en la parte superior y visualización de canales CH](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-port-bar.png)

![Panel de control manual en modo PWM: los títulos de los dedos muestran los canales CH y el botón de par está oculto](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-manual.png)

## Diferencias con la versión SCS0009

| Elemento | Versión de bus SCS0009 | Versión PWM |
|------|----------------|--------|
| Velocidad del puerto serie | 1.000.000 | **115.200** |
| Placa controladora | Placa controladora de bus USB | ESP32-S3 + placa adaptadora PWM |
| Par | Se puede activar/liberar | **No** (el firmware no tiene comando de par; el botón se oculta) |
| Parada de emergencia | Libera todo el par | Envía `0xFF` para abortar el gesto; los servos siguen alimentados y mantienen la posición |
| Velocidad | Admite parámetro de velocidad | Las tramas de control directo no llevan parámetro de velocidad |
| Realimentación | Lectura de posición/temperatura/voltaje/velocidad | **Sin lectura**, no se detectan bloqueos ni pérdida de pasos |
| Mano izquierda/derecha | ID de servo distintos | El mismo grupo de canales; se envía `0xF1` para cambiar (afecta sobre todo a los gestos del firmware; las poses de la página usan el mapeo de cada mano) |

## Calibración de ángulos

La página convierte los valores de pose en 8 ángulos de 0–180°, con esta fórmula por defecto:

```
angle = 90 + dir × scale × valor de pose + offset
```

- En cada dedo, el primer canal usa `dir = -1` y el segundo `dir = +1`
- Por defecto `scale = 1` y `offset = 0`, es decir, el ángulo del eje del servo se refleja directamente
- Cuando `mirror_pose` es verdadero, primero se intercambian los dos valores de pose de cada dedo (en este repositorio está activado en ambas manos)

Si en la máquina real la dirección sale invertida o el centro está desviado, edita `pwm.calibration` en [`config.json`](../../../Amazinghand-web-io/config.json):

```jsonc
"pwm": {
  "calibration": {
    "right": {
      "pointer": { "scale": 1.0, "offset_deg": [0, 0] }
    }
  }
}
```

- Dirección invertida: cambia el `scale` del dedo correspondiente a `-1`
- Centro desviado: ajusta `offset_deg` (uno por cada canal)
- Procedimiento dedo a dedo: vuelve al centro → mueve un solo dedo → observa la dirección/el centro → cambia `scale`/`offset_deg` → recarga la página y vuelve a probar

## Preguntas frecuentes

- **Falla la conexión / el ESP32 no responde**: comprueba que la velocidad en baudios sea 115200, que hayas seleccionado el puerto COM del ESP32, la alimentación de 5 V/3 A y la masa común; al abrir el puerto el ESP32 puede reiniciarse, y la página reintenta el NOP automáticamente
- **Los servos no se mueven o tiemblan**: confirma primero que los servos sean digitales de 333 Hz (PTK 7452 MG-D o similar) y que la alimentación sea suficiente; el SG90 requiere cambiar el firmware
- **La dirección está invertida**: cambia el `scale` del dedo correspondiente a `-1`
- **El centro no está bien**: ajusta el `offset_deg` del canal correspondiente
- **Sale «ocupado (gesto en curso)»**: el firmware está ejecutando un gesto interno; espera a que termine o pulsa la parada de emergencia (`0xFF`)
- **Escanear servos**: `tools/scan_servos.py` solo sirve para SCS0009; para PWM usa `AmazingHand-PWM/tools/serial_test.py` o la página web

---

## Páginas relacionadas

- [Protocolo y calibración PWM](../06-servo-tuning/pwm.md)
- [Aplicación de escritorio PWM](../04-desktop/pwm.md)
- [Inicio rápido PWM](../02-quick-start/pwm.md)
