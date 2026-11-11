---
title: "Comparação e seleção entre as versões SCS0009 e PWM"
description: "Comparação completa dos dois esquemas de hardware do AmazingHand: servos, feedback, controlador, alimentação, comunicação, ID/canais, firmware e cenários de aplicação."
version: both
---

# Comparação e seleção entre as versões SCS0009 e PWM

A estrutura mecânica do AmazingHand é idêntica, mas existem dois esquemas de servos. A seleção depende sobretudo da necessidade de **feedback de posição, controlo preciso de ângulos e recolha de dados**.

## Conclusão rápida

- **Escolha SCS0009**: se necessita de leitura de posição/temperatura/tensão, ângulos precisos e integração com o braço robótico SO-ARM101 para recolha e treino de dados LeRobot.
- **Escolha PWM**: demonstrações autónomas, interação por gestos, início rápido via web/desktop, sem necessidade de feedback.
- **Não misture**: ligue apenas um dos conjuntos de hardware de cada vez; alimentação, protocolo e firmware são diferentes.

## Comparação completa

| Item de comparação | Versão de barramento série SCS0009 | Versão de servos PWM |
|--------|--------------------|------------|
| Motivo recomendado | Controlo preciso de ângulos + leitura de dados; pode ligar-se ao braço robótico SO-ARM101 para recolha e treino de dados LeRobot | Demonstrações autónomas, interação por gestos, início rápido |
| Modelo de servo | Servos de barramento série Feetech SCS0009 ×8 | Servos PWM **digitais** PTK 7452 MG-D ×8 |
| Parâmetros dos servos | 2,3 kg·cm@6V, 300° controláveis, precisão de 0,293° | 4,5 kg·cm@7,4V (cerca de 2,8–3 kg·cm com a alimentação de 5V deste esquema), 180°±10°, atualização a 333 Hz |
| Feedback de posição/temperatura/tensão/velocidade | ✅ Suporta leitura | ❌ Sem leitura; impossível detetar bloqueio ou perda de passos |
| Controlador | Nenhum integrado; PC/Raspberry Pi ligado diretamente através da placa controladora de barramento | Firmware integrado no ESP32-S3 |
| Concentrador | Placa controladora de servos + concentrador de barramento série de 9 vias | Placa adaptadora PWM (8 tomadas 3P + 5V/GND) |
| Alimentação | Entrada de 7–12V (DC5521) na placa controladora; servos nominalmente de 6V | 5V / 3A ou mais; a placa adaptadora e o ESP32 têm de ter massa comum |
| Baudrate | **1,000,000** | Os servos não têm baudrate; série entre PC e ESP32 a **115200 8N1** |
| ID do servo | Obrigatório definir: mão direita 1–8, mão esquerda 11–18 | Sem ID; canais fixos CH1–CH8 (indicador 1/2, médio 3/4, anelar 5/6, polegar 7/8), cablagem idêntica nas duas mãos |
| Ligação de comunicação | PC → placa controladora → barramento → 8 servos | PC → série USB 115200 → ESP32 → 8 canais PWM |
| Forma dos comandos | Protocolo de barramento Feetech, ângulo enviado diretamente | Frames binários: `0x01–0x0A / 0x0C` gestos, `0xF0` acionamento direto, `0xF1` mão esquerda/direita, `0x00` NOP, `0xFE` repetir, `0xFF` parar |
| Firmware | Nenhum (não é necessário gravar) | Requer compilação com ESP-IDF ou gravação direta do `amazinghand_pwm.bin` pré-compilado |
| Mão esquerda/direita | IDs de servo diferentes (direita 1–8, esquerda 11–18) | O mesmo grupo de canais, mapeamento no código + `0xF1` para escolher o lado |
| Libertação do binário | Suporta comutação/libertação do binário | Não suporta; a paragem de emergência apenas interrompe o gesto, e os servos continuam alimentados e mantêm a posição |
| Controlo de velocidade | Suporta parâmetro de velocidade | Os frames de acionamento direto não têm parâmetro de velocidade |

## Pontos essenciais da versão SCS0009

- Cada servo tem um ID único; mão direita 1–8, mão esquerda 11–18; após alterar a cablagem ou substituir um servo, é obrigatório voltar a definir o ID.
- Utiliza um barramento série com leitura de posição, velocidade, tensão e temperatura, adequado a controlo em malha fechada e recolha de dados.
- O PC/Raspberry Pi controla diretamente através da placa controladora de barramento USB, sem necessidade de firmware adicional num MCU.
- Alimentação de 7–12V na placa controladora de barramento (servos de gama 6V); atenção à massa comum com a placa controladora.
- Adequado a fluxos de treino com feedback articular, como SO-ARM101 e LeRobot.

## Pontos essenciais da versão PWM

- Utiliza **servos digitais PTK 7452 MG-D** (333 Hz, 500–2500 µs); não é possível substituir diretamente por servos analógicos de 50 Hz como o SG90.
- Servo nominal de 4,5 kg·cm@7,4V; neste esquema, com alimentação de 5V/3A, o binário real é de cerca de 2,8–3 kg·cm.
- O ESP32-S3 gera 8 canais PWM; o PC só precisa de enviar comandos pela série USB a 115200.
- Não tem feedback de posição; não é possível ler ângulo, temperatura ou tensão, nem detetar bloqueio/perda de passos.
- As duas mãos partilham o mesmo grupo de canais; em cada dedo, o servo da direita é ímpar e o da esquerda par, com o indicador fixo em CH1/2.
- Requer gravação de firmware; o repositório disponibiliza um binário pré-compilado, e também é possível compilar com ESP-IDF.
- Adequado a demonstrações autónomas, interação por gestos e início rápido via web/desktop; não é adequado a treino LeRobot dependente de feedback.

## Próximos passos

- [Início rápido SCS0009](../02-quick-start/scs0009.md)
- [Início rápido PWM](../02-quick-start/pwm.md)
- [Visão geral do hardware](../01-hardware/overview.md)
- [Downloads e recursos](downloads.md)
