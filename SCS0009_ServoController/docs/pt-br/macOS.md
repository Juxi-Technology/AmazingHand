[English](../en/macOS.md) | [Deutsch](../de/macOS.md) | [Español](../es/macOS.md) | [Français](../fr/macOS.md) | [Italiano](../it/macOS.md) | [日本語](../ja/macOS.md) | [한국어](../ko/macOS.md) | Português (BR) | [Português (PT)](../pt-pt/macOS.md) | [简体中文](../zh-hans/macOS.md) | [繁體中文](../zh-hant/macOS.md)

# Ferramenta de depuração do servo SCS0009 — Guia para macOS

Para macOS 11 (Big Sur) e posteriores. Pontos principais: nomenclatura serial (`cu.*` vs `tty.*`), drivers USB.

> ⚠️ **Compatibilidade: atualmente esta ferramenta suporta apenas servos Feetech SCS0009 (série SCS, feedback de posição por potenciômetro, resolução de 10 bits 0-1023)**. A tabela de registradores e o formato xdat são projetados para o Feetech SCS0009; outras marcas/modelos não são garantidos.

---

## 1. Requisitos

| Dependência | Versão |
|-----------|---------|
| Python | >= 3.8 (recomenda-se 3.10+, via Homebrew) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| SO | macOS 11+ (Apple Silicon / Intel) |

## 2. Instalar o Python

Recomendado via Homebrew:

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

> ⚠️ **Crie o ambiente virtual apenas UMA VEZ**. Executá-lo novamente vai redefinir/sobrescrever o ambiente (apagando as dependências instaladas). Depois disso, basta `source .venv/bin/activate`.

## 4. ⚠️ Nomenclatura serial do macOS [Chave]

O macOS coloca os dispositivos seriais USB em `/dev` com **duas convenções de nomes**:

| Prefixo | Significado | Utilizável |
|--------|---------|--------|
| `/dev/tty.usbserial-*` | estilo modem (bloqueante) | pode travar, não recomendado |
| `/dev/cu.usbserial-*` | estilo call/terminal (**não bloqueante**) | ✅ recomendado |

**Encontre sua porta:**

```bash
ls /dev/cu.*
```

Saída típica:

```
/dev/cu.usbserial-0001      # CP2102 / FTDI
/dev/cu.usbmodem141101      # onboard USB serial (Arduino/ESP32)
/dev/cu.wchusbserial1420    # CH340
```

> A ferramenta prefere automaticamente os dispositivos `cu.*`. Se especificar a porta manualmente, use `cu.`, não `tty.`.

## 5. Drivers USB

Os chips mais comuns (CH340, CP2102, FTDI) já têm drivers integrados no macOS. Se o dispositivo não for reconhecido:

```bash
system_profiler SPUSBDataType | grep -A5 -i "serial\|CH340\|CP210"
```

- **CH340**: lotes mais antigos precisam do driver oficial da WCH
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

> Layout de painel único. Uma barra de rolagem aparece automaticamente quando a janela fica muito baixa; ela se estende para se ajustar ao maximizar.

### 8.1 Conexão serial
Selecione a porta e a taxa de transmissão (padrão 1M) e clique em **Conectar**.

### 8.2 Escanear servos
Clique em **Escanear servos** (ID 1-254); clique em uma linha da lista para preencher automaticamente o menu suspenso.

### 8.3 Leitura/escrita de parâmetros
- Lê todos os 44 registradores; a seleção de linha preenche endereço/tamanho/valor
- Escreve com desbloqueio/escrita/bloqueio automáticos; aviso de sucesso/falha exibido

### 8.4 Controle de posição
Arraste o controle deslizante (0-1023) ou digite o valor; aviso de movimento concluído para desligar o torque.

### 8.5 Taxa de transmissão / Restauração de fábrica
Altere a taxa de transmissão (reversão automática em caso de falha), restauração de fábrica.

### 8.6 Parâmetros xdat (somente EEPROM)
Salvar servo atual → abrir backup → restaurar no servo.

## 9. Solução de problemas

| Problema | Solução |
|---------|----------|
| Porta com `tty.` trava | Use o prefixo `cu.` em vez disso |
| Dispositivo não encontrado | `ls /dev/cu.*`; reconecte; `system_profiler SPUSBDataType` |
| Interface em chinês em branco | Normalmente a PingFang do sistema basta; instale Noto Sans CJK se estiver corrompido |
| Problema de permissão | O macOS em geral não exige permissão extra; autorize o acesso do terminal se for solicitado |
| Falha ao ativar o venv | `source .venv/bin/activate` (não `.bat`) |
| Erro de compilação no Apple Silicon | O Python 3.10+ é nativo; evite um Python antigo rodando sob Rosetta |

## 10. Linha de comando (opcional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 11. Dicas

- **O nome da porta muda**: os nomes `cu.*` podem variar conforme a porta USB; selecione no menu suspenso a cada inicialização
- **Repouso**: o macOS pode entrar em repouso e derrubar a conexão serial; mantenha-o acordado durante a operação
- **Permissão de privacidade**: se for solicitado a "acessar discos removíveis", permita
