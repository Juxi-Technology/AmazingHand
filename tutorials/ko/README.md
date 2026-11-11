---
title: "AmazingHand 로봇 손 튜토리얼 개요"
description: "AmazingHand 로봇 손 통합 튜토리얼 입구: SCS0009 시리얼 서보 버전과 PWM 서보 버전의 제품 선택, 하드웨어 배선, 빠른 시작, 웹 제어, 데스크톱 제어 프로그램, 손 추적, 서보 디버깅과 FAQ."
version: both
---

# AmazingHand 로봇 손 튜토리얼

AmazingHand는 오픈 소스이며 3D 프린팅이 가능한 인간형 로봇 손입니다: 손가락 4개, 자유도 8개, 모든 액추에이터가 손 내부에 내장되어 있으며 전체 무게는 약 400 g입니다. 현재 두 가지 하드웨어 방식을 제공하며, 기계 구조는 동일하고 서보, 드라이버 보드, 통신 방식이 다릅니다.

## 버전 먼저 선택

| 비교 항목 | SCS0009 시리얼 버스 버전 | PWM 서보 버전 |
|--------|--------------------|------------|
| 추천 시나리오 | 정밀 각도 제어, 데이터 읽기, SO-ARM101 / LeRobot 데이터 수집 및 학습 연동 | 독립 데모, 제스처 상호작용, 웹/데스크톱 빠른 시작 |
| 서보 | Feetech SCS0009 시리얼 버스 서보 ×8 | PTK 7452 MG-D **디지털** PWM 서보 ×8 |
| 서보 사양 | 2.3 kg·cm@6V, 300° 제어 가능, 0.293° 정밀도 | 4.5 kg·cm@7.4V(5V 공급 시 약 2.8–3 kg·cm), 180°±10°, 333 Hz |
| 위치/온도/전압 피드백 | ✅ 지원 | ❌ 읽기 없음, 걸림이나 탈조 감지 불가 |
| 메인 컨트롤러 | 온보드 없음, PC/라즈베리 파이가 버스 드라이버 보드를 통해 직접 연결 | ESP32-S3 온보드 펌웨어 |
| 전원 | 7–12V(DC5521) 드라이버 보드 입력 | 5V / 3A 이상, 반드시 공통 접지 |
| 통신 | 1,000,000 보드레이트 버스 프로토콜 | 호스트 PC↔ESP32 시리얼 **115200**(서보 자체에는 보드레이트 없음) |
| 서보 ID | 반드시 설정: 오른손 1–8, 왼손 11–18 | ID 설정 없음, 고정 채널 CH1–CH8: 검지 1/2, 중지 3/4, 약지 5/6, 엄지 7/8 |
| 펌웨어 | 플래싱 불필요 | ESP-IDF 컴파일 필요, 또는 사전 빌드된 bin 직접 플래싱 |

> **위치 읽기, 정밀도 또는 LeRobot 학습 데이터 수집**이 필요하면 SCS0009를, **독립 데모, 제스처 상호작용, 빠른 시작**만 필요하면 PWM을 선택하세요.

전체 비교와 선택 설명은 [버전 비교](00-product/version-comparison.md)를 참고하세요.

## 사용 방식별 탐색

| 사용 방식 | SCS0009 시리얼 버스 버전 | PWM 서보 버전 |
|----------|--------------------|------------|
| 빠른 시작 | [SCS0009 빠른 시작](02-quick-start/scs0009.md) | [PWM 빠른 시작](02-quick-start/pwm.md) |
| 웹 제어 | [SCS0009 웹 제어](03-web-control/scs0009.md) | [PWM 웹 제어](03-web-control/pwm.md) |
| 데스크톱 제어 프로그램 / CLI | [SCS0009 GUI와 CLI](04-desktop/scs0009.md) | [PWM 데스크톱 제어 프로그램](04-desktop/pwm.md) |
| 손 추적 | [SCS0009 공식 Demo](05-hand-tracking/scs0009.md) | [PWM GUI / dora 추적](05-hand-tracking/pwm.md) |
| 서보 디버깅과 캘리브레이션 | [SCS0009 디버깅과 캘리브레이션](06-servo-tuning/scs0009.md) | [PWM 프로토콜과 캘리브레이션](06-servo-tuning/pwm.md) |
| Arduino / 2차 개발 | [Arduino Nano](07-arduino/arduino-nano.md) · [예제 코드](07-arduino/examples.md) | 동일(기계 구조 공유) |

웹 제어 개요(드라이버 전환, 시리얼 포트 바, 화면 설명)는 [웹 제어 README](03-web-control/README.md)를 참고하세요.

## 시작하기 전에

- [제품 자료](00-product/product-info.md) — 사양, 포지셔닝, 자료
- [버전 비교와 선택](00-product/version-comparison.md) — 두 하드웨어의 전체 차이
- [하드웨어 개요](01-hardware/overview.md) — 구조, CAD, 조립, 3D 프린팅
- [SCS0009 배선](01-hardware/scs0009.md) / [PWM 배선](01-hardware/pwm.md)
- [카메라 키트 설치](01-hardware/camera-kit.md)
- [다운로드와 리소스](00-product/downloads.md)

## 안전 안내

- 외부 서보 전원과 ESP32/드라이버 보드는 반드시 **공통 접지**해야 합니다.
- 최초 전원 투입 전에 로봇 손을 중간 위치에 두고, 서보 혼을 중간 위치 기준으로 장착해 스트로크 끝에 닿지 않게 하세요.
- SCS0009와 PWM 두 하드웨어는 **동시에 한 세트만 연결**하고, 혼용하지 마세요.
- PWM 서보는 위치 피드백이 없어 E-stop으로 제스처만 중단할 수 있으며, 버스 서보처럼 토크를 읽거나 해제할 수 없습니다.

## Languages

[简体中文](../zh-hans/README.md) | [English](../en/README.md) | [Deutsch](../de/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Italiano](../it/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [Português (BR)](../pt-br/README.md) | [Português (PT)](../pt-pt/README.md) | [繁體中文](../zh-hant/README.md)
