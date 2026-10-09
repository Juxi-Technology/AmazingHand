[English](../en/Linux.md) | [Deutsch](../de/Linux.md) | [Español](../es/Linux.md) | [Français](../fr/Linux.md) | [Italiano](../it/Linux.md) | [日本語](../ja/Linux.md) | [한국어](../ko/Linux.md) | Português (BR) | [Português (PT)](../pt-pt/Linux.md) | [简体中文](../zh-hans/Linux.md) | [繁體中文](../zh-hant/Linux.md)

# Ferramenta de depuração do servo SCS0009 — Guia para Linux

Para Ubuntu / Debian / outras distribuições populares. Pontos principais: permissões de porta serial (dialout), detecção de dispositivos USB-serial.

> ⚠️ **Compatibilidade: atualmente esta ferramenta suporta apenas servos Feetech SCS0009 (série SCS, feedback de posição por potenciômetro, resolução de 10 bits 0-1023)**. A tabela de registradores e o formato xdat são projetados para o Feetech SCS0009; outras marcas/modelos não são garantidos.

---

## 1. Requisitos

| Dependência | Versão |
|-----------|---------|
| Python | >= 3.8 (recomenda-se 3.10+) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| SO | Ubuntu 20.04+ / Debian 11+ |

Fontes chinesas (necessárias para a interface em chinês):

```bash
sudo apt install fonts-noto-cjk
```

Fontes de ícones emoji (para ✅⚠️ etc. nos registros):

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

> ⚠️ **Crie o ambiente virtual apenas UMA VEZ**. Executá-lo novamente vai redefinir/sobrescrever o ambiente (apagando as dependências instaladas). Depois disso, basta `source .venv/bin/activate`.

> Se o pip informar "externally-managed-environment", use um venv ou `pip install --break-system-packages -r requirements.txt`.

## 3. ⚠️ Permissão da porta serial (dialout) [Obrigatório]

Por padrão, usuários comuns **não conseguem acessar** `/dev/ttyUSB*` / `/dev/ttyACM*`. Adicione seu usuário ao grupo `dialout`:

```bash
sudo usermod -a -G dialout $USER
```

**Saia da sessão e entre novamente** (ou reinicie). Verifique:

```bash
groups
# output should include dialout
```

> Algumas distribuições usam `uucp` (Arch) ou `tty`.

## 4. Identificar o dispositivo serial USB

Após conectar:

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

> Se existir apenas uma porta, a ferramenta a utiliza diretamente.

## 7. Fluxo de trabalho da interface

> Layout de painel único. Uma barra de rolagem aparece automaticamente quando a janela fica muito baixa; ela se estende para se ajustar ao maximizar.

### 7.1 Conexão serial
Selecione a porta e a taxa de transmissão (padrão 1M) e clique em **Conectar**.

### 7.2 Escanear servos
Clique em **Escanear servos** (ID 1-254); clique em uma linha da lista para preencher automaticamente o menu suspenso.

### 7.3 Leitura/escrita de parâmetros
- Lê todos os 44 registradores (EEPROM + SRAM); a seleção de linha preenche endereço/tamanho/valor
- Escreve com desbloqueio/escrita/bloqueio automáticos; aviso de sucesso/falha exibido

### 7.4 Controle de posição
Arraste o controle deslizante (0-1023) ou digite o valor; aviso de movimento concluído para desligar o torque.

### 7.5 Taxa de transmissão / Restauração de fábrica
Altere a taxa de transmissão (reversão automática em caso de falha), restauração de fábrica.

### 7.6 Parâmetros xdat (somente EEPROM)
Salvar servo atual → abrir backup → restaurar no servo.

## 8. Solução de problemas

| Problema | Solução |
|---------|----------|
| **Permission denied: /dev/ttyUSB0** | Você não está no grupo dialout, veja a seção 3; ou `sudo chmod 666 /dev/ttyUSB0` (temporário) |
| Nenhuma porta serial | `ls /dev/ttyUSB* /dev/ttyACM*`; `lsusb` para confirmar o dispositivo |
| O nome do dispositivo muda | A numeração ttyUSB depende da ordem de conexão; use uma regra udev ou selecione a cada inicialização |
| Interface em chinês em branco | Instale `fonts-noto-cjk` |
| Emojis aparecem como quadros | Instale `fonts-noto-color-emoji` |
| Falha no `pip install` | Use um venv; ou `--break-system-packages` |
| O aplicativo não inicia | Verifique `python3 --version`; `pip list` para as dependências |

## 9. Linha de comando (opcional)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

## 10. Avançado: nome de dispositivo fixo com udev (opcional)

Crie `/etc/udev/rules.d/99-servo.rules` para fixar o nome do dispositivo pelo ID de USB:

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyServo"
```

Em seguida, `ls -l /dev/ttyServo`. Obtenha o ID do fabricante com `lsusb`.
