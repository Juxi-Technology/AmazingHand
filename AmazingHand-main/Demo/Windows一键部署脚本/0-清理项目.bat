@echo off
chcp 936 >nul
setlocal EnableDelayedExpansion
title AmazingHand Cleanup (Windows)
cd /d "%~dp0"

echo ============================================
echo   AmazingHand 项目清理脚本 (Windows)
echo   清理 venv/target/缓存/备份，恢复默认端口
echo ============================================
echo.
echo   [警告] 将删除虚拟环境、编译产物、缓存，需重新部署！
echo.

set "ANS="
set /p "ANS=  确认清理？输入 Y 继续，其它退出: "
if /i not "%ANS%"=="Y" (
    echo   已取消。
    pause
    exit /b 0
)

REM ---- 定位 Demo 目录（脚本位于 Demo\Windows一键部署脚本 下）----
set "DEMO_DIR=%~dp0.."

REM ---- 1. 停止 dora 守护进程（避免文件占用）----
echo.
echo [1/5] 停止 dora 守护进程...
dora destroy >nul 2>nul
taskkill /IM dora.exe /F >nul 2>nul

REM ---- 2. 删除虚拟环境 ----
echo [2/5] 删除虚拟环境...
if exist "%DEMO_DIR%\.venv" (
    rmdir /s /q "%DEMO_DIR%\.venv"
    echo   已删除 Demo\.venv
)
if exist "%DEMO_DIR%\AHSimulation\.venv" (
    rmdir /s /q "%DEMO_DIR%\AHSimulation\.venv"
    echo   已删除 AHSimulation\.venv
)
if exist "%DEMO_DIR%\HandTracking\.venv" (
    rmdir /s /q "%DEMO_DIR%\HandTracking\.venv"
    echo   已删除 HandTracking\.venv
)

REM ---- 3. 删除 Rust 编译产物 ----
echo [3/5] 删除编译产物 (target)...
if exist "%DEMO_DIR%\target" (
    rmdir /s /q "%DEMO_DIR%\target"
    echo   已删除 Demo\target
)

REM ---- 4. 删除缓存与备份 ----
echo [4/5] 删除缓存与备份文件...
REM __pycache__
for /f "delims=" %%d in ('dir /s /b /ad "%DEMO_DIR%"\__pycache__ 2^>nul') do (
    rmdir /s /q "%%d"
)
REM .bak 备份文件
for /f "delims=" %%f in ('dir /s /b "%DEMO_DIR%"\*.bak 2^>nul') do (
    del /q "%%f"
)
REM 日志与临时文件
del /s /q "%DEMO_DIR%"\MUJOCO_LOG.TXT >nul 2>nul
REM dora 运行日志目录
if exist "%DEMO_DIR%\out" (
    rmdir /s /q "%DEMO_DIR%\out"
    echo   已删除 Demo\out (dora日志)
)
echo   已清理 __pycache__、*.bak、日志。

REM ---- 5. 恢复默认端口配置 (/dev/ttyACM0) ----
echo [5/5] 恢复 dataflow 默认端口 (/dev/ttyACM0)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0restore_port.ps1" -DemoDir "%DEMO_DIR%"

echo.
echo ============================================
echo   清理完成！
echo   重新部署请运行：3-部署代码.bat
echo ============================================
echo.
pause
