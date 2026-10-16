@echo off
setlocal EnableDelayedExpansion
title AmazingHand Run Helper (Windows)
cd /d "%~dp0"

set "PATH=%USERPROFILE%\.cargo\bin;%USERPROFILE%\.local\bin;%PATH%"

where dora >nul 2>nul
if errorlevel 1 (
    echo   [ERROR] dora not found. Run 1-Install_Env.bat first.
    pause
    exit /b 1
)

REM --- MSVC: dora build runs "cargo build" for AHControl, so this session needs
REM  the linker too. _msvc_env.bat loads vcvars64.bat into THIS session (no
REM  setlocal, so PATH/LIB/INCLUDE reach cargo). Warn only, never abort.
set "_MSVC_HELPER=%~dp0_msvc_env.bat"
if not exist "%_MSVC_HELPER%" (
    echo   [WARNING] _msvc_env.bat is missing from this folder. If the Rust build
    echo             fails, re-extract the complete Windows_Deploy_Scripts folder.
) else (
    call "%_MSVC_HELPER%"
    if errorlevel 1 echo   [WARNING] MSVC C++ build tools not available - the Rust build will most likely fail.
)

:menu_main
echo.
echo ============================================
echo   Select a run mode:
echo ============================================
echo    1 - Simulation (webcam hand tracking)
echo    2 - Real hardware
echo    q - Quit
echo ============================================
set "CHOICE="
set /p "CHOICE=  Enter number [1/2/q]: "

if /i "%CHOICE%"=="q" exit /b 0
if "%CHOICE%"=="1" (
    set "YML=dataflow_tracking_simu.yml"
    goto run_it
)
if "%CHOICE%"=="2" goto menu_real
echo   [Hint] Invalid input, please try again.
goto menu_main

:menu_real
echo.
echo ============================================
echo   Real hardware - select the hand:
echo ============================================
echo    1 - Right hand
echo    2 - Left hand
echo    3 - Both hands
echo    b - Back to main menu
echo ============================================
set "CHOICE2="
set /p "CHOICE2=  Enter number [1/2/3/b]: "

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
echo   [Hint] Invalid input, please try again.
goto menu_real

:run_it
REM Locate the Demo folder via absolute path (%%~dp0 is the script dir, parent is Demo)
set "DEMO_DIR=%~dp0.."
if not exist "%DEMO_DIR%\%YML%" (
    echo   [ERROR] %DEMO_DIR%\%YML% not found. Run this script from the "Windows_Deploy_Scripts" folder.
    pause
    exit /b 1
)
cd /d "%DEMO_DIR%"

echo.
echo   Config: %YML%
echo.
echo [1/3] Starting dora daemon...
dora up
if errorlevel 1 (
    REM  dora up gives up after ~2s and prints "daemon not connected" on slow
    REM  machines even though the daemon does come up. Retry once, then only warn:
    REM  a hard failure here would block setups that actually work.
    echo   [WARNING] dora up reported a problem, retrying once...
    dora up
    if errorlevel 1 echo   [WARNING] dora daemon may not be running. If the run below fails, re-run this script.
)

echo [2/3] Activating venv...
if exist ".venv" (
    call .venv\Scripts\activate.bat
) else (
    echo   [WARNING] .venv not found. Run 3-Deploy_Demo.bat first.
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
echo   Dataflow finished. Press any key to return to the main menu...
pause >nul
goto menu_main
