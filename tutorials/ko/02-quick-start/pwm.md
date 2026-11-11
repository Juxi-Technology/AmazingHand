---
title: "PWM 빠른 시작"
description: "AmazingHand PWM 서보 버전 최단 시작 경로: 배선, 펌웨어 플래싱, 데스크톱 GUI 또는 웹 제어, 최초 동작."
version: pwm
---

# PWM 빠른 시작

ESP32-S3 + PWM 서보 8채널 버전에 적합합니다. 전체 설명은 각 장의 링크를 참고하세요.

## 1. 배선

- PWM 서보 8개를 번호에 맞춰 어댑터 보드의 서보 1–8에 꽂습니다.
- 어댑터 보드의 PWM1–8을 ESP32-S3 GPIO 4, 5, 6, 7, 15, 16, 17, 18에 연결합니다.
- 어댑터 보드의 5V/GND를 5V/3A 전원에 연결하고 ESP32와 공통 접지합니다.
- 상세 배선: [PWM 배선, GPIO와 전원 공급](../01-hardware/pwm.md).

> 서보는 반드시 **PTK 7452 MG-D 디지털 서보(333 Hz)** 또는 동급이어야 합니다; SG90 등 50 Hz 아날로그 서보로 직접 대체할 수 없습니다.

## 2. 펌웨어 플래싱

### 방식 A: 사전 빌드된 bin(권장)

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  AmazingHand-PWM/firmware/prebuilt/amazinghand_pwm.bin
```

### 방식 B: ESP-IDF 컴파일

```bash
cd AmazingHand-PWM/firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

펌웨어 프로젝트 구조:

```text
firmware/AmazingHand_Serial/
├── main/main.c                  FreeRTOS 작업, 명령 큐 및 초기화
└── components/
    ├── hand_servo/              LEDC PWM 드라이버와 서보 캘리브레이션
    ├── hand_gestures/           제스처 파라미터 매크로와 제스처 함수
    └── hand_protocol/           시리얼 프레임 파싱과 명령 디스패치
```

> ESP-IDF 컴파일은 중국어 경로를 지원하지 않습니다: 프로젝트 디렉터리와 사용자 디렉터리 모두 영문을 사용하세요; ESP-IDF v5.x / v6.x를 권장하며 대상 칩은 **ESP32-S3**를 선택합니다.

전원을 켜면 시리얼 포트에 다음이 출력되어야 합니다:

```
AmazingHand Serial Control Ready (ESP-IDF)
Protocol: 115200-8N1 [0xAA CMD LEN DATA CKSUM]
```

## 3. 호스트 PC 연결

| 방식 | 경로 |
|------|------|
| 데스크톱 GUI | [PWM 데스크톱 제어 프로그램](../04-desktop/pwm.md): `python AmazingHand-PWM/tools/hand_gui.py` |
| 웹 제어 | [PWM 웹 제어](../03-web-control/pwm.md): 드라이버에서 **PWM(ESP32-S3)** 선택, 시리얼 115200 |
| 명령줄 테스트 | `python AmazingHand-PWM/tools/serial_test.py COM3 nop` |

## 4. 최초 동작

1. 연결하면 펌웨어가 먼저 중간 위치(90°)로 복귀합니다; 이상음/걸림이 없는지 확인하세요.
2. 손가락별 슬라이더로 방향과 중간 위치를 하나씩 확인합니다.
3. 그다음 "펼치기 / 주먹 쥐기" 등 작은 범위의 포즈를 시도합니다.
4. 방향이 반대이거나 중간 위치가 어긋나면 [PWM 프로토콜과 캘리브레이션](../06-servo-tuning/pwm.md)에 따라 조정합니다.

## 다음 단계

- [PWM 프로토콜과 캘리브레이션](../06-servo-tuning/pwm.md)
- [PWM 손 추적](../05-hand-tracking/pwm.md)
- [버전 비교와 선택](../00-product/version-comparison.md)
