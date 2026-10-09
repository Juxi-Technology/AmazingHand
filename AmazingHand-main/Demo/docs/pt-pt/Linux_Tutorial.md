[English](../en/Linux_Tutorial.md) | [Deutsch](../de/Linux_Tutorial.md) | [Español](../es/Linux_Tutorial.md) | [Français](../fr/Linux_Tutorial.md) | [Italiano](../it/Linux_Tutorial.md) | [日本語](../ja/Linux_Tutorial.md) | [한국어](../ko/Linux_Tutorial.md) | [Português (BR)](../pt-br/Linux_Tutorial.md) | Português (PT) | [简体中文](../zh-hans/Linux_Tutorial.md) | [繁體中文](../zh-hant/Linux_Tutorial.md)

# AmazingHand — Hand-Tracking da Mão Dextra · Tutorial Linux (Ubuntu)

Este tutorial aborda a Demo oficial do AmazingHand (mão dextra da Pollen Robotics) com scripts de instalação com um clique.
Execute os scripts na ordem numérica. **Todos os scripts estão em `Demo/Linux_Deploy_Scripts/` — execute `./script` num terminal.**

---

## Índice

1. [Preparação de hardware](#1-preparação-de-hardware)
2. [Conceder permissões aos scripts (importante)](#2-conceder-permissões-aos-scripts-importante)
3. [Configuração do ambiente (Script 1)](#3-configuração-do-ambiente-script-1)
4. [Ligações](#4-ligações)
5. [Configuração da porta série (Script 2)](#5-configuração-da-porta-série-script-2)
6. [Instalação do código (Script 3)](#6-instalação-do-código-script-3)
7. [Executar a demo (Script 4)](#7-executar-a-demo-script-4)
8. [Limpeza do projeto (Script 0)](#8-limpeza-do-projeto-script-0)
9. [Resolução de problemas e notas](#9-resolução-de-problemas-e-notas)
10. [Estrutura do código](#10-estrutura-do-código)

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

## 2. Conceder permissões aos scripts (importante)

**Quando os scripts são copiados do Windows ou de um zip para o Linux, a permissão de execução (`+x`) perde-se** — executá-los diretamente dá
`Permission denied`. **Execute isto uma vez antes da primeira utilização:**

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

Faz automaticamente:

1. **Instala o Rust** (rustup + toolchain stable)
2. **Configura o espelho tuna do cargo** (`~/.cargo/config.toml`) para acelerar as descargas de crates
3. **Instala o uv** (gestor de pacotes Python)
4. **Instala o dora-cli 0.5.0** (`cargo install`, a primeira compilação demora ~10–20 min, tenha paciência). As versões antigas do dora são detetadas automaticamente e substituídas à força.
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

### Espelho tuna do cargo (~/.cargo/config.toml)

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

## 4. Ligações

- Ligue a placa controladora de servos ao PC por USB, **alimente-a com uma fonte externa de 5V 4A**
- Encontre a porta:
  ```bash
  ls /dev/ttyUSB* /dev/ttyACM*
  ```
  Normalmente `/dev/ttyACM0`

---

## 5. Configuração da porta série (Script 2)

**Execute `./2-Setup_Serial.sh`**:

1. "Ligue a placa controladora" → prima Enter para procurar
2. As portas série detetadas são listadas (`/dev/ttyACM*` / `/dev/ttyUSB*`)
3. Uma única porta: prima Enter para confirmar; várias: escreva o índice
4. Escreve `--serialport` nos 3 ficheiros yml de dataflow e a porta predefinida em `AHControl/src/main.rs`
5. **Configura automaticamente as permissões da porta série**:
   ```bash
   sudo chmod 666 /dev/ttyACM0
   ```
   Recomendado: adicione o utilizador atual ao grupo dialout (evita voltar a introduzir a palavra-passe; saia e entre novamente para aplicar):
   ```bash
   sudo usermod -aG dialout $USER
   ```

> Se `ls /dev/ttyUSB* /dev/ttyACM*` não encontrar nada dentro de uma VM, ligue o dispositivo USB à VM nas configurações da VM.

---

## 6. Instalação do código (Script 3)

**Execute `./3-Deploy_Demo.sh`** — faz automaticamente:

1. Inicia o daemon do dora (`dora up`)
2. Cria um venv do Python 3.12 (`uv venv --python 3.12`)
3. Ativa o venv
4. Compila o nó Rust AHControl (`cargo build --release`, ~10 min na primeira vez)
5. Sincroniza as dependências do AHSimulation e do HandTracking (`uv sync`)
6. Instala à força o mediapipe==0.10.14 (armadilha conhecida, alternativa)

> Faça a instalação uma vez. Executar novamente pergunta se quer reconstruir o venv.

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

De seguida, executa `dora build` + `dora run`. Abre-se uma janela da câmara; faça gestos com a mão para mover a(s) mão(s) em tempo real. **Ctrl+C para parar**. Depois de o dataflow terminar, prima Enter para voltar ao menu e escolher outro modo, ou `q` para sair.

> O ambiente de trabalho do Linux precisa de permissão de câmara (Ubuntu: Configurações → Privacidade → Câmara). Certifique-se de que a câmara não está a ser usada por outra aplicação. Problemas de câmara em VM: consulte [9.6](#96-permissão-da-câmara--câmara-da-máquina-virtual-não-funciona).

---

## 8. Limpeza do projeto (Script 0)

**Execute `./0-Cleanup_Project.sh`**, escreva `Y` para confirmar:

1. Para o daemon do dora
2. Elimina os 3 ambientes virtuais (`.venv`)
3. Elimina a saída de compilação do Rust (`Demo/target`)
4. Elimina `__pycache__`, as cópias de segurança `.bak`, os registos e `Demo/out` (registos do dora)
5. **Restaura a porta predefinida** (`--serialport /dev/ttyACM0`), removendo os vestígios da porta desta máquina

> Após a limpeza, pode copiar a pasta `AmazingHand-main` completa para outra máquina — limpa e portátil.
> Na nova máquina, basta executar 1 → 2 → 3 → 4 pela ordem indicada.

---

## 9. Resolução de problemas e notas

### 9.1 `Permission denied` (o script não tem permissão de execução)

- Sintoma: `bash: ./1-Install_Env.sh: Permission denied`
- Causa: o script perdeu o bit de execução quando foi copiado do Windows / de um zip
- Solução:
  ```bash
  chmod +x *.sh
  ```
  Depois execute com `./script` (não `bash script`).

### 9.2 O cargo bloqueia em `Updating 'tuna' index`

- Causa: espelho configurado em **modo git-repo** (`.../git/crates.io-index.git`), a primeira execução descarrega mais de 1 GB de índice
- Solução: defina `~/.cargo/config.toml` com o **índice sparse** (ver 3.2), ou volte a executar `1-Install_Env.sh`

### 9.3 Submódulo solutions do mediapipe em falta / instalação danificada

```bash
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- Execute dentro do venv ativado (na pasta `Demo`)
- O `3-Deploy_Demo.sh` já faz isto como alternativa

### 9.4 Incompatibilidade de versões do dora (mensagem v0.8.0 vs v0.7.0)

- Sintoma: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- Causa: a versão do dora-cli é diferente da do dora-node-api. **Ambas têm de ser 0.5.0**
  - Verificação: `dora --version` deve imprimir `dora-cli 0.5.0` e `dora-message: 0.8.0`
  - O `1-Install_Env.sh` deteta agora automaticamente as versões antigas e instala a 0.5.0 à força

**Se houver um dora antigo (por exemplo, 0.4.1) no sistema, limpe-o primeiro:**

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

> Se `dora --version` ainda mostrar uma versão antiga, há outra cópia antiga escondida algures no PATH — use `which dora` para a encontrar e remover, e certifique-se de que `~/.cargo/bin` está no início do PATH.

### 9.5 Permissão negada na porta série

```bash
sudo chmod 666 /dev/ttyACM*
```

- Voltar a ligar o cabo pode repor as permissões
- Solução permanente: `sudo usermod -aG dialout $USER`, saia e entre novamente

### 9.6 Permissão da câmara / Câmara da máquina virtual não funciona

**Máquina real**:
- Ubuntu: Configurações → Privacidade → Câmara → permitir aplicações
- Certifique-se de que nenhuma outra aplicação (aplicação Câmara, Zoom, etc.) está a usar a webcam

**Câmara da máquina virtual (VMware) não funciona**:

Sintomas: `open VIDEOIO(V4L2:/dev/video0): can't open camera by index` ou `select() timeout`;
`/dev/video0` existe e o `v4l2-ctl` captura fotogramas, mas o `cap.read()` do OpenCV continua a devolver `ret = False`.

Diagnóstico e resolução (por ordem):

1. **Encaminhe a câmara para a VM**: Menu → VM → Removable Devices → Câmara → Connect
2. **Alterne a versão do controlador USB (a correção mais eficaz no VMware)**:
   - VM → Settings → **USB Controller** → alterne entre `USB 2.0` / `USB 3.1`
   - **Reinicie a VM** após a alteração
3. Verifique se o dispositivo existe:
   ```bash
   ls -l /dev/video0
   sudo usermod -aG video $USER   # add to video group, log out/in
   ```
4. Verifique se a câmara consegue realmente produzir fotogramas com o v4l2 (se sim, o controlador está bem e o problema é compatibilidade com o OpenCV):
   ```bash
   v4l2-ctl --device=/dev/video0 --set-fmt-video=width=640,height=480,pixelformat=MJPG --stream-mmap --stream-count=1 --stream-to=/tmp/frame.jpg
   ls -l /tmp/frame.jpg   # tens to hundreds of KB = stream works
   ```

### 9.7 O número da porta muda de cada vez

- Após voltar a ligar o USB, o nome do dispositivo pode mudar — volte a executar `2-Setup_Serial.sh`

### 9.8 OpenCV em falta

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
| `HandTracking` | Nó Python: seguimento de mãos com MediaPipe |
| `dataflow_*.yml` | Definições de dataflow do dora (grafo de nós) |
| `Linux_Deploy_Scripts` | Este pacote de scripts |

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

- A linha `args:` dos 3 ficheiros `dataflow_tracking_real_*.yml`: `--serialport /dev/ttyACMx`
- `AHControl/src/main.rs` `default_value = "/dev/ttyACM0"` (predefinição da serialport)
- `AHControl/config/*.toml`: modelo do servo, IDs, offsets (normalmente não é preciso alterar)
