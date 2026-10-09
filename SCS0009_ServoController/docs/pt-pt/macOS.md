[English](../en/macOS.md) | [Deutsch](../de/macOS.md) | [Español](../es/macOS.md) | [Français](../fr/macOS.md) | [Italiano](../it/macOS.md) | [日本語](../ja/macOS.md) | [한국어](../ko/macOS.md) | [Português (BR)](../pt-br/macOS.md) | Português (PT) | [简体中文](../zh-hans/macOS.md) | [繁體中文](../zh-hant/macOS.md)

# Ferramenta de Depuração do Servo SCS0009 — Guia macOS

Para macOS 11 (Big Sur) e posterior. Pontos-chave: nomenclatura da porta série (`cu.*` vs `tty.*`) e controladores USB.

> ⚠️ **Compatibilidade: esta ferramenta suporta atualmente apenas servos Feetech SCS0009 (série SCS, feedback por potenciómetro, resolução de 10 bits 0-1023)**. A tabela de registos e o formato xdat foram concebidos para o Feetech SCS0009; outros fabricantes/modelos não são garantidos.

---

## 1. Requisitos

| Dependência | Versão |
|-----------|---------|
| Python | >= 3.8 (recomenda-se 3.10+, via Homebrew) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| SO | macOS 11+ (Apple Silicon / Intel) |

## 2. Instalar o Python

Recomendado através do Homebrew:

```bash
# Install Homebrew if missing
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

Verifique:

```bash
python3 --version
```

## 3. Instalar as dependências

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Crie o ambiente virtual apenas UMA VEZ**. Executá-lo novamente irá redefinir/substituir o ambiente (apagando as dependências instaladas). Depois disso, basta executar `source .venv/bin/activate`.

## 4. ⚠️ Nomenclatura da porta série no macOS [Importante]

O macOS coloca os dispositivos série USB em `/dev` com **duas convenções de nomenclatura**:

| Prefixo | Significado | Utilizável |
|--------|---------|--------|
| `/dev/tty.usbserial-*` | estilo modem (bloqueante) | pode bloquear, não recomendado |
| `/dev/cu.usbserial-*` | estilo call/terminal (**não bloqueante**) | ✅ recomendado |

**Encontre a sua porta:**

```bash
ls /dev/cu.*
```

Saída típica:

```
/dev/cu.usbserial-0001      # CP2102 / FTDI
/dev/cu.usbmodem141101      # onboard USB serial (Arduino/ESP32)
/dev/cu.wchusbserial1420    # CH340
```

> A ferramenta dá preferência automática aos dispositivos `cu.*`. Se indicar uma porta manualmente, use `cu.` e não `tty.`.

## 5. Controladores USB

A maioria dos chips comuns (CH340, CP2102, FTDI) tem controladores incorporados no macOS. Se o dispositivo não for reconhecido:

```bash
system_profiler SPUSBDataType | grep -A5 -i "serial\|CH340\|CP210"
```

- **CH340**: os lotes mais antigos necessitam do controlador oficial da WCH
- Em geral, basta que `ls /dev/cu.*` mostre o dispositivo

## 6. Verificar o ambiente

```bash
python setup.py
```

## 7. Iniciar a GUI

```bash
python -m src.gui.factory_calibration_tool
```

Especifique a porta:

```bash
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 8. Fluxo de trabalho da interface

> Disposição de painel único. Uma barra de deslocamento aparece automaticamente quando a janela é demasiado baixa; estica para se ajustar quando maximizada.

### 8.1 Ligação série
Selecione a porta e a taxa de transmissão (predefinição 1M) e clique em **Conetar**.

### 8.2 Procurar servos
Clique em **Procurar servos** (ID 1-254); clique numa linha da lista para preencher automaticamente a lista pendente.

### 8.3 Leitura/escrita de parâmetros
- Ler todos os 44 registos; a seleção de um ponto preenche endereço/comprimento/valor
- Escrita com desbloqueio/escrita/bloqueio automáticos; é mostrada uma janela de sucesso/falha

### 8.4 Controlo de posição
Arraste o controlo deslizante (0-1023) ou introduza o valor; é apresentada uma indicação de movimento concluído para desativar o binário.

### 8.5 Taxa de transmissão / Reposição de fábrica
Alterar a taxa de transmissão (reversão automática em caso de falha), reposição de fábrica.

### 8.6 Parâmetros xdat (apenas EEPROM)
Guardar o servo atual → abrir cópia de segurança → restaurar no servo.

## 9. Resolução de problemas

| Problema | Solução |
|---------|----------|
| A porta com `tty.` bloqueia | Use antes o prefixo `cu.` |
| Dispositivo não encontrado | `ls /dev/cu.*`; volte a ligar; `system_profiler SPUSBDataType` |
| Interface em chinês em branco | O PingFang do sistema costuma ser suficiente; instale o Noto Sans CJK se estiver em branco |
| Problema de permissões | O macOS geralmente não exige permissões adicionais; permita o acesso ao terminal se for solicitado |
| A ativação do venv falha | `source .venv/bin/activate` (não `.bat`) |
| Erro de compilação em Apple Silicon | O Python 3.10+ é nativo; evite Python antigo sob Rosetta |

## 10. Linha de comandos (opcional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 11. Dicas

- **O nome da porta muda**: os nomes `cu.*` podem variar consoante a porta USB; selecione na lista pendente em cada arranque
- **Suspensão**: o macOS pode suspender e perder a porta série; mantenha o sistema ativo durante a utilização
- **Permissão de privacidade**: se for pedido para "access removable disks", permita-o
