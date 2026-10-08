# AmazingHand 灵巧手手势追踪 · Windows 使用教程

本教程基于 AmazingHand（Pollen Robotics 灵巧手）官方 Demo，已配好一键部署脚本。
按编号顺序执行即可。**所有脚本都位于 `Demo\Windows一键部署脚本\` 文件夹下，直接双击运行。**

---

## 目录

1. [硬件准备](#1-硬件准备)
2. [环境安装（脚本 1）](#2-环境安装脚本-1)
3. [接线方式](#3-接线方式)
4. [配置串口（脚本 2）](#4-配置串口脚本-2)
5. [代码部署（脚本 3）](#5-代码部署脚本-3)
6. [运行代码（脚本 4）](#6-运行代码脚本-4)
7. [项目清理（脚本 0）](#7-项目清理脚本-0)
8. [常见问题与注意事项](#8-常见问题与注意事项)
9. [代码结构说明](#9-代码结构说明)

---

## 1. 硬件准备

| 硬件 | 要求 |
|---|---|
| 灵巧手本体 | 右手 / 左手 / 双手 |
| 舵机驱动板 | 外接，USB 连电脑 |
| 电源 | **至少 5V 4A**（USB 供电不足，必须外接电源） |
| 摄像头 | 电脑自带或 USB 摄像头 |

> 模型文件可在 [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e) 查看或下载（含 URDF）。

---

## 2. 环境安装（脚本 1）

**双击 `1-安装环境.bat`**，自动完成：

1. **检查 MSVC 构建工具**（cl.exe）——Rust 编译必需。缺失时会提示安装
   Visual Studio 2022 Build Tools，勾选"使用 C++ 的桌面开发"，装完重开终端。
2. **安装 Rust**（rustup + stable-msvc 工具链）
3. **配置 cargo 清华镜像源**（`C:\Users\你的用户名\.cargo\config.toml`），加速 crate 下载
4. **安装 uv**（Python 包管理器）
5. **安装 dora-cli 0.5.0**（`cargo install`，首次编译约 10~20 分钟，耐心等待）
6. **安装 dora-rs pip 包**（可选，会装进虚拟环境）

> **重要**：脚本结束后**关闭并重新打开终端**，让环境变量生效。安装过程可能因网络较慢，请耐心等待，不要中途关闭。

### 手动安装备选（脚本不可用时）

- **Rust**：<https://www.rust-lang.org/tools/install>
  - Windows 用 rustup-init.exe，选默认 MSVC 工具链
  - 环境变量：`%USERPROFILE%\.cargo\bin` 加入 PATH
- **uv**：PowerShell 执行 `irm https://astral.sh/uv/install.ps1 | iex`
  - 环境变量：`%USERPROFILE%\.local\bin` 加入 PATH
- **dora-cli**：`cargo install dora-cli --version 0.5.0`

### cargo 清华镜像（~/.cargo/config.toml）

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

> 用 **sparse 稀疏索引**（如上），不要用 git 仓库镜像——git 方式首次要下载约 1GB 索引，容易卡死在 `Updating 'tuna' index`。

---

## 3. 接线方式

- 舵机驱动板 USB 连电脑，**外接 5V4A 电源**
- 电脑端找到端口号：**设备管理器 → 端口(COM和LPT)**，如 `COM11`

---

## 4. 配置串口（脚本 2）

**双击 `2-配置串口.bat`**（实际逻辑在 `2-配置串口.ps1`）：

1. 提示"请将舵机驱动板连接到电脑"→ 回车开始检测
2. 自动列出检测到的 COM 端口（带设备名）
3. 单个端口时回车确认，多个端口时输入编号
4. 自动写入 3 个 dataflow yml 的 `--serialport` 和 `AHControl\src\main.rs` 的默认端口
5. 原文件自动备份为 `.bak`

> 如果重新插拔 USB，端口号可能变化，需重新运行本脚本。

---

## 5. 代码部署（脚本 3）

**双击 `3-部署代码.bat`**，自动完成：

1. 启动 dora 守护进程（`dora up`）
2. 创建 Python 3.12 虚拟环境（`uv venv --python 3.12`）
3. 激活虚拟环境
4. 编译 AHControl Rust 节点（`cargo build --release`，首次约 10 分钟）
5. 同步 AHSimulation、HandTracking 依赖（`uv sync`）
6. 强制安装 mediapipe==0.10.14

> 部署只需执行一次。之后重复运行会提示是否重建虚拟环境。

---

## 6. 运行代码（脚本 4）

**双击 `4-运行代码.bat`**，出现交互菜单：

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

- 选 **1**：模拟环境，摄像头手势驱动两只仿真手
- 选 **2**：进入子菜单，选右手 / 左手 / 双手

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

选好后自动执行 `dora build` + `dora run`。摄像头窗口弹出，对着摄像头做手势，灵巧手实时跟随。**Ctrl+C 停止**，数据流结束后按回车返回主菜单，可再选其它模式或 `q` 退出。

> 首次运行时 Windows 可能拦截摄像头权限，点击"允许"即可。

---

## 7. 项目清理（脚本 0）

**双击 `0-清理项目.bat`**，输入 `Y` 确认后自动清理：

1. 停止 dora 守护进程
2. 删除 3 个虚拟环境（`.venv`）
3. 删除 Rust 编译产物（`Demo\target`）
4. 删除 `__pycache__`、`.bak` 备份、日志、`Demo\out`（dora 日志目录）
5. **恢复默认端口**（`--serialport /dev/ttyACM0`），去掉本机串口残留

> 清理后可把整个 `AmazingHand-main` 文件夹拷给他人，干净无残留。新机器上按 1 → 2 → 3 → 4 顺序执行即可。

---

## 8. 常见问题与注意事项

### 8.1 cargo 卡在 `Updating 'tuna' index`

- 原因：镜像配置用了 **git 仓库方式**（`.../git/crates.io-index.git`），首次要下载 1GB+ 索引
- 解决：`C:\Users\你的用户名\.cargo\config.toml` 改为 **sparse 稀疏索引**（见 2.2 节），或直接重跑 `1-安装环境.bat`

### 8.2 mediapipe 缺 solutions 子模块 / 安装损坏

```bat
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- 必须在虚拟环境激活状态下执行（在 `Demo` 目录）
- `3-部署代码.bat` 已自动做这一步兜底

### 8.3 dora 版本不兼容（message v0.8.0 vs v0.7.0）

- 症状：`version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- 原因：dora-cli 版本与 dora-node-api 不匹配。**必须统一为 0.5.0**
  - 检查：`dora --version` 应输出 `dora-cli 0.5.0`、`dora-message: 0.8.0`
  - 修复：`cargo install dora-cli --version 0.5.0 --force`
  - 若 PATH 里有多个 dora（如 `C:\Users\xxx\.dora\bin` 的旧版），确保 `.cargo\bin` 排在前面，或删除旧版

### 8.4 MuJoCo / mediapipe 加载模型失败（中文路径）

- 症状：`ParseXML: Error opening file '...\scene.xml'` 或 `Can't find file: ...\.tflite`
- 原因：MuJoCo 3.x / mediapipe 的 C++ 加载器在 Windows 上**打不开含中文的绝对路径**（如 `D:\Claude工作区\...`）
- 本项目已内置修复：
  - `AHSimulation\AHSimulation\mj_mink_*.py` 加载模型前切换工作目录
  - `HandTracking\mediapipe_patch.py` 用 8.3 短路径 + 相对路径绕过
- 不要删除这些修复代码

### 8.5 摄像头权限

- 首次运行弹窗选择"允许"
- 设置 → 隐私 → 相机 → 允许桌面应用访问

### 8.6 端口号每次变化

- 重新插拔 USB 后 COM 号可能变，重跑 `2-配置串口.bat`

### 8.7 缺少 openCV

```bat
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

（在 `HandTracking` 目录、激活虚拟环境后执行）

---

## 9. 代码结构说明

### Demo 目录

| 目录/文件 | 说明 |
|---|---|
| `AHControl` | Rust 节点，控制舵机电机。`src/main.rs` 是入口 |
| `AHSimulation` | Python 节点，MuJoCo 仿真 + 逆运动学（mink） |
| `HandTracking` | Python 节点，MediaPipe 手部追踪 |
| `dataflow_*.yml` | dora 数据流定义（节点连接图） |
| `Windows一键部署脚本` | 本套一键脚本 |

### 各 dataflow 对应关系

| 文件 | 用途 |
|---|---|
| `dataflow_tracking_simu.yml` | 模拟环境，摄像头手势 → 仿真双手 |
| `dataflow_tracking_real_right.yml` | 真机右手 |
| `dataflow_tracking_real_left.yml` | 真机左手 |
| `dataflow_tracking_real_2hands.yml` | 真机双手（连同一驱动板） |

### 数据流原理

```
摄像头 → HandTracking（MediaPipe 识别手势）
              ↓ 手部关键点坐标
         AHSimulation（MuJoCo 仿真 + 逆运动学）
              ↓ 关节目标角度
         AHControl（串口 → 舵机驱动板 → 灵巧手）
```

### 端口配置位置

- 三个 `dataflow_tracking_real_*.yml` 的 `args:` 行：`--serialport COMxx`
- `AHControl\src\main.rs` 的 `default_value = "COMxx"`（串口参数默认值）
- `AHControl\config\*.toml`：舵机型号、ID、偏移量（一般不用改）
