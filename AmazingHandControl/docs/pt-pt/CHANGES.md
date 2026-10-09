[English](../en/CHANGES.md) | [Deutsch](../de/CHANGES.md) | [Español](../es/CHANGES.md) | [Français](../fr/CHANGES.md) | [Italiano](../it/CHANGES.md) | [日本語](../ja/CHANGES.md) | [한국어](../ko/CHANGES.md) | [Português (BR)](../pt-br/CHANGES.md) | Português (PT) | [简体中文](../zh-hans/CHANGES.md) | [繁體中文](../zh-hant/CHANGES.md)

# Controlador AmazingHand · Registo de alterações e justificação

O que foi alterado em relação ao projeto original, porquê, e qual é de facto o resultado.

Projeto original: `Betatester777/AmazingHandControl` (GUI + CLI em Python para o AmazingHand)
Hardware: JuxiTechnology AmazingHand (8× servos Feetech SCS0009, feedback por potenciómetro) — **ambas as mãos suportadas**, selecionadas no arranque

---

## Conteúdo

1. [Recalibração do sistema de ângulos](#1-recalibração-do-sistema-de-ângulos)
2. [Botões globais: comandar posições raw exatas](#2-botões-globais-comandar-posições-raw-exatas)
3. [Novo botão de posição intermédia](#3-novo-botão-de-posição-intermédia)
4. [GUI e CLI em desacordo (o bug central)](#4-gui-e-cli-em-desacordo-o-bug-central)
5. [Correções dos dados de pose](#5-correções-dos-dados-de-pose)
6. [Reprodutor de sequências: temporização e diagnóstico](#6-reprodutor-de-sequências-temporização-e-diagnóstico)
7. [Nova linha de posição raw no feedback dos servos](#7-nova-linha-de-posição-raw-no-feedback-dos-servos)
8. [**Suporte a mão esquerda e direita**](#8-suporte-a-mão-esquerda-e-direita)
9. [Deteção automática de porta série](#9-deteção-automática-de-porta-série)
10. [Referência de configuração](#10-referência-de-configuração)
11. [Resultados medidos](#11-resultados-medidos)
12. [Resumo ficheiro a ficheiro](#12-resumo-ficheiro-a-ficheiro)

---

## 1. Recalibração do sistema de ângulos

### 1.1 Limites de ângulo: `0..110` → `-75..75`

O original estava calibrado como `0° = aberto, 110° = fechado`. O curso real desta mão situa-se em `-75..75`, pelo que tudo foi recalibrado.

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

**Todas as 19 poses foram reescaladas**, p. ex. `open` de `[0]*8` para `[-35]*8`, `close` de `[110]*8` para `[75]*8`.

### 1.2 Dispersão lateral: `±40°` → `±35°`

O controlo deslizante lateral normaliza com `u = |side_offset| / |side_min|`, pelo que alterar apenas o limite **não** muda a distância a que os dedos se abrem efetivamente — limita-se a reescalar o controlo deslizante. Para alterar a dispersão física é também preciso alterar `auto_extremes`. Com ambos alterados:

| | Antes (±40) | Depois (±35) |
|---|---|---|
| Intervalo do controlo deslizante | −40 … +40 | −35 … +35 |
| Totalmente aberto, no extremo lateral | `(32, -40)`, dispersão **72°** | `(32, -35)`, dispersão **67°** |

### 1.3 Correspondência com a referência do fabricante

A demonstração Arduino do fabricante (`Amazing_RHand_Demo.ino`) converte assim:

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

**Conclusão: ambos os lados usam a mesma escala em graus** (0,29297°/passo, escala completa de 300°, raw 0–1023) — não há erro de proporção. A única diferença sistemática é o ponto zero:

- o rustypot centra sempre em raw **511**
- o firmware do fabricante usa um valor de calibração por servo, `MiddlePos = {451, 571, 451, 571, 451, 571, 451, 571}`

Diferem em **±60 raw = ±17,6°**. É exatamente isso que o botão "Middle position" abaixo resolve.

---

## 2. Botões globais: comandar posições raw exatas

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

Esses valores provêm da **escala de calibração antiga** (0 = aberto, 110 = fechado). Após recalibrar para `-35 / 75`:

- o `open_all` definia 0° → converte para raw **511**, ou seja, aproximadamente o meio mecânico — os dedos nunca abriam
- o `close_all` definia 110° → limitado por `base_max = 75`, pelo que só atingia 75, embora a etiqueta continuasse a indicar 110°

### 2.2 A correção: um caminho direto para a posição raw

O caminho por ângulos passa pelo modelo de interpolação `base/side`, que não consegue atingir exatamente um valor raw arbitrário (ver secção 4). Por isso, os botões globais passaram a ter um caminho que escreve diretamente as posições raw dos servos.

**Um detalhe de implementação importante:** isto *não* usa o `sync_write_raw_goal_position` do rustypot. A leitura do código gerado por macros mostra que a API raw escreve `values.to_le_bytes()` diretamente no barramento, enquanto a API de conversão aplica primeiro `to_be()`:

```rust
fn to_raw(value: f64) -> i16 { let a = (...) as i16; a.to_be() }
// sync_write_raw_*: values.iter().map(|v| v.to_le_bytes())   <- no to_be
```

Assim, passar `451` emitiria `0xC301` (49921). Em vez disso, o código usa `sync_write_goal_position` (radianos) e resolve os radianos que caem **exatamente** no valor raw alvo, tomando o ponto médio de cada passo raw para evitar erros de truncatura.

### 2.3 Alvos raw dos três botões

Foi adicionado `raw_positions` a `data/config.yaml` (índice 0 → ID de servo 1):

```yaml
raw_positions:
  open:   [260, 760, 260, 760, 260, 760, 260, 760]
  close:  [760, 260, 760, 260, 760, 260, 760, 260]
  middle: [451, 571, 451, 571, 451, 571, 451, 571]
```

| Botão | Ação | Servos IDs 1–8 raw |
|---|---|---|
| ✋ Open All | totalmente estendida | 260, 760, 260, 760, 260, 760, 260, 760 |
| ✊ Close All | totalmente fechada | 760, 260, 760, 260, 760, 260, 760, 260 |
| ⊙ Center All | recentragem lateral (sem alterar abrir/fechar) | — |
| **Middle position** | **regressar ao meio calibrado** | 451, 571, 451, 571, 451, 571, 451, 571 |

> ⚠️ `raw_positions` são **valores de calibração por mão**. O próprio comentário do fabricante é *"replace values by your calibration results"* — volte a medir depois de trocar de mão ou de servos.

### 2.4 O compromisso da sincronização dos controlos deslizantes

Os alvos raw ignoram o modelo `base/side`, pelo que não têm um equivalente exato nos controlos deslizantes. Depois de um botão ser executado, os controlos deslizantes são definidos para o número inteiro mais próximo:

| Posição | O controlo deslizante mostra |
|---|---|
| open | base = −73, side = 0 |
| close | base = +73, side = 0 |
| middle | base = −17, side = 0 |

O custo: tocar num controlo deslizante depois disso desloca a mão até ~1 unidade raw (0,3°) em relação ao alvo. Isto é intencional — atingir exatamente a posição calibrada é mais importante.

---

## 3. Novo botão de posição intermédia

Colocado à direita de `✋ Open All` / `✊ Close All` / `⊙ Center All`. Repõe a mão no **meio mecânico calibrado pelo fabricante** (raw 451/571).

**Porque é necessário:** o ponto médio entre `open_all` e `close_all` *não* é o meio mecânico. O meio do fabricante é `MiddlePos`, que fica a ±60 raw (±17,6°) do raw 511. Após ligar, pretende-se um zero bem definido e repetível.

---

## 4. GUI e CLI em desacordo (o bug central)

### 4.1 Sintoma

**A mesma pose produz um movimento diferente da mão quando aplicada com o `✓ Apply` da GUI versus o `--pose` da CLI.**

### 4.2 Causa raiz

A GUI aplicava as poses através de:

```
set_positions(p1, p2)  →  decompose into (base, side), stored in the sliders
                       →  get_positions() recomputes via compute_auto_positions() in Auto mode
```

Mas o `compute_auto_positions` **não** é um inverso exato de `decompose_servo_positions` (o seu centro e extremos são valores empíricos). O `apply_pose()` da CLI envia os valores diretamente.

Medido: **12 de 19 poses estavam distorcidas**, em até 32°:

| Pose | Armazenada | GUI enviou efetivamente | Desvio |
|---|---|---|---|
| `ring_close` | Anelar `(75, -35)` | Anelar `(43, -5)` | **32° / 30°** |
| `middle_close` | Médio `(75, -35)` | Médio `(43, -5)` | **32° / 30°** |
| `pointer_close` | Indicador `(75, -35)` | Indicador `(43, -5)` | **32° / 30°** |
| `thumb_close` | Polegar `(75, -35)` | Polegar `(43, -5)` | **32° / 30°** |
| `wave1` | `(-75, -3)` | `(-75, 9)` | 12° |
| `hifive` | Polegar `(-75, -3)` | Polegar `(-75, 9)` | 12° |
| `greeting` | Anelar `(-18, -57)` | Anelar `(-10, -68)` | 8° / 11° |
| `victory` | Médio `(-68, -9)` | Médio `(-75, 1)` | 7° / 10° |
| `paper` | Indicador `(-52, -22)` | Indicador `(-59, -16)` | 7° / 6° |
| `ok` | Indicador `(36, 46)` | Indicador `(38, 43)` | 2° / 3° |

**O padrão:** as poses simétricas em que cada dedo tem `pos1 == pos2` (`open` `close` `stone` `two` `scissors` `one` `three`) fazem ida e volta exata. Todas as poses assimétricas com dispersão lateral sofrem desvio.

### 4.3 Correção

Foi adicionado `_send_exact_positions()`, que envia os ângulos diretamente para os servos na ordem de `SERVO_PAIRS` (equivalente ao `apply_pose` da CLI). Ambos os pontos de entrada de poses passam agora a usá-lo:

- o botão `✓ Apply` da Gestão de Poses
- `_apply_pose_from_config()` — o reprodutor de sequências e a lista de poses

Os controlos deslizantes continuam a ser atualizados por `set_positions()` para visualização, mas **já não decidem o que é enviado**.

### 4.4 Resultado

Depois da correção, **todas as 19 poses satisfazem `stored == GUI-sent == CLI-sent`**.

**Efeito secundário:** os gestos reais na GUI alteram-se, especialmente os assimétricos. É esse o efeito pretendido da correção.

---

## 5. Correções dos dados de pose

### 5.1 Quatro poses `*_close` estavam escritas erradamente

```yaml
# Before — target finger (75, -35)
ring_close:    [75, -35, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, -35, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, -35, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, -35]
```

`(75, -35)` decompõe-se em `base = 20, side = -55` (fora do intervalo) — ou seja, *"apenas 27% encurvado, desviado fortemente para a esquerda"*, e não "fechar este dedo". Tal como `close` e `one`, a forma correta é `(75, 75)`:

```yaml
# After — target finger fully closed (75, 75), others stay open (-35, -35)
ring_close:    [75, 75, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, 75, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, 75, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, 75]
```

Verificado por decomposição: dedo alvo `base = 75` (totalmente fechado), `side = 0` (não desviado para nenhum lado).

**Impacto:** a sequência `finger_roll`, que usa estas quatro, só agora é um verdadeiro "rodar cada dedo por sua vez".

### 5.2 O polegar em `greeting` / `paper`

Ambas tinham originalmente o polegar em `(75, 75)` (totalmente fechado). Para `paper` (布, uma palma aberta e plana) um polegar fechado está manifestamente errado.

`greeting` foi primeiro alterada para `(-75, -3)` (reutilizando o polegar aberto de `hifive`), mas os testes no hardware mostraram que esse passo exigia que o polegar percorresse **150°**, o que não cabe em 1,0 s (ver 6.3). Estado final:

```yaml
greeting: [-18, -57, -32, -32, -70, -7, -35, -35]   # thumb (-35, -35), same as open
paper:    [-19, -56, -34, -34, -52, -22, -75, -3]   # keeps the splayed thumb (flat palm)
```

Isto separa os dois gestos: `greeting` é um aceno, em que o polegar simplesmente abre naturalmente; `paper` é uma palma plana, em que o polegar se abre.

---

## 6. Reprodutor de sequências: temporização e diagnóstico

### 6.1 Corrigir avisos falsos de "não atingiu o alvo"

Executar `demo` no hardware produziu três falsos alarmes:

```
⚠ Pose #42 'greeting': Servos did not reach target! Max error: 52°
```

**Causa raiz:** o `_log_pose_completion` subtraía dois arrays que estavam em **ordens diferentes**.

- `monitor_servos()` escreve a sua cache na **ordem dos IDs de servo**: `latest_actual_positions[servo_id - 1] = ...` (índice 0 = ID1 = Pointer)
- os `target_positions` passados são um array de pose, na **ordem dos widgets** Ring / Middle / Pointer / Thumb (índice 0 = Ring = ID5)

Assim, subtraía a leitura do Pointer do alvo do Ring.

**Prova** (recalculando a partir do registo medido):

```
target (widget order)   : [-18, -57, -32, -32, -70, -7, -75, -3]
actual (servo-ID order) : [-68.85, -6.74, -33.69, -31.35, -18.46, -54.79, -74.12, -3.22]
compared as-is          -> max error 52°      <-- what the old code did
target reordered        : [-70, -7, -32, -32, -18, -57, -75, -3]
compared in servo order -> max error 2.21°    <-- actually spot on
```

**Correção:** foram adicionadas `pose_to_servo_order()` / `servo_to_pose_order()`, aplicadas antes da comparação; o `current` impresso é reconvertido para que `target` e `current` fiquem alinhados coluna a coluna no registo.

### 6.2 Corrigir quando a verificação de alcance é executada

O original verificava **2000 ms fixos** após o envio:

```python
self.root.after(2000, lambda ...: self._log_pose_completion(...))
```

Mas os passos da sequência só esperam 1,0 s, pelo que, quando a verificação era executada, o passo seguinte já tinha sido enviado — a leitura pertence necessariamente ao movimento *seguinte*:

```
25.388  Pose #40 'ok'      sent
26.782  Pose #41 'victory' sent        <- already moved on
27.742  Pose #40 'ok'      checked -> reading is mid-way to victory
```

**Correção:**

1. O `_apply_pose_from_config` ganhou um parâmetro `check_after`. Clicar em `✓ Apply` para uma única pose mantém-se inalterado (2,0 s e depois espera que o movimento pare); a reprodução de uma sequência passa **o próprio atraso do passo**, pelo que a verificação cai no limite do passo (atraso − 100 ms) e já não espera pelo movimento.
2. Foi adicionada uma **proteção contra substituição**: o `_log_pose_start` regista `current_pose_id`; se um comando mais recente tiver entretanto assumido o controlo, a verificação de alcance é ignorada e o registo mostra `current=<superseded>`.

### 6.3 Afinação dos atrasos da sequência

**Velocidade efetiva** calculada a partir do registo do hardware (a velocidade 3 é nominalmente 172°/s):

| Pose | Curso | Erro a 0,9 s | Velocidade efetiva implícita |
|---|---|---|---|
| `ok` | 110° | 0,5° | 121,7°/s (71% do nominal) |
| `victory` | 110° | 1,0° | 121,1°/s (70%) |
| `greeting` | 132° | 7,0° | 138,9°/s (81%) |

> Sob carga, a velocidade real é apenas cerca de **70%** da nominal. É esse o número que importa ao escolher os atrasos.

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

- `greeting` 1,0 s → **1,5 s**: esse passo percorre 132° (segundo servo do anelar) e não consegue terminar em 1,0 s
- **novo `close` final**: para que o `demo` termine com a mão fechada, o que também torna o loop limpo
- duração total 7,0 s → **9,5 s**

### 6.4 `wave`: limitar o balanço lateral a ±30°

O `wave_r` / `wave_l` original implicava um `side` de **±36** (além do limite de ±35, pelo que estava a ser limitado a 35).

Resolvendo `side = base − pos1`, `base = (pos1 + pos2) / 2` obtém-se `pos1 = base − side`, `pos2 = base + side`. Mantendo `base = −39` e reduzindo `side` para ±30:

```yaml
wave_r: [-9, -69, -9, -69, -9, -69, -69, -9]     # was [-3, -75, -3, -75, -3, -75, -75, -3]
wave_l: [-69, -9, -69, -9, -69, -9, -9, -69]     # was [-75, -3, -75, -3, -75, -3, -3, -75]
```

Verificado: `wave_r` tem `side` `[-30, -30, -30, +30]`, e `wave_l` é o seu espelho por dedo.

**Efeito secundário (esperado):** o curso de cada balanço também desce de 40°/72° para **34°/60°**. A onda é globalmente mais estreita, o que só aumenta a margem de temporização.

---

## 7. Nova linha de posição raw no feedback dos servos

Uma linha **`Current (0-1023)`** fica diretamente abaixo de `Position (°)`, mostrando a posição raw ao vivo do servo.

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

**Compromisso:** sem leituras série adicionais. O valor raw é derivado da posição que a thread de monitorização **já** tinha lido, pelo que o ciclo de consulta não duplica o tráfego série. A precisão foi verificada exaustivamente: **2048 combinações (raw 0–1023 × servo ímpar/par) fazem ida e volta com erro zero**.

**Utilização:** compare diretamente com a calibração do fabricante — `open` deve ler `260 / 760` alternadamente, `middle` deve ler `451 / 571`.

> O nome da linha inclui um prefixo de intervalo para a distinguir do `Current (mA)` existente (consumo de corrente estimado).

---

## 8. Suporte a mão esquerda e direita

### 8.1 O fabricante disponibiliza dois firmwares

O fabricante fornece uma demonstração Arduino separada por mão, com parâmetros completamente diferentes:

| | Right `Amazing_RHand_Demo` | Left `Amazing_LHand_Demo` |
|---|---|---|
| IDs dos servos | **1–8** | **11–18** |
| Dedo → ID | indicador `1,2` / médio `3,4` / anelar `5,6` / polegar `7,8` | **anelar `11,12` / médio `13,14` / indicador `15,16` / polegar `17,18`** |
| Middle `MiddlePos` | `[451, 571, 451, 571, …]` | `[571, 451, 571, 451, …]` |

O tutorial de depuração diz claramente: *"a single hand uses 8 servos; the right hand's IDs must be set to 1-8, and the left hand's to 11-18."*

Repare que a numeração da mão esquerda corre **ao contrário** (anelar primeiro) — correspondendo à sua disposição mecânica espelhada.

### 8.2 Porque é que mudar os IDs não é suficiente

Os IDs são apenas a primeira camada. Subsistem duas diferenças físicas entre as mãos, e falhar qualquer uma delas distorce os gestos.

#### Diferença 1: um desvio de montagem de 35,16°

Ambas as mãos usam **o mesmo valor de gesto mais o seu próprio `MiddlePos`**:

```c
// Right
#define MiddlePos {451, 571, ...}
Move_Index(-35, 35)  →  ID1 = 451 + (-35)/0.293 = 331.5

// Left
#define MiddlePos {571, 451, ...}
Move_Index(-35, 35)  →  ID15 = 571 + (-35)/0.293 = 451.5
```

O mesmo gesto "abrir" cai em valores raw diferentes em cada mão. Convertidos para o espaço de ângulos deste programa, diferem em **120 raw = 35,16°**.

#### Diferença 2: os dois servos de um dedo estão trocados

```c
// Right Victory                      // Left Victory
Move_Index (-15, 65);                Move_Index (-65, 15);
Move_Middle(-65, 15);                Move_Middle(-15, 65);
```

Por dedo, `(a, b) → (-b, -a)`; em valores de pose isto significa **trocar os dois números de cada dedo**.

Se isto for ignorado, a **direção da dispersão inverte-se** — o sintoma é um sinal de V a colapsar os dois dedos enquanto os dedos que deviam estar juntos se separam.

> Uma leitura fácil de enganar: em `Perfect` os valores do indicador e do médio são **idênticos** em ambas as mãos (`(50,-50)`, `(0,0)`), e só o polegar difere. Portanto, a regra não é "trocar indicador e médio", mas sim um `(-b,-a)` por dedo — que é a identidade para pares simétricos.

### 8.3 Implementação

**As duas mãos partilham um único `hand_config.yaml`.** As poses armazenadas estão sempre na **ordem da mão direita**; a mão esquerda converte à saída e de volta, pelo que não há uma segunda biblioteca de poses a manter.

A conversão reside em `hand_logic.py`:

| Função | Objetivo |
|---|---|
| `resolve_hand_config(app_config, hand)` | Sobrepõe `hands.<name>` à configuração de nível superior (mão direita) |
| `servo_pairs()` / `servo_ids()` | Os `(servo1_id, servo2_id)` dessa mão por dedo / todos os IDs de servo por ordem crescente |
| `hand_angle_offset()` / `hand_mirrors_pose()` | Lê os dois parâmetros de diferença da mão |
| `adapt_pose_for_hand(positions, mirror)` | Troca `(pos1, pos2)` de cada dedo. **A troca é o seu próprio inverso**, pelo que a mesma função converte ao aplicar e reconverte ao guardar |

**Integrado em:**

- GUI: aplicação de poses (o botão `✓ Apply` e a reprodução de sequências) e gravação de uma pose
- CLI: `--pose` / `--sequence`

**Os alvos raw dos três botões globais** são configurados por mão e não passam por esta conversão (`raw_positions` é escrito em `hands.left`).

### 8.4 Utilização

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

Premir Enter usa o valor `hand:` de `config.yaml`. Para saltar a pergunta:

```bash
python amazing_hand_gui.py --hand left
python amazing_hand_cmd.py --pose victory --hand left
```

### 8.5 Lista de verificação inicial para a mão esquerda

Em `hands.left.raw_positions`, apenas **middle** é o padrão do fabricante (`571, 451`); `open` e `close` foram derivados da demonstração do fabricante:

| Botão | Raw da mão esquerda | Origem |
|---|---|---|
| Middle position | `571, 451, …` | Padrão do fabricante |
| Open All | `380, 642, …` | Derivado: o mesmo gesto que o Open All da mão direita, aplicado ao `MiddlePos` da esquerda |
| Close All | `880, 142, …` | O mesmo |

**Verifique-os por esta ordem na primeira vez que ligar a mão esquerda:**

1. Prima **Middle position** e confirme que a linha `Current (0-1023)` lê `571, 451, 571, 451, …`
2. Prima **Open All** / **Close All** — o curso deve atingir os batentes sem bloquear
3. Experimente `victory` (indicador e médio abrem em V), `greeting` (três dedos juntos), `ok` (pontas do polegar e do indicador a tocar)

Se algo estiver errado:

| Sintoma | Alteração |
|---|---|
| Middle position lê errado | `hands.left.raw_positions.middle` |
| Direção da dispersão invertida | definir `hands.left.mirror_pose` como `false` |
| Curso demasiado curto ou demasiado longo | `hands.left.raw_positions.open` / `close` |

### 8.6 Se a sua mão esquerda estiver numerada de 1 a 8

Algumas pessoas renumeram os servos da mão esquerda para 1–8. Nesse caso, só `hands.left.servos` precisa de ser alterado:

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

> O `angle_offset` e o `mirror_pose` **não mudam** — descrevem a construção mecânica, não a numeração dos IDs. A inversão dos servos pares também continua a aplicar-se, porque o par de cada dedo mantém "ID ímpar primeiro".

---

## 9. Deteção automática de porta série

### 9.1 O problema

O original tinha a lista de portas do Windows fixa em `COM1`–`COM20`:

```python
available_ports = [f'COM{i}' for i in range(1, 21)]
```

Mas um adaptador pode ficar em qualquer número de porta (nesta máquina mediu-se `COM243`). O resultado: **a sua porta está simplesmente ausente da lista pendente**, e a ligação automática recorre a um padrão configurado que não existe, falhando com "the system cannot find the file specified".

### 9.2 Correção

Foi adicionada `available_serial_ports()`, com recurso por etapas:

1. `list_ports.comports()` do pyserial (usado quando instalado — informação mais rica)
2. Windows sem pyserial: ler a chave de registo `HARDWARE\DEVICEMAP\SERIALCOMM` (**apenas biblioteca padrão**, sem nova dependência)
3. Linux/macOS: glob `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`, `/dev/cu.usb*`
4. Só se tudo o acima falhar, recorrer à lista de candidatos original

As portas são ordenadas de forma **natural**, pelo que `COM2` vem antes de `COM10`.

### 9.3 Alterações de suporte

- A lista pendente passou de `readonly` a **editável** — pode escrever uma porta quando a deteção falha
- Se o padrão configurado não estiver presente, a GUI **inicia na primeira porta que existe efetivamente**, em vez de tentar um padrão que não está lá
- **Um `--port` explícito nunca é substituído** por esse fallback (registado através de `port_was_explicit`)

---

## 10. Referência de configuração

### `data/config.yaml`

O `servos` / `auto_extremes` / `raw_positions` de nível superior descrevem a **mão direita** e servem de padrões; `hands.<name>` sobrepõe-se-lhes chave a chave.

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

O `auto_extremes` é **partilhado** por ambas as mãos — o controlo deslizante lateral comporta-se da mesma forma no espaço de poses; uma mão espelhada limita-se a abrir-se no sentido físico oposto.

### `data/hand_config.yaml`

Os 8 valores de uma pose estão ordenados por **Ring, Middle, Pointer, Thumb** (pares de servos `(5,6) (3,4) (1,2) (7,8)`), **e não** por ID de servo.

**Este ficheiro é partilhado por ambas as mãos e está sempre armazenado na ordem da mão direita.** A mão esquerda troca o par de cada dedo ao aplicar e volta a trocá-lo ao guardar.

> ⚠️ O docstring no topo de `amazing_hand_cmd.py` afirma "index 0→servo1 … 7→servo8". Esse comentário está **errado**; a ordenação acima é o que o código faz efetivamente.

---

## 11. Resultados medidos

### Precisão de alcance (após as correções)

| Pose | Alvo | Real | Erro máx. |
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

### Problemas pendentes conhecidos

- **`ok` e `victory` no `demo` quase não têm margem de temporização** (+0,01 s segundo a velocidade medida). Atualmente passam apenas porque a tolerância < 5° os apanha. Uma quebra na tensão da bateria, uma variação de temperatura ou uma mão ligeiramente mais rígida podem empurrá-los para lá do limite. Aumentar ambos os atrasos de 1,0 s para 1,2 s é o próximo passo óbvio.
- **`scissors` é idêntica byte a byte a `two`**, e **`stone` é idêntica byte a byte a `close`**. Semanticamente é aceitável (scissors = dois dedos, stone = punho), mas literalmente duplicada, e não foi limpa.
- **Os controlos deslizantes ainda têm um erro de representação de ~0,3°** em relação aos alvos raw (ver 2.4).
- **O `config.yaml` e o `default_config` de `hand_logic.py` estão dessincronizados.** Este último ainda traz a escala original (`servo_min: -40`, etc.); só é usado quando falta o `config.yaml`. O teste `test_hand_logic.py::TestAngleLimits::test_defaults` afirma exatamente esses valores antigos.

---

## 12. Resumo ficheiro a ficheiro

| Ficheiro | Alterações |
|---|---|
| `hand_logic.py` | Novas constantes de conversão do SCS0009; `raw_to_degrees` / `raw_to_radians` / `degrees_to_raw` / `pose_to_servo_order` / `servo_to_pose_order`; formato de apresentação de `raw_position`; padrões de `raw_positions`; **suporte de mãos** (`HAND_NAMES` / `DEFAULT_HAND_SERVOS` / `resolve_hand_config` / `servo_pairs` / `servo_ids` / `hand_angle_offset` / `hand_mirrors_pose` / `adapt_pose_for_hand`); **`available_serial_ports()`**; a I/O do ficheiro de configuração passou para **UTF-8** (usava o GBK predefinido do Windows e colapsava com comentários não ASCII) |
| `amazing_hand_gui.py` | Novos `_apply_raw_hand_position` / `middle_all` / `_send_exact_positions`; reescritos `open_all` / `close_all` / `_apply_pose_from_config` / `_log_pose_completion`; novo botão **Middle position**; nova linha de posição raw no Servo Feedback; `self.app_config` promovido a atributo de instância; removido o `latest_goal_positions` não utilizado e unificada a ordem de escrita de `feedback_data['goal']`; **seleção de mão no arranque + `--hand`**; **8 `range(1,9)` fixos no código substituídos pelos IDs reais da mão**; o título da janela mostra a mão ativa; desvio de ângulo e conversão de espelho ligados em todos os caminhos de pose; **a lista pendente de porta passa a listar as portas detetadas e aceita entrada escrita** |
| `amazing_hand_cmd.py` | Novo `--hand`; `connect` / `apply_pose` / `wait_for_motion` / desativação de binário à saída passam a usar os IDs reais da mão; os caminhos de pose e sequência aplicam o desvio de ângulo e a conversão de espelho; leitura da configuração passou para UTF-8 |
| `data/config.yaml` | `limits` / `auto_extremes` recalibrados; adicionado `raw_positions`; adicionado `hand` e um bloco de sobreposição `hands.left` |
| `data/hand_config.yaml` | Todas as 19 poses reescaladas; as quatro poses `*_close` corrigidas; polegar de `greeting` / `paper` corrigido; balanço de `wave_r` / `wave_l` reduzido para ±30; o `demo` recebeu um atraso `greeting` maior e um novo passo de fecho |
| `pyproject.toml` | Corrigido o `build-backend` (`setuptools.backends.legacy:build` → `setuptools.build_meta`) |

### Glossário

| Termo | Significado |
|---|---|
| **Auto mode** | Dois controlos deslizantes — "base" (abrir/fechar) e "side" (lateral) — acionam indiretamente os dois servos de um dedo |
| **Raw mode** | Os ângulos de ambos os servos de um dedo são controlados diretamente |
| **base** | Quantidade de abrir/fechar, `(pos1 + pos2) / 2` |
| **side** | Desvio lateral, `base − pos1` |
| **raw** | A unidade de posição interna do servo: 0–1023 ao longo de 300°, centro 511 |
| **MiddlePos** | A calibração de meio por servo do firmware do fabricante; difere entre mãos (ver 8.1) |
| **angle_offset** | O desvio de montagem de 35,16° entre mãos (ver 8.2) |
| **mirror_pose** | A troca do par de servos por dedo da mão esquerda (ver 8.2) |
