[English](../en/scs_servo_protocol.md) | [Deutsch](../de/scs_servo_protocol.md) | [Español](../es/scs_servo_protocol.md) | [Français](../fr/scs_servo_protocol.md) | [Italiano](../it/scs_servo_protocol.md) | [日本語](../ja/scs_servo_protocol.md) | [한국어](../ko/scs_servo_protocol.md) | Português (BR) | [Português (PT)](../pt-pt/scs_servo_protocol.md) | [简体中文](../zh-hans/scs_servo_protocol.md) | [繁體中文](../zh-hant/scs_servo_protocol.md)

# Servo SCSCL com potenciômetro – Descrição da tabela de memória

## Sumário

- [Servo SCSCL com potenciômetro – Descrição da tabela de memória](#servo-scscl-com-potenciômetro--descrição-da-tabela-de-memória)
- [1. Protocolo de comunicação do servo](#1-protocolo-de-comunicação-do-servo)
- [2. Definição da tabela de memória do servo](#2-definição-da-tabela-de-memória-do-servo)
  - [2.1 Informações de versão](#21-informações-de-versão)
  - [2.2 Configuração EPROM](#22-configuração-eprom)
  - [2.3 Controle SRAM](#23-controle-sram)
  - [2.4 Feedback SRAM](#24-feedback-sram)
  - [2.5 Parâmetros de fábrica](#25-parâmetros-de-fábrica)
- [3. Descrição dos bytes especiais](#3-descrição-dos-bytes-especiais)
  - [3.1 Fase do servo](#31-fase-do-servo)
  - [3.2 Status do servo](#32-status-do-servo)
  - [3.3 Condições de descarga](#33-condições-de-descarga)
  - [3.4 Condições de alarme do LED](#34-condições-de-alarme-do-led)

---

## 1. Protocolo de comunicação do servo

O servo usa o **protocolo personalizado FT-SCS**.  

- Taxa de transmissão padrão: **1 Mbps ou 500 kbps**
- Camada física: **barramento único TTL**
- Bits de dados: **8**
- Paridade: **nenhuma**
- Bits de parada: **1**
- Faixa de baud configurável: **38 400 ~ 1 Mbps (500 k)**
- Endereço de comunicação padrão (ID): **1**

Referência do protocolo:  
[FT-SCS Custom Protocol](http://doc.feetech.cn/#/tiaozhunlujingft?srcType=FT-SCS-Protocol-41ad23fe8a244712ba160b93)

---

## 2. Definição da tabela de memória do servo

> Se um endereço de função usa um valor de 2 bytes, o **byte alto** é armazenado no **endereço inferior** e o **byte baixo** no **endereço superior** (big-endian dentro da tabela).

---

### 2.1 Informações de versão

| Address DEC | Address HEX | Nome da função          | Bytes | Default | Access | Range | Unit | Descrição                              |
|-------------|-------------|-------------------------|-------|---------|--------|-------|------|----------------------------------------|
| 0           | 0x00        | Versão principal do firmware | 1     | –       | R      |       |      |                                        |
| 1           | 0x01        | Versão secundária do firmware | 1     | –       | R      |       |      |                                        |
| 2           | 0x02        | END                     | 1     | 1       | R      |       |      | `1` indica armazenamento big-endian    |
| 3           | 0x03        | Versão principal do servo | 1     | –       | R      |       |      |                                        |
| 4           | 0x04        | Versão secundária do servo | 1     | –       | R      |       |      |                                        |

---

### 2.2 Configuração EPROM

| Address DEC | Address HEX | Nome da função                | Bytes | Default | Access | Range       | Unit  | Descrição                                                                                                                                           |
|-------------|-------------|-------------------------------|-------|---------|--------|-------------|-------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 5           | 0x05        | ID do servo                   | 1     | 1       | R/W   | 0 ~ 253     | ID    | ID principal única no barramento                                                                                                                    |
| 6           | 0x06        | Taxa de transmissão           | 1     | 0       | R/W   | 0 ~ 7       | –     | 0–7 representam a taxa de transmissão: 1000000(0), 500000(1), 250000(2), 128000(3), 115200(4), 76800(5), 57600(6), 38400(7)                        |
| 7           | 0x07        | Não definido                  | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 8           | 0x08        | Nível de retorno de status    | 1     | 1       | R/W   | 0 ~ 1       | –     | 0: apenas READ e PING retornam status; 1: todos os comandos retornam pacotes de status                                                              |
| 9           | 0x09        | Limite de ângulo mínimo       | 2     | 20      | R/W   | 0 ~ 1023    | steps | Ângulo de operação mínimo; deve ser menor que o ângulo máximo. Se **min angle = max angle = 0** → modo motor (rotação contínua)                    |
| 11          | 0x0B        | Limite de ângulo máximo       | 2     | 1003    | R/W   | 1 ~ 1023    | steps | Ângulo de operação máximo; deve ser maior que o ângulo mínimo. Se **min angle = max angle = 0** → modo motor                                       |
| 13          | 0x0D        | Limite máximo de temperatura  | 1     | 70      | R/W   | 0 ~ 100     | °C    |                                                                                                                                                     |
| 14          | 0x0E        | Tensão de entrada máxima      | 1     | –       | R/W   | 0 ~ 254     | 0.1 V | Se **max input voltage = min input voltage = 0**, o feedback de tensão fica desabilitado                                                            |
| 15          | 0x0F        | Tensão de entrada mínima      | 1     | 40      | R/W   | 0 ~ 254     | 0.1 V | Se **max input voltage = min input voltage = 0**, o feedback de tensão fica desabilitado                                                            |
| 16          | 0x10        | Torque máximo                 | 2     | 1000    | R/W   | 0 ~ 1000    | 0.1%  | Na energização, este valor é copiado para o endereço 48 (limite de torque)                                                                          |
| 18          | 0x12        | Fase                          | 1     | –       | R/W   | 0 ~ 254     | –     | Byte de função especial; não modificar sem necessidade específica                                                                                   |
| 19          | 0x13        | Condições de descarga         | 1     | –       | R/W   | 0 ~ 254     | –     | Cada bit habilita/desabilita uma proteção correspondente (veja [3.3](#33-condições-de-descarga))                                                    |
| 20          | 0x14        | Condições de alarme do LED    | 1     | –       | R/W   | 0 ~ 254     | –     | Cada bit habilita/desabilita o piscar do LED para um dado alarme (veja [3.4](#34-condições-de-alarme-do-led))                                       |
| 21          | 0x15        | Ganho P da malha de posição   | 1     | –       | R/W   | 0 ~ 254     | –     | Ganho proporcional para o controle de posição                                                                                                       |
| 22          | 0x16        | Ganho D da malha de posição   | 1     | –       | R/W   | 0 ~ 254     | –     | Ganho derivativo para o controle de posição                                                                                                         |
| 23          | 0x17        | Não definido                  | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 24          | 0x18        | Torque mínimo de partida      | 1     | –       | R/W   | 0 ~ 254     | 0.1%  | Saída de torque mínima necessária para iniciar o movimento                                                                                          |
| 25          | 0x19        | Não definido                  | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 26          | 0x1A        | Zona morta direta             | 1     | 1       | R/W   | 0 ~ 16      | steps | A menor unidade é um ângulo de resolução mínimo                                                                                                     |
| 27          | 0x1B        | Zona morta reversa            | 1     | 1       | R/W   | 0 ~ 16      | steps | A menor unidade é um ângulo de resolução mínimo                                                                                                     |
| 28 ~ 36     | 0x1C ~ 0x24 | Não definido                  | 1     | –       | R/W   | –           | –     | –                                                                                                                                                   |
| 37          | 0x25        | Torque de retenção            | 1     | 20      | R/W   | 0 ~ 254     | 1%    | Saída de torque após a proteção contra sobrecarga ser acionada; por exemplo, 20 = 20% do torque máximo                                             |
| 38          | 0x26        | Tempo de proteção             | 1     | 200     | R/W   | 0 ~ 254     | 10 ms | Tempo em que a carga excede o torque de sobrecarga antes de a proteção ser acionada; 200 = 2 s, máximo ≈ 2,5 s                                      |
| 39          | 0x24        | Torque de sobrecarga          | 1     | 80      | R/W   | 0 ~ 254     | 1%    | Torque limiar para iniciar o temporizador da proteção contra sobrecarga; 80 = 80% do torque máximo                                                  |

---

### 2.3 Controle SRAM

| Address DEC | Address HEX | Nome da função  | Bytes | Default | Access | Range                | Unit   | Descrição                                                                                                                                                              |
|-------------|-------------|-----------------|-------|---------|--------|----------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 40          | 0x28        | Chave de torque | 1     | 0       | R/W   | 0 ~ 2                | –      | 0: torque desligado / livre; 1: torque ligado; 2: modo de amortecimento                                                                                               |
| 41          | 0x29        | Não definido    | 1     | –       | R/W   | –                    | –      | –                                                                                                                                                                      |
| 42          | 0x2A        | Posição alvo    | 2     | 0       | R/W   | 0 ~ 1023             | steps  | Cada passo é um ângulo de resolução mínimo; controle de posição absoluta. O valor máximo corresponde ao ângulo efetivo máximo                                        |
| 44          | 0x2C        | Tempo de execução | 2   | 0       | R/W   | 0 ~ 9999 / -1000~1000| 1 ms / 0.1% | Tempo da posição atual até a posição alvo quando **run speed = 0**. No modo motor, define o duty do PWM de saída; o bit 10 é o bit de direção                          |
| 46          | 0x2E        | Velocidade de execução | 2     | Factory default max speed | R/W | 0 ~ 1000           | steps/s| Passos por segundo (velocidade de movimento)                                                                                                                          |
| 48          | 0x30        | Sinalizador de bloqueio | 1  | 1       | R/W   | 0 ~ 1                | –      | 0: desbloqueia a escrita na EPROM, os valores gravados nos endereços da EPROM são armazenados após desligar; 1: bloqueia a escrita na EPROM, os valores gravados nos endereços da EPROM **não** são armazenados        |
| 49 ~ 56     | 0x32~0x36   | Não definido    | 1     |         |        |                      |        | –                                                                                                                                                                      |

---

### 2.4 Feedback SRAM

| Address DEC | Address HEX | Nome da função        | Bytes | Default | Access | Range | Unit   | Descrição                                                                                                                                                          |
|-------------|-------------|-----------------------|-------|---------|--------|-------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 56          | 0x38        | Posição atual         | 2     | –       | R      | –     | steps  | Posição atual em passos; cada passo é um ângulo de resolução mínimo. Modo de posição absoluta; o valor máximo corresponde ao ângulo efetivo máximo                  |
| 58          | 0x3A        | Velocidade atual      | 2     | –       | R      | –     | steps/s| Velocidade atual do motor em passos por segundo                                                                                                                    |
| 60          | 0x3C        | Carga atual           | 2     | –       | R      | –     | 0.1%   | Ciclo de trabalho atual da saída de controle que aciona o motor; o bit 10 é o bit de direção                                                                       |
| 62          | 0x3E        | Tensão atual          | 1     | –       | R      | –     | 0.1 V  | Tensão de alimentação atual do servo                                                                                                                               |
| 63          | 0x3F        | Temperatura atual     | 1     | –       | R      | –     | °C     | Temperatura interna atual do servo                                                                                                                                 |
| 64          | 0x40        | Sinalizador de escrita assíncrona | 1   | 0       | R      | –     | –      | Sinalizador usado quando se utilizam comandos de escrita assíncrona                                                                                                |
| 65          | 0x41        | Status do servo       | 1     | 0       | R      | –     | –      | Bits definidos como 1 indicam o(s) erro(s) correspondente(s) (veja [3.2](#32-status-do-servo))                                                                     |
| 66          | 0x42        | Sinalizador de movimento | 1     | 0       | R      | –     | –      | 1 enquanto o servo está em movimento; 0 quando atingiu o alvo e parou; permanece 0 se nenhuma nova posição alvo for fornecida                                       |

---

### 2.5 Parâmetros de fábrica

| Address DEC | Address HEX | Nome da função                 | Bytes | Default | Access | Range | Unit | Descrição |
|-------------|-------------|--------------------------------|-------|---------|--------|-------|------|-----------|
| 78          | 0x4E        | Passo máximo no modo PWM       | 1     | 20      | R      | –     | –    | –           |
| 79          | 0x50        | Limiar de velocidade de movimento × 50 | 1     | 1       | R      | –     | –    | –           |
| 80          | 0x51        | DTs (ms)                       | 1     | 20      | R      | –     | –    | –           |
| 81          | 0x52        | Limite mínimo de velocidade × 50 | 1     | 1       | R      | –     | –    | –           |
| 82          | 0x53        | Limite máximo de velocidade × 50 | 1     | –       | R      | –     | –    | –           |
| 83          | 0x54        | Aceleração                     | 1     | 20      | R      | –     | –    | –           |

---

## 3. Descrição dos bytes especiais

---

### 3.1 Fase do servo

**Bits / peso: descrição**

- **BIT0 (1)**: Fase de direção do acionamento  
  - 0: direção normal  
  - 1: direção invertida
- **BIT1 (2)**: –––
- **BIT2 (4)**: –––
- **BIT3 (8)**: Modo de velocidade  
  - 0: velocidade = 0 significa parar  
  - 1: velocidade = 0 significa velocidade máxima
- **BIT4 (16)**: –––
- **BIT5 (32)**: Fase do PWM  
  - 0: em fase  
  - 1: invertida
- **BIT6 (64)**: Modo de tensão  
  - 0: detecção de baixa tensão 1.5 k  
  - 1: detecção de alta tensão 1 k
- **BIT7 (128)**: –––

> Se vários bits estiverem definidos ao mesmo tempo, o **valor de fase** é a **soma** dos valores de todos os bits definidos.

---

### 3.2 Status do servo

**Status do servo: 0 = normal, 1 = falha**

**Bits / peso: descrição**

- **BIT0 (1)**: Status de tensão  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Status de temperatura  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Status de carga  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Se houver várias condições de falha, o **valor de status** é a **soma** dos valores dos bits correspondentes.  
> Exemplo: sobretensão/subtensão e sobretemperatura → status = 4 + 1 = **5**.

---

### 3.3 Condições de descarga

**Condições de descarga: 0 = desabilitado, 1 = habilitado**  
("Unload" = o torque é desligado como proteção.)

**Bits / peso: descrição**

- **BIT0 (1)**: Proteção de tensão  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Proteção contra sobretemperatura  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Proteção contra sobrecarga  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Se vários bits estiverem definidos, o **valor da condição de descarga** é a **soma** dos valores dos bits.  
> Exemplo: proteção de tensão + proteção contra sobretemperatura habilitadas → valor de descarga = 4 + 1 = **5**.

---

### 3.4 Condições de alarme do LED

**Condições de alarme do LED: 0 = desligado, 1 = ligado**

**Bits / peso: descrição**

- **BIT0 (1)**: Alarme de tensão  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Alarme de sobretemperatura  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Alarme de sobrecarga  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Se vários bits estiverem definidos, o **valor da condição de alarme do LED** é a **soma** dos valores dos bits.  
> Exemplo: alarme de tensão + alarme de sobretemperatura habilitados → valor de alarme = 4 + 1 = **5**.
