---
title: "Visão geral do hardware: estrutura, CAD e montagem"
description: "Estrutura mecânica, CAD/STL/STEP, montagem e recursos de impressão 3D do AmazingHand."
version: both
---

# Visão geral do hardware

As duas opções de servos compartilham a mesma estrutura mecânica; a diferença está no modelo dos servos, na placa driver e na fiação. Confirme a versão escolhida antes de montar a mão.

## Estrutura mecânica

- 4 dedos, com 2 graus de liberdade cada: flexão/extensão (flexion/extension) + abdução/adução (abduction/adduction).
- Cada dedo é acionado por dois servos por meio de um mecanismo paralelo com acionamento diferencial; todos os servos ficam instalados na mão.
- Carcaça, ligações e juntas macias dos dedos impressas em 3D; a mão inteira pesa cerca de 400 g.
- A interface de punho original é compatível com o Orbita 3D do Reachy 2 e também pode ser adaptada a outros braços robóticos.

## CAD e modelos

- Arquivos STL / STEP: [`AmazingHand-main/cad/`](../../../AmazingHand-main/cad/)
- Documento online do Onshape e URDF: veja a seção CAD de [`AmazingHand-main/README_CN.md`](../../../AmazingHand-main/README_CN.md).

## Montagem e impressão 3D

- [Guia de montagem PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [Dicas de impressão 3D PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [Visão geral do AmazingHand PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)

> Antes de montar, posicione a mão no meio e instale os horns dos servos na posição do meio; os horns/estrias e o curso dos dois tipos de servo são diferentes e não podem ser misturados.

## Fiação dos dois conjuntos de hardware

| Versão | Guia de fiação e alimentação |
|------|----------------|
| Barramento serial SCS0009 | [Fiação, ID e alimentação SCS0009](scs0009.md) |
| PWM (ESP32-S3) | [Fiação, GPIO e alimentação PWM](pwm.md) |
| Kit de câmera | [Montagem do kit de câmera](camera-kit.md) |

## Próximos passos

- [Comparação de versões e escolha](../00-product/version-comparison.md)
- [Início rápido: SCS0009](../02-quick-start/scs0009.md) · [Início rápido: PWM](../02-quick-start/pwm.md)
