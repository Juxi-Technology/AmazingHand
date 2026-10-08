@echo off
setlocal EnableDelayedExpansion
title AmazingHand Demo Deploy (Windows)
cd /d "%~dp0"

echo ============================================
echo   AmazingHand Demo Deploy (Windows)
echo   Run 1-安装环境.bat first if needed
echo ============================================
echo.

set "PATH=%USERPROFILE%\.cargo\bin;%USERPROFILE%\.local\bin;%PATH%"

REM --- Check required commands ---
set "MISSING="
where dora >nul 2>nul || set "MISSING=!MISSING! dora"
where cargo >nul 2>nul || set "MISSING=!MISSING! cargo"
where uv >nul 2>nul || set "MISSING=!MISSING! uv"
if defined MISSING (
    echo   [ERROR] Missing commands: "!MISSING!"
    echo   Run 1-安装环境.bat first, then reopen the terminal.
    pause
    exit /b 1
)

REM 脚本位于 Demo\Windows一键部署脚本 下，上一级即 Demo 目录
cd ..
if not exist "AHControl" (
    echo   [ERROR] Demo folder not found. Run this script from the "Windows一键部署脚本" folder.
    pause
    exit /b 1
)

REM --- 1. Start dora daemon ---
echo [1/5] Starting dora daemon...
dora up

REM --- 2. Create / reuse venv ---
echo [2/5] Preparing Python 3.12 venv...
if exist ".venv" (
    choice /c YN /m "Existing .venv found. Rebuild overwrites it - rebuild? [Y/N]"
    if !errorlevel! equ 1 (
        echo   Removing old env and rebuilding...
        rmdir /s /q .venv
        uv venv --python 3.12
        if errorlevel 1 (
            echo   [ERROR] uv venv failed. Make sure uv and Python 3.12 are installed.
            pause
            exit /b 1
        )
    ) else (
        echo   Reusing existing .venv.
    )
) else (
    echo   Creating venv...
    uv venv --python 3.12
    if errorlevel 1 (
        echo   [ERROR] uv venv failed. Make sure uv and Python 3.12 are installed.
        pause
        exit /b 1
    )
)

REM --- 3. Activate venv ---
echo [3/5] Activating venv...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo   [ERROR] Failed to activate the venv.
    pause
    exit /b 1
)

REM --- 4. Build AHControl (Rust) ---
echo [4/5] Building AHControl (cargo build --release, first time takes minutes)...
cd AHControl
cargo build --release
if errorlevel 1 (
    echo   [ERROR] cargo build failed. Common causes: dora version mismatch, MSVC tools missing.
    pause
    exit /b 1
)
cd ..

REM --- 5. Sync Python deps ---
echo [5/5] Syncing Python deps (uv sync)...
echo   -- AHSimulation --
cd AHSimulation
uv sync
if errorlevel 1 (
    echo   [ERROR] AHSimulation uv sync failed.
    pause
    exit /b 1
)
cd ..
echo   -- HandTracking --
cd HandTracking
uv sync
if errorlevel 1 (
    echo   [ERROR] HandTracking uv sync failed.
    pause
    exit /b 1
)
cd ..

REM --- Fallback: force mediapipe 0.10.14 ---
echo [extra] Checking mediapipe==0.10.14 (known pitfall, force reinstall)...
uv pip uninstall -y mediapipe >nul 2>nul
uv pip install mediapipe==0.10.14
if errorlevel 1 (
    echo   [WARNING] mediapipe reinstall failed. You can run manually:
    echo   uv pip install mediapipe==0.10.14
) else (
    echo   mediapipe==0.10.14 ready.
)

echo.
echo ============================================
echo   Demo deployment finished^^!
echo   Run it with:  4-运行代码.bat [simu^|right^|left^|2hands^|angle]
echo ============================================
echo.
pause
