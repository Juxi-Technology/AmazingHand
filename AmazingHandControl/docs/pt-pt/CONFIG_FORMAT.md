[English](../en/CONFIG_FORMAT.md) | [Deutsch](../de/CONFIG_FORMAT.md) | [Español](../es/CONFIG_FORMAT.md) | [Français](../fr/CONFIG_FORMAT.md) | [Italiano](../it/CONFIG_FORMAT.md) | [日本語](../ja/CONFIG_FORMAT.md) | [한국어](../ko/CONFIG_FORMAT.md) | [Português (BR)](../pt-br/CONFIG_FORMAT.md) | Português (PT) | [简体中文](../zh-hans/CONFIG_FORMAT.md) | [繁體中文](../zh-hant/CONFIG_FORMAT.md)

# Formato de Configuração da Mão (YAML)

Este documento descreve os ficheiros de configuração YAML usados pelo AmazingHand.

| Ficheiro | Finalidade |
|------|---------|
| `data/hand_config.yaml` | Poses e sequências (criados/editados pela GUI e pela CLI) |
| `data/config.yaml` | Definições da aplicação (porta série, limites dos servos, velocidades, caminhos) |

---

## `data/config.yaml` – Definições da aplicação

Carregado no arranque pela GUI. Se o ficheiro estiver em falta, são usados os padrões incorporados.
A CLI usa os mesmos padrões (substituíveis via `--port` / `--baudrate`).

### Estrutura completa

```yaml
# Serial port settings
serial:
  port_windows: COM9          # Default port on Windows
  port_linux: /dev/ttyACM0   # Default port on Linux/macOS
  baudrate: 1000000           # Default baud rate
  baudrate_options: [9600, 115200, 1000000]  # Shown in GUI dropdown

# Servo assignments — [servo1_id, servo2_id] per finger
# servo1 (odd ID)  = position axis (open/close)
# servo2 (even ID) = side axis (left/right)
servos:
  ring:    [1, 2]
  middle:  [3, 4]
  pointer: [5, 6]
  thumb:   [7, 8]
  all_ids: [1, 2, 3, 4, 5, 6, 7, 8]

# Servo angle limits (degrees)
limits:
  servo_min: -40   # Absolute minimum for any servo command
  servo_max: 110   # Absolute maximum for any servo command
  base_min: 0      # Open/close slider minimum
  base_max: 110    # Open/close slider maximum
  side_min: -40    # Left/right slider minimum
  side_max: 40     # Left/right slider maximum

# Movement speeds (1–6 scale, where 6 is fastest)
speeds:
  default: 3
  min: 1
  max: 6

# Auto-mode blending extremes — [servo1_deg, servo2_deg]
# Used to interpolate combined position+side values in Auto mode
auto_extremes:
  left_open:    [32, -40]
  right_open:   [-40, 32]
  left_closed:  [110, 110]
  right_closed: [110, 110]
  center_open:  [0, 0]
  center_closed: [110, 110]

# File paths (relative to project root)
paths:
  poses_sequences_file: data/hand_config.yaml
```

### Notas
- Todas as chaves são opcionais — as chaves em falta revertem para os padrões incorporados mostrados acima.
- **Não** armazene poses nem sequências aqui; essas pertencem a `data/hand_config.yaml`.
- Reinicie a GUI após editar este ficheiro para que as alterações tenham efeito.

---

## `data/hand_config.yaml` – Poses e Sequências

Criado e editado pela GUI e pela CLI. Partilhado entre ambas as ferramentas.

### Estrutura YAML

```yaml
poses:
  <pose_name>:
    positions: [pos1, pos2, pos3, pos4, pos5, pos6, pos7, pos8]

sequences:
  <sequence_name>:
    steps:
      - "<pose_name>:speed1,speed2,...,speed8|delay"
      - "SLEEP:duration"
```

## Poses

Cada pose define uma posição completa da mão com 8 valores de servo.

### Formato
```yaml
poses:
  pose_name:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
```

### Array de posições
- **8 valores** que representam as posições dos servos em graus
- **Mapeamento dos servos**:
  - Servo 1: posição do dedo indicador (0=aberto, 110=fechado)
  - Servo 2: lado do dedo indicador (-20=esquerda, 0=centro, +20=direita)
  - Servo 3: posição do dedo médio
  - Servo 4: lado do dedo médio
  - Servo 5: posição do dedo anelar
  - Servo 6: lado do dedo anelar
  - Servo 7: posição do polegar
  - Servo 8: lado do polegar

- **Intervalo do controlo deslizante Abrir/Fechar**: 0-110° por dedo (0=aberto, 110=fechado)
- **Intervalo do controlo deslizante lateral**: -40° (esquerda) a +40° (direita)
- **Valores de servo armazenados**: como o YAML armazena os valores combinados (base ± side), é de esperar que os comandos reais dos servos fiquem aproximadamente entre -40° e 150°
- **Nota**: os servos com número par (2,4,6,8) têm os ângulos invertidos no hardware

### Regras de nomenclatura
- São permitidas letras, números e sublinhados
- **Caracteres proibidos**: `: { } [ ] , & * # ? | - < > = ! % @ \` " '`
- Máximo de 50 caracteres
- Sensível a maiúsculas/minúsculas

### Exemplo
```yaml
poses:
  open:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
  close:
    positions: [110, 0, 110, 0, 110, 0, 110, 0]
  peace:
    positions: [0, 0, 110, 0, 0, 0, 0, 0]
```

## Sequências

As sequências definem animações de vários passos com velocidades e atrasos individuais por servo.

### Formato
```yaml
sequences:
  sequence_name:
    steps:
      - "pose_name:speed1,speed2,speed3,speed4,speed5,speed6,speed7,speed8|delay"
      - "SLEEP:duration"
```

### Formato do passo

**Pose com velocidades individuais e atraso:**
```
"pose_name:s1,s2,s3,s4,s5,s6,s7,s8|delay"
```
- `pose_name`: nome da pose a executar
- `s1-s8`: velocidade individual de cada servo (1-6, em que 6 é a mais rápida)
- `delay`: tempo de espera após a conclusão do movimento (por exemplo, `2.0s`)

**Pose com velocidades padrão:**
```
"pose_name:3,3,3,3,3,3,3,3|2.0s"
```

**Sleep/pausa:**
```
"SLEEP:1.5s"
```
- Pausa durante a duração especificada sem mover os servos

### Valores de velocidade
- Intervalo: 1 (mais lenta) a 6 (mais rápida)
- Controla a velocidade de movimento dos servos
- Cada servo pode ter uma velocidade diferente num passo

### Controlo de loop
- A definição de loop **NÃO** é armazenada no YAML
- É controlada por caixa de verificação no reprodutor de sequências da GUI
- Permite uma reprodução flexível sem editar o YAML

### Exemplo
```yaml
sequences:
  demo:
    steps:
      - "open:3,3,3,3,3,3,3,3|2.0s"
      - "close:3,3,3,3,3,3,3,3|2.0s"
      - "open:3,3,3,3,3,3,3,3|1.0s"
  
  wave:
    steps:
      - "open:5,5,5,5,5,5,5,5|0.5s"
      - "SLEEP:0.3s"
      - "close:5,5,5,5,5,5,5,5|0.5s"
      - "SLEEP:0.3s"
```

## Gestão de poses e sequências

### Através da GUI (`amazing_hand_gui.py`)

**Poses:**
1. Posicione os dedos com os controlos deslizantes ou o teclado
2. Introduza o nome no campo "Name:"
3. Clique em "➕ Add New" para guardar

**Sequências:**
1. Clique no botão "Manage" na secção Reprodutor de Sequências
2. Construa a sequência na caixa de diálogo:
   - Selecione poses e velocidades
   - Adicione atrasos entre passos
   - Reordene com os botões ↑/↓
3. Introduza o nome da sequência e clique em "💾 Save"

**Execução:**
- Selecione a sequência na lista pendente
- Marque "Loop" se pretender reprodução contínua
- Clique em "▶ Play"

### Através da CLI (`amazing_hand_cmd.py`)

**Listar todas as poses e sequências:**
```bash
python amazing_hand_cmd.py --list
```

**Executar uma pose:**
```bash
python amazing_hand_cmd.py --pose open
```

**Executar uma sequência:**
```bash
python amazing_hand_cmd.py --sequence demo
```

**Executar com loop:**
```bash
python amazing_hand_cmd.py --sequence wave --loop
```

**Utilizar uma configuração alternativa:**
```bash
python amazing_hand_cmd.py --pose open --config /path/to/hand_config.yaml
```

## Edição manual

Pode editar `data/hand_config.yaml` diretamente:

1. **Siga a sintaxe YAML** - a indentação deve ser consistente (2 ou 4 espaços)
2. **Use o formato de array inline** para as posições:
   ```yaml
   positions: [0, 0, 0, 0, 0, 0, 0, 0]
   ```
3. **Coloque os passos da sequência entre aspas** para preservar os caracteres especiais:
   ```yaml
   steps:
     - "open:3,3,3,3,3,3,3,3|2.0s"
   ```
4. **Valide os nomes** - evite caracteres proibidos
5. **Reinicie a GUI** para recarregar as alterações
6. **Mantenha cópias de segurança** antes de edições importantes

## Validação

A GUI e a CLI validam automaticamente:
- nomes de poses/sequências (caracteres proibidos)
- sintaxe YAML ao guardar
- comprimento do array de posições (tem de ser 8)

Os nomes inválidos serão rejeitados com uma mensagem de erro que mostra os caracteres proibidos.

## Licença

Copyright 2026 AmazingHand Control Contributors

Licenciado ao abrigo da Apache License, Version 2.0
