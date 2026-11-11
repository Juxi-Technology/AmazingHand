---
title: "PWM 데스크톱 제어 프로그램(Tkinter GUI)"
description: "AmazingHand PWM 서보 버전 데스크톱 제어: 소스 실행, GUI 제스처/차동/직접 구동, 내장 MediaPipe 추적, 명령줄 테스트와 패키징."
version: pwm
---

# PWM 데스크톱 제어 프로그램(Tkinter GUI)

> 아래 명령은 저장소의 `AmazingHand-PWM/` 디렉터리에서 실행합니다.

이 페이지는 **PWM 서보 버전**의 데스크톱 제어 튜토리얼입니다. 웹 제어는 [PWM 웹 제어](../03-web-control/pwm.md), 배선은 [PWM 배선](../01-hardware/pwm.md), 펌웨어 플래싱은 [PWM 빠른 시작](../02-quick-start/pwm.md)을 참고하세요.

> 적용: ESP32-S3 + PWM 서보 8채널(차동 구동). 펌웨어 플래싱은 [PWM 빠른 시작](../02-quick-start/pwm.md), 프로토콜과 명령은 [PWM 프로토콜과 캘리브레이션](../06-servo-tuning/pwm.md)을 참고하세요.

## 1. 실행 방식

| 방식 | 필요 | 적합 |
|------|------|------|
| **소스 실행**(권장) | 64비트 Python 3.12 + pyserial | 모든 기능, 손 추적 포함 |
| 직접 exe 패키징 | PyInstaller | Python 설치 없이 배포(7절 참고) |

## 2. 소스 실행

### 의존성 설치

모듈 루트 디렉터리(`AmazingHand-PWM/`)에서 실행하세요:

```bash
# 기본 의존성(pyserial)
pip install -r tools/requirements.txt

# 손 추적이 필요할 때 실행(자동으로 tools/tracking_env를 만들고 mediapipe 설치)
tools/setup_tracking.bat
```

> mediapipe 0.10.14는 64비트 Windows wheel만 제공하므로 반드시 **64비트 Python 3.12**를 사용해야 합니다.

### GUI 실행

```bash
# pyserial이 있는 아무 Python
python tools/hand_gui.py

# 또는 추적 환경 사용(mediapipe 포함)
tools/tracking_env/Scripts/python tools/hand_gui.py
```

![제어 프로그램 메인 화면: 시리얼 포트 바, 제스처 명령, 서보 직접 구동과 손가락 차동 제어](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-main.png)

### GUI 사용

1. **시리얼 포트 선택**: 상단 드롭다운에서 ESP32의 COM 포트를 선택합니다(장치 관리자에서 확인).
2. **"연결" 클릭**: 상태등이 녹색으로 바뀌고 로그에 "已连接"이 표시되며 NOP 링크 테스트를 자동 전송합니다.
3. **제스처 명령**: "주먹 / 가위 / 보 / 엄지 척 / OK / 집기 / 가리키기 / 펼치기 / 주먹 쥐기"를 누르면 로봇 손이 실행합니다.
4. **왼손/오른손**: "오른손"/"왼손"을 체크해 전환합니다(엄지 미러 방향이 다름).
5. **서보 직접 구동**: 슬라이더 8개를 드래그해 개별 서보 각도를 실시간 제어합니다(0–180°).
6. **손가락 차동 제어**: 손가락마다 진행 바 두 개 —
   - **굽힘◀▶펴기**: 손가락을 굽히거나 폅니다(범위 -70 ~ +70).
   - **오른쪽 벌림◀▶왼쪽 벌림**: 손가락을 좌우로 벌립니다(범위 60 ~ 120, 90=중립).

   > 이 두 진행 바는 **제어축**이며 두 서보가 아닙니다. 프로그램이 이들을 해당 손가락 두 서보의 각도로 합성합니다: 같은 방향 성분은 벌림, 반대 방향 성분은 굴곡/신전을 만듭니다.

7. **반복 / 정지**: 마지막 제스처 반복 / 즉시 중단.
8. **통신 로그**: 하단에 송수신 프레임과 응답을 실시간 표시합니다.

![손가락 차동 제어 패널: 손가락마다 굽힘/펴기와 좌우 벌림](../../assets/robot-arms/amazing-hand/pwm-debugging/gui-differential.png)

### GUI 내장 손 추적

GUI에는 손 추적 패널이 내장되어 있습니다(카메라가 손 동작을 따라감):

1. 시리얼 포트를 연결한 뒤 "손 추적(MediaPipe 카메라)" 패널로 스크롤합니다.
2. 카메라 번호를 선택하고(기본 0) **"추적 시작"**을 누릅니다.
3. 손을 카메라 화면에 넣으면 로봇 손이 굽힘/펴기를 따라갑니다.

> 추적에는 `tools/setup_tracking.bat`로 mediapipe를 설치해야 하며, 소스 방식으로 시작한 GUI에만 추적 기능이 있습니다.

## 3. 명령줄 테스트(tools/serial_test.py)

모듈 루트 디렉터리에서 실행하세요:

```bash
# 링크 테스트(먼저 통신 확인)
python tools/serial_test.py COM3 nop

# 제스처
python tools/serial_test.py COM3 rock         # 주먹
python tools/serial_test.py COM3 thumbs_up    # 엄지 척
python tools/serial_test.py COM3 index        # 가리키기
python tools/serial_test.py COM3 open         # 펼치기
python tools/serial_test.py COM3 close        # 주먹 쥐기

# 단일 서보 직접 구동
python tools/serial_test.py COM3 servo 1 90   # 서보1 → 90°

# 전체 중간 위치
python tools/serial_test.py COM3 mid

# 왼손/오른손 설정
python tools/serial_test.py COM3 hand L
python tools/serial_test.py COM3 hand R

# 스윕/자체 점검
python tools/serial_test.py COM3 sweep 1      # 서보1 스윕
python tools/serial_test.py COM3 test         # 모든 서보 개별 테스트
```

## 4. 시리얼 도구 수동 테스트(선택)

제어 프로그램 없이 시리얼 도구로 16진수 프레임을 직접 보내 링크를 검증할 수도 있습니다.

**CoolTerm**(Windows / macOS / Linux):

1. `Options` → 보드레이트 **115200**, 8N1.
2. `Connection` → `Send String` → `Hex` 선택.
3. `AA 01 00 01`(주먹)을 보내면 응답 영역에 `BB 01 00 01`(ACK)과 `BB 01 10 11`(완료)이 나타나야 합니다.

**Linux / macOS 명령줄**:

```bash
# Linux
stty -F /dev/ttyUSB0 115200
printf '\xAA\x01\x00\x01' > /dev/ttyUSB0

# macOS
stty -f /dev/cu.usbserial-0001 115200
printf '\xAA\x01\x00\x01' > /dev/cu.usbserial-0001
```

프레임 형식, 체크섬과 전체 명령은 [PWM 프로토콜과 캘리브레이션](../06-servo-tuning/pwm.md)을 참고하세요.

## 5. Python 제어 스크립트(사용자 정의 개발)

```python
import time
import serial

PORT, BAUD = "COM3", 115200          # Linux/macOS에서는 /dev/ttyUSB0, /dev/cu.usbserial-*로 변경

def frame(cmd, data=b""):
    checksum = cmd ^ len(data)
    for byte in data:
        checksum ^= byte
    return bytes([0xAA, cmd, len(data)]) + data + bytes([checksum & 0xFF])

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(1)                        # ESP32 리셋 완료 대기

ser.write(frame(0x00))               # NOP 링크 테스트
ser.write(frame(0x01))               # 주먹
time.sleep(0.5)
ser.write(frame(0xF0, bytes([90] * 8)))  # 서보 8채널 모두 90°
ser.close()
```

응답 프레임은 `BB CMD STATUS CKSUM`이며, `STATUS=0x00`은 수락됨, `0x10`은 제스처 완료를 의미합니다. 전체 명령 표와 직접 구동/왼손·오른손 예시는 [PWM 프로토콜과 캘리브레이션](../06-servo-tuning/pwm.md)을 참고하세요.

## 6. 자주 묻는 질문

| 현상 | 처리 |
|------|------|
| 서보가 움직이지 않음 | 전원(5V 3A 독립 전원), COM 포트, 배선 확인 |
| 무응답 / 시리얼 포트를 연 뒤 서보가 함부로 움직임 | 보드레이트 115200 확인; GUI는 연결 시 먼저 NOP 핸드셰이크를 보냄 |
| 카메라 화면이 나오지 않음 | 카메라 권한 허용(설정→개인정보→카메라) |
| 손 모양이 반대 | 반대쪽 왼손/오른손을 체크 |
| 추적이 반응하지 않음 | `tools\tracking_env`의 Python으로 시작했는지, mediapipe 설치가 성공했는지 확인 |

## 7. 직접 exe 패키징(선택)

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole --name "AmazingHand控制台" tools/hand_gui.py
```

패키징 버전에는 손 추적이 포함되지 않습니다(mediapipe 리소스가 큼); 추적이 필요하면 소스 방식을 사용하세요.

> 전체 프로토콜과 명령 설명은 [PWM 프로토콜과 캘리브레이션](../06-servo-tuning/pwm.md)을 참고하세요.
