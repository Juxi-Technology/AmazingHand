#!/usr/bin/env bash
# AmazingHand environment setup (macOS)
# Install Rust + uv + dora-cli (0.5.0), configure the cargo tuna mirror
# Note: runs with /bin/bash (macOS built-in), requires curl and Xcode Command Line Tools
set -e
cd "$(dirname "$0")"

echo "============================================"
echo "  AmazingHand Environment Setup (macOS)"
echo "  Rust + uv + dora-rs one-click install"
echo "============================================"
echo

# ---------- 0. Check Xcode Command Line Tools ----------
echo "[0/6] Checking Xcode Command Line Tools..."
if ! xcode-select -p >/dev/null 2>&1; then
    echo "    [WARNING] Xcode Command Line Tools not found."
    echo "    Run in a terminal first: xcode-select --install"
    echo "    Re-run this script after the install completes."
    exit 1
else
    echo "    Xcode Command Line Tools found."
fi

# ---------- 1. Install Rust ----------
echo "[1/6] Checking / installing Rust (rustup + stable)..."
if command -v rustc >/dev/null 2>&1 || [ -x "$HOME/.cargo/bin/rustc" ]; then
    echo "    Rust already found. Skipping."
else
    echo "    Installing Rust via rustup..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --profile default
    if [ ! -f "$HOME/.cargo/env" ]; then
        echo "    [ERROR] rustup installation failed. Retry or see https://www.rust-lang.org/tools/install"
        exit 1
    fi
    echo "    Rust installed."
fi
# shellcheck source=/dev/null
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
export PATH="$HOME/.cargo/bin:$PATH"

# ---------- 2. Configure cargo tuna mirror ----------
echo "[2/6] Configuring cargo tuna mirror (crates.io-index)..."
CARGO_DIR="$HOME/.cargo"
CARGO_CONFIG="$CARGO_DIR/config.toml"
if [ -f "$CARGO_CONFIG" ]; then
    echo "    Existing config.toml backed up to config.toml.bak, then overwritten."
    cp "$CARGO_CONFIG" "$CARGO_CONFIG.bak"
fi
mkdir -p "$CARGO_DIR"
cat > "$CARGO_CONFIG" <<'EOF'
[source.crates-io]
replace-with = "tuna"

# sparse index (no longer the git repo url)
[source.tuna]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

# required for cargo search to recognize the "tuna" name
[registries.tuna]
index = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

# optional: disable certificate revocation check (some intranet setups)
[http]
check-revoke = false
EOF
echo "    Written to $CARGO_CONFIG"

# ---------- 3. Install uv ----------
echo "[3/6] Checking / installing uv (Python package manager)..."
if command -v uv >/dev/null 2>&1 || [ -x "$HOME/.local/bin/uv" ]; then
    echo "    uv already found. Skipping."
else
    echo "    Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if [ ! -x "$HOME/.local/bin/uv" ]; then
        echo "    [ERROR] uv installation failed. Run this manually:"
        echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    echo "    uv installed."
fi
export PATH="$HOME/.local/bin:$PATH"

# ---------- 4. Install dora-cli (force 0.5.0, remove old versions) ----------
echo "[4/6] Checking / installing dora-cli (version 0.5.0, matching dora-node-api 0.5.0)..."
DORA_OK=""
if command -v dora >/dev/null 2>&1; then
    DORA_VER=$(dora --version 2>/dev/null | head -1)
    case "$DORA_VER" in
        *0.5.0*) DORA_OK=1 ;;
    esac
fi
if [ -n "$DORA_OK" ]; then
    echo "    dora-cli 0.5.0 already installed. Skipping."
else
    if command -v dora >/dev/null 2>&1; then
        OLD_DORA=$(command -v dora)
        echo "    Old dora found: $OLD_DORA"
        echo "    Version: $(dora --version 2>/dev/null | head -1)"
        echo "    Cleaning old version and forcing install of dora-cli 0.5.0..."
        rm -f "$HOME/.cargo/bin/dora" 2>/dev/null || true
    fi
    echo "    Running cargo install dora-cli --version 0.5.0 (first compile may take minutes)..."
    cargo install dora-cli --version 0.5.0 --force
    echo "    dora-cli installed."
    if command -v dora >/dev/null 2>&1; then
        NEW_DORA=$(command -v dora)
        if [ "$NEW_DORA" != "$HOME/.cargo/bin/dora" ]; then
            echo "    [WARNING] dora in PATH is at: $NEW_DORA (not $HOME/.cargo/bin/dora)"
            echo "    Check for leftover old dora and make sure ~/.cargo/bin is early in PATH."
        fi
    fi
fi

# ---------- 5. Optional: dora-rs pip package ----------
echo "[5/6] Installing dora-rs pip package (optional)..."
if command -v python3 >/dev/null 2>&1; then
    echo "    Installing dora-rs==0.5.0..."
    python3 -m pip install dora-rs==0.5.0 || echo "    WARNING: dora-rs pip install failed (can be ignored, it is installed into the venv during Demo deploy)."
else
    echo "    python3 not found. Skipping."
    echo "    The dora-rs package will be installed into the venv by 3-Deploy_Demo.sh."
fi

# ---------- Version check ----------
echo
echo "============================================"
echo "  Environment setup finished. Versions:"
echo "============================================"
echo "  rustc : $(rustc --version 2>/dev/null)"
echo "  cargo : $(cargo --version 2>/dev/null)"
echo "  uv    : $(uv --version 2>/dev/null)"
echo "  dora  : $(dora --version 2>/dev/null)"
echo
echo "  NOTE: If any version shows empty, reopen the terminal and re-run this script."
echo "        Or add to ~/.zshrc:"
echo "        export PATH=\"\$HOME/.cargo/bin:\$HOME/.local/bin:\$PATH\""
echo
