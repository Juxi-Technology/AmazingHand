[English](../en/Windows_Tutorial.md) | [Deutsch](../de/Windows_Tutorial.md) | [Español](../es/Windows_Tutorial.md) | [Français](../fr/Windows_Tutorial.md) | [Italiano](../it/Windows_Tutorial.md) | [日本語](../ja/Windows_Tutorial.md) | [한국어](../ko/Windows_Tutorial.md) | [Português (BR)](../pt-br/Windows_Tutorial.md) | Português (PT) | [简体中文](../zh-hans/Windows_Tutorial.md) | [繁體中文](../zh-hant/Windows_Tutorial.md)

# AmazingHand — Hand-Tracking da Mão Dextra · Tutorial Windows

Este tutorial aborda a Demo oficial do AmazingHand (mão dextra da Pollen Robotics) com scripts de instalação com um clique.
Execute os scripts na ordem numérica. **Todos os scripts estão em `Demo\Windows_Deploy_Scripts\` — faça duplo clique para executar.**

---

## Índice

1. [Preparação de hardware](#1-preparação-de-hardware)
2. [Configuração do ambiente (Script 1)](#2-configuração-do-ambiente-script-1)
3. [Ligações](#3-ligações)
4. [Configuração da porta série (Script 2)](#4-configuração-da-porta-série-script-2)
5. [Instalação do código (Script 3)](#5-instalação-do-código-script-3)
6. [Executar a demo (Script 4)](#6-executar-a-demo-script-4)
7. [Limpeza do projeto (Script 0)](#7-limpeza-do-projeto-script-0)
8. [Resolução de problemas e notas](#8-resolução-de-problemas-e-notas)
9. [Estrutura do código](#9-estrutura-do-código)

---

## 1. Preparação de hardware

| Item | Requisito |
|---|---|
| Mão dextra | Direita / Esquerda / Ambas |
| Placa controladora de servos | Externa, USB para o PC |
| Alimentação | **Pelo menos 5V 4A** (a USB sozinha não é suficiente, use uma fonte de alimentação externa) |
| Câmara | Integrada ou webcam USB |

> Os ficheiros de modelo (URDF, etc.) podem ser vistos/descarregados no [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e).

---

## 2. Configuração do ambiente (Script 1)

**Faça duplo clique em `1-Install_Env.bat`** — faz automaticamente:

1. **Verifica as MSVC build tools** (cl.exe) — necessárias para compilar o Rust. Se faltarem, instale o Visual Studio 2022 Build Tools com a carga de trabalho "Desktop development with C++" e, depois, reabra o terminal.
2. **Instala o Rust** (rustup + toolchain stable-msvc)
3. **Configura o espelho tuna do cargo** (`C:\Users\<you>\.cargo\config.toml`) para acelerar as descargas de crates
4. **Instala o uv** (gestor de pacotes Python)
5. **Instala o dora-cli 0.5.0** (`cargo install`, a primeira compilação demora ~10–20 min, tenha paciência)
6. **Instala o pacote pip dora-rs** (opcional; também é instalado no venv durante a instalação)

> **Importante**: **Feche e reabra o terminal** após o script para que as variáveis de ambiente tenham efeito.
> As descargas podem ser lentas consoante a sua rede — aguarde, não interrompa.

### Instalação manual (se o script não for utilizável)

- **Rust**: <https://www.rust-lang.org/tools/install> — use o rustup-init.exe, toolchain MSVC predefinida.
  - PATH: adicione `%USERPROFILE%\.cargo\bin`
- **uv**: PowerShell: `irm https://astral.sh/uv/install.ps1 | iex`
  - PATH: adicione `%USERPROFILE%\.local\bin`
- **dora-cli**: `cargo install dora-cli --version 0.5.0`

### Espelho tuna do cargo (config.toml)

```
[source.crates-io]
replace-with = "tuna"

[source.tuna]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[registries.tuna]
index = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[http]
check-revoke = false
```

> Use o **índice sparse** (acima), e NÃO o espelho do repositório git — o espelho git descarrega primeiro ~1 GB de índice e fica frequentemente bloqueado em `Updating 'tuna' index`.

---

## 3. Ligações

- Ligue a placa controladora de servos ao PC por USB, **alimente-a com uma fonte externa de 5V 4A**
- Encontre a porta: **Gestor de Dispositivos → Portas (COM & LPT)**, por exemplo `COM11`

---

## 4. Configuração da porta série (Script 2)

**Faça duplo clique em `2-Setup_Serial.bat`** (a lógica está em `2-Setup_Serial.ps1`):

1. "Ligue a placa controladora" → prima Enter para procurar
2. As portas COM detetadas são listadas (com os nomes dos dispositivos)
3. Uma única porta: prima Enter para confirmar; várias: escreva o índice
4. Escreve `--serialport` nos 3 ficheiros yml de dataflow e a porta predefinida em `AHControl\src\main.rs`
5. Os ficheiros originais são guardados como `.bak`

> Se voltar a ligar o cabo USB, o número da COM pode mudar — volte a executar este script.

---

## 5. Instalação do código (Script 3)

**Faça duplo clique em `3-Deploy_Demo.bat`** — faz automaticamente:

1. Inicia o daemon do dora (`dora up`)
2. Cria um venv do Python 3.12 (`uv venv --python 3.12`)
3. Ativa o venv
4. Compila o nó Rust AHControl (`cargo build --release`, ~10 min na primeira vez)
5. Sincroniza as dependências do AHSimulation e do HandTracking (`uv sync`)
6. Instala à força o mediapipe==0.10.14 (armadilha conhecida, alternativa)

> Faça a instalação uma vez. Executar novamente pergunta se quer reconstruir o venv.

---

## 6. Executar a demo (Script 4)

**Faça duplo clique em `4-Run_Demo.bat`** — menu interativo:

```
============================================
  Select a run mode:
============================================
   1 - Simulation (webcam hand tracking)
   2 - Real hardware
   q - Quit
============================================
Enter number [1/2/q]:
```

- **1**: Simulação — gestos da webcam controlam duas mãos simuladas
- **2**: Hardware real — submenu para mão direita / esquerda / ambas

```
============================================
  Real hardware - select the hand:
============================================
   1 - Right hand
   2 - Left hand
   3 - Both hands
   b - Back to main menu
============================================
```

De seguida, executa `dora build` + `dora run`. Abre-se uma janela da câmara; faça gestos com a mão para mover a(s) mão(s) em tempo real. **Ctrl+C para parar**. Depois de o dataflow terminar, prima Enter para voltar ao menu e escolher outro modo, ou `q` para sair.

> Na primeira execução, o Windows pode pedir permissão de câmara — clique em "Allow".

---

## 7. Limpeza do projeto (Script 0)

**Faça duplo clique em `0-Cleanup_Project.bat`**, escreva `Y` para confirmar:

1. Para o daemon do dora
2. Elimina os 3 ambientes virtuais (`.venv`)
3. Elimina a saída de compilação do Rust (`Demo\target`)
4. Elimina `__pycache__`, as cópias de segurança `.bak`, os registos e `Demo\out` (registos do dora)
5. **Restaura a porta predefinida** (`--serialport /dev/ttyACM0`), removendo os vestígios de COM desta máquina

> Após a limpeza, pode copiar a pasta `AmazingHand-main` completa para outra máquina — limpa e portátil.
> Na nova máquina, basta executar 1 → 2 → 3 → 4 pela ordem indicada.

---

## 8. Resolução de problemas e notas

### 8.1 O cargo bloqueia em `Updating 'tuna' index`

- Causa: espelho configurado em **modo git-repo** (`.../git/crates.io-index.git`), a primeira execução descarrega mais de 1 GB de índice
- Solução: defina `C:\Users\<you>\.cargo\config.toml` com o **índice sparse** (ver 2.3), ou volte a executar `1-Install_Env.bat`

### 8.2 Submódulo solutions do mediapipe em falta / instalação danificada

```bat
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- Execute dentro do venv ativado (na pasta `Demo`)
- O `3-Deploy_Demo.bat` já faz isto como alternativa

### 8.3 Incompatibilidade de versões do dora (mensagem v0.8.0 vs v0.7.0)

- Sintoma: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Causa: a versão do dora-cli é diferente da do dora-node-api. **Ambas têm de ser 0.5.0**
  - Verificação: `dora --version` deve imprimir `dora-cli 0.5.0` e `dora-message: 0.8.0`
  - Solução: `cargo install dora-cli --version 0.5.0 --force`
  - O `1-Install_Env.bat` deteta agora automaticamente as versões antigas e instala a 0.5.0 à força

### 8.4 Falha ao carregar modelos MuJoCo / mediapipe (caminhos em chinês)

- Sintoma: `ParseXML: Error opening file '...\scene.xml'` ou `Can't find file: ...\.tflite`
- Causa: os carregadores C++ do MuJoCo 3.x / mediapipe falham com **caminhos absolutos que contenham caracteres não ASCII (chineses)** (por exemplo, `D:\Claude工作区\...`)
- Este projeto já inclui correções:
  - `AHSimulation\AHSimulation\mj_mink_*.py` muda o diretório de trabalho antes de carregar
  - `HandTracking\mediapipe_patch.py` usa caminhos curtos 8.3 + caminhos relativos
- **Não elimine estes ficheiros de correção**

### 8.5 Permissão de câmara

- Primeira execução: escolha "Allow"
- Configurações → Privacidade → Câmara → permitir aplicações de ambiente de trabalho

### 8.6 O número da porta muda de cada vez

- Após voltar a ligar o USB, o número da COM pode mudar — volte a executar `2-Setup_Serial.bat`

### 8.7 OpenCV em falta

```bat
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(na pasta `HandTracking`, com o venv ativado)

---

## 9. Estrutura do código

### Pasta Demo

| Caminho | Descrição |
|---|---|
| `AHControl` | Nó Rust que controla os servos. Entrada: `src/main.rs` |
| `AHSimulation` | Nó Python: simulação MuJoCo + cinemática inversa (mink) |
| `HandTracking` | Nó Python: seguimento de mãos com MediaPipe |
| `dataflow_*.yml` | Definições de dataflow do dora (grafo de nós) |
| `Windows_Deploy_Scripts` | Este pacote de scripts |

### Ficheiros de dataflow

| Ficheiro | Finalidade |
|---|---|
| `dataflow_tracking_simu.yml` | Simulação: gestos da webcam → mãos simuladas |
| `dataflow_tracking_real_right.yml` | Mão direita real |
| `dataflow_tracking_real_left.yml` | Mão esquerda real |
| `dataflow_tracking_real_2hands.yml` | Ambas as mãos reais (mesma placa controladora) |

### Princípio do dataflow

```
Webcam → HandTracking (MediaPipe hand detection)
              ↓ hand keypoints
         AHSimulation (MuJoCo simulation + IK)
              ↓ joint target angles
         AHControl (serial → servo driver board → hand)
```

### Locais de configuração da porta

- A linha `args:` dos 3 ficheiros `dataflow_tracking_real_*.yml`: `--serialport COMxx`
- `AHControl\src\main.rs` `default_value = "COMxx"` (predefinição da serialport)
- `AHControl\config\*.toml`: modelo do servo, IDs, offsets (normalmente não é preciso alterar)
