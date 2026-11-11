---
title: "Exemplos Arduino e Python"
description: "Exemplos oficiais Arduino/Python do AmazingHand: biblioteca SCServo, ferramenta de depuração Feetech, modos de cablagem do TTL Linker, porta série do Arduino Uno/Mega e scripts Python básicos."
version: scs0009
---

# Exemplos Arduino e Python

Esta página reúne os exemplos oficiais e os pontos essenciais de cablagem de `AmazingHand-main/ArduinoExample/` e `AmazingHand-main/PythonExample/`.

## Exemplos Arduino

### Preparação

- Instale a biblioteca **SCServo** no Gestor de Bibliotecas do Arduino IDE.
- Utilize a ferramenta de depuração Feetech FD para definir o ID dos servos (`feetech debug tool`).
- Entre o Arduino e o TTL Linker, **ligue RX/TX em cruz**.

### Modo Link: alterar o ID dos servos

1. Carregue primeiro o exemplo `Blink` no Arduino.
2. Ligue segundo o modo Link e abra o software Feetech para alterar o ID.

![Cablagem no modo Link](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Link-mode.jpg)

![Instalação da biblioteca SCServo](../../assets/robot-arms/amazing-hand/arduino-extension/SCServo.jpg)

### Modo Control: o Arduino controla os servos

Após carregar um programa personalizado, ligue segundo o modo Control:

![Cablagem no modo Control](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Control-mode.jpg)

- **Arduino Uno** (apenas uma porta série): use a porta série por software/pinos indicados conforme a figura.
- **Arduino Mega**: use **RX1 / TX1 (19 / 18)**.

![Cablagem da porta série do Uno](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Uno.jpg)

![Cablagem da porta série do Mega](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Mega.jpg)

> Os números dos pinos, as versões das bibliotecas e a orientação do TTL Linker seguem a serigrafia da placa real; antes de alterar o ID, confirme a alimentação do barramento e a massa comum.

## Exemplos Python

`AmazingHand-main/PythonExample/` disponibiliza 4 scripts básicos:

| Script | Função |
|------|------|
| `AmazingHand_Demo.py` | Demonstração básica de uma mão: ligar ao barramento, executar movimentos |
| `AmazingHand_Demo_Both.py` | Demonstração com as duas mãos |
| `AmazingHand_FingerTest.py` | Teste de um dedo |
| `AmazingHand_Hand_FingerMiddlePos.py` | Calibração da posição central dos dedos |

Antes de utilizar:

1. Defina o ID dos servos com o software Feetech (direita 1–8, esquerda 11–18).
2. Instale `pyserial` e, após alterar o nome da porta série/baudrate conforme o script, execute.
3. Confirme que a alimentação externa dos servos está ligada e com massa comum com a placa controladora de barramento.

> Estes são os exemplos básicos oficiais; para uma GUI/CLI mais completa, ver [Aplicação de desktop SCS0009](../04-desktop/scs0009.md); para cablagem TTL e posição central, ver [Depuração e calibração dos servos SCS0009](../06-servo-tuning/scs0009.md).

## Localização do código-fonte

- [`AmazingHand-main/ArduinoExample/`](../../../AmazingHand-main/ArduinoExample/)
- [`AmazingHand-main/PythonExample/`](../../../AmazingHand-main/PythonExample/)
