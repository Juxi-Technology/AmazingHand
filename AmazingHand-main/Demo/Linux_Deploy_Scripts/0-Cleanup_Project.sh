#!/usr/bin/env bash
# AmazingHand project cleanup (Linux)
# Remove venv/target/caches/backups, restore the default port /dev/ttyACM0
set -e
cd "$(dirname "$0")"

echo "============================================"
echo "  AmazingHand Project Cleanup (Linux)"
echo "  Remove venv/target/caches/backups, restore default port"
echo "============================================"
echo
echo "  [WARNING] This deletes virtual envs, build output and caches. Re-deploy required!"
echo
read -r -p "  Confirm cleanup? Type Y to continue, anything else to quit: " ans
if [ "$ans" != "Y" ] && [ "$ans" != "y" ]; then
    echo "  Cancelled."
    exit 0
fi

# Script is in Demo/Linux_Deploy_Scripts, parent is the Demo folder
DEMO_DIR="$(cd .. && pwd)"
echo "  Demo dir: $DEMO_DIR"
echo

# ---- 1. Stop the dora daemon ----
echo "[1/5] Stopping dora daemon..."
dora destroy >/dev/null 2>&1 || true
pkill -f dora-daemon >/dev/null 2>&1 || true

# ---- 2. Delete virtual envs ----
echo "[2/5] Deleting virtual envs..."
for v in ".venv" "AHSimulation/.venv" "HandTracking/.venv"; do
    if [ -d "$DEMO_DIR/$v" ]; then
        rm -rf "$DEMO_DIR/$v"
        echo "  Deleted $v"
    fi
done

# ---- 3. Delete Rust build output ----
echo "[3/5] Deleting build output (target)..."
if [ -d "$DEMO_DIR/target" ]; then
    rm -rf "$DEMO_DIR/target"
    echo "  Deleted Demo/target"
fi

# ---- 4. Delete caches and backups ----
echo "[4/5] Deleting caches and backups..."
find "$DEMO_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$DEMO_DIR" -type f -name "*.bak" -delete 2>/dev/null || true
find "$DEMO_DIR" -maxdepth 3 -name "MUJOCO_LOG.TXT" -delete 2>/dev/null || true
# dora log directory
if [ -d "$DEMO_DIR/out" ]; then
    rm -rf "$DEMO_DIR/out"
    echo "  Deleted Demo/out (dora logs)"
fi
echo "  Cleaned __pycache__, *.bak, logs."

# ---- 5. Restore default port (/dev/ttyACM0) ----
echo "[5/5] Restoring default port (/dev/ttyACM0)..."
for f in dataflow_tracking_real_right.yml dataflow_tracking_real_left.yml dataflow_tracking_real_2hands.yml; do
    if [ -f "$DEMO_DIR/$f" ]; then
        sed -i -E "s|--serialport[[:space:]]+[^[:space:]]+|--serialport /dev/ttyACM0|g" "$DEMO_DIR/$f"
        echo "  Restored $f"
    fi
done
if [ -f "$DEMO_DIR/AHControl/src/main.rs" ]; then
    awk -v port="/dev/ttyACM0" '
        /#\[arg\(short, long, default_value = "/ && !/config\// {
            sub(/default_value = "[^"]*"/, "default_value = \"" port "\"")
        }
        { print }
    ' "$DEMO_DIR/AHControl/src/main.rs" > "$DEMO_DIR/AHControl/src/main.rs.tmp" \
        && mv "$DEMO_DIR/AHControl/src/main.rs.tmp" "$DEMO_DIR/AHControl/src/main.rs"
    echo "  Restored main.rs"
fi

echo
echo "============================================"
echo "  Cleanup finished!"
echo "  To re-deploy run:  ./3-Deploy_Demo.sh"
echo "============================================"
echo
