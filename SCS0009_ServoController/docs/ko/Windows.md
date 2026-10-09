[English](../en/Windows.md) | [Deutsch](../de/Windows.md) | [Español](../es/Windows.md) | [Français](../fr/Windows.md) | [Italiano](../it/Windows.md) | [日本語](../ja/Windows.md) | 한국어 | [Português (BR)](../pt-br/Windows.md) | [Português (PT)](../pt-pt/Windows.md) | [简体中文](../zh-hans/Windows.md) | [繁體中文](../zh-hant/Windows.md)

# SCS0009 서보 디버그 도구 — Windows 가이드

Windows 10 / 11용. 설치부터 완전한 서보 디버깅까지 다룹니다.

> ⚠️ **호환성: 이 도구는 현재 Feetech SCS0009 서보(SCS 시리즈, 포텐셔미터 위치 피드백, 10비트 분해능 0-1023)만 지원합니다**. 레지스터 테이블과 xdat 형식은 Feetech SCS0009용으로 설계되었으며, 다른 브랜드/모델은 보장되지 않습니다.

---

## 1. 요구 사항

| 의존성 | 버전 | 비고 |
|-----------|---------|-------|
| Python | >= 3.8 | 3.10+ 권장, [python.org](https://www.python.org/downloads/)에서 다운로드 |
| PySide6 | >= 6.0 | GUI 프레임워크 |
| pyserial | >= 3.5 | 시리얼 통신 |
| OS | Win10 / Win11 | 모든 에디션 |

## 2. Python 설치

1. <https://www.python.org/downloads/> 방문
2. Python 3.10+ 설치 프로그램 다운로드
3. 설치 중 **"Add Python to PATH"를 체크**하십시오(그렇지 않으면 터미널에서 python을 찾을 수 없습니다)

확인:

```bash
python --version
```

## 3. 의존성 설치

시스템 Python을 오염시키지 않도록 가상 환경에 설치합니다:

```bash
cd SCS0009_ServoController
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> ⚠️ **가상 환경은 한 번만 생성하십시오**. 다시 실행하면 환경이 초기화/덮어쓰기됩니다(설치된 의존성이 지워집니다). 이후에는 매번 `activate`만 하면 됩니다.

> 활성화 후 프롬프트에 `(.venv)`가 표시됩니다.

## 4. 환경 확인

```bash
python setup.py
```

`[OK] 环境检查通过，可以运行项目`는 환경이 준비되었음을 의미합니다.

## 5. 하드웨어 연결

1. USB-시리얼 어댑터(CH340 / CP2102)를 꽂습니다
2. 서보 컨트롤러(로봇 암 제어 보드)를 연결합니다
3. 서보에 전원을 공급합니다(DC 5V 5A 표준, DC 12V 5A Pro)

장치 관리자에서 COM 포트를 확인합니다(`Win+X` → 장치 관리자):

```
Ports (COM & LPT)
  └─ USB-SERIAL CH340 (COM3)     ← your servo port
```

> 시작할 때 선택할 수 있도록 **COM 번호를 기록해 두십시오**.

## 6. GUI 실행

```bash
python -m src.gui.factory_calibration_tool
```

또는 포트를 지정:

```bash
python -m src.gui.factory_calibration_tool --port COM3
```

사용 가능한 포트 나열:

```bash
python -m src.gui.factory_calibration_tool --list-ports
```

## 7. 인터페이스 워크플로

> 단일 패널 레이아웃. 창이 너무 낮으면 스크롤 바가 자동으로 나타나며, 최대화하면 화면에 맞게 늘어납니다.

### 7.1 시리얼 연결

- 포트와 보레이트(기본 1M)를 선택하고 **Connect**를 클릭
- 상태에 `🟢 Connected` 표시

### 7.2 서보 스캔

- **Scan Servos**를 클릭하여 온라인 서보 감지(ID 1-254)
- 결과는 서보 목록에 실시간으로 표시됩니다(모델 포함)
- 목록의 행을 클릭 → 서보 드롭다운 자동 채움

### 7.3 파라미터 읽기/쓰기

- **Read Params**: 44개 레지스터(EEPROM + SRAM)를 모두 읽고, 로그에 결과가 실시간으로 표시됩니다
- **Parameter Table**: 5개 열(Address/Register/Value/Memory/Access), EEPROM/SRAM/DEFAULT로 색상 구분
- **Row Select Linkage**: 행을 클릭 → "Write Address", "Length", "Value" 자동 채움
- **Write**: 값을 수정한 후 write를 클릭; 도구가 EEPROM을 자동으로 잠금 해제/쓰기/잠금합니다
- **Write Result Popup**: 성공 시 녹색 "✅ Written successfully", 실패 시 빨간색 "❌ Write failed"(이유 포함)

### 7.4 위치 제어

- **Slider**: 드래그하여 목표 위치 조정(0-1023), 값 상자가 실시간 갱신
- **Value box**: 목표 위치를 직접 입력하면 슬라이더가 따라옵니다
- 이동 후 상태에 "move complete, please turn off torque" 표시

### 7.5 보레이트 / 공장 초기화

- **Change Baud Rate**: 38400-1000000 bps 선택, 실패 시 자동 롤백
- **Factory Reset**: 공장 기본값(ID=1, baud=1M)으로 복원, 재스캔 필요

### 7.6 xdat 파라미터(EEPROM만)

1. `💾 Save Current Servo`: 현재 서보 EEPROM 파라미터를 xdat 파일로 저장(백업)
2. `📂 Open xdat`: 백업 파일 로드
3. `📤 Restore to Servo`: 백업을 서보로 다시 기록

## 8. 문제 해결

| 문제 | 해결책 |
|---------|----------|
| 시리얼 포트 없음 | 장치 관리자에서 드라이버 확인; 다른 USB 포트 시도; CH340 드라이버 설치 |
| 포트가 사용 중 | 시리얼 모니터 닫기; 도구 재시작 |
| 중국어 텍스트가 비어 있음 | 시스템에 Microsoft YaHei가 있습니다. 깨지면 CJK 폰트 설치 |
| 서보를 찾을 수 없음 | 전원/배선 확인; 1M 보레이트 확인 |
| 쓰기 실패 | 서보 전원과 연결 확인; 레지스터가 쓰기 가능한지 확인 |
| 포트 열 때 PermissionError | 다른 프로세스가 COM 포트를 점유하지 않았는지 확인 |

## 9. 명령줄(선택)

```bash
# List available ports
python -m src.gui.factory_calibration_tool --list-ports

# Launch with specified port
python -m src.gui.factory_calibration_tool --port COM3
```
