#!/usr/bin/env bash
# AmazingHand 项目清理脚本 (Linux)
# 清理 venv/target/缓存/备份，恢复默认端口 /dev/ttyACM0
set -e
cd "$(dirname "$0")"

echo "============================================"
echo "  AmazingHand 项目清理脚本 (Linux)"
echo "  清理 venv/target/缓存/备份，恢复默认端口"
echo "============================================"
echo
echo "  [警告] 将删除虚拟环境、编译产物、缓存，需重新部署！"
echo
read -r -p "  确认清理？输入 Y 继续，其它退出: " ans
if [ "$ans" != "Y" ] && [ "$ans" != "y" ]; then
    echo "  已取消。"
    exit 0
fi

# 脚本位于 Demo/Linux(Ubuntu)一键部署脚本 下，上一级即 Demo
DEMO_DIR="$(cd .. && pwd)"
echo "  Demo 目录: $DEMO_DIR"
echo

# ---- 1. 停止 dora 守护进程 ----
echo "[1/5] 停止 dora 守护进程..."
dora destroy >/dev/null 2>&1 || true
pkill -f dora-daemon >/dev/null 2>&1 || true

# ---- 2. 删除虚拟环境 ----
echo "[2/5] 删除虚拟环境..."
for v in ".venv" "AHSimulation/.venv" "HandTracking/.venv"; do
    if [ -d "$DEMO_DIR/$v" ]; then
        rm -rf "$DEMO_DIR/$v"
        echo "  已删除 $v"
    fi
done

# ---- 3. 删除 Rust 编译产物 ----
echo "[3/5] 删除编译产物 (target)..."
if [ -d "$DEMO_DIR/target" ]; then
    rm -rf "$DEMO_DIR/target"
    echo "  已删除 Demo/target"
fi

# ---- 4. 删除缓存与备份 ----
echo "[4/5] 删除缓存与备份文件..."
find "$DEMO_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$DEMO_DIR" -type f -name "*.bak" -delete 2>/dev/null || true
find "$DEMO_DIR" -maxdepth 3 -name "MUJOCO_LOG.TXT" -delete 2>/dev/null || true
# dora 运行日志目录
if [ -d "$DEMO_DIR/out" ]; then
    rm -rf "$DEMO_DIR/out"
    echo "  已删除 Demo/out (dora日志)"
fi
echo "  已清理 __pycache__、*.bak、日志。"

# ---- 5. 恢复默认端口配置 (/dev/ttyACM0) ----
echo "[5/5] 恢复 dataflow 默认端口 (/dev/ttyACM0)..."
for f in dataflow_tracking_real_right.yml dataflow_tracking_real_left.yml dataflow_tracking_real_2hands.yml; do
    if [ -f "$DEMO_DIR/$f" ]; then
        # 替换所有 --serialport 后的值（args 行与行尾注释）
        sed -i -E "s|--serialport[[:space:]]+[^[:space:]]+|--serialport /dev/ttyACM0|g" "$DEMO_DIR/$f"
        echo "  已恢复 $f"
    fi
done
if [ -f "$DEMO_DIR/AHControl/src/main.rs" ]; then
    # 仅替换 serialport 字段默认值，不触碰 baudrate(config路径)
    awk -v port="/dev/ttyACM0" '
        /#\[arg\(short, long, default_value = "/ && !/config\// {
            sub(/default_value = "[^"]*"/, "default_value = \"" port "\"")
        }
        { print }
    ' "$DEMO_DIR/AHControl/src/main.rs" > "$DEMO_DIR/AHControl/src/main.rs.tmp" \
        && mv "$DEMO_DIR/AHControl/src/main.rs.tmp" "$DEMO_DIR/AHControl/src/main.rs"
    echo "  已恢复 main.rs"
fi

echo
echo "============================================"
echo "  清理完成！"
echo "  重新部署请运行：./3-部署代码.sh"
echo "============================================"
echo
