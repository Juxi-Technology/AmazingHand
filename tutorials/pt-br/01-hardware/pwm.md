---
title: "Fiação, GPIO e alimentação PWM"
description: "Versão com servos PWM do AmazingHand: ESP32-S3, 8 canais PWM, mapeamento de GPIO, alimentação e modelo de servo."
version: pwm
---

# Fiação, GPIO e alimentação PWM

Na versão PWM, o ESP32-S3 gera diretamente os 8 sinais PWM; o computador só precisa enviar comandos pela serial USB.

## Lista de hardware

| Item | Especificação |
|------|------|
| Controlador | Placa de desenvolvimento ESP32-S3 (Youxin YX-ESP32-S3 ou equivalente) |
| Servo | Servos PWM **digitais** PTK 7452 MG-D ×8 (333 Hz) |
| Placa adaptadora | Placa adaptadora para servos PWM (8 conectores 3P + 5V/GND) |
| Alimentação | 5 V / 3 A ou mais; a placa adaptadora e o ESP32 devem ter aterramento comum |

> Os servos são especificados em 4,5 kg·cm a 7,4 V; com a alimentação de 5 V deste projeto, o torque real fica em cerca de 2,8–3 kg·cm.
>
> ⚠️ Servos analógicos de 50 Hz como o SG90 não podem substituir diretamente o firmware de 333 Hz; ao trocar o modelo, é preciso alterar juntos `LEDC_FREQ` e a calibração da largura de pulso.

## Canal → GPIO → Dedo

| Canal | GPIO | Junta | Canal | GPIO | Junta |
|------|------|------|------|------|------|
| PWM1 / CH1 | 4 | Junta 1 do indicador | PWM5 / CH5 | 15 | Junta 1 do anelar |
| PWM2 / CH2 | 5 | Junta 2 do indicador | PWM6 / CH6 | 16 | Junta 2 do anelar |
| PWM3 / CH3 | 6 | Junta 1 do médio | PWM7 / CH7 | 17 | Junta 1 do polegar |
| PWM4 / CH4 | 7 | Junta 2 do médio | PWM8 / CH8 | 18 | Junta 2 do polegar |

- A fiação é igual nas duas mãos; o indicador fica sempre em CH1/2.
- Em cada par de dedos, o servo da direita usa o canal ímpar e o da esquerda o par.
- O número do canal é fixo no firmware; não é preciso definir ID do servo.

## Passos da fiação

1. Conecte os conectores 3P dos 8 servos aos pinos dos servos 1–8 da placa adaptadora, seguindo a numeração.
2. Conecte PWM1–PWM8 da placa adaptadora aos GPIO 4, 5, 6, 7, 15, 16, 17 e 18 do ESP32-S3.
3. Conecte 5V/GND da placa adaptadora à fonte externa de 5 V/3 A.
4. Leve outro par 5V/GND da placa adaptadora ao ESP32-S3; o **aterramento comum é obrigatório**.
5. Ordem dos fios 3P do servo: marrom/preto GND, vermelho V+, laranja/branco/amarelo sinal; conecte conforme a serigrafia da placa adaptadora, sem inverter.

## Alimentação e segurança

- Com os 8 servos se movendo ao mesmo tempo, a corrente é alta; recomenda-se 5 V/3 A ou mais e evitar alimentar apenas pela USB.
- Antes da primeira energização, posicione a mão no meio e instale os horns dos servos a 90°.
- Os canais não utilizados podem ficar vazios sem afetar os demais; isole os conectores vazios.
- Abrir a porta serial pode reiniciar o ESP32; o firmware retorna automaticamente ao meio.

## Próximos passos

- [Início rápido com PWM](../02-quick-start/pwm.md) (gravação do firmware + GUI/web)
- [Protocolo e calibração PWM](../06-servo-tuning/pwm.md)
- [Controle web](../03-web-control/pwm.md)
