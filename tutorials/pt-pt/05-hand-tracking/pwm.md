---
title: "Seguimento de mãos PWM (MediaPipe integrado na GUI)"
description: "Seguimento de mãos da versão de servos PWM do AmazingHand: MediaPipe integrado na GUI, instalação de dependências, execução, princípio e limitações, perguntas frequentes."
version: pwm
---

# Seguimento de mãos PWM (MediaPipe integrado na GUI)

> Os comandos seguintes são executados no diretório `AmazingHand-PWM/` do repositório.

Esta página descreve o seguimento de mãos da **versão de servos PWM**: o MediaPipe está integrado na GUI, a câmara reconhece os pontos-chave da mão e mapeia-os em tempo real nos 8 servos PWM. A cadeia completa dora + IK em MuJoCo pertence à Demo oficial do SCS0009, ver [Seguimento de mãos SCS0009](scs0009.md).

> Cadeia: câmara → esqueleto da mão no MediaPipe → ângulos de flexão/extensão dos quatro dedos → ESP32 → servos PWM
>
> Aplicável a: ESP32-S3 + 8 servos PWM. Para gravação de firmware, consulte [Início rápido PWM](../02-quick-start/pwm.md); para o protocolo, [Protocolo e calibração PWM](../06-servo-tuning/pwm.md).

> A Demo oficial que requer IK completo (MuJoCo + dora + Rust) não é distribuída com este módulo; este tutorial descreve apenas o seguimento integrado na GUI que acompanha o módulo.

## 1. Pré-requisitos

1. **Hardware**: ESP32-S3 + 8 servos PWM alimentados, USB ligado, câmara funcional.
2. **Firmware**: já gravado (ver [Início rápido PWM](../02-quick-start/pwm.md)).
3. **Python**: Python 3.12 de 64 bits (o mediapipe 0.10.14 só disponibiliza wheels de 64 bits).

## 2. Instalar as dependências de seguimento

No diretório raiz do módulo (`AmazingHand-PWM/`):

```bash
tools/setup_tracking.bat
```

O script faz automaticamente: procura Python de 64 bits → cria o ambiente virtual `tools/tracking_env` → instala `tools/requirements-tracking.txt` (mediapipe 0.10.14, numpy<2, scipy, opencv, Pillow, pyserial) → valida o mediapipe.

> Também pode instalar manualmente (com Python 3.12 de 64 bits):
> ```bash
> python -m pip install -r tools/requirements-tracking.txt
> ```

## 3. Executar

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

1. No topo, escolha a porta COM do ESP32 → clique em «Ligar».
2. Desça até ao painel «Seguimento de mãos (câmara MediaPipe)».
3. Escolha o número da câmara (predefinição 0) → clique em «Iniciar seguimento».
4. Coloque a mão na imagem; a mão robótica acompanha a flexão/extensão; clique em «Parar seguimento» para terminar.

![Painel de seguimento de mãos integrado na GUI: seleção de câmara, início do seguimento e mensagens de estado](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-tracking.png)

## 4. Princípio e limitações

- O MediaPipe 0.10.14 extrai vetores 3D das pontas dos 4 dedos (no referencial da mão).
- A função `tips_to_angles()` de `hand_tracking.py` mapeia cada dedo num ângulo diferencial:
  - flex (flexão/extensão): os três dedos usam a componente z; o polegar usa a componente y;
  - base (balanço lateral): fixo em 90 (o balanço lateral ainda não está implementado).
- Estes são **eixos de controlo**; ao enviar, o programa combina-os nos ângulos dos dois servos de cada dedo (mesmo sentido = abertura; sentidos opostos = flexão).
- A GUI inclui suavização EMA (alpha=0.4) + limitação a 60 ms para reduzir tremores.

Limitação: sem IK, a precisão é inferior à cadeia completa MuJoCo + dora; adequado a demonstrações e início rápido.

### Calibração de parâmetros

- `FLEX_SCALE` / `THUMB_FLEX_GAIN` no final de `hand_tracking.py` controlam a amplitude e o sentido da flexão (os valores atuais do código são a referência).
- O balanço lateral ainda não está implementado; `base` está fixo em 90; para balanço lateral, utilize a Demo oficial dora do SCS0009.
- As alterações só produzem efeito após reiniciar a GUI.

## 5. Alternar mão esquerda/direita

No topo da GUI, marque «Mão direita»/«Mão esquerda». Após a alternância, o sentido do espelhamento do polegar é diferente; se estiver invertido, experimente marcar o outro lado.

## 6. Perguntas frequentes

| Sintoma | Resolução |
|------|------|
| Servos totalmente imóveis | Verifique a alimentação (5V 3A), a porta COM e a cablagem; confirme que o firmware foi gravado |
| Sem imagem da câmara | Permita o acesso à câmara (Definições→Privacidade→Câmara) |
| A mão não acompanha / lenta | Luz suficiente, mão completamente no enquadramento, movimentos mais lentos e amplos |
| Formato da mão invertido / sentido do polegar invertido | Marque a mão esquerda/direita inversa |
| Mudou de porta USB e não encontra a porta série | Volte a escolher a porta COM na GUI |
| Erro de mediapipe em falta no arranque | Inicie com `tools\tracking_env\Scripts\python` ou execute novamente `tools/setup_tracking.bat` |

## 7. IK completo / servos de barramento SCS0009

- A cadeia completa de IK (câmara → MediaPipe → MuJoCo + mink IK → AHControl → ESP32) pertence a um projeto Demo dora independente, fora deste módulo; quando necessário, utilize o pacote de entrega original ou o projeto MediaPipe.
- Os servos de barramento SCS0009 são suportados pelo `Amazinghand-web/` e pelo `AmazingHandControl/` do repositório.

## Descrição dos diretórios

| Caminho | Conteúdo |
|------|------|
| `tools/hand_gui.py` | Aplicação de PC em Tkinter (gestos, acionamento direto, diferencial, seguimento integrado) |
| `tools/hand_tracking.py` | Seguimento de mãos com MediaPipe e mapeamento de ângulos |
| `tools/setup_tracking.bat` | Cria `tools/tracking_env` e instala as dependências de seguimento |
| `tools/requirements-tracking.txt` | Lista de dependências de seguimento |
| `tools/serial_test.py` | Teste de porta série por linha de comandos |
