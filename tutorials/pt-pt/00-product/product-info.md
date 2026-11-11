---
title: "Documentação do produto AmazingHand"
description: "Documentação do produto da mão robótica de destreza AmazingHand: estrutura mecânica, dimensões, carga, dois esquemas de servos e recursos de código aberto."
version: both
---

# Documentação do produto AmazingHand

AmazingHand é uma mão robótica de destreza antropomórfica, de código aberto e imprimível em 3D, destinada a investigação em inteligência incorporada, educação em robótica e protótipos de interação humano-computador. O corpo da mão é idêntico; existem atualmente dois conjuntos de hardware: **servos de barramento série SCS0009** e **servos PWM (ESP32-S3)**.

## Estrutura mecânica

- **4 dedos, 8 graus de liberdade**: cada dedo tem 2 graus de liberdade (flexão/extensão + abertura), acionados por dois servos através de um mecanismo paralelo de acionamento diferencial.
- **Atuadores integrados**: todos os servos estão montados na mão, sem necessidade de cabos até ao antebraço.
- **Impressão 3D**: a carcaça e as ligações podem ser impressas; a mão completa pesa cerca de 400 g.
- **Suporte para ambas as mãos**: pode utilizar-se apenas a mão esquerda ou a direita, ou as duas em coordenação num robô.
- **Interface de punho**: o design original é compatível com o punho Orbita 3D do Reachy 2, podendo também adaptar-se a outros braços robóticos.

## Parâmetros básicos

| Parâmetro | Especificação |
|------|------|
| Peso | Cerca de 0,416 kg |
| Número de dedos | 4 |
| Graus de liberdade por dedo | 2 DoF |
| Altura estendida (sem base) | 195 mm |
| Largura da palma | 105 mm |
| Espessura da palma | Cerca de 90 mm |
| Distância máxima entre indicador e polegar | 180 mm |
| Carga por dedo | Cerca de 0,2 kg |
| Carga máxima com os quatro dedos fechados | Cerca de 0,5 kg |

> A carga, a tensão e os parâmetros dos servos variam conforme a versão de servos escolhida; consulte a [Comparação de versões e seleção](version-comparison.md) para o quadro completo.

## Dois esquemas de hardware

| Item | Versão de barramento série SCS0009 | Versão de servos PWM |
|------|--------------------|------------|
| Servos | Feetech SCS0009 ×8 | Servos PWM digitais PTK 7452 MG-D ×8 |
| Controlo | PC/Raspberry Pi + placa controladora de barramento | Firmware integrado no ESP32-S3 |
| Feedback | Leitura de posição/velocidade/tensão/temperatura | Sem leitura |
| Aplicação | Precisão, recolha de dados, LeRobot / SO-ARM101 | Demonstrações autónomas, interação por gestos, início rápido |

## Ecossistema de software

- **Controlo web**: sliders no navegador, 19 poses predefinidas, teleoperação por câmara com MediaPipe, com suporte para comutação entre drivers SCS0009 / PWM.
- **Aplicação de desktop**: o SCS0009 usa `AmazingHandControl` (GUI Tkinter + CLI); o PWM usa `AmazingHand-PWM/tools/hand_gui.py`.
- **Seguimento de mãos**: o SCS0009 disponibiliza a Demo oficial dora + IK em MuJoCo; o PWM dispõe de seguimento MediaPipe integrado na GUI.
- **Recursos de código aberto**: CAD, documentação de montagem/impressão e exemplos Arduino/Python estão no repositório.

## Recursos de código aberto

- [Guia de montagem PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [Recomendações de impressão 3D PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [Visão geral do AmazingHand PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [CAD / STL / STEP](../../../AmazingHand-main/cad/)
- [Projeto oficial original (Pollen Robotics)](https://github.com/pollen-robotics/AmazingHand)

## Próximos passos

- [Comparação de versões e seleção](version-comparison.md)
- [Visão geral do hardware](../01-hardware/overview.md)
- [Início rápido SCS0009](../02-quick-start/scs0009.md)
- [Início rápido PWM](../02-quick-start/pwm.md)
