---
title: "Tutorial de uso do Arduino Nano"
description: "Executar o «02 演示程序» do AmazingHand com Arduino Nano (328P) e placa driver de servos: fiação, instalação das bibliotecas, compilação, envio e resultado."
version: scs0009
---

# Tutorial de uso do Arduino Nano

> Esta página é a demonstração com Arduino Nano da **versão com servos de barramento SCS0009**. Para a fiação TTL e a definição de ID, veja [Depuração e calibração de servos SCS0009](../06-servo-tuning/scs0009.md); para mais exemplos, [Exemplos em Arduino e Python](examples.md).


## Fiação (placa driver de servos + placa Nano)

**Confira com atenção a posição dos pinos da placa Nano (ou seja, da placa de desenvolvimento 328P)!**

![Posição dos pinos da placa Nano (1)](../../assets/robot-arms/amazing-hand/arduino-nano/01.png)

![Posição dos pinos da placa Nano (2)](../../assets/robot-arms/amazing-hand/arduino-nano/02.png)

![Posição dos pinos da placa Nano (3)](../../assets/robot-arms/amazing-hand/arduino-nano/03.png)

![Posição dos pinos da placa Nano (4)](../../assets/robot-arms/amazing-hand/arduino-nano/04.png)

O processo descrito abaixo é o de depuração com microcontrolador. O microcontrolador executa o programa de demonstração em loop; basta desconectar o cabo de dados para parar.

## Executar o «02 演示程序»

1. Instale o Arduino IDE por conta própria.

2. Conforme a **mão esquerda ou direita**, abra o arquivo `.ino` correspondente.

   ![Arquivos .ino do «02 演示程序» correspondentes à mão esquerda/direita](../../assets/robot-arms/amazing-hand/arduino-nano/05.png)

3. Antes de compilar e enviar o programa Arduino para a placa Nano, instale as **bibliotecas FTServo** e **SCServo** no «Gerenciador de Bibliotecas».

   ![Instalação das bibliotecas FTServo e SCServo no Gerenciador de Bibliotecas](../../assets/robot-arms/amazing-hand/arduino-nano/06.png)

4. No tipo de placa Nano, selecione «**Arduino Nano**».

   ![Seleção do tipo de placa Arduino Nano](../../assets/robot-arms/amazing-hand/arduino-nano/07.png)

5. Compile e envie.

> **Atenção:** neste momento, o PC está conectado apenas à placa Nano, e a placa Nano ainda não está conectada à placa driver de servos (ou seja, não está conectada à mão dexterosa).

Após o envio bem-sucedido, conecte a placa Nano à placa driver de servos com três jumpers e os servos à placa driver, conforme [a fiação para depuração com a placa MEGA328P Nano](https://juxitech.feishu.cn/wiki/Wt46wtt26imdWkkQlxTcL87qnHd#share-HdS4dNgwyo2seVxRZ9PcZ1R3nuc).

A mão dexterosa executa o «02 演示程序» continuamente em loop; o resultado é o seguinte:

![Resultado da execução do «02 演示程序»](../../assets/robot-arms/amazing-hand/arduino-nano/08.png)
