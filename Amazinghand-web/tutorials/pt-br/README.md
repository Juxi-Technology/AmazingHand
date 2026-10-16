[Deutsch](../de/README.md) | [English](../en/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | Português (Brasil) | [Português (Portugal)](../pt-pt/README.md) | [简体中文](../zh-hans/README.md) | [繁體中文](../zh-hant/README.md)

# AmazingHand Web Control

Controle a mão dexterosa AmazingHand a partir do navegador — **mão esquerda ou direita**, com duas formas de comandá-la:

- **Manual** — 8 sliders de servo + 19 poses predefinidas + retorno ao meio com um clique
- **Teleoperação por câmera** — o MediaPipe roda localmente no navegador e mapeia sua mão para os dedos em tempo real (o vídeo nunca sai da máquina)
- **Interface bilíngue** — alterne entre chinês e inglês no canto superior direito; a escolha é lembrada pelo navegador

O mapa de servos, a biblioteca de poses e as fórmulas de conversão batem com o
[AmazingHandControl](https://github.com/pollen-robotics/AmazingHand) (a GUI oficial).

---

## Início rápido

```bash
pip install -r requirements.txt

python server.py --no-connect   # recomendado: inicie o servidor e escolha a porta na página (nada se move)

# python server.py                # detecta a porta serial automaticamente e conecta
# python server.py --port COM9    # usa uma porta específica
# python server.py --hand left    # habilita apenas a mão esquerda
# python server.py --dry-run      # sem porta serial nenhuma, só a interface
```

Depois abra **http://localhost:8000** em um navegador.

### Escolhendo a porta serial na página

O topo da página tem uma barra de porta:

```
Port  [COM3 ★ USB-Enhanced-SERIAL CH343 ▾]  [Refresh]  [Connect]  [Disconnect]  Connected to COM3
```

- O menu suspenso lista todas as portas seriais da máquina. Chips USB-serial comuns (CH34x / CP210x / FTDI …) são marcados com **★** e ordenados primeiro
- **Refresh** refaz a varredura (use depois de plugar a placa)
- **Connect** abre a porta selecionada; logo em seguida a mão volta ao meio
- **Disconnect** libera o torque primeiro, para que os servos não fiquem travados onde estão
- Para trocar de porta, basta escolher a nova e clicar em Connect — a porta antiga é fechada para você

> **O `--no-connect` foi feito para este fluxo**: o servidor inicia sem tocar em nenhuma porta serial,
> então não corre o risco de pegar a porta errada e dar um solavanco na mão. Remova a flag se quiser que ele conecte na inicialização.

Os logs seriais vão para `server.log` (se você iniciar por um `.bat`, a janela pisca e passa — leia o arquivo em vez disso).

### Verificação da fiação

Lista os IDs de servo encontrados e os confere, mão por mão, contra o `config.json`.

```bash
python tools/scan_servos.py --port COM9
```

Substitua COM9 pela sua porta real.

---

## Mapa de servos

Fonte: `DEFAULT_HAND_SERVOS` em `AmazingHandControl/hand_logic.py` e
`docs/zh-hans/CONFIG_FORMAT.md`.

| Dedo | ID mão direita | ID mão esquerda |
|---|---|---|
| Anelar | 5, 6 | 11, 12 |
| Médio | 3, 4 | 13, 14 |
| Indicador | 1, 2 | 15, 16 |
| Polegar | 7, 8 | 17, 18 |

### Os dois servos de um dedo fazem trabalhos diferentes ⚠️

Convenção oficial:

```
servo1 (ID ímpar) = eixo de flexão   aberto ↔ fechado
servo2 (ID par)   = eixo de splay    dedos juntos ↔ afastados
```

A interface mostra exatamente esses dois eixos. **"O dedo não abre / não fecha" significa que o eixo de splay (abertura lateral) não está se movendo** —
um V estilo tesoura vem do splay do indicador `+17` e do splay do médio `−30` (um positivo, um negativo).

Eles são combinados no barramento (seguindo o formato de armazenamento oficial):

```
servo1 = flexão + splay
servo2 = flexão − splay
```

Faixa (derivada das 19 poses oficiais mais a posição do meio):

| Eixo | Faixa | Significado |
|---|---|---|
| Flexão | −50 ~ +90 | aberto (negativo) ↔ fechado (positivo) |
| Splay | −45 ~ +45 | juntos (negativo) ↔ afastados (positivo) |

**Duas regras de ID** (errar nelas queima servos ou inverte o movimento):

1. **IDs ímpares são o primeiro servo de um dedo, IDs pares o segundo.** Vale nas duas mãos
   (na esquerda, 11/12, 13/14 … também alternam). O segundo servo é **montado ao contrário**, então negue-o na conversão.
2. **A mão esquerda não é 9–16, é 11–18, numerada começando pelo anelar.** Ligá-la como 1–8 em sequência está sempre errado.

![Both_Hands-IDs](../../Both_Hands-IDs.jpg)

---

## Conversão

Idêntico ao `apply_pose()` do `AmazingHandControl` (verificado pose por pose):

```
1) quando mirror_pose é true, primeiro troque os dois valores de servo de cada dedo
2) servo_deg = (ID ímpar ? +1 : -1) × (valor da pose − angle_offset_deg)
```

| Mão | angle_offset_deg | mirror_pose |
|---|---|---|
| Direita | `0` | **sim** ⚠️ |
| Esquerda | `-35.16` | sim |

`-35.16°` é o deslocamento físico de meio entalhe dos horns dos servos da mão esquerda em relação à direita, retirado da config oficial.

> **Sobre o `mirror_pose` — esta build difere da oficial**
>
> Na referência oficial, só a mão esquerda é `true`. **O módulo da mão direita desta build também tem os
> pares de servos montados invertidos**, então a mão direita também é `true`.
>
> A troca inverte apenas o **splay**, nunca a flexão: `base = (a+b)/2` não muda com a troca, enquanto
> `side = (a−b)/2` troca de sinal. Então, se o splay de uma mão sair espelhado, este é o primeiro interruptor a verificar.

O array de pose é sempre 8 valores na ordem **`[ring, middle, index, thumb]`**, dois por dedo —
idêntico byte a byte ao `data/hand_config.yaml` oficial, então você pode compará-los diretamente.

### Exemplos resolvidos

| Pose | Direita | Esquerda |
|---|---|---|
| `open` `[-35]*8` | ID5 **−35** / ID6 **+35** | ID11 **+0.16** / ID12 **−0.16** |
| `close` `[75]*8` | ID5 **+75** / ID6 **−75** | ID11 **+110.16** / ID12 **−110.16** |
| middle `[-17.578]*8` | ID5 **−17.58** / ID6 **+17.58** | ID11 **+17.58** / ID12 **−17.58** |

> **Note que o `close` da mão esquerda precisa de ±110.16°**, bem além do da direita. É por isso que o `config.json`
> define o limite em **±120°** (a faixa completa do SCS0009 é de cerca de ±150°). Um limite de ±90 cortaria o punho fechado da mão esquerda.

---

## Poses predefinidas (19)

| Pose | | Pose | |
|---|---|---|---|
| `open` | Aberta | `wave1` | Acenar |
| `close` / `stone` | Punho fechado | `wave_r` / `wave_l` | Deslizar para a direita / esquerda |
| `ok` | OK | `ring_close` | Só o anelar |
| `greeting` | Saudação | `middle_close` | Só o médio |
| `victory` / `two` / `scissors` | Vitória / Dois | `pointer_close` | Só o indicador |
| `paper` | Papel | `thumb_close` | Só o polegar |
| `one` / `three` | Um / Três | `hifive` | High five |

Para mudar uma pose, edite a seção `poses` do `config.json`; as chaves correspondem aos nomes no YAML oficial.

### Esquerda e direita podem usar valores diferentes

Dentro de uma pose, `positions` é **compartilhado pelas duas mãos**. Se uma mão precisar de um conjunto diferente
por causa de diferenças na montagem mecânica, adicione uma chave `right` ou `left` a essa entrada e ela sobrescreve `positions`:

```jsonc
"close": {
  "label": "Punho fechado",
  "positions": [75, 75, 75, 75, 75, 75, 18, 18],   // compartilhado pelas duas mãos
  "right":     [ ... 8 valores ... ]               // opcional: apenas mão direita
}
```

Uma pose sem chave `right` / `left` usa os valores compartilhados nas duas mãos — então você só precisa escrever
as que realmente diferem. A posição do meio (`middle`) continua compartilhada pelas duas mãos.

---

## Dois modos

| Modo | Comportamento |
|---|---|
| **Mão direita** | Envia apenas para os 8 servos da mão direita |
| **Mão esquerda** | Envia apenas para os 8 servos da mão esquerda (espelhamento + offset de −35.16° aplicados automaticamente) |

Uma mão por vez. As duas mãos ficam no mesmo barramento; alterne com **Target** no topo.
A troca não perturba a outra mão — ela mantém a pose onde está.

---

## Teleoperação por câmera

Os landmarks de mão do MediaPipe rodam localmente no navegador (ativos em `web/mediapipe/`, funcionam offline).
Os 21 landmarks são convertidos em valores de pose para 4 dedos e enviados em streaming para a mão selecionada.

### 1. Capture três poses primeiro

Ligue a câmera, faça a pose com a mão e clique no botão de captura daquela pose (cerca de 1 segundo de média).
A ordem não importa; clique no mesmo botão de novo para recapturar. **O status só fica verde quando as três estiverem capturadas** —
nada é enviado antes disso, então a mão permanece no meio.

| Botão | Pose | Fornece |
|---|---|---|
| ① Spread | Dedos retos e afastados, polegar apontando para fora | A extremidade "reto" da flexão + a extremidade "afastado" do splay |
| ② Together | Dedos retos e juntos, polegar encostado no indicador | A extremidade "juntos" do splay |
| ③ Fist | Feche o punho, polegar recolhido em direção à palma | A extremidade "fechado" da flexão |

### 2. Cada eixo é uma reta passando por dois pontos medidos

Tanto a flexão quanto o splay usam **dois pontos medidos como extremidades para definir uma reta**:

```
t    = (medido − pontoA) / (pontoB − pontoA)   // limitado a 0..1
alvo = A.alvo + (B.alvo − A.alvo) × t
```

A vantagem: **o sinal da medição de cada dedo é absorvido automaticamente** — então não existe
uma caixa de seleção "inverter este dedo" para marcar. (Indicador e anelar ficam em lados opostos da linha central, e
a cadeia de juntas do polegar é diferente, então suas direções são realmente opostas — os dois pontos medidos absorvem isso.)

Os alvos das extremidades ficam na seção `camera` do `config.json`:

| Eixo | Extremidades | Anelar | Médio | Indicador |
|---|---|---|---|---|
| Flexão | reto → punho | −50 → 90 | −50 → 90 | −50 → 90 |
| Splay | juntos → afastados | −45 → +45 | 0 → 0 | +45 → −45 |

As duas extremidades do splay são 0 para o dedo médio (ele não balança para os lados).

> **Esses dois conjuntos são compartilhados pelas duas mãos.** Se uma mão acabar se movendo ao contrário, mude aquela
> mão em `camera.side_sign` (veja a cola de ajustes no final) e recarregue a página.

### 3. O polegar só flexiona ⚠️

A CMC do polegar é uma **articulação em sela (oponível)**, e sua flexão se acopla fortemente com a abdução —
com o polegar encostado no indicador ele já está numa posição de splay, então o "zero de flexão"
medido ali fica contaminado. Forçá-lo em dois eixos faz os dois saírem errados.

Então o polegar **só flexiona; seu splay é sempre 0** (os dois servos dele recebem o mesmo valor). As duas
poses de referência que ele precisa são a ① (apontando para fora) e a ③ (apontando para a palma) — nada extra para capturar.

### 4. O splay some à medida que o dedo se fecha

O splay final é escalado por:

```
side = side_measured × (1 − curl)
```

`splayDeg` é a projeção da direção MCP→PIP sobre o eixo lateral da palma, e a flexão do dedo
**gira exatamente em torno desse eixo** — passado um certo grau de fechamento, a projeção troca de sinal e o "afastamento"
medido salta de repente para a outra extremidade.

Sem esse fade, o salto passa por `servo2 = flexão − splay` e arrasta o **servo de ID par**
para o sentido inverso. (O ID ímpar recebe `flexão + splay`, então se move no mesmo sentido, só que mais rápido — você não percebe.)
O sintoma é "na metade do caminho para fechar o punho, os servos 12 e 16 invertem de repente" — 12 é o servo de splay do anelar
esquerdo e 16 o do indicador esquerdo, justamente os dois cujos alvos de splay são diferentes de zero.

Com o fade, o splay é **exatamente 0** no fechamento total, por mais maluca que a medição fique.
E um punho fechado deve ter os dedos juntos de qualquer forma.

### 5. Cores do esqueleto

| Dedo | Cor |
|---|---|
| Polegar | laranja |
| Indicador | vermelho |
| Médio | azul |
| Anelar | amarelo |
| Mindinho | cinza escuro |
| Ossos da palma | cinza neutro |

O mindinho não é usado no mapeamento de gestos, mas sua **MCP de base (landmark 17) define o sistema de
coordenadas da palma da mão direita**, então não dá para simplesmente descartá-lo. O modelo regride os 21 pontos de uma vez
e não tem um estado "este dedo não foi visto" — quando a palma o esconde, ele ainda retorna uma posição **estimada**.
Desenhá-lo em tom apagado deixa óbvio quando ele está chutando.

### Cola de ajustes

| O que você quer mudar | Onde |
|---|---|
| Valores-alvo dos eixos | seção `camera` do `config.json` |
| **O splay da esquerda e da direita vão em sentidos opostos** | defina `-1` para aquela mão em `camera.side_sign` (`1` = sem mudança) |
| Suavidade | `SMOOTH` em `tracking.js` (padrão 0.35; menor é mais estável, mas com mais atraso) |
| Velocidade com que o fechamento é registrado | recapture as três poses |

`side_sign` se aplica à mão que estiver selecionada em **Target**. Altere e recarregue a página —
não é preciso reiniciar o servidor:

```jsonc
"side_sign": { "right": 1, "left": -1 }   // inverte todo o eixo de splay na mão esquerda
```

A flexão não é afetada por `side_sign`.

---

## Estrutura do projeto

```
Amazinghand-web/
├── config.json          mapa de servos / biblioteca de poses / sequências / limites (gerado a partir do YAML oficial)
├── server.py            backend: serial + arquivos estáticos + WebSocket
├── requirements.txt
├── README.md            Inglês (o documento raiz)
├── tutorials/           de · en · es · fr · it · ja · ko · pt-br · pt-pt · zh-hans · zh-hant
├── tools/
│   └── scan_servos.py   varre o barramento em busca de servos e confere seus IDs
└── web/
    ├── index.html · app.js · tracking.js · style.css
    ├── i18n.js          textos da interface (dicionário chinês/inglês + o seletor no canto superior direito)
    └── mediapipe/       ativos do MediaPipe (empacotados localmente, offline, ~42 MB)
```

Protocolo frontend/backend:

```jsonc
// frontend → backend   target: "left" | "right"
{ "cmd": "ports" }                                  // re-escaneia as portas seriais
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
{ "type": "error", "msg": "falha ao conectar COM_FAKE: o sistema não pode encontrar o arquivo especificado." }
```

---

## Segurança

| Item | |
|---|---|
| **Limites de pose** | ±120° (`limits` no `config.json`); as 19 poses verificadas para ficarem dentro |
| **Deduplicação de mudanças** | mudanças abaixo de 0.5° não são enviadas, para não inundar o barramento com ruído |
| **Limitação de escrita** | mínimo de 20 ms entre escritas |
| **Botão de emergência** | o botão vermelho na interface libera todos os servos de uma vez |
| **Proteção na saída** | o torque é liberado automaticamente no Ctrl+C |
| **Debug de uma mão só** | `--hand left/right` |

---

## Solução de problemas

**O movimento está invertido** → verifique se a fiação segue "ID ímpar primeiro"; na mão esquerda, confirme também `angle_offset_deg = -35.16`.

**O punho da mão esquerda fica pequeno demais / os servos zumbem** → o limite provavelmente ainda está em ±90; verifique se o `config.json` tem ±120.

**Um dedo não se move / "expected N motors, found M"** → rode `tools/scan_servos.py`; os IDs da mão esquerda são os mais fáceis de ligar errado.

**A posição do meio está errada** → o valor do meio `-17.578125` é convertido do bruto oficial 451/571.
Para calibrar com a sua própria montagem, edite `middle.positions` no `config.json`.

**O rastreamento da câmera está tremendo** → iluminação uniforme, palma virada para a câmera. `SMOOTH` em `tracking.js`
(padrão 0.35) — mais alto é mais suave, mas com mais atraso.

**Os gestos da câmera estão errados / um dedo não acompanha** → veja a seção Teleoperação por câmera acima. Verifique três coisas primeiro:

1. **As três poses foram capturadas?** — o status precisa estar verde; nada é enviado antes disso e a mão fica no meio
2. **Uma direção invertida significa que aquela pose foi capturada ao contrário** — basta recapturar aquele botão, sem mudar código
3. **O polegar não deve fazer splay** — ele só flexiona, veja a seção 3 acima

**Um servo inverte de repente na metade do caminho para fechar o punho** → esse servo deve ter um **ID par** (o eixo de splay, por exemplo 12 / 16 na mão esquerda).
Normalmente o splay vai a 0 conforme o dedo fecha e nunca salta; se você vir isso, a linha `side *= (1 - curl)` em
`tracking.js` não está fazendo efeito, ou `curl` não está sendo calculado.
