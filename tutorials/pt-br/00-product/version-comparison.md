---
title: "Comparação e escolha entre as versões SCS0009 e PWM"
description: "Comparação completa das duas opções de hardware do AmazingHand: servos, feedback, controlador, alimentação, comunicação, ID/canal, firmware e cenários de uso."
version: both
---

# Comparação e escolha entre as versões SCS0009 e PWM

A estrutura da mão do AmazingHand é a mesma, mas há duas opções de servos. A escolha depende principalmente de você precisar de **feedback de posição, controle preciso de ângulo e coleta de dados**.

## Conclusão rápida

- **Escolha o SCS0009**: se precisa de leitura de posição/temperatura/tensão, ângulos precisos e integração com o braço robótico SO-ARM101 para coleta de dados e treinamento LeRobot.
- **Escolha o PWM**: para demonstrações independentes, interação por gestos e início rápido no navegador/desktop, sem necessidade de feedback.
- **Não misture**: conecte apenas um conjunto de hardware por vez; alimentação, protocolo e firmware são diferentes.

## Comparação completa

| Item de comparação | Versão de barramento serial SCS0009 | Versão com servos PWM |
|--------|--------------------|------------|
| Motivo da recomendação | Controle preciso de ângulo + leitura de dados; pode ser integrado ao braço SO-ARM101 para coleta de dados e treinamento LeRobot | Demonstrações independentes, interação por gestos, início rápido |
| Modelo do servo | Servos de barramento serial Feetech SCS0009 ×8 | Servos PWM **digitais** PTK 7452 MG-D ×8 |
| Parâmetros do servo | 2,3 kg·cm a 6 V, curso controlável de 300°, precisão de 0,293° | 4,5 kg·cm a 7,4 V (com a alimentação de 5 V deste projeto, cerca de 2,8–3 kg·cm), 180°±10°, atualização a 333 Hz |
| Feedback de posição/temperatura/tensão/velocidade | ✅ Leitura suportada | ❌ Sem leitura, não detecta travamento nem perda de passos |
| Controlador | Sem placa embutida; PC/Raspberry Pi conectados diretamente pela placa driver de barramento | Firmware embutido no ESP32-S3 |
| Hub de conexão | Placa driver de servos + hub de barramento serial de 9 vias | Placa adaptadora PWM (8 conectores 3P + 5V/GND) |
| Alimentação | 7–12 V (DC5521) na entrada da placa driver; servos especificados para 6 V | 5 V / 3 A ou mais; a placa adaptadora e o ESP32 devem ter aterramento comum |
| Baudrate | **1.000.000** | O servo não tem baudrate; serial PC↔ESP32 a **115200 8N1** |
| ID do servo | Obrigatório definir: mão direita 1–8, mão esquerda 11–18 | Sem ID; canais fixos CH1–CH8 (indicador 1/2, médio 3/4, anelar 5/6, polegar 7/8), com a mesma fiação para as duas mãos |
| Link de comunicação | PC → placa driver → barramento → 8 servos | PC → serial USB 115200 → ESP32 → 8 canais PWM |
| Formato dos comandos | Protocolo de barramento Feetech, ângulos enviados diretamente | Quadros binários: `0x01–0x0A / 0x0C` gestos, `0xF0` acionamento direto, `0xF1` mão esquerda/direita, `0x00` NOP, `0xFE` repetir, `0xFF` parar |
| Firmware | Nenhum (não precisa ser gravado) | Requer compilação com ESP-IDF ou gravação do `amazinghand_pwm.bin` pré-compilado |
| Mão esquerda/direita | IDs de servo diferentes (direita 1–8, esquerda 11–18) | O mesmo conjunto de canais, mapeamento no código + `0xF1` para escolher o lado |
| Liberação de torque | Suporta ativar/liberar o torque | Não suporta; a parada de emergência só aborta o gesto e os servos continuam energizados mantendo a posição |
| Controle de velocidade | Suporta parâmetro de velocidade | Os quadros de acionamento direto não têm parâmetro de velocidade |

## Pontos-chave da versão SCS0009

- Cada servo tem um ID único; mão direita 1–8 e esquerda 11–18. Após refazer a fiação ou trocar um servo, é preciso redefinir o ID.
- Usa barramento serial e permite ler posição, velocidade, tensão e temperatura, sendo adequado para controle em malha fechada e coleta de dados.
- O PC/Raspberry Pi controla diretamente pela placa driver de barramento USB, sem precisar de firmware de MCU adicional.
- Alimentação de 7–12 V na entrada da placa driver de barramento (servos de 6 V); atenção ao aterramento comum com a placa driver.
- Adequado para integrar a fluxos de treinamento que exigem feedback de juntas, como SO-ARM101 e LeRobot.

## Pontos-chave da versão PWM

- Usa **servos digitais PTK 7452 MG-D** (333 Hz, 500–2500 µs); servos analógicos de 50 Hz como o SG90 não podem substituí-los diretamente.
- Os servos são especificados em 4,5 kg·cm a 7,4 V; com a alimentação de 5 V/3 A deste projeto, o torque real fica em cerca de 2,8–3 kg·cm.
- O ESP32-S3 gera os 8 canais PWM; o PC só precisa enviar comandos pela serial USB a 115200.
- Não há feedback de posição; não é possível ler ângulo, temperatura ou tensão, nem detectar travamento/perda de passos.
- As duas mãos usam o mesmo conjunto de canais; em cada par de dedos, o servo da direita é o canal ímpar e o da esquerda o par, com o indicador sempre em CH1/2.
- Requer gravação de firmware; o repositório fornece um bin pré-compilado, e também é possível compilar com ESP-IDF.
- Adequado para demonstrações independentes, interação por gestos e início rápido no navegador/desktop; não é adequado para treinamento LeRobot que depende de feedback.

## Próximos passos

- [Início rápido com SCS0009](../02-quick-start/scs0009.md)
- [Início rápido com PWM](../02-quick-start/pwm.md)
- [Visão geral do hardware](../01-hardware/overview.md)
- [Downloads e recursos](downloads.md)
