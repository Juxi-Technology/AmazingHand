[English](../en/Linux_Tutorial.md) | [Deutsch](../de/Linux_Tutorial.md) | [Español](../es/Linux_Tutorial.md) | [Français](../fr/Linux_Tutorial.md) | [Italiano](../it/Linux_Tutorial.md) | [日本語](../ja/Linux_Tutorial.md) | [한국어](../ko/Linux_Tutorial.md) | Português (BR) | [Português (PT)](../pt-pt/Linux_Tutorial.md) | [简体中文](../zh-hans/Linux_Tutorial.md) | [繁體中文](../zh-hant/Linux_Tutorial.md)

# AmazingHand — Hand-Tracking da Mão Dextra · Tutorial Linux (Ubuntu)

Este tutorial cobre a Demo oficial do AmazingHand (mão dextra da Pollen Robotics) com scripts de implantação em um clique.
Execute os scripts na ordem numérica. **Todos os scripts estão em `Demo/Linux_Deploy_Scripts/` — execute `./script` em um terminal.**

---

## Sumário

1. [Preparação do hardware](#1-preparação-do-hardware)
2. [Conceder permissões aos scripts (importante)](#2-conceder-permissões-aos-scripts-importante)
3. [Configuração do ambiente (Script 1)](#3-configuração-do-ambiente-script-1)
4. [Ligação](#4-ligação)
5. [Configuração da porta serial (Script 2)](#5-configuração-da-porta-serial-script-2)
6. [Implantação do código (Script 3)](#6-implantação-do-código-script-3)
7. [Executar a demo (Script 4)](#7-executar-a-demo-script-4)
8. [Limpeza do projeto (Script 0)](#8-limpeza-do-projeto-script-0)
9. [Solução de problemas e observações](#9-solução-de-problemas-e-observações)
10. [Estrutura do código](#10-estrutura-do-código)

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

## 2. Conceder permissões aos scripts (importante)

**Quando os scripts são copiados do Windows ou de um zip para o Linux, a permissão de execução (`+x`) é perdida** — executá-los diretamente resulta em
`Permission denied`. **Execute isto uma vez antes do primeiro uso:**

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
chmod +x *.sh
```

Depois, cada script pode ser executado com `./script`. Ou combine:

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts" && chmod +x *.sh && ./1-Install_Env.sh
```

> Dica: para mover a pasta `AmazingHand-main` para o Linux mantendo as permissões, empacote com **tar**:
> `tar czf AmazingHand-main.tar.gz AmazingHand-main`, ou simplesmente execute `chmod +x *.sh` uma vez após descompactar.

---

## 3. Configuração do ambiente (Script 1)

Na pasta dos scripts, execute (após o `chmod +x` do passo 2):

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
./1-Install_Env.sh
```

Ele faz automaticamente:

1. **Instala o Rust** (rustup + toolchain stable)
2. **Configura a mirror tuna do cargo** (`~/.cargo/config.toml`) para acelerar o download de crates
3. **Instala o uv** (gerenciador de pacotes Python)
4. **Instala o dora-cli 0.5.0** (`cargo install`, a primeira compilação leva ~10–20 min, tenha paciência). Versões antigas do dora são detectadas automaticamente e substituídas à força.
5. **Instala o pacote pip dora-rs** (opcional)

> **Importante**: **Feche e reabra o terminal** após o script para que as variáveis de ambiente tenham efeito.
> Se alguma versão aparecer vazia, adicione a `~/.bashrc`:
>
> ```bash
> export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
> ```

### Instalação manual (se o script não for utilizável)

- **Rust**:
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```
- **uv**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **dora-cli**:
  ```bash
  cargo install dora-cli --version 0.5.0
  ```

### Mirror tuna do cargo (~/.cargo/config.toml)

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

## 4. Ligação

- Conecte a placa driver de servos ao PC com USB, **alimente-a com uma fonte externa de 5V 4A**
- Localize a porta:
  ```bash
  ls /dev/ttyUSB* /dev/ttyACM*
  ```
  Geralmente `/dev/ttyACM0`

---

## 5. Configuração da porta serial (Script 2)

**Execute `./2-Setup_Serial.sh`**:

1. "Conecte a placa driver" → pressione Enter para escanear
2. As portas seriais detectadas são listadas (`/dev/ttyACM*` / `/dev/ttyUSB*`)
3. Uma única porta: pressione Enter para confirmar; várias: digite o índice
4. Ele grava `--serialport` nos 3 arquivos yml de dataflow e a porta padrão em `AHControl/src/main.rs`
5. **Configura as permissões da serial automaticamente**:
   ```bash
   sudo chmod 666 /dev/ttyACM0
   ```
   Recomendado: adicione o usuário atual ao grupo dialout (evita digitar a senha novamente; saia e entre novamente para aplicar):
   ```bash
   sudo usermod -aG dialout $USER
   ```

> Se `ls /dev/ttyUSB* /dev/ttyACM*` não encontrar nada dentro de uma VM, conecte o dispositivo USB à VM nas configurações da VM.

---

## 6. Implantação do código (Script 3)

**Execute `./3-Deploy_Demo.sh`** — ele faz automaticamente:

1. Inicia o daemon do dora (`dora up`)
2. Cria um venv do Python 3.12 (`uv venv --python 3.12`)
3. Ativa o venv
4. Compila o nó Rust AHControl (`cargo build --release`, ~10 min na primeira vez)
5. Sincroniza as dependências de AHSimulation e HandTracking (`uv sync`)
6. Instala à força o mediapipe==0.10.14 (armadilha conhecida, fallback)

> Faça a implantação uma vez. Executar novamente pergunta se você quer reconstruir o venv.

---

## 7. Executar a demo (Script 4)

**Execute `./4-Run_Demo.sh`** — menu interativo:

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

> A área de trabalho do Linux precisa de permissão de câmera (Ubuntu: Configurações → Privacidade → Câmera). Certifique-se de que a câmera não esteja sendo usada por outro aplicativo. Problemas de câmera em VM: consulte [9.6](#96-permissão-da-câmera--câmera-da-máquina-virtual-não-funciona).

---

## 8. Limpeza do projeto (Script 0)

**Execute `./0-Cleanup_Project.sh`**, digite `Y` para confirmar:

1. Para o daemon do dora
2. Exclui os 3 ambientes virtuais (`.venv`)
3. Exclui a saída de compilação do Rust (`Demo/target`)
4. Exclui `__pycache__`, os backups `.bak`, os logs e `Demo/out` (logs do dora)
5. **Restaura a porta padrão** (`--serialport /dev/ttyACM0`), removendo os resíduos de porta desta máquina

> Após a limpeza, você pode copiar a pasta `AmazingHand-main` inteira para outra máquina — limpa e portátil.
> Na nova máquina, basta executar 1 → 2 → 3 → 4 na ordem.

---

## 9. Solução de problemas e observações

### 9.1 `Permission denied` (o script não tem permissão de execução)

- Sintoma: `bash: ./1-Install_Env.sh: Permission denied`
- Causa: o script perdeu o bit de execução ao ser copiado do Windows / de um zip
- Solução:
  ```bash
  chmod +x *.sh
  ```
  Depois execute com `./script` (não `bash script`).

### 9.2 cargo travado em `Updating 'tuna' index`

- Causa: mirror configurada no **modo repositório git** (`.../git/crates.io-index.git`), a primeira execução baixa um índice de 1 GB+
- Solução: defina `~/.cargo/config.toml` com o **índice sparse** (veja 3.2), ou execute `1-Install_Env.sh` novamente

### 9.3 mediapipe sem o submódulo solutions / instalação quebrada

```bash
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- Execute dentro do venv ativado (na pasta `Demo`)
- `3-Deploy_Demo.sh` já faz isso como fallback

### 9.4 Incompatibilidade de versão do dora (mensagem v0.8.0 vs v0.7.0)

- Sintoma: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Causa: a versão do dora-cli difere da do dora-node-api. **Ambas devem ser 0.5.0**
  - Verificação: `dora --version` deve imprimir `dora-cli 0.5.0` e `dora-message: 0.8.0`
  - O `1-Install_Env.sh` agora detecta automaticamente versões antigas e instala à força a 0.5.0

**Se um dora antigo (ex.: 0.4.1) estiver no sistema, limpe-o primeiro:**

```bash
# 1. Find where the old dora is
which dora
ls -la ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora 2>/dev/null

# 2. Delete the found old versions (adjust paths; there may be several)
rm -f ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora

# 3. Force-install 0.5.0 (goes to ~/.cargo/bin)
cargo install dora-cli --version 0.5.0 --force

# 4. Verify (should print dora-cli 0.5.0 / dora-message: 0.8.0)
dora --version
```

> Se `dora --version` ainda mostrar uma versão antiga, outra cópia antiga está escondida em algum lugar no PATH — use `which dora` para encontrá-la e removê-la, e certifique-se de que `~/.cargo/bin` esteja no início do PATH.

### 9.5 Permissão negada na porta serial

```bash
sudo chmod 666 /dev/ttyACM*
```

- Reconectar pode redefinir as permissões
- Solução permanente: `sudo usermod -aG dialout $USER`, saia e entre novamente

### 9.6 Permissão da câmera / Câmera da máquina virtual não funciona

**Máquina real**:
- Ubuntu: Configurações → Privacidade → Câmera → permitir aplicativos
- Certifique-se de que nenhum outro aplicativo (app de Câmera, Zoom etc.) esteja usando a webcam

**Câmera da máquina virtual (VMware) não funciona**:

Sintomas: `open VIDEOIO(V4L2:/dev/video0): can't open camera by index` ou `select() timeout`;
`/dev/video0` existe e o `v4l2-ctl` captura quadros, mas o `cap.read()` do OpenCV continua retornando `ret = False`.

Diagnóstico e correção (na ordem):

1. **Encaminhe a câmera para a VM**: Menu → VM → Removable Devices → Câmera → Connect
2. **Troque a versão do controlador USB (correção mais eficaz no VMware)**:
   - VM → Settings → **USB Controller** → alterne entre `USB 2.0` / `USB 3.1`
   - **Reinicie a VM** após a troca
3. Verifique se o dispositivo existe:
   ```bash
   ls -l /dev/video0
   sudo usermod -aG video $USER   # add to video group, log out/in
   ```
4. Verifique se a câmera consegue realmente produzir quadros com o v4l2 (se sim, o driver está OK e o problema é compatibilidade com o OpenCV):
   ```bash
   v4l2-ctl --device=/dev/video0 --set-fmt-video=width=640,height=480,pixelformat=MJPG --stream-mmap --stream-count=1 --stream-to=/tmp/frame.jpg
   ls -l /tmp/frame.jpg   # tens to hundreds of KB = stream works
   ```

### 9.7 O número da porta muda a cada vez

- Após reconectar o USB, o nome do dispositivo pode mudar — execute `2-Setup_Serial.sh` novamente

### 9.8 OpenCV ausente

```bash
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(na pasta `HandTracking`, com o venv ativado)

---

## 10. Estrutura do código

### Pasta Demo

| Caminho | Descrição |
|---|---|
| `AHControl` | Nó Rust que controla os servos. Entrada: `src/main.rs` |
| `AHSimulation` | Nó Python: simulação MuJoCo + cinemática inversa (mink) |
| `HandTracking` | Nó Python: rastreamento de mãos com MediaPipe |
| `dataflow_*.yml` | Definições de dataflow do dora (grafo de nós) |
| `Linux_Deploy_Scripts` | Este pacote de scripts |

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

- A linha `args:` dos 3 arquivos `dataflow_tracking_real_*.yml`: `--serialport /dev/ttyACMx`
- `AHControl/src/main.rs` `default_value = "/dev/ttyACM0"` (padrão da serialport)
- `AHControl/config/*.toml`: modelo do servo, IDs, offsets (normalmente não precisa alterar)
