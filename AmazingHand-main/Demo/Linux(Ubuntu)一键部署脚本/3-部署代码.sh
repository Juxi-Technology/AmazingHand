#!/usr/bin/env bash
# AmazingHand Demo 一键部署 (Linux)
# 需先运行 1-安装环境.sh 完成环境安装
set -e
cd "$(dirname "$0")"

echo "============================================"
echo "  AmazingHand Demo 一键部署 (Linux)"
echo "  需要先完成 1-安装环境.sh 环境安装"
echo "============================================"
echo

export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# 校验必需命令
for cmd in dora cargo uv; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "  [错误] 缺少命令：$cmd"
        echo "  请先运行 ./1-安装环境.sh 安装环境，并【重新打开终端】后再试。"
        exit 1
    fi
done

# 脚本位于 Demo/Linux(Ubuntu)一键部署脚本 下，上一级即 Demo 目录
cd ..
if [ ! -d "AHControl" ]; then
    echo "  [错误] 未找到 Demo 目录，请确认脚本位于 Demo/Linux(Ubuntu)一键部署脚本 文件夹中。"
    exit 1
fi

# 1. 启动 dora 守护进程
echo "[1/5] 启动 dora 守护进程..."
dora up

# 2. 创建/复用虚拟环境
echo "[2/5] 准备 Python 3.12 虚拟环境..."
if [ -d ".venv" ]; then
    read -r -p "检测到已存在的 .venv，重建会覆盖旧环境，是否重建？[y/N]: " ans
    if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
        echo "  正在删除旧环境并重建..."
        rm -rf .venv
        uv venv --python 3.12
    else
        echo "  复用已有 .venv。"
    fi
else
    echo "  正在创建虚拟环境..."
    uv venv --python 3.12
fi

# 3. 激活虚拟环境
echo "[3/5] 激活虚拟环境..."
# shellcheck source=/dev/null
source .venv/bin/activate

# 4. 编译 AHControl (Rust)
echo "[4/5] 编译 AHControl (cargo build --release，首次约需数分钟)..."
cd AHControl
cargo build --release
cd ..

# 5. 同步 AHSimulation 与 HandTracking 依赖
echo "[5/5] 同步 Python 依赖 (uv sync)..."
echo "  -- AHSimulation --"
cd AHSimulation
uv sync
cd ..
echo "  -- HandTracking --"
cd HandTracking
uv sync
cd ..

# 兜底：强制安装 mediapipe 0.10.14（教程已知坑：版本不兼容/包损坏）
echo "[附加] 校验 mediapipe==0.10.14（教程已知坑点，强制重装兜底）..."
uv pip uninstall -y mediapipe >/dev/null 2>&1 || true
if uv pip install mediapipe==0.10.14; then
    echo "  mediapipe==0.10.14 已就绪。"
else
    echo "  [警告] mediapipe 强制重装失败，可稍后在 HandTracking 目录手动执行："
    echo "  uv pip install mediapipe==0.10.14"
fi

echo
echo "============================================"
echo "  Demo 环境部署完成！"
echo "  以后运行代码请执行：./4-运行代码.sh [simu|right|left|2hands|angle]"
echo "============================================"
echo
