---
title: "Perguntas frequentes (FAQ)"
description: "Resumo das perguntas frequentes gerais do AmazingHand e das versões SCS0009, PWM, controle web, aplicativo de desktop e rastreamento de mãos."
version: both
---

# Perguntas frequentes (FAQ)

## Geral

**Devo escolher SCS0009 ou PWM?**
Escolha SCS0009 se precisar de feedback de posição, precisão ou coleta de dados LeRobot/SO-ARM101; escolha PWM para demonstrações independentes, interação por gestos e início rápido no navegador/desktop. Detalhes em [Comparação de versões](../00-product/version-comparison.md).

**É possível conectar os dois tipos de servo ao mesmo tempo?**
Não. Alimentação, protocolo e firmware são diferentes; conecte apenas um conjunto por vez.

**Posso energizar a mão diretamente?**
Antes da primeira energização, posicione a mão no meio e instale os horns dos servos na posição do meio; a fonte externa e a placa driver/ESP32 devem ter aterramento comum.

**É possível trocar o modelo dos servos?**
A versão SCS0009 usa servos de barramento; o firmware da versão PWM é calibrado para o PTK 7452 MG-D (servo digital de 333 Hz). Servos analógicos de 50 Hz como o SG90 não podem substituir diretamente a versão PWM; é preciso alterar `LEDC_FREQ` e a calibração da largura de pulso.

## Versão de barramento serial SCS0009

**O movimento está invertido** → verifique se a fiação segue "ID ímpar primeiro"; na mão esquerda, confirme `angle_offset_deg = -35.16`.

**O punho da mão esquerda fica pequeno demais / os servos zumbem** → verifique se o limite no `config.json` foi ampliado para ±120° (o padrão de ±90 corta o punho fechado da mão esquerda).

**Um dedo não se move / mensagem "expected N motors, found M"** → rode `tools/scan_servos.py`; os IDs da mão esquerda são os mais fáceis de ligar errado (11–18, não 9–16).

**A posição do meio está errada** → o valor do meio `-17.578125` corresponde ao bruto oficial 451/571; para calibrar com a sua montagem, edite `middle.positions` no `config.json`.

**Como definir o ID do servo?** → use a [ferramenta de depuração SCS0009](../06-servo-tuning/scs0009.md) para escanear e alterar os IDs; mão direita 1–8, mão esquerda 11–18.

**No Linux, não é possível abrir a porta serial** → adicione o usuário atual ao grupo `dialout` e faça login novamente.

**É possível ler posição/temperatura/tensão?** → Sim; o SCS0009 permite ler posição, velocidade, tensão e temperatura; a tabela de memória do protocolo está em [`scs_servo_protocol.md`](../../../AmazingHandControl/docs/zh-hans/scs_servo_protocol.md).

## Versão com servos PWM

**Falha na conexão / ESP32 não responde** → confirme o baudrate 115200, a porta COM do ESP32, a alimentação de 5 V/3 A e o aterramento comum; abrir a serial pode reiniciar o ESP32 e a página repete o NOP automaticamente.

**Os servos não se movem ou tremem** → confirme que são servos digitais de 333 Hz (PTK 7452 MG-D ou equivalente) e que a fonte é suficiente; o SG90 exige alteração no firmware.

**Direção invertida** → no `config.json` da página web, em `pwm.calibration`, mude o `scale` do dedo correspondente para `-1`.

**Meio errado** → ajuste o `offset_deg` do canal correspondente; detalhes em [Protocolo, comandos e calibração dos servos PWM](../06-servo-tuning/pwm.md).

**Mensagem "ocupado (executando gesto)"** → o firmware está executando um gesto interno; aguarde terminar ou envie a parada (`0xFF`).

**A versão PWM tem feedback?** → Não há leitura de posição/temperatura/tensão, nem detecção de travamento ou perda de passos.

**Os servos PWM têm baudrate?** → O servo em si não tem; a serial PC↔ESP32 é fixa em 115200 8N1.

**É possível testar conectando apenas alguns servos?** → Sim. Os canais não conectados podem ficar vazios sem afetar os demais; isole os conectores vazios.

**A câmera tem imagem, mas a mão não acompanha / a resposta é lenta** → iluminação uniforme, palma a cerca de 40–80 cm da câmera e virada para ela; feche outros programas que usam a câmera; confirme que a serial está conectada. Para os parâmetros da GUI, veja [Rastreamento de mãos PWM](../05-hand-tracking/pwm.md).

**Alternar a mão esquerda/direita não tem efeito** → o firmware usa `0xF1` para alternar (a página web envia automaticamente ao conectar); essa configuração afeta principalmente a direção do polegar nos gestos internos do firmware, enquanto as poses da página usam o mapeamento de cada mão conforme o Target atual.

**A imagem do rastreamento trava / o log para** → pare o rastreamento e inicie de novo; se continuar sem resposta, feche e reabra a GUI e confirme que a câmera não está sendo usada por outro programa.

**Depois de trocar a porta USB, a serial não aparece** → confirme o novo número de COM no Gerenciador de Dispositivos e clique em "Atualizar" na GUI ou na página web para selecionar de novo.

## Controle web

**Falha no modelo / falha ao carregar o rastreamento por câmera** → confirme que a página é servida por um serviço local (não aberta diretamente via `file://`) e que o caminho dos recursos do MediaPipe está acessível; o tutorial local já corrige a rota do MediaPipe no servidor. Se ainda falhar, veja no Console/Network do navegador os erros 404 ou de permissão.

**O reconhecimento da câmera está impreciso** → iluminação uniforme e palma virada para a câmera; em `tracking.js`, quanto maior o `SMOOTH` (padrão 0.35), mais suave, mas com mais atraso.

**Um dedo não acompanha** → recapture as três poses; se a direção estiver invertida, recapture a pose correspondente; o polegar só flexiona e não participa da abdução.

**Um servo inverte no meio do fechamento do punho** → a abdução deve decair a 0 conforme o dedo fecha (`side *= (1 - curl)`); verifique se o sinal e o valor de controle da abdução estão anormais.

**Como alternar o driver na página web?** → selecione SCS0009 ou PWM no menu suspenso "Driver" no topo; para PWM, escolha a serial a 115200. Detalhes em [Visão geral do controle web](../03-web-control/README.md).

## Aplicativo de desktop

**A GUI SCS0009 não lista a porta serial** → reconecte o adaptador USB, instale os drivers ou reinicie a GUI; no Linux, verifique `dialout`.

**Botão Connect esmaecido** → já está conectado; clique primeiro em Disconnect.

**A sequência não move todos os dedos** → verifique a velocidade de cada etapa e garanta que cada pose contenha os 8 valores de servo.

**O indicador de bloqueio persiste** → verifique obstruções mecânicas; o bloqueio é acionado quando meta e posição real diferem muito e não há movimento.

**A GUI PWM reporta mediapipe ausente na inicialização** → inicie com o Python de `tools/tracking_env` ou rode novamente `tools/setup_tracking.bat`.

## Rastreamento de mãos

**mediapipe sem o submódulo solutions** → instale `mediapipe==0.10.14` e confirme que o Python 3.12 é de 64 bits.

**Versão do dora incompatível** → alinhe a versão do dora conforme o `pyproject.toml` e os logs; limpe e reinstale.

**Falha ao carregar modelos (caminhos em chinês)** → coloque o projeto/modelo em um caminho totalmente em inglês.

**Sem imagem da câmera / permissões** → permita o acesso à câmera no sistema; em máquina virtual, é preciso fazer passthrough USB da câmera.

**Qual a diferença entre a Demo oficial do SCS0009 e o rastreamento da GUI PWM?** → O SCS0009 usa a cadeia completa dora + MuJoCo IK; a versão PWM oferece rastreamento leve com MediaPipe embutido na GUI, e a Demo dora não está incluída no módulo. Detalhes em [Rastreamento de mãos SCS0009](../05-hand-tracking/scs0009.md) / [Rastreamento de mãos PWM](../05-hand-tracking/pwm.md).

## Mais

- [Comparação de versões e escolha](../00-product/version-comparison.md)
- [Visão geral do hardware](../01-hardware/overview.md)
- [Downloads e recursos](../00-product/downloads.md)
