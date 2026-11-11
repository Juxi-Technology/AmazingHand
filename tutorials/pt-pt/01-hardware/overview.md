---
title: "Visão geral do hardware: estrutura, CAD e montagem"
description: "Estrutura mecânica, CAD/STL/STEP, montagem e recursos de impressão 3D do AmazingHand."
version: both
---

# Visão geral do hardware

Os dois esquemas de servos partilham a mesma estrutura mecânica; as diferenças estão no modelo de servo, na placa controladora e na cablagem. Confirme a versão escolhida antes de montar a mão.

## Estrutura mecânica

- 4 dedos, cada um com 2 graus de liberdade: flexão/extensão + abertura (abduction/adduction).
- Cada dedo é acionado por dois servos através de um mecanismo paralelo de acionamento diferencial; todos os servos estão montados na mão.
- Carcaça, ligações e falanges flexíveis impressas em 3D; a mão completa pesa cerca de 400 g.
- A interface de punho original é compatível com o Orbita 3D do Reachy 2, podendo adaptar-se a outros braços robóticos.

## CAD e modelos

- Ficheiros STL / STEP: [`AmazingHand-main/cad/`](../../../AmazingHand-main/cad/)
- Documentação online do Onshape e URDF: consulte a secção CAD do [`AmazingHand-main/README_CN.md`](../../../AmazingHand-main/README_CN.md).

## Montagem e impressão 3D

- [Guia de montagem PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [Recomendações de impressão 3D PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [Visão geral do AmazingHand PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)

> Antes de montar, coloque a mão na posição central e monte os braços dos servos nessa posição; os braços/estriados e o curso dos dois tipos de servo são diferentes e não podem ser misturados.

## Cablagem dos dois conjuntos de hardware

| Versão | Guia de cablagem e alimentação |
|------|----------------|
| Barramento série SCS0009 | [Cablagem, ID e alimentação SCS0009](scs0009.md) |
| PWM (ESP32-S3) | [Cablagem, GPIO e alimentação PWM](pwm.md) |
| Kit de câmara | [Instalação do kit de câmara](camera-kit.md) |

## Próximos passos

- [Comparação de versões e seleção](../00-product/version-comparison.md)
- [Início rápido: SCS0009](../02-quick-start/scs0009.md) · [Início rápido: PWM](../02-quick-start/pwm.md)
