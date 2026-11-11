---
title: "Controle web PWM"
description: "Controle web da versão com servos PWM do AmazingHand: conexão do ESP32-S3, troca de driver, diferenças em relação ao SCS0009, calibração de ângulos e perguntas frequentes."
version: pwm
---

# Controle web PWM

Esta página é a descrição específica do **controle web na versão PWM (ESP32-S3)**. Para a interface geral, formas de iniciar, poses predefinidas e teleoperação por câmera, veja [Visão geral do controle web](README.md).

## Hardware e gravação

- Fiação, GPIO, alimentação e modelo de servo: [Fiação, GPIO e alimentação PWM](../01-hardware/pwm.md).
- Gravação do firmware (ESP-IDF ou bin pré-compilado): [Início rápido com PWM](../02-quick-start/pwm.md).
- Serial PC↔ESP32 fixa em **115200 8N1**; o servo em si não tem baudrate.

## Conexão pela página web

1. No menu suspenso **Driver** no topo, selecione **PWM (ESP32-S3)**
2. Clique em **Adicionar porta…** e selecione a porta USB do ESP32-S3
3. Clique em **Conectar**: a página faz o handshake automaticamente (NOP), envia a escolha de mão e retorna ao meio
4. Depois controle com os controles deslizantes, as poses predefinidas e a teleoperação por câmera; o título dos dedos mostra **CH 1/2 …** (número do canal PWM)

![Modo PWM: seleção de driver no topo e exibição dos canais CH](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-port-bar.png)

![Painel de controle manual no modo PWM: o título dos dedos mostra os canais CH e o botão de torque fica oculto](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-pwm-manual.png)

## Diferenças em relação à versão SCS0009

| Item | Versão de barramento SCS0009 | Versão PWM |
|------|----------------|--------|
| Baudrate da serial | 1.000.000 | **115.200** |
| Placa driver | Placa driver de barramento USB | ESP32-S3 + placa adaptadora PWM |
| Torque | Pode ativar/liberar | **Nenhum** (o firmware não tem comando de torque e o botão fica oculto) |
| Parada de emergência | Libera todo o torque | Envia `0xFF` para abortar o gesto; os servos continuam energizados e mantêm a posição |
| Velocidade | Suporta parâmetro de velocidade | Os quadros de acionamento direto não têm parâmetro de velocidade |
| Feedback | Leitura de posição/temperatura/tensão/velocidade | **Sem leitura**; não detecta travamento nem perda de passos |
| Mão esquerda/direita | IDs de servo diferentes | O mesmo conjunto de canais; envie `0xF1` para alternar (afeta principalmente os gestos do firmware; as poses da página usam o mapeamento de cada mão) |

## Calibração dos ângulos

A página converte os valores de pose em 8 ângulos de 0–180°, com a fórmula padrão:

```
angle = 90 + dir × scale × valor da pose + offset
```

- Para cada dedo, o primeiro canal tem `dir = -1` e o segundo `dir = +1`
- Por padrão `scale = 1` e `offset = 0`, ou seja, espelha diretamente o ângulo do eixo do servo
- Quando `mirror_pose` é verdadeiro, primeiro troque os dois valores de pose de cada dedo (neste repositório está ativado para as duas mãos)

Se na máquina real a direção ficar invertida ou o meio deslocado, edite `pwm.calibration` no [`config.json`](../../../Amazinghand-web-io/config.json):

```jsonc
"pwm": {
  "calibration": {
    "right": {
      "pointer": { "scale": 1.0, "offset_deg": [0, 0] }
    }
  }
}
```

- Direção invertida: mude o `scale` do dedo correspondente para `-1`
- Deslocamento do meio: ajuste `offset_deg` (separadamente para os dois canais)
- Passo a passo por dedo: volte ao meio → arraste um único dedo → observe direção/meio → altere `scale`/`offset_deg` → recarregue a página e tente de novo

## Perguntas frequentes

- **Falha na conexão / ESP32 não responde**: confirme que o baudrate é 115200, que a porta COM selecionada é a do ESP32, que a alimentação é 5 V/3 A e que há aterramento comum; ao abrir a porta, o ESP32 pode reiniciar e a página tenta o NOP automaticamente
- **Os servos não se movem ou tremem**: confirme primeiro que os servos são digitais de 333 Hz (PTK 7452 MG-D ou equivalente) e que a fonte é suficiente; o SG90 exige alteração no firmware
- **Direção invertida**: mude o `scale` do dedo correspondente para `-1`
- **Meio errado**: ajuste o `offset_deg` do canal correspondente
- **Mensagem "ocupado (executando gesto)"**: o firmware está executando um gesto interno; espere terminar ou clique na parada de emergência (`0xFF`)
- **Varredura de servos**: `tools/scan_servos.py` só se aplica ao SCS0009; para PWM, use `AmazingHand-PWM/tools/serial_test.py` ou a página web

---

## Páginas relacionadas

- [Protocolo e calibração PWM](../06-servo-tuning/pwm.md)
- [Aplicativo de desktop PWM](../04-desktop/pwm.md)
- [Início rápido com PWM](../02-quick-start/pwm.md)
