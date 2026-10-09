[English](../en/CHANGES.md) | [Deutsch](../de/CHANGES.md) | [Español](../es/CHANGES.md) | [Français](../fr/CHANGES.md) | [Italiano](../it/CHANGES.md) | [日本語](../ja/CHANGES.md) | [한국어](../ko/CHANGES.md) | Português (BR) | [Português (PT)](../pt-pt/CHANGES.md) | [简体中文](../zh-hans/CHANGES.md) | [繁體中文](../zh-hant/CHANGES.md)

# AmazingHand Controller · Registro de alterações e justificativa

O que mudou em relação ao projeto original, por quê, e qual é de fato o resultado.

Projeto original: `Betatester777/AmazingHandControl` (GUI + CLI em Python para o AmazingHand)
Hardware: JuxiTechnology AmazingHand (8× servos Feetech SCS0009, feedback por potenciômetro) — **ambas as mãos suportadas**, selecionadas na inicialização

---

## Conteúdo

1. [Recalibração do sistema de ângulos](#1-recalibração-do-sistema-de-ângulos)
2. [Botões globais: acionar posições raw exatas](#2-botões-globais-acionar-posições-raw-exatas)
3. [Novo botão de posição central](#3-novo-botão-de-posição-central)
4. [GUI e CLI em discordância (o bug central)](#4-gui-e-cli-em-discordância-o-bug-central)
5. [Correções dos dados de pose](#5-correções-dos-dados-de-pose)
6. [Reprodutor de sequências: temporização e diagnóstico](#6-reprodutor-de-sequências-temporização-e-diagnóstico)
7. [Nova linha de posição raw no feedback dos servos](#7-nova-linha-de-posição-raw-no-feedback-dos-servos)
8. [**Suporte a mão esquerda e direita**](#8-suporte-a-mão-esquerda-e-direita)
9. [Detecção automática de porta serial](#9-detecção-automática-de-porta-serial)
10. [Referência de configuração](#10-referência-de-configuração)
11. [Resultados medidos](#11-resultados-medidos)
12. [Resumo arquivo por arquivo](#12-resumo-arquivo-por-arquivo)

---

## 1. Recalibração do sistema de ângulos

### 1.1 Limites de ângulo: `0..110` → `-75..75`

O original foi calibrado como `0° = aberto, 110° = fechado`. O curso real desta mão fica em `-75..75`, então tudo foi recalibrado.

**`data/config.yaml`**

| Chave | Antes | Depois |
|---|---|---|
| `servo_min` / `servo_max` | -40 / 110 | **-75 / 75** |
| `base_min` / `base_max` | 0 / 110 | **-75 / 75** |
| `side_min` / `side_max` | -40 / 40 | **-35 / 35** |
| `left_open` | `[32, -40]` | **`[32, -35]`** |
| `right_open` | `[-40, 32]` | **`[-35, 32]`** |
| `left_closed` / `right_closed` | `[110, 110]` | **`[75, 75]`** |
| `center_closed` | `[110, 110]` | **`[75, 75]`** |

**Todas as 19 poses foram reescaladas**, por exemplo, `open` de `[0]*8` para `[-35]*8`, `close` de `[110]*8` para `[75]*8`.

### 1.2 Dispersão lateral: `±40°` → `±35°`

O controle deslizante lateral normaliza com `u = |side_offset| / |side_min|`, então mudar apenas o limite **não** altera a distância com que os dedos realmente se abrem — só reescala o controle deslizante. Para mudar a dispersão física é preciso mudar também `auto_extremes`. Com ambos alterados:

| | Antes (±40) | Depois (±35) |
|---|---|---|
| Faixa do controle deslizante | −40 … +40 | −35 … +35 |
| Totalmente aberto, no extremo lateral | `(32, -40)`, dispersão de **72°** | `(32, -35)`, dispersão de **67°** |

### 1.3 Correspondência com a referência do fabricante

O demo Arduino do fabricante (`Amazing_RHand_Demo.ino`) converte assim:

```c
float Step = 0.293; // 300°/1024
sc.RegWritePos(1, MiddlePos[0] + Pos_1 / Step, 0, Speed);
```

E o rustypot 1.4.2 (`src/servo/feetech/scs0009.rs`):

```rust
fn to_raw(value: f64) -> i16 {
    let a = (1024.0 * value / (300.0_f64.to_radians()) + 511.0) as i16;
    a.to_be()
}
```

**Conclusão: os dois lados usam a mesma escala de graus** (0,29297°/passo, 300° de escala total, raw 0–1023) — não há erro de proporção. A única diferença sistemática é o ponto zero:

- o rustypot sempre centraliza no raw **511**
- o firmware do fabricante usa um valor de calibração por servo, `MiddlePos = {451, 571, 451, 571, 451, 571, 451, 571}`

Eles diferem em **±60 raw = ±17,6°**. É exatamente isso que o botão "Middle position" abaixo resolve.

---

## 2. Botões globais: acionar posições raw exatas

### 2.1 O problema

Os `open_all()` / `close_all()` originais tinham ângulos fixos no código:

```python
def open_all(self):
    for finger in self.fingers:
        finger.pos_var.set(0)      # hard-coded 0
        finger.side_var.set(0)
        ...
def close_all(self):
    for finger in self.fingers:
        finger.pos_var.set(110)    # hard-coded 110
```

Esses valores vêm da **escala de calibração antiga** (0 = aberto, 110 = fechado). Após recalibrar para `-35 / 75`:

- `open_all` definia 0° → converte para o raw **511**, ou seja, mais ou menos o meio mecânico — os dedos nunca abriam
- `close_all` definia 110° → limitado por `base_max = 75`, então só chegava a 75, enquanto o rótulo ainda mostrava 110°

### 2.2 A correção: um caminho direto de posição raw

O caminho por ângulos passa pelo modelo de interpolação `base/side`, que não consegue atingir um valor raw arbitrário com exatidão (veja a seção 4). Por isso os botões globais ganharam um caminho que escreve posições raw dos servos diretamente.

**Um detalhe importante de implementação:** isso *não* usa o `sync_write_raw_goal_position` do rustypot. Ler o código gerado por macro mostra que a API raw escreve `values.to_le_bytes()` direto no barramento, enquanto a API de conversão aplica `to_be()` antes:

```rust
fn to_raw(value: f64) -> i16 { let a = (...) as i16; a.to_be() }
// sync_write_raw_*: values.iter().map(|v| v.to_le_bytes())   <- no to_be
```

Passar `451` emitiria, portanto, `0xC301` (49921). Em vez disso, o código usa `sync_write_goal_position` (radianos) e resolve os radianos que caem **exatamente** no valor raw desejado, tomando o ponto médio de cada passo raw para evitar erro de truncamento.

### 2.3 Alvos raw dos três botões

Adicionado `raw_positions` ao `data/config.yaml` (índice 0 → ID de servo 1):

```yaml
raw_positions:
  open:   [260, 760, 260, 760, 260, 760, 260, 760]
  close:  [760, 260, 760, 260, 760, 260, 760, 260]
  middle: [451, 571, 451, 571, 451, 571, 451, 571]
```

| Botão | Ação | IDs de servo 1–8 (raw) |
|---|---|---|
| ✋ Open All | totalmente estendida | 260, 760, 260, 760, 260, 760, 260, 760 |
| ✊ Close All | totalmente fechada | 760, 260, 760, 260, 760, 260, 760, 260 |
| ⊙ Center All | recentralização lateral (sem mudança em abrir/fechar) | — |
| **Middle position** | **retorno ao meio calibrado** | 451, 571, 451, 571, 451, 571, 451, 571 |

> ⚠️ Os `raw_positions` são **valores de calibração por mão**. O próprio comentário do fabricante é *"replace values by your calibration results"* — meça novamente ao trocar de mão ou de servo.

### 2.4 O trade-off da sincronização dos controles deslizantes

Os alvos raw contornam o modelo `base/side`, então não têm equivalente exato nos controles deslizantes. Depois que um botão é executado, os controles deslizantes são definidos para o inteiro mais próximo:

| Posição | O controle deslizante mostra |
|---|---|
| open | base = −73, side = 0 |
| close | base = +73, side = 0 |
| middle | base = −17, side = 0 |

O custo: tocar em um controle deslizante depois move a mão em até ~1 unidade raw (0,3°) para longe do alvo. Isso é proposital — atingir a posição calibrada com exatidão importa mais.

---

## 3. Novo botão de posição central

Colocado à direita de `✋ Open All` / `✊ Close All` / `⊙ Center All`. Ele retorna a mão ao **meio mecânico calibrado pelo fabricante** (raw 451/571).

**Por que é necessário:** o ponto médio entre `open_all` e `close_all` *não* é o meio mecânico. O meio do fabricante é o `MiddlePos`, que fica a ±60 raw (±17,6°) do raw 511. Após ligar, você quer um zero bem definido e repetível.

---

## 4. GUI e CLI em discordância (o bug central)

### 4.1 Sintoma

**A mesma pose produz um movimento diferente na mão quando aplicada com o `✓ Apply` da GUI versus o `--pose` da CLI.**

### 4.2 Causa raiz

A GUI aplicava as poses por:

```
set_positions(p1, p2)  →  decompose into (base, side), stored in the sliders
                       →  get_positions() recomputes via compute_auto_positions() in Auto mode
```

Mas `compute_auto_positions` **não** é um inverso exato de `decompose_servo_positions` (seu centro e seus extremos são valores empíricos). O `apply_pose()` da CLI envia os valores diretamente.

Medição: **12 das 19 poses estavam distorcidas**, em até 32°:

| Pose | Armazenada | A GUI realmente enviou | Desvio |
|---|---|---|---|
| `ring_close` | Ring `(75, -35)` | Ring `(43, -5)` | **32° / 30°** |
| `middle_close` | Middle `(75, -35)` | Middle `(43, -5)` | **32° / 30°** |
| `pointer_close` | Pointer `(75, -35)` | Pointer `(43, -5)` | **32° / 30°** |
| `thumb_close` | Thumb `(75, -35)` | Thumb `(43, -5)` | **32° / 30°** |
| `wave1` | `(-75, -3)` | `(-75, 9)` | 12° |
| `hifive` | Thumb `(-75, -3)` | Thumb `(-75, 9)` | 12° |
| `greeting` | Ring `(-18, -57)` | Ring `(-10, -68)` | 8° / 11° |
| `victory` | Middle `(-68, -9)` | Middle `(-75, 1)` | 7° / 10° |
| `paper` | Pointer `(-52, -22)` | Pointer `(-59, -16)` | 7° / 6° |
| `ok` | Pointer `(36, 46)` | Pointer `(38, 43)` | 2° / 3° |

**O padrão:** poses simétricas em que cada dedo tem `pos1 == pos2` (`open` `close` `stone` `two` `scissors` `one` `three`) fazem a ida e volta exata. Toda pose assimétrica que envolve dispersão lateral sofre desvio.

### 4.3 Correção

Adicionado `_send_exact_positions()`, que envia os ângulos direto aos servos na ordem de `SERVO_PAIRS` (equivalente ao `apply_pose` da CLI). Agora os dois pontos de entrada de pose usam isso:

- o botão `✓ Apply` em Pose Management
- `_apply_pose_from_config()` — o reprodutor de sequências e a lista de poses

Os controles deslizantes ainda são atualizados por `set_positions()` para exibição, mas **não decidem mais o que é enviado**.

### 4.4 Resultado

Após a correção, **todas as 19 poses satisfazem `stored == GUI-sent == CLI-sent`**.

**Efeito colateral:** os gestos reais na GUI mudam, sobretudo os assimétricos. Esse é o efeito pretendido da correção.

---

## 5. Correções dos dados de pose

### 5.1 Quatro poses `*_close` estavam escritas erradas

```yaml
# Before — target finger (75, -35)
ring_close:    [75, -35, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, -35, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, -35, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, -35]
```

`(75, -35)` decompõe para `base = 20, side = -55` (fora de faixa) — ou seja, *"só 27% curvado, girado com força para a esquerda"*, e não "fechar este dedo". Correspondendo a `close` e `one`, a forma correta é `(75, 75)`:

```yaml
# After — target finger fully closed (75, 75), others stay open (-35, -35)
ring_close:    [75, 75, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, 75, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, 75, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, 75]
```

Verificado por decomposição: dedo alvo com `base = 75` (totalmente fechado), `side = 0` (nem para um lado nem para o outro).

**Impacto:** a sequência `finger_roll`, que usa essas quatro, só agora é de fato um "role cada dedo por vez".

### 5.2 O polegar em `greeting` / `paper`

As duas originalmente tinham o polegar em `(75, 75)` (totalmente fechado). Para `paper` (布, uma palma plana aberta) um polegar fechado está claramente errado.

`greeting` foi primeiro alterada para `(-75, -3)` (reutilizando o polegar aberto de `hifive`), mas o teste no hardware mostrou que aquela etapa exigia que o polegar percorresse **150°**, o que não cabe em 1,0 s (veja 6.3). Estado final:

```yaml
greeting: [-18, -57, -32, -32, -70, -7, -35, -35]   # thumb (-35, -35), same as open
paper:    [-19, -56, -34, -34, -52, -22, -75, -3]   # keeps the splayed thumb (flat palm)
```

Isso separa os dois gestos: `greeting` é um aceno, em que o polegar apenas abre naturalmente; `paper` é uma palma plana, em que o polegar se abre lateralmente.

---

## 6. Reprodutor de sequências: temporização e diagnóstico

### 6.1 Corrigindo falsos avisos de "did not reach target"

Executar `demo` no hardware produziu três alarmes falsos:

```
⚠ Pose #42 'greeting': Servos did not reach target! Max error: 52°
```

**Causa raiz:** `_log_pose_completion` subtraía dois arrays que estavam em **ordens diferentes**.

- `monitor_servos()` grava seu cache na **ordem de ID de servo**: `latest_actual_positions[servo_id - 1] = ...` (índice 0 = ID1 = Pointer)
- os `target_positions` passados são um array de pose, na **ordem dos widgets** anelar / médio / indicador / polegar (índice 0 = anelar = ID5)

Então estava subtraindo a leitura do indicador da meta do anelar.

**Evidência** (recalculando a partir do log medido):

```
target (widget order)   : [-18, -57, -32, -32, -70, -7, -75, -3]
actual (servo-ID order) : [-68.85, -6.74, -33.69, -31.35, -18.46, -54.79, -74.12, -3.22]
compared as-is          -> max error 52°      <-- what the old code did
target reordered        : [-70, -7, -32, -32, -18, -57, -75, -3]
compared in servo order -> max error 2.21°    <-- actually spot on
```

**Correção:** adicionados `pose_to_servo_order()` / `servo_to_pose_order()`, aplicados antes da comparação; o `current` impresso é convertido de volta, para que `target` e `current` fiquem alinhados coluna a coluna no log.

### 6.2 Corrigindo quando a verificação de alcance é executada

O original verificava **2000 ms fixos** após o envio:

```python
self.root.after(2000, lambda ...: self._log_pose_completion(...))
```

Mas as etapas de sequência só esperam 1,0 s, então, na hora em que a verificação rodava, a próxima etapa já tinha sido enviada — a leitura pertence necessariamente ao movimento *seguinte*:

```
25.388  Pose #40 'ok'      sent
26.782  Pose #41 'victory' sent        <- already moved on
27.742  Pose #40 'ok'      checked -> reading is mid-way to victory
```

**Correção:**

1. `_apply_pose_from_config` ganhou um parâmetro `check_after`. Clicar em `✓ Apply` para uma única pose permanece inalterado (2,0 s e depois espera o movimento parar); a reprodução de sequência passa **o próprio atraso da etapa**, então a verificação cai no limite da etapa (atraso − 100 ms) e não espera mais pelo movimento.
2. Adicionada uma **proteção de substituição**: `_log_pose_start` registra `current_pose_id`; se um comando mais novo assumiu o controle desde então, a verificação de alcance é ignorada e o log mostra `current=<superseded>`.

### 6.3 Ajuste dos atrasos das sequências

**Velocidade efetiva** calculada de trás para frente a partir do log do hardware (velocidade 3 é nominalmente 172°/s):

| Pose | Curso | Erro em 0,9 s | Velocidade efetiva implícita |
|---|---|---|---|
| `ok` | 110° | 0,5° | 121,7°/s (71% do nominal) |
| `victory` | 110° | 1,0° | 121,1°/s (70%) |
| `greeting` | 132° | 7,0° | 138,9°/s (81%) |

> Sob carga, a velocidade real é de apenas cerca de **70%** do nominal. Esse é o número que importa ao escolher os atrasos.

**Alterações em `demo`:**

```yaml
  demo:
    steps:
    - open:3,3,3,3,3,3,3,3|2.0s
    - close:6,6,6,6,6,6,6,6|2.0s
    - ok:3,3,3,3,3,3,3,3|1.0s
    - victory:3,3,3,3,3,3,3,3|1.0s
    - greeting:3,3,3,3,3,3,3,3|1.5s      # was 1.0s
    - close:6,6,6,6,6,6,6,6|2.0s         # new: settle back into a fist
```

- `greeting` 1,0 s → **1,5 s**: essa etapa percorre 132° (segundo servo do anelar) e não consegue terminar em 1,0 s
- **novo `close` final**: para que `demo` termine com a mão fechada, o que também torna o loop limpo
- tempo total de execução 7,0 s → **9,5 s**

### 6.4 `wave`: limitando o balanço lateral a ±30°

A `wave_r` / `wave_l` original implicava um `side` de **±36** (além do limite de ±35, então estava sendo limitado a 35).

Resolvendo `side = base − pos1`, `base = (pos1 + pos2) / 2`, obtém-se `pos1 = base − side`, `pos2 = base + side`. Mantendo `base = −39` e reduzindo `side` para ±30:

```yaml
wave_r: [-9, -69, -9, -69, -9, -69, -69, -9]     # was [-3, -75, -3, -75, -3, -75, -75, -3]
wave_l: [-69, -9, -69, -9, -69, -9, -9, -69]     # was [-75, -3, -75, -3, -75, -3, -3, -75]
```

Verificado: `wave_r` tem side `[-30, -30, -30, +30]`, e `wave_l` é seu espelho por dedo.

**Efeito colateral (esperado):** o curso de cada balanço também cai de 40°/72° para **34°/60°**. A onda fica mais estreita no geral, o que só aumenta a margem de temporização.

---

## 7. Nova linha de posição raw no feedback dos servos

Uma linha **`Current (0-1023)`** fica logo abaixo de `Position (°)`, mostrando a posição raw dos servos ao vivo.

```
1. Goal (°)
2. Position (°)
3. Current (0-1023)      <== new
4. Speed (°/s)
5. Torque (%)
6. Voltage (V)
7. Current (mA)
8. Temperature (°C)
9. Status
10. Moving
```

**Trade-off:** nenhuma leitura serial extra. O valor raw é derivado da posição que a thread de monitoramento **já** leu, então o loop de polling não dobra seu tráfego serial. A precisão foi verificada de forma exaustiva: **2048 combinações (raw 0–1023 × servo ímpar/par) fazem ida e volta com erro zero**.

**Uso:** compare diretamente com a calibração do fabricante — `open` deve ler `260 / 760` alternadamente, `middle` deve ler `451 / 571`.

> O nome da linha traz um prefixo de faixa para distingui-la do `Current (mA)` existente (consumo de corrente estimado).

---

## 8. Suporte a mão esquerda e direita

### 8.1 O fabricante fornece dois firmwares

O fabricante fornece um demo Arduino separado por mão, com parâmetros completamente diferentes:

| | Direita `Amazing_RHand_Demo` | Esquerda `Amazing_LHand_Demo` |
|---|---|---|
| IDs de servo | **1–8** | **11–18** |
| Dedo → ID | indicador `1,2` / médio `3,4` / anelar `5,6` / polegar `7,8` | **anelar `11,12` / médio `13,14` / indicador `15,16` / polegar `17,18`** |
| `MiddlePos` do médio | `[451, 571, 451, 571, …]` | `[571, 451, 571, 451, …]` |

O tutorial de depuração diz claramente: *"a single hand uses 8 servos; the right hand's IDs must be set to 1-8, and the left hand's to 11-18."*

Observe que a numeração da mão esquerda segue **na ordem inversa** (anelar primeiro) — acompanhando seu layout mecânico espelhado.

### 8.2 Por que mudar os IDs não é suficiente

Os IDs são apenas a primeira camada. Restam duas diferenças físicas entre as mãos, e negligenciar qualquer uma delas distorce os gestos.

#### Diferença 1: um deslocamento de montagem de 35,16°

As duas mãos usam **o mesmo valor de gesto mais o próprio `MiddlePos`**:

```c
// Right
#define MiddlePos {451, 571, ...}
Move_Index(-35, 35)  →  ID1 = 451 + (-35)/0.293 = 331.5

// Left
#define MiddlePos {571, 451, ...}
Move_Index(-35, 35)  →  ID15 = 571 + (-35)/0.293 = 451.5
```

O mesmo gesto "open" cai em valores raw diferentes em cada mão. Convertidos para o espaço de ângulos deste programa, eles diferem em **120 raw = 35,16°**.

#### Diferença 2: os dois servos de um dedo estão trocados

```c
// Right Victory                      // Left Victory
Move_Index (-15, 65);                Move_Index (-65, 15);
Move_Middle(-65, 15);                Move_Middle(-15, 65);
```

Por dedo, `(a, b) → (-b, -a)`; em valores de pose, isso significa **trocar os dois números de cada dedo**.

Se você não fizer isso, a **direção da dispersão se inverte** — o sintoma é um sinal de V colapsando seus dois dedos enquanto os dedos que deveriam estar juntos se separam.

> Uma leitura equivocada fácil: em `Perfect` os valores de indicador e médio são **idênticos** nas duas mãos (`(50,-50)`, `(0,0)`), e apenas o polegar difere. Então a regra não é "trocar indicador e médio", mas um `(-b,-a)` por dedo — que é a identidade para pares simétricos.

### 8.3 Implementação

**As duas mãos compartilham um único `hand_config.yaml`.** As poses armazenadas estão sempre na **ordem da mão direita**; a mão esquerda converte na saída e na volta, de modo que não há uma segunda biblioteca de poses a manter.

A conversão fica em `hand_logic.py`:

| Função | Finalidade |
|---|---|
| `resolve_hand_config(app_config, hand)` | Sobrepõe `hands.<name>` à configuração de nível superior (da mão direita) |
| `servo_pairs()` / `servo_ids()` | Os `(servo1_id, servo2_id)` daquela mão por dedo / todos os IDs de servo em ordem crescente |
| `hand_angle_offset()` / `hand_mirrors_pose()` | Leem os dois parâmetros de diferença da mão |
| `adapt_pose_for_hand(positions, mirror)` | Troca o `(pos1, pos2)` de cada dedo. **A troca é seu próprio inverso**, então a mesma função converte ao aplicar e converte de volta ao salvar |

**Ligado em:**

- GUI: aplicação de pose (o botão `✓ Apply` e a reprodução de sequência) e salvamento de pose
- CLI: `--pose` / `--sequence`

**Os alvos raw dos três botões globais** são configurados por mão e não passam por essa conversão (`raw_positions` é gravado sob `hands.left`).

### 8.4 Uso

A GUI pergunta antes de abrir:

```
  AmazingHand — which hand?
    1 = right hand  (servo IDs 1-8)
    2 = left hand   (servo IDs 11-18)
  Enter 1 or 2 [1]:
  LEFT hand — servo IDs 11-18
    Ring (11, 12)  Middle (13, 14)  Pointer (15, 16)  Thumb (17, 18)
    middle position raw: [571, 451, 571, 451, 571, 451, 571, 451]
```

Pressionar Enter usa o valor de `hand:` de `config.yaml`. Para pular o prompt:

```bash
python amazing_hand_gui.py --hand left
python amazing_hand_cmd.py --pose victory --hand left
```

### 8.5 Checklist da primeira vez para a mão esquerda

Em `hands.left.raw_positions`, apenas **middle** é o padrão do fabricante (`571, 451`); `open` e `close` foram derivados do demo do fabricante:

| Botão | Raw da mão esquerda | Origem |
|---|---|---|
| Middle position | `571, 451, …` | Padrão do fabricante |
| Open All | `380, 642, …` | Derivado: o mesmo gesto que o Open All da mão direita, aplicado ao `MiddlePos` da esquerda |
| Close All | `880, 142, …` | Idem |

**Verifique-os nesta ordem na primeira vez que conectar a mão esquerda:**

1. Pressione **Middle position** e confirme que a linha `Current (0-1023)` lê `571, 451, 571, 451, …`
2. Pressione **Open All** / **Close All** — o curso deve atingir os batentes sem travar
3. Experimente `victory` (indicador e médio abrindo em V), `greeting` (três dedos juntos), `ok` (pontas do polegar e do indicador se encontrando)

Se algo estiver errado:

| Sintoma | Alteração |
|---|---|
| Middle position lê errado | `hands.left.raw_positions.middle` |
| Direção da dispersão invertida | defina `hands.left.mirror_pose` como `false` |
| Curso curto ou longo demais | `hands.left.raw_positions.open` / `close` |

### 8.6 Se a sua mão esquerda estiver numerada 1-8

Algumas pessoas renumeram os servos da mão esquerda para 1–8. Nesse caso, só `hands.left.servos` precisa mudar:

```yaml
hands:
  left:
    servos:
      # Renumbered following the vendor's left-hand order: ring first
      ring:    [1, 2]
      middle:  [3, 4]
      pointer: [5, 6]
      thumb:   [7, 8]
      all_ids: [1, 2, 3, 4, 5, 6, 7, 8]
```

> `angle_offset` e `mirror_pose` **não mudam** — eles descrevem a construção mecânica, não a numeração dos IDs. A inversão dos servos pares também continua valendo, porque o par de cada dedo mantém "ID ímpar primeiro".

---

## 9. Detecção automática de porta serial

### 9.1 O problema

O original tinha a lista de portas do Windows fixa no código, de `COM1` a `COM20`:

```python
available_ports = [f'COM{i}' for i in range(1, 21)]
```

Mas um adaptador pode cair em qualquer número de porta (nesta máquina foi medido `COM243`). O resultado: **sua porta simplesmente não aparece no menu suspenso**, e a conexão automática recorre a um padrão configurado que não existe, falhando com "the system cannot find the file specified".

### 9.2 Correção

Adicionado `available_serial_ports()`, com fallback em etapas:

1. `list_ports.comports()` do pyserial (usado quando instalado — informação mais rica)
2. Windows sem pyserial: leitura da chave de registro `HARDWARE\DEVICEMAP\SERIALCOMM` (**apenas biblioteca padrão**, sem nova dependência)
3. Linux/macOS: glob de `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`, `/dev/cu.usb*`
4. Só se tudo acima falhar, recorre à lista de candidatos original

As portas são ordenadas de forma **natural**, então `COM2` vem antes de `COM10`.

### 9.3 Alterações de apoio

- O menu suspenso passou de `readonly` para **editável** — você pode digitar uma porta quando a detecção não a encontra
- Se o padrão configurado não estiver presente, a GUI **inicia na primeira porta que existe de fato** em vez de tentar um padrão que não está lá
- **Um `--port` explícito nunca é sobrescrito** por esse fallback (acompanhado via `port_was_explicit`)

---

## 10. Referência de configuração

### `data/config.yaml`

Os `servos` / `auto_extremes` / `raw_positions` de nível superior descrevem a **mão direita** e servem como padrões; `hands.<name>` os sobrepõe chave a chave.

```yaml
hand: right           # active hand: right | left (the GUI asks; --hand skips it)

limits:
  servo_min: -75      # absolute lower travel limit
  servo_max: 75       # absolute upper travel limit
  base_min: -75       # open/close slider range (-75 = fully open)
  base_max: 75        #                          ( 75 = fully closed)
  side_min: -35       # left/right slider range
  side_max: 35

auto_extremes:        # servo positions at the side slider's extremes — right hand
  left_open:  [32, -35]
  right_open: [-35, 32]
  left_closed:  [75, 75]
  right_closed: [75, 75]

raw_positions:        # global buttons' raw targets — right hand (index 0 → servo ID 1)
  open:   [260, 760, ...]
  close:  [760, 260, ...]
  middle: [451, 571, ...]

hands:
  left:               # overrides for the left hand; only list what differs
    servos:
      ring:    [11, 12]
      middle:  [13, 14]
      pointer: [15, 16]
      thumb:   [17, 18]
    raw_positions:    # index 0 → servo ID 11
      open:   [380, 642, ...]
      close:  [880, 142, ...]
      middle: [571, 451, ...]
    angle_offset: -35.16   # mounting offset (see 8.2)
    mirror_pose: true      # per-finger servo swap (see 8.2)
```

`auto_extremes` é **compartilhado** pelas duas mãos — o controle deslizante lateral se comporta igual no espaço de poses; uma mão espelhada simplesmente se abre para o outro lado fisicamente.

### `data/hand_config.yaml`

Os 8 valores de uma pose estão ordenados como **anelar, médio, indicador, polegar** (pares de servos `(5,6) (3,4) (1,2) (7,8)`), **não** por ID de servo.

**Este arquivo é compartilhado pelas duas mãos e sempre armazenado na ordem da mão direita.** A mão esquerda troca o par de cada dedo ao aplicar e troca de volta ao salvar.

> ⚠️ A docstring no topo de `amazing_hand_cmd.py` afirma "index 0→servo1 … 7→servo8". Esse comentário está **errado**; a ordem acima é o que o código realmente faz.

---

## 11. Resultados medidos

### Precisão de alcance (após as correções)

| Pose | Meta | Real | Erro máx. |
|---|---|---|---|
| `open` | todos −35 | −36,6 … −33,4 | ≤1,6° |
| `close` | todos 75 | 74,7 … 75,3 | ≤0,3° |
| `ok` | — | — | 0,5° |
| `victory` | — | — | 1,0° |
| `greeting` | — | — | 2,2° |

### Verificações de conversão

```
raw -> degrees -> raw: 2048 combinations, zero error
open    raw [260, 760] -> back [260, 760]
middle  raw [451, 571] -> back [451, 571]
close   raw [760, 260] -> back [760, 260]
```

### Problemas conhecidos remanescentes

- **`ok` e `victory` em `demo` quase não têm margem de temporização** (+0,01 s pela velocidade medida). No momento, passam só porque a tolerância de < 5° os captura. Uma queda na tensão da bateria, uma mudança de temperatura ou uma mão um pouco mais rígida poderia estourá-la. Aumentar os dois atrasos de 1,0 s para 1,2 s é o próximo passo óbvio.
- **`scissors` é idêntica byte a byte a `two`**, e **`stone` é idêntica byte a byte a `close`**. Semanticamente tudo bem (scissors = dois dedos, stone = punho), mas literalmente duplicadas, e não foram limpas.
- **Os controles deslizantes ainda mantêm um erro de representação de ~0,3°** em relação aos alvos raw (veja 2.4).
- **`config.yaml` e o `default_config` de `hand_logic.py` estão dessincronizados.** Este último ainda carrega a escala original (`servo_min: -40` etc.); ele só é usado quando falta o `config.yaml`. O teste `test_hand_logic.py::TestAngleLimits::test_defaults` afirma exatamente aqueles padrões antigos.

---

## 12. Resumo arquivo por arquivo

| Arquivo | Alterações |
|---|---|
| `hand_logic.py` | Novas constantes de conversão do SCS0009; `raw_to_degrees` / `raw_to_radians` / `degrees_to_raw` / `pose_to_servo_order` / `servo_to_pose_order`; formato de exibição `raw_position`; padrões de `raw_positions`; **suporte a mãos** (`HAND_NAMES` / `DEFAULT_HAND_SERVOS` / `resolve_hand_config` / `servo_pairs` / `servo_ids` / `hand_angle_offset` / `hand_mirrors_pose` / `adapt_pose_for_hand`); **`available_serial_ports()`**; E/S do arquivo de configuração trocada para **UTF-8** (usava o padrão GBK do Windows e travava com comentários não ASCII) |
| `amazing_hand_gui.py` | Novos `_apply_raw_hand_position` / `middle_all` / `_send_exact_positions`; reescritos `open_all` / `close_all` / `_apply_pose_from_config` / `_log_pose_completion`; novo botão **Middle position**; nova linha de posição raw no Servo Feedback; `self.app_config` promovido a atributo de instância; removido o `latest_goal_positions` não usado e unificada a ordem de escrita de `feedback_data['goal']`; **seleção de mão na inicialização + `--hand`**; **8 `range(1,9)` fixos no código substituídos pelos IDs reais da mão**; o título da janela mostra a mão ativa; deslocamento de ângulo e conversão de espelhamento ligados em todos os caminhos de pose; **o menu suspenso de porta agora lista as portas detectadas e aceita entrada digitada** |
| `amazing_hand_cmd.py` | Novo `--hand`; `connect` / `apply_pose` / `wait_for_motion` / desligar o torque na saída agora usam os IDs reais da mão; os caminhos de pose e sequência aplicam o deslocamento de ângulo e a conversão de espelhamento; leitura da configuração trocada para UTF-8 |
| `data/config.yaml` | `limits` / `auto_extremes` recalibrados; adicionado `raw_positions`; adicionados `hand` e um bloco de sobreposição `hands.left` |
| `data/hand_config.yaml` | Todas as 19 poses reescaladas; as quatro poses `*_close` corrigidas; polegar de `greeting` / `paper` corrigido; balanço de `wave_r` / `wave_l` reduzido para ±30; `demo` ganhou um atraso maior em `greeting` e uma nova etapa de fechamento |
| `pyproject.toml` | `build-backend` corrigido (`setuptools.backends.legacy:build` → `setuptools.build_meta`) |

### Glossário

| Termo | Significado |
|---|---|
| **Modo Auto** | Dois controles deslizantes — "base" (abrir/fechar) e "side" (lateral) — acionam indiretamente os dois servos de um dedo |
| **Modo Raw** | Os dois ângulos de servo de um dedo são controlados diretamente |
| **base** | Quantidade de abertura/fechamento, `(pos1 + pos2) / 2` |
| **side** | Deslocamento lateral, `base − pos1` |
| **raw** | A unidade interna de posição do servo: 0–1023 ao longo de 300°, centro 511 |
| **MiddlePos** | A calibração de meio por servo do firmware do fabricante; difere entre as mãos (veja 8.1) |
| **angle_offset** | O deslocamento de montagem de 35,16° entre as mãos (veja 8.2) |
| **mirror_pose** | A troca do par de servos por dedo na mão esquerda (veja 8.2) |
