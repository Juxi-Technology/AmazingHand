[English](../en/Mac_Tutorial.md) | [Deutsch](../de/Mac_Tutorial.md) | [Español](../es/Mac_Tutorial.md) | [Français](../fr/Mac_Tutorial.md) | [Italiano](../it/Mac_Tutorial.md) | [日本語](../ja/Mac_Tutorial.md) | [한국어](../ko/Mac_Tutorial.md) | [Português (BR)](../pt-br/Mac_Tutorial.md) | [Português (PT)](../pt-pt/Mac_Tutorial.md) | 简体中文 | [繁體中文](../zh-hant/Mac_Tutorial.md)

# AmazingHand 灵巧手手势追踪 · macOS 使用教程

本教程基于 AmazingHand（Pollen Robotics 灵巧手）官方 Demo，已配好一键部署脚本。
按编号顺序执行即可。**所有脚本都位于 `Demo/Mac_Deploy_Scripts/` 文件夹下，在终端中执行 `./脚本名`。**

---

## 目录

1. [硬件准备](#1-硬件准备)
2. [获取脚本执行权限（重要）](#2-获取脚本执行权限重要)
3. [环境安装（脚本 1）](#3-环境安装脚本-1)
4. [接线方式](#4-接线方式)
5. [配置串口（脚本 2）](#5-配置串口脚本-2)
6. [代码部署（脚本 3）](#6-代码部署脚本-3)
7. [运行代码（脚本 4）](#7-运行代码脚本-4)
8. [项目清理（脚本 0）](#8-项目清理脚本-0)
9. [常见问题与注意事项](#9-常见问题与注意事项)
10. [代码结构说明](#10-代码结构说明)

---

## 1. 硬件准备

| 硬件 | 要求 |
|---|---|
| 灵巧手本体 | 右手 / 左手 / 双手 |
| 舵机驱动板 | 外接，USB 连电脑 |
| 电源 | **至少 5V 4A**（USB 供电不足，必须外接电源） |
| 摄像头 | Mac 自带摄像头或 USB 摄像头 |

> 模型文件可在 [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e) 查看或下载（含 URDF）。
> 支持 Apple Silicon（M1/M2/M3/M4）与 Intel 芯片。

---

## 2. 获取脚本执行权限（重要）

**脚本从 Windows / 压缩包拷贝到 Mac 后，执行权限（`+x`）会丢失**，直接运行会报
`Permission denied`。**第一次使用前必须先执行：**

```bash
cd "AmazingHand-main/Demo/Mac_Deploy_Scripts"
chmod +x *.sh
```

之后每个脚本就可以用 `./脚本名` 运行了。

> 提示：把 `AmazingHand-main` 拷到 Mac 时，用 **tar** 保留权限最稳：
> `tar czf AmazingHand-main.tar.gz AmazingHand-main`，或解压后统一执行一次 `chmod +x *.sh`。

---

## 3. 环境安装（脚本 1）

在终端进入脚本目录，执行（确保已做过上面第 2 步的 `chmod +x`）：

```bash
cd "AmazingHand-main/Demo/Mac_Deploy_Scripts"
./1-Install_Env.sh
```

自动完成：

1. **检查 Xcode 命令行工具**（Rust 编译必需）。缺失时提示 `xcode-select --install`
2. **安装 Rust**（rustup + stable 工具链）
3. **配置 cargo 清华镜像源**（`~/.cargo/config.toml`），加速 crate 下载
4. **安装 uv**（Python 包管理器）
5. **安装 dora-cli 0.5.0**（`cargo install`，首次编译约 10~20 分钟，耐心等待）。自动清理旧版 dora
6. **安装 dora-rs pip 包**（可选）

> **重要**：脚本结束后**关闭并重新打开终端**，让环境变量生效。若版本号显示为空，
> 将以下路径加入 `~/.zshrc`：
>
> ```bash
> export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
> ```

### 手动安装备选（脚本不可用时）

- **Xcode 命令行工具**：`xcode-select --install`
- **Rust**：`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- **uv**：`curl -LsSf https://astral.sh/uv/install.sh | sh`
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

## 4. 接线方式

- 舵机驱动板 USB 连电脑，**外接 5V4A 电源**
- macOS 的 USB 串口设备名是 **`/dev/tty.usbmodem*`** 或 **`/dev/cu.usbmodem*`**（不是 Linux 的 `/dev/ttyACM*`）
- 查看端口：
  ```bash
  ls /dev/tty.usbmodem* /dev/cu.usbmodem*
  ```

---

## 5. 配置串口（脚本 2）

**执行 `./2-Setup_Serial.sh`**：

1. 提示"请将舵机驱动板连接到电脑"→ 回车开始检测
2. 自动列出检测到的串口（`/dev/tty.usbmodem*` / `/dev/cu.usbmodem*` / `*.usbserial*`）
3. 单个端口时回车确认，多个端口时输入编号
4. 自动写入 3 个 dataflow yml 的 `--serialport` 和 `AHControl/src/main.rs` 的默认端口
5. macOS 的 USB 串口通常对用户可读写；若提示无权限，手动执行：
   ```bash
   sudo chmod 666 /dev/cu.usbmodem*
   ```
   或到 **系统设置 → 隐私与安全性 → 输入监控**，允许终端访问。

> 若在虚拟机中，请把 USB 设备连接到虚拟机。

---

## 6. 代码部署（脚本 3）

**执行 `./3-Deploy_Demo.sh`**，自动完成：

1. 启动 dora 守护进程（`dora up`）
2. 创建 Python 3.12 虚拟环境（`uv venv --python 3.12`）
3. 激活虚拟环境
4. 编译 AHControl Rust 节点（`cargo build --release`，首次约 10 分钟）
5. 同步 AHSimulation、HandTracking 依赖（`uv sync`）
6. 强制安装 mediapipe==0.10.14（教程已知坑，兜底）

> 部署只需执行一次。之后重复运行会提示是否重建虚拟环境。

---

## 7. 运行代码（脚本 4）

**执行 `./4-Run_Demo.sh`**，出现交互菜单：

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

> **首次运行 macOS 会弹摄像头授权**：系统设置 → 隐私与安全性 → 相机，允许终端使用摄像头。

---

## 8. 项目清理（脚本 0）

**执行 `./0-Cleanup_Project.sh`**，输入 `Y` 确认后自动清理：

1. 停止 dora 守护进程
2. 删除 3 个虚拟环境（`.venv`）
3. 删除 Rust 编译产物（`Demo/target`）
4. 删除 `__pycache__`、`.bak` 备份、日志、`Demo/out`（dora 日志目录）
5. **恢复默认端口**（`--serialport /dev/ttyACM0`），去掉本机串口残留

> 清理后可把整个 `AmazingHand-main` 文件夹拷给他人，干净无残留。新机器上按 1 → 2 → 3 → 4 顺序执行即可。

---

## 9. 常见问题与注意事项

### 9.1 `Permission denied`（脚本没有执行权限）

- 症状：执行 `./1-Install_Env.sh` 时报 `bash: ./1-Install_Env.sh: Permission denied`
- 原因：脚本从 Windows / 压缩包拷到 Mac 后**执行位丢失**
- 解决：
  ```bash
  chmod +x *.sh
  ```

### 9.2 cargo 卡在 `Updating 'tuna' index`

- 原因：镜像配置用了 **git 仓库方式**（`.../git/crates.io-index.git`），首次要下载 1GB+ 索引
- 解决：`~/.cargo/config.toml` 改为 **sparse 稀疏索引**（见 3.2 节），或直接重跑 `1-Install_Env.sh`

### 9.3 mediapipe 缺 solutions 子模块 / 安装损坏

```bash
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- 必须在虚拟环境激活状态下执行（在 `Demo` 目录）
- `3-Deploy_Demo.sh` 已自动做这一步兜底

### 9.4 dora 版本不兼容（message v0.8.0 vs v0.7.0）

- 症状：`version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- 原因：dora-cli 版本与 dora-node-api 不匹配。**必须统一为 0.5.0**
  - 检查：`dora --version` 应输出 `dora-cli 0.5.0`、`dora-message: 0.8.0`
  - `1-Install_Env.sh` 会自动检测旧版并强制重装

**若系统残留旧版 dora（如 0.4.1），先手动清理：**

```bash
# 1. 定位旧版 dora
which dora
ls -la ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora 2>/dev/null

# 2. 删除找到的旧版（按实际路径）
rm -f ~/.cargo/bin/dora ~/.dora/bin/dora ~/.local/bin/dora

# 3. 强制安装 0.5.0
cargo install dora-cli --version 0.5.0 --force

# 4. 确认版本（应输出 dora-cli 0.5.0 / dora-message: 0.8.0）
dora --version
```

> 若 `dora --version` 仍显示旧版，说明 PATH 里还有其它旧 dora，用 `which dora` 逐个排查删除。

### 9.5 串口无权限

```bash
sudo chmod 666 /dev/cu.usbmodem*
```

- 或 **系统设置 → 隐私与安全性 → 输入监控** → 允许终端
- 若用的是 `tty.*` 设备读不了，改用对应的 `cu.*` 设备（cu 设备只读端口，更适合直接控制）

### 9.6 摄像头权限

- **首次运行弹窗选"允许"**，或到 **系统设置 → 隐私与安全性 → 相机**，允许终端使用摄像头
- 确认摄像头未被其它应用（FaceTime、会议软件）占用

### 9.7 端口号每次变化

- 重新插拔 USB 后设备名可能变，重跑 `2-Setup_Serial.sh`

### 9.8 缺少 openCV

```bash
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

（在 `HandTracking` 目录、激活虚拟环境后执行）

### 9.9 Apple Silicon 编译较慢 / 首次运行被 Gatekeeper 拦截

- Apple Silicon 首次 `cargo build` 编译 dora 依赖较慢属正常，耐心等待
- 若提示"无法验证开发者"：系统设置 → 隐私与安全性 → 仍要打开

---

## 10. 代码结构说明

### Demo 目录

| 目录/文件 | 说明 |
|---|---|
| `AHControl` | Rust 节点，控制舵机电机。`src/main.rs` 是入口 |
| `AHSimulation` | Python 节点，MuJoCo 仿真 + 逆运动学（mink） |
| `HandTracking` | Python 节点，MediaPipe 手部追踪 |
| `dataflow_*.yml` | dora 数据流定义（节点连接图） |
| `Mac_Deploy_Scripts` | 本套一键脚本 |

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

- 三个 `dataflow_tracking_real_*.yml` 的 `args:` 行：`--serialport /dev/cu.usbmodem...`
- `AHControl/src/main.rs` 的 `default_value`（串口参数默认值）
- `AHControl/config/*.toml`：舵机型号、ID、偏移量（一般不用改）
