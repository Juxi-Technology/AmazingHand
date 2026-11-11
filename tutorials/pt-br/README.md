---
title: "Visão geral dos tutoriais da mão dexterosa AmazingHand"
description: "Ponto de entrada unificado dos tutoriais da mão dexterosa AmazingHand: escolha de produto, fiação de hardware, início rápido, controle web, aplicativo de desktop, rastreamento de mãos, ajuste de servos e FAQ para as versões com servos de barramento SCS0009 e com servos PWM."
version: both
---

# Tutoriais da mão dexterosa AmazingHand

O AmazingHand é uma mão dexterosa antropomórfica de código aberto e imprimível em 3D: 4 dedos, 8 graus de liberdade, com todos os acionadores embutidos na mão e cerca de 400 g no total. Atualmente há duas opções de hardware; a estrutura da mão é a mesma, mas os servos, a placa driver e o método de comunicação são diferentes.

## Escolha a versão primeiro

| Item de comparação | Versão de barramento serial SCS0009 | Versão com servos PWM |
|--------|--------------------|------------|
| Cenários recomendados | Controle preciso de ângulo, leitura de dados, integração com SO-ARM101 / coleta de dados para treinamento LeRobot | Demonstrações independentes, interação por gestos, início rápido no navegador/desktop |
| Servo | Servos de barramento serial Feetech SCS0009 ×8 | Servos PWM **digitais** PTK 7452 MG-D ×8 |
| Parâmetros do servo | 2,3 kg·cm a 6 V, curso controlável de 300°, precisão de 0,293° | 4,5 kg·cm a 7,4 V (com alimentação de 5 V, cerca de 2,8–3 kg·cm), 180°±10°, 333 Hz |
| Feedback de posição/temperatura/tensão | ✅ Suportado | ❌ Sem leitura, não detecta travamento nem perda de passos |
| Controlador | Sem placa embutida; PC/Raspberry Pi conectados diretamente pela placa driver de barramento | Firmware embutido no ESP32-S3 |
| Alimentação | 7–12 V (DC5521) na entrada da placa driver | 5 V / 3 A ou mais, com aterramento comum obrigatório |
| Comunicação | Protocolo de barramento a 1.000.000 de baud | Serial PC↔ESP32 a **115200** (o servo em si não tem baudrate) |
| ID do servo | Obrigatório definir: mão direita 1–8, mão esquerda 11–18 | Sem ID; canais fixos CH1–CH8: indicador 1/2, médio 3/4, anelar 5/6, polegar 7/8 |
| Firmware | Não precisa ser gravado | Requer compilação com ESP-IDF ou gravação do bin pré-compilado |

> Se você precisa de **leitura de posição, precisão ou coleta de dados de treinamento LeRobot**, escolha o SCS0009; se só quer **demonstrações independentes, interação por gestos e início rápido**, escolha o PWM.

A comparação completa e as orientações de escolha estão em [Comparação de versões](00-product/version-comparison.md).

## Navegação por forma de uso

| Forma de uso | Versão de barramento serial SCS0009 | Versão com servos PWM |
|----------|--------------------|------------|
| Início rápido | [Início rápido com SCS0009](02-quick-start/scs0009.md) | [Início rápido com PWM](02-quick-start/pwm.md) |
| Controle web | [Controle web SCS0009](03-web-control/scs0009.md) | [Controle web PWM](03-web-control/pwm.md) |
| Aplicativo de desktop / CLI | [GUI e CLI SCS0009](04-desktop/scs0009.md) | [Aplicativo de desktop PWM](04-desktop/pwm.md) |
| Rastreamento de mãos | [Demo oficial SCS0009](05-hand-tracking/scs0009.md) | [GUI / rastreamento dora PWM](05-hand-tracking/pwm.md) |
| Depuração e calibração de servos | [Depuração e calibração SCS0009](06-servo-tuning/scs0009.md) | [Protocolo e calibração PWM](06-servo-tuning/pwm.md) |
| Arduino / desenvolvimento secundário | [Arduino Nano](07-arduino/arduino-nano.md) · [Código de exemplo](07-arduino/examples.md) | O mesmo (estrutura mecânica compartilhada) |

A visão geral do controle web (troca de driver, barra serial, descrição da interface) está em [README do controle web](03-web-control/README.md).

## Antes de começar

- [Informações do produto](00-product/product-info.md) — parâmetros, posicionamento, materiais
- [Comparação de versões e escolha](00-product/version-comparison.md) — diferenças completas entre os dois hardwares
- [Visão geral do hardware](01-hardware/overview.md) — estrutura, CAD, montagem, impressão 3D
- [Fiação SCS0009](01-hardware/scs0009.md) / [Fiação PWM](01-hardware/pwm.md)
- [Montagem do kit de câmera](01-hardware/camera-kit.md)
- [Downloads e recursos](00-product/downloads.md)

## Avisos de segurança

- A fonte externa dos servos e o ESP32/placa driver devem ter **aterramento comum**.
- Antes da primeira energização, posicione a mão no meio e instale os horns dos servos na posição do meio, para evitar bater no fim de curso.
- Conecte **apenas um** dos dois conjuntos de hardware (SCS0009 ou PWM) por vez; não os misture.
- Os servos PWM não têm feedback de posição; a parada de emergência só aborta o gesto e não permite ler nem liberar o torque como nos servos de barramento.

## Languages

[简体中文](../zh-hans/README.md) | [English](../en/README.md) | [Deutsch](../de/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (BR)](../pt-br/README.md) | [Português (PT)](../pt-pt/README.md) | [繁體中文](../zh-hant/README.md)
