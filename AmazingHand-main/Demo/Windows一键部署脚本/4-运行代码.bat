@echo off
setlocal EnableDelayedExpansion
title AmazingHand Run Helper (Windows)
cd /d "%~dp0"

set "PATH=%USERPROFILE%\.cargo\bin;%USERPROFILE%\.local\bin;%PATH%"

where dora >nul 2>nul
if errorlevel 1 (
    echo   [ERROR] dora not found. Run 1-安装环境.bat first.
    pause
    exit /b 1
)

:menu_main
echo.
echo ============================================
echo   请选择运行模式：
echo ============================================
echo    1 - 模拟仿真（摄像头手势追踪）
echo    2 - 真实硬件
echo    q - 退出
echo ============================================
set "CHOICE="
set /p "CHOICE=  请输入序号 [1/2/q]: "

if /i "%CHOICE%"=="q" exit /b 0
if "%CHOICE%"=="1" (
    set "YML=dataflow_tracking_simu.yml"
    goto run_it
)
if "%CHOICE%"=="2" goto menu_real
echo   [提示] 输入无效，请重新选择。
goto menu_main

:menu_real
echo.
echo ============================================
echo   真实硬件 - 请选择灵巧手：
echo ============================================
echo    1 - 右手
echo    2 - 左手
echo    3 - 左右双手
echo    b - 返回上级菜单
echo ============================================
set "CHOICE2="
set /p "CHOICE2=  请输入序号 [1/2/3/b]: "

if /i "%CHOICE2%"=="b" goto menu_main
if "%CHOICE2%"=="1" (
    set "YML=dataflow_tracking_real_right.yml"
    goto run_it
)
if "%CHOICE2%"=="2" (
    set "YML=dataflow_tracking_real_left.yml"
    goto run_it
)
if "%CHOICE2%"=="3" (
    set "YML=dataflow_tracking_real_2hands.yml"
    goto run_it
)
echo   [提示] 输入无效，请重新选择。
goto menu_real

:run_it
REM 用绝对路径定位 Demo 目录（%~dp0 为脚本目录，上一级即 Demo）
set "DEMO_DIR=%~dp0.."
if not exist "%DEMO_DIR%\%YML%" (
    echo   [ERROR] %DEMO_DIR%\%YML% not found. Run this script from the "Windows一键部署脚本" folder.
    pause
    exit /b 1
)
cd /d "%DEMO_DIR%"

echo.
echo   Config: %YML%
echo.
echo [1/3] Starting dora daemon...
dora up

echo [2/3] Activating venv...
if exist ".venv" (
    call .venv\Scripts\activate.bat
) else (
    echo   [WARNING] .venv not found. Run 3-部署代码.bat first.
)

echo [3/3] Building and running %YML% ...
echo.
echo   dora build %YML% --uv
dora build %YML% --uv
if errorlevel 1 (
    echo   [ERROR] dora build failed. See errors above.
    pause
    exit /b 1
)
echo.
echo   dora run %YML% --uv   (Ctrl+C to stop)
echo.
dora run %YML% --uv

echo.
echo   数据流已结束。按任意键返回主菜单...
pause >nul
goto menu_main
