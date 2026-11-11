---
title: "Arduino Nano 사용 튜토리얼"
description: "Arduino Nano(328P)와 서보 드라이버 보드로 AmazingHand '02 데모 프로그램' 실행: 배선, 라이브러리 설치, 컴파일 업로드와 실행 결과."
version: scs0009
---

# Arduino Nano 사용 튜토리얼

> 이 페이지는 **SCS0009 버스 서보 버전**의 Arduino Nano 데모입니다. TTL 배선과 ID 설정은 [SCS0009 서보 디버깅과 캘리브레이션](../06-servo-tuning/scs0009.md), 더 많은 예제는 [Arduino / Python 예제](examples.md)를 참고하세요.


## 배선 방식(서보 드라이버 보드 + Nano 보드)

**Nano 보드(즉 328P 개발 보드)의 핀 위치를 정확히 확인하세요!**

![Nano 보드 핀 위치(1)](../../assets/robot-arms/amazing-hand/arduino-nano/01.png)

![Nano 보드 핀 위치(2)](../../assets/robot-arms/amazing-hand/arduino-nano/02.png)

![Nano 보드 핀 위치(3)](../../assets/robot-arms/amazing-hand/arduino-nano/03.png)

![Nano 보드 핀 위치(4)](../../assets/robot-arms/amazing-hand/arduino-nano/04.png)

아래는 MCU를 사용한 디버깅 과정을 설명합니다. MCU 자체가 데모 프로그램을 계속 반복 실행하므로 데이터 케이블만 분리하면 멈춥니다.

## "02 데모 프로그램" 실행

1. Arduino IDE를 직접 설치합니다.

2. **왼손/오른손**에 따라 해당 `.ino` 파일을 엽니다.

   ![왼손/오른손에 대응하는 02 데모 프로그램 ino 파일](../../assets/robot-arms/amazing-hand/arduino-nano/05.png)

3. Arduino 프로그램을 컴파일해 Nano 보드에 업로드하기 전에 "라이브러리 관리자"에서 **FTServo 라이브러리**와 **SCServo 라이브러리**를 설치합니다.

   ![라이브러리 관리자에서 FTServo와 SCServo 라이브러리 설치](../../assets/robot-arms/amazing-hand/arduino-nano/06.png)

4. Nano 보드 종류에서 "**Arduino Nano**" 선택.

   ![개발 보드 종류에서 Arduino Nano 선택](../../assets/robot-arms/amazing-hand/arduino-nano/07.png)

5. 컴파일 및 업로드.

> **주의:** 이때 PC는 Nano 보드에만 단독 연결하고, Nano 보드는 서보 드라이버 보드에 연결하지 않습니다(즉 로봇 손과 연결하지 않음).

업로드 성공 후 Nano 보드를 점퍼 와이어 3개로 서보 드라이버 보드에 연결하고, 서보를 서보 드라이버 보드에 연결합니다. [MEGA328P Nano 보드 디버깅 시 배선 방식](https://juxitech.feishu.cn/wiki/Wt46wtt26imdWkkQlxTcL87qnHd#share-HdS4dNgwyo2seVxRZ9PcZ1R3nuc) 참고.

로봇 손은 "02 데모 프로그램"을 계속 반복 실행하며, 실행 결과는 다음과 같습니다:

![02 데모 프로그램 실행 결과](../../assets/robot-arms/amazing-hand/arduino-nano/08.png)
