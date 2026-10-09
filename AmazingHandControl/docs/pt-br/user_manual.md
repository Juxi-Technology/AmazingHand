[English](../en/user_manual.md) | [Deutsch](../de/user_manual.md) | [Español](../es/user_manual.md) | [Français](../fr/user_manual.md) | [Italiano](../it/user_manual.md) | [日本語](../ja/user_manual.md) | [한국어](../ko/user_manual.md) | Português (BR) | [Português (PT)](../pt-pt/user_manual.md) | [简体中文](../zh-hans/user_manual.md) | [繁體中文](../zh-hant/user_manual.md)

# AmazingHand Controller – Manual do usuário

> **Versão:** 2026-03-22  
> **Aplica-se a:** `amazing_hand_gui.py` (GUI), `amazing_hand_cmd.py` (CLI)

---

## 1. Introdução

A GUI do AmazingHand Controller oferece monitoramento em tempo real e controle manual de uma mão robótica de oito servos acionada por atuadores Feetech SCS0009. A interface é dividida em painéis para controle dos dedos, gerenciamento global, visualização da telemetria e registro de atividade. Este guia conduz você pela instalação, navegação e fluxos de trabalho comuns.

> **Dica:** Mantenha este manual aberto enquanto opera a GUI. As dicas (tooltips) integradas ao aplicativo repetem as mesmas descrições quando você passa o mouse sobre os controles.

![AmazingHand hardware with controller connected](../en/screenshots/hand_overview.png)

---

## 2. Lista de início rápido

1. **Instale as dependências** (uma vez por ambiente):
   ```bash
   python -m pip install -r requirements.txt
   ```
2. **Energize o hardware:** conecte a alimentação de 5 V à cadeia de servos e plugue o adaptador serial USB.
3. **Inicie a GUI:**
   ```bash
   python amazing_hand_gui.py
   ```
4. **Conecte-se ao controlador:** escolha a **Porta** serial (por exemplo, `COM9`) e clique em **▶ Conectar**.
5. **Verifique a telemetria:** procure atualizações ao vivo no gráfico e na tabela de feedback.

---

## 3. Visão geral da tela

```
+--------------------------------------------------------------------------------+
|                              AmazingHand Controller                            |
+---------------------------+-----------------------------------------------+----+
| Finger Controls           | Chart Controls & Telemetry Plot                    |
| (Ring – Middle – Pointer) | (Display menu, chart canvas)                       |
+---------------------------+-----------------------------------------------+----+
| Control Stack             | Thumb finger   | Feedback Table (Servo Metrics)    |
| (Connection, Global, Pose,| control        | (Goal, Position, Load, etc.)      |
|  Sequence)                |                |                                   |
+---------------------------+                                                    |
| Execution Log & Status    |                                                    |
+--------------------------------------------------------------------------------+
```

![Main window overview highlighting the major panels](../en/screenshots/mainscreen.png)

### 3.1 Painéis em resumo

| Painel | Localização | Finalidade |
|-------|----------|---------|
| **Controles dos dedos** | Esquerda, topo (3 dedos) + inferior direito (polegar) | Controles deslizantes individuais e seletores de velocidade para cada par de dedos. Inclui indicadores de mimic e LEDs de status por dedo. |
| **Pilha de controle direita** | Esquerda, inferior direito | Configurações de conexão, controles globais, gerenciamento de poses e reprodutor de sequências. |
| **Painel de telemetria** | Direita | Gráficos em tempo real com controles deslizantes de zoom/pan e uma tabela de feedback configurável. |
| **Log de execução** | Base | Fluxo de mensagens de status, avisos e progresso das sequências. |

---

## 4. Guia detalhado dos painéis

### 4.1 Painel de controle dos dedos (coluna esquerda)

Cada widget de dedo controla um par de servos (posição + deslocamento lateral):

- **Alternância de modo:** alterna entre **Auto** (controles deslizantes de base + deslocamento) e **Raw** (alvos diretos dos servos).
- **LED de status:** cinza (ocioso), verde (em movimento), vermelho (potencial de bloqueio, com base na carga versus meta).
- **Controle deslizante de posição:** 0–110° (aberto a fechado). A roda do mouse ajusta em 1°; arrastar encaixa rapidamente.
- **Controle deslizante lateral:** ±40° para ajustes laterais. O controle deslizante lateral do polegar é **invertido** para que a direção física corresponda à orientação anatômica da mão — arrastar para a direita move o polegar na direção positiva em relação à sua montagem no hardware.
- **Seletor de velocidade:** menu suspenso de 1–6 que controla a velocidade de movimento dos dois servos do par de dedos.
- **Caixa de seleção Mimic:** espelha os movimentos de fechar/abrir de um dedo de origem para movimento coordenado no modo Auto.

**Modos do dedo: Auto vs Raw**

- **O modo Auto** (padrão) expõe o controle deslizante de fechar/abrir, o controle deslizante de deslocamento lateral, o menu suspenso de velocidade e o botão de centralizar. A GUI combina esses dois valores de controle em comandos de servo usando os extremos calibrados armazenados em `data/hand_config.yaml`, de modo que o par acompanhe poses naturais dos dedos sem cálculos manuais de servo. O Mimic permanece ativo aqui — habilite-o em vários dedos para acioná-los em sincronia com o dedo que você estiver ajustando.
- **O modo Raw** substitui os controles do modo Auto por dois controles deslizantes verticais rotulados pelo servo. Mova-os para comandar diretamente os ângulos dos servos subjacentes ao testar fim de curso, validar a calibração ou diagnosticar problemas de articulação. O botão de centralizar e a caixa de seleção Mimic ficam desabilitados porque o Raw contorna a lógica de mistura automática; os atalhos de teclado continuam funcionando, com Cima/Baixo acionando o servo 1 e Esquerda/Direita acionando o servo 2. O Raw usa o último valor de velocidade selecionado, então defina as velocidades antes de alternar se precisar de uma taxa de movimento específica.

**Como o modo Auto calcula os alvos dos servos**

- O valor do controle deslizante de fechar/abrir é limitado a `limits.base_min/base_max` e depois normalizado (`t = base / base_max`) para interpolar entre as poses `auto_extremes` de aberto e fechado para cada lado do dedo.
- O controle deslizante de deslocamento lateral é limitado a `limits.side_min/side_max` e convertido em um fator de mistura (`u`). Deslocamentos negativos interpolam da pose central em direção a `left_open`/`left_closed`; deslocamentos positivos interpolam em direção aos extremos do lado direito.
- Sem deslocamento lateral, os dois servos simplesmente recebem o valor do controle deslizante de base. Os alvos finais dos servos são limitados a `limits.servo_min/servo_max` antes de serem emitidos, mantendo os movimentos dentro dos limites seguros calibrados.

Os atalhos de teclado complementam os controles deslizantes (documentados no §5.2).

![Finger control panel with per-finger sliders and status indicators](../en/screenshots/finger_control_frame.png)

### 4.2 Pilha de controle global (à direita do painel dos dedos)

1. **Conexão:** seleção de porta e taxa de transmissão (ambos os menus suspensos ficam desabilitados durante a conexão), botões de conectar/desconectar. A barra de status na parte inferior informa sucesso ou erros.
2. **Controles globais:**
   - **Abrir tudo / Fechar tudo / Centralizar tudo** – aplicam-se a todos os dedos instantaneamente.
   - **Menu suspenso de velocidade global** – define os seletores de velocidade de cada dedo para um valor comum (1–6).
3. **Gerenciamento de poses:** salvar, carregar, aplicar e excluir poses armazenadas em `data/hand_config.yaml`.
   - Layout: `Pose: [menu suspenso]  ✓ Aplicar  🗑 Excluir  Nome: [campo]  ➕ Adicionar novo`
   - **🗑 Excluir** remove permanentemente a pose selecionada (com diálogo de confirmação).
4. **Reprodutor de sequências:** seleciona e executa animações de várias etapas, com loop opcional. Acesse o diálogo do gerenciador de sequências em **🔧 Gerenciar**.

![Connection, global controls, pose management, and sequence player stack](../en/screenshots/control_frame.png)

### 4.3 Painel de telemetria e feedback (coluna direita)

- **Linha de controles:**
  - Pausar/retomar as atualizações do gráfico.
  - Alternância de janela rolante.
  - Seleção de métricas (posição, carga, velocidade, temperatura, tensão, sinalizador de movimento).
  - Alternância de modo (Multi-Servo vs Scope) com seletor de servo para o último.
  - Menu suspenso de visibilidade de servos com auxiliares "Todos/Nenhum/Limpar".
  
![Display mode, metric selection, and scope controls](../en/screenshots/chart_mode_controls.png)

![Display menu for choosing telemetry metrics](../en/screenshots/chart_select_display_values.png)

![Servo visibility menu with quick actions](../en/screenshots/chart_servos_selection.png)

#### Modos do gráfico

- **Multi-Servo** (padrão) mantém todos os traços de servos habilitados no gráfico. Use o menu suspenso **Servos** para alternar grupos rapidamente e comparar movimento ou carga entre os dedos.
- **Scope** ativa o seletor **Scope Servo**, permitindo focar em um único canal enquanto ainda usa as mesmas caixas de seleção de métricas. Combine esse modo com o menu de visibilidade de servos (por exemplo, ocultar tudo e depois reabilitar o servo do scope) para obter uma visão estilo osciloscópio sem outros traços.
- Independentemente do modo, a tabela de telemetria continua apresentando todos os servos, para que você possa correlacionar o gráfico focado com o instantâneo mais amplo dos dados.
- **Área do gráfico:** gráfico Matplotlib mostrando a telemetria selecionada. Zoom via controles deslizantes:
  - **Y Zoom / Pan:** escala e deslocamento verticais.
  - **Time Zoom / Pan:** foco no histórico recente ou em amostras mais antigas.
- **Tabela de feedback:** grade rolável que resume meta, posição, velocidade, carga, tensão, temperatura, status e sinalizadores de movimento de cada servo.

![Chart controls with zoom/pan sliders and telemetry traces](../en/screenshots/chart_frame.png)

![Feedback table showing live servo metrics](../en/screenshots/feedback_frame.png)

### 4.4 Log de execução e barra de status

Localizado abaixo do painel dos dedos, o log registra as operações em ordem cronológica. A barra de status exibe a última ação ou aviso.

![Execution log and current status bar](../en/screenshots/log_and_last_action_frame.png)

---

## 5. Operando a mão

### 5.1 Conectando ao hardware

1. Energize os servos e conecte o adaptador USB.
2. Inicie a GUI e confirme que a **Porta** correta é autosselecionada (`COM*` no Windows ou `/dev/tty*` no Linux/macOS).
3. Clique em **▶ Conectar**. O sucesso altera os estados dos botões e atualiza a barra de status.
4. Se a conexão falhar, verifique o cabeamento, a alimentação e a atribuição de porta.

### 5.2 Controle manual e atalhos

- Selecione um dedo com as teclas **1–4** (1 = anelar, 2 = médio, 3 = indicador, 4 = polegar).
- **Teclas de seta:** Cima/Baixo ajustam a posição; Esquerda/Direita ajustam o deslocamento lateral.
- Manter **Shift** multiplica o tamanho do passo por 5; **Ctrl** multiplica por 10.
- **Q / E:** fecham / abrem totalmente o dedo selecionado.
- **C:** centraliza o deslocamento lateral.
- Os controles deslizantes na tela espelham a entrada do teclado em tempo real.

![Manual finger control panel with keyboard shortcut overlay](../en/screenshots/manual_finger_control_frame.png)

![Example of fully closing a finger using controls](../en/screenshots/close_finger.png)

![Example of lateral movement adjustment](../en/screenshots/move_finger.png)

### 5.3 Definindo velocidades

- O menu suspenso de velocidade por dedo (1 = lento, 6 = rápido) controla a velocidade do servo.
- O seletor **Global Speed** sincroniza as velocidades de todos os dedos.
- Observe as mudanças de velocidade na tabela de feedback (linha **Velocidade**) durante o movimento.

### 5.4 Aplicando e excluindo poses

1. Disponha as posições dos dedos usando os controles deslizantes ou os atalhos de teclado.
2. Em **Gerenciamento de poses**, digite um nome exclusivo e clique em **➕ Adicionar novo**.
3. Para aplicar, selecione a pose no menu suspenso e clique em **✓ Aplicar**.
4. Para excluir, selecione a pose no menu suspenso e clique em **🗑 Excluir**. Um diálogo de confirmação evita a remoção acidental.

> As poses armazenam apenas as posições dos servos; as velocidades são determinadas em tempo de execução pelas configurações da GUI.

### 5.5 Montando e executando sequências

1. Clique em **🔧 Gerenciar** no Reprodutor de sequências.
2. No diálogo:
   - Use a lista **Poses disponíveis** para adicionar etapas (clique duas vezes ou pressione **➕ Adicionar**).
   - Ajuste as velocidades por dedo pelas caixas de rotação e defina atrasos opcionais por etapa.
   - Insira intervalos de repouso dedicados com **⏱ Atraso**.
   - Reordene as etapas com os botões ↑/↓.
   - Digite um nome e clique em **💾 Salvar sequência**.
   - Clique em **▶ Executar** para testar sem salvar.
3. De volta à janela principal, selecione a sequência e pressione **▶ Reproduzir**. Habilite **Loop** para reprodução contínua.

> As definições das sequências ficam em `data/hand_config.yaml`, sob a chave `sequences`. Os loops são controlados em tempo de execução, não no YAML.

![Sequence manager dialog with available poses and sequence builder](../en/screenshots/sequences_editor.png)

### 5.6 Monitorando a telemetria

- Certifique-se de que as métricas desejadas estejam marcadas no menu **Display**.
- Use os controles deslizantes de zoom/pan para focar nos segmentos de interesse.
- Passe o mouse sobre os elementos do gráfico (interações padrão do Matplotlib) para inspecionar valores.
- A tabela de feedback é atualizada de forma assíncrona; células destacadas indicam mudanças recentes.
- Se o gráfico ficar sobrecarregado, clique em **⌫ Limpar** para redefinir os dados coletados.

---

## 6. Interface de linha de comando (`amazing_hand_cmd.py`)

A CLI permite aplicar poses e reproduzir sequências diretamente de um terminal, sem iniciar a GUI. Ela lê o mesmo arquivo `data/hand_config.yaml`.

### 6.1 Uso básico

```bash
# List all saved poses and sequences
python amazing_hand_cmd.py --list

# Apply a single pose
python amazing_hand_cmd.py --pose open
python amazing_hand_cmd.py --pose close

# Play a sequence once
python amazing_hand_cmd.py --sequence demo

# Play a sequence in a loop (Ctrl+C to stop)
python amazing_hand_cmd.py --sequence wave --loop
```

### 6.2 Opções

| Opção | Padrão | Descrição |
|--------|---------|-------------|
| `--pose NAME` | – | Aplica a pose nomeada e encerra |
| `--sequence NAME` | – | Reproduz a sequência nomeada e encerra |
| `--list` | – | Lista todas as poses e sequências |
| `--loop` | desligado | Repete a sequência continuamente até Ctrl+C |
| `--port PORT` | `/dev/ttyACM0` (Linux) / `COM9` (Win) | Substituição da porta serial |
| `--baudrate N` | `1000000` | Substituição da taxa de transmissão |
| `--config PATH` | `data/hand_config.yaml` | Caminho para um arquivo de configuração alternativo |

### 6.3 Observações

- O torque é **habilitado** ao conectar e **desabilitado** na saída, para que os servos relaxem após o término do script.
- As velocidades e os atrasos por etapa se comportam de forma idêntica ao reprodutor de sequências da GUI.
- A flag `--loop` só pode ser usada em conjunto com `--sequence`.

---

## 7. Solução de problemas

| Sintoma | Ação sugerida |
|---------|-----------------| 
| **Nenhuma porta serial listada** | Reconecte o adaptador USB, instale os drivers ou reinicie a GUI. |
| **Botão de conectar esmaecido** | Já está conectado; clique primeiro em **⏹ Desconectar**. |
| **Interface lenta ao redimensionar** | As otimizações de desempenho (redimensionamento com debounce, redesenhos com throttling) minimizam isso, mas fechar janelas desnecessárias pode ajudar. |
| **A sequência não move todos os dedos** | Verifique as velocidades por etapa e garanta que cada pose contenha todos os oito valores de servo. |
| **Indicador de bloqueio persiste** | Inspecione obstruções mecânicas; o status de bloqueio é acionado quando a meta e a posição diferem significativamente sem movimento. |

---

## 8. Apêndice

### 8.1 Estrutura de arquivos

```
AmazingHandControl/
├── amazing_hand_gui.py          # GUI application
├── amazing_hand_cmd.py          # CLI tool
├── data/hand_config.yaml        # Poses & sequences
├── data/config.yaml             # Application settings
├── docs/<lang>/user_manual.md        # This document
├── docs/<lang>/CONFIG_FORMAT.md      # YAML config file reference
├── docs/en/screenshots/              # PNG captures embedded in this manual
├── docs/<lang>/scs_servo_protocol.md # SCS servo protocol reference
└── README.md                    # Quick reference
```

### 8.2 Links úteis

- [AmazingHand (projeto oficial)](https://github.com/pollen-robotics/AmazingHand)
- [Ferramenta de depuração de servo Feetech](https://github.com/Robot-Maker-SAS/FeetechServo/tree/main/feetech%20debug%20tool%20master/FD1.9.8.2)
- [Tutorial de identificação de servos](https://www.robot-maker.com/forum/tutorials/article/168-brancher-et-controler-le-servomoteur-feetech-sts3032-360/)

---

## 9. Histórico de revisões

| Data | Autor | Notas |
|------|--------|-------|
| 2026-03-22 | Ingo | Adicionada a seção da CLI (`amazing_hand_cmd.py`); atualização da versão do manual. |
| 2026-03-21 | Ingo | Atualização do layout dos painéis: troca anelar/indicador, polegar movido para a direita, pilha de controle movida para a esquerda. Controle deslizante lateral do polegar invertido. Botão de excluir pose adicionado entre Apply e Name. Os menus suspensos de porta e taxa de transmissão agora ficam bloqueados durante a conexão. O atalho de teclado 1–4 agora mapeia anelar/médio/indicador/polegar. |
| 2025-11-25 | Ingo | Adicionada galeria de capturas de tela ampliada, explicações dos modos do gráfico e passeios renovados pelos painéis. |
| 2025-11-25 | Ingo | Manual inicial cobrindo os painéis da interface, os fluxos de trabalho e o uso da telemetria. |
