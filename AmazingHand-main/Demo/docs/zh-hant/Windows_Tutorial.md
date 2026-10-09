[English](../en/Windows_Tutorial.md) | [Deutsch](../de/Windows_Tutorial.md) | [Español](../es/Windows_Tutorial.md) | [Français](../fr/Windows_Tutorial.md) | [Italiano](../it/Windows_Tutorial.md) | [日本語](../ja/Windows_Tutorial.md) | [한국어](../ko/Windows_Tutorial.md) | [Português (BR)](../pt-br/Windows_Tutorial.md) | [Português (PT)](../pt-pt/Windows_Tutorial.md) | [简体中文](../zh-hans/Windows_Tutorial.md) | 繁體中文

# AmazingHand 靈巧手手勢追蹤 · Windows 使用教學

本教學基於 AmazingHand（Pollen Robotics 靈巧手）官方 Demo，已配好一鍵部署腳本。
按編號順序執行即可。**所有腳本都位於 `Demo\Windows_Deploy_Scripts\` 資料夾下，直接雙擊執行。**

---

## 目錄

1. [硬體準備](#1-硬體準備)
2. [環境安裝（腳本 1）](#2-環境安裝腳本-1)
3. [接線方式](#3-接線方式)
4. [設定序列埠（腳本 2）](#4-設定序列埠腳本-2)
5. [程式碼部署（腳本 3）](#5-程式碼部署腳本-3)
6. [執行程式碼（腳本 4）](#6-執行程式碼腳本-4)
7. [專案清理（腳本 0）](#7-專案清理腳本-0)
8. [常見問題與注意事項](#8-常見問題與注意事項)
9. [程式碼結構說明](#9-程式碼結構說明)

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

## 2. 環境安裝（腳本 1）

**雙擊 `1-Install_Env.bat`**，自動完成：

1. **檢查 MSVC 建置工具**（cl.exe）——Rust 編譯必需。缺失時會提示安裝
   Visual Studio 2022 Build Tools，勾選"使用 C++ 的桌面開發"，裝完重開終端機。
2. **安裝 Rust**（rustup + stable-msvc 工具鏈）
3. **設定 cargo 清華鏡像源**（`C:\Users\你的用户名\.cargo\config.toml`），加速 crate 下載
4. **安裝 uv**（Python 套件管理器）
5. **安裝 dora-cli 0.5.0**（`cargo install`，首次編譯約 10~20 分鐘，耐心等待）
6. **安裝 dora-rs pip 套件**（可選，會裝進虛擬環境）

> **重要**：腳本結束後**關閉並重新開啟終端機**，讓環境變數生效。安裝過程可能因網路較慢，請耐心等待，不要中途關閉。

### 手動安裝備選（腳本不可用時）

- **Rust**：<https://www.rust-lang.org/tools/install>
  - Windows 用 rustup-init.exe，選預設 MSVC 工具鏈
  - 環境變數：`%USERPROFILE%\.cargo\bin` 加入 PATH
- **uv**：PowerShell 執行 `irm https://astral.sh/uv/install.ps1 | iex`
  - 環境變數：`%USERPROFILE%\.local\bin` 加入 PATH
- **dora-cli**：`cargo install dora-cli --version 0.5.0`

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

## 3. 接線方式

- 伺服馬達驅動板 USB 連電腦，**外接 5V4A 電源**
- 電腦端找到連接埠號：**裝置管理員 → 連接埠(COM和LPT)**，如 `COM11`

---

## 4. 設定序列埠（腳本 2）

**雙擊 `2-Setup_Serial.bat`**（實際邏輯在 `2-Setup_Serial.ps1`）：

1. 提示"請將伺服馬達驅動板連接到電腦"→ 按 Enter 鍵開始偵測
2. 自動列出偵測到的 COM 連接埠（帶裝置名稱）
3. 單個連接埠時按 Enter 鍵確認，多個連接埠時輸入編號
4. 自動寫入 3 個 dataflow yml 的 `--serialport` 和 `AHControl\src\main.rs` 的預設連接埠
5. 原始檔案自動備份為 `.bak`

> 如果重新插拔 USB，連接埠號可能變化，需重新執行本腳本。

---

## 5. 程式碼部署（腳本 3）

**雙擊 `3-Deploy_Demo.bat`**，自動完成：

1. 啟動 dora 常駐程式（`dora up`）
2. 建立 Python 3.12 虛擬環境（`uv venv --python 3.12`）
3. 啟用虛擬環境
4. 編譯 AHControl Rust 節點（`cargo build --release`，首次約 10 分鐘）
5. 同步 AHSimulation、HandTracking 相依套件（`uv sync`）
6. 強制安裝 mediapipe==0.10.14

> 部署只需執行一次。之後重複執行會提示是否重建虛擬環境。

---

## 6. 執行程式碼（腳本 4）

**雙擊 `4-Run_Demo.bat`**，出現互動選單：

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

> 首次執行時 Windows 可能攔截攝影機權限，點擊"允許"即可。

---

## 7. 專案清理（腳本 0）

**雙擊 `0-Cleanup_Project.bat`**，輸入 `Y` 確認後自動清理：

1. 停止 dora 常駐程式
2. 刪除 3 個虛擬環境（`.venv`）
3. 刪除 Rust 編譯產物（`Demo\target`）
4. 刪除 `__pycache__`、`.bak` 備份、日誌、`Demo\out`（dora 日誌目錄）
5. **還原預設連接埠**（`--serialport /dev/ttyACM0`），去掉本機序列埠殘留

> 清理後可把整個 `AmazingHand-main` 資料夾複製給他人，乾淨無殘留。新機器上按 1 → 2 → 3 → 4 順序執行即可。

---

## 8. 常見問題與注意事項

### 8.1 cargo 卡在 `Updating 'tuna' index`

- 原因：鏡像設定用了 **git 倉庫方式**（`.../git/crates.io-index.git`），首次要下載 1GB+ 索引
- 解決：`C:\Users\你的用户名\.cargo\config.toml` 改為 **sparse 稀疏索引**（見 2.2 節），或直接重跑 `1-Install_Env.bat`

### 8.2 mediapipe 缺 solutions 子模組 / 安裝損壞

```bat
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- 必須在虛擬環境啟用狀態下執行（在 `Demo` 目錄）
- `3-Deploy_Demo.bat` 已自動做這一步兜底

### 8.3 dora 版本不相容（message v0.8.0 vs v0.7.0）

- 症狀：`version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- 原因：dora-cli 版本與 dora-node-api 不相符。**必須統一為 0.5.0**
  - 檢查：`dora --version` 應輸出 `dora-cli 0.5.0`、`dora-message: 0.8.0`
  - 修復：`cargo install dora-cli --version 0.5.0 --force`
  - 若 PATH 裡有多個 dora（如 `C:\Users\xxx\.dora\bin` 的舊版），確保 `.cargo\bin` 排在前面，或刪除舊版

### 8.4 MuJoCo / mediapipe 載入模型失敗（中文路徑）

- 症狀：`ParseXML: Error opening file '...\scene.xml'` 或 `Can't find file: ...\.tflite`
- 原因：MuJoCo 3.x / mediapipe 的 C++ 載入器在 Windows 上**打不開含中文的絕對路徑**（如 `D:\Claude工作区\...`）
- 本專案已內建修復：
  - `AHSimulation\AHSimulation\mj_mink_*.py` 載入模型前切換工作目錄
  - `HandTracking\mediapipe_patch.py` 用 8.3 短路徑 + 相對路徑繞過
- 不要刪除這些修復程式碼

### 8.5 攝影機權限

- 首次執行彈出視窗選擇"允許"
- 設定 → 隱私 → 相機 → 允許桌面應用程式存取

### 8.6 連接埠號每次變動

- 重新插拔 USB 後 COM 號可能變，重跑 `2-Setup_Serial.bat`

### 8.7 缺少 openCV

```bat
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

（在 `HandTracking` 目錄、啟用虛擬環境後執行）

---

## 9. 程式碼結構說明

### Demo 目錄

| 目錄/檔案 | 說明 |
|---|---|
| `AHControl` | Rust 節點，控制伺服馬達。`src/main.rs` 是入口 |
| `AHSimulation` | Python 節點，MuJoCo 模擬 + 逆運動學（mink） |
| `HandTracking` | Python 節點，MediaPipe 手部追蹤 |
| `dataflow_*.yml` | dora 資料流定義（節點連接圖） |
| `Windows_Deploy_Scripts` | 本套一鍵腳本 |

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

- 三個 `dataflow_tracking_real_*.yml` 的 `args:` 行：`--serialport COMxx`
- `AHControl\src\main.rs` 的 `default_value = "COMxx"`（序列埠參數預設值）
- `AHControl\config\*.toml`：伺服馬達型號、ID、偏移量（一般不用改）
