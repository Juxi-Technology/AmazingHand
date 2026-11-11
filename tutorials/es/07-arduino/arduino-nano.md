---
title: "Tutorial de uso de Arduino Nano"
description: "Ejecutar el «programa de demostración 02» de AmazingHand con un Arduino Nano (328P) y una placa controladora de servos: cableado, instalación de bibliotecas, compilación, carga y resultado."
version: scs0009
---

# Tutorial de uso de Arduino Nano

> Esta página es la demostración con Arduino Nano de la **versión con servos de bus SCS0009**. Para el cableado TTL y la configuración de ID, consulta [Depuración y calibración de servos SCS0009](../06-servo-tuning/scs0009.md); para más ejemplos, [Ejemplos de Arduino / Python](examples.md).


## Cableado (placa controladora de servos + placa Nano)

**¡Fíjate bien en la posición de los pines de la placa Nano (es decir, la placa de desarrollo 328P)!**

![Posición de los pines de la placa Nano (1)](../../assets/robot-arms/amazing-hand/arduino-nano/01.png)

![Posición de los pines de la placa Nano (2)](../../assets/robot-arms/amazing-hand/arduino-nano/02.png)

![Posición de los pines de la placa Nano (3)](../../assets/robot-arms/amazing-hand/arduino-nano/03.png)

![Posición de los pines de la placa Nano (4)](../../assets/robot-arms/amazing-hand/arduino-nano/04.png)

Lo que se describe a continuación es el proceso de depuración con microcontrolador. El microcontrolador ejecuta el programa de demostración en bucle continuo; basta con desconectar el cable de datos para detenerlo.

## Ejecutar el «programa de demostración 02»

1. Instala Arduino IDE.

2. Según sea **mano izquierda o derecha**, abre el archivo `.ino` correspondiente.

   ![Archivos ino del programa de demostración 02 para mano izquierda/derecha](../../assets/robot-arms/amazing-hand/arduino-nano/05.png)

3. Antes de compilar y cargar el programa Arduino en la placa Nano, instala las bibliotecas **FTServo** y **SCServo** en el «Administrador de bibliotecas».

   ![Instalación de las bibliotecas FTServo y SCServo en el Administrador de bibliotecas](../../assets/robot-arms/amazing-hand/arduino-nano/06.png)

4. Tipo de placa Nano: selecciona «**Arduino Nano**».

   ![Selección del tipo de placa Arduino Nano](../../assets/robot-arms/amazing-hand/arduino-nano/07.png)

5. Compila y carga.

> **Nota:** en este momento el PC solo está conectado a la placa Nano, y la placa Nano no debe estar conectada a la placa controladora de servos (es decir, no conectada a la mano diestra).

Tras cargarlo correctamente, conecta la placa Nano a la placa controladora de servos con tres cables de puente y conecta los servos a la placa controladora; consulta [Método de cableado al depurar con la placa MEGA328P Nano](https://juxitech.feishu.cn/wiki/Wt46wtt26imdWkkQlxTcL87qnHd#share-HdS4dNgwyo2seVxRZ9PcZ1R3nuc).

La mano diestra ejecutará el «programa de demostración 02» en bucle continuo; el resultado es el siguiente:

![Resultado de ejecución del programa de demostración 02](../../assets/robot-arms/amazing-hand/arduino-nano/08.png)
