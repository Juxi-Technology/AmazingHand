---
title: "Perguntas frequentes (FAQ)"
description: "Reunião de perguntas frequentes gerais do AmazingHand, do SCS0009, do PWM, do controlo web, da aplicação de desktop e do seguimento de mãos."
version: both
---

# Perguntas frequentes (FAQ)

## Geral

**Devo escolher SCS0009 ou PWM?**
Se precisar de feedback de posição, precisão e recolha de dados LeRobot/SO-ARM101, escolha SCS0009; para demonstrações autónomas, interação por gestos e início rápido via web/desktop, escolha PWM. Ver [Comparação de versões](../00-product/version-comparison.md).

**É possível ligar os dois tipos de servos ao mesmo tempo?**
Não. Alimentação, protocolo e firmware são diferentes; ligue apenas um conjunto de cada vez.

**Posso alimentar a mão diretamente?**
Antes da primeira alimentação, coloque a mão na posição central e monte os braços dos servos nessa posição; a alimentação externa e a placa controladora/ESP32 têm de ter massa comum.

**Posso trocar o modelo de servo?**
A versão SCS0009 usa servos de barramento; o firmware da versão PWM está calibrado para o PTK 7452 MG-D (servo digital de 333 Hz). Servos analógicos de 50 Hz como o SG90 não podem substituir diretamente a versão PWM; é necessário alterar `LEDC_FREQ` e a calibração da largura de pulso.

## Versão de barramento série SCS0009

**O sentido do movimento está invertido** → verifique se a cablagem segue «primeiro o ID ímpar»; na mão esquerda, confirme `angle_offset_deg = -35.16`.

**Punho da mão esquerda com pouca amplitude / servo a zumbir** → verifique se o limite do `config.json` já está em ±120° (o predefinido ±90 corta o punho da mão esquerda).

**Dedo não se move / aviso «eram necessários N motores, foram detetados M»** → execute `tools/scan_servos.py`; os IDs da mão esquerda são os mais fáceis de ligar mal (11–18, não 9–16).

**Posição central errada** → o valor central `-17.578125` corresponde aos valores brutos oficiais 451/571; para calibrar com a sua montagem mecânica, edite `middle.positions` do `config.json`.

**Como definir o ID dos servos?** → utilize a [ferramenta de depuração SCS0009](../06-servo-tuning/scs0009.md) para procurar e alterar os IDs; mão direita 1–8, mão esquerda 11–18.

**O Linux não consegue abrir a porta série** → adicione o utilizador atual ao grupo `dialout` e reinicie a sessão.

**É possível ler posição/temperatura/tensão?** → Sim; o SCS0009 suporta leitura de posição, velocidade, tensão e temperatura; o mapa de memória do protocolo está em [`scs_servo_protocol.md`](../../../AmazingHandControl/docs/zh-hans/scs_servo_protocol.md).

## Versão de servos PWM

**Falha de ligação / ESP32 sem resposta** → confirme o baudrate 115200, a porta COM do ESP32, a alimentação de 5V/3A e a massa comum; abrir a porta série pode reiniciar, e a página volta a tentar o NOP automaticamente.

**Servos não se movem ou tremem** → confirme que são servos digitais de 333 Hz (PTK 7452 MG-D ou equivalentes) e que a alimentação é suficiente; o SG90 exige alteração do firmware.

**Sentido invertido** → na secção `pwm.calibration` do `config.json` da página web, altere o `scale` do dedo correspondente para `-1`.

**Centro errado** → ajuste o `offset_deg` do canal correspondente; ver [Protocolo, comandos e calibração PWM](../06-servo-tuning/pwm.md).

**Aparece «ocupado (gesto em execução)»** → o firmware está a executar um gesto incorporado; aguarde que termine ou envie parar (`0xFF`).

**A versão PWM tem feedback?** → Não tem leitura de posição/temperatura/tensão; não é possível detetar bloqueio ou perda de passos.

**Os servos PWM têm baudrate?** → O servo em si não; a porta série entre PC e ESP32 está fixa em 115200 8N1.

**Posso testar com apenas alguns servos ligados?** → Sim. Os canais livres não afetam os restantes; tenha atenção ao isolamento das fichas livres.

**A câmara tem imagem mas a mão não acompanha / reação lenta** → luz uniforme, palma a cerca de 40–80 cm da câmara e virada para ela; feche outros programas que usem a câmara; confirme que a porta série está ligada. Para parâmetros de seguimento da GUI, ver [Seguimento de mãos PWM](../05-hand-tracking/pwm.md).

**Alternar a mão esquerda/direita não tem efeito** → o firmware usa `0xF1` para alternar mão esquerda/direita (a página web envia automaticamente ao ligar); esta definição afeta sobretudo o sentido do polegar nos gestos incorporados do firmware, enquanto as poses da página web usam o mapeamento da mão do alvo de controlo atual.

**A imagem de seguimento bloqueia / o registo para** → pare o seguimento e volte a iniciar; se continuar sem resposta, feche e reabra a GUI e confirme que a câmara não está a ser usada por outro programa.

**Depois de mudar de porta USB não encontra a porta série** → confirme o novo número COM no Gestor de Dispositivos e, na GUI ou na página web, clique em «Atualizar» e volte a selecionar.

## Controlo web

**Falha do modelo / falha de carregamento do seguimento por câmara** → confirme que a página é servida por um serviço local (não aberta diretamente como `file://`) e que o caminho dos recursos MediaPipe está acessível; o tutorial local já corrigiu o encaminhamento MediaPipe do servidor. Se continuar a falhar, veja erros 404 ou de permissões na Consola/Rede do navegador.

**Reconhecimento da câmara impreciso** → luz uniforme e palma virada para a câmara; em `tracking.js`, quanto maior o `SMOOTH` (predefinição 0.35), mais suave mas mais lento.

**Um dedo não acompanha** → volte a capturar as três poses; se o sentido estiver invertido, recapture a pose correspondente; o polegar só faz flexão e não participa na abertura.

**A meio do punho um servo inverte** → a abertura deve atenuar até 0 com a flexão (`side *= (1 - curl)`); verifique se o sinal e a magnitude da abertura estão anormais.

**Como alternar o driver na página web?** → Na lista pendente «Driver» do topo, escolha SCS0009 ou PWM; o PWM requer uma porta série a 115200; ver [Visão geral do controlo web](../03-web-control/README.md).

## Aplicação de desktop

**A GUI SCS0009 não lista portas série** → volte a ligar/desligar o adaptador USB, instale o driver ou reinicie a GUI; no Linux, verifique `dialout`.

**O botão Connect está a cinzento** → já está ligado; clique primeiro em Disconnect.

**A sequência não aciona todos os dedos** → verifique a velocidade de cada passo e garanta que cada pose contém valores para os 8 servos.

**O indicador de bloqueio permanece** → verifique bloqueios mecânicos; um bloqueio é acionado quando a diferença entre o alvo e a posição real é grande e não há movimento.

**A GUI PWM arranca com erro de mediapipe em falta** → inicie com o Python de `tools/tracking_env` ou volte a executar `tools/setup_tracking.bat`.

## Seguimento de mãos

**O mediapipe não tem o submódulo solutions** → instale `mediapipe==0.10.14` e confirme que o Python 3.12 é de 64 bits.

**Versão do dora incompatível** → alinhe a versão do dora segundo o `pyproject.toml` e os registos; limpe e reinstale.

**Falha de carregamento de modelos (caminhos com caracteres chineses)** → coloque o projeto/modelos num caminho totalmente em inglês.

**Sem imagem da câmara / permissões** → permita as permissões de câmara do sistema; a máquina virtual precisa de passagem USB da câmara.

**Qual é a diferença entre a Demo oficial SCS0009 e o seguimento da GUI PWM?** → O SCS0009 usa a cadeia completa dora + IK em MuJoCo; a versão PWM disponibiliza seguimento leve com MediaPipe integrado na GUI, e a Demo dora não está no módulo. Ver [Seguimento de mãos SCS0009](../05-hand-tracking/scs0009.md) / [Seguimento de mãos PWM](../05-hand-tracking/pwm.md).

## Mais

- [Comparação de versões e seleção](../00-product/version-comparison.md)
- [Visão geral do hardware](../01-hardware/overview.md)
- [Downloads e recursos](../00-product/downloads.md)
