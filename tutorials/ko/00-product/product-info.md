---
title: "AmazingHand 제품 자료"
description: "AmazingHand 로봇 손 제품 자료: 기계 구조, 치수, 부하, 두 가지 서보 방식과 오픈 소스 리소스."
version: both
---

# AmazingHand 제품 자료

AmazingHand는 오픈 소스이며 3D 프린팅이 가능한 인간형 로봇 손으로, 임바디드 AI 연구, 로봇 교육, 인간-로봇 상호작용 프로토타입을 대상으로 합니다. 로봇 손 본체는 동일하며 현재 **SCS0009 시리얼 버스 서보**와 **PWM 서보(ESP32-S3)** 두 가지 하드웨어 방식을 제공합니다.

## 기계 구조

- **손가락 4개, 자유도 8개**: 손가락마다 자유도 2개(굴곡/신전 + 모음/벌림)이며, 서보 2개가 병렬 기구로 차동 구동합니다.
- **액추에이터 내장**: 모든 서보가 손에 장착되어 있어 팔뚝으로 케이블을 빼낼 필요가 없습니다.
- **3D 프린팅**: 외형과 링크를 프린팅할 수 있으며 전체 손 무게는 약 400 g입니다.
- **양손 지원**: 왼손 또는 오른손을 단독으로 사용하거나, 양손 로봇으로 협응시킬 수 있습니다.
- **손목 인터페이스**: 원본 설계는 Reachy 2의 Orbita 3D 손목에 맞춰져 있으며, 다른 로봇 팔로도 연결할 수 있습니다.

## 기본 사양

| 파라미터 | 사양 |
|------|------|
| 무게 | 약 0.416 kg |
| 손가락 수 | 4 |
| 손가락당 자유도 | 2 DoF |
| 신장 높이(베이스 제외) | 195 mm |
| 손바닥 너비 | 105 mm |
| 손바닥 두께 | 약 90 mm |
| 검지와 엄지 최대 벌림 거리 | 180 mm |
| 손가락당 하중 | 약 0.2 kg |
| 네 손가락으로 꽉 쥔 최대 하중 | 약 0.5 kg |

> 부하, 전압, 서보 사양은 선택한 서보 버전에 따라 다릅니다; 전체 대조는 [버전 비교와 선택](version-comparison.md)을 참고하세요.

## 두 가지 하드웨어 방식

| 항목 | SCS0009 시리얼 버스 버전 | PWM 서보 버전 |
|------|--------------------|------------|
| 서보 | Feetech SCS0009 ×8 | PTK 7452 MG-D 디지털 PWM 서보 ×8 |
| 제어 | PC/라즈베리 파이 + 버스 드라이버 보드 | ESP32-S3 온보드 펌웨어 |
| 피드백 | 위치/속도/전압/온도 읽기 | 읽기 없음 |
| 적용 | 정밀도, 데이터 수집, LeRobot / SO-ARM101 | 독립 데모, 제스처 상호작용, 빠른 시작 |

## 소프트웨어 생태계

- **웹 제어**: 브라우저 슬라이더, 프리셋 포즈 19개, MediaPipe 카메라 텔레오퍼레이션, SCS0009 / PWM 드라이버 전환 지원.
- **데스크톱 제어 프로그램**: SCS0009는 `AmazingHandControl`(Tkinter GUI + CLI)을 사용하고, PWM은 `AmazingHand-PWM/tools/hand_gui.py`를 사용합니다.
- **손 추적**: SCS0009는 공식 dora + MuJoCo IK Demo를 제공하고, PWM은 GUI 내장 MediaPipe 추적을 제공합니다.
- **오픈 소스 리소스**: CAD, 조립/프린팅 문서, Arduino/Python 예제가 모두 저장소에 있습니다.

## 오픈 소스 리소스

- [조립 가이드 PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [3D 프린팅 권장 사항 PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand 개요 PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)
- [CAD / STL / STEP](../../../AmazingHand-main/cad/)
- [공식 업스트림 프로젝트(Pollen Robotics)](https://github.com/pollen-robotics/AmazingHand)

## 다음 단계

- [버전 비교와 선택](version-comparison.md)
- [하드웨어 개요](../01-hardware/overview.md)
- [SCS0009 빠른 시작](../02-quick-start/scs0009.md)
- [PWM 빠른 시작](../02-quick-start/pwm.md)
