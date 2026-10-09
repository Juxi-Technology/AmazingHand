[English](../en/Linux_Tutorial.md) | [Deutsch](../de/Linux_Tutorial.md) | [Español](../es/Linux_Tutorial.md) | [Français](../fr/Linux_Tutorial.md) | [Italiano](../it/Linux_Tutorial.md) | [日本語](../ja/Linux_Tutorial.md) | 한국어 | [Português (BR)](../pt-br/Linux_Tutorial.md) | [Português (PT)](../pt-pt/Linux_Tutorial.md) | [简体中文](../zh-hans/Linux_Tutorial.md) | [繁體中文](../zh-hant/Linux_Tutorial.md)

# AmazingHand 정교한 로봇 손 핸드 트래킹 · Linux (Ubuntu) 튜토리얼

이 튜토리얼은 AmazingHand(Pollen Robotics의 정교한 로봇 손) 공식 Demo를 원클릭 배포 스크립트와 함께 다룹니다.
스크립트는 번호 순서대로 실행하십시오. **모든 스크립트는 `Demo/Linux_Deploy_Scripts/`에 있으며, 터미널에서 `./script`를 실행합니다.**

---

## 목차

1. [하드웨어 준비](#1-하드웨어-준비)
2. [스크립트 권한 부여 (중요)](#2-스크립트-권한-부여-중요)
3. [환경 설정 (스크립트 1)](#3-환경-설정-스크립트-1)
4. [배선](#4-배선)
5. [시리얼 포트 설정 (스크립트 2)](#5-시리얼-포트-설정-스크립트-2)
6. [코드 배포 (스크립트 3)](#6-코드-배포-스크립트-3)
7. [Demo 실행 (스크립트 4)](#7-demo-실행-스크립트-4)
8. [프로젝트 정리 (스크립트 0)](#8-프로젝트-정리-스크립트-0)
9. [문제 해결 및 참고 사항](#9-문제-해결-및-참고-사항)
10. [코드 구조](#10-코드-구조)

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

## 2. 스크립트 실행 권한 부여 (중요)

**Windows나 zip에서 Linux로 스크립트를 복사하면 실행 권한(`+x`)이 사라집니다** — 그대로 실행하면
`Permission denied`가 발생합니다. **처음 사용하기 전에 한 번 실행하십시오:**

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
chmod +x *.sh
```

그러면 각 스크립트를 `./script`로 실행할 수 있습니다. 또는 다음과 같이 묶어서 실행할 수도 있습니다:

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts" && chmod +x *.sh && ./1-Install_Env.sh
```

> 팁: 권한을 유지한 채 `AmazingHand-main` 폴더를 Linux로 옮기려면 **tar**로 묶으십시오:
> `tar czf AmazingHand-main.tar.gz AmazingHand-main`, 또는 압축을 푼 뒤 `chmod +x *.sh`를 한 번 실행하기만 해도 됩니다.

---

## 3. 환경 설정 (스크립트 1)

스크립트 폴더에서 실행합니다(2단계의 `chmod +x` 이후):

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
./1-Install_Env.sh
```

자동으로 다음을 수행합니다:

1. **Rust 설치** (rustup + stable 툴체인)
2. **cargo tuna 미러 설정** (`~/.cargo/config.toml`) — crate 다운로드 속도 향상
3. **uv 설치** (Python 패키지 관리자)
4. **dora-cli 0.5.0 설치** (`cargo install`, 첫 컴파일은 약 10–20분 소요, 기다려 주십시오). 구버전 dora는 자동으로 감지되어 강제 교체됩니다.
5. **dora-rs pip 패키지 설치** (선택)

> **중요**: 스크립트 실행 후 **터미널을 닫았다가 다시 여십시오**. 그래야 환경 변수가 적용됩니다.
> 버전이 비어 있게 표시되면 `~/.bashrc`에 다음을 추가하십시오:
>
> ```bash
> export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
> ```

### 수동 설치 (스크립트를 사용할 수 없는 경우)

- **Rust**:
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```
- **uv**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **dora-cli**:
  ```bash
  cargo install dora-cli --version 0.5.0
  ```

### cargo tuna 미러 (~/.cargo/config.toml)

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

## 4. 배선

- 서보 드라이버 보드를 USB로 PC에 연결하고, **외부 5V 4A 전원으로 전원을 공급합니다**
- 포트를 찾습니다:
  ```bash
  ls /dev/ttyUSB* /dev/ttyACM*
  ```
  보통 `/dev/ttyACM0`

---

## 5. 시리얼 포트 설정 (스크립트 2)

**`./2-Setup_Serial.sh`를 실행합니다**:

1. "Connect the driver board" → Enter를 눌러 스캔
2. 감지된 시리얼 포트가 나열됩니다 (`/dev/ttyACM*` / `/dev/ttyUSB*`)
3. 포트가 하나면 Enter로 확인하고, 여러 개면 인덱스를 입력합니다
4. 3개의 dataflow yml 파일에 `--serialport`를, `AHControl/src/main.rs`에 기본 포트를 기록합니다
5. **시리얼 권한을 자동으로 설정합니다**:
   ```bash
   sudo chmod 666 /dev/ttyACM0
   ```
   권장: 현재 사용자를 dialout 그룹에 추가합니다(비밀번호 재입력 방지, 적용하려면 로그아웃/로그인):
   ```bash
   sudo usermod -aG dialout $USER
   ```

> VM 안에서 `ls /dev/ttyUSB* /dev/ttyACM*`가 아무것도 찾지 못하면 VM 설정에서 USB 장치를 VM에 연결하십시오.

---

## 6. 코드 배포 (스크립트 3)

**`./3-Deploy_Demo.sh`를 실행합니다** — 자동으로 다음을 수행합니다:

1. dora 데몬 시작 (`dora up`)
2. Python 3.12 venv 생성 (`uv venv --python 3.12`)
3. venv 활성화
4. AHControl Rust 노드 빌드 (`cargo build --release`, 최초 약 10분)
5. AHSimulation 및 HandTracking 의존성 동기화 (`uv sync`)
6. mediapipe==0.10.14 강제 설치 (알려진 문제, 폴백)

> 한 번만 배포하십시오. 다시 실행하면 venv를 재빌드할지 묻습니다.

---

## 7. Demo 실행 (스크립트 4)

**`./4-Run_Demo.sh`를 실행합니다** — 대화형 메뉴:

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

> Linux 데스크톱에는 카메라 권한이 필요합니다(Ubuntu: Settings → Privacy → Camera). 카메라가 다른 앱에서 사용 중이 아닌지 확인하십시오. VM 카메라 문제: [9.6](#96-카메라-권한--가상-머신-카메라가-작동하지-않음)을 참조하십시오.

---

## 8. 프로젝트 정리 (스크립트 0)

**`./0-Cleanup_Project.sh`를 실행하고** `Y`를 입력하여 확인합니다:

1. dora 데몬 중지
2. 3개의 가상 환경 삭제 (`.venv`)
3. Rust 빌드 출력 삭제 (`Demo/target`)
4. `__pycache__`, `.bak` 백업, 로그, `Demo/out`(dora 로그) 삭제
5. **기본 포트 복원** (`--serialport /dev/ttyACM0`) — 이 머신의 포트 잔여 설정 제거

> 정리 후에는 `AmazingHand-main` 폴더 전체를 다른 머신으로 복사할 수 있습니다 — 깨끗하고 이식 가능합니다.
> 새 머신에서는 1 → 2 → 3 → 4를 순서대로 실행하기만 하면 됩니다.

---

## 9. 문제 해결 및 참고 사항

### 9.1 `Permission denied` (스크립트에 실행 권한 없음)

- 증상: `bash: ./1-Install_Env.sh: Permission denied`
- 원인: Windows / zip에서 복사할 때 스크립트의 실행 비트가 사라짐
- 해결:
  ```bash
  chmod +x *.sh
  ```
  그런 다음 `./script`로 실행합니다(`bash script`가 아님).

### 9.2 cargo가 `Updating 'tuna' index`에서 멈춤

- 원인: 미러가 **git-repo 모드**(`.../git/crates.io-index.git`)로 설정되어 첫 실행 시 1 GB 이상의 인덱스를 다운로드
- 해결: `~/.cargo/config.toml`을 **sparse 인덱스**로 설정하거나(3.2 참조) `1-Install_Env.sh`를 다시 실행

### 9.3 mediapipe solutions 서브모듈 누락 / 설치 손상

```bash
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- 활성화된 venv 안에서 실행합니다(`Demo` 폴더에서)
- `3-Deploy_Demo.sh`가 이미 폴백으로 이 작업을 수행합니다

### 9.4 dora 버전 불일치 (message v0.8.0 vs v0.7.0)

- 증상: `version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- 원인: dora-cli 버전이 dora-node-api와 다름. **둘 다 0.5.0이어야 합니다**
  - 확인: `dora --version`이 `dora-cli 0.5.0`과 `dora-message: 0.8.0`을 출력해야 합니다
  - `1-Install_Env.sh`가 이제 구버전을 자동 감지하여 0.5.0을 강제 설치합니다

**구버전 dora(예: 0.4.1)가 시스템에 남아 있다면 먼저 정리하십시오:**

```bash
# 1. Find where the old dora is
which dora
ls -la ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora 2>/dev/null

# 2. Delete the found old versions (adjust paths; there may be several)
rm -f ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora

# 3. Force-install 0.5.0 (goes to ~/.cargo/bin)
cargo install dora-cli --version 0.5.0 --force

# 4. Verify (should print dora-cli 0.5.0 / dora-message: 0.8.0)
dora --version
```

> `dora --version`이 여전히 구버전을 표시하면 PATH 어딘가에 또 다른 구버전 복사본이 숨어 있는 것입니다. `which dora`로 찾아 삭제하고, `~/.cargo/bin`이 PATH 앞부분에 있는지 확인하십시오.

### 9.5 시리얼 포트 권한 거부

```bash
sudo chmod 666 /dev/ttyACM*
```

- 다시 꽂으면 권한이 초기화될 수 있습니다
- 영구 해결: `sudo usermod -aG dialout $USER` 후 로그아웃/로그인

### 9.6 카메라 권한 / 가상 머신 카메라가 작동하지 않음

**실제 머신**:
- Ubuntu: Settings → Privacy → Camera → 앱 허용
- 다른 앱(Camera 앱, Zoom 등)이 웹캠을 사용 중이 아닌지 확인하십시오

**가상 머신(VMware) 카메라가 작동하지 않음**:

증상: `open VIDEOIO(V4L2:/dev/video0): can't open camera by index` 또는 `select() timeout`;
`/dev/video0`이 존재하고 `v4l2-ctl`이 프레임을 캡처하는데도 OpenCV `cap.read()`가 계속 `ret = False`를 반환합니다.

문제 해결(순서대로):

1. **카메라를 VM으로 전달**: Menu → VM → Removable Devices → Camera → Connect
2. **USB 컨트롤러 버전 전환(가장 효과적인 VMware 해결책)**:
   - VM → Settings → **USB Controller** → `USB 2.0` / `USB 3.1` 사이를 전환
   - 전환 후 **VM을 재시작**
3. 장치가 존재하는지 확인:
   ```bash
   ls -l /dev/video0
   sudo usermod -aG video $USER   # add to video group, log out/in
   ```
4. v4l2로 카메라가 실제로 프레임을 생성하는지 확인(가능하다면 드라이버는 정상이며, 문제는 OpenCV 호환성):
   ```bash
   v4l2-ctl --device=/dev/video0 --set-fmt-video=width=640,height=480,pixelformat=MJPG --stream-mmap --stream-count=1 --stream-to=/tmp/frame.jpg
   ls -l /tmp/frame.jpg   # tens to hundreds of KB = stream works
   ```

### 9.7 포트 번호가 매번 바뀜

- USB를 다시 꽂으면 장치 이름이 바뀔 수 있습니다 — `2-Setup_Serial.sh`를 다시 실행하십시오

### 9.8 OpenCV 누락

```bash
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

(`HandTracking` 폴더에서, venv 활성화 상태)

---

## 10. 코드 구조

### Demo 폴더

| 경로 | 설명 |
|---|---|
| `AHControl` | 서보를 제어하는 Rust 노드. 진입점: `src/main.rs` |
| `AHSimulation` | Python 노드: MuJoCo 시뮬레이션 + 역기구학(mink) |
| `HandTracking` | Python 노드: MediaPipe 핸드 트래킹 |
| `dataflow_*.yml` | dora dataflow 정의(노드 그래프) |
| `Linux_Deploy_Scripts` | 이 스크립트 묶음 |

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

- 3개의 `dataflow_tracking_real_*.yml` 파일의 `args:` 줄: `--serialport /dev/ttyACMx`
- `AHControl/src/main.rs`의 `default_value = "/dev/ttyACM0"`(직렬 포트 기본값)
- `AHControl/config/*.toml`: 서보 모델, ID, 오프셋(보통 변경 불필요)
