---
title: "Início rápido PWM"
description: "Caminho mais curto para começar com a versão de servos PWM do AmazingHand: cablagem, gravação do firmware, GUI de desktop ou controlo web e primeiros movimentos."
version: pwm
---

# Início rápido PWM

Para a versão ESP32-S3 + 8 servos PWM. Consulte os links de cada capítulo para a explicação completa.

## 1. Cablagem

- Ligue os 8 servos PWM às tomadas 1–8 da placa adaptadora, pela ordem de numeração.
- Ligue PWM1–8 da placa adaptadora aos GPIO 4, 5, 6, 7, 15, 16, 17, 18 do ESP32-S3.
- Ligue 5V/GND da placa adaptadora a uma fonte de 5V/3A, com massa comum com o ESP32.
- Cablagem detalhada: [Cablagem, GPIO e alimentação PWM](../01-hardware/pwm.md).

> Os servos têm de ser **digitais PTK 7452 MG-D (333 Hz)** ou equivalentes; servos analógicos de 50 Hz como o SG90 não podem substituir diretamente.

## 2. Gravar o firmware

### Opção A: binário pré-compilado (recomendado)

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
├── main/main.c                  Tarefas FreeRTOS, fila de comandos e inicialização
└── components/
    ├── hand_servo/              Driver PWM LEDC e calibração dos servos
    ├── hand_gestures/           Macros dos parâmetros de gestos e funções de gestos
    └── hand_protocol/           Análise de frames série e distribuição de comandos
```

> A compilação com ESP-IDF não suporta caminhos com caracteres chineses: tanto o diretório do projeto como o diretório do utilizador devem usar apenas caracteres latinos; recomenda-se ESP-IDF v5.x / v6.x, com o chip alvo **ESP32-S3**.

Após a alimentação, a porta série deve imprimir:

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

## 3. Ligar o software de PC

| Modo | Entrada |
|------|------|
| GUI de desktop | [Aplicação de desktop PWM](../04-desktop/pwm.md): `python AmazingHand-PWM/tools/hand_gui.py` |
| Controlo web | [Controlo web PWM](../03-web-control/pwm.md): escolha o driver **PWM (ESP32-S3)**, porta série 115200 |
| Teste por linha de comandos | `python AmazingHand-PWM/tools/serial_test.py COM3 nop` |

## 4. Primeiros movimentos

1. Após a ligação, o firmware regressa primeiro ao centro (90°); confirme que não há ruídos anómalos nem bloqueio.
2. Utilize os sliders de cada dedo para confirmar um a um o sentido e a posição central.
3. Experimente depois poses de pequena amplitude, como «Abrir / Punho».
4. Se o sentido estiver invertido ou a posição central desviada, ajuste segundo [Protocolo e calibração PWM](../06-servo-tuning/pwm.md).

## Próximos passos

- [Protocolo e calibração PWM](../06-servo-tuning/pwm.md)
- [Seguimento de mãos PWM](../05-hand-tracking/pwm.md)
- [Comparação de versões e seleção](../00-product/version-comparison.md)
