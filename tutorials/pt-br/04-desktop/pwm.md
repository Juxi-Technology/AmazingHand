---
title: "Aplicativo de desktop PWM (GUI Tkinter)"
description: "Controle de desktop da versão com servos PWM do AmazingHand: execução a partir do código-fonte, gestos/diferencial/acionamento direto na GUI, rastreamento MediaPipe embutido, teste por linha de comando e empacotamento."
version: pwm
---

# Aplicativo de desktop PWM (GUI Tkinter)

> Os comandos abaixo são executados no diretório `AmazingHand-PWM/` do repositório.

Esta página é o tutorial de controle de desktop da **versão com servos PWM**. Para o controle web, veja [Controle web PWM](../03-web-control/pwm.md); para a fiação, [Fiação PWM](../01-hardware/pwm.md); para a gravação do firmware, [Início rápido com PWM](../02-quick-start/pwm.md).

> Aplicável a: ESP32-S3 + 8 servos PWM (acionamento diferencial). Gravação do firmware em [Início rápido com PWM](../02-quick-start/pwm.md); protocolo e comandos em [Protocolo e calibração PWM](../06-servo-tuning/pwm.md).

## 1. Formas de execução

| Método | Requisitos | Indicado para |
|------|------|------|
| **Executar a partir do código-fonte** (recomendado) | Python 3.12 de 64 bits + pyserial | Todos os recursos, incluindo rastreamento de mãos |
| Empacotar exe por conta própria | PyInstaller | Distribuir sem instalar Python (veja a seção 7) |

## 2. Execução a partir do código-fonte

### Instalar dependências

No diretório raiz do módulo (`AmazingHand-PWM/`), execute:

```bash
# dependências básicas (pyserial)
pip install -r tools/requirements.txt

# execute só se precisar de rastreamento de mãos (cria tools/tracking_env e instala o mediapipe automaticamente)
tools/setup_tracking.bat
```

> O mediapipe 0.10.14 só fornece wheel para Windows de 64 bits; é obrigatório usar **Python 3.12 de 64 bits**.

### Iniciar a GUI

```bash
# qualquer Python com pyserial
python tools/hand_gui.py

# ou use o ambiente de rastreamento (com mediapipe)
tools/tracking_env/Scripts/python tools/hand_gui.py
```

![Janela principal do aplicativo: barra serial, comandos de gesto, acionamento direto dos servos e controle diferencial dos dedos](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-main.png)

### Uso da GUI

1. **Selecione a porta serial**: no menu suspenso do topo, escolha a porta COM do ESP32 (veja no Gerenciador de Dispositivos).
2. **Clique em «Conectar»**: o LED de status fica verde, o log mostra "conectado" e o teste de link NOP é enviado automaticamente.
3. **Comandos de gesto**: clique em «Pedra / Tesoura / Papel / Joinha / OK / Pinça / Apontar / Abrir / Punho fechado» e a mão executa.
4. **Mão esquerda/direita**: marque «Mão direita» / «Mão esquerda» para alternar (a direção espelhada do polegar é diferente).
5. **Acionamento direto dos servos**: arraste os 8 controles deslizantes para controlar o ângulo de cada servo em tempo real (0–180°).
6. **Controle diferencial dos dedos**: duas barras de progresso por dedo —
   - **Flexionar◀▶Estender**: flexiona ou estende o dedo (faixa -70 ~ +70).
   - **Balançar à direita◀▶à esquerda**: move o dedo para os lados (faixa 60 ~ 120, 90 = neutro).

   > Essas duas barras de progresso são **eixos de controle**, não dois servos. O programa as combina nos ângulos dos dois servos do dedo: a componente de mesmo sentido gera abdução e a de sentidos opostos gera flexão/extensão.

7. **Repetir / Parar**: repete o último gesto / interrompe imediatamente.
8. **Log de comunicação**: mostra em tempo real, na parte inferior, os quadros enviados/recebidos e as respostas.

![Painel de controle diferencial dos dedos: flexão/extensão e balanço lateral de cada dedo](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-differential.png)

### Rastreamento de mãos embutido na GUI

A GUI inclui um painel de rastreamento de mãos (a câmera acompanha os movimentos da mão):

1. Depois de conectar a serial, role até o painel «Rastreamento de mãos (câmera MediaPipe)».
2. Escolha o número da câmera (padrão 0) e clique em **«Iniciar rastreamento»**.
3. Coloque a mão no campo de visão da câmera e a mão dexterosa acompanha a flexão/extensão.

> O rastreamento exige o mediapipe instalado por `tools/setup_tracking.bat`; só a GUI iniciada a partir do código-fonte tem o recurso de rastreamento.

## 3. Teste por linha de comando (tools/serial_test.py)

No diretório raiz do módulo, execute:

```bash
# teste de link (confirme primeiro que há comunicação)
python tools/serial_test.py COM3 nop

# gestos
python tools/serial_test.py COM3 rock         # pedra
python tools/serial_test.py COM3 thumbs_up    # joinha
python tools/serial_test.py COM3 index        # apontar
python tools/serial_test.py COM3 open         # abrir
python tools/serial_test.py COM3 close        # punho fechado

# acionamento direto de um servo
python tools/serial_test.py COM3 servo 1 90   # servo 1 → 90°

# centralizar tudo
python tools/serial_test.py COM3 mid

# definir mão esquerda/direita
python tools/serial_test.py COM3 hand L
python tools/serial_test.py COM3 hand R

# varredura/autoteste
python tools/serial_test.py COM3 sweep 1      # varredura do servo 1
python tools/serial_test.py COM3 test         # testa todos os servos, um a um
```

## 4. Teste manual com ferramenta serial (opcional)

Sem o aplicativo, também é possível verificar o link enviando quadros hexadecimais diretamente por uma ferramenta serial.

**CoolTerm** (Windows / macOS / Linux):

1. `Options` → baudrate **115200**, 8N1.
2. `Connection` → `Send String` → selecione `Hex`.
3. Envie `AA 01 00 01` (pedra); na área de resposta devem aparecer `BB 01 00 01` (ACK) e `BB 01 10 11` (concluído).

**Linha de comando no Linux / macOS**:

```bash
# Linux
stty -F /dev/ttyUSB0 115200
printf '\xAA\x01\x00\x01' > /dev/ttyUSB0

# macOS
stty -f /dev/cu.usbserial-0001 115200
printf '\xAA\x01\x00\x01' > /dev/cu.usbserial-0001
```

Formato dos quadros, checksum e todos os comandos em [Protocolo e calibração PWM](../06-servo-tuning/pwm.md).

## 5. Script de controle em Python (desenvolvimento personalizado)

```python
import time
import serial

PORT, BAUD = "COM3", 115200          # no Linux/macOS, troque por /dev/ttyUSB0, /dev/cu.usbserial-*

def frame(cmd, data=b""):
    checksum = cmd ^ len(data)
    for byte in data:
        checksum ^= byte
    return bytes([0xAA, cmd, len(data)]) + data + bytes([checksum & 0xFF])

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(1)                        # espera a reinicialização do ESP32 terminar

ser.write(frame(0x00))               # teste de link NOP
ser.write(frame(0x01))               # pedra
time.sleep(0.5)
ser.write(frame(0xF0, bytes([90] * 8)))  # todos os 8 servos a 90°
ser.close()
```

O quadro de resposta é `BB CMD STATUS CKSUM`; `STATUS=0x00` significa aceito e `0x10` significa gesto concluído. A tabela completa de comandos e exemplos de acionamento direto/mão esquerda-direita estão em [Protocolo e calibração PWM](../06-servo-tuning/pwm.md).

## 6. Perguntas frequentes

| Sintoma | Ação |
|------|------|
| Servos não se movem | Verifique a alimentação (fonte independente de 5 V 3 A), a porta COM e a fiação |
| Sem resposta / servos se movem sem controle ao abrir a serial | Confirme o baudrate 115200; a GUI envia um handshake NOP ao conectar |
| Sem imagem da câmera | Permita o acesso à câmera (Configurações → Privacidade → Câmera) |
| Mão invertida | Marque a mão oposta (esquerda/direita) |
| Rastreamento sem reação | Confirme que iniciou com o Python de `tools\tracking_env` e que o mediapipe foi instalado com sucesso |

## 7. Empacotar exe por conta própria (opcional)

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole --name "AmazingHand控制台" tools/hand_gui.py
```

A versão empacotada não inclui o rastreamento de mãos (os recursos do mediapipe são grandes); para rastreamento, use a execução a partir do código-fonte.

> Para a descrição completa do protocolo e dos comandos, veja [Protocolo e calibração PWM](../06-servo-tuning/pwm.md).
