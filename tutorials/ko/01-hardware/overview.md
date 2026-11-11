---
title: "하드웨어 개요: 구조, CAD와 조립"
description: "AmazingHand 기계 구조, CAD/STL/STEP, 조립과 3D 프린팅 리소스."
version: both
---

# 하드웨어 개요

두 서보 방식은 동일한 로봇 손 구조를 공유하며, 차이는 서보 모델, 드라이버 보드, 배선에 있습니다. 로봇 손을 조립하기 전에 선택한 버전을 먼저 확인하세요.

## 기계 구조

- 손가락 4개, 손가락마다 자유도 2개: 굴곡/신전(flexion/extension) + 벌림/모음(abduction/adduction).
- 손가락마다 서보 2개가 병렬 기구로 차동 구동하며, 모든 서보가 손에 장착됩니다.
- 3D 프린팅 외형, 링크, 연성 관절; 전체 손 무게는 약 400 g.
- 원본 손목 인터페이스는 Reachy 2의 Orbita 3D에 맞춰져 있으며, 다른 로봇 팔로도 직접 연결할 수 있습니다.

## CAD와 모델

- STL / STEP 파일: [`AmazingHand-main/cad/`](../../../AmazingHand-main/cad/)
- Onshape 온라인 문서와 URDF: [`AmazingHand-main/README_CN.md`](../../../AmazingHand-main/README_CN.md)의 CAD 장을 참고하세요.

## 조립과 3D 프린팅

- [조립 가이드 PDF](../../../AmazingHand-main/docs/AmazingHand_Assembly.pdf)
- [3D 프린팅 권장 사항 PDF](../../../AmazingHand-main/docs/AmazingHand_3DprintingTips.pdf)
- [AmazingHand 개요 PDF](../../../AmazingHand-main/docs/AmazingHand_Overview.pdf)

> 조립 전에 로봇 손을 중간 위치에 두고 서보 혼을 중간 위치 기준으로 장착하세요; 두 서보의 서보 혼/스플라인과 스트로크가 달라 혼용할 수 없습니다.

## 두 하드웨어 배선

| 버전 | 배선과 전원 공급 가이드 |
|------|----------------|
| SCS0009 시리얼 버스 | [SCS0009 배선, ID와 전원 공급](scs0009.md) |
| PWM(ESP32-S3) | [PWM 배선, GPIO와 전원 공급](pwm.md) |
| 카메라 키트 | [카메라 키트 설치](camera-kit.md) |

## 다음 단계

- [버전 비교와 선택](../00-product/version-comparison.md)
- [빠른 시작: SCS0009](../02-quick-start/scs0009.md) · [빠른 시작: PWM](../02-quick-start/pwm.md)
