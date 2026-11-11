---
title: "Tutorial de utilização do Arduino Nano"
description: "Executar o «02 programa de demonstração» do AmazingHand com um Arduino Nano (328P) e a placa controladora dos servos: cablagem, instalação de bibliotecas, compilação/carregamento e resultado."
version: scs0009
---

# Tutorial de utilização do Arduino Nano

> Esta página é a demonstração com Arduino Nano da **versão de servos de barramento SCS0009**. Para cablagem TTL e definição de IDs, ver [Depuração e calibração dos servos SCS0009](../06-servo-tuning/scs0009.md); para mais exemplos, ver [Exemplos Arduino / Python](examples.md).


## Modo de cablagem (placa controladora dos servos + placa Nano)

**Verifique bem a posição dos pinos da placa Nano (ou seja, a placa de desenvolvimento 328P)!**

![Posição dos pinos da placa Nano (1)](../../assets/robot-arms/amazing-hand/arduino-nano/01.png)

![Posição dos pinos da placa Nano (2)](../../assets/robot-arms/amazing-hand/arduino-nano/02.png)

![Posição dos pinos da placa Nano (3)](../../assets/robot-arms/amazing-hand/arduino-nano/03.png)

![Posição dos pinos da placa Nano (4)](../../assets/robot-arms/amazing-hand/arduino-nano/04.png)

A descrição seguinte refere-se ao processo de depuração com microcontrolador. O microcontrolador executa continuamente o programa de demonstração em ciclo; basta desligar o cabo de dados para parar.

## Executar o "02 programa de demonstração"

1. Instale o Arduino IDE.

2. De acordo com a **mão esquerda ou direita**, abra o ficheiro `.ino` correspondente.

   ![Ficheiros ino do 02 programa de demonstração correspondentes à mão esquerda/direita](../../assets/robot-arms/amazing-hand/arduino-nano/05.png)

3. Antes de compilar e carregar o programa Arduino para a placa Nano, instale a **biblioteca FTServo** e a **biblioteca SCServo** no «Gestor de Bibliotecas».

   ![Instalação das bibliotecas FTServo e SCServo no Gestor de Bibliotecas](../../assets/robot-arms/amazing-hand/arduino-nano/06.png)

4. Tipo de placa Nano: escolha «**Arduino Nano**».

   ![Seleção do tipo de placa Arduino Nano](../../assets/robot-arms/amazing-hand/arduino-nano/07.png)

5. Compile e carregue.

> **Atenção:** nesta altura, o PC está ligado apenas à placa Nano, que ainda não está ligada à placa controladora dos servos (ou seja, não está ligada à mão robótica).

Após o carregamento ser bem-sucedido, ligue a placa Nano à placa controladora dos servos com três cabos jumper; os servos ligam-se à placa controladora dos servos. Consulte [Modo de cablagem ao depurar com a placa MEGA328P Nano](https://juxitech.feishu.cn/wiki/Wt46wtt26imdWkkQlxTcL87qnHd#share-HdS4dNgwyo2seVxRZ9PcZ1R3nuc).

A mão robótica executa continuamente o «02 programa de demonstração»; o resultado é o seguinte:

![Resultado da execução do 02 programa de demonstração](../../assets/robot-arms/amazing-hand/arduino-nano/08.png)
