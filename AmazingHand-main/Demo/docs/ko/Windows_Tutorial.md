[English](../en/Windows_Tutorial.md) | [Deutsch](../de/Windows_Tutorial.md) | [Español](../es/Windows_Tutorial.md) | [Français](../fr/Windows_Tutorial.md) | [Italiano](../it/Windows_Tutorial.md) | [日本語](../ja/Windows_Tutorial.md) | 한국어 | [Português (BR)](../pt-br/Windows_Tutorial.md) | [Português (PT)](../pt-pt/Windows_Tutorial.md) | [简体中文](../zh-hans/Windows_Tutorial.md) | [繁體中文](../zh-hant/Windows_Tutorial.md)

# AmazingHand 정교한 로봇 손 핸드 트래킹 · Windows 튜토리얼

이 튜토리얼은 AmazingHand(Pollen Robotics의 정교한 로봇 손) 공식 Demo를 원클릭 배포 스크립트와 함께 다룹니다.
스크립트는 번호 순서대로 실행하십시오. **모든 스크립트는 `Demo\Windows_Deploy_Scripts\`에 있으며, 더블 클릭으로 실행합니다.**

---

## 목차

1. [하드웨어 준비](#1-하드웨어-준비)
2. [환경 설정 (스크립트 1)](#2-환경-설정-스크립트-1)
3. [배선](#3-배선)
4. [시리얼 포트 설정 (스크립트 2)](#4-시리얼-포트-설정-스크립트-2)
5. [코드 배포 (스크립트 3)](#5-코드-배포-스크립트-3)
6. [Demo 실행 (스크립트 4)](#6-demo-실행-스크립트-4)
7. [프로젝트 정리 (스크립트 0)](#7-프로젝트-정리-스크립트-0)
8. [문제 해결 및 참고 사항](#8-문제-해결-및-참고-사항)
9. [코드 구조](#9-코드-구조)

---

## 1. 하드웨어 준비

| 품목 | 요구 사항 |
|---|---|
| 정교한 로봇 손 | 오른손 / 왼손 / 양손 |
| 서보 드라이버 보드 | 외장형, USB로 PC 연결 |
| 전원 | **최소 5V 4A** (USB만으로는 부족하므로 외부 PSU 사용) |
| 카메라 | 내장 카메라 또는 USB 웹캠 |

> 모델 파일(URDF 등)은 [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e)에서 열람/다운로드할 수 있습니다.

---

## 2. 환경 설정 (스크립트 1)

**`1-Install_Env.bat`을 더블 클릭합니다** — 자동으로 다음을 수행합니다:

1. **MSVC 빌드 도구 확인** (cl.exe) — Rust 컴파일에 필요합니다. 없으면
   "Desktop development with C++" 워크로드와 함께 Visual Studio 2022 Build Tools를 설치한 뒤 터미널을 다시 여십시오.
2. **Rust 설치** (rustup + stable-msvc 툴체인)
3. **cargo tuna 미러 설정** (`C:\Users\<you>\.cargo\config.toml`) — crate 다운로드 속도 향상
4. **uv 설치** (Python 패키지 관리자)
5. **dora-cli 0.5.0 설치** (`cargo install`, 첫 컴파일은 약 10–20분 소요, 기다려 주십시오)
6. **dora-rs pip 패키지 설치** (선택, 배포 중 venv에도 설치됩니다)

> **중요**: 스크립트 실행 후 **터미널을 닫았다가 다시 여십시오**. 그래야 환경 변수가 적용됩니다.
> 네트워크 환경에 따라 다운로드가 느릴 수 있습니다 — 중단하지 말고 기다려 주십시오.

### 수동 설치 (스크립트를 사용할 수 없는 경우)

- **Rust**: <https://www.rust-lang.org/tools/install> — rustup-init.exe 사용, 기본 MSVC 툴체인.
  - PATH: `%USERPROFILE%\.cargo\bin` 추가
- **uv**: PowerShell: `irm https://astral.sh/uv/install.ps1 | iex`
  - PATH: `%USERPROFILE%\.local\bin` 추가
- **dora-cli**: `cargo install dora-cli --version 0.5.0`

### cargo tuna 미러 (config.toml)

```
[source.crates-io]
replace-with = "tuna"

[source.tuna]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[registries.tuna]
index = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[http]
check-revoke = false
```

> **sparse 인덱스**(위)를 사용하고, git 리포지터리 미러는 사용하지 마십시오. git 미러는 먼저 약 1 GB의 인덱스를 다운로드하며 `Updating 'tuna' index`에서 멈추는 경우가 많습니다.

---

## 3. 배선

- 서보 드라이버 보드를 USB로 PC에 연결하고, **외부 5V 4A 전원으로 전원을 공급합니다**
- 포트를 찾습니다: **장치 관리자 → 포트(COM 및 LPT)**, 예: `COM11`

---

## 4. 시리얼 포트 설정 (스크립트 2)

**`2-Setup_Serial.bat`을 더블 클릭합니다**(로직은 `2-Setup_Serial.ps1`에 있음):

1. "Connect the driver board" → Enter를 눌러 스캔
2. 감지된 COM 포트가 나열됩니다(장치 이름 포함)
3. 포트가 하나면 Enter로 확인하고, 여러 개면 인덱스를 입력합니다
4. 3개의 dataflow yml 파일에 `--serialport`를, `AHControl\src\main.rs`에 기본 포트를 기록합니다
5. 원본 파일은 `.bak`으로 백업됩니다

> USB 케이블을 다시 꽂으면 COM 번호가 바뀔 수 있습니다 — 이 스크립트를 다시 실행하십시오.

---

## 5. 코드 배포 (스크립트 3)

**`3-Deploy_Demo.bat`을 더블 클릭합니다** — 자동으로 다음을 수행합니다:

1. dora 데몬 시작 (`dora up`)
2. Python 3.12 venv 생성 (`uv venv --python 3.12`)
3. venv 활성화
4. AHControl Rust 노드 빌드 (`cargo build --release`, 최초 약 10분)
5. AHSimulation 및 HandTracking 의존성 동기화 (`uv sync`)
6. mediapipe==0.10.14 강제 설치 (알려진 문제, 폴백)

> 한 번만 배포하십시오. 다시 실행하면 venv를 재빌드할지 묻습니다.

---

## 6. Demo 실행 (스크립트 4)

**`4-Run_Demo.bat`을 더블 클릭합니다** — 대화형 메뉴:

```
============================================
  Select a run mode:
============================================
   1 - Simulation (webcam hand tracking)
   2 - Real hardware
   q - Quit
============================================
Enter number [1/2/q]:
```

- **1**: 시뮬레이션 — 웹캠 제스처로 두 개의 시뮬레이션 손을 구동
- **2**: 실물 하드웨어 — 오른손 / 왼손 / 양손 서브메뉴

```
============================================
  Real hardware - select the hand:
============================================
   1 - Right hand
   2 - Left hand
   3 - Both hands
   b - Back to main menu
============================================
```

그런 다음 `dora build` + `dora run`을 실행합니다. 카메라 창이 열리며, 손 제스처를 취하면 실시간으로 손이 움직입니다. **중지하려면 Ctrl+C**. dataflow가 끝난 후 Enter를 누르면 메뉴로 돌아가 다른 모드를 선택하거나 `q`로 종료할 수 있습니다.

> 최초 실행 시 Windows가 카메라 권한을 요청할 수 있습니다 — "Allow"를 클릭하십시오.

---

## 7. 프로젝트 정리 (스크립트 0)

**`0-Cleanup_Project.bat`을 더블 클릭하고** `Y`를 입력하여 확인합니다:

1. dora 데몬 중지
2. 3개의 가상 환경 삭제 (`.venv`)
3. Rust 빌드 출력 삭제 (`Demo\target`)
4. `__pycache__`, `.bak` 백업, 로그, `Demo\out`(dora 로그) 삭제
5. **기본 포트 복원** (`--serialport /dev/ttyACM0`) — 이 머신의 COM 잔여 설정 제거

> 정리 후에는 `AmazingHand-main` 폴더 전체를 다른 머신으로 복사할 수 있습니다 — 깨끗하고 이식 가능합니다.
> 새 머신에서는 1 → 2 → 3 → 4를 순서대로 실행하기만 하면 됩니다.

---

## 8. 문제 해결 및 참고 사항

### 8.1 cargo가 `Updating 'tuna' index`에서 멈춤

- 원인: 미러가 **git-repo 모드**(`.../git/crates.io-index.git`)로 설정되어 첫 실행 시 1 GB 이상의 인덱스를 다운로드
- 해결: `C:\Users\<you>\.cargo\config.toml`을 **sparse 인덱스**로 설정하거나(2.3 참조) `1-Install_Env.bat`을 다시 실행

### 8.2 mediapipe solutions 서브모듈 누락 / 설치 손상

```bat
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- 활성화된 venv 안에서 실행합니다(`Demo` 폴더에서)
- `3-Deploy_Demo.bat`이 이미 폴백으로 이 작업을 수행합니다

### 8.3 dora 버전 불일치 (message v0.8.0 vs v0.7.0)

- 증상: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- 원인: dora-cli 버전이 dora-node-api와 다름. **둘 다 0.5.0이어야 합니다**
  - 확인: `dora --version`이 `dora-cli 0.5.0`과 `dora-message: 0.8.0`을 출력해야 합니다
  - 해결: `cargo install dora-cli --version 0.5.0 --force`
  - `1-Install_Env.bat`이 이제 구버전을 자동 감지하여 0.5.0을 강제 설치합니다

### 8.4 MuJoCo / mediapipe 모델 로드 실패 (중국어 경로)

- 증상: `ParseXML: Error opening file '...\scene.xml'` 또는 `Can't find file: ...\.tflite`
- 원인: MuJoCo 3.x / mediapipe C++ 로더가 **비 ASCII(중국어) 문자가 포함된 절대 경로**에서 실패합니다(예: `D:\Claude工作区\...`)
- 이 프로젝트에는 이미 수정 사항이 포함되어 있습니다:
  - `AHSimulation\AHSimulation\mj_mink_*.py`는 로드 전에 작업 디렉터리를 전환합니다
  - `HandTracking\mediapipe_patch.py`는 8.3 단축 경로 + 상대 경로를 사용합니다
- **이 수정 파일들을 삭제하지 마십시오**

### 8.5 카메라 권한

- 최초 실행: "Allow" 선택
- Settings → Privacy → Camera → 데스크톱 앱 허용

### 8.6 포트 번호가 매번 바뀜

- USB를 다시 꽂으면 COM 번호가 바뀔 수 있습니다 — `2-Setup_Serial.bat`을 다시 실행하십시오

### 8.7 OpenCV 누락

```bat
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(`HandTracking` 폴더에서, venv 활성화 상태)

---

## 9. 코드 구조

### Demo 폴더

| 경로 | 설명 |
|---|---|
| `AHControl` | 서보를 제어하는 Rust 노드. 진입점: `src/main.rs` |
| `AHSimulation` | Python 노드: MuJoCo 시뮬레이션 + 역기구학(mink) |
| `HandTracking` | Python 노드: MediaPipe 핸드 트래킹 |
| `dataflow_*.yml` | dora dataflow 정의(노드 그래프) |
| `Windows_Deploy_Scripts` | 이 스크립트 묶음 |

### dataflow 파일

| 파일 | 용도 |
|---|---|
| `dataflow_tracking_simu.yml` | 시뮬레이션: 웹캠 제스처 → 시뮬레이션 손 |
| `dataflow_tracking_real_right.yml` | 실물 오른손 |
| `dataflow_tracking_real_left.yml` | 실물 왼손 |
| `dataflow_tracking_real_2hands.yml` | 실물 양손(동일 드라이버 보드) |

### dataflow 원리

```
Webcam → HandTracking (MediaPipe hand detection)
              ↓ hand keypoints
         AHSimulation (MuJoCo simulation + IK)
              ↓ joint target angles
         AHControl (serial → servo driver board → hand)
```

### 포트 설정 위치

- 3개의 `dataflow_tracking_real_*.yml` 파일의 `args:` 줄: `--serialport COMxx`
- `AHControl\src\main.rs`의 `default_value = "COMxx"`(직렬 포트 기본값)
- `AHControl\config\*.toml`: 서보 모델, ID, 오프셋(보통 변경 불필요)
