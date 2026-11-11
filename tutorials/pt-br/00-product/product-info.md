---
title: "Informações do produto AmazingHand"
description: "Informações do produto da mão dexterosa AmazingHand: estrutura mecânica, dimensões, carga, as duas opções de servos e recursos de código aberto."
version: both
---

# Informações do produto AmazingHand

O AmazingHand é uma mão dexterosa antropomórfica de código aberto e imprimível em 3D, voltada para pesquisa em inteligência corporificada, educação em robótica e protótipos de interação humano-robô. A estrutura da mão é a mesma; atualmente há duas opções de hardware: **servos de barramento serial SCS0009** e **servos PWM (ESP32-S3)**.

## Estrutura mecânica

- **4 dedos, 8 graus de liberdade**: cada dedo tem 2 graus de liberdade (flexão/extensão + abdução/adução), acionados por dois servos por meio de um mecanismo paralelo com acionamento diferencial.
- **Acionadores embutidos**: todos os servos ficam na mão, sem cabos saindo para o antebraço.
- **Impressão 3D**: a carcaça e as ligações podem ser impressas; a mão inteira pesa cerca de 400 g.
- **Suporte a duas mãos**: é possível usar a mão esquerda ou a direita isoladamente, ou as duas em um robô colaborativo.
- **Interface de punho**: o projeto original é compatível com o punho Orbita 3D do Reachy 2 e também pode ser adaptado a outros braços robóticos.

## Parâmetros básicos

| Parâmetro | Especificação |
|------|------|
| Peso | Aproximadamente 0,416 kg |
| Número de dedos | 4 |
| Graus de liberdade por dedo | 2 DoF |
| Altura estendida (sem a base) | 195 mm |
| Largura da palma | 105 mm |
| Espessura da palma | Cerca de 90 mm |
| Distância máxima entre indicador e polegar abertos | 180 mm |
| Carga por dedo | Cerca de 0,2 kg |
| Carga máxima com os quatro dedos cerrados | Cerca de 0,5 kg |

> Carga, tensão e parâmetros dos servos variam conforme a versão escolhida; para a comparação completa, veja [Comparação de versões e escolha](version-comparison.md).

## As duas opções de hardware

| Item | Versão de barramento serial SCS0009 | Versão com servos PWM |
|------|--------------------|------------|
| Servo | Feetech SCS0009 ×8 | Servos PWM digitais PTK 7452 MG-D ×8 |
| Controle | PC/Raspberry Pi + placa driver de barramento | Firmware embutido no ESP32-S3 |
| Feedback | Leitura de posição/velocidade/tensão/temperatura | Sem leitura |
| Aplicação | Precisão, coleta de dados, LeRobot / SO-ARM101 | Demonstrações independentes, interação por gestos, início rápido |

## Ecossistema de software

- **Controle web**: controles deslizantes no navegador, 19 poses predefinidas e teleoperação por câmera com MediaPipe, com troca entre os drivers SCS0009 / PWM.
- **Aplicativo de desktop**: o SCS0009 usa o `AmazingHandControl` (GUI Tkinter + CLI); o PWM usa `AmazingHand-PWM/tools/hand_gui.py`.
- **Rastreamento de mãos**: o SCS0009 oferece a Demo oficial dora + MuJoCo IK; o PWM oferece rastreamento com MediaPipe embutido na GUI.
- **Recursos de código aberto**: CAD, documentação de montagem/impressão e exemplos em Arduino/Python estão no repositório.

## Recursos de código aberto

- [Guia de montagem PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [Dicas de impressão 3D PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [Visão geral do AmazingHand PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [CAD / STL / STEP](../../../AmazingHand-main/cad/)
- [Projeto upstream oficial (Pollen Robotics)](https://github.com/pollen-robotics/AmazingHand)

## Próximos passos

- [Comparação de versões e escolha](version-comparison.md)
- [Visão geral do hardware](../01-hardware/overview.md)
- [Início rápido com SCS0009](../02-quick-start/scs0009.md)
- [Início rápido com PWM](../02-quick-start/pwm.md)
