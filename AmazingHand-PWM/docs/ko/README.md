# AmazingHand PWM 서보 에디션 — 빠른 시작

**ESP32-S3와 PWM 서보 8개**로 AmazingHand를 구동합니다. 전체 매뉴얼은 이 `docs/` 폴더에 있습니다.

## 하드웨어

| 항목 | 모델 |
|------|------|
| 메인 컨트롤러 | ESP32-S3 개발 보드(YX-ESP32-S3 또는 동급) |
| 서보 | PWM 서보 8개 — 펌웨어는 **PTK 7452 MG-D 디지털 서보(333 Hz)** 기준으로 캘리브레이션됨 |
| 어댑터 보드 | PWM 서보 어댑터 보드 |
| 전원 | 5 V / 3 A, ESP32와 공통 접지 |

> SG90 같은 50 Hz 아날로그 서보는 333 Hz 펌웨어를 **그대로 대체할 수 없습니다**.

| 채널 | GPIO | 관절 | 채널 | GPIO | 관절 |
|---------|------|-------|---------|------|-------|
| PWM1 | 4 | 검지 1 | PWM5 | 15 | 약지 1 |
| PWM2 | 5 | 검지 2 | PWM6 | 16 | 약지 2 |
| PWM3 | 6 | 중지 1 | PWM7 | 17 | 엄지 1 |
| PWM4 | 7 | 중지 2 | PWM8 | 18 | 엄지 2 |

## 1. 펌웨어 플래싱

ESP-IDF 사용 시:

```bash
cd firmware/AmazingHand_Serial
idf.py set-target esp32s3
idf.py build
idf.py -p COM3 flash monitor
```

사전 빌드된 이미지와 `esptool` 사용 시:

```bash
python -m esptool --chip esp32s3 -p COM3 -b 460800 write_flash 0x0 \
  firmware/prebuilt/amazinghand_pwm.bin
```

시리얼 포트는 **115200-8N1**로 동작하며, 시작 시 배너를 출력합니다.

## 2. 핸드 제어

데스크톱 GUI:

```bash
pip install -r tools/requirements.txt
python tools/hand_gui.py
```

카메라 트래킹에는 `tools/setup_tracking.bat`으로 만드는 추가 환경이 필요합니다. 그런 다음:

```bash
tools/tracking_env/Scripts/python tools/hand_gui.py
```

웹 제어: 저장소의 `Amazinghand-web-io/` 페이지를 열고(또는 `Amazinghand-web/server.py --driver pwm` 실행), 드라이버에서 **PWM (ESP32-S3)** 을 선택한 뒤 ESP32 시리얼 포트를 골라 연결합니다.

## 3. 전체 문서

| 문서 | 내용 |
|----------|----------|
| [`../en/user_manual.md`](../en/user_manual.md) / [`../zh-hans/用户手册.md`](../zh-hans/用户手册.md) | 프로토콜, 명령 레퍼런스, 배선, 캘리브레이션, FAQ |
| [`../en/full_workflow.md`](../en/full_workflow.md) / [`../zh-hans/全流程使用教程.md`](../zh-hans/全流程使用教程.md) | 엔드투엔드 워크플로 |
| [`../en/gui_usage.md`](../en/gui_usage.md) / [`../zh-hans/使用教程.md`](../zh-hans/使用教程.md) | GUI 및 시리얼 테스트 도구 |
| [`../en/hand_tracking.md`](../en/hand_tracking.md) / [`../zh-hans/手势追踪教程.md`](../zh-hans/手势追踪教程.md) | MediaPipe 핸드 트래킹 |

## 4. 자주 발생하는 문제

- **무응답**: 보드레이트가 115200인지, ESP32의 COM 포트, 5 V / 3 A 전원, 공통 접지를 확인하세요. 페이지는 NOP 핸드셰이크를 자동으로 재시도합니다.
- **서보가 움직이지 않음 / 떨림**: 서보가 333 Hz 디지털 서보인지, 전원 공급이 충분한지 확인하세요.
- **방향이 반대**: `Amazinghand-web-io/config.json`의 `pwm.calibration`에서 해당 손가락의 `scale`을 `-1`로 설정하세요.
- **중간 위치가 어긋남**: 해당 채널의 `offset_deg`를 조정하세요.
- **바쁨 상태**: 펌웨어가 내장 제스처를 실행 중입니다. 기다리거나 정지 명령(`0xFF`)을 보내세요.
