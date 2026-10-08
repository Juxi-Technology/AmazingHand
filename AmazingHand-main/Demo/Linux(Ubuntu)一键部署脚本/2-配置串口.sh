#!/usr/bin/env bash
# AmazingHand 串口自动配置脚本 (Linux)
# 检测舵机驱动板串口 -> 交互确认 -> 写入 dataflow yml 与 AHControl/src/main.rs
set -e
cd "$(dirname "$0")"

# dataflow yml 位于 Demo 目录，即脚本所在文件夹的上一级
DemoDir=".."
YmlFiles=(
    "../dataflow_tracking_real_right.yml"
    "../dataflow_tracking_real_left.yml"
    "../dataflow_tracking_real_2hands.yml"
)
MainRs="../AHControl/src/main.rs"

echo "============================================"
echo "  AmazingHand 串口自动配置 (Linux)"
echo "============================================"
echo

detect_ports() {
    # 列出 ttyACM* / ttyUSB* 设备
    ls -1 /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || true
}

write_port() {
    local port="$1"
    local ok=0

    # 替换 dataflow yml 中 args: 行的 --serialport 值
    for f in "${YmlFiles[@]}"; do
        if [ ! -f "$f" ]; then
            echo "  [警告] 跳过（文件不存在）：$f"
            continue
        fi
        cp "$f" "$f.bak"
        echo "  已备份 $f -> $f.bak"
        # 替换所有 --serialport 后的值（args 行与行尾注释，保持一致）
        # 用 | 作 sed 分隔符，避免端口路径 /dev/... 中的斜杠冲突
        sed -i -E "s|--serialport[[:space:]]+[^[:space:]]+|--serialport $port|g" "$f"
        echo "  已写入 $f : --serialport $port"
        ok=$((ok+1))
    done

    # 替换 main.rs 中 serialport 的默认值（不触碰 baudrate 与 config 路径）
    if [ -f "$MainRs" ]; then
        cp "$MainRs" "$MainRs.bak"
        echo "  已备份 main.rs -> main.rs.bak"
        # 仅替换 serialport 字段的默认值；排除 config 路径行（default_value = "config/..."）
        # 与 baudrate 行（default_value_t，不匹配本模式）
        awk -v port="$port" '
            /#\[arg\(short, long, default_value = "/ && !/config\// {
                sub(/default_value = "[^"]*"/, "default_value = \"" port "\"")
            }
            { print }
        ' "$MainRs" > "$MainRs.tmp" && mv "$MainRs.tmp" "$MainRs"
        echo "  已写入 AHControl/src/main.rs : serialport 默认值 = $port"
        ok=$((ok+1))
    else
        echo "  [警告] 未找到 AHControl/src/main.rs，跳过（检查 Demo 目录完整性）"
    fi

    echo
    if [ "$ok" -gt 0 ]; then
        echo "  串口配置完成（共写入 $ok 个文件）。"
        echo "  [提示] 若之前已 build 过 AHControl，请重新运行 3-部署代码.sh 使 main.rs 改动生效。"
    else
        echo "  [警告] 未写入任何文件，请检查项目结构。"
    fi
}

port=""
while true; do
    echo "[等待灵巧手连接]"
    echo "  请将灵巧手舵机驱动板【用 USB 连接到电脑】，然后按回车开始检测..."
    read -r -p "  按回车继续（输入 q 退出）: " tmp
    if [ "$tmp" = "q" ] || [ "$tmp" = "Q" ]; then
        exit 0
    fi

    echo "[检测串口]"
    mapfile -t ports < <(detect_ports)
    if [ "${#ports[@]}" -eq 0 ]; then
        echo "  [警告] 未检测到任何串口设备。请确认："
        echo "    1) 舵机驱动板已通电且 USB 线已连接；"
        echo "    2) 可执行 ls /dev/ttyUSB* /dev/ttyACM* 查看。"
        echo "    3) 若在虚拟机内，请在虚拟机设置中将 USB 设备连接到虚拟机。"
        echo "    按回车重新检测，输入 q 退出..."
        read -r -p "    : " tmp
        if [ "$tmp" = "q" ] || [ "$tmp" = "Q" ]; then
            exit 0
        fi
        continue
    fi

    echo "  检测到以下串口设备："
    for i in "${!ports[@]}"; do
        echo "    [$i] ${ports[$i]}"
    done

    if [ "${#ports[@]}" -eq 1 ]; then
        candidate="${ports[0]}"
        echo
        echo "[确认端口]"
        read -r -p "  检测到的端口为 $candidate，是否为该端口？[回车=确认，或输入其它端口号]: " ans
        if [ -z "$ans" ]; then
            port="$candidate"
        else
            port="$ans"
        fi
    else
        echo
        echo "[选择端口]"
        read -r -p "  输入端口编号 [0-$((${#ports[@]}-1))]，或直接输入其它端口号: " ans
        if [[ "$ans" =~ ^[0-9]+$ ]]; then
            if [ "$ans" -ge 0 ] && [ "$ans" -lt "${#ports[@]}" ]; then
                port="${ports[$ans]}"
            else
                echo "  [警告] 编号超出范围，请重试。"
                continue
            fi
        elif [ -n "$ans" ]; then
            port="$ans"
        else
            echo "  [警告] 输入无效，请重试。"
            continue
        fi
    fi

    if [[ "$port" =~ ^/dev/tty ]]; then
        echo "  确认使用端口：$port"
        break
    else
        echo "  [警告] 端口号格式应为 /dev/tty...（如 /dev/ttyACM0），输入的内容为：$port ，请重试。"
    fi
done

echo
echo "[写入配置文件]"
write_port "$port"

# Linux 串口权限处理
echo
if [ -e "$port" ]; then
    echo "[配置串口权限]"
    echo "  尝试授予当前用户对该串口的读写权限..."
    if sudo chmod 666 "$port" 2>/dev/null; then
        echo "  已执行：sudo chmod 666 $port"
    else
        echo "  [警告] chmod 失败（可能未输入正确密码或用户无 sudo 权限）。"
    fi
    echo "  建议（可选）将当前用户加入 dialout 组，避免每次重新插拔后无权限："
    echo "    sudo usermod -aG dialout \$USER"
    echo "  [注意] 该命令需要【注销并重新登录】后才生效。"
else
    echo "  [提示] 端口 $port 当前不存在（可能未连接），请连接后手动执行："
    echo "    sudo chmod 666 $port"
fi

echo
echo "  串口配置完成。如需运行，请执行 ./4-运行代码.sh 或重新执行 ./3-部署代码.sh"
