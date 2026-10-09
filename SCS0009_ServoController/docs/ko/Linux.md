[English](../en/Linux.md) | [Deutsch](../de/Linux.md) | [Español](../es/Linux.md) | [Français](../fr/Linux.md) | [Italiano](../it/Linux.md) | [日本語](../ja/Linux.md) | 한국어 | [Português (BR)](../pt-br/Linux.md) | [Português (PT)](../pt-pt/Linux.md) | [简体中文](../zh-hans/Linux.md) | [繁體中文](../zh-hant/Linux.md)

# SCS0009 서보 디버그 도구 — Linux 가이드

Ubuntu / Debian / 기타 주요 배포판용. 핵심 사항: 시리얼 권한(dialout), USB-시리얼 장치 감지.

> ⚠️ **호환성: 이 도구는 현재 Feetech SCS0009 서보(SCS 시리즈, 포텐셔미터 위치 피드백, 10비트 분해능 0-1023)만 지원합니다**. 레지스터 테이블과 xdat 형식은 Feetech SCS0009용으로 설계되었으며, 다른 브랜드/모델은 보장되지 않습니다.

---

## 1. 요구 사항

| 의존성 | 버전 |
|-----------|---------|
| Python | >= 3.8 (3.10+ 권장) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| OS | Ubuntu 20.04+ / Debian 11+ |

중국어 폰트(중국어 UI에 필요):

```bash
sudo apt install fonts-noto-cjk
```

이모지 아이콘 폰트(로그의 ✅⚠️ 등에 사용):

```bash
sudo apt install fonts-noto-color-emoji
```

## 2. Python 의존성 설치

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **가상 환경은 한 번만 생성하십시오**. 다시 실행하면 환경이 초기화/덮어쓰기됩니다(설치된 의존성이 지워집니다). 이후에는 `source .venv/bin/activate`만 하면 됩니다.

> pip가 "externally-managed-environment"를 보고하면, venv를 사용하거나 `pip install --break-system-packages -r requirements.txt`를 실행하십시오.

## 3. ⚠️ 시리얼 권한(dialout) [필수]

기본적으로 일반 사용자는 `/dev/ttyUSB*` / `/dev/ttyACM*`에 **접근할 수 없습니다**. 사용자를 `dialout` 그룹에 추가하십시오:

```bash
sudo usermod -a -G dialout $USER
```

**로그아웃 후 다시 로그인**하십시오(또는 재부팅). 확인:

```bash
groups
# output should include dialout
```

> 일부 배포판은 `uucp`(Arch) 또는 `tty`를 사용합니다.

## 4. USB 시리얼 장치 식별

연결 후:

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

일반적인 출력:

```
/dev/ttyUSB0   # CH340 / CP2102 / PL2303
/dev/ttyACM0   # native USB serial (Arduino/ESP32 onboard)
```

## 5. 환경 확인

```bash
python setup.py
```

## 6. GUI 실행

```bash
python -m src.gui.factory_calibration_tool
```

포트 지정:

```bash
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

> 포트가 하나만 존재하면 도구가 이를 직접 사용합니다.

## 7. 인터페이스 워크플로

> 단일 패널 레이아웃. 창이 너무 낮으면 스크롤 바가 자동으로 나타나며, 최대화하면 화면에 맞게 늘어납니다.

### 7.1 시리얼 연결
포트와 보레이트(기본 1M)를 선택하고 **Connect**를 클릭합니다.

### 7.2 서보 스캔
**Scan Servos**를 클릭합니다(ID 1-254); 목록 행을 클릭하면 드롭다운이 자동으로 채워집니다.

### 7.3 파라미터 읽기/쓰기
- 44개 레지스터(EEPROM + SRAM)를 모두 읽으며, 행을 선택하면 주소/길이/값이 자동으로 채워집니다
- 자동 잠금 해제/쓰기/잠금으로 쓰기; 성공/실패 팝업 표시

### 7.4 위치 제어
슬라이더(0-1023)를 드래그하거나 값을 입력합니다; 이동 완료 시 토크를 끄라는 프롬프트가 표시됩니다.

### 7.5 보레이트 / 공장 초기화
보레이트 변경(실패 시 자동 롤백), 공장 초기화.

### 7.6 xdat 파라미터(EEPROM만)
현재 서보 저장 → 백업 열기 → 서보로 복원.

## 8. 문제 해결

| 문제 | 해결책 |
|---------|----------|
| **Permission denied: /dev/ttyUSB0** | dialout 그룹에 없습니다. 섹션 3을 참조하거나 `sudo chmod 666 /dev/ttyUSB0`(임시) |
| 시리얼 포트 없음 | `ls /dev/ttyUSB* /dev/ttyACM*`; `lsusb`로 장치 확인 |
| 장치 이름이 바뀜 | ttyUSB 번호는 연결 순서에 따라 달라집니다. udev 규칙을 사용하거나 실행할 때마다 선택하십시오 |
| 중국어 UI가 비어 있음 | `fonts-noto-cjk` 설치 |
| 이모지가 네모로 표시됨 | `fonts-noto-color-emoji` 설치 |
| pip install 실패 | venv 사용; 또는 `--break-system-packages` |
| 앱이 시작되지 않음 | `python3 --version` 확인; 의존성은 `pip list`로 확인 |

## 9. 명령줄(선택)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/ttyUSB0
```

## 10. 고급: udev 고정 장치 이름(선택)

USB ID로 장치 이름을 고정하려면 `/etc/udev/rules.d/99-servo.rules`를 생성하십시오:

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyServo"
```

그런 다음 `ls -l /dev/ttyServo`. 벤더 ID는 `lsusb`로 확인합니다.
