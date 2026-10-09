[English](../en/CHANGES.md) | [Deutsch](../de/CHANGES.md) | [Español](../es/CHANGES.md) | [Français](../fr/CHANGES.md) | [Italiano](../it/CHANGES.md) | [日本語](../ja/CHANGES.md) | 한국어 | [Português (BR)](../pt-br/CHANGES.md) | [Português (PT)](../pt-pt/CHANGES.md) | [简体中文](../zh-hans/CHANGES.md) | [繁體中文](../zh-hant/CHANGES.md)

# AmazingHand Controller · 변경 기록 및 근거

원본 프로젝트 대비 무엇이 변경되었는지, 그 이유는 무엇인지, 그리고 그 결과가 실제로 어떠한지 정리합니다.

원본 프로젝트: `Betatester777/AmazingHandControl` (AmazingHand용 Python GUI + CLI)
하드웨어: JuxiTechnology AmazingHand (Feetech SCS0009 서보 8개, 포텐셔미터 피드백) — **양손 지원**, 시작 시 선택

---

## 목차

1. [각도 체계 재캘리브레이션](#1-각도-체계-재캘리브레이션)
2. [전역 버튼: 정확한 raw 위치 구동](#2-전역-버튼-정확한-raw-위치-구동)
3. [새 Middle position 버튼](#3-새-middle-position-버튼)
4. [GUI와 CLI의 불일치(핵심 버그)](#4-gui와-cli의-불일치핵심-버그)
5. [포즈 데이터 수정](#5-포즈-데이터-수정)
6. [시퀀스 플레이어: 타이밍과 진단](#6-시퀀스-플레이어-타이밍과-진단)
7. [Servo Feedback의 새 raw 위치 행](#7-servo-feedback의-새-raw-위치-행)
8. [**좌우 손 지원**](#8-좌우-손-지원)
9. [시리얼 포트 자동 감지](#9-시리얼-포트-자동-감지)
10. [설정 레퍼런스](#10-설정-레퍼런스)
11. [측정 결과](#11-측정-결과)
12. [파일별 요약](#12-파일별-요약)

---

## 1. 각도 체계 재캘리브레이션

### 1.1 각도 한계: `0..110` → `-75..75`

원본은 `0° = 열림, 110° = 닫힘`으로 캘리브레이션되어 있었습니다. 이 손의 실제 가동 범위는 `-75..75`에 해당하므로 모든 것을 재캘리브레이션했습니다.

**`data/config.yaml`**

| 키 | 변경 전 | 변경 후 |
|---|---|---|
| `servo_min` / `servo_max` | -40 / 110 | **-75 / 75** |
| `base_min` / `base_max` | 0 / 110 | **-75 / 75** |
| `side_min` / `side_max` | -40 / 40 | **-35 / 35** |
| `left_open` | `[32, -40]` | **`[32, -35]`** |
| `right_open` | `[-40, 32]` | **`[-35, 32]`** |
| `left_closed` / `right_closed` | `[110, 110]` | **`[75, 75]`** |
| `center_closed` | `[110, 110]` | **`[75, 75]`** |

**19개 포즈 모두 재조정했습니다**, 예를 들어 `open`을 `[0]*8`에서 `[-35]*8`로, `close`를 `[110]*8`에서 `[75]*8`로 변경했습니다.

### 1.2 측방 벌어짐: `±40°` → `±35°`

side 슬라이더는 `u = |side_offset| / |side_min|`로 정규화되므로, 한계값만 바꾸는 것으로는 손가락이 실제로 벌어지는 정도가 **바뀌지 않습니다** — 슬라이더 스케일만 조정될 뿐입니다. 물리적 벌어짐을 바꾸려면 `auto_extremes`도 함께 변경해야 합니다. 둘 다 변경한 결과:

| | 변경 전 (±40) | 변경 후 (±35) |
|---|---|---|
| 슬라이더 범위 | −40 … +40 | −35 … +35 |
| 완전히 열었을 때, 측방 극한에서 | `(32, -40)`, 벌어짐 **72°** | `(32, -35)`, 벌어짐 **67°** |

### 1.3 벤더 레퍼런스와 일치

벤더의 Arduino 데모(`Amazing_RHand_Demo.ino`)는 다음과 같이 변환합니다:

```c
float Step = 0.293; // 300°/1024
sc.RegWritePos(1, MiddlePos[0] + Pos_1 / Step, 0, Speed);
```

그리고 rustypot 1.4.2 (`src/servo/feetech/scs0009.rs`):

```rust
fn to_raw(value: f64) -> i16 {
    let a = (1024.0 * value / (300.0_f64.to_radians()) + 511.0) as i16;
    a.to_be()
}
```

**결론: 양쪽 모두 동일한 각도 스케일을 사용합니다**(0.29297°/스텝, 300° 전체 스케일, raw 0–1023) — 비율 오차는 없습니다. 유일한 체계적 차이는 영점입니다:

- rustypot는 항상 raw **511**을 중심으로 합니다
- 벤더 펌웨어는 서보별 캘리브레이션 값 `` `MiddlePos = {451, 571, 451, 571, 451, 571, 451, 571}` ``을 사용합니다

이 둘은 **±60 raw = ±17.6°**만큼 차이가 납니다. 바로 이것을 아래의 「Middle position」 버튼이 해결합니다.

---

## 2. 전역 버튼: 정확한 raw 위치 구동

### 2.1 문제

원본 `open_all()` / `close_all()`은 각도를 하드코딩하고 있었습니다:

```python
def open_all(self):
    for finger in self.fingers:
        finger.pos_var.set(0)      # hard-coded 0
        finger.side_var.set(0)
        ...
def close_all(self):
    for finger in self.fingers:
        finger.pos_var.set(110)    # hard-coded 110
```

이 값들은 **구 캘리브레이션 스케일**(0 = 열림, 110 = 닫힘)에서 온 것입니다. `-35 / 75`로 재캘리브레이션한 후에는:

- `open_all`이 0°로 설정 → raw **511**로 변환, 즉 대략 기계적 중간 위치 — 손가락이 전혀 열리지 않았습니다
- `close_all`이 110°로 설정 → `base_max = 75`로 클램프되어 75까지만 도달했지만, 레이블은 여전히 110°를 표시했습니다

### 2.2 해결: 직접 raw 위치 경로

각도 경로는 `base/side` 보간 모델을 거치며, 이는 임의의 raw 값에 정확히 도달할 수 없습니다(섹션 4 참조). 그래서 전역 버튼에는 raw 서보 위치를 직접 기록하는 경로를 추가했습니다.

**중요한 구현 세부 사항 하나:** 여기서는 rustypot의 `sync_write_raw_goal_position`을 사용하지 *않습니다*. 매크로로 생성된 소스를 읽어보면, raw API는 `values.to_le_bytes()`를 그대로 전송하는 반면, 변환 API는 먼저 `to_be()`를 적용합니다:

```rust
fn to_raw(value: f64) -> i16 { let a = (...) as i16; a.to_be() }
// sync_write_raw_*: values.iter().map(|v| v.to_le_bytes())   <- no to_be
```

따라서 `451`을 전달하면 `0xC301`(49921)이 출력됩니다. 대신 코드는 `sync_write_goal_position`(라디안)을 사용하여 목표 raw 값에 **정확히** 안착하는 라디안을 풀어내며, 잘림 오차를 피하기 위해 각 raw 스텝의 중간값을 취합니다.

### 2.3 세 버튼의 raw 목표값

`data/config.yaml`에 `raw_positions`를 추가했습니다(인덱스 0 → 서보 ID 1):

```yaml
raw_positions:
  open:   [260, 760, 260, 760, 260, 760, 260, 760]
  close:  [760, 260, 760, 260, 760, 260, 760, 260]
  middle: [451, 571, 451, 571, 451, 571, 451, 571]
```

| 버튼 | 동작 | 서보 ID 1–8 raw |
|---|---|---|
| ✋ Open All | 완전히 펼침 | 260, 760, 260, 760, 260, 760, 260, 760 |
| ✊ Close All | 완전히 닫힘 | 760, 260, 760, 260, 760, 260, 760, 260 |
| ⊙ Center All | 측방 재중앙 정렬(열림/닫힘은 변경 없음) | — |
| **Middle position** | **캘리브레이션된 중간 위치로 복귀** | 451, 571, 451, 571, 451, 571, 451, 571 |

> ⚠️ `raw_positions`는 **손별 캘리브레이션 값**입니다. 벤더 자신의 주석은 *"값을 여러분의 캘리브레이션 결과로 교체하십시오"* 입니다 — 손이나 서보를 교체한 후에는 다시 측정하십시오.

### 2.4 슬라이더 동기화 트레이드오프

raw 목표값은 `base/side` 모델을 우회하므로 정확히 대응하는 슬라이더 값이 없습니다. 버튼을 실행하면 슬라이더는 가장 가까운 정수로 설정됩니다:

| 위치 | 슬라이더 표시 |
|---|---|
| open | base = −73, side = 0 |
| close | base = +73, side = 0 |
| middle | base = −17, side = 0 |

비용: 이후 슬라이더를 건드리면 손이 목표에서 최대 약 1 raw 단위(0.3°)만큼 벗어납니다. 이는 의도된 것입니다 — 캘리브레이션된 위치에 정확히 도달하는 것이 더 중요하기 때문입니다.

---

## 3. 새 Middle position 버튼

`✋ Open All` / `✊ Close All` / `⊙ Center All` 오른쪽에 배치했습니다. 손을 **벤더 캘리브레이션 기계적 중간 위치**(raw 451/571)로 되돌립니다.

**왜 필요한가:** `open_all`과 `close_all`의 중간점은 기계적 중간 위치가 *아닙니다*. 벤더의 중간 위치는 `MiddlePos`이며, raw 511에서 ±60 raw(±17.6°) 떨어져 있습니다. 전원을 켠 후에는 잘 정의되고 반복 가능한 영점이 필요합니다.

---

## 4. GUI와 CLI의 불일치(핵심 버그)

### 4.1 증상

**동일한 포즈라도 GUI의 `✓ Apply`로 적용할 때와 CLI의 `--pose`로 적용할 때 손의 움직임이 다릅니다.**

### 4.2 근본 원인

GUI는 다음과 같은 경로로 포즈를 적용했습니다:

```
set_positions(p1, p2)  →  decompose into (base, side), stored in the sliders
                       →  get_positions() recomputes via compute_auto_positions() in Auto mode
```

그러나 `compute_auto_positions`는 `decompose_servo_positions`의 **정확한 역함수가 아닙니다**(중심값과 극값이 경험적 값입니다). CLI의 `apply_pose()`는 값을 직접 전송합니다.

측정 결과: **19개 포즈 중 12개가 왜곡**되었으며, 최대 32°에 달했습니다:

| 포즈 | 저장값 | GUI가 실제 전송한 값 | 편차 |
|---|---|---|---|
| `ring_close` | 약지 `(75, -35)` | 약지 `(43, -5)` | **32° / 30°** |
| `middle_close` | 중지 `(75, -35)` | 중지 `(43, -5)` | **32° / 30°** |
| `pointer_close` | 검지 `(75, -35)` | 검지 `(43, -5)` | **32° / 30°** |
| `thumb_close` | 엄지 `(75, -35)` | 엄지 `(43, -5)` | **32° / 30°** |
| `wave1` | `(-75, -3)` | `(-75, 9)` | 12° |
| `hifive` | 엄지 `(-75, -3)` | 엄지 `(-75, 9)` | 12° |
| `greeting` | 약지 `(-18, -57)` | 약지 `(-10, -68)` | 8° / 11° |
| `victory` | 중지 `(-68, -9)` | 중지 `(-75, 1)` | 7° / 10° |
| `paper` | 검지 `(-52, -22)` | 검지 `(-59, -16)` | 7° / 6° |
| `ok` | 검지 `(36, 46)` | 검지 `(38, 43)` | 2° / 3° |

**패턴:** 각 손가락이 `pos1 == pos2`인 대칭 포즈(`open` `close` `stone` `two` `scissors` `one` `three`)는 정확히 왕복합니다. 측방 벌어짐이 포함된 모든 비대칭 포즈는 어긋납니다.

### 4.3 수정

`SERVO_PAIRS` 순서로 각도를 서보에 직접 전송하는 `_send_exact_positions()`를 추가했습니다(CLI의 `apply_pose`와 동일). 이제 두 포즈 진입점 모두 이를 사용합니다:

- Pose Management의 `✓ Apply` 버튼
- `_apply_pose_from_config()` — 시퀀스 플레이어와 포즈 목록

슬라이더는 여전히 표시를 위해 `set_positions()`로 갱신되지만, **무엇을 전송할지는 더 이상 결정하지 않습니다**.

### 4.4 결과

수정 후 **19개 포즈 모두 `stored == GUI-sent == CLI-sent`를 만족합니다**.

**부작용:** GUI의 실제 제스처가 바뀝니다, 특히 비대칭 포즈에서 두드러집니다. 이는 이 수정의 의도된 효과입니다.

---

## 5. 포즈 데이터 수정

### 5.1 네 개의 `*_close` 포즈가 잘못 작성됨

```yaml
# Before — target finger (75, -35)
ring_close:    [75, -35, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, -35, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, -35, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, -35]
```

`(75, -35)`는 `base = 20, side = -55`(범위 초과)로 분해됩니다 — 이는 "이 손가락을 닫으라"가 아니라 *"27%만 말리고 왼쪽으로 강하게 쓸어 넘김"*을 의미합니다. `close`와 `one`에 맞춰 올바른 형태는 `(75, 75)`입니다:

```yaml
# After — target finger fully closed (75, 75), others stay open (-35, -35)
ring_close:    [75, 75, -35, -35, -35, -35, -35, -35]
middle_close:  [-35, -35, 75, 75, -35, -35, -35, -35]
pointer_close: [-35, -35, -35, -35, 75, 75, -35, -35]
thumb_close:   [-35, -35, -35, -35, -35, -35, 75, 75]
```

분해로 검증: 목표 손가락 `base = 75`(완전히 닫힘), `side = 0`(좌우 어느 쪽으로도 치우치지 않음).

**영향:** 이 네 개를 사용하는 `finger_roll` 시퀀스가 이제서야 진정한 "각 손가락을 차례로 말기"가 되었습니다.

### 5.2 `greeting` / `paper`의 엄지

둘 다 원래 엄지가 `(75, 75)`(완전히 닫힘)였습니다. `paper`(布, 펼친 평평한 손바닥)에서 닫힌 엄지는 명백히 잘못입니다.

`greeting`은 처음에 `(-75, -3)`으로 변경했지만(`hifive`의 벌어진 엄지를 재사용), 하드웨어 테스트 결과 해당 스텝은 엄지가 **150°** 이동해야 했고 이는 1.0초에 맞지 않았습니다(6.3 참조). 최종 상태:

```yaml
greeting: [-18, -57, -32, -32, -70, -7, -35, -35]   # thumb (-35, -35), same as open
paper:    [-19, -56, -34, -34, -52, -22, -75, -3]   # keeps the splayed thumb (flat palm)
```

이로써 두 제스처가 구분됩니다: `greeting`은 파도 인사로 엄지가 자연스럽게 열리기만 하고, `paper`는 평평한 손바닥으로 엄지가 벌어집니다.

---

## 6. 시퀀스 플레이어: 타이밍과 진단

### 6.1 잘못된 "목표에 도달하지 못함" 경고 수정

하드웨어에서 `demo`를 실행하면 세 개의 잘못된 경고가 발생했습니다:

```
⚠ Pose #42 'greeting': Servos did not reach target! Max error: 52°
```

**근본 원인:** `_log_pose_completion`이 **서로 다른 순서**의 두 배열을 빼고 있었습니다.

- `monitor_servos()`는 캐시를 **서보 ID 순서**로 기록합니다: `latest_actual_positions[servo_id - 1] = ...`(인덱스 0 = ID1 = 검지)
- 전달된 `target_positions`는 포즈 배열로, **위젯 순서** 약지 / 중지 / 검지 / 엄지입니다(인덱스 0 = 약지 = ID5)

따라서 검지의 판독값을 약지의 목표값에서 빼고 있었습니다.

**증거**(측정 로그에서 재계산):

```
target (widget order)   : [-18, -57, -32, -32, -70, -7, -75, -3]
actual (servo-ID order) : [-68.85, -6.74, -33.69, -31.35, -18.46, -54.79, -74.12, -3.22]
compared as-is          -> max error 52°      <-- what the old code did
target reordered        : [-70, -7, -32, -32, -18, -57, -75, -3]
compared in servo order -> max error 2.21°    <-- actually spot on
```

**수정:** 비교 전에 `pose_to_servo_order()` / `servo_to_pose_order()`를 적용했고, 출력되는 `current`는 다시 변환하여 로그에서 `target`과 `current`가 열 단위로 정렬되도록 했습니다.

### 6.2 도달 확인 실행 시점 수정

원본은 전송 후 **고정 2000 ms** 후에 확인했습니다:

```python
self.root.after(2000, lambda ...: self._log_pose_completion(...))
```

그러나 시퀀스 스텝은 1.0초만 기다리므로, 확인이 실행될 때쯤에는 다음 스텝이 이미 전송되어 판독값이 필연적으로 *다음* 동작에 속하게 됩니다:

```
25.388  Pose #40 'ok'      sent
26.782  Pose #41 'victory' sent        <- already moved on
27.742  Pose #40 'ok'      checked -> reading is mid-way to victory
```

**수정:**

1. `_apply_pose_from_config`에 `check_after` 매개변수를 추가했습니다. 단일 포즈에 `✓ Apply`를 클릭하는 동작은 그대로입니다(2.0초 후 동작이 멈출 때까지 대기); 시퀀스 재생은 **해당 스텝 자체의 지연**을 전달하므로 확인이 스텝 경계(지연 − 100 ms)에서 이루어지고 더 이상 동작을 기다리지 않습니다.
2. **대체 방지 가드**를 추가했습니다: `_log_pose_start`가 `current_pose_id`를 기록하고, 이후 더 새로운 명령이 이를 대체했다면 도달 확인을 건너뛰고 로그에 `current=<superseded>`를 표시합니다.

### 6.3 시퀀스 지연 튜닝

하드웨어 로그에서 **유효 속도**를 역산했습니다(속도 3은 명목상 172°/s):

| 포즈 | 이동량 | 0.9초에서 오차 | 추정 유효 속도 |
|---|---|---|---|
| `ok` | 110° | 0.5° | 121.7°/s (명목의 71%) |
| `victory` | 110° | 1.0° | 121.1°/s (70%) |
| `greeting` | 132° | 7.0° | 138.9°/s (81%) |

> 부하가 걸리면 실제 속도는 명목의 약 **70%**에 불과합니다. 지연을 선택할 때 중요한 숫자는 바로 이것입니다.

**`demo` 변경 사항:**

```yaml
  demo:
    steps:
    - open:3,3,3,3,3,3,3,3|2.0s
    - close:6,6,6,6,6,6,6,6|2.0s
    - ok:3,3,3,3,3,3,3,3|1.0s
    - victory:3,3,3,3,3,3,3,3|1.0s
    - greeting:3,3,3,3,3,3,3,3|1.5s      # was 1.0s
    - close:6,6,6,6,6,6,6,6|2.0s         # new: settle back into a fist
```

- `greeting` 1.0초 → **1.5초**: 해당 스텝은 132°(약지의 두 번째 서보)를 이동하며 1.0초 안에 끝낼 수 없습니다
- **새 마지막 `close`**: `demo`가 손을 닫은 상태로 끝나며, 루프도 깔끔해집니다
- 총 실행 시간 7.0초 → **9.5초**

### 6.4 `wave`: 측방 스윙을 ±30°로 제한

원본 `wave_r` / `wave_l`은 **±36**의 `side`를 의미했습니다(±35 한계를 초과하므로 35로 클램프되고 있었습니다).

`side = base − pos1`, `base = (pos1 + pos2) / 2`를 풀면 `pos1 = base − side`, `pos2 = base + side`가 됩니다. `base = −39`를 유지하고 `side`를 ±30으로 줄이면:

```yaml
wave_r: [-9, -69, -9, -69, -9, -69, -69, -9]     # was [-3, -75, -3, -75, -3, -75, -75, -3]
wave_l: [-69, -9, -69, -9, -69, -9, -9, -69]     # was [-75, -3, -75, -3, -75, -3, -3, -75]
```

검증: `wave_r`의 side는 `[-30, -30, -30, +30]`이고, `wave_l`은 이의 손가락별 대칭입니다.

**부작용(예상됨):** 각 스윙의 이동량도 40°/72°에서 **34°/60°**로 줄어듭니다. 파도가 전체적으로 좁아지며, 이는 타이밍 여유를 넓혀줄 뿐입니다.

---

## 7. Servo Feedback의 새 raw 위치 행

**`Current (0-1023)`** 행이 `Position (°)` 바로 아래에 위치하며, 실시간 raw 서보 위치를 표시합니다.

```
1. Goal (°)
2. Position (°)
3. Current (0-1023)      <== new
4. Speed (°/s)
5. Torque (%)
6. Voltage (V)
7. Current (mA)
8. Temperature (°C)
9. Status
10. Moving
```

**트레이드오프:** 추가 시리얼 읽기가 없습니다. raw 값은 모니터 스레드가 **이미** 읽은 위치에서 파생되므로 폴링 루프가 시리얼 트래픽을 두 배로 늘리지 않습니다. 정확도는 철저히 검증했습니다: **2048개 조합(raw 0–1023 × 홀수/짝수 서보)이 오차 없이 왕복합니다**.

**활용:** 벤더의 캘리브레이션과 직접 비교하십시오 — `open`은 `260 / 760`이 교대로, `middle`은 `451 / 571`이 나와야 합니다.

> 행 이름에는 기존의 `Current (mA)`(추정 전류 소비)와 구별하기 위해 범위 접두사가 붙어 있습니다.

---

## 8. 좌우 손 지원

### 8.1 벤더는 두 개의 펌웨어를 제공합니다

벤더는 손마다 별도의 Arduino 데모를 제공하며, 매개변수가 완전히 다릅니다:

| | 오른손 `Amazing_RHand_Demo` | 왼손 `Amazing_LHand_Demo` |
|---|---|---|
| 서보 ID | **1–8** | **11–18** |
| 손가락 → ID | 검지 `1,2` / 중지 `3,4` / 약지 `5,6` / 엄지 `7,8` | **약지 `11,12` / 중지 `13,14` / 검지 `15,16` / 엄지 `17,18`** |
| 중간 `MiddlePos` | `[451, 571, 451, 571, …]` | `[571, 451, 571, 451, …]` |

디버그 튜토리얼에는 분명히 나와 있습니다: *"손 하나는 서보 8개를 사용하며, 오른손의 ID는 1-8로, 왼손의 ID는 11-18로 설정해야 합니다."*

왼손의 번호 매김은 **역순**(약지가 먼저)이며, 이는 거울 대칭된 기계적 배치에 대응합니다.

### 8.2 ID만 바꾸는 것으로는 부족한 이유

ID는 첫 번째 계층일 뿐입니다. 손 사이에는 두 가지 물리적 차이가 남아 있으며, 둘 중 하나만 놓쳐도 제스처가 왜곡됩니다.

#### 차이 1: 35.16° 장착 오프셋

양손 모두 **동일한 제스처 값에 각자의 `MiddlePos`를 더한 것**을 사용합니다:

```c
// Right
#define MiddlePos {451, 571, ...}
Move_Index(-35, 35)  →  ID1 = 451 + (-35)/0.293 = 331.5

// Left
#define MiddlePos {571, 451, ...}
Move_Index(-35, 35)  →  ID15 = 571 + (-35)/0.293 = 451.5
```

동일한 "open" 제스처가 각 손에서 서로 다른 raw 값에 도달합니다. 이를 이 프로그램의 각도 공간으로 변환하면 **120 raw = 35.16°**만큼 차이가 납니다.

#### 차이 2: 손가락의 두 서보가 서로 바뀝니다

```c
// Right Victory                      // Left Victory
Move_Index (-15, 65);                Move_Index (-65, 15);
Move_Middle(-65, 15);                Move_Middle(-15, 65);
```

손가락마다 `(a, b) → (-b, -a)`이며, 포즈 값에서는 **각 손가락의 두 숫자를 교환**하는 것을 의미합니다.

이를 놓치면 **벌어짐 방향이 반전**됩니다 — 증상은 V 사인이 두 손가락을 오므리는 동안, 붙어 있어야 할 손가락들이 벌어지는 것입니다.

> 흔한 오독 하나: `Perfect`에서 검지와 중지 값은 양손 모두 **동일**하며(`(50,-50)`, `(0,0)`), 엄지만 다릅니다. 따라서 규칙은 "검지와 중지를 교환"이 아니라 손가락별 `(-b,-a)`입니다 — 이는 대칭 쌍에서는 항등 연산입니다.

### 8.3 구현

**양손은 하나의 `hand_config.yaml`을 공유합니다.** 저장되는 포즈는 항상 **오른손 순서**이며, 왼손은 내보낼 때와 되돌릴 때 변환하므로 유지 관리할 두 번째 포즈 라이브러리가 없습니다.

변환은 `hand_logic.py`에 있습니다:

| 함수 | 목적 |
|---|---|
| `resolve_hand_config(app_config, hand)` | `hands.<name>`을 최상위(오른손) 설정 위에 덮어씁니다 |
| `servo_pairs()` / `servo_ids()` | 해당 손의 손가락별 `(servo1_id, servo2_id)` / 모든 서보 ID 오름차순 |
| `hand_angle_offset()` / `hand_mirrors_pose()` | 손의 두 차이 매개변수를 읽습니다 |
| `adapt_pose_for_hand(positions, mirror)` | 각 손가락의 `(pos1, pos2)`를 교환합니다. **교환은 자기 자신의 역연산**이므로 동일한 함수가 적용 시 변환하고 저장 시 되돌립니다 |

**적용된 위치:**

- GUI: 포즈 적용(`✓ Apply` 버튼과 시퀀스 재생), 그리고 포즈 저장
- CLI: `--pose` / `--sequence`

**세 전역 버튼의 raw 목표값**은 손별로 설정되며 이 변환을 거치지 않습니다(`raw_positions`는 `hands.left` 아래에 따로 기록됩니다).

### 8.4 사용법

GUI는 열기 전에 묻습니다:

```
  AmazingHand — which hand?
    1 = right hand  (servo IDs 1-8)
    2 = left hand   (servo IDs 11-18)
  Enter 1 or 2 [1]:
  LEFT hand — servo IDs 11-18
    Ring (11, 12)  Middle (13, 14)  Pointer (15, 16)  Thumb (17, 18)
    middle position raw: [571, 451, 571, 451, 571, 451, 571, 451]
```

Enter를 누르면 `config.yaml`의 `hand:` 값이 사용됩니다. 프롬프트를 건너뛰려면:

```bash
python amazing_hand_gui.py --hand left
python amazing_hand_cmd.py --pose victory --hand left
```

### 8.5 왼손 최초 사용 체크리스트

`hands.left.raw_positions`에서 벤더 기본값인 것은 **middle**뿐이며(`571, 451`), `open`과 `close`는 벤더의 데모에서 도출했습니다:

| 버튼 | 왼손 raw | 출처 |
|---|---|---|
| Middle position | `571, 451, …` | 벤더 기본값 |
| Open All | `380, 642, …` | 도출: 오른손 Open All과 동일한 제스처를 왼손 `MiddlePos`에 적용 |
| Close All | `880, 142, …` | 동일 |

**왼손을 처음 연결할 때 다음 순서로 확인하십시오:**

1. **Middle position**을 눌러 `Current (0-1023)` 행이 `571, 451, 571, 451, …`를 표시하는지 확인합니다
2. **Open All** / **Close All**을 누릅니다 — 걸림 없이 스톱까지 도달해야 합니다
3. `victory`(검지와 중지가 V자로 벌어짐), `greeting`(세 손가락이 모임), `ok`(엄지와 검지 끝이 만남)를 시도합니다

문제가 있으면:

| 증상 | 변경 |
|---|---|
| Middle position이 잘못 표시됨 | `hands.left.raw_positions.middle` |
| 벌어짐 방향이 반전됨 | `hands.left.mirror_pose`를 `false`로 설정 |
| 이동량이 너무 짧거나 김 | `hands.left.raw_positions.open` / `close` |

### 8.6 왼손이 1-8로 번호가 매겨진 경우

일부는 왼손의 서보 번호를 1–8로 다시 매깁니다. 이 경우 `hands.left.servos`만 변경하면 됩니다:

```yaml
hands:
  left:
    servos:
      # Renumbered following the vendor's left-hand order: ring first
      ring:    [1, 2]
      middle:  [3, 4]
      pointer: [5, 6]
      thumb:   [7, 8]
      all_ids: [1, 2, 3, 4, 5, 6, 7, 8]
```

> `angle_offset`과 `mirror_pose`는 **변경되지 않습니다** — 이들은 ID 번호가 아니라 기계적 구조를 설명합니다. 각 손가락의 쌍이 "홀수 ID가 먼저"를 유지하므로 짝수 서보 반전도 여전히 적용됩니다.

---

## 9. 시리얼 포트 자동 감지

### 9.1 문제

원본은 Windows 포트 목록을 `COM1`–`COM20`으로 하드코딩했습니다:

```python
available_ports = [f'COM{i}' for i in range(1, 21)]
```

그러나 어댑터는 어떤 포트 번호에도 붙을 수 있습니다(이 머신에서는 `COM243`이 측정되었습니다). 결과: **드롭다운에 여러분의 포트가 아예 나타나지 않으며**, 자동 연결은 존재하지 않는 설정 기본값으로 폴백하여 "시스템이 지정된 파일을 찾을 수 없습니다" 오류로 실패합니다.

### 9.2 수정

`available_serial_ports()`를 추가하여 단계적으로 폴백합니다:

1. pyserial의 `list_ports.comports()`(설치된 경우 사용 — 가장 풍부한 정보)
2. pyserial이 없는 Windows: 레지스트리 키 `HARDWARE\DEVICEMAP\SERIALCOMM` 읽기 (**표준 라이브러리만 사용**, 새 의존성 없음)
3. Linux/macOS: `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/ttyAMA*`, `/dev/cu.usb*` 글롭
4. 위의 모든 것이 실패한 경우에만 원래의 후보 목록으로 폴백

포트는 **자연 정렬**되므로 `COM2`가 `COM10`보다 먼저 옵니다.

### 9.3 지원 변경

- 드롭다운이 `readonly`에서 **편집 가능**으로 변경되었습니다 — 감지가 놓친 포트를 직접 입력할 수 있습니다
- 설정된 기본값이 없으면 GUI는 존재하지 않는 기본값을 시도하는 대신 **실제로 존재하는 첫 번째 포트로 시작**합니다
- **명시적 `--port`는 이 폴백으로 덮어쓰이지 않습니다**(`port_was_explicit`으로 추적)

---

## 10. 설정 레퍼런스

### `data/config.yaml`

최상위 `servos` / `auto_extremes` / `raw_positions`는 **오른손**을 설명하며 기본값 역할을 합니다; `hands.<name>`이 키별로 이를 덮어씁니다.

```yaml
hand: right           # active hand: right | left (the GUI asks; --hand skips it)

limits:
  servo_min: -75      # absolute lower travel limit
  servo_max: 75       # absolute upper travel limit
  base_min: -75       # open/close slider range (-75 = fully open)
  base_max: 75        #                          ( 75 = fully closed)
  side_min: -35       # left/right slider range
  side_max: 35

auto_extremes:        # servo positions at the side slider's extremes — right hand
  left_open:  [32, -35]
  right_open: [-35, 32]
  left_closed:  [75, 75]
  right_closed: [75, 75]

raw_positions:        # global buttons' raw targets — right hand (index 0 → servo ID 1)
  open:   [260, 760, ...]
  close:  [760, 260, ...]
  middle: [451, 571, ...]

hands:
  left:               # overrides for the left hand; only list what differs
    servos:
      ring:    [11, 12]
      middle:  [13, 14]
      pointer: [15, 16]
      thumb:   [17, 18]
    raw_positions:    # index 0 → servo ID 11
      open:   [380, 642, ...]
      close:  [880, 142, ...]
      middle: [571, 451, ...]
    angle_offset: -35.16   # mounting offset (see 8.2)
    mirror_pose: true      # per-finger servo swap (see 8.2)
```

`auto_extremes`는 양손이 **공유**합니다 — side 슬라이더는 포즈 공간에서 동일하게 동작하며, 거울 대칭 손은 물리적으로 반대 방향으로 벌어질 뿐입니다.

### `data/hand_config.yaml`

포즈의 8개 값은 **약지, 중지, 검지, 엄지** 순서이며(서보 쌍 `(5,6) (3,4) (1,2) (7,8)`), 서보 ID 순서가 **아닙니다**.

**이 파일은 양손이 공유하며 항상 오른손 순서로 저장됩니다.** 왼손은 적용 시 각 손가락의 쌍을 교환하고, 저장 시 다시 교환합니다.

> ⚠️ `amazing_hand_cmd.py` 상단의 docstring은 "index 0→servo1 … 7→servo8"이라고 주장합니다. 이 주석은 **틀렸습니다**; 위의 순서가 코드가 실제로 사용하는 것입니다.

---

## 11. 측정 결과

### 도달 정확도(수정 후)

| 포즈 | 목표 | 실제 | 최대 오차 |
|---|---|---|---|
| `open` | 모두 −35 | −36.6 … −33.4 | ≤1.6° |
| `close` | 모두 75 | 74.7 … 75.3 | ≤0.3° |
| `ok` | — | — | 0.5° |
| `victory` | — | — | 1.0° |
| `greeting` | — | — | 2.2° |

### 변환 검증

```
raw -> degrees -> raw: 2048 combinations, zero error
open    raw [260, 760] -> back [260, 760]
middle  raw [451, 571] -> back [451, 571]
close   raw [760, 260] -> back [760, 260]
```

### 알려진 잔여 문제

- **`demo`의 `ok`와 `victory`는 타이밍 여유가 거의 없습니다**(측정 속도 기준 +0.01초). < 5° 허용오차가 이들을 잡아주기 때문에 현재는 통과합니다. 배터리 전압이 떨어지거나, 온도가 변하거나, 손이 조금만 더 뻑뻑해져도 초과할 수 있습니다. 두 지연을 1.0초에서 1.2초로 올리는 것이 다음 단계로 명백합니다.
- **`scissors`는 `two`와 바이트 단위로 동일**하며, **`stone`은 `close`와 바이트 단위로 동일**합니다. 의미상으로는 문제없지만(가위 = 두 손가락, 주먹 = 주먹) 문자 그대로 중복이며 정리되지 않았습니다.
- **슬라이더는 여전히 raw 목표값에 대해 약 0.3°의 표현 오차**를 가집니다(2.4 참조).
- **`config.yaml`과 `hand_logic.py`의 `default_config`는 동기화되어 있지 않습니다.** 후자는 여전히 원래 스케일(`servo_min: -40` 등)을 담고 있으며, `config.yaml`이 없을 때만 사용됩니다. 테스트 `test_hand_logic.py::TestAngleLimits::test_defaults`는 바로 그 옛 기본값을 단언합니다.

---

## 12. 파일별 요약

| 파일 | 변경 사항 |
|---|---|
| `hand_logic.py` | 새 SCS0009 변환 상수; `raw_to_degrees` / `raw_to_radians` / `degrees_to_raw` / `pose_to_servo_order` / `servo_to_pose_order`; `raw_position` 표시 형식; `raw_positions` 기본값; **손 지원**(`HAND_NAMES` / `DEFAULT_HAND_SERVOS` / `resolve_hand_config` / `servo_pairs` / `servo_ids` / `hand_angle_offset` / `hand_mirrors_pose` / `adapt_pose_for_hand`); **`available_serial_ports()`**; 설정 파일 I/O를 **UTF-8**로 전환(Windows GBK 기본값을 사용하던 탓에 비 ASCII 주석에서 충돌했음) |
| `amazing_hand_gui.py` | 새 `_apply_raw_hand_position` / `middle_all` / `_send_exact_positions`; `open_all` / `close_all` / `_apply_pose_from_config` / `_log_pose_completion` 재작성; 새 **Middle position** 버튼; Servo Feedback에 새 raw 위치 행; `self.app_config`를 인스턴스 속성으로 승격; 미사용 `latest_goal_positions` 제거 및 `feedback_data['goal']` 기록 순서 통일; **시작 시 손 선택 + `--hand`**; **하드코딩된 8개의 `range(1,9)`를 손의 실제 ID로 교체**; 창 제목에 활성 손 표시; 각도 오프셋과 거울 변환을 모든 포즈 경로에 연결; **포트 드롭다운이 이제 감지된 포트를 나열하고 입력도 허용** |
| `amazing_hand_cmd.py` | 새 `--hand`; `connect` / `apply_pose` / `wait_for_motion` / 종료 시 토크 해제가 이제 손의 실제 ID를 사용; 포즈 및 시퀀스 경로에 각도 오프셋과 거울 변환 적용; 설정 읽기를 UTF-8로 전환 |
| `data/config.yaml` | `limits` / `auto_extremes` 재캘리브레이션; `raw_positions` 추가; `hand`와 `hands.left` 오버라이드 블록 추가 |
| `data/hand_config.yaml` | 19개 포즈 모두 재조정; 네 개의 `*_close` 포즈 수정; `greeting` / `paper` 엄지 수정; `wave_r` / `wave_l` 스윙을 ±30으로 축소; `demo`에 더 긴 `greeting` 지연과 새 닫기 스텝 추가 |
| `pyproject.toml` | `build-backend` 수정(`setuptools.backends.legacy:build` → `setuptools.build_meta`) |

### 용어집

| 용어 | 의미 |
|---|---|
| **Auto mode** | 슬라이더 두 개 — "base"(열기/닫기)와 "side"(측방) — 가 한 손가락의 두 서보를 간접적으로 구동 |
| **Raw mode** | 손가락의 두 서보 각도를 직접 제어 |
| **base** | 열기/닫기 양, `(pos1 + pos2) / 2` |
| **side** | 측방 오프셋, `base − pos1` |
| **raw** | 서보 내부 위치 단위: 300°에 걸쳐 0–1023, 중심 511 |
| **MiddlePos** | 벤더 펌웨어의 서보별 중간 캘리브레이션; 손마다 다름(8.1 참조) |
| **angle_offset** | 손 사이의 35.16° 장착 오프셋(8.2 참조) |
| **mirror_pose** | 왼손의 손가락별 서보 쌍 교환(8.2 참조) |
