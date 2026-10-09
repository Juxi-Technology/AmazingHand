[English](../en/macOS.md) | [Deutsch](../de/macOS.md) | [Español](../es/macOS.md) | [Français](../fr/macOS.md) | [Italiano](../it/macOS.md) | [日本語](../ja/macOS.md) | 한국어 | [Português (BR)](../pt-br/macOS.md) | [Português (PT)](../pt-pt/macOS.md) | [简体中文](../zh-hans/macOS.md) | [繁體中文](../zh-hant/macOS.md)

# SCS0009 서보 디버그 도구 — macOS 가이드

macOS 11(Big Sur) 이상용. 핵심 사항: 시리얼 이름 규칙(`cu.*` vs `tty.*`), USB 드라이버.

> ⚠️ **호환성: 이 도구는 현재 Feetech SCS0009 서보(SCS 시리즈, 포텐셔미터 위치 피드백, 10비트 분해능 0-1023)만 지원합니다**. 레지스터 테이블과 xdat 형식은 Feetech SCS0009용으로 설계되었으며, 다른 브랜드/모델은 보장되지 않습니다.

---

## 1. 요구 사항

| 의존성 | 버전 |
|-----------|---------|
| Python | >= 3.8 (3.10+ 권장, Homebrew 경유) |
| PySide6 | >= 6.0 |
| pyserial | >= 3.5 |
| OS | macOS 11+ (Apple Silicon / Intel) |

## 2. Python 설치

Homebrew를 통한 설치를 권장합니다:

```bash
# Install Homebrew if missing
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

확인:

```bash
python3 --version
```

## 3. 의존성 설치

```bash
cd SCS0009_ServoController
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ **가상 환경은 한 번만 생성하십시오**. 다시 실행하면 환경이 초기화/덮어쓰기됩니다(설치된 의존성이 지워집니다). 이후에는 `source .venv/bin/activate`만 하면 됩니다.

## 4. ⚠️ macOS 시리얼 이름 규칙 [중요]

macOS는 USB 시리얼 장치를 `/dev` 아래에 **두 가지 이름 규칙**으로 배치합니다:

| 접두사 | 의미 | 사용 가능 |
|--------|---------|--------|
| `/dev/tty.usbserial-*` | 모뎀 스타일(블로킹) | 멈출 수 있음, 권장하지 않음 |
| `/dev/cu.usbserial-*` | call/terminal 스타일(**논블로킹**) | ✅ 권장 |

**포트 찾기:**

```bash
ls /dev/cu.*
```

일반적인 출력:

```
/dev/cu.usbserial-0001      # CP2102 / FTDI
/dev/cu.usbmodem141101      # onboard USB serial (Arduino/ESP32)
/dev/cu.wchusbserial1420    # CH340
```

> 도구는 `cu.*` 장치를 자동으로 우선합니다. 포트를 수동으로 지정할 때는 `tty.`가 아니라 `cu.`를 사용하십시오.

## 5. USB 드라이버

대부분의 일반적인 칩(CH340, CP2102, FTDI)에는 macOS용 드라이버가 내장되어 있습니다. 장치가 인식되지 않으면:

```bash
system_profiler SPUSBDataType | grep -A5 -i "serial\|CH340\|CP210"
```

- **CH340**: 오래된 배치는 WCH 공식 드라이버가 필요합니다
- 일반적으로 `ls /dev/cu.*`에 장치가 표시되면 충분합니다

## 6. 환경 확인

```bash
python setup.py
```

## 7. GUI 실행

```bash
python -m src.gui.factory_calibration_tool
```

포트 지정:

```bash
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 8. 인터페이스 워크플로

> 단일 패널 레이아웃. 창이 너무 낮으면 스크롤 바가 자동으로 나타나며, 최대화하면 화면에 맞게 늘어납니다.

### 8.1 시리얼 연결
포트와 보레이트(기본 1M)를 선택하고 **Connect**를 클릭합니다.

### 8.2 서보 스캔
**Scan Servos**를 클릭합니다(ID 1-254); 목록 행을 클릭하면 드롭다운이 자동으로 채워집니다.

### 8.3 파라미터 읽기/쓰기
- 44개 레지스터를 모두 읽으며, 행을 선택하면 주소/길이/값이 자동으로 채워집니다
- 자동 잠금 해제/쓰기/잠금으로 쓰기; 성공/실패 팝업 표시

### 8.4 위치 제어
슬라이더(0-1023)를 드래그하거나 값을 입력합니다; 이동 완료 시 토크를 끄라는 프롬프트가 표시됩니다.

### 8.5 보레이트 / 공장 초기화
보레이트 변경(실패 시 자동 롤백), 공장 초기화.

### 8.6 xdat 파라미터(EEPROM만)
현재 서보 저장 → 백업 열기 → 서보로 복원.

## 9. 문제 해결

| 문제 | 해결책 |
|---------|----------|
| `tty.` 포트가 멈춤 | 대신 `cu.` 접두사 사용 |
| 장치를 찾을 수 없음 | `ls /dev/cu.*`; 다시 연결; `system_profiler SPUSBDataType` |
| 중국어 UI가 비어 있음 | 보통 시스템 PingFang이면 충분합니다. 깨지면 Noto Sans CJK 설치 |
| 권한 문제 | macOS는 보통 추가 권한이 필요하지 않습니다. 요청되면 터미널 접근을 허용하십시오 |
| venv 활성화 실패 | `source .venv/bin/activate`(`.bat` 아님) |
| Apple Silicon 빌드 오류 | Python 3.10+는 네이티브입니다. Rosetta의 오래된 Python은 피하십시오 |

## 10. 명령줄(선택)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port /dev/cu.usbserial-0001
```

## 11. 팁

- **포트 이름 변경**: `cu.*` 이름은 USB 포트에 따라 달라질 수 있습니다. 실행할 때마다 드롭다운에서 선택하십시오
- **슬립**: macOS가 슬립하여 시리얼 연결이 끊길 수 있습니다. 조작 중에는 슬립되지 않게 하십시오
- **개인정보 권한**: "이동식 디스크 접근"을 요청하면 허용하십시오
