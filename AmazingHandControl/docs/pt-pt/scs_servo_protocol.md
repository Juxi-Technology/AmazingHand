[English](../en/scs_servo_protocol.md) | [Deutsch](../de/scs_servo_protocol.md) | [Español](../es/scs_servo_protocol.md) | [Français](../fr/scs_servo_protocol.md) | [Italiano](../it/scs_servo_protocol.md) | [日本語](../ja/scs_servo_protocol.md) | [한국어](../ko/scs_servo_protocol.md) | [Português (BR)](../pt-br/scs_servo_protocol.md) | Português (PT) | [简体中文](../zh-hans/scs_servo_protocol.md) | [繁體中文](../zh-hant/scs_servo_protocol.md)

# Servo SCSCL com potenciómetro – Descrição da tabela de memória

## Índice

- [Servo SCSCL com potenciómetro – Descrição da tabela de memória](#servo-scscl-com-potenciómetro--descrição-da-tabela-de-memória)
- [1. Protocolo de comunicação do servo](#1-protocolo-de-comunicação-do-servo)
- [2. Definição da tabela de memória do servo](#2-definição-da-tabela-de-memória-do-servo)
  - [2.1 Informações de versão](#21-informações-de-versão)
  - [2.2 Configuração EPROM](#22-configuração-eprom)
  - [2.3 Controlo SRAM](#23-controlo-sram)
  - [2.4 Feedback SRAM](#24-feedback-sram)
  - [2.5 Parâmetros de fábrica](#25-parâmetros-de-fábrica)
- [3. Descrição dos bytes especiais](#3-descrição-dos-bytes-especiais)
  - [3.1 Fase do servo](#31-fase-do-servo)
  - [3.2 Estado do servo](#32-estado-do-servo)
  - [3.3 Condições de descarga](#33-condições-de-descarga)
  - [3.4 Condições de alarme do LED](#34-condições-de-alarme-do-led)

---

## 1. Protocolo de comunicação do servo

O servo usa o **protocolo personalizado FT-SCS**.  

- Taxa de transmissão padrão: **1 Mbps ou 500 kbps**
- Camada física: **barramento único TTL**
- Bits de dados: **8**
- Paridade: **nenhuma**
- Bits de paragem: **1**
- Intervalo de taxa configurável: **38 400 ~ 1 Mbps (500 k)**
- Endereço de comunicação padrão (ID): **1**

Referência do protocolo:  
[FT-SCS Custom Protocol](http://doc.feetech.cn/#/tiaozhunlujingft?srcType=FT-SCS-Protocol-41ad23fe8a244712ba160b93)

---

## 2. Definição da tabela de memória do servo

> Se um endereço de função usar um valor de 2 bytes, o **byte alto** é armazenado no **endereço inferior** e o **byte baixo** no **endereço superior** (big-endian dentro da tabela).

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

| Address DEC | Address HEX | Nome da função                | Bytes | Default | Access | Range       | Unit  | Descrição                                                                                                                                         |
|-------------|-------------|-------------------------------|-------|---------|--------|-------------|-------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 5           | 0x05        | ID do servo                   | 1     | 1       | R/W   | 0 ~ 253     | ID    | ID principal único no barramento                                                                                                                   |
| 6           | 0x06        | Taxa de transmissão           | 1     | 0       | R/W   | 0 ~ 7       | –     | 0–7 representam a taxa: 1000000(0), 500000(1), 250000(2), 128000(3), 115200(4), 76800(5), 57600(6), 38400(7)                                      |
| 7           | 0x07        | Indefinido                    | 1     | –       | R/W   | –           | –     | –                                                                                                                                                  |
| 8           | 0x08        | Nível de retorno de estado    | 1     | 1       | R/W   | 0 ~ 1       | –     | 0: apenas READ e PING devolvem estado; 1: todos os comandos devolvem pacotes de estado                                                             |
| 9           | 0x09        | Limite mínimo de ângulo       | 2     | 20      | R/W   | 0 ~ 1023    | steps | Ângulo mínimo de funcionamento; tem de ser inferior ao ângulo máximo. Se **ângulo mín = ângulo máx = 0** → modo motor (rotação contínua)          |
| 11          | 0x0B        | Limite máximo de ângulo       | 2     | 1003    | R/W   | 1 ~ 1023    | steps | Ângulo máximo de funcionamento; tem de ser superior ao ângulo mínimo. Se **ângulo mín = ângulo máx = 0** → modo motor                              |
| 13          | 0x0D        | Limite máximo de temperatura  | 1     | 70      | R/W   | 0 ~ 100     | °C    |                                                                                                                                                    |
| 14          | 0x0E        | Tensão de entrada máxima      | 1     | –       | R/W   | 0 ~ 254     | 0.1 V | Se **tensão de entrada máx = tensão de entrada mín = 0**, o feedback de tensão é desativado                                                        |
| 15          | 0x0F        | Tensão de entrada mínima      | 1     | 40      | R/W   | 0 ~ 254     | 0.1 V | Se **tensão de entrada máx = tensão de entrada mín = 0**, o feedback de tensão é desativado                                                        |
| 16          | 0x10        | Binário máximo                | 2     | 1000    | R/W   | 0 ~ 1000    | 0.1%  | Ao ligar, este valor é copiado para o endereço 48 (limite de binário)                                                                              |
| 18          | 0x12        | Fase                          | 1     | –       | R/W   | 0 ~ 254     | –     | Byte de função especial; não modificar sem necessidade específica                                                                                  |
| 19          | 0x13        | Condições de descarga         | 1     | –       | R/W   | 0 ~ 254     | –     | Cada bit ativa/desativa uma proteção correspondente (ver [3.3](#33-condições-de-descarga))                                                        |
| 20          | 0x14        | Condições de alarme do LED    | 1     | –       | R/W   | 0 ~ 254     | –     | Cada bit ativa/desativa o piscar do LED para um dado alarme (ver [3.4](#34-condições-de-alarme-do-led))                                           |
| 21          | 0x15        | Ganho P do ciclo de posição   | 1     | –       | R/W   | 0 ~ 254     | –     | Ganho proporcional para o controlo de posição                                                                                                      |
| 22          | 0x16        | Ganho D do ciclo de posição   | 1     | –       | R/W   | 0 ~ 254     | –     | Ganho derivativo para o controlo de posição                                                                                                        |
| 23          | 0x17        | Indefinido                    | 1     | –       | R/W   | –           | –     | –                                                                                                                                                  |
| 24          | 0x18        | Binário mínimo de arranque    | 1     | –       | R/W   | 0 ~ 254     | 0.1%  | Binário mínimo de saída necessário para iniciar o movimento                                                                                        |
| 25          | 0x19        | Indefinido                    | 1     | –       | R/W   | –           | –     | –                                                                                                                                                  |
| 26          | 0x1A        | Zona morta de avanço          | 1     | 1       | R/W   | 0 ~ 16      | steps | A unidade mais pequena é um ângulo de resolução mínimo                                                                                             |
| 27          | 0x1B        | Zona morta de recuo           | 1     | 1       | R/W   | 0 ~ 16      | steps | A unidade mais pequena é um ângulo de resolução mínimo                                                                                             |
| 28 ~ 36     | 0x1C ~ 0x24 | Indefinido                    | 1     | –       | R/W   | –           | –     | –                                                                                                                                                  |
| 37          | 0x25        | Binário de retenção           | 1     | 20      | R/W   | 0 ~ 254     | 1%    | Binário de saída após o acionamento da proteção contra sobrecarga; p. ex. 20 = 20% do binário máximo                                               |
| 38          | 0x26        | Tempo de proteção             | 1     | 200     | R/W   | 0 ~ 254     | 10 ms | Tempo durante o qual a carga excede o binário de sobrecarga antes de a proteção ser acionada; 200 = 2 s, máx. ≈ 2,5 s                              |
| 39          | 0x24        | Binário de sobrecarga         | 1     | 80      | R/W   | 0 ~ 254     | 1%    | Binário-limite para iniciar o temporizador de proteção contra sobrecarga; 80 = 80% do binário máximo                                              |

---

### 2.3 Controlo SRAM

| Address DEC | Address HEX | Nome da função   | Bytes | Default | Access | Range                | Unit   | Descrição                                                                                                                                                              |
|-------------|-------------|-----------------|-------|---------|--------|----------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 40          | 0x28        | Interruptor de binário | 1     | 0       | R/W   | 0 ~ 2                | –      | 0: binário desligado / livre; 1: binário ligado; 2: modo de amortecimento                                                                                             |
| 41          | 0x29        | Indefinido       | 1     | –       | R/W   | –                    | –      | –                                                                                                                                                                      |
| 42          | 0x2A        | Posição alvo     | 2     | 0       | R/W   | 0 ~ 1023             | steps  | Cada passo é um ângulo de resolução mínimo; controlo de posição absoluta. O valor máximo corresponde ao ângulo efetivo máximo                                          |
| 44          | 0x2C        | Tempo de execução| 2     | 0       | R/W   | 0 ~ 9999 / -1000~1000| 1 ms / 0.1% | Tempo da posição atual até à posição alvo quando **velocidade de execução = 0**. Em modo motor, define o ciclo de trabalho do PWM de saída; o bit 10 é o bit de direção |
| 46          | 0x2E        | Velocidade de execução | 2     | Factory default max speed | R/W | 0 ~ 1000           | steps/s| Passos por segundo (velocidade de movimento)                                                                                                                           |
| 48          | 0x30        | Sinalizador de bloqueio | 1     | 1       | R/W   | 0 ~ 1                | –      | 0: desbloqueia a escrita na EPROM, os valores escritos nos endereços da EPROM são armazenados após desligar; 1: bloqueia a escrita na EPROM, os valores escritos nos endereços da EPROM **não** são armazenados |
| 49 ~ 56     | 0x32~0x36   | Indefinido       | 1     |         |        |                      |        | –                                                                                                                                                                      |

---

### 2.4 Feedback SRAM

| Address DEC | Address HEX | Nome da função     | Bytes | Default | Access | Range | Unit   | Descrição                                                                                                                                                        |
|-------------|-------------|-------------------|-------|---------|--------|-------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 56          | 0x38        | Posição atual      | 2     | –       | R      | –     | steps  | Posição atual em passos; cada passo é um ângulo de resolução mínimo. Modo de posição absoluta; o valor máximo corresponde ao ângulo efetivo máximo               |
| 58          | 0x3A        | Velocidade atual   | 2     | –       | R      | –     | steps/s| Velocidade atual do motor em passos por segundo                                                                                                                    |
| 60          | 0x3C        | Carga atual        | 2     | –       | R      | –     | 0.1%   | Ciclo de trabalho da saída de controlo que aciona o motor; o bit 10 é o bit de direção                                                                             |
| 62          | 0x3E        | Tensão atual       | 1     | –       | R      | –     | 0.1 V  | Tensão de alimentação atual do servo                                                                                                                               |
| 63          | 0x3F        | Temperatura atual  | 1   | –       | R      | –     | °C     | Temperatura interna atual do servo                                                                                                                                 |
| 64          | 0x40        | Sinalizador de escrita assíncrona | 1     | 0       | R      | –     | –      | Sinalizador utilizado quando são usados comandos de escrita assíncrona                                                                                            |
| 65          | 0x41        | Estado do servo    | 1     | 0       | R      | –     | –      | Os bits definidos como 1 indicam o(s) erro(s) correspondente(s) (ver [3.2](#32-estado-do-servo))                                                                  |
| 66          | 0x42        | Sinalizador de movimento | 1     | 0       | R      | –     | –      | 1 enquanto o servo está em movimento; 0 quando atingiu o alvo e parou; permanece 0 se não for dada uma nova posição alvo                                         |

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

- **BIT0 (1)**: Fase da direção de acionamento  
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
  - 0: deteção de baixa tensão 1,5 k  
  - 1: deteção de alta tensão 1 k
- **BIT7 (128)**: –––

> Se vários bits estiverem definidos ao mesmo tempo, o **valor da fase** é a **soma** dos valores de todos os bits definidos.

---

### 3.2 Estado do servo

**Estado do servo: 0 = normal, 1 = falha**

**Bits / peso: descrição**

- **BIT0 (1)**: Estado da tensão  
- **BIT1 (2)**: –––  
- **BIT2 (4)**: Estado da temperatura  
- **BIT3 (8)**: –––  
- **BIT4 (16)**: –––  
- **BIT5 (32)**: Estado da carga  
- **BIT6 (64)**: –––  
- **BIT7 (128)**: –––  

> Se estiverem presentes várias condições de falha, o **valor de estado** é a **soma** dos valores dos bits correspondentes.  
> Exemplo: sobretensão/subtensão e sobretemperatura → estado = 4 + 1 = **5**.

---

### 3.3 Condições de descarga

**Condições de descarga: 0 = desativado, 1 = ativado**  
("Descarga" = o binário é desligado como proteção.)

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
> Exemplo: proteção de tensão + proteção contra sobretemperatura ativadas → valor de descarga = 4 + 1 = **5**.

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
> Exemplo: alarme de tensão + alarme de sobretemperatura ativados → valor de alarme = 4 + 1 = **5**.
