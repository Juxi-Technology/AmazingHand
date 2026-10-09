[English](../en/REQUIREMENTS.md) | [Deutsch](../de/REQUIREMENTS.md) | [Español](../es/REQUIREMENTS.md) | [Français](../fr/REQUIREMENTS.md) | [Italiano](../it/REQUIREMENTS.md) | [日本語](../ja/REQUIREMENTS.md) | [한국어](../ko/REQUIREMENTS.md) | Português (BR) | [Português (PT)](../pt-pt/REQUIREMENTS.md) | [简体中文](../zh-hans/REQUIREMENTS.md) | [繁體中文](../zh-hant/REQUIREMENTS.md)

# AmazingHandGUI — Requisitos e critérios de aceitação

Este documento reúne os requisitos funcionais e os critérios de aceitação
derivados da implementação atual. Cada requisito referencia o(s) arquivo(s)-fonte
onde o comportamento é implementado.

---

## 1. Gerenciamento da conexão

### FR-CONN-1: Seleção da porta serial
A GUI oferece uma caixa de combinação que lista as portas seriais detectadas automaticamente.

| AC | Critério |
|----|-----------|
| 1.1 | No Linux, aparecem os dispositivos `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`; se não existir nenhum, `/dev/ttyACM0` e `/dev/ttyUSB0` são listados como alternativas. |
| 1.2 | No Windows, são listadas `COM1`–`COM20`. |
| 1.3 | O padrão coincide com o valor específico da plataforma em `config.yaml` (`/dev/ttyACM0` ou `COM9`). |

### FR-CONN-2: Seleção da taxa de transmissão
Uma caixa de combinação oferece opções configuráveis de taxa de transmissão.

| AC | Critério |
|----|-----------|
| 2.1 | As opções vêm de `config.yaml` → `serial.baudrate_options` (padrão `[9600, 115200, 1000000]`). |
| 2.2 | A seleção padrão é `1000000`. |
| 2.3 | O menu suspenso fica desabilitado durante a conexão. |

### FR-CONN-3: Conectar / Desconectar
Os botões Conectar e Desconectar gerenciam a conexão serial e o torque dos servos.

| AC | Critério |
|----|-----------|
| 3.1 | Conectar abre a porta serial, habilita o torque nos servos 1–8, desabilita os controles Conectar/porta/baud e habilita Desconectar. |
| 3.2 | Desconectar desabilita o torque em todos os 8 servos, reabilita Conectar/porta/baud e desabilita Desconectar. |
| 3.3 | Uma falha de conexão exibe um erro na barra de status e no log; a GUI permanece desconectada. |

### FR-CONN-4: Conexão automática na inicialização
A GUI tenta se conectar automaticamente 100 ms após a inicialização.

| AC | Critério |
|----|-----------|
| 4.1 | `connect_controller()` é chamado via `root.after(100, …)` durante a inicialização. |

### FR-CONN-5: Conexão via CLI
A CLI se conecta pelos argumentos `--port` e `--baudrate`.

| AC | Critério |
|----|-----------|
| 5.1 | `--port` e `--baudrate` sobrescrevem os padrões. |
| 5.2 | O torque é habilitado em todos os 8 servos ao conectar. |
| 5.3 | O torque é desabilitado na saída (incluindo Ctrl+C via bloco `finally`). |
| 5.4 | `--list` **não** abre uma conexão de hardware. |

---

## 2. Controle dos dedos

### FR-FING-1: Quatro widgets de dedo
São exibidos quatro controles de dedo: anelar, médio, indicador e polegar — cada um com 2 servos.

| AC | Critério |
|----|-----------|
| 1.1 | Exatamente 4 widgets `FingerControl` são renderizados com nomes que correspondem aos pares de servos de `config.yaml`: anelar (5,6), médio (3,4), indicador (1,2), polegar (7,8). |

### FR-FING-2: Modo Auto (Base + Lateral)
O modo Auto oferece um controle deslizante vertical de fechar/abrir e um controle deslizante horizontal de lateralidade.

| AC | Critério |
|----|-----------|
| 2.1 | Controle deslizante vertical: 0° (aberto) a 110° (fechado); topo = fechado, base = aberto. |
| 2.2 | Controle deslizante horizontal: −40° a +40°. |
| 2.3 | Mover qualquer um dos controles envia posições interpoladas (via `compute_auto_positions`) para ambos os servos. |

### FR-FING-3: Modo Raw
O modo Raw mostra dois controles deslizantes verticais independentes (um por servo).

| AC | Critério |
|----|-----------|
| 3.1 | Selecionar Raw oculta os controles do modo Auto e mostra dois controles deslizantes verticais por servo (−40 a 110). |
| 3.2 | A caixa de seleção Mimic é desabilitada e desmarcada; o botão Centralizar é desabilitado. |
| 3.3 | A troca de modo sincroniza os valores bidirecionalmente (auto ↔ raw via `decompose_servo_positions`). |

### FR-FING-4: Controle de velocidade
Cada dedo tem uma caixa de combinação de velocidade (1–6).

| AC | Critério |
|----|-----------|
| 4.1 | A faixa vai de `speeds.min` (1) a `speeds.max` (6), padrão `speeds.default` (3). |
| 4.2 | A velocidade é enviada via `write_goal_speed()` por servo antes dos comandos de posição. |

### FR-FING-5: Modo Mimic
Alterações de fechar/abrir em um dedo que imita são propagadas para todos os outros dedos com o Mimic habilitado.

| AC | Critério |
|----|-----------|
| 5.1 | Habilitar o Mimic em A e B faz com que as alterações do controle de fechar/abrir de A se reflitam em B e vice-versa. |
| 5.2 | O Mimic só se aplica no modo Auto; mudar para Raw o desabilita. |

### FR-FING-6: Botão Centralizar
Redefine o deslocamento lateral para 0°.

| AC | Critério |
|----|-----------|
| 6.1 | Clicar em Centralizar define `side_var` como 0 e dispara uma atualização de posição. |
| 6.2 | Centralizar fica desabilitado no modo Raw. |

### FR-FING-7: Roda do mouse no controle deslizante de posição
A roda de rolagem ajusta a posição em ±5°.

| AC | Critério |
|----|-----------|
| 7.1 | Rolar para cima → +5° (fechar), rolar para baixo → −5° (abrir), limitado aos limites. |

### FR-FING-8: Indicador de atividade em LED
Cada dedo exibe um LED de status.

| AC | Critério |
|----|-----------|
| 8.1 | Em movimento (moving flag = true) → verde piscando a cada ~350 ms. |
| 8.2 | Bloqueado (erro meta-versus-posição ≥ 8° e sem movimento) → vermelho fixo. |
| 8.3 | Ocioso → cinza. |

---

## 3. Controle por teclado

### FR-KEY-1: Seleção do dedo
As teclas 1–4 selecionam o dedo ativo.

| AC | Critério |
|----|-----------|
| 1.1 | 1 = anelar, 2 = médio, 3 = indicador, 4 = polegar. |
| 1.2 | A barra de status mostra o nome do dedo selecionado. |

### FR-KEY-2: Movimento pelas teclas de seta
As teclas de seta movem o dedo selecionado.

| AC | Critério |
|----|-----------|
| 2.1 | Cima = fechar (aumentar a posição), Baixo = abrir (diminuir). |
| 2.2 | Direita = aumentar o deslocamento lateral, Esquerda = diminuir. |

### FR-KEY-3: Modificadores de precisão
O tamanho do passo varia conforme a tecla modificadora.

| AC | Critério |
|----|-----------|
| 3.1 | Sem modificador: 1° (preciso). |
| 3.2 | Shift: 5° (normal). |
| 3.3 | Ctrl: 10° (rápido). |
| 3.4 | A barra de status mostra o nome do modo e o ângulo resultante. |

### FR-KEY-4: Ações rápidas
Atalhos de tecla única para ações comuns.

| AC | Critério |
|----|-----------|
| 4.1 | Q = fechar totalmente a 110°. |
| 4.2 | E = abrir totalmente a 0°. |
| 4.3 | C = centralizar a lateral em 0°. |

---

## 4. Controles globais

### FR-GLOB-1: Abrir tudo
Coloca todos os dedos totalmente abertos.

| AC | Critério |
|----|-----------|
| 1.1 | Todos os `pos_var` → 0, todos os `side_var` → 0, posições enviadas ao hardware. |

### FR-GLOB-2: Fechar tudo
Coloca todos os dedos totalmente fechados.

| AC | Critério |
|----|-----------|
| 2.1 | Todos os `pos_var` → 110, todos os `side_var` → 0, posições enviadas. |

### FR-GLOB-3: Centralizar tudo
Redefine todos os deslocamentos laterais.

| AC | Critério |
|----|-----------|
| 3.1 | Todos os `side_var` → 0, posições enviadas. |

### FR-GLOB-4: Velocidade global
Um menu suspenso define as velocidades de todos os dedos de uma só vez.

| AC | Critério |
|----|-----------|
| 4.1 | Selecionar um valor atualiza todas as caixas de combinação de velocidade por dedo. |
| 4.2 | A velocidade é limitada a [1, 6]. |

---

## 5. Gerenciamento de poses

### FR-POSE-1: Salvar pose
O usuário digita um nome e salva as posições atuais dos 8 servos.

| AC | Critério |
|----|-----------|
| 1.1 | As posições dos 4 dedos (8 valores) são capturadas via `get_positions()`. |
| 1.2 | O nome é validado via `validate_name()` antes de salvar. |
| 1.3 | Em caso de sucesso: o menu suspenso é atualizado (ordenado), o campo é limpo e a barra de status confirma. |
| 1.4 | Nome inválido ou vazio exibe uma caixa de mensagem de erro. |

### FR-POSE-2: Aplicar pose
Selecionar uma pose e clicar em Aplicar move a mão para essa pose.

| AC | Critério |
|----|-----------|
| 2.1 | As 8 posições são aplicadas a todos os widgets dos dedos. |
| 2.2 | As posições dos servos são enviadas ao hardware. |
| 2.3 | O atraso é estimado a partir da distância do movimento e da velocidade; a conclusão da pose é registrada após esse atraso, com comparação entre meta e valor real. |

### FR-POSE-3: Excluir pose
Remove a pose selecionada após confirmação.

| AC | Critério |
|----|-----------|
| 3.1 | Uma caixa de mensagem sim/não pede confirmação. |
| 3.2 | Ao confirmar: a pose é removida da configuração, o YAML é salvo e o menu suspenso é atualizado. |
| 3.3 | Se não restar nenhuma pose, o menu suspenso mostra `<no poses>`. |

### FR-POSE-4: Validação de nome
Os nomes são validados para evitar corrupção do YAML.

| AC | Critério |
|----|-----------|
| 4.1 | Vazio / só espaços → rejeitado. |
| 4.2 | Mais de 50 caracteres → rejeitado. |
| 4.3 | Contém `: { } [ ] , & * # ? \| - < > = ! % @ \` " '` → rejeitado. |
| 4.4 | Contém caracteres de controle (ASCII < 32) → rejeitado. |
| 4.5 | Espaços no início/fim → rejeitado. |

---

## 6. Gerenciamento de sequências

### FR-SEQ-1: Reprodutor de sequências (janela principal)
Seleção por menu suspenso, caixa de seleção Loop e botões Reproduzir / Pausar / Parar.

| AC | Critério |
|----|-----------|
| 1.1 | O menu suspenso lista todas as sequências salvas (ou `<no sequences>`). |
| 1.2 | A caixa de seleção Loop habilita a repetição contínua. |
| 1.3 | Reproduzir inicia a sequência em uma thread em segundo plano. |
| 1.4 | Pausar alterna entre pausado/retomado; o texto do botão alterna entre "⏸ Pause" e "▶ Resume". |
| 1.5 | Parar define `stop_sequence = True`; a thread da sequência termina. |

### FR-SEQ-2: Mecanismo de execução de sequências
As sequências rodam em uma thread em segundo plano com repousos interrompíveis.

| AC | Critério |
|----|-----------|
| 2.1 | As etapas de pose interpretam o formato `"pose_name:s1,s2,...,s8\|delay"`. |
| 2.2 | As etapas `SLEEP:duration` fazem pausa sem comandos de hardware. |
| 2.3 | Sem atraso explícito: espera automática = `15.0 − (avg_speed − 1) × 2.4` segundos. |
| 2.4 | Os repousos executam em incrementos de 0,1 s, verificando os sinalizadores de parada/pausa a cada tique. |
| 2.5 | No modo loop, um intervalo de 0,5 s separa as iterações. |
| 2.6 | Nomes de pose desconhecidos são ignorados com um aviso. |
| 2.7 | Os botões Reproduzir/Pausar/Parar alternam entre habilitado/desabilitado durante a execução. |

### FR-SEQ-3: Diálogo do gerenciador de sequências
Diálogo de dois painéis acessado pelo botão "🔧 Manage".

| AC | Critério |
|----|-----------|
| 3.1 | Painel esquerdo: caixa de listagem das sequências salvas com os botões Executar, Editar e Excluir. |
| 3.2 | Clicar duas vezes executa a sequência uma vez (sem loop), sem fechar o diálogo. |
| 3.3 | Editar carrega as etapas no construtor, preenchendo antes o campo de nome. |

### FR-SEQ-4: Construtor de sequências
Painel direito para montar sequências a partir de poses.

| AC | Critério |
|----|-----------|
| 4.1 | Poses disponíveis listadas; clicar duas vezes adiciona uma etapa com a velocidade/atraso atuais. |
| 4.2 | Caixas de rotação de velocidade por dedo (1–6); "⬇ Copy from UI" importa as velocidades da janela principal. |
| 4.3 | A entrada de atraso acrescenta o sufixo `\|delay` às etapas de pose. |
| 4.4 | "⏱ Delay" insere uma etapa `SLEEP:Xs` autônoma. |
| 4.5 | ↑/↓ reordenam, ➖ remove, 🗑 limpa tudo. |
| 4.6 | "💾 Save Sequence" valida o nome, salva e atualiza os menus suspensos. |
| 4.7 | "▶ Execute" executa a sequência montada sem salvar nem fechar o diálogo. |

### FR-SEQ-5: Validação da entrada de atraso
Valores de ponto flutuante inválidos no campo de atraso são tratados de forma tolerante.

| AC | Critério |
|----|-----------|
| 5.1 | Atraso não numérico assume nenhum atraso (etapa adicionada sem `\|delay`). |
| 5.2 | Atraso de SLEEP não numérico mostra "Invalid delay value" na barra de status. |

---

## 7. Monitoramento dos servos

### FR-MON-1: Coleta de telemetria em segundo plano
Uma thread daemon consulta os 8 servos a ~10 Hz.

| AC | Critério |
|----|-----------|
| 1.1 | A thread dorme 0,1 s entre as iterações. |
| 1.2 | Métricas coletadas por servo: posição, carga, temperatura, tensão, velocidade, sinalizador de movimento, status e meta. |
| 1.3 | Uma leitura falha repete o último valor conhecido para manter os arrays sincronizados. |
| 1.4 | Os dados de feedback são atualizados de forma atômica sob `feedback_lock`. |

### FR-MON-2: Exibição do gráfico
Gráfico Matplotlib embutido no painel direito.

| AC | Critério |
|----|-----------|
| 2.1 | Métricas selecionáveis: posição, meta versus atual, torque, velocidade, temperatura, tensão e movimento. |
| 2.2 | O menu suspenso "Servos" alterna quais dos 8 traços ficam visíveis (com ✓ All / ✕ None). |
| 2.3 | As atualizações do gráfico são limitadas a intervalos de ≥100 ms. |
| 2.4 | Nenhuma métrica selecionada → mensagem "Select at least one metric". |
| 2.5 | Sem dados → mensagem "Waiting for data...". |

### FR-MON-3: Modos do gráfico
Dois modos: Multi-Servo e Scope.

| AC | Critério |
|----|-----------|
| 3.1 | O modo Scope mostra um seletor "Scope Servo" para focar em um único servo. |
| 3.2 | O Multi-Servo oculta o seletor Scope Servo. |

### FR-MON-4: Zoom e pan do gráfico
Quatro controles deslizantes para controlar a visualização.

| AC | Critério |
|----|-----------|
| 4.1 | Y-Zoom: 0,2× a 5,0×, padrão 1,1×. |
| 4.2 | Y-Pan: −3,0 a +3,0, padrão 0,0. |
| 4.3 | Time-Zoom: 10 % a 100 % dos dados disponíveis. |
| 4.4 | Time-Pan: 0 % (mais antigo) a 100 % (mais recente). |
| 4.5 | Todos os controles disparam atualizações do gráfico com debounce. |

### FR-MON-5: Modo rolante
Limita o gráfico aos últimos N pontos de dados.

| AC | Critério |
|----|-----------|
| 5.1 | Quando habilitado e os dados excedem `max_data_points` (100), as amostras mais antigas são descartadas. |
| 5.2 | Desabilitar o modo rolante retém todos os dados coletados. |

### FR-MON-6: Pausar / Retomar / Limpar gráfico

| AC | Critério |
|----|-----------|
| 6.1 | Pausar interrompe as atualizações do gráfico; a coleta de telemetria continua. |
| 6.2 | Limpar redefine todos os arrays de dados e o zoom/pan para os padrões. |

### FR-MON-7: Painel de feedback
Tabela em grade mostrando a telemetria ao vivo de todos os servos.

| AC | Critério |
|----|-----------|
| 7.1 | Colunas: S1–S8. Linhas: meta, posição, velocidade, torque, tensão, corrente, temperatura, status e movimento. |
| 7.2 | Valores formatados por `format_feedback_value()`: posição `X.XX°`, velocidade `X.X°/s`, tensão `X.XX V`, temperatura `X.X °C`, corrente `X mA`, carga `X.X %`, status `0xHH`, movimento `Yes/No`. |
| 7.3 | Apenas as células alteradas são atualizadas (cache de diferenças). |
| 7.4 | Atualização limitada a intervalos de ≥50 ms. |

---

## 8. Configuração

### FR-CFG-1: Carregamento da configuração do aplicativo
`config.yaml` é carregado com padrões para todas as chaves ausentes.

| AC | Critério |
|----|-----------|
| 1.1 | Arquivo ausente → configuração padrão completa usada. |
| 1.2 | Chaves ausentes preenchidas a partir dos padrões (mescla em dois níveis). |
| 1.3 | Falha de análise → padrões retornados; erro impresso em stdout. |

### FR-CFG-2: Mapeamento dos servos
IDs de servo por dedo definidos em `config.yaml` → `servos`.

| AC | Critério |
|----|-----------|
| 2.1 | A configuração define indicador=[1,2], médio=[3,4], anelar=[5,6], polegar=[7,8]. |
| 2.2 | `all_ids` = [1,2,3,4,5,6,7,8]. |

### FR-CFG-3: Limites de ângulo

| AC | Critério |
|----|-----------|
| 3.1 | `servo_min` = −40, `servo_max` = 110, `base_min` = 0, `base_max` = 110, `side_min` = −40, `side_max` = 40. |
| 3.2 | Todas as faixas dos controles deslizantes derivam desses valores. |

### FR-CFG-4: Extremos do modo Auto
Pontos de extremidade da interpolação bilinear para o cálculo do deslocamento lateral.

| AC | Critério |
|----|-----------|
| 4.1 | `left_open`, `right_open`, `left_closed`, `right_closed`, `center_open` e `center_closed` são configuráveis. |
| 4.2 | `compute_auto_positions()` usa esses valores para a interpolação. |

### FR-CFG-5: Configuração de velocidade

| AC | Critério |
|----|-----------|
| 5.1 | `speeds.default` = 3, `speeds.min` = 1, `speeds.max` = 6. |

---

## 9. Ferramenta de linha de comando (CLI)

### FR-CLI-1: Listar poses e sequências
`--list` imprime todas as poses e sequências sem abrir uma conexão.

| AC | Critério |
|----|-----------|
| 1.1 | A saída mostra a contagem de poses, cada nome com as posições. |
| 1.2 | A saída mostra a contagem de sequências, cada nome com a contagem de etapas e detalhes. |
| 1.3 | Nenhuma conexão serial é aberta. |

### FR-CLI-2: Aplicar pose
`--pose NAME` envia uma pose salva ao hardware.

| AC | Critério |
|----|-----------|
| 2.1 | Posições carregadas da configuração; velocidade padrão 3 aplicada a todos os servos. |
| 2.2 | Pose desconhecida → erro + `sys.exit(1)`. |

### FR-CLI-3: Reproduzir sequência
`--sequence NAME` reproduz uma sequência; `--loop` repete até Ctrl+C.

| AC | Critério |
|----|-----------|
| 3.1 | Velocidades e atraso analisados a partir da string da etapa. |
| 3.2 | As etapas `SLEEP` fazem pausa sem comandos de hardware. |
| 3.3 | Sem atraso explícito → espera automática = `15.0 − (avg_speed − 1) × 2.4` segundos. |
| 3.4 | SIGINT define `stop_flag` para interrupção graciosa. |
| 3.5 | Sequência desconhecida → saída com erro. |
| 3.6 | Sequência vazia → saída com erro. |
| 3.7 | Poses desconhecidas dentro de uma sequência são ignoradas com um WARNING. |

### FR-CLI-4: Análise das etapas
`parse_step()` trata vários formatos.

| AC | Critério |
|----|-----------|
| 4.1 | `SLEEP:2.0s` → repouso de 2,0 s. |
| 4.2 | `open:3,3,...\|2.0s` → pose "open" com velocidades e atraso de 2,0 s. |
| 4.3 | `open` (nome puro) → pose com velocidades padrão, sem atraso. |
| 4.4 | Velocidades com menos de 8 são completadas com 3; as maiores são truncadas. |
| 4.5 | O sufixo de duração `s` / `S` é removido. |

### FR-CLI-5: Ações mutuamente exclusivas
`--list`, `--pose` e `--sequence` são mutuamente exclusivos.

| AC | Critério |
|----|-----------|
| 5.1 | Passar várias ações → saída diferente de zero. |
| 5.2 | `--loop` sem `--sequence` → erro. |

### FR-CLI-6: Substituição do arquivo de configuração
`--config PATH` usa um arquivo YAML alternativo.

| AC | Critério |
|----|-----------|
| 6.1 | Arquivo ausente → erro + `sys.exit(1)`. |

---

## 10. Persistência de dados

### FR-DATA-1: Arquivo de configuração YAML
Poses e sequências são armazenadas em `data/hand_config.yaml`.

| AC | Critério |
|----|-----------|
| 1.1 | O arquivo usa o formato YAML com as chaves de nível superior `poses` e `sequences`. |

### FR-DATA-2: Carregar configuração

| AC | Critério |
|----|-----------|
| 2.1 | Arquivo ausente → `{'poses': {}, 'sequences': {}}`. |
| 2.2 | Arquivo vazio → chaves preenchidas automaticamente. |
| 2.3 | YAML malformado → estrutura vazia; erro impresso em stdout. |

### FR-DATA-3: Salvar configuração com arrays em linha
As posições são salvas em estilo flow via pós-processamento com regex.

| AC | Critério |
|----|-----------|
| 3.1 | O arquivo contém o estilo `positions: [v1, v2, …, v8]`. |
| 3.2 | Valores negativos preservados no formato em linha. |
| 3.3 | Retorna `True` em caso de sucesso e `False` em caso de erro. |

### FR-DATA-4: Criação automática do diretório de dados

| AC | Critério |
|----|-----------|
| 4.1 | O diretório `data/` é criado, caso não exista, antes da gravação. |

### FR-DATA-5: Integridade de ida e volta
Dados gravados pela GUI podem ser lidos pela CLI e vice-versa.

| AC | Critério |
|----|-----------|
| 5.1 | Poses, posições negativas e etapas de sequência sobrevivem a uma ida e volta GUI-salva → CLI-lê. |

---

## 11. Tratamento de erros

### FR-ERR-1: Erro de conexão
Conexões falhas não travam o aplicativo.

| AC | Critério |
|----|-----------|
| 1.1 | A barra de status mostra "Connection failed: …"; `connected` permanece `False`. |

### FR-ERR-2: Taxa de transmissão inválida

| AC | Critério |
|----|-----------|
| 2.1 | Taxa de transmissão não numérica → a barra de status mostra "Invalid baudrate". |

### FR-ERR-3: Recuperação da thread de monitoramento

| AC | Critério |
|----|-----------|
| 3.1 | Uma única falha de leitura de servo não trava a thread. |
| 3.2 | Os erros são impressos em stdout. |

### FR-ERR-4: Degradação do sinalizador de movimento

| AC | Critério |
|----|-----------|
| 4.1 | Após 3 falhas consecutivas de `read_moving`, a supervisão é desabilitada com uma mensagem de log. |
| 4.2 | Muda de `sync_read_moving` para leituras por servo na primeira falha de sincronização. |

### FR-ERR-5: Avisos de conclusão de pose

| AC | Critério |
|----|-----------|
| 5.1 | Erro meta versus real > 5° dispara um aviso ⚠ no log. |
| 5.2 | O tempo limite de movimento (6,0 s) dispara um aviso de tempo limite se os servos nunca pararem de se mover. |

### FR-ERR-6: Configuração ausente (CLI)

| AC | Critério |
|----|-----------|
| 6.1 | Arquivo de configuração ausente → mensagem de erro + `sys.exit(1)`. |

### FR-ERR-7: Sequência vazia / inválida

| AC | Critério |
|----|-----------|
| 7.1 | Etapas de sequência vazias → `sys.exit(1)`. |
| 7.2 | Poses desconhecidas na sequência → ignoradas com WARNING. |

---

## 12. Layout da interface

### FR-UI-1: Estrutura da janela

| AC | Critério |
|----|-----------|
| 1.1 | O título inclui a versão: "AmazingHand Controller v0.8". |
| 1.2 | Geometria inicial: 1920×1200. |
| 1.3 | Um `PanedWindow` horizontal separa os painéis esquerdo (controles) e direito (gráfico). |

### FR-UI-2: Painel esquerdo

| AC | Critério |
|----|-----------|
| 2.1 | Linha 1: anelar, médio, indicador (3 dedos lado a lado). |
| 2.2 | Linha 2: polegar (à direita) + controles empilhados (conexão, global, pose, sequência). |
| 2.3 | Log de execução abaixo dos controles, em um divisor vertical redimensionável. |

### FR-UI-3: Barra de status

| AC | Critério |
|----|-----------|
| 3.1 | É atualizada ao conectar, desconectar, selecionar dedo, alterar velocidade, em operações de pose e em erros. |

### FR-UI-4: Log de execução

| AC | Critério |
|----|-----------|
| 4.1 | Mensagens prefixadas com o carimbo de data/hora `[HH:MM:SS.mmm]`. |
| 4.2 | Rolagem automática até a última entrada. |
| 4.3 | As mensagens também são impressas em stdout. |

### FR-UI-5: Tooltips

| AC | Critério |
|----|-----------|
| 5.1 | Um popup amarelo aparece após 500 ms de hover, posicionado abaixo à direita do widget. |
| 5.2 | Desaparece ao sair com o mouse ou ao pressionar um botão. |

### FR-UI-6: Painel direito (área do gráfico)

| AC | Critério |
|----|-----------|
| 6.1 | `PanedWindow` vertical: gráfico em cima (mín. 200 px), feedback embaixo (mín. 150 px). |
| 6.2 | Controles de tempo abaixo do gráfico; controles Y à direita. |

### FR-UI-7: Ajuda da CLI

| AC | Critério |
|----|-----------|
| 7.1 | `--help` sai com código 0 e mostra todas as opções. |

### FR-UI-8: Argumentos de linha de comando da GUI

| AC | Critério |
|----|-----------|
| 8.1 | `--port` sobrescreve a porta serial padrão. |
| 8.2 | `--baudrate` sobrescreve a taxa de transmissão padrão (1000000). |

---

## Resumo da cobertura de testes

| Arquivo de teste | Escopo | Contagem |
|-----------|-------|-------|
| `tests/test_hand_logic.py` | `load_app_config` (6), `servo_mapping` (3), `angle_limits` (1), `auto_extremes` (2), `speed_config` (1), `default_serial_port` (2), `ensure_data_dir` (2), `load_pose_definitions` (3), `compute_auto_positions` (6), `decompose_servo_positions` (5), `coerce_numeric` (11), `coerce_angle_degrees` (6), `coerce_bool` (6), `load_to_percent` (7), `estimate_current_from_load` (5), `format_feedback_value` (12), `get_time_window_indices` (8), `angle_rad` (3) | 89 |
| `tests/test_gui_utils.py` | `validate_name` (21), `clamp` (8), `load_config` (6), `save_config` (6) | 41 + 10 parametrizados |
| `tests/test_cmd.py` | `angle_rad` (8), `parse_step` (11), `cmd_list` (4), `load_config` (2), `apply_pose` (6), `_interruptible_sleep` (2), `auto_wait` (3), `mutual_exclusion` (1), `config_override` (2) | 41 |
| `tests/test_integration.py` | `cmd_pose` e2e (5), `cmd_sequence` e2e (6), ida e volta da configuração (3) | 14 |
| `tests/test_system.py` | Subprocesso da CLI: `--help` (5), `--list` (9), opções de `--help` (3), caminhos de erro (5) | 22 |
| `tests/test_system_hardware.py` | Hardware real: conexão (2), conexão via CLI (2), aplicação de pose (3), velocidade (2), telemetria (6), sequência (2), recuperação de erro (1), movimento (2), desconexão (1) — **requer a flag `--hardware`** | 21 |
| **Total (sem hardware)** | **217 testes** |
| **Total (com hardware)** | **238 testes** |
