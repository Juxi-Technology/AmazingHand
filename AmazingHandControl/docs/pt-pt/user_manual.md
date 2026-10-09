[English](../en/user_manual.md) | [Deutsch](../de/user_manual.md) | [Español](../es/user_manual.md) | [Français](../fr/user_manual.md) | [Italiano](../it/user_manual.md) | [日本語](../ja/user_manual.md) | [한국어](../ko/user_manual.md) | [Português (BR)](../pt-br/user_manual.md) | Português (PT) | [简体中文](../zh-hans/user_manual.md) | [繁體中文](../zh-hant/user_manual.md)

# Controlador AmazingHand – Manual do Utilizador

> **Versão:** 2026-03-22  
> **Aplica-se a:** `amazing_hand_gui.py` (GUI), `amazing_hand_cmd.py` (CLI)

---

## 1. Introdução

A GUI do Controlador AmazingHand proporciona monitorização em tempo real e controlo manual de uma mão robótica de oito servos acionada por atuadores Feetech SCS0009. A interface está dividida em painéis para o controlo dos dedos, a gestão global, a visualização da telemetria e o registo de atividade. Este guia acompanha-o na instalação, na navegação e nos fluxos de trabalho mais comuns.

> **Dica:** mantenha este manual aberto enquanto utiliza a GUI. As dicas (tooltips) incorporadas na aplicação repetem as mesmas descrições quando passa o rato sobre os controlos.

![AmazingHand hardware with controller connected](../en/screenshots/hand_overview.png)

---

## 2. Lista de verificação de início rápido

1. **Instale as dependências** (uma vez por ambiente):
   ```bash
   python -m pip install -r requirements.txt
   ```
2. **Alimente o hardware:** ligue a alimentação de 5 V à cadeia de servos e ligue o adaptador série USB.
3. **Inicie a GUI:**
   ```bash
   python amazing_hand_gui.py
   ```
4. **Ligue-se ao controlador:** escolha a **Porta** série (por exemplo, `COM9`) e clique em **▶ Conetar**.
5. **Verifique a telemetria:** procure atualizações ao vivo no gráfico e na tabela de feedback.

---

## 3. Visão geral do ecrã

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

### 3.1 Painéis num relance

| Painel | Localização | Finalidade |
|-------|----------|---------|
| **Controlos dos dedos** | Esquerda, topo (3 dedos) + canto inferior direito (polegar) | Controlos deslizantes individuais e seletores de velocidade para cada par de dedos. Inclui indicadores de mimic e LEDs de estado por dedo. |
| **Pilha de controlo direita** | Esquerda, canto inferior direito | Definições de ligação, controlos globais, gestão de poses e reprodutor de sequências. |
| **Painel de telemetria** | Direita | Gráficos em tempo real com controlos deslizantes de zoom/pan e uma tabela de feedback configurável. |
| **Registo de execução** | Fundo | Fluxo de mensagens de estado, avisos e progresso das sequências. |

---

## 4. Guia detalhado dos painéis

### 4.1 Painel de controlo dos dedos (coluna esquerda)

Cada widget de dedo controla um par de servos (posição + desvio lateral):

- **Alternância de modo:** alterne entre **Auto** (controlos deslizantes base + desvio) e **Raw** (alvos diretos dos servos).
- **LED de estado:** cinzento (inativo), verde (em movimento), vermelho (potencial bloqueio, com base na carga vs alvo).
- **Controlo deslizante de posição:** 0–110° (aberto a fechado). A roda do rato ajusta em 1°; arrastar move rapidamente.
- **Controlo deslizante lateral:** ±40° para ajustes laterais. O controlo deslizante lateral do polegar está **invertido**, para que a direção física corresponda à orientação anatómica da mão — arrastar para a direita move o polegar no sentido positivo relativamente à sua montagem no hardware.
- **Seletor de velocidade:** lista pendente 1–6 que controla a velocidade de movimento de ambos os servos do par do dedo.
- **Caixa de verificação Mimic:** espelha os movimentos de abrir/fechar de um dedo de origem para um movimento coordenado no modo Auto.

**Modos dos dedos: Auto vs Raw**

- **Modo Auto** (predefinição) expõe o controlo deslizante de abrir/fechar, o controlo deslizante de desvio lateral, a lista pendente de velocidade e o botão de centrar. A GUI combina os valores desses dois controlos deslizantes em comandos de servo, usando os extremos calibrados armazenados em `data/hand_config.yaml`, para que o par acompanhe poses naturais dos dedos sem cálculos manuais de servo. O Mimic permanece ativo aqui — ative-o em vários dedos para os acionar em sincronia com o dedo que estiver a ajustar.
- **Modo Raw** substitui os controlos do modo Auto por dois controlos deslizantes verticais identificados por servo. Mova-os para comandar diretamente os ângulos dos servos subjacentes ao testar os fins de curso, validar a calibração ou diagnosticar problemas de ligação mecânica. O botão de centrar e a caixa de verificação mimic ficam desativados, porque o Raw ignora a lógica de mistura automática; os atalhos de teclado continuam a funcionar, com Cima/Baixo a acionar o servo 1 e Esquerda/Direita a acionar o servo 2. O Raw usa o último valor de velocidade selecionado, pelo que deve definir as velocidades antes de mudar, se precisar de uma velocidade de movimento específica.

**Como o modo Auto calcula os alvos dos servos**

- O valor do controlo deslizante de abrir/fechar é limitado a `limits.base_min/base_max` e depois normalizado (`t = base / base_max`) para interpolar entre as poses aberta e fechada de `auto_extremes` para cada lado do dedo.
- O controlo deslizante de desvio lateral é limitado a `limits.side_min/side_max` e convertido num fator de mistura (`u`). Os desvios negativos interpolam da pose central em direção a `left_open`/`left_closed`; os desvios positivos interpolam em direção aos extremos do lado direito.
- Sem desvio lateral, ambos os servos recebem simplesmente o valor do controlo deslizante base. Os alvos finais dos servos são limitados a `limits.servo_min/servo_max` antes de serem enviados, mantendo os movimentos dentro dos limites seguros calibrados.

Os atalhos de teclado complementam os controlos deslizantes (documentados em §5.2).

![Finger control panel with per-finger sliders and status indicators](../en/screenshots/finger_control_frame.png)

### 4.2 Pilha de controlo global (à direita do painel dos dedos)

1. **Ligação:** seleção de porta e taxa de transmissão (ambas as listas pendentes ficam desativadas durante a ligação) e botões de conetar/desconectar. A barra de estado na parte inferior comunica o sucesso ou os erros.
2. **Controlos globais:**
   - **Abrir tudo / Fechar tudo / Centrar tudo** – aplicam-se instantaneamente a todos os dedos.
   - **Lista pendente Global Speed** – define os seletores de velocidade por dedo com um valor comum (1–6).
3. **Gestão de poses:** guarde, carregue, aplique e elimine poses armazenadas em `data/hand_config.yaml`.
   - Layout: `Pose: [lista pendente]  ✓ Aplicar  🗑 Eliminar  Nome: [campo]  ➕ Adicionar novo`
   - **🗑 Eliminar** remove permanentemente a pose selecionada (é apresentada uma caixa de diálogo de confirmação).
4. **Reprodutor de sequências:** selecione e execute animações de vários passos, com loop opcional. Aceda à caixa de diálogo do gestor de sequências através de **🔧 Gerir**.

![Connection, global controls, pose management, and sequence player stack](../en/screenshots/control_frame.png)

### 4.3 Painel de telemetria e feedback (coluna direita)

- **Linha de controlos:**
  - Pausar/retomar as atualizações do gráfico.
  - Alternância da janela deslizante (rolling).
  - Seleção de métricas (posição, carga, velocidade, temperatura, tensão, sinalizador de movimento).
  - Alternância de modo (Multi-Servo vs Scope) com seletor de servo para o último.
  - Lista pendente de visibilidade dos servos com auxiliares "All/None/Clear".
  
![Display mode, metric selection, and scope controls](../en/screenshots/chart_mode_controls.png)

![Display menu for choosing telemetry metrics](../en/screenshots/chart_select_display_values.png)

![Servo visibility menu with quick actions](../en/screenshots/chart_servos_selection.png)

#### Modos do gráfico

- **Multi-Servo** (predefinição) mantém todos os traçados de servos ativos no gráfico. Use a lista pendente **Servos** para ativar/desativar grupos rapidamente e comparar o movimento ou a carga entre dedos.
- **Scope** ativa o seletor **Scope Servo**, permitindo-lhe focar num único canal mantendo as mesmas caixas de verificação de métricas. Combine este modo com o menu de visibilidade dos servos (por exemplo, ocultar tudo e depois reativar o servo do scope) para obter uma vista ao estilo de osciloscópio sem outros traçados.
- Independentemente do modo, a tabela de telemetria continua a apresentar todos os servos, para que possa correlacionar o gráfico focado com o panorama mais amplo dos dados.
- **Área do gráfico:** gráfico Matplotlib que mostra a telemetria selecionada. Zoom através dos controlos deslizantes:
  - **Y Zoom / Pan:** escala e deslocamento verticais.
  - **Time Zoom / Pan:** foco no histórico recente ou em amostras mais antigas.
- **Tabela de feedback:** grelha deslocável que resume os sinalizadores Goal, Position, Speed, Load, Voltage, Temperature, Status e Moving de cada servo.

![Chart controls with zoom/pan sliders and telemetry traces](../en/screenshots/chart_frame.png)

![Feedback table showing live servo metrics](../en/screenshots/feedback_frame.png)

### 4.4 Registo de execução e barra de estado

Localizado abaixo do painel dos dedos, o registo grava as operações por ordem cronológica. A barra de estado mostra a última ação ou aviso.

![Execution log and current status bar](../en/screenshots/log_and_last_action_frame.png)

---

## 5. Utilizar a mão

### 5.1 Ligar ao hardware

1. Alimente os servos e ligue o adaptador USB.
2. Inicie a GUI e confirme que a **Porta** correta é selecionada automaticamente (`COM*` no Windows ou `/dev/tty*` no Linux/macOS).
3. Clique em **▶ Conetar**. O sucesso altera os estados dos botões e atualiza a barra de estado.
4. Se a ligação falhar, verifique a cablagem, a alimentação e a atribuição da porta.

### 5.2 Controlo manual e atalhos

- Selecione um dedo com as teclas **1–4** (1 = anelar, 2 = médio, 3 = indicador, 4 = polegar).
- **Teclas de seta:** Cima/Baixo ajustam a posição; Esquerda/Direita ajustam o desvio lateral.
- Manter **Shift** multiplica o tamanho do passo por 5; **Ctrl** multiplica por 10.
- **Q / E:** fechar / abrir totalmente o dedo selecionado.
- **C:** centrar o desvio lateral.
- Os controlos deslizantes no ecrã refletem a entrada do teclado em tempo real.

![Manual finger control panel with keyboard shortcut overlay](../en/screenshots/manual_finger_control_frame.png)

![Example of fully closing a finger using controls](../en/screenshots/close_finger.png)

![Example of lateral movement adjustment](../en/screenshots/move_finger.png)

### 5.3 Definir velocidades

- A lista pendente de velocidade por dedo (1 = lento, 6 = rápido) controla a velocidade dos servos.
- O seletor **Global Speed** sincroniza todas as velocidades dos dedos.
- Observe as alterações de velocidade na tabela de feedback (linha `Speed`) durante o movimento.

### 5.4 Aplicar e eliminar poses

1. Disponha as posições dos dedos com os controlos deslizantes ou os atalhos de teclado.
2. Em **Gestão de poses**, escreva um nome único e clique em **➕ Adicionar novo**.
3. Para aplicar, selecione a pose na lista pendente e clique em **✓ Aplicar**.
4. Para eliminar, selecione a pose na lista pendente e clique em **🗑 Eliminar**. Uma caixa de diálogo de confirmação evita a remoção acidental.

> As poses armazenam apenas posições de servo; as velocidades são determinadas em tempo de execução pelas definições da GUI.

### 5.5 Construir e executar sequências

1. Clique em **🔧 Gerir** no Reprodutor de Sequências.
2. Na caixa de diálogo:
   - Use a lista **Available Poses** para adicionar passos (clique duas vezes ou prima **➕ Adicionar**).
   - Ajuste as velocidades por dedo através das caixas numéricas e defina atrasos opcionais nos passos.
   - Insira intervalos de pausa dedicados através de **⏱ Delay**.
   - Reordene os passos com os botões ↑/↓.
   - Introduza um nome e clique em **💾 Save Sequence**.
   - Clique em **▶ Execute** para testar sem guardar.
3. De volta à janela principal, selecione a sequência e prima **▶ Play**. Ative **Loop** para reprodução contínua.

> As definições das sequências residem em `data/hand_config.yaml` sob a chave `sequences`. Os loops são controlados do lado da execução, não no YAML.

![Sequence manager dialog with available poses and sequence builder](../en/screenshots/sequences_editor.png)

### 5.6 Monitorizar a telemetria

- Certifique-se de que as métricas pretendidas estão marcadas no menu **Display**.
- Use os controlos deslizantes de zoom/pan para focar nos segmentos de interesse.
- Passe o rato sobre os elementos do gráfico (interações padrão do Matplotlib) para inspecionar valores.
- A tabela de feedback atualiza-se de forma assíncrona; as células destacadas indicam alterações recentes.
- Se o gráfico ficar sobrecarregado, clique em **⌫ Limpar** para reiniciar os dados recolhidos.

---

## 6. Interface de linha de comandos (`amazing_hand_cmd.py`)

A CLI permite-lhe aplicar poses e reproduzir sequências diretamente a partir de um terminal, sem iniciar a GUI. Lê o mesmo ficheiro `data/hand_config.yaml`.

### 6.1 Utilização básica

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
| `--pose NAME` | – | Aplica a pose indicada e sai |
| `--sequence NAME` | – | Reproduz a sequência indicada e sai |
| `--list` | – | Lista todas as poses e sequências |
| `--loop` | off | Repete a sequência continuamente até Ctrl+C |
| `--port PORT` | `/dev/ttyACM0` (Linux) / `COM9` (Win) | Substituição da porta série |
| `--baudrate N` | `1000000` | Substituição da taxa de transmissão |
| `--config PATH` | `data/hand_config.yaml` | Caminho para um ficheiro de configuração alternativo |

### 6.3 Observações

- O binário é **ativado** na ligação e **desativado** na saída, para que os servos relaxem após o fim do script.
- As velocidades e os atrasos por passo comportam-se de forma idêntica ao reprodutor de sequências da GUI.
- A flag `--loop` só pode ser usada em conjunto com `--sequence`.

---

## 7. Resolução de problemas

| Sintoma | Ação sugerida |
|---------|-----------------| 
| **Nenhuma porta série listada** | Volte a ligar o adaptador USB, instale controladores ou reinicie a GUI. |
| **Botão Conetar a cinzento** | Já está ligado; clique primeiro em **⏹ Desconectar**. |
| **Interface lenta durante o redimensionamento** | As otimizações de desempenho (redimensionamento com debounce, redesenhos limitados) minimizam isto, mas fechar janelas desnecessárias pode ajudar. |
| **A sequência não move todos os dedos** | Verifique as velocidades por passo e certifique-se de que cada pose contém os oito valores de servo. |
| **O indicador de bloqueio persiste** | Inspecione obstruções mecânicas; o estado de bloqueio é acionado quando o alvo e a posição diferem significativamente sem movimento. |

---

## 8. Apêndice

### 8.1 Estrutura de ficheiros

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

### 8.2 Ligações úteis

- [AmazingHand (projeto oficial)](https://github.com/pollen-robotics/AmazingHand)
- [Ferramenta de depuração do servo Feetech](https://github.com/Robot-Maker-SAS/FeetechServo/tree/main/feetech%20debug%20tool%20master/FD1.9.8.2)
- [Tutorial de identificação de servos](https://www.robot-maker.com/forum/tutorials/article/168-brancher-et-controler-le-servomoteur-feetech-sts3032-360/)

---

## 9. Histórico de revisões

| Data | Autor | Notas |
|------|--------|-------|
| 2026-03-22 | Ingo | Adicionada a secção da CLI (`amazing_hand_cmd.py`); atualização da versão do manual. |
| 2026-03-21 | Ingo | Atualização da disposição dos painéis: troca anelar/indicador, polegar movido para a direita, pilha de controlo movida para a esquerda. Controlo deslizante lateral do polegar invertido. Botão de eliminar pose adicionado entre Apply e Name. As listas pendentes de Port e Baudrate ficam agora bloqueadas durante a ligação. O atalho de teclado 1–4 agora mapeia anelar/médio/indicador/polegar. |
| 2025-11-25 | Ingo | Adicionada galeria de capturas de ecrã ampliada, explicações dos modos do gráfico e percursos pelos painéis renovados. |
| 2025-11-25 | Ingo | Manual inicial que cobre os painéis da interface, os fluxos de trabalho e a utilização da telemetria. |
