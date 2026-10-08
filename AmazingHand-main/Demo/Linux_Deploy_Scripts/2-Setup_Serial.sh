#!/usr/bin/env bash
# AmazingHand serial port auto-config (Linux)
# Detect the driver-board serial port -> confirm -> write into dataflow yml and AHControl/src/main.rs
set -e
cd "$(dirname "$0")"

# dataflow yml files are in the Demo folder, i.e. the parent of this script folder
DemoDir=".."
YmlFiles=(
    "../dataflow_tracking_real_right.yml"
    "../dataflow_tracking_real_left.yml"
    "../dataflow_tracking_real_2hands.yml"
)
MainRs="../AHControl/src/main.rs"

echo "============================================"
echo "  AmazingHand Serial Port Setup (Linux)"
echo "============================================"
echo

detect_ports() {
    # List ttyACM* / ttyUSB* devices
    ls -1 /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || true
}

write_port() {
    local port="$1"
    local ok=0

    # Replace the value after --serialport in the dataflow yml files
    for f in "${YmlFiles[@]}"; do
        if [ ! -f "$f" ]; then
            echo "  [WARNING] Skipped (not found): $f"
            continue
        fi
        cp "$f" "$f.bak"
        echo "  Backed up $f -> $f.bak"
        # Replace every --serialport value (args line and trailing comment stay consistent).
        # Use | as the sed delimiter so the port path /dev/... slashes don't conflict.
        sed -i -E "s|--serialport[[:space:]]+[^[:space:]]+|--serialport $port|g" "$f"
        echo "  Updated $f : --serialport $port"
        ok=$((ok+1))
    done

    # Replace the serialport default in main.rs (leave baudrate and config path alone)
    if [ -f "$MainRs" ]; then
        cp "$MainRs" "$MainRs.bak"
        echo "  Backed up main.rs -> main.rs.bak"
        # Only touch the serialport default_value; exclude config-path lines and baudrate(default_value_t)
        awk -v port="$port" '
            /#\[arg\(short, long, default_value = "/ && !/config\// {
                sub(/default_value = "[^"]*"/, "default_value = \"" port "\"")
            }
            { print }
        ' "$MainRs" > "$MainRs.tmp" && mv "$MainRs.tmp" "$MainRs"
        echo "  Updated AHControl/src/main.rs : serialport default = $port"
        ok=$((ok+1))
    else
        echo "  [WARNING] AHControl/src/main.rs not found, skipped (check Demo folder structure)"
    fi

    echo
    if [ "$ok" -gt 0 ]; then
        echo "  Serial port configured ($ok file(s))."
        echo "  [Hint] If AHControl was built before, re-run 3-Deploy_Demo.sh so the main.rs change takes effect."
    else
        echo "  [WARNING] Nothing was written. Check the project structure."
    fi
}

port=""
while true; do
    echo "[Waiting for the hand to connect]"
    echo "  Connect the servo driver board to the PC with USB, then press Enter to scan..."
    read -r -p "  Press Enter to continue (type q to quit): " tmp
    if [ "$tmp" = "q" ] || [ "$tmp" = "Q" ]; then
        exit 0
    fi

    echo "[Detecting serial ports]"
    mapfile -t ports < <(detect_ports)
    if [ "${#ports[@]}" -eq 0 ]; then
        echo "  [WARNING] No serial device detected. Please check:"
        echo "    1) The driver board is powered and the USB cable is connected;"
        echo "    2) Run: ls /dev/ttyUSB* /dev/ttyACM*"
        echo "    3) If inside a VM, connect the USB device to the VM."
        echo "    Press Enter to re-scan, type q to quit..."
        read -r -p "    : " tmp
        if [ "$tmp" = "q" ] || [ "$tmp" = "Q" ]; then
            exit 0
        fi
        continue
    fi

    echo "  Detected serial devices:"
    for i in "${!ports[@]}"; do
        echo "    [$i] ${ports[$i]}"
    done

    if [ "${#ports[@]}" -eq 1 ]; then
        candidate="${ports[0]}"
        echo
        echo "[Confirm port]"
        read -r -p "  Detected port is $candidate. Use this one? [Enter=yes, or type another port]: " ans
        if [ -z "$ans" ]; then
            port="$candidate"
        else
            port="$ans"
        fi
    else
        echo
        echo "[Select port]"
        read -r -p "  Enter port number [0-$((${#ports[@]}-1))], or type another device: " ans
        if [[ "$ans" =~ ^[0-9]+$ ]]; then
            if [ "$ans" -ge 0 ] && [ "$ans" -lt "${#ports[@]}" ]; then
                port="${ports[$ans]}"
            else
                echo "  [WARNING] Index out of range, try again."
                continue
            fi
        elif [ -n "$ans" ]; then
            port="$ans"
        else
            echo "  [WARNING] Invalid input, try again."
            continue
        fi
    fi

    if [[ "$port" =~ ^/dev/tty ]]; then
        echo "  Using port: $port"
        break
    else
        echo "  [WARNING] Port must look like /dev/tty... (e.g. /dev/ttyACM0). Got: $port , try again."
    fi
done

echo
echo "[Writing configuration]"
write_port "$port"

# Linux serial port permissions
echo
if [ -e "$port" ]; then
    echo "[Configuring serial port permissions]"
    echo "  Trying to grant the current user read/write access to the port..."
    if sudo chmod 666 "$port" 2>/dev/null; then
        echo "  Done: sudo chmod 666 $port"
    else
        echo "  [WARNING] chmod failed (wrong password or no sudo rights)."
    fi
    echo "  Recommended (optional): add the current user to the dialout group to avoid losing access after replugging:"
    echo "    sudo usermod -aG dialout \$USER"
    echo "  [NOTE] Log out and back in for this to take effect."
else
    echo "  [Hint] Port $port does not exist right now (maybe not connected). After connecting, run manually:"
    echo "    sudo chmod 666 $port"
fi

echo
echo "  Serial port configured. To run, use ./4-Run_Demo.sh, or re-run ./3-Deploy_Demo.sh"
