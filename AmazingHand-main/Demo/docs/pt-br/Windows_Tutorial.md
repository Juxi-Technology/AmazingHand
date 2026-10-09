[English](../en/Windows_Tutorial.md) | [Deutsch](../de/Windows_Tutorial.md) | [Español](../es/Windows_Tutorial.md) | [Français](../fr/Windows_Tutorial.md) | [Italiano](../it/Windows_Tutorial.md) | [日本語](../ja/Windows_Tutorial.md) | [한국어](../ko/Windows_Tutorial.md) | Português (BR) | [Português (PT)](../pt-pt/Windows_Tutorial.md) | [简体中文](../zh-hans/Windows_Tutorial.md) | [繁體中文](../zh-hant/Windows_Tutorial.md)

# AmazingHand — Hand-Tracking da Mão Dextra · Tutorial Windows

Este tutorial cobre a Demo oficial do AmazingHand (mão dextra da Pollen Robotics) com scripts de implantação em um clique.
Execute os scripts na ordem numérica. **Todos os scripts estão em `Demo\Windows_Deploy_Scripts\` — dê um duplo clique para executar.**

---

## Sumário

1. [Preparação do hardware](#1-preparação-do-hardware)
2. [Configuração do ambiente (Script 1)](#2-configuração-do-ambiente-script-1)
3. [Ligação](#3-ligação)
4. [Configuração da porta serial (Script 2)](#4-configuração-da-porta-serial-script-2)
5. [Implantação do código (Script 3)](#5-implantação-do-código-script-3)
6. [Executar a demo (Script 4)](#6-executar-a-demo-script-4)
7. [Limpeza do projeto (Script 0)](#7-limpeza-do-projeto-script-0)
8. [Solução de problemas e observações](#8-solução-de-problemas-e-observações)
9. [Estrutura do código](#9-estrutura-do-código)

---

## 1. Preparação do hardware

| Item | Requisito |
|---|---|
| Mão dextra | Direita / Esquerda / Ambas |
| Placa driver de servos | Externa, USB para o PC |
| Alimentação | **Pelo menos 5V 4A** (só a USB não basta, use uma fonte externa) |
| Câmera | Integrada ou webcam USB |

> Os arquivos de modelo (URDF etc.) podem ser visualizados/baixados no [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e).

---

## 2. Configuração do ambiente (Script 1)

**Dê um duplo clique em `1-Install_Env.bat`** — ele faz automaticamente:

1. **Verifica as ferramentas de build do MSVC** (cl.exe) — necessárias para compilar o Rust. Se estiverem faltando, instale as
   Visual Studio 2022 Build Tools com a carga de trabalho "Desenvolvimento para desktop com C++" e reabra o terminal.
2. **Instala o Rust** (rustup + toolchain stable-msvc)
3. **Configura a mirror tuna do cargo** (`C:\Users\<you>\.cargo\config.toml`) para acelerar o download de crates
4. **Instala o uv** (gerenciador de pacotes Python)
5. **Instala o dora-cli 0.5.0** (`cargo install`, a primeira compilação leva ~10–20 min, tenha paciência)
6. **Instala o pacote pip dora-rs** (opcional; ele também é instalado no venv durante a implantação)

> **Importante**: **Feche e reabra o terminal** após o script para que as variáveis de ambiente tenham efeito.
> Os downloads podem ser lentos dependendo da sua rede — aguarde, não interrompa.

### Instalação manual (se o script não for utilizável)

- **Rust**: <https://www.rust-lang.org/tools/install> — use o rustup-init.exe, toolchain MSVC padrão.
  - PATH: adicione `%USERPROFILE%\.cargo\bin`
- **uv**: PowerShell: `irm https://astral.sh/uv/install.ps1 | iex`
  - PATH: adicione `%USERPROFILE%\.local\bin`
- **dora-cli**: `cargo install dora-cli --version 0.5.0`

### Mirror tuna do cargo (config.toml)

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

> Use o **índice sparse** (acima), NÃO a mirror do repositório git — a mirror git primeiro baixa ~1 GB de índice e costuma travar em `Updating 'tuna' index`.

---

## 3. Ligação

- Conecte a placa driver de servos ao PC com USB, **alimente-a com uma fonte externa de 5V 4A**
- Localize a porta: **Gerenciador de Dispositivos → Portas (COM e LPT)**, por exemplo `COM11`

---

## 4. Configuração da porta serial (Script 2)

**Dê um duplo clique em `2-Setup_Serial.bat`** (a lógica está em `2-Setup_Serial.ps1`):

1. "Conecte a placa driver" → pressione Enter para escanear
2. As portas COM detectadas são listadas (com os nomes dos dispositivos)
3. Uma única porta: pressione Enter para confirmar; várias: digite o índice
4. Ele grava `--serialport` nos 3 arquivos yml de dataflow e a porta padrão em `AHControl\src\main.rs`
5. Os arquivos originais são salvos como backup em `.bak`

> Se você reconectar o cabo USB, o número da COM pode mudar — execute este script novamente.

---

## 5. Implantação do código (Script 3)

**Dê um duplo clique em `3-Deploy_Demo.bat`** — ele faz automaticamente:

1. Inicia o daemon do dora (`dora up`)
2. Cria um venv do Python 3.12 (`uv venv --python 3.12`)
3. Ativa o venv
4. Compila o nó Rust AHControl (`cargo build --release`, ~10 min na primeira vez)
5. Sincroniza as dependências de AHSimulation e HandTracking (`uv sync`)
6. Instala à força o mediapipe==0.10.14 (armadilha conhecida, fallback)

> Faça a implantação uma vez. Executar novamente pergunta se você quer reconstruir o venv.

---

## 6. Executar a demo (Script 4)

**Dê um duplo clique em `4-Run_Demo.bat`** — menu interativo:

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

Em seguida, ele executa `dora build` + `dora run`. Uma janela da câmera se abre; faça gestos com a mão para mover a(s) mão(s) em tempo real. **Ctrl+C para parar**. Após o fim do dataflow, pressione Enter para voltar ao menu e escolher outro modo, ou `q` para sair.

> Na primeira execução, o Windows pode pedir permissão de câmera — clique em "Permitir".

---

## 7. Limpeza do projeto (Script 0)

**Dê um duplo clique em `0-Cleanup_Project.bat`**, digite `Y` para confirmar:

1. Para o daemon do dora
2. Exclui os 3 ambientes virtuais (`.venv`)
3. Exclui a saída de compilação do Rust (`Demo\target`)
4. Exclui `__pycache__`, os backups `.bak`, os logs e `Demo\out` (logs do dora)
5. **Restaura a porta padrão** (`--serialport /dev/ttyACM0`), removendo os resíduos de COM desta máquina

> Após a limpeza, você pode copiar a pasta `AmazingHand-main` inteira para outra máquina — limpa e portátil.
> Na nova máquina, basta executar 1 → 2 → 3 → 4 na ordem.

---

## 8. Solução de problemas e observações

### 8.1 cargo travado em `Updating 'tuna' index`

- Causa: mirror configurada no **modo repositório git** (`.../git/crates.io-index.git`), a primeira execução baixa um índice de 1 GB+
- Solução: defina `C:\Users\<you>\.cargo\config.toml` com o **índice sparse** (veja 2.3), ou execute `1-Install_Env.bat` novamente

### 8.2 mediapipe sem o submódulo solutions / instalação quebrada

```bat
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- Execute dentro do venv ativado (na pasta `Demo`)
- `3-Deploy_Demo.bat` já faz isso como fallback

### 8.3 Incompatibilidade de versão do dora (mensagem v0.8.0 vs v0.7.0)

- Sintoma: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Causa: a versão do dora-cli difere da do dora-node-api. **Ambas devem ser 0.5.0**
  - Verificação: `dora --version` deve imprimir `dora-cli 0.5.0` e `dora-message: 0.8.0`
  - Solução: `cargo install dora-cli --version 0.5.0 --force`
  - O `1-Install_Env.bat` agora detecta automaticamente versões antigas e instala à força a 0.5.0

### 8.4 Falha ao carregar modelos do MuJoCo / mediapipe (caminhos em chinês)

- Sintoma: `ParseXML: Error opening file '...\scene.xml'` ou `Can't find file: ...\.tflite`
- Causa: os carregadores C++ do MuJoCo 3.x / mediapipe falham em **caminhos absolutos que contêm caracteres não ASCII (chineses)** (por exemplo, `D:\Claude工作区\...`)
- Este projeto já inclui correções:
  - `AHSimulation\AHSimulation\mj_mink_*.py` muda o diretório de trabalho antes de carregar
  - `HandTracking\mediapipe_patch.py` usa caminhos curtos 8.3 + caminhos relativos
- **Não exclua esses arquivos de correção**

### 8.5 Permissão da câmera

- Primeira execução: escolha "Permitir"
- Configurações → Privacidade → Câmera → permitir aplicativos de desktop

### 8.6 O número da porta muda a cada vez

- Após reconectar o USB, o número da COM pode mudar — execute `2-Setup_Serial.bat` novamente

### 8.7 OpenCV ausente

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
| `HandTracking` | Nó Python: rastreamento de mãos com MediaPipe |
| `dataflow_*.yml` | Definições de dataflow do dora (grafo de nós) |
| `Windows_Deploy_Scripts` | Este pacote de scripts |

### Arquivos de dataflow

| Arquivo | Finalidade |
|---|---|
| `dataflow_tracking_simu.yml` | Simulação: gestos da webcam → mãos simuladas |
| `dataflow_tracking_real_right.yml` | Mão direita real |
| `dataflow_tracking_real_left.yml` | Mão esquerda real |
| `dataflow_tracking_real_2hands.yml` | Ambas as mãos reais (mesma placa driver) |

### Princípio do dataflow

```
Webcam → HandTracking (MediaPipe hand detection)
              ↓ hand keypoints
         AHSimulation (MuJoCo simulation + IK)
              ↓ joint target angles
         AHControl (serial → servo driver board → hand)
```

### Locais de configuração da porta

- A linha `args:` dos 3 arquivos `dataflow_tracking_real_*.yml`: `--serialport COMxx`
- `AHControl\src\main.rs` `default_value = "COMxx"` (padrão da serialport)
- `AHControl\config\*.toml`: modelo do servo, IDs, offsets (normalmente não precisa alterar)
