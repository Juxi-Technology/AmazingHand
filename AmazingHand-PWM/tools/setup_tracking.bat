@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
title AmazingHand 手势追踪环境部署

echo ============================================
echo  AmazingHand 手势追踪环境部署脚本
echo  需要 64 位 Python 3.12 (mediapipe 必需)
echo ============================================
echo.

REM ---- 1. 查找 64 位 Python ----
echo [1/4] 查找 64 位 Python...
set "PYEXE="

REM 方法1: 检测 D:\Python312-64bit (常用)
if exist "D:\Python312-64bit\python.exe" (
    set "PYEXE=D:\Python312-64bit\python.exe"
    goto found
)

REM 方法1b: 检测 D:\Python312-64
if exist "D:\Python312-64\python.exe" (
    set "PYEXE=D:\Python312-64\python.exe"
    goto found
)

REM 方法2: py launcher 检测 64 位
for /f "usebackq delims=" %%p in (`py -3.12-64 -c "import sys;print(sys.executable)" 2^>nul`) do set "PYEXE=%%p"
if defined PYEXE goto found

REM 方法3: 常用路径
for %%d in (
    "%LOCALAPPDATA%\Programs\Python\Python312-64\python.exe"
    "C:\Program Files\Python312-64\python.exe"
) do (
    if exist %%d set "PYEXE=%%~d"
)
if defined PYEXE goto found

echo   [错误] 未找到 64 位 Python 3.12
echo   请从 https://www.python.org/downloads/ 下载 64 位 installer
echo   安装时选择 Add to PATH, 或装到 D:\Python312-64
pause
exit /b 1

:found
echo   [OK] 使用: %PYEXE%
"%PYEXE%" -c "import struct; exit(0 if struct.calcsize('P')*8==64 else 1)"
if errorlevel 1 (
    echo   [错误] 找到的 Python 不是 64 位, 请安装 64 位版本
    pause
    exit /b 1
)
echo   [OK] 已确认 64 位

REM ---- 2. 创建 venv ----
echo.
echo [2/4] 创建虚拟环境 tracking_env...
if not exist "%~dp0tracking_env\Scripts\python.exe" (
    "%PYEXE%" -m venv "%~dp0tracking_env"
    if errorlevel 1 (
        echo   [错误] venv 创建失败
        pause
        exit /b 1
    )
)
set "VENV_PY=%~dp0tracking_env\Scripts\python.exe"
echo   [OK] venv: %VENV_PY%

REM ---- 3. 安装依赖 ----
echo.
echo [3/4] 安装依赖 (mediapipe 0.10.14 等, 需几分钟)...
"%VENV_PY%" -m pip install --upgrade pip -q
"%VENV_PY%" -m pip install -r "%~dp0requirements-tracking.txt"
if errorlevel 1 (
    echo   [错误] 依赖安装失败, 请检查网络后重试
    pause
    exit /b 1
)
echo   [OK] 依赖安装完成

REM ---- 4. 验证 ----
echo.
echo [4/4] 验证 mediapipe...
"%VENV_PY%" -c "import mediapipe; print('  mediapipe', mediapipe.__version__)"
if errorlevel 1 (
    echo   [错误] mediapipe 导入失败
    pause
    exit /b 1
)
echo.
echo ============================================
echo  部署完成!
echo  在模块根目录运行:
echo    tools\tracking_env\Scripts\python tools\hand_gui.py
echo ============================================
pause
