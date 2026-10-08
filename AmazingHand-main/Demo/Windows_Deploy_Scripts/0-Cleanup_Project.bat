@echo off
setlocal EnableDelayedExpansion
title AmazingHand Project Cleanup (Windows)
cd /d "%~dp0"

echo ============================================
echo   AmazingHand Project Cleanup (Windows)
echo   Remove venv/target/cache/backups, restore default port
echo ============================================
echo.
echo   [WARNING] This deletes virtual envs, build output and caches. Re-deploy required!
echo.

set "ANS="
set /p "ANS=  Confirm cleanup? Type Y to continue, anything else to quit: "
if /i not "%ANS%"=="Y" (
    echo   Cancelled.
    pause
    exit /b 0
)

REM Locate the Demo folder (script is in Demo\Windows_Deploy_Scripts, parent is Demo)
set "DEMO_DIR=%~dp0.."

REM ---- 1. Stop dora daemon (avoid file locks) ----
echo.
echo [1/5] Stopping dora daemon...
dora destroy >nul 2>nul
taskkill /IM dora.exe /F >nul 2>nul

REM ---- 2. Delete virtual envs ----
echo [2/5] Deleting virtual envs...
if exist "%DEMO_DIR%\.venv" (
    rmdir /s /q "%DEMO_DIR%\.venv"
    echo   Deleted Demo\.venv
)
if exist "%DEMO_DIR%\AHSimulation\.venv" (
    rmdir /s /q "%DEMO_DIR%\AHSimulation\.venv"
    echo   Deleted AHSimulation\.venv
)
if exist "%DEMO_DIR%\HandTracking\.venv" (
    rmdir /s /q "%DEMO_DIR%\HandTracking\.venv"
    echo   Deleted HandTracking\.venv
)

REM ---- 3. Delete Rust build output ----
echo [3/5] Deleting build output (target)...
if exist "%DEMO_DIR%\target" (
    rmdir /s /q "%DEMO_DIR%\target"
    echo   Deleted Demo\target
)

REM ---- 4. Delete caches and backups ----
echo [4/5] Deleting caches and backups...
REM __pycache__
for /f "delims=" %%d in ('dir /s /b /ad "%DEMO_DIR%"\__pycache__ 2^>nul') do (
    rmdir /s /q "%%d"
)
REM .bak backup files
for /f "delims=" %%f in ('dir /s /b "%DEMO_DIR%"\*.bak 2^>nul') do (
    del /q "%%f"
)
REM logs and temp files
del /s /q "%DEMO_DIR%"\MUJOCO_LOG.TXT >nul 2>nul
REM dora log directory
if exist "%DEMO_DIR%\out" (
    rmdir /s /q "%DEMO_DIR%\out"
    echo   Deleted Demo\out (dora logs)
)
echo   Cleaned __pycache__, *.bak, logs.

REM ---- 5. Restore default port (/dev/ttyACM0) ----
echo [5/5] Restoring default port (/dev/ttyACM0)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0restore_port.ps1" -DemoDir "%DEMO_DIR%"

echo.
echo ============================================
echo   Cleanup finished!
echo   To re-deploy run:  3-Deploy_Demo.bat
echo ============================================
echo.
pause
