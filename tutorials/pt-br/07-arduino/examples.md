---
title: "Exemplos em Arduino e Python"
description: "Exemplos oficiais de Arduino/Python do AmazingHand: biblioteca SCServo, ferramenta de depuração Feetech, modelos de fiação do TTL Linker, serial do Arduino Uno/Mega e scripts básicos em Python."
version: scs0009
---

# Exemplos em Arduino e Python

Esta página reúne os exemplos oficiais e os pontos principais de fiação de `AmazingHand-main/ArduinoExample/` e `AmazingHand-main/PythonExample/`.

## Exemplos em Arduino

### Preparação

- Instale a biblioteca **SCServo** no Gerenciador de Bibliotecas do Arduino IDE.
- Use a ferramenta de depuração FD da Feetech para definir o ID do servo (`feetech debug tool`).
- Entre o Arduino e o TTL Linker, faça a **ligação cruzada RX/TX**.

### Modo Link: alterar o ID do servo

1. Primeiro, envie o exemplo `Blink` ao Arduino.
2. Faça a fiação no modo Link e abra o software Feetech para alterar o ID.

![Fiação no modo Link](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Link-mode.jpg)

![Instalação da biblioteca SCServo](../../assets/robot-arms/amazing-hand/arduino-extension/SCServo.jpg)

### Modo Control: Arduino controlando os servos

Depois de enviar um programa personalizado, faça a fiação no modo Control:

![Fiação no modo Control](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Control-mode.jpg)

- **Arduino Uno** (só tem uma serial): use a serial por software/pinos indicados, conforme a figura.
- **Arduino Mega**: use **RX1 / TX1 (19 / 18)**.

![Fiação serial do Uno](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Uno.jpg)

![Fiação serial do Mega](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Mega.jpg)

> Os números de pino, as versões das bibliotecas e a direção do TTL Linker devem seguir a serigrafia da placa real; antes de alterar o ID, confirme a alimentação do barramento e o aterramento comum.

## Exemplos em Python

`AmazingHand-main/PythonExample/` fornece 4 scripts básicos:

| Script | Função |
|------|------|
| `AmazingHand_Demo.py` | demonstração básica de uma mão: conecta ao barramento e executa movimentos |
| `AmazingHand_Demo_Both.py` | demonstração com as duas mãos |
| `AmazingHand_FingerTest.py` | teste de um dedo |
| `AmazingHand_Hand_FingerMiddlePos.py` | calibração do meio dos dedos |

Antes de usar:

1. Defina os IDs dos servos com o software Feetech (direita 1–8, esquerda 11–18).
2. Instale `pyserial` e ajuste o nome da porta serial/baudrate dentro do script antes de executar.
3. Confirme que a fonte externa dos servos está conectada e tem aterramento comum com a placa driver de barramento.

> Estes são os exemplos básicos oficiais; para uma GUI/CLI mais completa, veja [Aplicativo de desktop SCS0009](../04-desktop/scs0009.md); para fiação TTL e meio, [Depuração e calibração de servos SCS0009](../06-servo-tuning/scs0009.md).

## Localização do código-fonte

- [`AmazingHand-main/ArduinoExample/`](../../../AmazingHand-main/ArduinoExample/)
- [`AmazingHand-main/PythonExample/`](../../../AmazingHand-main/PythonExample/)
