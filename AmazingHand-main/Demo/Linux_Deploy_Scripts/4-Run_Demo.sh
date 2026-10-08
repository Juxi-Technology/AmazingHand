#!/usr/bin/env bash
# AmazingHand run helper (Linux)
# Interactive menu: 1=Simulation  2=Real hardware (right/left/both)  q=Quit
set -e
cd "$(dirname "$0")"

export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

if ! command -v dora >/dev/null 2>&1; then
    echo "  [ERROR] dora not found. Run ./1-Install_Env.sh first."
    exit 1
fi

menu_main() {
    echo
    echo "============================================"
    echo "  Select a run mode:"
    echo "============================================"
    echo "    1 - Simulation (webcam hand tracking)"
    echo "    2 - Real hardware"
    echo "    q - Quit"
    echo "============================================"
    read -r -p "  Enter number [1/2/q]: " CHOICE

    case "$CHOICE" in
        q|Q) exit 0 ;;
        1) YML="dataflow_tracking_simu.yml"; run_it ;;
        2) menu_real ;;
        *) echo "  [Hint] Invalid input, please try again."; menu_main ;;
    esac
}

menu_real() {
    echo
    echo "============================================"
    echo "  Real hardware - select the hand:"
    echo "============================================"
    echo "    1 - Right hand"
    echo "    2 - Left hand"
    echo "    3 - Both hands"
    echo "    b - Back to main menu"
    echo "============================================"
    read -r -p "  Enter number [1/2/3/b]: " CHOICE

    case "$CHOICE" in
        b|B) menu_main ;;
        1) YML="dataflow_tracking_real_right.yml"; run_it ;;
        2) YML="dataflow_tracking_real_left.yml"; run_it ;;
        3) YML="dataflow_tracking_real_2hands.yml"; run_it ;;
        *) echo "  [Hint] Invalid input, please try again."; menu_real ;;
    esac
}

run_it() {
    # yml is in the parent folder (Demo), script is in Demo/Linux_Deploy_Scripts
    if [ ! -f "../$YML" ]; then
        echo "  [ERROR] ../$YML not found. Run this script from the Demo/Linux_Deploy_Scripts folder."
        exit 1
    fi
    cd ..

    echo
    echo "  Config: $YML"
    echo
    echo "[1/3] Starting dora daemon..."
    dora up

    echo "[2/3] Activating venv..."
    if [ -d ".venv" ]; then
        # shellcheck source=/dev/null
        source .venv/bin/activate
    else
        echo "  [WARNING] .venv not found. Run ./3-Deploy_Demo.sh first."
    fi

    echo "[3/3] Building and running $YML ..."
    echo
    echo "  dora build $YML --uv"
    dora build "$YML" --uv
    echo
    echo "  dora run $YML --uv  (Ctrl+C to stop)"
    echo
    dora run "$YML" --uv

    echo
    echo "  Dataflow finished. Press Enter to return to the main menu..."
    read -r -p ""
    menu_main
}

menu_main
