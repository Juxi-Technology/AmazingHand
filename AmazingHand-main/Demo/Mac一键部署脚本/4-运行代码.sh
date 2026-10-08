#!/usr/bin/env bash
# AmazingHand 运行辅助 (macOS)
# 交互式菜单：1=模拟仿真  2=真实硬件（右手/左手/双手）  q=退出
set -e
cd "$(dirname "$0")"

export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

if ! command -v dora >/dev/null 2>&1; then
    echo "  [错误] 未找到 dora，请先运行 ./1-安装环境.sh。"
    exit 1
fi

menu_main() {
    echo
    echo "============================================"
    echo "  请选择运行模式："
    echo "============================================"
    echo "    1 - 模拟仿真（摄像头手势追踪）"
    echo "    2 - 真实硬件"
    echo "    q - 退出"
    echo "============================================"
    read -r -p "  请输入序号 [1/2/q]: " CHOICE

    case "$CHOICE" in
        q|Q) exit 0 ;;
        1) YML="dataflow_tracking_simu.yml"; run_it ;;
        2) menu_real ;;
        *) echo "  [提示] 输入无效，请重新选择。"; menu_main ;;
    esac
}

menu_real() {
    echo
    echo "============================================"
    echo "  真实硬件 - 请选择灵巧手："
    echo "============================================"
    echo "    1 - 右手"
    echo "    2 - 左手"
    echo "    3 - 左右双手"
    echo "    b - 返回上级菜单"
    echo "============================================"
    read -r -p "  请输入序号 [1/2/3/b]: " CHOICE

    case "$CHOICE" in
        b|B) menu_main ;;
        1) YML="dataflow_tracking_real_right.yml"; run_it ;;
        2) YML="dataflow_tracking_real_left.yml"; run_it ;;
        3) YML="dataflow_tracking_real_2hands.yml"; run_it ;;
        *) echo "  [提示] 输入无效，请重新选择。"; menu_real ;;
    esac
}

run_it() {
    # yml 位于上一级（Demo 目录），脚本位于 Demo/Mac一键部署脚本
    if [ ! -f "../$YML" ]; then
        echo "  [错误] 未找到 ../$YML，请确认脚本位于 Demo/Mac一键部署脚本 文件夹中。"
        exit 1
    fi
    cd ..

    echo
    echo "  Config: $YML"
    echo
    echo "[1/3] 启动 dora 守护进程..."
    dora up

    echo "[2/3] 激活虚拟环境..."
    if [ -d ".venv" ]; then
        # shellcheck source=/dev/null
        source .venv/bin/activate
    else
        echo "  [警告] 未找到 .venv，请先运行 ./3-部署代码.sh 完成部署。"
    fi

    echo "[3/3] 构建并运行 $YML ..."
    echo
    echo "  dora build $YML --uv"
    dora build "$YML" --uv
    echo
    echo "  dora run $YML --uv  （Ctrl+C 停止）"
    echo
    dora run "$YML" --uv

    echo
    echo "  数据流已结束。按回车返回主菜单..."
    read -r -p ""
    menu_main
}

menu_main
