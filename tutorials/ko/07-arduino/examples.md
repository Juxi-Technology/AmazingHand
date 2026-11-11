---
title: "Arduino와 Python 예제"
description: "AmazingHand 공식 Arduino/Python 예제: SCServo 라이브러리, Feetech 디버깅 도구, TTL Linker 배선 모드, Arduino Uno/Mega 시리얼과 Python 기본 스크립트."
version: scs0009
---

# Arduino와 Python 예제

이 페이지는 `AmazingHand-main/ArduinoExample/`과 `AmazingHand-main/PythonExample/`의 공식 예제와 배선 요점을 정리합니다.

## Arduino 예제

### 준비 작업

- Arduino IDE의 라이브러리 관리자에서 **SCServo** 라이브러리를 설치합니다.
- Feetech FD 디버깅 도구(`feetech debug tool`)로 서보 ID를 설정합니다.
- Arduino와 TTL Linker 사이는 **RX/TX 교차 연결**합니다.

### Link 모드: 서보 ID 변경

1. 먼저 Arduino에 `Blink` 예제를 업로드합니다.
2. Link 모드로 배선하고 Feetech 소프트웨어를 열어 ID를 수정합니다.

![Link 모드 배선](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Link-mode.jpg)

![SCServo 라이브러리 설치](../../assets/robot-arms/amazing-hand/arduino-extension/SCServo.jpg)

### Control 모드: Arduino로 서보 제어

사용자 정의 프로그램을 업로드한 뒤 Control 모드로 배선합니다:

![Control 모드 배선](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Control-mode.jpg)

- **Arduino Uno**(시리얼 포트 하나): 그림과 같이 소프트웨어 시리얼/지정 핀 사용.
- **Arduino Mega**: **RX1 / TX1(19 / 18)** 사용.

![Uno 시리얼 배선](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Uno.jpg)

![Mega 시리얼 배선](../../assets/robot-arms/amazing-hand/arduino-extension/Arduino_Mega.jpg)

> 핀 번호, 라이브러리 버전, TTL Linker 방향은 실제 보드 실크스크린 기준입니다; ID 변경 전에 버스 전원과 공통 접지를 확인하세요.

## Python 예제

`AmazingHand-main/PythonExample/`은 기본 스크립트 4개를 제공합니다:

| 스크립트 | 역할 |
|------|------|
| `AmazingHand_Demo.py` | 한 손 기본 데모: 버스 연결, 동작 실행 |
| `AmazingHand_Demo_Both.py` | 양손 데모 |
| `AmazingHand_FingerTest.py` | 손가락별 테스트 |
| `AmazingHand_Hand_FingerMiddlePos.py` | 손가락 중간 위치 캘리브레이션 |

사용 전:

1. Feetech 소프트웨어로 서보 ID 설정(오른손 1–8, 왼손 11–18).
2. `pyserial` 설치, 스크립트 내 시리얼 포트명/보드레이트를 수정한 뒤 실행.
3. 외부 서보 전원이 연결되고 버스 드라이버 보드와 공통 접지되었는지 확인.

> 공식 기본 예제입니다; 더 완전한 GUI/CLI는 [SCS0009 데스크톱 제어 프로그램](../04-desktop/scs0009.md), TTL 배선과 중간 위치는 [SCS0009 서보 디버깅과 캘리브레이션](../06-servo-tuning/scs0009.md)을 참고하세요.

## 소스 위치

- [`AmazingHand-main/ArduinoExample/`](../../../AmazingHand-main/ArduinoExample/)
- [`AmazingHand-main/PythonExample/`](../../../AmazingHand-main/PythonExample/)
