---
title: "Aplicação de desktop PWM (GUI Tkinter)"
description: "Controlo de desktop da versão de servos PWM do AmazingHand: execução a partir do código-fonte, gestos/diferencial/acionamento direto na GUI, seguimento MediaPipe integrado, testes por linha de comandos e empacotamento."
version: pwm
---

# Aplicação de desktop PWM (GUI Tkinter)

> Os comandos seguintes são executados no diretório `AmazingHand-PWM/` do repositório.

Esta página é o tutorial de controlo de desktop da **versão de servos PWM**. Para controlo web, consulte [Controlo web PWM](../03-web-control/pwm.md); para cablagem, [Cablagem PWM](../01-hardware/pwm.md); para gravação de firmware, [Início rápido PWM](../02-quick-start/pwm.md).

> Aplicável a: ESP32-S3 + 8 servos PWM (acionamento diferencial). Para gravação de firmware, consulte [Início rápido PWM](../02-quick-start/pwm.md); para o protocolo e comandos, [Protocolo e calibração PWM](../06-servo-tuning/pwm.md).

## 1. Modos de execução

| Modo | Requisitos | Adequado a |
|------|------|------|
| **Execução a partir do código-fonte** (recomendado) | Python 3.12 de 64 bits + pyserial | Todas as funcionalidades, incluindo seguimento de mãos |
| Empacotamento próprio em exe | PyInstaller | Distribuição sem instalar Python (ver secção 7) |

## 2. Execução a partir do código-fonte

### Instalar dependências

No diretório raiz do módulo (`AmazingHand-PWM/`):

```bash
# Dependências base (pyserial)
pip install -r tools/requirements.txt

# Executar apenas se precisar de seguimento de mãos (cria automaticamente tools/tracking_env e instala o mediapipe)
tools/setup_tracking.bat
```

> O mediapipe 0.10.14 só disponibiliza wheels de 64 bits para Windows, pelo que é obrigatório usar **Python 3.12 de 64 bits**.

### Iniciar a GUI

```bash
# Qualquer Python com pyserial
python tools/hand_gui.py

# Ou usar o ambiente de seguimento (com mediapipe)
tools/tracking_env/Scripts/python tools/hand_gui.py
```

![Interface principal da aplicação: barra de porta série, comandos de gestos, acionamento direto dos servos e controlo diferencial dos dedos](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-main.png)

### Utilização da GUI

1. **Escolher a porta série**: no topo, escolha a porta COM do ESP32 na lista pendente (ver no Gestor de Dispositivos).
2. **Clique em «Ligar»**: a luz de estado fica verde, o registo mostra "ligado" e é enviado automaticamente um teste de ligação NOP.
3. **Comandos de gestos**: clique em «Pedra / Tesoura / Papel / Fixe / OK / Pinça / Apontar / Abrir / Punho» e a mão executa.
4. **Mão esquerda/direita**: marque «Mão direita»/«Mão esquerda» para alternar (o sentido do espelhamento do polegar é diferente).
5. **Acionamento direto dos servos**: arraste os 8 sliders para controlar em tempo real o ângulo de cada servo (0–180°).
6. **Controlo diferencial dos dedos**: duas barras de progresso por dedo —
   - **Flexão◀▶Extensão**: flete ou estende o dedo (intervalo -70 ~ +70).
   - **Balanço direita◀▶esquerda**: balança o dedo lateralmente (intervalo 60 ~ 120, 90=neutro).

   > Estas duas barras de progresso são **eixos de controlo**, não dois servos. O programa combina-as nos ângulos dos dois servos desse dedo: a componente no mesmo sentido produz abertura; a componente em sentidos opostos produz flexão.

7. **Repetir / Parar**: repete o último gesto / interrompe imediatamente.
8. **Registo de comunicação**: mostra em baixo, em tempo real, os frames enviados/recebidos e as respostas.

![Painel de controlo diferencial dos dedos: flexão/extensão e balanço lateral de cada dedo](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-differential.png)

### Seguimento de mãos integrado na GUI

A GUI inclui um painel de seguimento de mãos (a câmara acompanha os movimentos da mão):

1. Após ligar a porta série, desça até ao painel «Seguimento de mãos (câmara MediaPipe)».
2. Escolha o número da câmara (predefinição 0) e clique em **«Iniciar seguimento»**.
3. Coloque a mão na imagem da câmara; a mão robótica acompanha a flexão/extensão.

> O seguimento requer que o `tools/setup_tracking.bat` tenha instalado o mediapipe; só a GUI iniciada a partir do código-fonte tem a funcionalidade de seguimento.

## 3. Teste por linha de comandos (tools/serial_test.py)

No diretório raiz do módulo:

```bash
# Teste de ligação (confirme primeiro que comunica)
python tools/serial_test.py COM3 nop

# Gestos
python tools/serial_test.py COM3 rock         # Pedra
python tools/serial_test.py COM3 thumbs_up    # Fixe
python tools/serial_test.py COM3 index        # Apontar
python tools/serial_test.py COM3 open         # Abrir
python tools/serial_test.py COM3 close        # Punho

# Acionamento direto de um servo
python tools/serial_test.py COM3 servo 1 90   # Servo 1 → 90°

# Todos ao centro
python tools/serial_test.py COM3 mid

# Definir mão esquerda/direita
python tools/serial_test.py COM3 hand L
python tools/serial_test.py COM3 hand R

# Varredura/autoteste
python tools/serial_test.py COM3 sweep 1      # Varredura do servo 1
python tools/serial_test.py COM3 test         # Teste individual de todos os servos
```

## 4. Teste manual com ferramenta de porta série (opcional)

Sem a aplicação de PC, também é possível validar a ligação enviando frames hexadecimais diretamente com uma ferramenta de porta série.

**CoolTerm** (Windows / macOS / Linux):

1. `Options` → baudrate **115200**, 8N1.
2. `Connection` → `Send String` → escolha `Hex`.
3. Envie `AA 01 00 01` (Pedra); na área de resposta deve aparecer `BB 01 00 01` (ACK) e `BB 01 10 11` (concluído).

**Linha de comandos Linux / macOS:**

```bash
# Linux
stty -F /dev/ttyUSB0 115200
printf '\xAA\x01\x00\x01' > /dev/ttyUSB0

# macOS
stty -f /dev/cu.usbserial-0001 115200
printf '\xAA\x01\x00\x01' > /dev/cu.usbserial-0001
```

O formato dos frames, a soma de verificação e todos os comandos estão em [Protocolo e calibração PWM](../06-servo-tuning/pwm.md).

## 5. Script de controlo em Python (desenvolvimento personalizado)

```python
import time
import serial

PORT, BAUD = "COM3", 115200          # Linux/macOS: substituir por /dev/ttyUSB0, /dev/cu.usbserial-*

def frame(cmd, data=b""):
    checksum = cmd ^ len(data)
    for byte in data:
        checksum ^= byte
    return bytes([0xAA, cmd, len(data)]) + data + bytes([checksum & 0xFF])

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(1)                        # aguarda a conclusão do reinício do ESP32

ser.write(frame(0x00))               # teste de ligação NOP
ser.write(frame(0x01))               # Pedra
time.sleep(0.5)
ser.write(frame(0xF0, bytes([90] * 8)))  # todos os 8 canais de servo a 90°
ser.close()
```

O frame de resposta é `BB CMD STATUS CKSUM`; `STATUS=0x00` indica aceite e `0x10` indica gesto concluído. Consulte [Protocolo e calibração PWM](../06-servo-tuning/pwm.md) para a tabela completa de comandos e exemplos de acionamento direto/mão esquerda-direita.

## 6. Perguntas frequentes

| Sintoma | Resolução |
|------|------|
| Servos não se movem | Verifique a alimentação (fonte autónoma de 5V 3A), a porta COM e a cablagem |
| Sem resposta / servos descontrolados ao abrir a porta série | Confirme o baudrate 115200; ao ligar, a GUI envia primeiro o handshake NOP |
| Sem imagem da câmara | Permita o acesso à câmara (Definições→Privacidade→Câmara) |
| Formato da mão invertido | Marque a mão esquerda/direita inversa |
| Seguimento sem reação | Confirme que inicia com o Python de `tools\tracking_env` e que o mediapipe foi instalado com sucesso |

## 7. Empacotamento próprio em exe (opcional)

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole --name "AmazingHand控制台" tools/hand_gui.py
```

A versão empacotada não inclui o seguimento de mãos (os recursos do mediapipe são grandes); se precisar de seguimento, utilize a execução a partir do código-fonte.

> Para a descrição completa do protocolo e comandos, consulte [Protocolo e calibração PWM](../06-servo-tuning/pwm.md).
