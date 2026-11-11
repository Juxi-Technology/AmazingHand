---
title: "Início rápido com PWM"
description: "Caminho mais curto para a versão com servos PWM do AmazingHand: fiação, gravação do firmware, GUI de desktop ou controle web e primeiros movimentos."
version: pwm
---

# Início rápido com PWM

Para a versão ESP32-S3 + 8 servos PWM. Consulte os links de cada capítulo para a documentação completa.

## 1. Fiação

- Conecte os 8 servos PWM aos conectores 1–8 da placa adaptadora, seguindo a numeração.
- Conecte PWM1–8 da placa adaptadora aos GPIO 4, 5, 6, 7, 15, 16, 17 e 18 do ESP32-S3.
- Conecte 5V/GND da placa adaptadora à fonte de 5 V/3 A, com aterramento comum com o ESP32.
- Fiação detalhada: [Fiação, GPIO e alimentação PWM](../01-hardware/pwm.md).

> Os servos devem ser **digitais PTK 7452 MG-D (333 Hz)** ou equivalentes; servos analógicos de 50 Hz como o SG90 não podem substituí-los diretamente.

## 2. Gravação do firmware

### Opção A: bin pré-compilado (recomendado)

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  AmazingHand-PWM/firmware/prebuilt/amazinghand_pwm.bin
```

### Opção B: compilação com ESP-IDF

```bash
cd AmazingHand-PWM/firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

Estrutura do projeto de firmware:

```text
firmware/AmazingHand_Serial/
├── main/main.c                  tarefas FreeRTOS, fila de comandos e inicialização
└── components/
    ├── hand_servo/              driver PWM LEDC e calibração dos servos
    ├── hand_gestures/           macros de parâmetros dos gestos e funções de gesto
    └── hand_protocol/           análise de quadros seriais e despacho de comandos
```

> A compilação com ESP-IDF não aceita caminhos com caracteres chineses: use caminhos em inglês no diretório do projeto e no diretório do usuário; recomenda-se ESP-IDF v5.x / v6.x e o chip alvo **ESP32-S3**.

Ao energizar, a serial deve imprimir:

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

## 3. Conectar o software de PC

| Método | Acesso |
|------|------|
| GUI de desktop | [Aplicativo de desktop PWM](../04-desktop/pwm.md): `python AmazingHand-PWM/tools/hand_gui.py` |
| Controle web | [Controle web PWM](../03-web-control/pwm.md): selecione o driver **PWM (ESP32-S3)**, serial 115200 |
| Teste por linha de comando | `python AmazingHand-PWM/tools/serial_test.py COM3 nop` |

## 4. Primeiros movimentos

1. Ao conectar, o firmware primeiro retorna ao meio (90°); confirme que não há ruído anormal nem travamento.
2. Use os controles deslizantes de cada dedo para confirmar a direção e o meio, um a um.
3. Depois teste poses de pequena amplitude, como “abrir / punho fechado”.
4. Se a direção estiver invertida ou o meio deslocado, ajuste conforme [Protocolo e calibração PWM](../06-servo-tuning/pwm.md).

## Próximos passos

- [Protocolo e calibração PWM](../06-servo-tuning/pwm.md)
- [Rastreamento de mãos PWM](../05-hand-tracking/pwm.md)
- [Comparação de versões e escolha](../00-product/version-comparison.md)
