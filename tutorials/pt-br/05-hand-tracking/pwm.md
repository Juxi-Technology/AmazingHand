---
title: "Rastreamento de mãos PWM (MediaPipe embutido na GUI)"
description: "Rastreamento de mãos da versão com servos PWM do AmazingHand: MediaPipe embutido na GUI, instalação das dependências, execução, princípio e limitações, perguntas frequentes."
version: pwm
---

# Rastreamento de mãos PWM (MediaPipe embutido na GUI)

> Os comandos abaixo são executados no diretório `AmazingHand-PWM/` do repositório.

Esta página apresenta o rastreamento de mãos da **versão com servos PWM**: MediaPipe embutido na GUI, com a câmera reconhecendo os landmarks da mão e mapeando-os em tempo real para os 8 servos PWM. A cadeia completa dora + MuJoCo IK pertence à Demo oficial do SCS0009; veja [Rastreamento de mãos SCS0009](scs0009.md).

> Cadeia: câmera → esqueleto da mão no MediaPipe → ângulos de flexão/extensão dos quatro dedos → ESP32 → servos PWM
>
> Aplicável a: ESP32-S3 + 8 servos PWM. Gravação do firmware em [Início rápido com PWM](../02-quick-start/pwm.md); protocolo em [Protocolo e calibração PWM](../06-servo-tuning/pwm.md).

> A Demo oficial que exige IK completo (MuJoCo + dora + Rust) não é distribuída com este módulo; este tutorial cobre apenas o rastreamento embutido na GUI que acompanha o módulo.

## 1. Pré-requisitos

1. **Hardware**: ESP32-S3 + 8 servos PWM energizados, USB conectado e câmera disponível.
2. **Firmware**: já gravado (veja [Início rápido com PWM](../02-quick-start/pwm.md)).
3. **Python**: Python 3.12 de 64 bits (o mediapipe 0.10.14 só fornece wheel de 64 bits).

## 2. Instalar as dependências do rastreamento

No diretório raiz do módulo (`AmazingHand-PWM/`), execute:

```bash
tools/setup_tracking.bat
```

O script faz automaticamente: localiza o Python de 64 bits → cria o ambiente virtual `tools/tracking_env` → instala `tools/requirements-tracking.txt` (mediapipe 0.10.14, numpy<2, scipy, opencv, Pillow, pyserial) → verifica o mediapipe.

> Também é possível instalar manualmente (com Python 3.12 de 64 bits):
> ```bash
> python -m pip install -r tools/requirements-tracking.txt
> ```

## 3. Execução

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

1. No topo, selecione a porta COM do ESP32 → clique em «Conectar».
2. Role até o painel «Rastreamento de mãos (câmera MediaPipe)».
3. Escolha o número da câmera (padrão 0) → clique em «Iniciar rastreamento».
4. Coloque a mão no campo de visão; a mão dexterosa acompanha a flexão/extensão; clique em «Parar rastreamento» para terminar.

![Painel de rastreamento de mãos embutido na GUI: seleção de câmera, início do rastreamento e avisos de status](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-tracking.png)

## 4. Princípio e limitações

- O MediaPipe 0.10.14 extrai vetores 3D das pontas dos 4 dedos (no sistema de coordenadas da mão).
- A função `tips_to_angles()` de `hand_tracking.py` mapeia cada dedo em um ângulo diferencial:
  - flex (flexão/extensão): os três dedos usam a componente z; o polegar usa a componente y;
  - base (movimento lateral): fixo em 90 (o movimento lateral ainda não foi implementado).
- Estes são **eixos de controle**; no envio, o programa os combina nos ângulos dos dois servos de cada dedo (mesmo sentido = abdução, sentidos opostos = flexão/extensão).
- A GUI inclui suavização EMA (alpha=0.4) + throttling de 60 ms para reduzir o tremor.

Limitação: sem IK, a precisão é menor que a da cadeia completa MuJoCo + dora; adequado para demonstrações e início rápido.

### Calibração dos parâmetros

- `FLEX_SCALE` / `THUMB_FLEX_GAIN` no final de `hand_tracking.py` controlam a amplitude e a direção da flexão (os valores atuais seguem o arquivo).
- O movimento lateral ainda não foi implementado e `base` é fixo em 90; se precisar de movimento lateral, use a Demo oficial dora do SCS0009.
- As alterações passam a valer após reiniciar a GUI.

## 5. Alternar entre mão esquerda e direita

Marque «Mão direita» / «Mão esquerda» no topo da GUI. A direção espelhada do polegar muda conforme a mão; se estiver invertida, marque o outro lado e teste.

## 6. Perguntas frequentes

| Sintoma | Ação |
|------|------|
| Servos não se movem de jeito nenhum | Verifique a alimentação (5 V 3 A), a porta COM e a fiação; confirme que o firmware foi gravado |
| Sem imagem da câmera | Permita o acesso à câmera (Configurações → Privacidade → Câmera) |
| Mão não acompanha / resposta lenta | Boa iluminação, mão inteira no quadro, movimentos mais lentos e amplos |
| Mão invertida / direção do polegar invertida | Marque a mão oposta (esquerda/direita) |
| Trocou a porta USB e a serial não aparece | Selecione novamente a porta COM na GUI |
| Erro de mediapipe ausente na inicialização | Inicie com `tools\tracking_env\Scripts\python` ou rode novamente `tools/setup_tracking.bat` |

## 7. IK completo / servos de barramento SCS0009

- A cadeia completa de IK (câmera → MediaPipe → MuJoCo + mink IK → AHControl → ESP32) vem do projeto dora Demo independente e não faz parte deste módulo; se precisar, use o pacote de entrega original ou o projeto MediaPipe.
- Os servos de barramento SCS0009 são suportados por `Amazinghand-web/` e `AmazingHandControl/` no repositório.

## Descrição dos diretórios

| Caminho | Conteúdo |
|------|------|
| `tools/hand_gui.py` | aplicativo Tkinter (gestos, acionamento direto, diferencial, rastreamento embutido) |
| `tools/hand_tracking.py` | rastreamento de mãos com MediaPipe e mapeamento de ângulos |
| `tools/setup_tracking.bat` | cria `tools/tracking_env` e instala as dependências do rastreamento |
| `tools/requirements-tracking.txt` | lista de dependências do rastreamento |
| `tools/serial_test.py` | teste serial por linha de comando |
