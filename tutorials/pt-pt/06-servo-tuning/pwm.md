---
title: "Protocolo, comandos e calibração dos servos PWM"
description: "Versão PWM do AmazingHand: gestos suportados, calibração do firmware, protocolo de porta série, referência de comandos, afinação dos parâmetros de gestos e perguntas frequentes."
version: pwm
---

# Protocolo, comandos e calibração dos servos PWM

Esta página cobre o protocolo de porta série, os comandos, a calibração e a afinação de parâmetros do firmware PWM. Para cablagem, consulte [Cablagem PWM](../01-hardware/pwm.md); para gravação, [Início rápido PWM](../02-quick-start/pwm.md); para controlo de desktop/web, [Aplicação de desktop PWM](../04-desktop/pwm.md) / [Controlo web PWM](../03-web-control/pwm.md).

> Os comandos seguintes são executados no diretório `AmazingHand-PWM/` do repositório. Código-fonte do firmware: [`firmware/AmazingHand_Serial/`](../../../AmazingHand-PWM/firmware/AmazingHand_Serial/).

## 1. Visão geral de comandos e gestos

As primeiras 11 linhas são comandos de gestos; as restantes são comandos de acionamento direto, seleção de lado, repetição, paragem e teste de ligação.

| Gesto/comando | Comando | Descrição |
|------|------|------|
| Pedra | 0x01 | Pedra-papel-tesoura: todos os dedos fechados |
| Tesoura | 0x02 | Pedra-papel-tesoura: indicador + médio esticados em V |
| Papel | 0x03 | Pedra-papel-tesoura: todos os dedos abertos |
| Fixe | 0x04 | Polegar levantado, restantes dedos fechados |
| Provocação 1 | 0x05 | Abanar o indicador ("não, não, não")|
| Provocação 2 | 0x06 | Anelar esticado a oscilar (substitui o mindinho)|
| Abrir | 0x07 | Todos os dedos abertos |
| Punho | 0x08 | Todos os dedos fechados |
| OK | 0x09 | Gesto OK |
| Pinça | 0x0A | Gesto de pinça |
| Apontar | 0x0C | Indicador esticado em gesto de "apontar" |
| Acionamento direto | 0xF0 | Controlo direto dos ângulos dos 8 servos |
| Definir mão esquerda/direita | 0xF1 | Alterna entre modo mão esquerda/mão direita |
| Repetir | 0xFE | Repete o último gesto |
| Parar | 0xFF | Termina imediatamente o gesto atual |
| NOP | 0x00 | Teste de ligação |

> Nota: o comando 0x0B está desativado (o antigo "polegar para baixo" repetia o gesto "Fixe" e foi removido).

---

## 2. Calibração do firmware (opcional, recomendada na primeira utilização)

A posição central e a largura de pulso dos servos devem ser calibradas para o mecanismo real; podem ser alteradas diretamente no código-fonte do firmware:

- Edite `middle_pos[8]` e `min_pw/mid_pw/max_pw[8]` no topo de `components/hand_servo/hand_servo.c`.

Após a calibração, é necessário voltar a compilar e gravar.

---

## 3. Protocolo de comunicação série

### 3.1 Camada física

| Parâmetro | Valor |
|------|-----|
| Interface | USB Serial (UART0) |
| Baudrate | **115200** |
| Bits de dados | 8 |
| Bit de paridade | Nenhum (None) |
| Bits de paragem | 1 |
| Controlo de fluxo | Nenhum |

### 3.2 Formato dos frames

#### PC → ESP32 (frame de comando)

```
┌────────┬────────┬──────────┬────────────────┬──────────┐
│  0xAA  │ CMD_ID │ DATA_LEN │ DATA[0 .. N-1] │ CHECKSUM │
│ 1 Byte │ 1 Byte │  1 Byte  │    N Bytes     │  1 Byte  │
└────────┴────────┴──────────┴────────────────┴──────────┘
 Cabeçalho  ID do comando  Comprimento dos dados  Carga útil  Soma de verificação
```

- **Cabeçalho**: `0xAA` fixo, identifica o início de um frame
- **CMD_ID**: número do comando (ver [Referência de comandos](#4-referência-de-comandos))
- **DATA_LEN**: número de bytes da carga útil (0-8; frames com mais de 8 são inválidos)
- **DATA**: carga útil, com comprimento determinado por DATA_LEN
- **CHECKSUM**: `CMD_ID ^ DATA_LEN ^ DATA[0] ^ ... ^ DATA[N-1]` (verificação XOR)

> Se DATA_LEN = 0, então CHECKSUM = CMD_ID.

#### ESP32 → PC (frame de resposta)

```
┌────────┬────────┬────────┬──────────┐
│  0xBB  │ CMD_ID │ STATUS │ CHECKSUM │
│ 1 Byte │ 1 Byte │ 1 Byte │  1 Byte  │
└────────┴────────┴────────┴──────────┘
 Cabeçalho  ID do comando  Código de estado  Soma de verificação
```

- **Cabeçalho**: `0xBB` fixo
- **CMD_ID**: número do comando original
- **STATUS**: código de estado (ver tabela abaixo)
- **CHECKSUM**: `CMD_ID ^ STATUS`

#### Códigos de estado

| STATUS | Significado | Descrição |
|--------|------|------|
| 0x00 | OK | Comando aceite, execução iniciada |
| 0x01 | Comando inválido | CMD_ID não existe na tabela de comandos |
| 0x02 | Erro de parâmetro | Comprimento ou conteúdo dos dados incorreto |
| 0x03 | Ocupado | Gesto em execução; não aceita novos comandos por agora |
| 0x10 | Concluído | Gesto concluído |

### 3.3 Temporização da comunicação

```
PC                            ESP32
 │                              │
 │──── [AA 01 00 01] ────────→│  envia o comando "Pedra"
 │                              │
 │←─── [BB 01 00 01] ─────────│  ACK: comando aceite
 │                              │
 │                      (a executar o gesto)
 │                              │
 │←─── [BB 01 10 11] ─────────│  concluído: gesto terminado
 │                              │
 │──── [AA 02 00 02] ────────→│  envia o comando "Tesoura"
 │                              │
 │←─── [BB 02 00 02] ─────────│  ACK
 │                              │
```

### 3.4 Parar gestos e timeout de frames

- Enviar `[AA FF 00 FF]` interrompe a qualquer momento o gesto em execução
- Se o ESP32 não receber um frame completo em 200 ms, descarta-o automaticamente (para evitar perda permanente de sincronismo por perda de bytes)
- Frames com soma de verificação errada são descartados silenciosamente; o software de PC deve implementar reenvio com timeout

### 3.5 Modos de mão esquerda/direita

O modo predefinido é mão direita. Envie `[AA F1 01 02 F2]` para mudar para a mão esquerda e `[AA F1 01 01 F1]` para voltar à mão direita. A mão esquerda/direita afeta o sentido de movimento do polegar (gestos com polegar, como Pedra/Tesoura/Fixe/OK/Pinça).

---

## 4. Referência de comandos

### 4.1 Comandos de gestos (0x01–0x0A, 0x0C)

Estes comandos não requerem carga útil (DATA_LEN=0); o ESP32 executa imediatamente o gesto correspondente ao receber.

| Comando | Frame HEX | Resposta | Descrição |
|------|--------|------|------|
| Pedra | `AA 01 00 01` | `BB 01 00 01` → `BB 01 10 11` | Todos os dedos fechados |
| Tesoura | `AA 02 00 02` | `BB 02 00 02` → `BB 02 10 12` | Indicador + médio esticados |
| Papel | `AA 03 00 03` | `BB 03 00 03` → `BB 03 10 13` | Todos os dedos abertos |
| Fixe | `AA 04 00 04` | `BB 04 00 04` → `BB 04 10 14` | Polegar levantado |
| Provocação 1 | `AA 05 00 05` | `BB 05 00 05` → `BB 05 10 15` | Abanar o indicador (cerca de 2,5 s) |
| Provocação 2 | `AA 06 00 06` | `BB 06 00 06` → `BB 06 10 16` | Anelar a oscilar (cerca de 2,5 s) |
| Abrir | `AA 07 00 07` | `BB 07 00 07` → `BB 07 10 17` | Todos os dedos abertos |
| Punho | `AA 08 00 08` | `BB 08 00 08` → `BB 08 10 18` | Todos os dedos fechados |
| OK | `AA 09 00 09` | `BB 09 00 09` → `BB 09 10 19` | Gesto OK |
| Pinça | `AA 0A 00 0A` | `BB 0A 00 0A` → `BB 0A 10 1A` | Gesto de pinça |
| Apontar | `AA 0C 00 0C` | `BB 0C 00 0C` → `BB 0C 10 1C` | Indicador esticado em gesto de "apontar" |

### 4.2 Comando de acionamento direto (0xF0)

Controla diretamente os ângulos dos 8 servos; os 8 bytes de dados correspondem aos servos 1-8, com cada byte entre 0-180.

**Exemplo: todos os servos ao centro (90°)**

```
Envio: AA F0 08 5A 5A 5A 5A 5A 5A 5A 5A F8
       │  │  │  └── 8 × 0x5A (90°) ──┘  │
       │  │  │                            └── CHECKSUM
       │  │  └── DATA_LEN = 8
       │  └── CMD_DIRECT_DRIVE
       └── cabeçalho
```

Soma de verificação = `F0 ^ 08 ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A ^ 5A` = `F8`

> 8 valores iguais a 0x5A fazem XOR dois a dois e dão 0x00, resultando em `0xF0 ^ 0x08 ^ 0x00 = 0xF8`

**Exemplo: indicador aberto (servo 1=170°, servo 2=10°), restantes ao centro (90°)**

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

### 4.4 Comandos de controlo

| Comando | Frame HEX | Descrição |
|------|--------|------|
| NOP | `AA 00 00 00` | Teste de ligação; devolve imediatamente `BB 00 00 00` |
| Repetir | `AA FE 00 FE` | Repete o último gesto |
| Parar | `AA FF 00 FF` | Termina imediatamente o gesto atual |

### 4.5 Respostas (referência rápida)

Ao receber um comando inválido (usando o comando inexistente 0xFC como exemplo):

```
Envio: AA FC 00 FC
Resposta: BB FC 01 FD    (STATUS=0x01 comando inválido)
```

> Verificação da soma: `FC ^ 00 = FC`, e na resposta `FC ^ 01 = FD`

---

## 5. Afinação dos parâmetros de gestos

### 5.1 Localização dos parâmetros

O desvio angular de cada gesto é definido com macros `#define`, **sem necessidade de alterar o código lógico**; apenas os valores numéricos.

- **Versão ESP-IDF**: secção "Parâmetros de gestos (ajustáveis pelo utilizador)" no topo de `components/hand_gestures/hand_gestures.c`

### 5.2 Significado dos parâmetros

```c
// Exemplo: gesto Pedra
#define ROCK_IDX_OFF1    70    // desvio da articulação 1 do indicador
#define ROCK_IDX_OFF2   -70    // desvio da articulação 2 do indicador
```

- **Valor positivo = fletir e fechar**, **valor negativo = estender e abrir**
- Cada dedo tem 2 desvios, relativos a `middle_pos` (predefinido 90°)
- Estrutura diferencial: os dois servos ficam lado a lado, com eixos colineares; a rotação no mesmo sentido produz abertura lateral e a rotação em sentidos opostos produz flexão; a soma dos dois desvios corresponde à abertura, e a diferença à flexão.

### 5.3 Passos de afinação

1. Encontre a macro `#define` do gesto correspondente
2. Altere o valor (aumentar → maior amplitude; diminuir → menor amplitude)
3. Volte a compilar e gravar e teste com o software de PC
4. Ajuste repetidamente até o movimento ficar natural

---

## 6. Perguntas frequentes

### P1: O software de PC não consegue ligar-se à porta série?

1. Confirme que o ESP32 está ligado ao PC por Type-C
2. Verifique se o número COM no Gestor de Dispositivos corresponde ao selecionado na GUI
3. Confirme o baudrate 115200
4. Feche outros programas que ocupem a porta série

### P2: Enviar comandos não produz reação?

1. Envie primeiro `AA 00 00 00` (NOP); deve receber `BB 00 00 00`
2. Confirme que o firmware foi gravado e que o chip alvo é o ESP32-S3
3. Verifique a cablagem (o GND tem massa comum?)

### P3: Amplitude do gesto errada ou sentido invertido?

Aceda à afinação dos parâmetros de gestos (ver [secção 5](#5-afinação-dos-parâmetros-de-gestos)) e ajuste a macro correspondente.

### P4: Que gestos são afetados pelo modo mão esquerda/direita?

Gestos **com polegar**, como Pedra/Tesoura/Fixe/OK/Pinça; ao alternar a mão, o sentido do espelhamento do polegar muda.

### P5: Um dedo fica preso e não estica?

Antes de executar qualquer gesto de contração, a mão abre totalmente e depois fecha, evitando que os dedos fiquem bloqueados pelo gesto anterior. Se ainda ficar preso, verifique a montagem mecânica ou reduza a amplitude de contração.

## Páginas relacionadas

- [Cablagem, GPIO e alimentação PWM](../01-hardware/pwm.md)
- [Início rápido PWM](../02-quick-start/pwm.md)
- [Aplicação de desktop PWM](../04-desktop/pwm.md)
- [Seguimento de mãos PWM](../05-hand-tracking/pwm.md)
- [FAQ](../08-faq/faq.md)
