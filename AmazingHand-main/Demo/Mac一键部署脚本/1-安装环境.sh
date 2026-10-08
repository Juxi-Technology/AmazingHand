#!/usr/bin/env bash
# AmazingHand 环境安装脚本 (macOS)
# 安装 Rust + uv + dora-cli(0.5.0)，配置 cargo 清华镜像源
# 说明：本脚本以 /bin/bash 运行（macOS 自带），依赖 curl / xcode-select 命令行工具
set -e
cd "$(dirname "$0")"

echo "============================================"
echo "  AmazingHand 环境安装脚本 (macOS)"
echo "  Rust + uv + dora-rs 一键安装"
echo "============================================"
echo

# ---------- 0. 检查 Xcode 命令行工具 ----------
echo "[0/6] 检查 Xcode Command Line Tools..."
if ! xcode-select -p >/dev/null 2>&1; then
    echo "    [警告] 未检测到 Xcode Command Line Tools。"
    echo "    请先在终端执行：xcode-select --install"
    echo "    安装完成后重跑本脚本。"
    exit 1
else
    echo "    已检测到 Xcode Command Line Tools。"
fi

# ---------- 1. 安装 Rust ----------
echo "[1/6] 检查 / 安装 Rust (rustup + stable)..."
if command -v rustc >/dev/null 2>&1 || [ -x "$HOME/.cargo/bin/rustc" ]; then
    echo "    已检测到 Rust，跳过安装。"
else
    echo "    正在通过 rustup 安装 Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --profile default
    if [ ! -f "$HOME/.cargo/env" ]; then
        echo "    [错误] rustup 安装失败，请重试或参考 https://www.rust-lang.org/tools/install"
        exit 1
    fi
    echo "    Rust 安装完成。"
fi
# shellcheck source=/dev/null
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
export PATH="$HOME/.cargo/bin:$PATH"

# ---------- 2. 配置 cargo 清华镜像源 ----------
echo "[2/6] 配置 cargo 清华镜像源 (crates.io-index)..."
CARGO_DIR="$HOME/.cargo"
CARGO_CONFIG="$CARGO_DIR/config.toml"
if [ -f "$CARGO_CONFIG" ]; then
    echo "    检测到已有 config.toml，备份为 config.toml.bak 后覆盖写入。"
    cp "$CARGO_CONFIG" "$CARGO_CONFIG.bak"
fi
mkdir -p "$CARGO_DIR"
cat > "$CARGO_CONFIG" <<'EOF'
[source.crates-io]
replace-with = "tuna"

# 稀疏索引地址（不再用git仓库地址）
[source.tuna]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

# 必须加 registries 段，cargo search 才能识别tuna这个名字
[registries.tuna]
index = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

# 可选，关闭证书吊销检查，部分内网环境
[http]
check-revoke = false
EOF
echo "    已写入 $CARGO_CONFIG"

# ---------- 3. 安装 uv ----------
echo "[3/6] 检查 / 安装 uv (Python 包管理器)..."
if command -v uv >/dev/null 2>&1 || [ -x "$HOME/.local/bin/uv" ]; then
    echo "    已检测到 uv，跳过安装。"
else
    echo "    正在安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if [ ! -x "$HOME/.local/bin/uv" ]; then
        echo "    [错误] uv 安装失败，请手动执行以下命令后重试："
        echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    echo "    uv 安装完成。"
fi
export PATH="$HOME/.local/bin:$PATH"

# ---------- 4. 安装 dora-cli ----------
echo "[4/6] 检查 / 安装 dora-cli (版本 0.5.0，与 dora-node-api 0.5.0 匹配)..."
DORA_OK=""
if command -v dora >/dev/null 2>&1; then
    DORA_VER=$(dora --version 2>/dev/null | head -1)
    case "$DORA_VER" in
        *0.5.0*) DORA_OK=1 ;;
    esac
fi
if [ -n "$DORA_OK" ]; then
    echo "    已检测到 dora-cli 0.5.0，跳过安装。"
else
    if command -v dora >/dev/null 2>&1; then
        OLD_DORA=$(command -v dora)
        echo "    检测到旧版 dora：$OLD_DORA"
        echo "    版本：$(dora --version 2>/dev/null | head -1)"
        echo "    正在清理旧版并强制安装 dora-cli 0.5.0..."
        rm -f "$HOME/.cargo/bin/dora" 2>/dev/null || true
    fi
    echo "    正在 cargo install dora-cli --version 0.5.0（首次编译约需数分钟）..."
    cargo install dora-cli --version 0.5.0 --force
    echo "    dora-cli 安装完成。"
    # 校验安装后 dora 是否指向 cargo bin
    if command -v dora >/dev/null 2>&1; then
        NEW_DORA=$(command -v dora)
        if [ "$NEW_DORA" != "$HOME/.cargo/bin/dora" ]; then
            echo "    [警告] 当前 PATH 中的 dora 位于：$NEW_DORA（不是 $HOME/.cargo/bin/dora）"
            echo "    请检查是否残留旧版 dora，并确保 ~/.cargo/bin 在 PATH 中靠前。"
        fi
    fi
fi

# ---------- 5. 可选：dora-rs pip 包 ----------
echo "[5/6] 安装 dora-rs pip 包（可选）..."
if command -v python3 >/dev/null 2>&1; then
    echo "    正在安装 dora-rs==0.5.0..."
    python3 -m pip install dora-rs==0.5.0 || echo "    警告：dora-rs pip 包安装失败（可忽略，Demo 部署时会装入虚拟环境）。"
else
    echo "    未检测到 python3，跳过。"
    echo "    dora-rs 包会在 Demo 部署 (3-部署代码.sh) 时自动装入虚拟环境。"
fi

# ---------- 版本验证 ----------
echo
echo "============================================"
echo "  环境安装完成，版本信息如下："
echo "============================================"
echo "  rustc : $(rustc --version 2>/dev/null)"
echo "  cargo : $(cargo --version 2>/dev/null)"
echo "  uv    : $(uv --version 2>/dev/null)"
echo "  dora  : $(dora --version 2>/dev/null)"
echo
echo "  注意：如果某个版本号显示为空，请【重新打开终端】后重跑本脚本。"
echo "        或将以下路径加入 ~/.zshrc："
echo "        export PATH=\"\$HOME/.cargo/bin:\$HOME/.local/bin:\$PATH\""
echo
