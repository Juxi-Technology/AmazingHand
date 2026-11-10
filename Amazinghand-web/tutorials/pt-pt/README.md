[Deutsch](../de/README.md) | [English](../en/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (Brasil)](../pt-br/README.md) | Português (Portugal) | [简体中文](../zh-hans/README.md) | [繁體中文](../zh-hant/README.md)

# Controlo Web do AmazingHand

Controla a mão de destreza AmazingHand a partir do navegador — **mão esquerda ou direita**, com duas formas de a comandar:

- **Manual** — 8 sliders de servo + 19 poses predefinidas + regresso ao centro com um clique
- **Teleoperação por câmara** — o MediaPipe corre localmente no navegador e mapeia a tua mão nos dedos em tempo real (o vídeo nunca sai da máquina)
- **Interface bilingue** — alterna entre chinês e inglês no canto superior direito; a escolha é memorizada pelo navegador

O mapa dos servos, a biblioteca de poses e as fórmulas de conversão estão todos alinhados com o
[AmazingHandControl](https://github.com/pollen-robotics/AmazingHand) (a GUI oficial).

---

## Início rápido

Abre um terminal e entra na pasta Amazinghand-web:

```bash
pip install -r requirements.txt

python server.py --no-connect   # recomendado: arranca o servidor, escolhe a porta na página (nada se move)

# python server.py                # deteta automaticamente a porta série e liga
# python server.py --port COM9    # usa uma porta específica
# python server.py --hand left    # ativa apenas a mão esquerda
# python server.py --driver pwm   # usa servos PWM do ESP32-S3
# python server.py --dry-run      # sem porta série nenhuma, só a UI
```

Depois abre **http://localhost:8000** no navegador.

### Escolher a porta série na página

No topo da página há uma barra de ferramentas — primeiro escolhe o driver, depois a porta série:

```
Driver  [SCS0009 bus ▾]  Port  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [Refresh]  [Connect]  [Disconnect]  Connected to COM3
```

- A lista pendente do driver: **SCS0009 bus** (servos de barramento oficiais, predefinido) ou **PWM (ESP32-S3)** (ver abaixo a [Versão de servos PWM](#versão-de-servos-pwm-acionamento-direto-pelo-esp32-s3))
- A lista pendente mostra todas as portas série da máquina. Os chips USB-série mais comuns (CH34x / CP210x / FTDI …) estão marcados com **★** e aparecem primeiro
- **Refresh** volta a fazer a deteção (usa-o depois de ligares a placa)
- **Connect** abre a porta selecionada; a mão regressa ao centro logo a seguir
- **Disconnect** liberta primeiro o binário, para que os servos não fiquem bloqueados onde estão
- Para trocar de porta, basta escolher a nova e clicar em Connect — a porta antiga é fechada automaticamente

> **O `--no-connect` foi pensado para este fluxo**: o servidor arranca sem tocar em nenhuma porta série,
> por isso não pode agarrar a porta errada e sacudir a mão. Remove a flag se quiseres que ele se ligue no arranque.

Os registos da porta série vão para `server.log` (se arrancares através de um `.bat`, a janela passa a correr — lê o ficheiro em vez disso).

### Verificação da cablagem

Lista os IDs de servo que encontra e verifica-os mão a mão contra o `config.json`.

```bash
python tools/scan_servos.py --port COM9
```

Substitui COM9 pela tua porta real.

> Esta ferramenta só se aplica a **servos de barramento SCS0009**. Para a verificação de cablagem da versão PWM, vê a secção abaixo, ou usa `AmazingHand-PWM/tools/serial_test.py`.

---

## Versão de servos PWM (acionamento direto pelo ESP32-S3)

A página web suporta as duas variantes de hardware: os servos de barramento SCS0009 oficiais e 8 servos PWM ligados a um ESP32-S3. Na versão PWM, o próprio ESP32-S3 gera os 8 sinais PWM; o computador apenas envia comandos pela porta série, **sem precisar de placa controladora de barramento**.

### Hardware e cablagem

| Item | Modelo |
|------|--------|
| Controlador | Placa de desenvolvimento ESP32-S3 (Youxin YX-ESP32-S3 ou equivalente) |
| Servos | 8 servos PWM — o firmware está calibrado para **servos digitais PTK 7452 MG-D (333 Hz)** |
| Placa adaptadora | Placa adaptadora para servos PWM |
| Alimentação | 5 V / 3 A, com terra comum entre a placa adaptadora e o ESP32 |

> O servo é especificado em 4,5 kg·cm a 7,4 V; com a alimentação de 5 V/3 A usada aqui, conte com cerca de 2,8–3 kg·cm.

Canal PWM → GPIO:

| Canal | GPIO | Articulação | Canal | GPIO | Articulação |
|------|------|------|------|------|------|
| PWM1 | 4 | Indicador, articulação 1 | PWM5 | 15 | Anelar, articulação 1 |
| PWM2 | 5 | Indicador, articulação 2 | PWM6 | 16 | Anelar, articulação 2 |
| PWM3 | 6 | Médio, articulação 1 | PWM7 | 17 | Polegar, articulação 1 |
| PWM4 | 7 | Médio, articulação 2 | PWM8 | 18 | Polegar, articulação 2 |

> ⚠️ Servos analógicos comuns de 50 Hz, como o SG90, não podem substituir diretamente o firmware de 333 Hz. Para trocar o modelo de servo, é preciso alterar ao mesmo tempo `LEDC_FREQ` e a calibração da largura de pulso, e voltar a validar.

> A cablagem é idêntica nas duas mãos: em cada par de dedos, o servo da direita é o canal ímpar e o da esquerda o par; o indicador é sempre CH1/2. As diferenças entre esquerda/direita estão apenas no código.

### Gravar o firmware

O código-fonte do firmware e os ficheiros pré-compilados estão em [`AmazingHand-PWM/`](../../../AmazingHand-PWM/README.md):

```bash
# Opção 1: ESP-IDF (v5.x / v6.x)
cd AmazingHand-PWM/firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor

# Opção 2: bin pré-compilado (requer esptool)
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  AmazingHand-PWM/firmware/prebuilt/amazinghand_pwm.bin
```

Depois de ligar, a porta série imprime:

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

### Ligação pela página web

1. No topo, escolhe **PWM (ESP32-S3)** na lista pendente **Driver**
2. Clica em **Add port…** e escolhe a porta USB série do ESP32-S3
3. Clica em **Connect**: a página faz automaticamente o handshake (NOP), envia a escolha de mão esquerda/direita e regressa ao centro
4. A partir daí, controla com os sliders, as poses predefinidas e a teleoperação por câmara; os títulos dos dedos mostram **CH 1/2 …** (o número do canal PWM)

### Diferenças em relação à versão SCS0009

| Item | Versão de barramento SCS0009 | Versão PWM |
|------|----------------|--------|
| Baudrate da porta série | 1,000,000 | **115,200** |
| Placa controladora | Placa controladora USB de barramento | ESP32-S3 + placa adaptadora PWM |
| Binário | Pode ser ativado/libertado | **Nenhum** (o firmware não tem comando de binário; o botão fica oculto) |
| Paragem de emergência | Liberta todo o binário | Envia `0xFF` para abortar o gesto; os servos continuam alimentados e mantêm a posição |
| Velocidade | Aceita parâmetro de velocidade | Os frames de acionamento direto não têm parâmetro de velocidade |
| Feedback | Leitura de posição/temperatura/tensão/velocidade | **Sem leitura**; não deteta bloqueio ou perda de passos |
| Mão esquerda/direita | IDs de servo diferentes | Os mesmos canais; envia `0xF1` para alternar (afeta principalmente os gestos do firmware; as poses da página web usam o mapeamento de cada mão) |

### Calibração dos ângulos

A página web converte os valores de pose em 8 ângulos de 0–180°, com a fórmula predefinida:

```
angle = 90 + dir × scale × valor da pose + offset
```

- O primeiro canal de cada dedo tem `dir = -1`; o segundo tem `dir = +1`
- Por omissão, `scale = 1` e `offset = 0`, ou seja, o ângulo do eixo do servo é espelhado diretamente
- A mão esquerda troca primeiro os dois valores de pose de cada dedo segundo `mirror_pose`

Se na máquina real o sentido estiver invertido ou o centro estiver desviado, edita `pwm.calibration` no [`config.json`](../../../Amazinghand-web-io/config.json):

```jsonc
"pwm": {
  "calibration": {
    "right": {
      "pointer": { "scale": 1.0, "offset_deg": [0, 0] }
    }
  }
}
```

- Sentido invertido: muda o `scale` do dedo em questão para `-1`
- Desvio do centro: ajusta `offset_deg` (os dois canais individualmente)
- Passos por dedo: voltar ao centro → arrastar um único dedo → observar o sentido/centro → alterar `scale`/`offset_deg` → recarregar a página e tentar de novo

### Perguntas frequentes

- **Falha na ligação / ESP32 não responde**: confirma que o baudrate é 115200, que escolheste a porta COM do ESP32 e que a alimentação de 5 V/3 A e o terra comum estão corretos; ao abrir a porta, o ESP32 pode reiniciar, e a página volta a tentar o NOP automaticamente
- **Os servos não se mexem ou tremem**: confirma primeiro que os servos são digitais de 333 Hz (PTK 7452 MG-D ou equivalentes) e que a alimentação é suficiente; o SG90 exige alterações no firmware
- **O sentido está invertido**: muda o `scale` do dedo em questão para `-1`
- **O centro está errado**: ajusta o `offset_deg` do canal em questão
- **Aparece «ocupado (gesto em execução)»**: o firmware está a executar um gesto incorporado; aguarda que termine ou clica na paragem de emergência (`0xFF`)
- **Procurar servos**: `tools/scan_servos.py` só se aplica ao SCS0009; para PWM, usa `AmazingHand-PWM/tools/serial_test.py` ou a página web

---

## Mapa dos servos

Fonte: `DEFAULT_HAND_SERVOS` em `AmazingHandControl/hand_logic.py` e
`docs/zh-hans/CONFIG_FORMAT.md`.

| Dedo | ID mão direita | ID mão esquerda |
|---|---|---|
| Anelar | 5, 6 | 11, 12 |
| Médio | 3, 4 | 13, 14 |
| Indicador | 1, 2 | 15, 16 |
| Polegar | 7, 8 | 17, 18 |

### Os dois servos de um dedo fazem trabalhos diferentes ⚠️

```
servo1 (ID ímpar)  = eixo de flexão    aberto ↔ fechado
servo2 (ID par)    = eixo de abertura  dedos juntos ↔ afastados
```

A UI mostra exatamente estes dois eixos. **«O dedo não abre / não fecha» significa que o eixo de abertura não se está a mover** —
um V em tesoura vem da abertura do indicador `+17` e da abertura do médio `−30` (um positivo, um negativo).

São combinados no barramento:

```
servo1 = flexão + abertura
servo2 = flexão − abertura
```

Intervalo (derivado das 19 poses oficiais mais o centro):

| Eixo | Intervalo | Significado |
|---|---|---|
| Flexão | −50 ~ +90 | aberto (negativo) ↔ fechado (positivo) |
| Abertura | −45 ~ +45 | juntos (negativo) ↔ afastados (positivo) |

**Duas regras de IDs** (enganar-se nelas queima servos ou inverte o movimento):

1. **Os IDs ímpares são o primeiro servo de um dedo, os IDs pares o segundo.** Verdade em ambas as mãos
   (esquerda 11/12, 13/14 … também alternam). O segundo servo está **montado ao contrário**, por isso nega-o na conversão.
2. **A mão esquerda não é 9–16, é 11–18, numerada começando pelo anelar.** Cablá-la como 1–8 por ordem está sempre errado.

![Both_Hands-IDs](../../Both_Hands-IDs.jpg)

---

## Conversão

Idêntica ao `apply_pose()` do `AmazingHandControl` (verificada pose a pose):

```
1) quando mirror_pose é true, troca primeiro os dois valores de servo de cada dedo
2) servo_deg = (ID ímpar ? +1 : -1) × (valor da pose − angle_offset_deg)
```

| Mão | angle_offset_deg | mirror_pose |
|---|---|---|
| Direita | `0` | **sim** ⚠️ |
| Esquerda | `-35.16` | sim |

`-35.16°` é o desvio físico de meio entalhe dos braços dos servos da mão esquerda em relação à direita, retirado da configuração oficial.

> **Sobre o `mirror_pose` — esta versão difere da oficial**
>
> Na referência oficial, só a mão esquerda é `true`. **Nesta versão, o módulo da mão direita também
> tem os pares de servos montados ao contrário**, por isso a mão direita também é `true`.
>
> A troca só inverte a **abertura**, nunca a flexão: `base = (a+b)/2` não muda com a troca, enquanto
> `side = (a−b)/2` muda de sinal. Portanto, se a abertura de uma mão sair espelhada, este é o primeiro interruptor a verificar.

O array de pose tem sempre 8 valores na ordem **`[ring, middle, index, thumb]`**, dois por dedo —
idêntico byte a byte ao `data/hand_config.yaml` oficial, por isso podes compará-los diretamente.

### Exemplos práticos

| Pose | Direita | Esquerda |
|---|---|---|
| `open` `[-35]*8` | ID5 **−35** / ID6 **+35** | ID11 **+0.16** / ID12 **−0.16** |
| `close` `[75]*8` | ID5 **+75** / ID6 **−75** | ID11 **+110.16** / ID12 **−110.16** |
| middle `[-17.578]*8` | ID5 **−17.58** / ID6 **+17.58** | ID11 **+17.58** / ID12 **−17.58** |

> **Nota que o `close` da mão esquerda precisa de ±110.16°**, muito acima do da direita. É por isso que o `config.json`
> define o limite em **±120°** (o intervalo total do SCS0009 é cerca de ±150°). Um limite de ±90 cortaria o punho da mão esquerda.

---

## Poses predefinidas (19)

| Pose | | Pose | |
|---|---|---|---|
| `open` | Aberta | `wave1` | Aceno |
| `close` / `stone` | Punho | `wave_r` / `wave_l` | Deslizar à direita / à esquerda |
| `ok` | OK | `ring_close` | Só o anelar |
| `greeting` | Cumprimento | `middle_close` | Só o médio |
| `victory` / `two` / `scissors` | Vitória / Dois | `pointer_close` | Só o indicador |
| `paper` | Papel | `thumb_close` | Só o polegar |
| `one` / `three` | Um / Três | `hifive` | High five |

Para alterar uma pose, edita a secção `poses` do `config.json`; as chaves correspondem aos nomes no YAML oficial.

### As mãos esquerda e direita podem usar valores diferentes

Dentro de uma pose, `positions` é **partilhado pelas duas mãos**. Se uma mão precisar de um conjunto
diferente devido a diferenças de montagem mecânica, acrescenta uma chave `right` ou `left` a essa entrada e esta sobrepõe-se a `positions`:

```jsonc
"close": {
  "label": "Punho",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // partilhado pelas duas mãos
  "right":     [ ... 8 valores ... ]                // opcional: só a mão direita
}
```

---

## Dois modos

| Modo | Comportamento |
|---|---|
| **Mão direita** | Envia apenas para os 8 servos da mão direita |
| **Mão esquerda** | Envia apenas para os 8 servos da mão esquerda (espelhamento + desvio de −35.16° aplicados automaticamente) |

Uma mão de cada vez. As duas mãos estão no mesmo barramento; alterna com **Target** no topo.
A alternância não perturba a outra mão — esta mantém a pose onde está.

---

## Teleoperação por câmara

Os landmarks da mão do MediaPipe correm localmente no navegador (recursos em `web/mediapipe/`, funciona offline).
Os 21 landmarks são convertidos em valores de pose para 4 dedos e transmitidos para a mão selecionada.

### 1. Captura primeiro três poses

Liga a câmara, coloca a mão na pose e clica no botão de captura dessa pose (cerca de 1 segundo de média).
A ordem não importa; clica no mesmo botão outra vez para recapturar. **O estado só fica verde quando as três estiverem capturadas** —
nada é enviado antes disso, por isso a mão fica no centro.

| Botão | Pose | Fornece |
|---|---|---|
| ① Spread | Dedos esticados e afastados, polegar apontado para fora | O extremo «estendido» da flexão + o extremo «afastado» da abertura |
| ② Together | Dedos esticados e juntos, polegar encostado ao indicador | O extremo «junto» da abertura |
| ③ Fist | Faz um punho, polegar recolhido contra a palma | O extremo «fechado» da flexão |

### 2. Cada eixo é uma reta que passa por dois pontos medidos

Tanto a flexão como a abertura usam **dois pontos extremos medidos para definir uma reta**:

```
t      = (medido − endpointA) / (endpointB − endpointA)      // limitado a 0..1
alvo   = A.alvo + (B.alvo − A.alvo) × t
```

A vantagem: **o sinal da medição de cada dedo é absorvido automaticamente** — por isso não há
nenhuma caixa «inverter este dedo» para assinalar. (O indicador e o anelar estão em lados opostos da linha central, e
a cadeia de articulações do polegar é diferente, por isso as suas direções são mesmo opostas — dois pontos extremos medidos absorvem isso.)

Os alvos dos pontos extremos estão na secção `camera` do `config.json`:

| Eixo | Pontos extremos | Anelar | Médio | Indicador |
|---|---|---|---|---|
| Flexão | estendido → punho | −50 → 90 | −50 → 90 | −50 → 90 |
| Abertura | juntos → afastados | −45 → +45 | 0 → 0 | +45 → −45 |

Ambos os extremos da abertura são 0 para o dedo médio (não oscila lateralmente).

### 3. O polegar apenas flexiona ⚠️

A CMC do polegar é uma **articulação em sela (oponível)**, e a sua flexão está fortemente acoplada à abdução —
com o polegar encostado ao indicador já está numa posição de abertura, por isso a «flexão zero» medida aí é
contaminada. Forçá-la em dois eixos faz com que ambos saiam errados.

Por isso o polegar **apenas flexiona; a sua abertura é sempre 0** (os seus dois servos recebem o mesmo valor). As duas
poses de referência de que precisa são a ① (apontado para fora) e a ③ (apontado para a palma) — nada mais para capturar.

### 4. A abertura desvanece à medida que o dedo se enrola

A abertura final é escalada por:

```
side = side_measured × (1 − curl)
```

`splayDeg` é a projeção da direção MCP→PIP sobre o eixo lateral da palma, e a flexão do dedo
**roda exatamente em torno desse eixo** — passado um certo enrolamento, a projeção troca de sinal e a «abertura»
medida salta de repente para o outro extremo.

Sem este desvanecimento, esse salto atravessa `servo2 = flexion − splay` e arrasta o **servo de ID par**
para o sentido inverso. (O ID ímpar recebe `flexion + splay`, por isso move-se no mesmo sentido, apenas mais depressa — não se nota.)
O sintoma é «a meio de fechar o punho, os servos 12 e 16 invertem de repente» — o 12 é o servo de abertura do
anelar esquerdo e o 16 o do indicador esquerdo, precisamente os dois cujos alvos de abertura são diferentes de zero.

Com o desvanecimento, a abertura é **exatamente 0** no enrolamento total, por muito disparatada que a medição fique.
E um punho deve ter os dedos juntos de qualquer forma.

### 5. Cores do esqueleto

| Dedo | Cor |
|---|---|
| Polegar | laranja |
| Indicador | vermelho |
| Médio | azul |
| Anelar | amarelo |
| Mindinho | cinzento escuro |
| Ossos da palma | cinzento neutro |

O mindinho não é usado no mapeamento de gestos, mas a sua **MCP de base (landmark 17) define o referencial de coordenadas
da palma da mão direita**, por isso não pode ser simplesmente descartado.

### Guia rápido de afinação

| O que queres alterar | Onde |
|---|---|
| Valores alvo dos eixos | secção `camera` do `config.json` |
| **A abertura da esquerda e da direita vai em sentidos opostos** | define essa mão como `-1` em `camera.side_sign` (`1` = sem alteração) |
| Suavidade | `SMOOTH` em `tracking.js` (por omissão 0.35; mais baixo é mais estável mas com mais atraso) |
| Rapidez com que um enrolamento é detetado | recaptura as três poses |

`side_sign` aplica-se à mão que estiver selecionada em **Target**. Altera-o e recarrega a página —
não é preciso reiniciar o servidor:

```jsonc
"side_sign": { "right": 1, "left": -1 }   // inverte todo o eixo de abertura na mão esquerda
```

A flexão não é afetada pelo `side_sign`.

---

## Estrutura do projeto

```
Amazinghand-web/
├── config.json          mapa de servos / biblioteca de poses / sequências / limites (gerado a partir do YAML oficial)
├── server.py            backend: porta série + ficheiros estáticos + WebSocket
├── requirements.txt
├── README.md            Inglês (ficheiro original)
├── tutorials/           de · en · es · fr · it · ja · ko · pt-br · pt-pt · zh-hans · zh-hant
├── tools/
│   └── scan_servos.py   procura servos no barramento e verifica os seus IDs
└── web/
    ├── index.html · app.js · tracking.js · style.css
    ├── i18n.js          textos da UI (dicionário chinês/inglês + comutador no canto superior direito)
    └── mediapipe/       recursos do MediaPipe (incluídos localmente, offline, ~42 MB)
```

Protocolo frontend/backend:

```jsonc
// frontend → backend   target: "left" | "right"
{ "cmd": "ports" }                                  // volta a procurar as portas série
{ "cmd": "connect",    "port": "COM3" }
{ "cmd": "disconnect" }
{ "cmd": "target", "target": "left" }
{ "cmd": "set",    "target": "left", "angles": { "pointer": [0, 0], ... } }
{ "cmd": "pose",   "target": "left", "name": "close" }
{ "cmd": "middle", "target": "left" }
{ "cmd": "torque", "target": "left", "on": true }
{ "cmd": "stop" }

// backend → frontend
{ "type": "state", "hands": {...}, "poses": {...}, "positions": {...},
  "axes": {...}, "camera": {...}, "target": "left",
  "limits": {...}, "port": { "available": [...], "current": "COM3", "connected": true } }
{ "type": "ports" | "connected" | "disconnected", "ports": [...], ... }
{ "type": "error", "msg": "connect COM_FAKE failed: the system cannot find the file specified." }
```

---

## Segurança

| Item | |
|---|---|
| **Limites de pose** | ±120° (`limits` no `config.json`); as 19 poses verificadas para se manterem dentro |
| **Deduplicação de alterações** | alterações abaixo de 0.5° não são enviadas, para o barramento não ser inundado com ruído |
| **Limitação de escrita** | mínimo de 20 ms entre escritas |
| **Paragem de emergência** | o botão vermelho na UI liberta todos os servos de uma vez |
| **Proteção à saída** | o binário é libertado automaticamente com Ctrl+C |
| **Depuração de uma só mão** | `--hand left/right` |

---

## Resolução de problemas

**O movimento está invertido** → verifica se a cablagem segue «primeiro o ID ímpar»; na mão esquerda confirma também `angle_offset_deg = -35.16`.

**O punho da mão esquerda é demasiado pequeno / os servos zumbem** → o limite provavelmente ainda é ±90; verifica se o `config.json` tem ±120.

**Um dedo não se move / «expected N motors, found M»** → executa `tools/scan_servos.py`; os IDs da mão esquerda são os mais fáceis de ligar mal.

**A posição central está errada** → o valor central `-17.578125` é convertido do valor bruto oficial 451/571.
Para calibrar com a tua própria montagem, edita `middle.positions` no `config.json`.

**O seguimento da câmara está instável** → iluminação uniforme, palma virada para a câmara. `SMOOTH` em `tracking.js`
(por omissão 0.35) — mais alto é mais suave mas com mais atraso.

**Os gestos da câmara estão errados / um dedo não acompanha** → vê a secção Teleoperação por câmara acima. Verifica primeiro três coisas:

1. **As três poses estão todas capturadas?** — o estado tem de estar verde; nada é enviado antes disso e a mão fica no centro
2. **Uma direção invertida significa que essa pose foi capturada ao contrário** — basta recapturar esse botão, sem alterar código
3. **O polegar não deve abrir** — apenas flexiona, vê a secção 3 acima

**Um servo entra em sentido inverso a meio de fechar o punho** → esse servo deve ter um **ID par** (o eixo de abertura, por exemplo 12 / 16 na mão esquerda).
Normalmente a abertura desvanece para 0 com o enrolamento e nunca salta; se vires isto, a linha `side *= (1 - curl)` em
`tracking.js` não está a ter efeito, ou o `curl` não está a ser calculado.
