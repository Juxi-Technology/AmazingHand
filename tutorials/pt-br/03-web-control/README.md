---
title: "Controle web AmazingHand"
description: "Visão geral do controle web do AmazingHand: como iniciar, troca de driver, barra serial, controle manual, teleoperação por câmera e projeto de segurança."
version: both
---

# Controle web AmazingHand

Controle a mão dexterosa AmazingHand pelo navegador, **com dois modos (mão esquerda / mão direita)** e duas formas de operação:

- **Controle manual** — 8 controles deslizantes de servo + 19 poses predefinidas + retorno ao meio com um clique
- **Teleoperação interativa por câmera** — o MediaPipe roda localmente no navegador e mapeia os movimentos da mão para os dedos em tempo real (o vídeo nunca sai da máquina)
- **Alternância entre chinês e inglês** — alterne no canto superior direito; a escolha é lembrada pelo navegador e mantida na próxima abertura

> Esta página é a **descrição geral do controle web**. O mapeamento/conversão específico do SCS0009 está em [Controle web SCS0009](scs0009.md); a fiação/gravação/calibração específica do PWM está em [Controle web PWM](pwm.md).

## Início rápido

Abra um terminal e entre na pasta Amazinghand-web:

```bash
pip install -r requirements.txt

python server.py --no-connect   # recomendado: inicie o servidor e escolha a porta na página (nada se move)

# python server.py                # detecta a porta serial automaticamente e conecta
# python server.py --port COM9    # usa uma porta específica
# python server.py --hand left    # habilita apenas a mão esquerda
# python server.py --driver pwm   # usa os servos PWM do ESP32-S3
# python server.py --dry-run      # sem porta serial nenhuma, só a interface
```

Abra **http://localhost:8000** no navegador.

Também é possível usar diretamente o frontend estático (Web Serial, sem servidor Python):

- Online: <https://juxi-technology.github.io/AmazingHand/Amazinghand-web-io/> (Chrome / Edge)
- Local: no diretório raiz do repositório, execute `python -m http.server 8099` e abra <http://localhost:8099/Amazinghand-web-io/>

### Escolhendo a porta serial na página

O topo da página tem uma barra de ferramentas: primeiro escolha o driver, depois a porta serial:

```
Driver  [Barramento SCS0009 ▾]  Porta serial  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [Atualizar]  [Conectar]  [Desconectar]  Conectado a COM3
```

- O menu suspenso **Driver**: **Barramento SCS0009** (servos de barramento oficiais, padrão) ou **PWM (ESP32-S3)** (veja [Controle web PWM](pwm.md))
- O menu da porta lista todas as portas seriais da máquina. Chips USB-serial comuns (CH34x / CP210x / FTDI etc.) são marcados com **★** e ordenados primeiro
- **Atualizar** refaz a varredura (use depois de plugar a placa)
- **Conectar** abre a porta selecionada; logo em seguida a mão volta ao meio
- **Desconectar** libera o torque primeiro, para que os servos não fiquem travados onde estão (a versão PWM não tem comando de torque, veja a explicação abaixo)
- Para trocar de porta, basta escolher a nova e clicar em Conectar — a porta antiga é fechada para você

> **A implantação estática (GitHub Pages) não tem servidor Python**: por privacidade, o navegador não pode enumerar portas silenciosamente e só vê os dispositivos que você autorizou. Nesse caso, clique em **Adicionar porta…** e escolha a placa na janela do navegador; o comportamento acima de “listar todas as portas da máquina” só se aplica ao modo servidor com `server.py`.

![Topo da página: seleção de driver, barra serial e troca de mão esquerda/direita](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-port-bar.png)

> **O `--no-connect` foi feito para este fluxo**: o servidor inicia sem tocar em nenhuma porta serial,
> então não corre o risco de pegar a porta errada e dar um solavanco na mão. Remova o parâmetro se quiser que ele conecte na inicialização.

Os logs seriais vão para `server.log` (se você iniciar por um `.bat`, a janela pisca e passa — leia esse arquivo).

### Verificação da fiação

Lista os IDs de servo encontrados e os confere, mão por mão, contra o `config.json`.

```bash
python tools/scan_servos.py --port COM9
```

Substitua COM9 pela sua porta real.

> Esta ferramenta só se aplica aos **servos de barramento SCS0009**. Para a verificação da fiação da versão PWM, veja [Controle web PWM](pwm.md) ou use `AmazingHand-PWM/tools/serial_test.py`.

---

## Poses predefinidas (19)

![Painel de controle manual: controles deslizantes dos quatro dedos, 19 poses predefinidas e botões de ação](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-manual.png)

| Pose | Descrição | Pose | Descrição |
|---|---|---|---|
| `open` | Aberta | `wave1` | Acenar |
| `close` / `stone` | Punho fechado | `wave_r` / `wave_l` | Deslizar para a direita / esquerda |
| `ok` | OK | `ring_close` | Só o anelar |
| `greeting` | Saudação | `middle_close` | Só o médio |
| `victory` / `two` / `scissors` | Vitória / Dois | `pointer_close` | Só o indicador |
| `paper` | Papel | `thumb_close` | Só o polegar |
| `one` / `three` | Um / Três | `hifive` | High five |

Para alterar poses por conta própria, edite a seção `poses` do `config.json`; os nomes das chaves correspondem aos nomes no YAML oficial.

### Esquerda e direita podem usar valores diferentes

Dentro de uma pose, `positions` é **compartilhado pelas duas mãos**. Se uma mão precisar de outro conjunto por causa de diferenças na montagem mecânica, adicione uma chave `right` ou `left` a essa entrada e ela sobrescreve `positions`:

```jsonc
"close": {
  "label": "Punho fechado",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // compartilhado pelas duas mãos
  "right":     [ ... 8 valores ... ]               // opcional: apenas mão direita
}
```

---

## Dois modos

| Modo | Comportamento |
|---|---|
| **Mão direita** | Envia apenas para os 8 servos da mão direita |
| **Mão esquerda** | Envia apenas para os 8 servos da mão esquerda (no SCS0009, aplica automaticamente o espelhamento e o deslocamento de −35.16°; no PWM, usa o mapeamento de canais da mão esquerda) |

Uma mão por vez; alterne com o **Target** no topo. A troca não perturba a outra mão — ela mantém a pose onde está. No SCS0009, as duas mãos podem ficar no mesmo barramento; no PWM, cada mão é controlada por uma placa ESP32-S3 própria.

---

## Teleoperação interativa por câmera

Os landmarks de mão do MediaPipe rodam localmente no navegador (recursos em `Amazinghand-web/web/mediapipe/`, funcionam offline; a página também procura primeiro `Amazinghand-web-io/mediapipe/`) e convertem os 21 landmarks em valores de pose para 4 dedos, enviados em streaming para a mão selecionada.

![Painel da câmera: início, exibição do esqueleto, captura das três poses e área de status](../../assets/robot-arms/amazing-hand/AmazingHand-Web-Control/web-camera.png)

### 1. Capture três poses primeiro

Ligue a câmera, faça a pose e clique no botão de captura daquela pose (cerca de 1 segundo de média). A ordem não importa; se capturar errado, clique no mesmo botão de novo. **O status só fica verde quando as três estiverem capturadas** — nada é enviado antes disso e a mão permanece no meio.

| Botão | Pose | Fornece |
|---|---|---|
| ① Estender e abrir | Dedos retos e afastados, polegar apontando para fora | A extremidade "reto" da flexão + a extremidade "aberto" da abdução |
| ② Estender e juntar | Dedos retos e juntos, polegar encostado no indicador | A extremidade "juntos" da abdução |
| ③ Punho fechado | Feche o punho, polegar recolhido em direção à palma | A extremidade "fechado" da flexão |

### 2. Cada eixo é definido por dois pontos medidos

Tanto a flexão quanto a abdução usam **dois pontos medidos como extremidades para definir uma reta**:

```
t    = (medido − pontoA) / (pontoB − pontoA)   // limitado a 0..1
alvo = A.alvo + (B.alvo − A.alvo) × t
```

A vantagem: **o sinal da medição de cada dedo é absorvido automaticamente** — então não existe uma caixa de seleção "inverter este dedo". (Indicador e anelar ficam em lados opostos da linha central, e a cadeia de juntas do polegar é diferente, então suas direções são realmente opostas — os dois pontos medidos absorvem isso.)

Os alvos das extremidades ficam na seção `camera` do `config.json`:

| Eixo | Extremidades | Anelar | Médio | Indicador |
|---|---|---|---|---|
| Flexão | reto → punho | −50 → 90 | −50 → 90 | −50 → 90 |
| Abdução | juntos → abertos | −45 → +45 | 0 → 0 | +45 → −45 |

As duas extremidades da abdução são 0 para o dedo médio (ele não balança para os lados).

### 3. O polegar só flexiona ⚠️

A CMC do polegar é uma **articulação em sela (oponível)**, e sua flexão se acopla fortemente com a abdução — com o polegar encostado no indicador ele já está numa posição de abdução, então o "zero de flexão" medido ali fica contaminado. Forçá-lo em dois eixos faz os dois saírem errados.

Então o polegar **só flexiona; sua abdução é sempre 0** (os dois servos dele recebem o mesmo valor). As duas poses de referência que ele precisa são a ① (apontando para fora) e a ③ (apontando para a palma) — nada extra para capturar.

### 4. A abdução diminui à medida que o dedo se fecha

A abdução final é escalada por:

```
side = side_measured × (1 − curl)
```

`splayDeg` é a projeção da direção MCP→PIP sobre o eixo lateral da palma, e a flexão do dedo **gira exatamente em torno desse eixo** — passado um certo grau de fechamento, a projeção troca de sinal e o "grau de abertura" medido salta de repente para a outra extremidade.

Sem esse decaimento, o salto passa por `servo2 = flexão − abdução` e arrasta o **servo de ID par** para o sentido inverso. (O ID ímpar recebe `flexão + abdução`, então sua variação vai no sentido oposto e chama menos atenção.) O sintoma é "na metade do caminho para fechar o punho, os servos 12 e 16 invertem de repente" — 12 é o segundo servo do anelar esquerdo e 16 o do indicador esquerdo, justamente os dois cujo componente de abdução é diferente de zero.

Com o decaimento, a abdução é **exatamente 0** no fechamento total, por mais absurda que fique a medição. E um punho fechado deve ter os dedos juntos de qualquer forma.

### 5. Cores do esqueleto

| Dedo | Cor |
|---|---|
| Polegar | laranja |
| Indicador | vermelho |
| Médio | azul |
| Anelar | amarelo |
| Mindinho | cinza escuro |
| Ossos da palma | cinza neutro |

O mindinho não é usado no mapeamento de gestos, mas sua **MCP de base (landmark 17) define o sistema de coordenadas da palma da mão direita**, então não dá para simplesmente descartá-lo.

### Guia rápido de ajustes

| O que você quer mudar | Onde |
|---|---|
| Valores-alvo dos eixos | seção `camera` do `config.json` |
| **As direções de abdução das mãos esquerda e direita são opostas** | defina `-1` para aquela mão em `camera.side_sign` (`1` = sem mudança) |
| Suavidade | `SMOOTH` em `tracking.js` (padrão 0.35; menor é mais estável, mas com mais atraso) |
| Velocidade com que o fechamento é detectado | recapture as três poses |

`side_sign` se aplica à mão selecionada em **Target**; altere e recarregue a página — não é preciso reiniciar o servidor:

```jsonc
"side_sign": { "right": 1, "left": -1 }   // inverte todo o eixo de abdução na mão esquerda
```

A flexão (flexion) não é afetada por `side_sign`.

---

## Estrutura do projeto

```
Amazinghand-web-io/          frontend (estático, pode ser implantado separadamente)
├── index.html
├── app.js                   interface, troca de driver, poses e UI da câmera
├── io.js                    backend Web Serial SCS0009
├── pwm.js                   backend Web Serial PWM
├── common.js                configuração compartilhada, conversão de poses e limites
├── ws.js                    backend WebSocket (modo servidor Python)
├── tracking.js              rastreamento por câmera MediaPipe
├── i18n.js                  textos da interface em chinês/inglês
├── config.json              driver, mapeamento de servos, biblioteca de poses, parâmetros da câmera
└── tools/pwm_protocol_test.mjs

Amazinghand-web/
├── server.py                servidor HTTP + WebSocket + serial
├── requirements.txt
├── tools/scan_servos.py     escaneia o barramento SCS0009 e confere os IDs
└── web/mediapipe/           recursos do MediaPipe (offline, ~42MB)
```

Protocolo frontend/backend:

```jsonc
// frontend → backend   target: "left" | "right"
{ "cmd": "ports" }                                  // re-escaneia as portas seriais
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
{ "type": "error", "msg": "falha ao conectar COM_FAKE: o sistema não pode encontrar o arquivo especificado." }
```

---

## Segurança

| Item | Descrição |
|---|---|
| **Limites de pose** | Valores de pose ±120° (`limits` no `config.json`); as 19 poses foram verificadas e ficam dentro dos limites |
| **Deduplicação de mudanças** | Mudanças abaixo de 0,5° não são enviadas, para evitar saturar o barramento com ruído |
| **Limitação de escrita** | Intervalo mínimo de 20 ms no SCS0009; acionamento direto PWM cerca de 30 ms |
| **Parada de emergência** | SCS0009: libera todo o torque; PWM: envia `0xFF` para abortar o gesto, e os servos continuam energizados mantendo a posição |
| **Proteção na saída** | SCS0009: Ctrl+C desliga o torque; PWM: após desconectar a serial, os servos mantêm a posição |
| **Depuração de uma mão só** | `--hand left/right` |

---

## Perguntas frequentes

**O reconhecimento da câmera está impreciso** → iluminação uniforme e palma virada para a câmera. Em `tracking.js`, quanto maior o `SMOOTH` (padrão 0.35), mais suave, mas com mais atraso.

**Os gestos da câmera estão errados / um dedo não acompanha** → confirme primeiro que as três poses foram capturadas (status verde); se uma direção estiver invertida, recapture a pose correspondente; o polegar só flexiona e não participa da abdução.

**Um servo inverte de repente na metade do caminho para fechar o punho** → verifique se a abdução decai a 0 conforme o dedo fecha (`side *= (1 - curl)`) e se o sinal/valor de controle da abdução está anormal.

**Problemas de direção/ID/meio no SCS0009** → veja [Controle web SCS0009](scs0009.md) e [Depuração e calibração SCS0009](../06-servo-tuning/scs0009.md).

**Problemas de conexão/baudrate/calibração no PWM** → veja [Controle web PWM](pwm.md).

**Mais problemas** → [FAQ](../08-faq/faq.md).
