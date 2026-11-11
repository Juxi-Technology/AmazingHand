---
title: "Visão geral dos tutoriais AmazingHand"
description: "Entrada unificada dos tutoriais da mão robótica de destreza AmazingHand: seleção de produto, cablagem de hardware, início rápido, controlo web, aplicação de desktop, seguimento de mãos, afinação dos servos e FAQ para as versões com servos de barramento série SCS0009 e com servos PWM."
version: both
---

# Tutoriais da mão robótica de destreza AmazingHand

AmazingHand é uma mão robótica de destreza antropomórfica, de código aberto e imprimível em 3D: 4 dedos, 8 graus de liberdade, com todos os atuadores integrados na mão, pesando cerca de 400 g no total. Existem atualmente dois conjuntos de hardware; a estrutura mecânica é idêntica, mas os servos, as placas controladoras e o modo de comunicação são diferentes.

## Escolher primeiro a versão

| Item de comparação | Versão de barramento série SCS0009 | Versão de servos PWM |
|--------|--------------------|------------|
| Cenário recomendado | Controlo preciso de ângulos, leitura de dados, integração com SO-ARM101 / recolha e treino de dados LeRobot | Demonstrações autónomas, interação por gestos, início rápido via web/desktop |
| Servos | Servos de barramento série Feetech SCS0009 ×8 | Servos PWM **digitais** PTK 7452 MG-D ×8 |
| Parâmetros dos servos | 2,3 kg·cm@6V, 300° controláveis, precisão de 0,293° | 4,5 kg·cm@7,4V (cerca de 2,8–3 kg·cm com alimentação de 5V), 180°±10°, 333 Hz |
| Feedback de posição/temperatura/tensão | ✅ Suportado | ❌ Sem leitura; impossível detetar bloqueio ou perda de passos |
| Controlador | Nenhum integrado; PC/Raspberry Pi ligado diretamente através da placa controladora de barramento | Firmware integrado no ESP32-S3 |
| Alimentação | Entrada de 7–12V (DC5521) na placa controladora | 5V / 3A ou mais, com massa comum obrigatória |
| Comunicação | Protocolo de barramento a 1,000,000 baud | Série entre PC e ESP32 a **115200** (o servo em si não tem baudrate) |
| ID do servo | Obrigatório definir: mão direita 1–8, mão esquerda 11–18 | Sem ID; canais fixos CH1–CH8: indicador 1/2, médio 3/4, anelar 5/6, polegar 7/8 |
| Firmware | Não é necessário gravar | Requer compilação com ESP-IDF ou gravação direta do binário pré-compilado |

> Se precisar de **leitura de posição, precisão ou recolha de dados para treino LeRobot**, escolha SCS0009; se apenas precisar de **demonstrações autónomas, interação por gestos e início rápido**, escolha PWM.

Consulta [Comparação de versões](00-product/version-comparison.md) para a comparação completa e as orientações de seleção.

## Navegar por modo de utilização

| Modo de utilização | Versão de barramento série SCS0009 | Versão de servos PWM |
|----------|--------------------|------------|
| Início rápido | [Início rápido SCS0009](02-quick-start/scs0009.md) | [Início rápido PWM](02-quick-start/pwm.md) |
| Controlo web | [Controlo web SCS0009](03-web-control/scs0009.md) | [Controlo web PWM](03-web-control/pwm.md) |
| Aplicação de desktop / CLI | [GUI e CLI SCS0009](04-desktop/scs0009.md) | [Aplicação de desktop PWM](04-desktop/pwm.md) |
| Seguimento de mãos | [Demo oficial SCS0009](05-hand-tracking/scs0009.md) | [Seguimento GUI / dora PWM](05-hand-tracking/pwm.md) |
| Depuração e calibração dos servos | [Depuração e calibração SCS0009](06-servo-tuning/scs0009.md) | [Protocolo e calibração PWM](06-servo-tuning/pwm.md) |
| Arduino / desenvolvimento secundário | [Arduino Nano](07-arduino/arduino-nano.md) · [Exemplos de código](07-arduino/examples.md) | O mesmo (estrutura mecânica partilhada) |

A visão geral do controlo web (comutação de driver, barra de porta série, descrição da interface) está em [README do controlo web](03-web-control/README.md).

## Antes de começar

- [Documentação do produto](00-product/product-info.md) — especificações, posicionamento, recursos
- [Comparação de versões e seleção](00-product/version-comparison.md) — diferenças completas entre os dois conjuntos de hardware
- [Visão geral do hardware](01-hardware/overview.md) — estrutura, CAD, montagem, impressão 3D
- [Cablagem SCS0009](01-hardware/scs0009.md) / [Cablagem PWM](01-hardware/pwm.md)
- [Instalação do kit de câmara](01-hardware/camera-kit.md)
- [Downloads e recursos](00-product/downloads.md)

## Avisos de segurança

- A alimentação externa dos servos e o ESP32/placa controladora têm de ter **massa comum**.
- Antes da primeira alimentação, coloque a mão na posição central e monte os braços dos servos nessa posição, para evitar bater no fim de curso.
- Os dois conjuntos de hardware, SCS0009 e PWM, devem ser ligados **apenas um de cada vez**; não os misture.
- Os servos PWM não têm feedback de posição: a paragem de emergência apenas interrompe o gesto, não permitindo ler ou libertar o binário como nos servos de barramento.

## Languages

[简体中文](../zh-hans/README.md) | [English](../en/README.md) | [Deutsch](../de/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (BR)](../pt-br/README.md) | [Português (PT)](../pt-pt/README.md) | [繁體中文](../zh-hant/README.md)
