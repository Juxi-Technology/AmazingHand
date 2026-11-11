---
title: "Protocolo, comandos e calibração dos servos PWM"
description: "Versão PWM do AmazingHand: gestos suportados, calibração do firmware, protocolo serial, referência de comandos, ajuste fino dos parâmetros dos gestos e perguntas frequentes."
version: pwm
---

# Protocolo, comandos e calibração dos servos PWM

Esta página cobre o protocolo serial, os comandos, a calibração e o ajuste fino de parâmetros do firmware PWM. Fiação em [Fiação PWM](../01-hardware/pwm.md); gravação em [Início rápido com PWM](../02-quick-start/pwm.md); controle de desktop/web em [Aplicativo de desktop PWM](../04-desktop/pwm.md) / [Controle web PWM](../03-web-control/pwm.md).

> Os comandos abaixo são executados no diretório `AmazingHand-PWM/` do repositório. Código-fonte do firmware: [`firmware/AmazingHand_Serial/`](../../../AmazingHand-PWM/firmware/AmazingHand_Serial/).

## 1. Visão geral dos comandos e gestos

As primeiras 11 linhas são comandos de gesto; as demais são comandos de acionamento direto, seleção de lado, repetição, parada e teste de link.

| Gesto/comando | Comando | Descrição |
|------|------|------|
| Pedra | 0x01 | Pedra-papel-tesoura: todos os dedos fechados |
| Tesoura | 0x02 | Pedra-papel-tesoura: indicador + médio estendidos em V |
| Papel | 0x03 | Pedra-papel-tesoura: todos os dedos abertos |
| Joinha | 0x04 | Polegar levantado, os demais dedos fechados |
| Provocação 1 | 0x05 | Balança o indicador ("não, não, não") |
| Provocação 2 | 0x06 | Anelar estendido e balançando (no lugar do mindinho) |
| Abrir | 0x07 | Todos os dedos abertos |
| Punho fechado | 0x08 | Todos os dedos fechados |
| OK | 0x09 | Gesto OK |
| Pinça | 0x0A | Gesto de pinça |
| Apontar | 0x0C | Indicador estendido fazendo o gesto de "apontar" |
| Acionamento direto | 0xF0 | Controla diretamente o ângulo dos 8 servos |
| Definir mão esquerda/direita | 0xF1 | Alterna entre os modos mão esquerda/mão direita |
| Repetir | 0xFE | Repete o último gesto |
| Parar | 0xFF | Encerra imediatamente o gesto atual |
| NOP | 0x00 | Teste de link |

> Nota: o comando 0x0B foi desativado (o antigo "polegar para baixo" era repetido com "joinha" e foi removido).

---

## 2. Calibração do firmware (opcional, recomendada na primeira vez)

A posição central e a largura de pulso dos servos precisam ser calibradas conforme o mecanismo real; é possível ajustar diretamente no código-fonte do firmware:

- Edite `middle_pos[8]` e `min_pw/mid_pw/max_pw[8]` no início de `components/hand_servo/hand_servo.c`.

Após a calibração, é preciso recompilar e gravar.

---

## 3. Protocolo de comunicação serial

### 3.1 Camada física

| Parâmetro | Valor |
|------|-----|
| Interface | USB Serial (UART0) |
| Baudrate | **115200** |
| Bits de dados | 8 |
| Paridade | Nenhuma (None) |
| Bits de parada | 1 |
| Controle de fluxo | Nenhum |

### 3.2 Formato do quadro

#### Host → ESP32 (quadro de comando)

```
┌────────┬────────┬──────────┬────────────────┬──────────┐
│  0xAA  │ CMD_ID │ DATA_LEN │ DATA[0 .. N-1] │ CHECKSUM │
│ 1 Byte │ 1 Byte │  1 Byte  │    N Bytes     │  1 Byte  │
└────────┴────────┴──────────┴────────────────┴──────────┘
 Cabeçalho   CMD_ID   Tam. dados    Dados        Checksum
```

- **Cabeçalho**: fixo em `0xAA`, marca o início de um quadro
- **CMD_ID**: número do comando (veja [Referência de comandos](#4-referência-de-comandos))
- **DATA_LEN**: número de bytes da carga de dados (0-8; quadros com mais de 8 são inválidos)
- **DATA**: carga de dados, com comprimento definido por DATA_LEN
- **CHECKSUM**: `CMD_ID ^ DATA_LEN ^ DATA[0] ^ ... ^ DATA[N-1]` (verificação XOR)

> Se DATA_LEN = 0, então CHECKSUM = CMD_ID.

#### ESP32 → host (quadro de resposta)

```
┌────────┬────────┬────────┬──────────┐
│  0xBB  │ CMD_ID │ STATUS │ CHECKSUM │
│ 1 Byte │ 1 Byte │ 1 Byte │  1 Byte  │
└────────┴────────┴────────┴──────────┘
 Cabeçalho   CMD_ID   Status   Checksum
```

- **Cabeçalho**: fixo em `0xBB`
- **CMD_ID**: número do comando original
- **STATUS**: código de status (veja a tabela abaixo)
- **CHECKSUM**: `CMD_ID ^ STATUS`

#### Códigos de status

| STATUS | Significado | Descrição |
|--------|------|------|
| 0x00 | OK | comando aceito, iniciando a execução |
| 0x01 | Comando inválido | CMD_ID não está na tabela de comandos |
| 0x02 | Erro de parâmetro | comprimento ou conteúdo dos dados incorreto |
| 0x03 | Ocupado | gesto em execução, não aceita novos comandos no momento |
| 0x10 | Concluído | gesto terminado |

### 3.3 Sequência de comunicação

```
Host                          ESP32
 │                              │
 │──── [AA 01 00 01] ────────→│  envia o comando "pedra"
 │                              │
 │←─── [BB 01 00 01] ─────────│  ACK: comando aceito
 │                              │
 │                      (executando o gesto)
 │                              │
 │←─── [BB 01 10 11] ─────────│  Concluído: gesto terminado
 │                              │
 │──── [AA 02 00 02] ────────→│  envia o comando "tesoura"
 │                              │
 │←─── [BB 02 00 02] ─────────│  ACK
 │                              │
```

### 3.4 Parar o gesto e timeout de quadro

- Enviar `[AA FF 00 FF]` interrompe a qualquer momento o gesto em execução
- Se o ESP32 não receber um quadro completo em 200 ms, ele o descarta automaticamente (para evitar desincronização permanente por perda de bytes)
- Quadros com checksum incorreto são descartados silenciosamente; o software de PC deve implementar reenvio por timeout

### 3.5 Modo mão esquerda/direita

O modo padrão é mão direita. Envie `[AA F1 01 02 F2]` para alternar para a mão esquerda e `[AA F1 01 01 F1]` para voltar à mão direita. A escolha de mão afeta a direção de movimento do polegar (gestos com polegar, como pedra/tesoura/joinha/OK/pinça).

---

## 4. Referência de comandos

### 4.1 Comandos de gesto (0x01–0x0A, 0x0C)

Esses comandos não precisam de carga de dados (DATA_LEN=0); o ESP32 executa o gesto correspondente assim que os recebe.

| Comando | Quadro HEX | Resposta | Descrição |
|------|--------|------|------|
| Pedra | `AA 01 00 01` | `BB 01 00 01` → `BB 01 10 11` | todos os dedos fechados |
| Tesoura | `AA 02 00 02` | `BB 02 00 02` → `BB 02 10 12` | indicador + médio estendidos |
| Papel | `AA 03 00 03` | `BB 03 00 03` → `BB 03 10 13` | todos os dedos abertos |
| Joinha | `AA 04 00 04` | `BB 04 00 04` → `BB 04 10 14` | polegar levantado |
| Provocação 1 | `AA 05 00 05` | `BB 05 00 05` → `BB 05 10 15` | balança o indicador (cerca de 2,5 s) |
| Provocação 2 | `AA 06 00 06` | `BB 06 00 06` → `BB 06 10 16` | anelar balançando (cerca de 2,5 s) |
| Abrir | `AA 07 00 07` | `BB 07 00 07` → `BB 07 10 17` | todos os dedos abertos |
| Punho fechado | `AA 08 00 08` | `BB 08 00 08` → `BB 08 10 18` | todos os dedos fechados |
| OK | `AA 09 00 09` | `BB 09 00 09` → `BB 09 10 19` | gesto OK |
| Pinça | `AA 0A 00 0A` | `BB 0A 00 0A` → `BB 0A 10 1A` | gesto de pinça |
| Apontar | `AA 0C 00 0C` | `BB 0C 00 0C` → `BB 0C 10 1C` | indicador estendido fazendo o gesto de "apontar" |

### 4.2 Comando de acionamento direto (0xF0)

Controla diretamente o ângulo dos 8 servos; os 8 bytes de dados correspondem aos servos 1-8, cada byte com valor de 0-180.

**Exemplo: todos os servos no meio (90°)**

```
Envio: AA F0 08 5A 5A 5A 5A 5A 5A 5A 5A F8
       │  │  │  └── 8 × 0x5A (90°) ──┘  │
       │  │  │                            └── CHECKSUM
       │  │  └── DATA_LEN = 8
       │  └── CMD_DIRECT_DRIVE
       └── cabeçalho
```

Checksum = `F0 ^ 08 ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A` = `F8`

> Os 8 valores 0x5A iguais, combinados dois a dois por XOR, dão 0x00; no final, `0xF0 ^ 0x08 ^ 0x00 = 0xF8`

**Exemplo: indicador aberto (servo 1 = 170°, servo 2 = 10°), os demais no meio (90°)**

```
Envio: AA F0 08 AA 0A 5A 5A 5A 5A 5A 5A 58
               └─170°  └─10°
```

### 4.3 Definir mão esquerda/direita (0xF1)

1 byte de dados: `0x01` = mão direita, `0x02` = mão esquerda.

```
Definir mão direita: AA F1 01 01 F1
Definir mão esquerda: AA F1 01 02 F2
```

### 4.4 Comandos de controle

| Comando | Quadro HEX | Descrição |
|------|--------|------|
| NOP | `AA 00 00 00` | teste de link, retorna imediatamente `BB 00 00 00` |
| Repetir | `AA FE 00 FE` | repete o último gesto |
| Parar | `AA FF 00 FF` | encerra imediatamente o gesto atual |

### 4.5 Consulta rápida de respostas

Ao receber um comando inválido (usando o 0xFC, que não existe, como exemplo):

```
Envio: AA FC 00 FC
Resposta: BB FC 01 FD    (STATUS=0x01 comando inválido)
```

> Verificação do checksum: `FC ^ 00 = FC`; na resposta, `FC ^ 01 = FD`

---

## 5. Ajuste fino dos parâmetros dos gestos

### 5.1 Localização dos parâmetros

O deslocamento angular de cada gesto é definido por macros `#define`; **não é preciso alterar o código de lógica**, só os valores.

- **Versão ESP-IDF**: seção "Parâmetros dos gestos (ajustáveis pelo usuário)" no início de `components/hand_gestures/hand_gestures.c`

### 5.2 Significado dos parâmetros

```c
// exemplo: gesto de pedra
#define ROCK_IDX_OFF1    70    // deslocamento da junta 1 do indicador
#define ROCK_IDX_OFF2   -70    // deslocamento da junta 2 do indicador
```

- **Valor positivo = flexionar/fechar**, **valor negativo = estender/abrir**
- Cada dedo tem 2 deslocamentos, relativos a `middle_pos` (padrão 90°)
- Estrutura diferencial: os dois servos ficam lado a lado, com eixos colineares; rotação no mesmo sentido gera abdução lateral e em sentidos opostos gera flexão/extensão; a soma dos dois ângulos de deslocamento corresponde à abdução e a diferença à flexão/extensão.

### 5.3 Passos do ajuste

1. Localize a macro `#define` do gesto correspondente
2. Altere o valor (aumentar → amplitude maior; diminuir → amplitude menor)
3. Recompile e grave, e teste o resultado no software de PC
4. Ajuste repetidamente até o movimento ficar natural

---

## 6. Perguntas frequentes

### Q1: O software de PC não conecta à porta serial?

1. Confirme que o ESP32 está conectado ao PC via Type-C
2. Verifique se o número da COM no Gerenciador de Dispositivos é o mesmo selecionado na GUI
3. Confirme o baudrate 115200
4. Desconecte outros softwares que estejam usando a porta serial

### Q2: Enviar um comando não tem efeito?

1. Envie primeiro `AA 00 00 00` (NOP); deve receber `BB 00 00 00`
2. Confirme que o firmware foi gravado e que o chip alvo é ESP32-S3
3. Verifique a fiação (se o GND tem aterramento comum)

### Q3: A amplitude do gesto está errada ou a direção invertida?

Vá ao ajuste fino dos parâmetros dos gestos (veja [seção 5](#5-ajuste-fino-dos-parâmetros-dos-gestos)) e ajuste a macro correspondente.

### Q4: Quais gestos o modo mão esquerda/direita afeta?

Os gestos **com polegar**, como pedra/tesoura/joinha/OK/pinça; ao alternar a mão, a direção do polegar é espelhada.

### Q5: Um dedo trava e não estende?

Antes de executar qualquer gesto de contração, o firmware automaticamente "abre a mão inteira e depois fecha", para evitar que um dedo fique preso pelo gesto anterior. Se ainda travar, verifique a montagem mecânica ou reduza a amplitude de contração.

## Páginas relacionadas

- [Fiação, GPIO e alimentação PWM](../01-hardware/pwm.md)
- [Início rápido com PWM](../02-quick-start/pwm.md)
- [Aplicativo de desktop PWM](../04-desktop/pwm.md)
- [Rastreamento de mãos PWM](../05-hand-tracking/pwm.md)
- [FAQ](../08-faq/faq.md)
