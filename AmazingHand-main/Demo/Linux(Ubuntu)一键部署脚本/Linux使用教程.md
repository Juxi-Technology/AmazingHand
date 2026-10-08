# AmazingHand 灵巧手手势追踪 · Linux (Ubuntu) 使用教程

本教程基于 AmazingHand（Pollen Robotics 灵巧手）官方 Demo，已配好一键部署脚本。
按编号顺序执行即可。**所有脚本都位于 `Demo/Linux(Ubuntu)一键部署脚本/` 文件夹下，在终端中执行 `./脚本名`。**

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
| 摄像头 | 电脑自带或 USB 摄像头 |

> 模型文件可在 [Onshape](https://cad.onshape.com/documents/430ff184cf3dd9557aaff2be/w/e3658b7152c139971d22c688/e/d79fbb3641873de0a515037e) 查看或下载（含 URDF）。

---

## 2. 获取脚本执行权限（重要）

**脚本从 Windows / 压缩包拷贝到 Linux 后，执行权限（`+x`）会丢失**，直接运行会报
`Permission denied`。**第一次使用前必须先执行：**

```bash
cd "AmazingHand-main/Demo/Linux(Ubuntu)一键部署脚本"
chmod +x *.sh
```

之后每个脚本就可以用 `./脚本名` 运行了。也可以两步合一：

```bash
cd "AmazingHand-main/Demo/Linux(Ubuntu)一键部署脚本" && chmod +x *.sh && ./1-安装环境.sh
```

> 提示：把 `AmazingHand-main` 拷到 Linux 时，用 **tar** 保留权限最稳：
> `tar czf AmazingHand-main.tar.gz AmazingHand-main`（在 Windows/Linux 任意端打包，Linux 端解包），
> 或解压后统一执行一次 `chmod +x *.sh` 即可。

---

## 3. 环境安装（脚本 1）

在终端进入脚本目录，执行（确保已做过上面第 2 步的 `chmod +x`）：

```bash
cd "Demo/Linux(Ubuntu)一键部署脚本"
./1-安装环境.sh
```

自动完成：

1. **安装 Rust**（rustup + stable 工具链）
2. **配置 cargo 清华镜像源**（`~/.cargo/config.toml`），加速 crate 下载
3. **安装 uv**（Python 包管理器）
4. **安装 dora-cli 0.5.0**（`cargo install`，首次编译约 10~20 分钟，耐心等待）
5. **安装 dora-rs pip 包**（可选）

> **重要**：脚本结束后**关闭并重新打开终端**，让环境变量生效。若版本号显示为空，将以下路径加入 `~/.bashrc`：
>
> ```bash
> export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
> ```

### 手动安装备选（脚本不可用时）

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
- 查看端口号：
  ```bash
  ls /dev/ttyUSB* /dev/ttyACM*
  ```
  一般为 `/dev/ttyACM0`

---

## 5. 配置串口（脚本 2）

**执行 `./2-配置串口.sh`**：

1. 提示"请将舵机驱动板连接到电脑"→ 回车开始检测
2. 自动列出检测到的串口（`/dev/ttyACM*` / `/dev/ttyUSB*`）
3. 单个端口时回车确认，多个端口时输入编号
4. 自动写入 3 个 dataflow yml 的 `--serialport` 和 `AHControl/src/main.rs` 的默认端口
5. **自动配置串口权限**：
   ```bash
   sudo chmod 666 /dev/ttyACM0
   ```
   建议把当前用户加入 dialout 组（免每次输密码，需注销重登）：
   ```bash
   sudo usermod -aG dialout $USER
   ```

> 若在虚拟机里 `ls /dev/ttyUSB* /dev/ttyACM*` 无结果，请在虚拟机设置中把 USB 设备连接到虚拟机。

---

## 6. 代码部署（脚本 3）

**执行 `./3-部署代码.sh`**，自动完成：

1. 启动 dora 守护进程（`dora up`）
2. 创建 Python 3.12 虚拟环境（`uv venv --python 3.12`）
3. 激活虚拟环境
4. 编译 AHControl Rust 节点（`cargo build --release`，首次约 10 分钟）
5. 同步 AHSimulation、HandTracking 依赖（`uv sync`）
6. 强制安装 mediapipe==0.10.14（教程已知坑，兜底）

> 部署只需执行一次。之后重复运行会提示是否重建虚拟环境。

---

## 7. 运行代码（脚本 4）

**执行 `./4-运行代码.sh`**，出现交互菜单：

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

> Linux 桌面需要摄像头权限（如 Ubuntu 的隐私设置 → 相机），并确认摄像头未被其它应用占用。
> 虚拟机里摄像头打不开见 [9.6 摄像头权限 / 虚拟机打不开摄像头](#96-摄像头权限--虚拟机打不开摄像头)。

---

## 8. 项目清理（脚本 0）

**执行 `./0-清理项目.sh`**，输入 `Y` 确认后自动清理：

1. 停止 dora 守护进程
2. 删除 3 个虚拟环境（`.venv`）
3. 删除 Rust 编译产物（`Demo/target`）
4. 删除 `__pycache__`、`.bak` 备份、日志、`Demo/out`（dora 日志目录）
5. **恢复默认端口**（`--serialport /dev/ttyACM0`），去掉本机串口残留

> 清理后可把整个 `AmazingHand-main` 文件夹拷给他人，干净无残留。新机器上按 1 → 2 → 3 → 4 顺序执行即可。

---

## 9. 常见问题与注意事项

### 9.1 `Permission denied`（脚本没有执行权限）

- 症状：执行 `./1-安装环境.sh` 时报 `bash: ./1-安装环境.sh: Permission denied`
- 原因：脚本从 Windows / 压缩包拷到 Linux 后**执行位丢失**
- 解决：给所有脚本加执行权限
  ```bash
  chmod +x *.sh
  ```
  然后用 `./脚本名` 运行（不要用 `bash 脚本名`，会跳过本教程第 2 步的交互提示）

### 9.2 cargo 卡在 `Updating 'tuna' index`

- 原因：镜像配置用了 **git 仓库方式**（`.../git/crates.io-index.git`），首次要下载 1GB+ 索引
- 解决：`~/.cargo/config.toml` 改为 **sparse 稀疏索引**（见 3.2 节），或直接重跑 `1-安装环境.sh`

### 9.3 mediapipe 缺 solutions 子模块 / 安装损坏

```bash
uv pip uninstall mediapipe
uv pip install mediapipe==0.10.14
```

- 必须在虚拟环境激活状态下执行（在 `Demo` 目录）
- `3-部署代码.sh` 已自动做这一步兜底

### 9.4 dora 版本不兼容（message v0.8.0 vs v0.7.0）

- 症状：`version mismatch: message format v0.8.0 is not compatible with expected message format v0.7.0`
- 原因：dora-cli 版本与 dora-node-api 不匹配。**必须统一为 0.5.0**
  - 检查：`dora --version` 应输出 `dora-cli 0.5.0`、`dora-message: 0.8.0`
  - `1-安装环境.sh` 现在会**自动检测版本**：不是 0.5.0 就清理并强制重装

**如果系统里残留旧版 dora（如 0.4.1），先手动清理再重装：**

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

> 若 `dora --version` 仍显示旧版，说明 PATH 里还有其它位置藏了旧 dora，用 `which dora` 逐个排查删除，并确保 `~/.cargo/bin` 在 PATH 靠前。

### 9.5 串口无权限（Permission denied）

```bash
sudo chmod 666 /dev/ttyACM*
```

- 每次重新插拔可能权限重置
- 根治：`sudo usermod -aG dialout $USER`，注销重登

### 9.6 摄像头权限 / 虚拟机打不开摄像头

**真实机**：
- Ubuntu：设置 → 隐私 → 相机 → 允许应用访问
- 确认摄像头未被其它应用（相机 App、Zoom 等）占用

**虚拟机（VMware）打不开摄像头**：

症状：`open VIDEOIO(V4L2:/dev/video0): can't open camera by index` 或 `select() timeout`，
而 `ls /dev/video0` 存在、`v4l2-ctl` 能抓帧，但 OpenCV `cap.read()` 一直 `ret = False`。

排查与解决（按顺序）：

1. **把摄像头转发进虚拟机**：菜单 → 虚拟机 → 可移动设备 → 摄像头 → 连接
2. **切换 USB 控制器版本（VMware 常见解法，最有效）**：
   - 虚拟机 → 设置 → **USB 控制器** → 切换 `USB 2.0` / `USB 3.1`
   - 切换后**重启虚拟机**再试
3. 验证设备存在：
   ```bash
   ls -l /dev/video0
   sudo usermod -aG video $USER   # 加入 video 组，注销重登
   ```
4. 用 v4l2 验证摄像头是否真的能出帧（能出帧 = 驱动正常，问题在 OpenCV 兼容性）：
   ```bash
   v4l2-ctl --device=/dev/video0 --set-fmt-video=width=640,height=480,pixelformat=MJPG --stream-mmap --stream-count=1 --stream-to=/tmp/frame.jpg
   ls -l /tmp/frame.jpg   # 有几十~几百KB = 流通
   ```

### 9.7 端口号每次变化

- 重新插拔 USB 后设备号可能变，重跑 `2-配置串口.sh`

### 9.8 缺少 openCV

```bash
python -m pip install opencv-contrib-python numpy mediapipe -i https://mirrors.aliyun.com/pypi/simple/
```

（在 `HandTracking` 目录、激活虚拟环境后执行）

---

## 10. 代码结构说明

### Demo 目录

| 目录/文件 | 说明 |
|---|---|
| `AHControl` | Rust 节点，控制舵机电机。`src/main.rs` 是入口 |
| `AHSimulation` | Python 节点，MuJoCo 仿真 + 逆运动学（mink） |
| `HandTracking` | Python 节点，MediaPipe 手部追踪 |
| `dataflow_*.yml` | dora 数据流定义（节点连接图） |
| `Linux(Ubuntu)一键部署脚本` | 本套一键脚本 |

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

- 三个 `dataflow_tracking_real_*.yml` 的 `args:` 行：`--serialport /dev/ttyACMx`
- `AHControl/src/main.rs` 的 `default_value = "/dev/ttyACM0"`（串口参数默认值）
- `AHControl/config/*.toml`：舵机型号、ID、偏移量（一般不用改）
