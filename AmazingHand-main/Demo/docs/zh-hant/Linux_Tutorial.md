[English](../en/Linux_Tutorial.md) | [Deutsch](../de/Linux_Tutorial.md) | [Español](../es/Linux_Tutorial.md) | [Français](../fr/Linux_Tutorial.md) | [Italiano](../it/Linux_Tutorial.md) | [日本語](../ja/Linux_Tutorial.md) | [한국어](../ko/Linux_Tutorial.md) | [Português (BR)](../pt-br/Linux_Tutorial.md) | [Português (PT)](../pt-pt/Linux_Tutorial.md) | [简体中文](../zh-hans/Linux_Tutorial.md) | 繁體中文

# AmazingHand 靈巧手手勢追蹤 · Linux (Ubuntu) 使用教學

本教學基於 AmazingHand（Pollen Robotics 靈巧手）官方 Demo，已配好一鍵部署腳本。
按編號順序執行即可。**所有腳本都位於 `Demo/Linux_Deploy_Scripts/` 資料夾下，在終端機中執行 `./脚本名`。**

---

## 目錄

1. [硬體準備](#1-硬體準備)
2. [取得腳本執行權限（重要）](#2-取得腳本執行權限重要)
3. [環境安裝（腳本 1）](#3-環境安裝腳本-1)
4. [接線方式](#4-接線方式)
5. [設定序列埠（腳本 2）](#5-設定序列埠腳本-2)
6. [程式碼部署（腳本 3）](#6-程式碼部署腳本-3)
7. [執行程式碼（腳本 4）](#7-執行程式碼腳本-4)
8. [專案清理（腳本 0）](#8-專案清理腳本-0)
9. [常見問題與注意事項](#9-常見問題與注意事項)
10. [程式碼結構說明](#10-程式碼結構說明)

---

## 1. 硬體準備

| 硬體 | 要求 |
|---|---|
| 靈巧手本體 | 右手 / 左手 / 雙手 |
| 伺服馬達驅動板 | 外接，USB 連電腦 |
| 電源 | **至少 5V 4A**（USB 供電不足，必須外接電源） |
| 攝影機 | 電腦內建或 USB 攝影機 |

> 模型檔案可在 [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e) 查看或下載（含 URDF）。

---

## 2. 取得腳本執行權限（重要）

**腳本從 Windows / 壓縮檔複製到 Linux 後，執行權限（`+x`）會遺失**，直接執行會回報
`Permission denied`。**第一次使用前必須先執行：**

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts"
chmod +x *.sh
```

之後每個腳本就可以用 `./脚本名` 執行了。也可以兩步合一：

```bash
cd "AmazingHand-main/Demo/Linux_Deploy_Scripts" && chmod +x *.sh && ./1-Install_Env.sh
```

> 提示：把 `AmazingHand-main` 複製到 Linux 時，用 **tar** 保留權限最穩：
> `tar czf AmazingHand-main.tar.gz AmazingHand-main`（在 Windows/Linux 任意端打包，Linux 端解壓縮），
> 或解壓縮後統一執行一次 `chmod +x *.sh` 即可。

---

## 3. 環境安裝（腳本 1）

在終端機進入腳本目錄，執行（確保已做過上面第 2 步的 `chmod +x`）：

```bash
cd "Demo/Linux_Deploy_Scripts"
./1-Install_Env.sh
```

自動完成：

1. **安裝 Rust**（rustup + stable 工具鏈）
2. **設定 cargo 清華鏡像源**（`~/.cargo/config.toml`），加速 crate 下載
3. **安裝 uv**（Python 套件管理器）
4. **安裝 dora-cli 0.5.0**（`cargo install`，首次編譯約 10~20 分鐘，耐心等待）
5. **安裝 dora-rs pip 套件**（可選）

> **重要**：腳本結束後**關閉並重新開啟終端機**，讓環境變數生效。若版本號顯示為空，將以下路徑加入 `~/.bashrc`：
>
> ```bash
> export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
> ```

### 手動安裝備選（腳本不可用時）

- **Rust**：
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```
- **uv**：
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **dora-cli**：
  ```bash
  cargo install dora-cli --version 0.5.0
  ```

### cargo 清華鏡像（~/.cargo/config.toml）

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

> 用 **sparse 稀疏索引**（如上），不要用 git 倉庫鏡像——git 方式首次要下載約 1GB 索引，容易卡死在 `Updating 'tuna' index`。

---

## 4. 接線方式

- 伺服馬達驅動板 USB 連電腦，**外接 5V4A 電源**
- 查看連接埠號：
  ```bash
  ls /dev/ttyUSB* /dev/ttyACM*
  ```
  一般為 `/dev/ttyACM0`

---

## 5. 設定序列埠（腳本 2）

**執行 `./2-Setup_Serial.sh`**：

1. 提示"請將伺服馬達驅動板連接到電腦"→ 按 Enter 鍵開始偵測
2. 自動列出偵測到的序列埠（`/dev/ttyACM*` / `/dev/ttyUSB*`）
3. 單個連接埠時按 Enter 鍵確認，多個連接埠時輸入編號
4. 自動寫入 3 個 dataflow yml 的 `--serialport` 和 `AHControl/src/main.rs` 的預設連接埠
5. **自動設定序列埠權限**：
   ```bash
   sudo chmod 666 /dev/ttyACM0
   ```
   建議將目前使用者加入 dialout 群組（免每次輸入密碼，需登出後重新登入）：
   ```bash
   sudo usermod -aG dialout $USER
   ```

> 若在虛擬機裡 `ls /dev/ttyUSB* /dev/ttyACM*` 無結果，請在虛擬機設定中把 USB 裝置連接到虛擬機。

---

## 6. 程式碼部署（腳本 3）

**執行 `./3-Deploy_Demo.sh`**，自動完成：

1. 啟動 dora 常駐程式（`dora up`）
2. 建立 Python 3.12 虛擬環境（`uv venv --python 3.12`）
3. 啟用虛擬環境
4. 編譯 AHControl Rust 節點（`cargo build --release`，首次約 10 分鐘）
5. 同步 AHSimulation、HandTracking 相依套件（`uv sync`）
6. 強制安裝 mediapipe==0.10.14（教學已知坑，兜底）

> 部署只需執行一次。之後重複執行會提示是否重建虛擬環境。

---

## 7. 執行程式碼（腳本 4）

**執行 `./4-Run_Demo.sh`**，出現互動選單：

```
============================================
   请选择运行模式：
============================================
    1 - 模拟仿真（摄像头手势追踪）
    2 - 真实硬件
    q - 退出
============================================
  请输入序号 [1/2/q]:
```

- 選 **1**：模擬環境，攝影機手勢驅動兩隻模擬手
- 選 **2**：進入子選單，選右手 / 左手 / 雙手

```
============================================
   真实硬件 - 请选择灵巧手：
============================================
    1 - 右手
    2 - 左手
    3 - 左右双手
    b - 返回上级菜单
============================================
```

選好後自動執行 `dora build` + `dora run`。攝影機視窗彈出，對著攝影機做手勢，靈巧手即時跟隨。**Ctrl+C 停止**，資料流結束後按 Enter 鍵返回主選單，可再選其它模式或 `q` 結束。

> Linux 桌面需要攝影機權限（如 Ubuntu 的隱私設定 → 相機），並確認攝影機未被其它應用占用。
> 虛擬機裡攝影機打不開見 [9.6 攝影機權限 / 虛擬機打不開攝影機](#96-攝影機權限--虛擬機打不開攝影機)。

---

## 8. 專案清理（腳本 0）

**執行 `./0-Cleanup_Project.sh`**，輸入 `Y` 確認後自動清理：

1. 停止 dora 常駐程式
2. 刪除 3 個虛擬環境（`.venv`）
3. 刪除 Rust 編譯產物（`Demo/target`）
4. 刪除 `__pycache__`、`.bak` 備份、日誌、`Demo/out`（dora 日誌目錄）
5. **還原預設連接埠**（`--serialport /dev/ttyACM0`），去掉本機序列埠殘留

> 清理後可把整個 `AmazingHand-main` 資料夾複製給他人，乾淨無殘留。新機器上按 1 → 2 → 3 → 4 順序執行即可。

---

## 9. 常見問題與注意事項

### 9.1 `Permission denied`（腳本沒有執行權限）

- 症狀：執行 `./1-Install_Env.sh` 時回報 `bash: ./1-Install_Env.sh: Permission denied`
- 原因：腳本從 Windows / 壓縮檔複製到 Linux 後**執行位遺失**
- 解決：給所有腳本加執行權限
  ```bash
  chmod +x *.sh
  ```
  然後用 `./脚本名` 執行（不要用 `bash 脚本名`，會跳過本教學第 2 步的互動提示）

### 9.2 cargo 卡在 `Updating 'tuna' index`

- 原因：鏡像設定用了 **git 倉庫方式**（`.../git/crates.io-index.git`），首次要下載 1GB+ 索引
- 解決：`~/.cargo/config.toml` 改為 **sparse 稀疏索引**（見 3.2 節），或直接重跑 `1-Install_Env.sh`

### 9.3 mediapipe 缺 solutions 子模組 / 安裝損壞

```bash
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- 必須在虛擬環境啟用狀態下執行（在 `Demo` 目錄）
- `3-Deploy_Demo.sh` 已自動做這一步兜底

### 9.4 dora 版本不相容（message v0.8.0 vs v0.7.0）

- 症狀：`version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- 原因：dora-cli 版本與 dora-node-api 不相符。**必須統一為 0.5.0**
  - 檢查：`dora --version` 應輸出 `dora-cli 0.5.0`、`dora-message: 0.8.0`
  - `1-Install_Env.sh` 現在會**自動偵測版本**：不是 0.5.0 就清理並強制重裝

**如果系統裡殘留舊版 dora（如 0.4.1），先手動清理再重裝：**

```bash
# 1. 定位旧版 dora 在哪
which dora
ls -la ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora 2>/dev/null

# 2. 删除找到的旧版（按实际路径删，可能多个）
rm -f ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora

# 3. 强制安装 0.5.0（装到 ~/.cargo/bin）
cargo install dora-cli --version 0.5.0 --force

# 4. 确认版本（应输出 dora-cli 0.5.0 / dora-message: 0.8.0）
dora --version
```

> 若 `dora --version` 仍顯示舊版，說明 PATH 裡還有其它位置藏了舊 dora，用 `which dora` 逐個排查刪除，並確保 `~/.cargo/bin` 在 PATH 靠前。

### 9.5 序列埠無權限（Permission denied）

```bash
sudo chmod 666 /dev/ttyACM*
```

- 每次重新插拔可能權限重置
- 根治：`sudo usermod -aG dialout $USER`，登出後重新登入

### 9.6 攝影機權限 / 虛擬機打不開攝影機

**實體機**：
- Ubuntu：設定 → 隱私 → 相機 → 允許應用程式存取
- 確認攝影機未被其它應用（相機 App、Zoom 等）占用

**虛擬機（VMware）打不開攝影機**：

症狀：`open VIDEOIO(V4L2:/dev/video0): can't open camera by index` 或 `select() timeout`，
而 `ls /dev/video0` 存在、`v4l2-ctl` 能抓幀，但 OpenCV `cap.read()` 一直 `ret = False`。

排查與解決（按順序）：

1. **把攝影機轉發進虛擬機**：選單 → 虛擬機 → 可移除式裝置 → 攝影機 → 連接
2. **切換 USB 控制器版本（VMware 常見解法，最有效）**：
   - 虛擬機 → 設定 → **USB 控制器** → 切換 `USB 2.0` / `USB 3.1`
   - 切換後**重新啟動虛擬機**再試
3. 驗證裝置存在：
   ```bash
   ls -l /dev/video0
   sudo usermod -aG video $USER   # 加入 video 组，注销重登
   ```
4. 用 v4l2 驗證攝影機是否真的能出幀（能出幀 = 驅動正常，問題在 OpenCV 相容性）：
   ```bash
   v4l2-ctl --device=/dev/video0 --set-fmt-video=width=640,height=480,pixelformat=MJPG --stream-mmap --stream-count=1 --stream-to=/tmp/frame.jpg
   ls -l /tmp/frame.jpg   # 有几十~几百KB = 流通
   ```

### 9.7 連接埠號每次變動

- 重新插拔 USB 後裝置號可能變，重跑 `2-Setup_Serial.sh`

### 9.8 缺少 openCV

```bash
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

（在 `HandTracking` 目錄、啟用虛擬環境後執行）

---

## 10. 程式碼結構說明

### Demo 目錄

| 目錄/檔案 | 說明 |
|---|---|
| `AHControl` | Rust 節點，控制伺服馬達。`src/main.rs` 是入口 |
| `AHSimulation` | Python 節點，MuJoCo 模擬 + 逆運動學（mink） |
| `HandTracking` | Python 節點，MediaPipe 手部追蹤 |
| `dataflow_*.yml` | dora 資料流定義（節點連接圖） |
| `Linux_Deploy_Scripts` | 本套一鍵腳本 |

### 各 dataflow 對應關係

| 檔案 | 用途 |
|---|---|
| `dataflow_tracking_simu.yml` | 模擬環境，攝影機手勢 → 模擬雙手 |
| `dataflow_tracking_real_right.yml` | 實機右手 |
| `dataflow_tracking_real_left.yml` | 實機左手 |
| `dataflow_tracking_real_2hands.yml` | 實機雙手（連同一驅動板） |

### 資料流原理

```
摄像头 → HandTracking（MediaPipe 识别手势）
              ↓ 手部关键点坐标
         AHSimulation（MuJoCo 仿真 + 逆运动学）
              ↓ 关节目标角度
         AHControl（串口 → 舵机驱动板 → 灵巧手）
```

### 連接埠設定位置

- 三個 `dataflow_tracking_real_*.yml` 的 `args:` 行：`--serialport /dev/ttyACMx`
- `AHControl/src/main.rs` 的 `default_value = "/dev/ttyACM0"`（序列埠參數預設值）
- `AHControl/config/*.toml`：伺服馬達型號、ID、偏移量（一般不用改）
