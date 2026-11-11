---
title: "Cablagem, GPIO e alimentação PWM"
description: "Versão de servos PWM do AmazingHand: ESP32-S3, 8 canais PWM, mapeamento GPIO, alimentação e descrição do modelo de servo."
version: pwm
---

# Cablagem, GPIO e alimentação PWM

Na versão PWM, o ESP32-S3 gera diretamente os 8 sinais PWM; o PC só precisa de enviar comandos pela porta série USB.

## Lista de hardware

| Item | Especificação |
|------|------|
| Controlador | Placa de desenvolvimento ESP32-S3 (Youxin YX-ESP32-S3 ou equivalente) |
| Servos | Servos PWM **digitais** PTK 7452 MG-D ×8 (333 Hz) |
| Placa adaptadora | Placa adaptadora para servos PWM (8 tomadas 3P + 5V/GND) |
| Alimentação | 5V / 3A ou mais; a placa adaptadora e o ESP32 têm de ter massa comum |

> Servo nominal de 4,5 kg·cm@7,4V; neste esquema, com alimentação de 5V, o binário real é de cerca de 2,8–3 kg·cm.
>
> ⚠️ Servos analógicos de 50 Hz como o SG90 não podem substituir diretamente o firmware de 333 Hz; ao trocar o modelo, é obrigatório alterar simultaneamente `LEDC_FREQ` e a calibração da largura de pulso.

## Canal → GPIO → dedo

| Canal | GPIO | Articulação | Canal | GPIO | Articulação |
|------|------|------|------|------|------|
| PWM1 / CH1 | 4 | Indicador, articulação 1 | PWM5 / CH5 | 15 | Anelar, articulação 1 |
| PWM2 / CH2 | 5 | Indicador, articulação 2 | PWM6 / CH6 | 16 | Anelar, articulação 2 |
| PWM3 / CH3 | 6 | Médio, articulação 1 | PWM7 / CH7 | 17 | Polegar, articulação 1 |
| PWM4 / CH4 | 7 | Médio, articulação 2 | PWM8 / CH8 | 18 | Polegar, articulação 2 |

- A cablagem é idêntica nas duas mãos; o indicador está sempre em CH1/2.
- Em cada dedo, o servo da direita é o canal ímpar e o da esquerda o canal par.
- O número do canal é fixado pelo firmware; não é necessário definir IDs de servo.

## Passos de cablagem

1. Ligue as fichas 3P dos 8 servos às barras de pinos dos servos 1–8 da placa adaptadora, pela ordem de numeração.
2. Ligue PWM1–PWM8 da placa adaptadora aos GPIO 4, 5, 6, 7, 15, 16, 17, 18 do ESP32-S3.
3. Ligue 5V/GND da placa adaptadora à alimentação externa de 5V/3A.
4. Ligue outra saída de 5V/GND da placa adaptadora ao ESP32-S3, **com massa comum obrigatória**.
5. Ordem dos fios 3P dos servos: castanho/preto GND, vermelho V+, laranja/branco/amarelo sinal; ligue segundo a serigrafia da placa adaptadora, sem inverter.

## Alimentação e segurança

- Quando os 8 servos se movem em simultâneo, a corrente é elevada; recomenda-se 5V/3A ou mais, evitando depender apenas da alimentação USB.
- Antes da primeira alimentação, coloque a mão na posição central e monte os braços dos servos a 90°.
- Os canais não utilizados podem ficar livres, sem afetar os restantes; tenha atenção ao isolamento das fichas livres.
- Abrir a porta série pode reiniciar o ESP32; o firmware regressa automaticamente ao centro.

## Próximos passos

- [Início rápido PWM](../02-quick-start/pwm.md) (gravação do firmware + GUI/web)
- [Protocolo e calibração PWM](../06-servo-tuning/pwm.md)
- [Controlo web](../03-web-control/pwm.md)
