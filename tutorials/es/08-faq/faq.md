---
title: "Preguntas frecuentes (FAQ)"
description: "Recopilación de preguntas frecuentes sobre AmazingHand general, SCS0009, PWM, control web, aplicación de escritorio y seguimiento de manos."
version: both
---

# Preguntas frecuentes (FAQ)

## Generales

**¿Debo elegir SCS0009 o PWM?**
Elige SCS0009 si necesitas realimentación de posición, precisión o adquisición de datos con LeRobot/SO-ARM101; elige PWM para demostraciones independientes, interacción por gestos e inicio rápido en web/escritorio. Ver [Comparación de versiones](../00-product/version-comparison.md).

**¿Se pueden conectar los dos tipos de servo a la vez?**
No. La alimentación, el protocolo y el firmware son distintos; conecta solo un conjunto a la vez.

**¿Se puede encender la mano directamente?**
Antes del primer encendido, coloca la mano en la posición central e instala las bocinas del servo en esa posición; la fuente externa y la placa controladora/ESP32 deben compartir masa común.

**¿Se puede cambiar el modelo de servo?**
La versión SCS0009 usa servos de bus; el firmware de la versión PWM está calibrado para el PTK 7452 MG-D (servo digital de 333 Hz). Los servos analógicos de 50 Hz como el SG90 no pueden sustituir directamente la versión PWM; hay que cambiar `LEDC_FREQ` y la calibración de anchura de pulso.

## Versión con bus serie SCS0009

**La dirección del movimiento está invertida** → comprueba si el cableado sigue «primero el ID impar»; en la mano izquierda confirma `angle_offset_deg = -35.16`.

**El puño de la mano izquierda no cierra lo suficiente / los servos zumban** → comprueba si el límite de `config.json` está en ±120° (el valor por defecto ±90 recorta el puño de la mano izquierda).

**Un dedo no se mueve / aparece «se esperaban N motores y se detectaron M»** → ejecuta `tools/scan_servos.py`; los ID de la mano izquierda son los más fáciles de cablear mal (11–18, no 9–16).

**La posición central está desviada** → el valor central `-17.578125` corresponde a los raw oficiales 451/571; para calibrar según el montaje mecánico, edita `middle.positions` de `config.json`.

**¿Cómo se configura el ID de servo?** → usa la [herramienta de depuración SCS0009](../06-servo-tuning/scs0009.md) para escanear y modificar el ID; mano derecha 1–8, mano izquierda 11–18.

**Linux no abre el puerto serie** → añade el usuario actual al grupo `dialout` y vuelve a iniciar sesión.

**¿Se pueden leer posición/temperatura/voltaje?** → Sí, el SCS0009 admite lectura de posición, velocidad, voltaje y temperatura; la tabla de memoria del protocolo está en [`scs_servo_protocol.md`](../../../AmazingHandControl/docs/zh-hans/scs_servo_protocol.md).

## Versión con servos PWM

**Falla la conexión / el ESP32 no responde** → comprueba la velocidad de 115200 baudios, el puerto COM del ESP32, la alimentación de 5 V/3 A y la masa común; al abrir el puerto el ESP32 puede reiniciarse y la página reintenta el NOP automáticamente.

**Los servos no se mueven o tiemblan** → confirma que sean servos digitales de 333 Hz (PTK 7452 MG-D o similar) y que la alimentación sea suficiente; el SG90 requiere cambiar el firmware.

**La dirección está invertida** → en `pwm.calibration` de `config.json` de la web, cambia el `scale` del dedo correspondiente a `-1`.

**El centro no está bien** → ajusta el `offset_deg` del canal correspondiente; ver [Protocolo, comandos y calibración PWM](../06-servo-tuning/pwm.md).

**Sale «ocupado (gesto en curso)»** → el firmware está ejecutando un gesto interno; espera a que termine o envía la parada (`0xFF`).

**¿La versión PWM tiene realimentación?** → No tiene lectura de posición/temperatura/voltaje y no puede detectar bloqueos ni pérdida de pasos.

**¿Los servos PWM tienen velocidad en baudios?** → Los servos en sí no; el puerto serie PC↔ESP32 está fijo a 115200 8N1.

**¿Se puede probar conectando solo algunos servos?** → Sí. Los canales no conectados pueden quedarse libres sin afectar a los demás; aísla los conectores vacíos.

**La cámara muestra imagen pero la mano no sigue / reacciona con lentitud** → luz uniforme, palma a unos 40–80 cm de la cámara y de frente; cierra otros programas que usen la cámara; confirma que el puerto serie esté conectado. Para los parámetros de seguimiento de la GUI, consulta [Seguimiento de manos PWM](../05-hand-tracking/pwm.md).

**El cambio de mano izquierda/derecha no surte efecto** → el firmware usa `0xF1` para cambiar de mano (la página lo envía automáticamente al conectar); este ajuste afecta principalmente a la dirección del pulgar de los gestos integrados del firmware; las poses de la página usan el mapeo de cada mano según el objeto de control actual.

**La imagen de seguimiento se congela / el registro se detiene** → detén el seguimiento y vuelve a iniciarlo; si sigue sin responder, cierra y vuelve a abrir la GUI y confirma que la cámara no esté ocupada por otro programa.

**Tras cambiar el puerto USB no se encuentra el puerto serie** → consulta el nuevo número COM en el Administrador de dispositivos, pulsa «Actualizar» en la GUI o en la página y vuelve a seleccionarlo.

## Control web

**Falla el modelo / falla la carga del seguimiento por cámara** → confirma que la página se sirve desde un servicio local (no abrir directamente con `file://`) y que la ruta de los recursos de MediaPipe es accesible; el tutorial local ya corrige el enrutado de MediaPipe del servidor. Si sigue fallando, revisa los errores 404 o de permisos en la consola/red del navegador.

**La cámara reconoce mal** → luz uniforme y palma frente a la cámara; en `tracking.js`, cuanto mayor es `SMOOTH` (por defecto 0.35), más suave pero más lento.

**Un dedo no sigue** → vuelve a capturar las tres poses; si una dirección está invertida, vuelve a capturar la pose correspondiente; el pulgar solo flexiona y no participa en el splay.

**A mitad de puño un servo se invierte** → el splay debe atenuarse a 0 con la flexión (`side *= (1 - curl)`); comprueba si el signo y la magnitud del control de splay son anómalos.

**¿Cómo se cambia el controlador de la web?** → en el desplegable «controlador» de la parte superior, elige SCS0009 o PWM; PWM requiere seleccionar el puerto serie a 115200; ver [Descripción general del control web](../03-web-control/README.md).

## Aplicación de escritorio

**La GUI de SCS0009 no lista el puerto serie** → vuelve a conectar el adaptador USB, instala el controlador o reinicia la GUI; en Linux comprueba `dialout`.

**El botón Connect está gris** → ya está conectado; pulsa primero Disconnect.

**La secuencia no mueve todos los dedos** → comprueba la velocidad de cada paso y asegúrate de que cada pose incluya los valores de los 8 servos.

**El indicador de bloqueo permanece activo** → comprueba si hay obstrucción mecánica; se activa cuando la diferencia entre objetivo y posición real es grande y no hay movimiento.

**La GUI PWM indica al arrancar que falta mediapipe** → inicia con el Python de `tools/tracking_env` o vuelve a ejecutar `tools/setup_tracking.bat`.

## Seguimiento de manos

**A mediapipe le falta el submódulo solutions** → instala `mediapipe==0.10.14` y confirma que Python 3.12 sea de 64 bits.

**Versión de dora incompatible** → alinea la versión de dora según `pyproject.toml` y los registros; limpia y reinstala.

**Fallo al cargar el modelo (rutas con caracteres chinos)** → coloca el proyecto/modelo en una ruta totalmente en inglés.

**La cámara no muestra imagen / permisos** → concede permiso de cámara al sistema; la máquina virtual necesita paso USB directo de la cámara.

**¿Qué diferencia hay entre el Demo oficial de SCS0009 y el seguimiento de la GUI PWM?** → SCS0009 usa la cadena completa dora + MuJoCo IK; la versión PWM ofrece seguimiento ligero con MediaPipe integrado en la GUI, y el Demo dora no está en el módulo. Ver [Seguimiento de manos SCS0009](../05-hand-tracking/scs0009.md) / [Seguimiento de manos PWM](../05-hand-tracking/pwm.md).

## Más

- [Comparación de versiones y selección](../00-product/version-comparison.md)
- [Descripción general del hardware](../01-hardware/overview.md)
- [Descargas y recursos](../00-product/downloads.md)
