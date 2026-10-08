@echo off
setlocal EnableDelayedExpansion
title AmazingHand Environment Setup (Windows)
cd /d "%~dp0"

echo ============================================
echo   AmazingHand Environment Setup (Windows)
echo   Rust + uv + dora-rs one-click install
echo ============================================
echo.

REM --- 1. Check MSVC build tools (cl.exe) ---
echo [1/6] Checking MSVC build tools (cl.exe)...
set "CL_FOUND="
where cl.exe >nul 2>nul && set "CL_FOUND=1"
if not defined CL_FOUND (
    for /f "usebackq delims=" %%i in (`"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -latest -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2^>nul`) do (
        if exist "%%i\VC\Auxiliary\Build\vcvars64.bat" set "CL_FOUND=1"
    )
)
if defined CL_FOUND goto msvc_ok
goto msvc_missing

:msvc_missing
echo       [WARNING] MSVC build tools (cl.exe) NOT found.
echo       Rust MSVC toolchain requires the C++ workload of Visual Studio Build Tools.
echo.
echo       How to install (choose one):
echo         1. Open https://visualstudio.microsoft.com/zh-hans/downloads/
echo            and download "Visual Studio 2022 Build Tools".
echo         2. In the installer, check the "Desktop development with C++" workload, install, restart.
echo         3. Or install full Visual Studio 2022 Community.
echo.
pause

:msvc_ok
echo       MSVC build tools found. OK.

REM --- 2. Install Rust (skip if present) ---
echo.
echo [2/6] Installing Rust (rustup + stable-msvc)...
set "RUST_FOUND="
where rustc >nul 2>nul && set "RUST_FOUND=1"
if not defined RUST_FOUND if exist "%USERPROFILE%\.cargo\bin\rustc.exe" set "RUST_FOUND=1"
if defined RUST_FOUND goto rust_ok
goto rust_install

:rust_install
if exist "%TEMP%\rustup-init.exe" goto rust_run
echo       Downloading rustup-init.exe...
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://win.rustup.rs/x86_64' -OutFile ('%TEMP%\rustup-init.exe')"
if errorlevel 1 goto rust_dl_fail

:rust_run
echo       Installing Rust (default MSVC toolchain)...
"%TEMP%\rustup-init.exe" -y --default-toolchain stable --profile default
if errorlevel 1 goto rust_fail
goto rust_ok

:rust_dl_fail
echo       [ERROR] Failed to download rustup-init.exe. Check your network.
pause
exit /b 1

:rust_fail
echo       [ERROR] Rust installation failed. See https://www.rust-lang.org/tools/install
pause
exit /b 1

:rust_ok
echo       Rust ready.
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"

REM --- 3. Configure cargo tuna mirror ---
echo.
echo [3/6] Configuring cargo tuna mirror (crates.io-index)...
set "CARGO_HOME_CONFIG=%USERPROFILE%\.cargo\config.toml"
if exist "%CARGO_HOME_CONFIG%" (
    echo       Existing config.toml backed up to config.toml.bak.
    copy /y "%CARGO_HOME_CONFIG%" "%CARGO_HOME_CONFIG%.bak" >nul
)
if not exist "%USERPROFILE%\.cargo" mkdir "%USERPROFILE%\.cargo"
(
echo [source.crates-io]
echo replace-with = "tuna"
echo.
echo # sparse index (no longer the git repo url)
echo [source.tuna]
echo registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"
echo.
echo # required for cargo search to recognize the "tuna" name
echo [registries.tuna]
echo index = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"
echo.
echo # optional: disable certificate revocation check (some intranet setups)
echo [http]
echo check-revoke = false
) > "%CARGO_HOME_CONFIG%"
echo       Written to %CARGO_HOME_CONFIG%

REM --- 4. Install uv (skip if present) ---
echo.
echo [4/6] Installing uv (Python package manager)...
set "UV_FOUND="
where uv >nul 2>nul && set "UV_FOUND=1"
if not defined UV_FOUND if exist "%USERPROFILE%\.local\bin\uv.exe" set "UV_FOUND=1"
if defined UV_FOUND goto uv_ok
goto uv_install

:uv_install
echo       Installing uv...
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
if errorlevel 1 goto uv_fail
goto uv_ok

:uv_fail
echo       [ERROR] uv installation failed. Run this manually:
echo       powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 ^| iex"
pause
exit /b 1

:uv_ok
echo       uv ready.
set "PATH=%USERPROFILE%\.local\bin;%PATH%"

REM --- 5. Install dora-cli ---
echo.
echo [5/6] Installing dora-cli (version 0.5.0, matching dora-node-api 0.5.0)...
set "DORA_FOUND="
for /f "usebackq delims=" %%v in (`dora --version 2^>nul`) do set "DORA_VER=%%v"
if not defined DORA_VER if exist "%USERPROFILE%\.cargo\bin\dora.exe" (
    for /f "usebackq delims=" %%v in (`"%USERPROFILE%\.cargo\bin\dora.exe" --version 2^>nul`) do set "DORA_VER=%%v"
)
if not defined DORA_VER goto dora_install
echo       Detected: !DORA_VER!
echo !DORA_VER! | findstr /i "0.5.0" >nul && goto dora_ok
echo       [WARNING] Old dora detected, forcing install of 0.5.0...
del /q "%USERPROFILE%\.cargo\bin\dora.exe" >nul 2>nul
goto dora_install

:dora_install
echo       Running cargo install dora-cli --version 0.5.0 (first compile may take minutes)...
cargo install dora-cli --version 0.5.0 --force
if errorlevel 1 goto dora_fail
goto dora_ok

:dora_fail
echo       [ERROR] dora-cli installation failed. See https://dora-rs.ai/dora/zh-CN/getting-started/installation
pause
exit /b 1

:dora_ok
echo       dora ready.
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"

REM --- 6. Optional: dora-rs pip package ---
echo.
echo [6/6] Installing dora-rs pip package (optional)...
where python >nul 2>nul
if errorlevel 1 goto no_python
echo       Installing dora-rs==0.5.0...
python -m pip install dora-rs==0.5.0
goto ver_check

:no_python
echo       System Python not found. Skipping.
echo       The dora-rs package will be installed into the venv by 3-²¿Êð´úÂë.bat.

:ver_check
REM --- Version check ---
echo.
echo ============================================
echo   Environment setup finished. Versions:
echo ============================================
for /f "delims=" %%i in ('rustc --version 2^>nul') do set "VER_RUSTC=%%i"
for /f "delims=" %%i in ('cargo --version 2^>nul') do set "VER_CARGO=%%i"
for /f "delims=" %%i in ('uv --version 2^>nul') do set "VER_UV=%%i"
for /f "delims=" %%i in ('dora --version 2^>nul') do set "VER_DORA=%%i"
echo   rustc : !VER_RUSTC!
echo   cargo : !VER_CARGO!
echo   uv    : !VER_UV!
echo   dora  : !VER_DORA!
echo.
echo   NOTE: Close and reopen this terminal for PATH to take effect globally.
echo         If any version shows empty, re-run this script in a new terminal.
echo.
pause
