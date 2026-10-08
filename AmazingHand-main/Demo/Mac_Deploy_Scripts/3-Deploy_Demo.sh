#!/usr/bin/env bash
# AmazingHand Demo one-click deploy (macOS)
# Run 1-Install_Env.sh first if needed
set -e
cd "$(dirname "$0")"

echo "============================================"
echo "  AmazingHand Demo Deploy (macOS)"
echo "  Run 1-Install_Env.sh first if needed"
echo "============================================"
echo

export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# Check required commands
for cmd in dora cargo uv; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "  [ERROR] Missing command: $cmd"
        echo "  Run ./1-Install_Env.sh first, then reopen the terminal."
        exit 1
    fi
done

# Script is in Demo/Mac_Deploy_Scripts, parent is the Demo folder
cd ..
if [ ! -d "AHControl" ]; then
    echo "  [ERROR] Demo folder not found. Run this script from the Demo/Mac_Deploy_Scripts folder."
    exit 1
fi

# 1. Start the dora daemon
echo "[1/5] Starting dora daemon..."
dora up

# 2. Create / reuse venv
echo "[2/5] Preparing Python 3.12 venv..."
if [ -d ".venv" ]; then
    read -r -p "Existing .venv found. Rebuild overwrites it - rebuild? [y/N]: " ans
    if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
        echo "  Removing old env and rebuilding..."
        rm -rf .venv
        uv venv --python 3.12
    else
        echo "  Reusing existing .venv."
    fi
else
    echo "  Creating venv..."
    uv venv --python 3.12
fi

# 3. Activate the venv
echo "[3/5] Activating venv..."
# shellcheck source=/dev/null
source .venv/bin/activate

# 4. Build AHControl (Rust)
echo "[4/5] Building AHControl (cargo build --release, first time takes minutes)..."
cd AHControl
cargo build --release
cd ..

# 5. Sync Python deps
echo "[5/5] Syncing Python deps (uv sync)..."
echo "  -- AHSimulation --"
cd AHSimulation
uv sync
cd ..
echo "  -- HandTracking --"
cd HandTracking
uv sync
cd ..

# Fallback: force mediapipe 0.10.14
echo "[extra] Checking mediapipe==0.10.14 (known pitfall, force reinstall)..."
uv pip uninstall -y mediapipe >/dev/null 2>&1 || true
if uv pip install mediapipe==0.10.14; then
    echo "  mediapipe==0.10.14 ready."
else
    echo "  [WARNING] mediapipe reinstall failed. You can run manually:"
    echo "  uv pip install mediapipe==0.10.14"
fi

echo
echo "============================================"
echo "  Demo deployment finished!"
echo "  Run it with:  ./4-Run_Demo.sh"
echo "============================================"
echo
