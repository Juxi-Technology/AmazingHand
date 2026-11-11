---
title: "Controlo web do AmazingHand"
description: "Visão geral do controlo web do AmazingHand: modo de arranque, comutação de driver, barra de porta série, controlo manual, teleoperação por câmara e conceção de segurança."
version: both
---

# Controlo web do AmazingHand

Controle a mão robótica de destreza AmazingHand a partir do navegador, **em modo mão esquerda ou mão direita**, com duas formas de operação:

- **Controlo manual** —— 8 sliders de servo + 19 poses predefinidas + regresso ao centro com um clique
- **Teleoperação interativa por câmara** —— o MediaPipe reconhece os movimentos da mão localmente no navegador e mapeia-os em tempo real nos dedos (a imagem nunca sai do computador)
- **Alternância chinês/inglês** —— no canto superior direito; a escolha fica memorizada no navegador e mantém-se na próxima abertura

> Esta página é a **descrição geral do controlo web**. Para o mapeamento/conversão específicos do SCS0009, consulte [Controlo web SCS0009](scs0009.md); para cablagem/gravação/calibração específicas do PWM, consulte [Controlo web PWM](pwm.md).

## Início rápido

Abra um terminal e entre no diretório Amazinghand-web:

```bash
pip install -r requirements.txt

python server.py --no-connect   # recomendado: inicia o serviço primeiro e escolhe a porta na página (não toca nos servos)

# python server.py                # deteta e liga automaticamente a porta série
# python server.py --port COM9    # especifica a porta série
# python server.py --hand left    # ativa apenas a mão esquerda
# python server.py --driver pwm   # usa a versão de servos PWM do ESP32-S3
# python server.py --dry-run      # não abre qualquer porta série, apenas valida a interface
```

Abra **http://localhost:8000** no navegador.

Também pode usar diretamente o frontend estático (Web Serial, sem necessidade de servidor Python):

- Online: <https://juxi-technology.github.io/AmazingHand/Amazinghand-web-io/> (Chrome / Edge)
- Local: no diretório raiz do repositório, execute `python -m http.server 8099` e abra <http://localhost:8099/Amazinghand-web-io/>

### Escolher a porta série na página

No topo da página há uma barra de ferramentas; escolha primeiro o driver e depois a porta série:

```
Driver  [SCS0009 bus ▾]  Porta  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [Atualizar]  [Ligar]  [Desligar]  Ligado a COM3
```

- Lista pendente do driver: **SCS0009 bus** (servos de barramento oficiais, predefinido) ou **PWM (ESP32-S3)** (ver [Controlo web PWM](pwm.md))
- A lista pendente mostra todas as portas série da máquina; os chips USB-série mais comuns (CH34x / CP210x / FTDI, etc.) estão marcados com **★** e aparecem primeiro
- Clique em **Atualizar** para voltar a procurar (após ligar/desligar a placa)
- Clique em **Ligar** para abrir a porta selecionada; após a ligação, a mão regressa automaticamente ao centro
- Clique em **Desligar** para libertar primeiro o binário e depois fechar, para que os servos não fiquem rígidos na posição atual (a versão PWM não tem comando de binário; ver a nota abaixo)
- Para trocar de porta, basta escolher a nova e clicar em «Ligar»; a porta antiga é fechada automaticamente

> **O alojamento estático (GitHub Pages) não tem servidor Python**: por questões de privacidade, o navegador não pode enumerar as portas série silenciosamente e só vê os dispositivos que autorizou. Nesse caso, clique em **Adicionar porta…** e escolha a placa controladora na caixa de diálogo do navegador; o comportamento de "listar todas as portas série da máquina" descrito acima aplica-se apenas ao modo com servidor `server.py`.

![Topo da página: seleção de driver, barra de porta série e alternância de mão esquerda/direita](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-port-bar.png)

> **O `--no-connect` foi pensado para este fluxo**: no arranque apenas inicia o serviço e não toca na porta série,
> por isso a mão não se mexe por ligar à porta errada. Se quiser que ligue automaticamente no arranque, remova este parâmetro.

Os registos da porta série são escritos em `server.log` (ao iniciar com duplo clique no .bat, a janela fecha imediatamente — consulte este ficheiro).

### Verificação da cablagem

Lista os IDs de servo encontrados e verifica-os mão a mão contra o `config.json`.

```bash
python tools/scan_servos.py --port COM9
```

Substitua COM9 pela sua porta real.

> Esta ferramenta só se aplica a **servos de barramento SCS0009**. Para a verificação de cablagem da versão PWM, consulte [Controlo web PWM](pwm.md), ou utilize `AmazingHand-PWM/tools/serial_test.py`.

---

## Poses predefinidas (19)

![Painel de controlo manual: sliders dos quatro dedos, 19 poses predefinidas e botões de operação](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-manual.png)

| Pose | Descrição | Pose | Descrição |
|---|---|---|---|
| `open` | Abrir | `wave1` | Acenar |
| `close` / `stone` | Punho | `wave_r` / `wave_l` | Balançar à direita/esquerda |
| `ok` | OK | `ring_close` | Fechar só o anelar |
| `greeting` | Cumprimento | `middle_close` | Fechar só o médio |
| `victory` / `two` / `scissors` | V de vitória / Dois | `pointer_close` | Fechar só o indicador |
| `paper` | Papel | `thumb_close` | Fechar só o polegar |
| `one` / `three` | Um / Três | `hifive` | High five |

Para modificar as poses, edite a secção `poses` do `config.json`; os nomes das chaves correspondem aos nomes no YAML oficial.

### As mãos esquerda e direita podem ter valores de pose diferentes

Dentro de cada pose, `positions` é **partilhado pelas duas mãos**. Se uma mão precisar de outro conjunto de valores devido a diferenças de montagem mecânica, basta acrescentar uma chave `right` ou `left` na mesma entrada, que substitui `positions`:

```jsonc
"close": {
  "label": "Punho",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // partilhado pelas duas mãos
  "right":     [ ... 8 valores ... ]                // opcional: apenas para a mão direita
}
```

---

## Dois modos

| Modo | Comportamento |
|---|---|
| **Mão direita** | Envia apenas para os 8 servos da mão direita |
| **Mão esquerda** | Envia apenas para os 8 servos da mão esquerda (o SCS0009 aplica automaticamente o espelhamento e o desvio de −35.16°; o PWM usa o mapeamento de canais da mão esquerda)|

Controla-se uma mão de cada vez, alternando com o **Target** no topo; a alternância não afeta a outra mão, que mantém a pose atual no lugar. No SCS0009, as duas mãos podem ligar-se ao mesmo barramento; no PWM, cada mão é controlada por um ESP32-S3 próprio.

---

## Teleoperação interativa por câmara

O navegador executa localmente os pontos-chave da mão do MediaPipe (os recursos estão em `Amazinghand-web/web/mediapipe/` e funcionam offline; a página também tenta primeiro `Amazinghand-web-io/mediapipe/`),
converte os 21 pontos-chave em valores de pose para os 4 dedos e envia-os em tempo real para a mão selecionada.

![Painel da câmara: início, visualização do esqueleto, captura de três poses e área de estado](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-camera.png)

### 1. Capturar primeiro três poses

Depois de iniciar a câmara, coloque a mão numa pose e clique no botão correspondente para capturar uma vez (cerca de 1 segundo com média).
A ordem é indiferente; se capturar mal, clique no mesmo botão para recapturar. **O estado só fica verde quando as três estiverem capturadas**;
antes disso nada é enviado e a mão permanece na pose central.

| Botão | Pose | O que fornece |
|---|---|---|
| ① Esticar e abrir | Dedos esticados e afastados, polegar para fora | Extremo «esticado» da flexão + extremo «aberto» da abertura |
| ② Esticar e juntar | Dedos esticados e juntos, polegar encostado ao indicador | Extremo «junto» da abertura |
| ③ Punho | Punho fechado, polegar junto à palma | Extremo «fechado» da flexão |

### 2. Dois pontos medidos por eixo

Tanto a flexão como a abertura usam **dois pontos extremos medidos para definir uma reta**:

```
t    = (medido − extremoA) / (extremoB − extremoA)        // limitado a 0~1
alvo = A.alvo + (B.alvo − A.alvo) × t
```

A vantagem é que **o sinal da medição de cada dedo é absorvido automaticamente** — por isso não é necessário qualquer interruptor do tipo «inverter determinado dedo»
(indicador e anelar estão em lados opostos da linha central, e a cadeia articular do polegar é diferente, pelo que os sentidos são naturalmente opostos, mas dois extremos medidos ajustam-nos automaticamente).

Os valores alvo dos extremos estão na secção `camera` do `config.json`:

| Eixo | Extremos | Anelar | Médio | Indicador |
|---|---|---|---|---|
| Flexão | esticado → punho | −50 → 90 | −50 → 90 | −50 → 90 |
| Abertura | juntos → afastados | −45 → +45 | 0 → 0 | +45 → −45 |

Ambos os extremos da abertura do dedo médio são 0 (não oscila lateralmente).

### 3. O polegar só faz flexão ⚠️

A CMC do polegar é uma **articulação de oposição** e o acoplamento entre flexão e abertura lateral é muito forte — com o polegar encostado ao indicador já está numa posição de abertura, pelo que a "origem da flexão" medida nesse momento está contaminada. Forçá-la em dois eixos faz com que ambos fiquem imprecisos.

Por isso o polegar **só faz flexão, com abertura sempre 0** (o diferencial de abertura dos dois servos é 0). As duas poses de referência de que necessita são a ① (dedo para fora) e a ③ (dedo para a palma), sem necessidade de capturas adicionais.

### 4. A abertura atenua-se com a flexão

A abertura final é ajustada pela fórmula:

```
side = side_measured × (1 − curl)
```

`splayDeg` é a projeção da direção MCP→PIP sobre o eixo transversal da palma, e a flexão do dedo **roda precisamente em torno desse eixo** — a partir de um certo grau de flexão, a projeção inverte-se e a "abertura" salta de repente para o outro extremo.

Sem atenuação, esse salto propaga-se por `servo2 = flexão − abertura` e arrasta o **servo de ID par** no sentido inverso
(o ID ímpar recebe `flexão + abertura`, com variação no sentido oposto, pelo que é menos evidente).
O sintoma é «a meio do punho, os servos 12 e 16 invertem bruscamente» — o 12 é o segundo servo do anelar esquerdo e o 16 o segundo servo do indicador esquerdo, exatamente os dois arrastados pelo diferencial quando a componente de abertura não é nula.

Com a atenuação, no fecho total a abertura é **sempre 0**, independentemente de quão absurda seja a medição. E um punho fechado deve, por natureza, ter os dedos juntos.

### 5. Cores do esqueleto

| Dedo | Cor |
|---|---|
| Polegar | Laranja |
| Indicador | Vermelho |
| Médio | Azul |
| Anelar | Amarelo |
| Mindinho | Cinzento-escuro |
| Ossos da palma | Cinzento-neutro |

O mindinho não participa no mapeamento de gestos, mas a sua **MCP de base (ponto 17) serve para definir o referencial da palma da mão direita**, pelo que não pode ser removido.

### Guia rápido de afinação

| O que alterar | Onde alterar |
|---|---|
| Valores alvo dos eixos | Secção `camera` do `config.json` |
| **Sentidos de abertura opostos entre mão esquerda e direita** | Altere essa mão em `camera.side_sign` para `-1` (`1` = manter) |
| Nível de suavização | `SMOOTH` em `tracking.js` (por omissão 0.35; menor = mais estável mas mais lento) |
| Rapidez de deteção da flexão dos dedos | Volte a capturar as três poses |

`side_sign` aplica-se à mão escolhida no **Target**; após a alteração, basta atualizar a página, sem reiniciar o serviço:

```jsonc
"side_sign": { "right": 1, "left": -1 }   // a mão esquerda inverte todo o eixo de abertura
```

A flexão não é afetada por `side_sign`.

---

## Estrutura do projeto

```
Amazinghand-web-io/          Frontend (estático, pode ser alojado separadamente)
├── index.html
├── app.js                   Interface, comutação de driver, poses e UI da câmara
├── io.js                    Backend SCS0009 Web Serial
├── pwm.js                   Backend PWM Web Serial
├── common.js                Configuração partilhada, conversão de poses e limites
├── ws.js                    Backend WebSocket (modo com servidor Python)
├── tracking.js              Seguimento por câmara com MediaPipe
├── i18n.js                  Textos em chinês e inglês
├── config.json              Driver, mapeamento de servos, biblioteca de poses, parâmetros da câmara
└── tools/pwm_protocol_test.mjs

Amazinghand-web/
├── server.py                Servidor HTTP + WebSocket + porta série
├── requirements.txt
├── tools/scan_servos.py     Procura no barramento SCS0009 e verifica os IDs
└── web/mediapipe/           Recursos MediaPipe (offline, cerca de 42 MB)
```

Protocolo entre frontend e backend:

```jsonc
// frontend → backend   target: "left" | "right"
{ "cmd": "ports" }                                  // volta a procurar as portas série
{ "cmd": "driver", "driver": "pwm" }                // scs0009 | pwm
{ "cmd": "connect",    "port": "COM3" }
{ "cmd": "disconnect" }
{ "cmd": "target", "target": "left" }
{ "cmd": "set",    "target": "left", "angles": { "pointer": [0, 0], ... } }
{ "cmd": "pose",   "target": "left", "name": "close" }
{ "cmd": "middle", "target": "left" }
{ "cmd": "torque", "target": "left", "on": true }   // apenas SCS0009
{ "cmd": "stop" }

// backend → frontend
{ "type": "state", "hands": {...}, "poses": {...}, "positions": {...},
  "axes": {...}, "camera": {...}, "target": "left", "driver": "scs0009",
  "capabilities": { "torque": true, "speed": true }, "pwm": {...},
  "limits": {...}, "port": { "available": [...], "current": "COM3", "connected": true } }
{ "type": "ports" | "connected" | "disconnected", "ports": [...], ... }
{ "type": "error", "msg": "falha ao ligar a COM_FAKE: o sistema não consegue encontrar o ficheiro especificado." }
```

---

## Conceção de segurança

| Item | Descrição |
|---|---|
| **Limites de pose** | Valores de pose ±120° (`limits` do `config.json`); todas as 19 poses verificadas dentro dos limites |
| **Deduplicação de alterações** | Alterações < 0,5° não são enviadas, para evitar encher o barramento com ruído |
| **Limitação de escrita** | Intervalo mínimo de 20 ms no SCS0009; acionamento direto PWM cerca de 30 ms |
| **Paragem de emergência** | SCS0009: liberta todo o binário; PWM: envia `0xFF` para interromper o gesto, e os servos continuam alimentados e mantêm a posição |
| **Proteção à saída** | SCS0009: Ctrl+C desliga o binário; PWM: após desligar a porta série, os servos mantêm a posição |
| **Depuração de uma só mão** | `--hand left/right` |

---

## Perguntas frequentes

**Reconhecimento da câmara impreciso** → luz uniforme e palma virada para a câmara. Em `tracking.js`, quanto maior o `SMOOTH` (por omissão 0.35), mais suave mas mais lento.

**Gestos da câmara errados, um dedo não acompanha** → confirme primeiro que as três poses estão capturadas (estado verde); se o sentido estiver invertido, recapture a pose correspondente; o polegar só faz flexão e não participa na abertura.

**A meio do fecho do punho um servo inverte bruscamente** → verifique se a abertura atenua até 0 com a flexão (`side *= (1 - curl)`) e se o sinal/magnitude da abertura estão anormais.

**Problemas de sentido/ID/posição central no SCS0009** → consulte [Controlo web SCS0009](scs0009.md) e [Depuração e calibração SCS0009](../06-servo-tuning/scs0009.md).

**Problemas de ligação/baudrate/calibração PWM** → consulte [Controlo web PWM](pwm.md).

**Mais perguntas** → [FAQ](../08-faq/faq.md).
