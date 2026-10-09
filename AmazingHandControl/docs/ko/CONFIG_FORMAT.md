[English](../en/CONFIG_FORMAT.md) | [Deutsch](../de/CONFIG_FORMAT.md) | [Español](../es/CONFIG_FORMAT.md) | [Français](../fr/CONFIG_FORMAT.md) | [Italiano](../it/CONFIG_FORMAT.md) | [日本語](../ja/CONFIG_FORMAT.md) | 한국어 | [Português (BR)](../pt-br/CONFIG_FORMAT.md) | [Português (PT)](../pt-pt/CONFIG_FORMAT.md) | [简体中文](../zh-hans/CONFIG_FORMAT.md) | [繁體中文](../zh-hant/CONFIG_FORMAT.md)

# 손 설정 형식(YAML)

이 문서는 AmazingHand에서 사용하는 YAML 설정 파일을 설명합니다.

| 파일 | 용도 |
|------|---------|
| `data/hand_config.yaml` | 포즈와 시퀀스(GUI와 CLI가 생성/편집) |
| `data/config.yaml` | 애플리케이션 설정(시리얼 포트, 서보 한계, 속도, 경로) |

---

## `data/config.yaml` – 애플리케이션 설정

GUI가 시작 시 로드합니다. 파일이 없으면 내장 기본값이 사용됩니다.
CLI도 동일한 기본값을 사용합니다(`--port` / `--baudrate`로 재정의 가능).

### 전체 구조

```yaml
# Serial port settings
serial:
  port_windows: COM9          # Default port on Windows
  port_linux: /dev/ttyACM0   # Default port on Linux/macOS
  baudrate: 1000000           # Default baud rate
  baudrate_options: [9600, 115200, 1000000]  # Shown in GUI dropdown

# Servo assignments — [servo1_id, servo2_id] per finger
# servo1 (odd ID)  = position axis (open/close)
# servo2 (even ID) = side axis (left/right)
servos:
  ring:    [1, 2]
  middle:  [3, 4]
  pointer: [5, 6]
  thumb:   [7, 8]
  all_ids: [1, 2, 3, 4, 5, 6, 7, 8]

# Servo angle limits (degrees)
limits:
  servo_min: -40   # Absolute minimum for any servo command
  servo_max: 110   # Absolute maximum for any servo command
  base_min: 0      # Open/close slider minimum
  base_max: 110    # Open/close slider maximum
  side_min: -40    # Left/right slider minimum
  side_max: 40     # Left/right slider maximum

# Movement speeds (1–6 scale, where 6 is fastest)
speeds:
  default: 3
  min: 1
  max: 6

# Auto-mode blending extremes — [servo1_deg, servo2_deg]
# Used to interpolate combined position+side values in Auto mode
auto_extremes:
  left_open:    [32, -40]
  right_open:   [-40, 32]
  left_closed:  [110, 110]
  right_closed: [110, 110]
  center_open:  [0, 0]
  center_closed: [110, 110]

# File paths (relative to project root)
paths:
  poses_sequences_file: data/hand_config.yaml
```

### 참고
- 모든 키는 선택 사항입니다 — 누락된 키는 위에 표시된 내장 기본값으로 대체됩니다.
- 여기에 포즈나 시퀀스를 저장하지 **마십시오**; 그것들은 `data/hand_config.yaml`에 속합니다.
- 이 파일을 편집한 후 변경 사항을 적용하려면 GUI를 재시작하십시오.

---

## `data/hand_config.yaml` – 포즈 및 시퀀스

GUI와 CLI가 생성하고 편집합니다. 두 도구가 공유합니다.

### YAML 구조

```yaml
poses:
  <pose_name>:
    positions: [pos1, pos2, pos3, pos4, pos5, pos6, pos7, pos8]

sequences:
  <sequence_name>:
    steps:
      - "<pose_name>:speed1,speed2,...,speed8|delay"
      - "SLEEP:duration"
```

## 포즈

각 포즈는 8개의 서보 값으로 완전한 손 위치를 정의합니다.

### 형식
```yaml
poses:
  pose_name:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
```

### 위치 배열
- **8개 값**으로 서보 위치를 도(degree) 단위로 나타냅니다
- **서보 매핑**:
  - 서보 1: 검지 위치(0=열림, 110=닫힘)
  - 서보 2: 검지 측방(-20=왼쪽, 0=중앙, +20=오른쪽)
  - 서보 3: 중지 위치
  - 서보 4: 중지 측방
  - 서보 5: 약지 위치
  - 서보 6: 약지 측방
  - 서보 7: 엄지 위치
  - 서보 8: 엄지 측방

- **닫기/열기 슬라이더 범위**: 손가락당 0-110°(0=열림, 110=닫힘)
- **측방 슬라이더 범위**: -40°(왼쪽) ~ +40°(오른쪽)
- **저장되는 서보 값**: YAML은 결합 값(base ± side)을 저장하므로 실제 서보 명령은 대략 -40°에서 150° 사이가 될 것으로 예상하십시오
- **참고**: 짝수 번호 서보(2,4,6,8)는 하드웨어에서 각도가 반전되어 있습니다

### 이름 규칙
- 영문자, 숫자, 밑줄만 허용
- **금지 문자**: `: { } [ ] , & * # ? | - < > = ! % @ \` " '`
- 최대 50자
- 대소문자 구분

### 예시
```yaml
poses:
  open:
    positions: [0, 0, 0, 0, 0, 0, 0, 0]
  close:
    positions: [110, 0, 110, 0, 110, 0, 110, 0]
  peace:
    positions: [0, 0, 110, 0, 0, 0, 0, 0]
```

## 시퀀스

시퀀스는 서보별 속도와 지연을 가진 다단계 애니메이션을 정의합니다.

### 형식
```yaml
sequences:
  sequence_name:
    steps:
      - "pose_name:speed1,speed2,speed3,speed4,speed5,speed6,speed7,speed8|delay"
      - "SLEEP:duration"
```

### 스텝 형식

**개별 속도와 지연이 있는 포즈:**
```
"pose_name:s1,s2,s3,s4,s5,s6,s7,s8|delay"
```
- `pose_name`: 실행할 포즈의 이름
- `s1-s8`: 각 서보의 개별 속도(1-6, 6이 가장 빠름)
- `delay`: 이동 완료 후 대기할 시간(예: `2.0s`)

**기본 속도를 사용하는 포즈:**
```
"pose_name:3,3,3,3,3,3,3,3|2.0s"
```

**슬립/일시정지:**
```
"SLEEP:1.5s"
```
- 서보를 움직이지 않고 지정된 시간 동안 일시정지합니다

### 속도 값
- 범위: 1(가장 느림) ~ 6(가장 빠름)
- 서보 이동 속도를 제어합니다
- 스텝 내에서 각 서보가 서로 다른 속도를 가질 수 있습니다

### 루프 제어
- 루프 설정은 YAML에 저장되지 **않습니다**
- GUI 시퀀스 플레이어의 체크박스로 제어합니다
- YAML을 편집하지 않고도 유연한 재생이 가능합니다

### 예시
```yaml
sequences:
  demo:
    steps:
      - "open:3,3,3,3,3,3,3,3|2.0s"
      - "close:3,3,3,3,3,3,3,3|2.0s"
      - "open:3,3,3,3,3,3,3,3|1.0s"
  
  wave:
    steps:
      - "open:5,5,5,5,5,5,5,5|0.5s"
      - "SLEEP:0.3s"
      - "close:5,5,5,5,5,5,5,5|0.5s"
      - "SLEEP:0.3s"
```

## 포즈와 시퀀스 관리

### GUI 사용 (`amazing_hand_gui.py`)

**포즈:**
1. 슬라이더나 키보드로 손가락을 배치합니다
2. 「Name:」 필드에 이름을 입력합니다
3. 「➕ Add New」를 클릭하여 저장합니다

**시퀀스:**
1. Sequence Player 섹션에서 「Manage」 버튼을 클릭합니다
2. 대화 상자에서 시퀀스를 작성합니다:
   - 포즈와 속도를 선택합니다
   - 스텝 사이에 지연을 추가합니다
   - ↑/↓ 버튼으로 순서를 바꿉니다
3. 시퀀스 이름을 입력하고 「💾 Save」를 클릭합니다

**실행:**
- 드롭다운에서 시퀀스를 선택합니다
- 연속 재생을 원하면 「Loop」를 체크합니다
- 「▶ Play」를 클릭합니다

### CLI 사용 (`amazing_hand_cmd.py`)

**모든 포즈와 시퀀스 나열:**
```bash
python amazing_hand_cmd.py --list
```

**포즈 실행:**
```bash
python amazing_hand_cmd.py --pose open
```

**시퀀스 실행:**
```bash
python amazing_hand_cmd.py --sequence demo
```

**루프로 실행:**
```bash
python amazing_hand_cmd.py --sequence wave --loop
```

**대체 설정 사용:**
```bash
python amazing_hand_cmd.py --pose open --config /path/to/hand_config.yaml
```

## 수동 편집

`data/hand_config.yaml`을 직접 편집할 수 있습니다:

1. **YAML 문법을 따르십시오** - 들여쓰기는 일관되어야 합니다(2칸 또는 4칸)
2. 위치에는 **인라인 배열 형식**을 사용하십시오:
   ```yaml
   positions: [0, 0, 0, 0, 0, 0, 0, 0]
   ```
3. 특수 문자를 보존하려면 **시퀀스 스텝을 따옴표로 감싸십시오**:
   ```yaml
   steps:
     - "open:3,3,3,3,3,3,3,3|2.0s"
   ```
4. **이름을 검증하십시오** - 금지 문자를 피하십시오
5. 변경 사항을 다시 로드하려면 **GUI를 재시작**하십시오
6. 중요한 편집 전에 **백업을 유지**하십시오

## 검증

GUI와 CLI는 다음을 자동으로 검증합니다:
- 포즈/시퀀스 이름(금지 문자)
- 저장 시 YAML 문법
- 위치 배열 길이(8이어야 함)

유효하지 않은 이름은 금지 문자를 보여주는 오류 메시지와 함께 거부됩니다.

## 라이선스

Copyright 2026 AmazingHand Control Contributors

Apache License, Version 2.0에 따라 라이선스가 부여됩니다
