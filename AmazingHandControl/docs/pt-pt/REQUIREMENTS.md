[English](../en/REQUIREMENTS.md) | [Deutsch](../de/REQUIREMENTS.md) | [Español](../es/REQUIREMENTS.md) | [Français](../fr/REQUIREMENTS.md) | [Italiano](../it/REQUIREMENTS.md) | [日本語](../ja/REQUIREMENTS.md) | [한국어](../ko/REQUIREMENTS.md) | [Português (BR)](../pt-br/REQUIREMENTS.md) | Português (PT) | [简体中文](../zh-hans/REQUIREMENTS.md) | [繁體中文](../zh-hant/REQUIREMENTS.md)

# AmazingHandGUI — Requisitos e Critérios de Aceitação

Este documento reúne os requisitos funcionais e os critérios de aceitação
derivados da implementação atual. Cada requisito referencia o(s) ficheiro(s) de origem
onde o comportamento é implementado.

---

## 1. Gestão da ligação

### FR-CONN-1: Seleção da porta série
A GUI disponibiliza uma caixa de combinação que lista as portas série detetadas automaticamente.

| AC | Critério |
|----|-----------|
| 1.1 | No Linux, aparecem os dispositivos `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`; se não existir nenhum, `/dev/ttyACM0` e `/dev/ttyUSB0` são listados como alternativas. |
| 1.2 | No Windows, são listadas `COM1`–`COM20`. |
| 1.3 | O padrão corresponde ao valor específico da plataforma em `config.yaml` (`/dev/ttyACM0` ou `COM9`). |

### FR-CONN-2: Seleção da taxa de transmissão
Uma caixa de combinação oferece opções configuráveis de taxa de transmissão.

| AC | Critério |
|----|-----------|
| 2.1 | As opções provêm de `config.yaml` → `serial.baudrate_options` (padrão `[9600, 115200, 1000000]`). |
| 2.2 | A seleção padrão é `1000000`. |
| 2.3 | A lista pendente fica desativada durante a ligação. |

### FR-CONN-3: Conetar / Desconectar
Os botões Conetar e Desconectar gerem a ligação série e o binário dos servos.

| AC | Critério |
|----|-----------|
| 3.1 | Conetar abre a porta série, ativa o binário nos servos 1–8, desativa os controlos Conetar/porta/taxa e ativa Desconectar. |
| 3.2 | Desconectar desativa o binário em todos os 8 servos, reativa Conetar/porta/taxa e desativa Desconectar. |
| 3.3 | Uma falha de ligação mostra um erro na barra de estado e no registo; a GUI permanece desligada. |

### FR-CONN-4: Ligação automática no arranque
A GUI tenta ligar-se automaticamente 100 ms após o arranque.

| AC | Critério |
|----|-----------|
| 4.1 | `connect_controller()` é chamado através de `root.after(100, …)` durante a inicialização. |

### FR-CONN-5: Ligação via CLI
A CLI liga-se através dos argumentos `--port` e `--baudrate`.

| AC | Critério |
|----|-----------|
| 5.1 | `--port` e `--baudrate` substituem os padrões. |
| 5.2 | O binário é ativado em todos os 8 servos na ligação. |
| 5.3 | O binário é desativado na saída (incluindo Ctrl+C através do bloco `finally`). |
| 5.4 | `--list` **não** abre uma ligação ao hardware. |

---

## 2. Controlo dos dedos

### FR-FING-1: Quatro widgets de dedo
São apresentados quatro controlos de dedo: anelar, médio, indicador e polegar — cada um com 2 servos.

| AC | Critério |
|----|-----------|
| 1.1 | Exatamente 4 widgets `FingerControl` são renderizados com nomes correspondentes aos pares de servos de `config.yaml`: anelar (5,6), médio (3,4), indicador (1,2), polegar (7,8). |

### FR-FING-2: Modo Auto (Base + Lateral)
O modo Auto disponibiliza um controlo deslizante vertical de abrir/fechar e um controlo deslizante horizontal de lateralidade.

| AC | Critério |
|----|-----------|
| 2.1 | Controlo deslizante vertical: 0° (aberto) a 110° (fechado); topo = fechado, fundo = aberto. |
| 2.2 | Controlo deslizante horizontal: −40° a +40°. |
| 2.3 | Mover qualquer um dos controlos envia posições interpoladas (via `compute_auto_positions`) para ambos os servos. |

### FR-FING-3: Modo Raw
O modo Raw mostra dois controlos deslizantes verticais independentes (um por servo).

| AC | Critério |
|----|-----------|
| 3.1 | Selecionar Raw oculta os controlos deslizantes do modo Auto e mostra dois controlos deslizantes verticais por servo (−40 a 110). |
| 3.2 | A caixa de verificação Mimic fica desativada e desmarcada; o botão Centrar fica desativado. |
| 3.3 | A troca de modo sincroniza os valores bidirecionalmente (auto ↔ raw via `decompose_servo_positions`). |

### FR-FING-4: Controlo de velocidade
Cada dedo tem uma caixa de combinação de velocidade (1–6).

| AC | Critério |
|----|-----------|
| 4.1 | O intervalo vai de `speeds.min` (1) a `speeds.max` (6), com padrão `speeds.default` (3). |
| 4.2 | A velocidade é enviada via `write_goal_speed()` por servo antes dos comandos de posição. |

### FR-FING-5: Modo Mimic
As alterações de abrir/fechar num dedo que imita são propagadas para todos os outros dedos com o Mimic ativado.

| AC | Critério |
|----|-----------|
| 5.1 | Ativar o Mimic em A e B faz com que as alterações do controlo deslizante de abrir/fechar de A se reflitam em B e vice-versa. |
| 5.2 | O Mimic só se aplica no modo Auto; mudar para Raw desativa-o. |

### FR-FING-6: Botão Centrar
Reinicia o desvio lateral para 0°.

| AC | Critério |
|----|-----------|
| 6.1 | Clicar em Centrar define `side_var` como 0 e desencadeia uma atualização de posição. |
| 6.2 | Centrar fica desativado no modo Raw. |

### FR-FING-7: Roda do rato no controlo deslizante de posição
A roda de deslocamento ajusta a posição em ±5°.

| AC | Critério |
|----|-----------|
| 7.1 | Rolar para cima → +5° (fechar), rolar para baixo → −5° (abrir), limitado aos limites. |

### FR-FING-8: Indicador de atividade LED
Cada dedo mostra um LED de estado.

| AC | Critério |
|----|-----------|
| 8.1 | Em movimento (moving flag = true) → verde intermitente a cada ~350 ms. |
| 8.2 | Bloqueado (erro alvo-vs-posição ≥ 8° e sem movimento) → vermelho fixo. |
| 8.3 | Inativo → cinzento. |

---

## 3. Controlo por teclado

### FR-KEY-1: Seleção de dedo
As teclas 1–4 selecionam o dedo ativo.

| AC | Critério |
|----|-----------|
| 1.1 | 1 = anelar, 2 = médio, 3 = indicador, 4 = polegar. |
| 1.2 | A barra de estado mostra o nome do dedo selecionado. |

### FR-KEY-2: Movimento com teclas de seta
As teclas de seta movem o dedo selecionado.

| AC | Critério |
|----|-----------|
| 2.1 | Cima = fechar (aumentar a posição), Baixo = abrir (diminuir). |
| 2.2 | Direita = aumentar o desvio lateral, Esquerda = diminuir. |

### FR-KEY-3: Modificadores de precisão
O tamanho do passo varia consoante a tecla modificadora.

| AC | Critério |
|----|-----------|
| 3.1 | Sem modificador: 1° (preciso). |
| 3.2 | Shift: 5° (normal). |
| 3.3 | Ctrl: 10° (rápido). |
| 3.4 | A barra de estado mostra o nome do modo e o ângulo resultante. |

### FR-KEY-4: Ações rápidas
Atalhos de uma única tecla para ações comuns.

| AC | Critério |
|----|-----------|
| 4.1 | Q = fechar totalmente a 110°. |
| 4.2 | E = abrir totalmente a 0°. |
| 4.3 | C = centrar o lado em 0°. |

---

## 4. Controlos globais

### FR-GLOB-1: Abrir tudo
Coloca todos os dedos totalmente abertos.

| AC | Critério |
|----|-----------|
| 1.1 | Todos os `pos_var` → 0, todos os `side_var` → 0, posições enviadas para o hardware. |

### FR-GLOB-2: Fechar tudo
Coloca todos os dedos totalmente fechados.

| AC | Critério |
|----|-----------|
| 2.1 | Todos os `pos_var` → 110, todos os `side_var` → 0, posições enviadas. |

### FR-GLOB-3: Centrar tudo
Reinicia todos os desvios laterais.

| AC | Critério |
|----|-----------|
| 3.1 | Todos os `side_var` → 0, posições enviadas. |

### FR-GLOB-4: Velocidade global
Uma lista pendente define todas as velocidades dos dedos de uma só vez.

| AC | Critério |
|----|-----------|
| 4.1 | Selecionar um valor atualiza todas as caixas de combinação de velocidade por dedo. |
| 4.2 | Velocidade limitada a [1, 6]. |

---

## 5. Gestão de poses

### FR-POSE-1: Guardar pose
O utilizador introduz um nome e guarda as posições atuais dos 8 servos.

| AC | Critério |
|----|-----------|
| 1.1 | As posições dos 4 dedos (8 valores) são capturadas via `get_positions()`. |
| 1.2 | O nome é validado via `validate_name()` antes de guardar. |
| 1.3 | Em caso de sucesso: a lista pendente é atualizada (ordenada), o campo é limpo e a barra de estado confirma. |
| 1.4 | Um nome inválido ou vazio mostra uma caixa de mensagem de erro. |

### FR-POSE-2: Aplicar pose
Selecionar uma pose e clicar em Aplicar move a mão para essa pose.

| AC | Critério |
|----|-----------|
| 2.1 | As 8 posições são aplicadas a todos os widgets de dedo. |
| 2.2 | As posições dos servos são enviadas para o hardware. |
| 2.3 | O atraso é estimado a partir da distância de movimento e da velocidade; a conclusão da pose é registada após esse atraso com comparação entre alvo e real. |

### FR-POSE-3: Eliminar pose
Remove a pose selecionada após confirmação.

| AC | Critério |
|----|-----------|
| 3.1 | Uma caixa de mensagem sim/não pede confirmação. |
| 3.2 | Ao confirmar: a pose é removida da configuração, o YAML é guardado e a lista pendente é atualizada. |
| 3.3 | Se não restarem poses, a lista pendente mostra `<no poses>`. |

### FR-POSE-4: Validação de nomes
Os nomes são validados para evitar a corrupção do YAML.

| AC | Critério |
|----|-----------|
| 4.1 | Vazio / apenas espaços → rejeitado. |
| 4.2 | Mais de 50 caracteres → rejeitado. |
| 4.3 | Contém `: { } [ ] , & * # ? \| - < > = ! % @ \` " '` → rejeitado. |
| 4.4 | Contém caracteres de controlo (ASCII < 32) → rejeitado. |
| 4.5 | Espaços no início/fim → rejeitado. |

---

## 6. Gestão de sequências

### FR-SEQ-1: Reprodutor de sequências (janela principal)
Seleção por lista pendente, caixa de verificação Loop e botões Reproduzir / Pausar / Parar.

| AC | Critério |
|----|-----------|
| 1.1 | A lista pendente mostra todas as sequências guardadas (ou `<no sequences>`). |
| 1.2 | A caixa de verificação Loop ativa a repetição contínua. |
| 1.3 | Reproduzir inicia a sequência numa thread em segundo plano. |
| 1.4 | Pausar alterna entre pausa e retoma; o texto do botão alterna entre "⏸ Pause" e "▶ Resume". |
| 1.5 | Parar define `stop_sequence = True`; a thread da sequência termina. |

### FR-SEQ-2: Motor de execução de sequências
As sequências são executadas numa thread em segundo plano com pausas interrompíveis.

| AC | Critério |
|----|-----------|
| 2.1 | Os passos de pose analisam o formato `"pose_name:s1,s2,...,s8\|delay"`. |
| 2.2 | Os passos `SLEEP:duration` pausam sem comandos de hardware. |
| 2.3 | Sem atraso explícito: espera automática = `15.0 − (avg_speed − 1) × 2.4` segundos. |
| 2.4 | As pausas são executadas em incrementos de 0,1 s, verificando os sinalizadores de parar/pausar a cada ciclo. |
| 2.5 | No modo loop, um intervalo de 0,5 s separa as iterações. |
| 2.6 | Os nomes de pose desconhecidos são ignorados com um aviso. |
| 2.7 | Os botões Reproduzir/Pausar/Parar alternam entre o estado ativado/desativado durante a execução. |

### FR-SEQ-3: Caixa de diálogo do gestor de sequências
Caixa de diálogo de dois painéis, acedida através do botão "🔧 Manage".

| AC | Critério |
|----|-----------|
| 3.1 | Painel esquerdo: caixa de lista das sequências guardadas com botões Executar, Editar e Eliminar. |
| 3.2 | Clicar duas vezes executa a sequência uma vez (sem loop) sem fechar a caixa de diálogo. |
| 3.3 | Editar carrega os passos no construtor, preenchendo previamente o campo do nome. |

### FR-SEQ-4: Construtor de sequências
Painel direito para construir sequências a partir de poses.

| AC | Critério |
|----|-----------|
| 4.1 | Lista das poses disponíveis; clicar duas vezes adiciona um passo com a velocidade/atraso atuais. |
| 4.2 | Caixas numéricas de velocidade por dedo (1–6); "⬇ Copy from UI" importa as velocidades da janela principal. |
| 4.3 | O campo de atraso acrescenta o sufixo `\|delay` aos passos de pose. |
| 4.4 | "⏱ Delay" insere um passo autónomo `SLEEP:Xs`. |
| 4.5 | ↑/↓ reordenam, ➖ remove, 🗑 limpa tudo. |
| 4.6 | "💾 Save Sequence" valida o nome, guarda e atualiza as listas pendentes. |
| 4.7 | "▶ Execute" executa a sequência construída sem guardar nem fechar a caixa de diálogo. |

### FR-SEQ-5: Validação da entrada de atraso
Os valores decimais inválidos no campo de atraso são tratados de forma tolerante.

| AC | Critério |
|----|-----------|
| 5.1 | Um atraso não numérico assume por omissão ausência de atraso (passo adicionado sem `\|delay`). |
| 5.2 | Um atraso SLEEP não numérico mostra "Invalid delay value" na barra de estado. |

---

## 7. Monitorização dos servos

### FR-MON-1: Recolha de telemetria em segundo plano
Uma thread daemon consulta os 8 servos a ~10 Hz.

| AC | Critério |
|----|-----------|
| 1.1 | A thread pausa 0,1 s entre iterações. |
| 1.2 | Métricas recolhidas por servo: posição, carga, temperatura, tensão, velocidade, sinalizador de movimento, estado e alvo. |
| 1.3 | Uma leitura falhada repete o último valor conhecido para manter os arrays sincronizados. |
| 1.4 | Os dados de feedback são atualizados sob `feedback_lock` de forma atómica. |

### FR-MON-2: Apresentação do gráfico
Gráfico Matplotlib incorporado no painel direito.

| AC | Critério |
|----|-----------|
| 2.1 | Métricas selecionáveis: Posição, Alvo vs Atual, Binário, Velocidade, Temperatura, Tensão e Movimento. |
| 2.2 | A lista pendente "Servos" alterna quais dos 8 traçados estão visíveis (com ✓ All / ✕ None). |
| 2.3 | Os redesenhos do gráfico são limitados a intervalos ≥100 ms. |
| 2.4 | Nenhuma métrica selecionada → mensagem "Select at least one metric". |
| 2.5 | Sem dados → mensagem "Waiting for data...". |

### FR-MON-3: Modos do gráfico
Dois modos: Multi-Servo e Osciloscópio.

| AC | Critério |
|----|-----------|
| 3.1 | O modo Osciloscópio mostra um seletor "Scope Servo" para focar num único servo. |
| 3.2 | O modo Multi-Servo oculta o seletor Scope Servo. |

### FR-MON-4: Zoom e deslocamento do gráfico
Quatro controlos deslizantes para controlar a vista.

| AC | Critério |
|----|-----------|
| 4.1 | Y-Zoom: 0,2× a 5,0×, padrão 1,1×. |
| 4.2 | Y-Pan: −3,0 a +3,0, padrão 0,0. |
| 4.3 | Time-Zoom: 10 % a 100 % dos dados disponíveis. |
| 4.4 | Time-Pan: 0 % (mais antigo) a 100 % (mais recente). |
| 4.5 | Todos os controlos deslizantes desencadeiam redesenhos do gráfico com debounce. |

### FR-MON-5: Modo rolling
Limita o gráfico aos N pontos de dados mais recentes.

| AC | Critério |
|----|-----------|
| 5.1 | Quando ativado e os dados excedem `max_data_points` (100), as amostras mais antigas são descartadas. |
| 5.2 | Desativar o modo rolling mantém todos os dados recolhidos. |

### FR-MON-6: Pausar / Retomar / Limpar gráfico

| AC | Critério |
|----|-----------|
| 6.1 | Pausar interrompe os redesenhos do gráfico; a recolha de telemetria continua. |
| 6.2 | Limpar reinicia todos os arrays de dados e o zoom/pan para os padrões. |

### FR-MON-7: Painel de feedback
Tabela em grelha que mostra a telemetria ao vivo de todos os servos.

| AC | Critério |
|----|-----------|
| 7.1 | Colunas: S1–S8. Linhas: Goal, Position, Speed, Torque, Voltage, Current, Temperature, Status, Moving. |
| 7.2 | Os valores são formatados por `format_feedback_value()`: posição `X.XX°`, velocidade `X.X°/s`, tensão `X.XX V`, temperatura `X.X °C`, corrente `X mA`, carga `X.X %`, estado `0xHH`, movimento `Yes/No`. |
| 7.3 | Só as células alteradas são atualizadas (cache de diferenças). |
| 7.4 | A atualização é limitada a ≥50 ms entre atualizações. |

---

## 8. Configuração

### FR-CFG-1: Carregamento da configuração da aplicação
`config.yaml` é carregado com valores padrão para todas as chaves em falta.

| AC | Critério |
|----|-----------|
| 1.1 | Ficheiro em falta → é usada a configuração padrão completa. |
| 1.2 | Chaves em falta fundidas a partir dos padrões (fusão a dois níveis). |
| 1.3 | Falha de análise → são devolvidos os padrões e o erro é impresso em stdout. |

### FR-CFG-2: Mapeamento dos servos
Os IDs dos servos por dedo são definidos em `config.yaml` → `servos`.

| AC | Critério |
|----|-----------|
| 2.1 | A configuração define pointer=[1,2], middle=[3,4], ring=[5,6], thumb=[7,8]. |
| 2.2 | `all_ids` = [1,2,3,4,5,6,7,8]. |

### FR-CFG-3: Limites de ângulo

| AC | Critério |
|----|-----------|
| 3.1 | `servo_min` = −40, `servo_max` = 110, `base_min` = 0, `base_max` = 110, `side_min` = −40, `side_max` = 40. |
| 3.2 | Todos os intervalos dos controlos deslizantes derivam destes valores. |

### FR-CFG-4: Extremos automáticos
Pontos finais de interpolação bilinear para o cálculo do desvio lateral.

| AC | Critério |
|----|-----------|
| 4.1 | `left_open`, `right_open`, `left_closed`, `right_closed`, `center_open` e `center_closed` são configuráveis. |
| 4.2 | `compute_auto_positions()` usa estes valores para a interpolação. |

### FR-CFG-5: Configuração de velocidade

| AC | Critério |
|----|-----------|
| 5.1 | `speeds.default` = 3, `speeds.min` = 1, `speeds.max` = 6. |

---

## 9. Ferramenta CLI

### FR-CLI-1: Listar poses e sequências
`--list` imprime todas as poses e sequências sem abrir uma ligação.

| AC | Critério |
|----|-----------|
| 1.1 | A saída mostra o número de poses e cada nome com as posições. |
| 1.2 | A saída mostra o número de sequências e cada nome com o número de passos e detalhes. |
| 1.3 | Não é aberta qualquer ligação série. |

### FR-CLI-2: Aplicar pose
`--pose NAME` envia uma pose guardada para o hardware.

| AC | Critério |
|----|-----------|
| 2.1 | As posições são carregadas da configuração; a velocidade padrão 3 é aplicada a todos os servos. |
| 2.2 | Pose desconhecida → erro + `sys.exit(1)`. |

### FR-CLI-3: Reproduzir sequência
`--sequence NAME` reproduz uma sequência; `--loop` repete até Ctrl+C.

| AC | Critério |
|----|-----------|
| 3.1 | As velocidades e o atraso são analisados a partir da cadeia do passo. |
| 3.2 | Os passos `SLEEP` pausam sem comandos de hardware. |
| 3.3 | Sem atraso explícito → espera automática = `15.0 − (avg_speed − 1) × 2.4` segundos. |
| 3.4 | O SIGINT define `stop_flag` para uma interrupção controlada. |
| 3.5 | Sequência desconhecida → sair com erro. |
| 3.6 | Sequência vazia → sair com erro. |
| 3.7 | As poses desconhecidas dentro de uma sequência são ignoradas com um WARNING. |

### FR-CLI-4: Análise de passos
`parse_step()` trata vários formatos.

| AC | Critério |
|----|-----------|
| 4.1 | `SLEEP:2.0s` → pausa de 2,0 s. |
| 4.2 | `open:3,3,...\|2.0s` → pose "open" com velocidades e atraso de 2,0 s. |
| 4.3 | `open` (nome simples) → pose com velocidades padrão, sem atraso. |
| 4.4 | Velocidades com menos de 8 são preenchidas com 3; as mais longas são truncadas. |
| 4.5 | O sufixo de duração `s` / `S` é removido. |

### FR-CLI-5: Ações mutuamente exclusivas
`--list`, `--pose` e `--sequence` são mutuamente exclusivos.

| AC | Critério |
|----|-----------|
| 5.1 | Passar várias ações → saída com código não nulo. |
| 5.2 | `--loop` sem `--sequence` → erro. |

### FR-CLI-6: Substituição do ficheiro de configuração
`--config PATH` usa um ficheiro YAML alternativo.

| AC | Critério |
|----|-----------|
| 6.1 | Ficheiro em falta → erro + `sys.exit(1)`. |

---

## 10. Persistência de dados

### FR-DATA-1: Ficheiro de configuração YAML
As poses e sequências são armazenadas em `data/hand_config.yaml`.

| AC | Critério |
|----|-----------|
| 1.1 | O ficheiro usa o formato YAML com as chaves de nível superior `poses` e `sequences`. |

### FR-DATA-2: Carregar configuração

| AC | Critério |
|----|-----------|
| 2.1 | Ficheiro em falta → `{'poses': {}, 'sequences': {}}`. |
| 2.2 | Ficheiro vazio → chaves preenchidas automaticamente. |
| 2.3 | YAML malformado → estrutura vazia, erro impresso em stdout. |

### FR-DATA-3: Guardar configuração com arrays inline
As posições são guardadas em estilo flow através de pós-processamento com expressões regulares.

| AC | Critério |
|----|-----------|
| 3.1 | O ficheiro contém o estilo `positions: [v1, v2, …, v8]`. |
| 3.2 | Os valores negativos são preservados no formato inline. |
| 3.3 | Devolve `True` em caso de sucesso e `False` em caso de erro. |

### FR-DATA-4: Criação automática da pasta de dados

| AC | Critério |
|----|-----------|
| 4.1 | A pasta `data/` é criada, caso não exista, antes da escrita. |

### FR-DATA-5: Integridade de ida e volta
Os dados escritos pela GUI podem ser lidos pela CLI e vice-versa.

| AC | Critério |
|----|-----------|
| 5.1 | Poses, posições negativas e passos de sequência sobrevivem a uma ida e volta GUI-guarda → CLI-lê. |

---

## 11. Tratamento de erros

### FR-ERR-1: Erro de ligação
As ligações falhadas não fazem a aplicação colapsar.

| AC | Critério |
|----|-----------|
| 1.1 | A barra de estado mostra "Connection failed: …"; `connected` permanece `False`. |

### FR-ERR-2: Taxa de transmissão inválida

| AC | Critério |
|----|-----------|
| 2.1 | Taxa de transmissão não numérica → a barra de estado mostra "Invalid baudrate". |

### FR-ERR-3: Recuperação da thread de monitorização

| AC | Critério |
|----|-----------|
| 3.1 | Uma única falha de leitura de um servo não faz a thread colapsar. |
| 3.2 | Os erros são impressos em stdout. |

### FR-ERR-4: Degradação do sinalizador de movimento

| AC | Critério |
|----|-----------|
| 4.1 | Após 3 falhas consecutivas de `read_moving`, a supervisão é desativada com uma mensagem no registo. |
| 4.2 | Recorre de `sync_read_moving` para leituras por servo à primeira falha de sincronização. |

### FR-ERR-5: Avisos de conclusão de pose

| AC | Critério |
|----|-----------|
| 5.1 | Um erro entre alvo e real > 5° desencadeia um aviso ⚠ no registo. |
| 5.2 | Um timeout de movimento (6,0 s) desencadeia um aviso de timeout se os servos nunca pararem de se mover. |

### FR-ERR-6: Configuração em falta (CLI)

| AC | Critério |
|----|-----------|
| 6.1 | Ficheiro de configuração em falta → mensagem de erro + `sys.exit(1)`. |

### FR-ERR-7: Sequência vazia / inválida

| AC | Critério |
|----|-----------|
| 7.1 | Passos de sequência vazios → `sys.exit(1)`. |
| 7.2 | Poses desconhecidas na sequência → ignoradas com WARNING. |

---

## 12. Disposição da interface

### FR-UI-1: Estrutura da janela

| AC | Critério |
|----|-----------|
| 1.1 | O título inclui a versão: "AmazingHand Controller v0.8". |
| 1.2 | Geometria inicial: 1920×1200. |
| 1.3 | Um `PanedWindow` horizontal separa os painéis esquerdo (controlos) e direito (gráfico). |

### FR-UI-2: Painel esquerdo

| AC | Critério |
|----|-----------|
| 2.1 | Linha 1: anelar, médio, indicador (3 dedos lado a lado). |
| 2.2 | Linha 2: polegar (à direita) + controlos empilhados (ligação, globais, pose, sequência). |
| 2.3 | Registo de execução abaixo dos controlos num separador vertical redimensionável. |

### FR-UI-3: Barra de estado

| AC | Critério |
|----|-----------|
| 3.1 | Atualiza-se na ligação, desconexão, seleção de dedo, alteração de velocidade, operações de pose e erros. |

### FR-UI-4: Registo de execução

| AC | Critério |
|----|-----------|
| 4.1 | As mensagens são prefixadas com um timestamp `[HH:MM:SS.mmm]`. |
| 4.2 | Desloca-se automaticamente para a entrada mais recente. |
| 4.3 | As mensagens são também impressas em stdout. |

### FR-UI-5: Dicas (tooltips)

| AC | Critério |
|----|-----------|
| 5.1 | Uma janela amarela aparece após 500 ms de passagem do rato, posicionada em baixo à direita do widget. |
| 5.2 | Desaparece quando o rato sai ou se prime um botão. |

### FR-UI-6: Painel direito (área do gráfico)

| AC | Critério |
|----|-----------|
| 6.1 | `PanedWindow` vertical: gráfico em cima (mín. 200 px) e feedback em baixo (mín. 150 px). |
| 6.2 | Controlos deslizantes de tempo abaixo do gráfico; controlos deslizantes de Y à direita. |

### FR-UI-7: Ajuda da CLI

| AC | Critério |
|----|-----------|
| 7.1 | `--help` sai com 0 e mostra todas as opções. |

### FR-UI-8: Argumentos de linha de comandos da GUI

| AC | Critério |
|----|-----------|
| 8.1 | `--port` substitui a porta série padrão. |
| 8.2 | `--baudrate` substitui a taxa de transmissão padrão (1000000). |

---

## Resumo da cobertura de testes

| Ficheiro de teste | Âmbito | Contagem |
|-----------|-------|-------|
| `tests/test_hand_logic.py` | `load_app_config` (6), `servo_mapping` (3), `angle_limits` (1), `auto_extremes` (2), `speed_config` (1), `default_serial_port` (2), `ensure_data_dir` (2), `load_pose_definitions` (3), `compute_auto_positions` (6), `decompose_servo_positions` (5), `coerce_numeric` (11), `coerce_angle_degrees` (6), `coerce_bool` (6), `load_to_percent` (7), `estimate_current_from_load` (5), `format_feedback_value` (12), `get_time_window_indices` (8), `angle_rad` (3) | 89 |
| `tests/test_gui_utils.py` | `validate_name` (21), `clamp` (8), `load_config` (6), `save_config` (6) | 41 + 10 parametrizados |
| `tests/test_cmd.py` | `angle_rad` (8), `parse_step` (11), `cmd_list` (4), `load_config` (2), `apply_pose` (6), `_interruptible_sleep` (2), `auto_wait` (3), `mutual_exclusion` (1), `config_override` (2) | 41 |
| `tests/test_integration.py` | `cmd_pose` e2e (5), `cmd_sequence` e2e (6), ida e volta da configuração (3) | 14 |
| `tests/test_system.py` | Subprocesso da CLI: `--help` (5), `--list` (9), opções de `--help` (3), caminhos de erro (5) | 22 |
| `tests/test_system_hardware.py` | Hardware real: ligação (2), ligação via CLI (2), aplicação de pose (3), velocidade (2), telemetria (6), sequência (2), recuperação de erros (1), movimento (2), desconexão (1) — **requer a flag `--hardware`** | 21 |
| **Total (sem hardware)** | **217 testes** |
| **Total (com hardware)** | **238 testes** |
