[English](../en/Linux.md) | [Deutsch](../de/Linux.md) | [Español](../es/Linux.md) | [Français](../fr/Linux.md) | [Italiano](../it/Linux.md) | [日本語](../ja/Linux.md) | [한국어](../ko/Linux.md) | [Português (BR)](../pt-br/Linux.md) | Português (PT) | [简体中文](../zh-hans/Linux.md) | [繁體中文](../zh-hant/Linux.md)

# Ferramenta de Depuração do Servo SCS0009 — Guia Linux

Para Ubuntu / Debian / outras distribuições convencionais. Pontos-chave: permissões da porta série (dialout) e deteção de dispositivos USB-série.

> ⚠️ **Compatibilidade: esta ferramenta suporta atualmente apenas servos Feetech SCS0009 (série SCS, feedback por potenciómetro, resolução de 10 bits 0-1023)**. A tabela de registos e o formato xdat foram concebidos para o Feetech SCS0009; outros fabricantes/modelos não são garantidos.

---

## 1. Requisitos

| Dependência | Versão |
|-----------|---------|
| Python | >= 3.8 (recomenda-se 3.10+) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| SO | Ubuntu 20.04+ / Debian 11+ |

Tipos de letra chineses (necessários para a interface em chinês):

```bash
sudo apt install fonts-noto-cjk
```

Tipos de letra de ícones emoji (para ✅⚠️ etc. nos registos):

```bash
sudo apt install fonts-noto-color-emoji
```

## 2. Instalar as dependências do Python

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **Crie o ambiente virtual apenas UMA VEZ**. Executá-lo novamente irá redefinir/substituir o ambiente (apagando as dependências instaladas). Depois disso, basta executar `source .venv/bin/activate`.

> Se o pip reportar "externally-managed-environment", utilize um venv ou `pip install --break-system-packages -r requirements.txt`.

## 3. ⚠️ Permissão da porta série (dialout) [Obrigatório]

Por predefinição, os utilizadores normais **não conseguem aceder** a `/dev/ttyUSB*` / `/dev/ttyACM*`. Adicione o seu utilizador ao grupo `dialout`:

```bash
sudo usermod -a -G dialout $USER
```

**Termine a sessão e volte a iniciá-la** (ou reinicie). Verifique:

```bash
groups
# output should include dialout
```

> Algumas distribuições usam `uucp` (Arch) ou `tty`.

## 4. Identificar o dispositivo série USB

Depois de ligar:

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Saída típica:

```
/dev/ttyUSB0   # CH340 / CP2102 / PL2303
/dev/ttyACM0   # native USB serial (Arduino/ESP32 onboard)
```

## 5. Verificar o ambiente

```bash
python setup.py
```

## 6. Iniciar a GUI

```bash
python -m src.gui.factory_calibration_tool
```

Especifique a porta:

```bash
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

> Se existir apenas uma porta, a ferramenta utiliza-a diretamente.

## 7. Fluxo de trabalho da interface

> Disposição de painel único. Uma barra de deslocamento aparece automaticamente quando a janela é demasiado baixa; estica para se ajustar quando maximizada.

### 7.1 Ligação série
Selecione a porta e a taxa de transmissão (predefinição 1M) e clique em **Conetar**.

### 7.2 Procurar servos
Clique em **Procurar servos** (ID 1-254); clique numa linha da lista para preencher automaticamente a lista pendente.

### 7.3 Leitura/escrita de parâmetros
- Ler todos os 44 registos (EEPROM + SRAM); a seleção de um ponto preenche endereço/comprimento/valor
- Escrita com desbloqueio/escrita/bloqueio automáticos; é mostrada uma janela de sucesso/falha

### 7.4 Controlo de posição
Arraste o controlo deslizante (0-1023) ou introduza o valor; é apresentada uma indicação de movimento concluído para desativar o binário.

### 7.5 Taxa de transmissão / Reposição de fábrica
Alterar a taxa de transmissão (reversão automática em caso de falha), reposição de fábrica.

### 7.6 Parâmetros xdat (apenas EEPROM)
Guardar o servo atual → abrir cópia de segurança → restaurar no servo.

## 8. Resolução de problemas

| Problema | Solução |
|---------|----------|
| **Permission denied: /dev/ttyUSB0** | Não pertence ao grupo dialout, ver a secção 3; ou `sudo chmod 666 /dev/ttyUSB0` (temporário) |
| Sem porta série | `ls /dev/ttyUSB* /dev/ttyACM*`; `lsusb` para confirmar o dispositivo |
| O nome do dispositivo muda | a numeração ttyUSB depende da ordem de ligação; use uma regra udev ou selecione em cada arranque |
| Interface em chinês em branco | Instale `fonts-noto-cjk` |
| Os emojis aparecem como quadrados | Instale `fonts-noto-color-emoji` |
| A instalação com pip falha | Use um venv; ou `--break-system-packages` |
| A aplicação não arranca | Verifique `python3 --version`; `pip list` para as dependências |

## 9. Linha de comandos (opcional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

## 10. Avançado: nome de dispositivo fixo com udev (opcional)

Crie `/etc/udev/rules.d/99-servo.rules` para fixar o nome do dispositivo pelo ID USB:

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyServo"
```

Depois, `ls -l /dev/ttyServo`. Obtenha o ID do fabricante com `lsusb`.
