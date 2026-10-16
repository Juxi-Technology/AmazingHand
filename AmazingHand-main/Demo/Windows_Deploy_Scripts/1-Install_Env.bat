@echo off
setlocal EnableDelayedExpansion
title AmazingHand Environment Setup (Windows)
cd /d "%~dp0"

echo ============================================
echo   AmazingHand Environment Setup (Windows)
echo   Rust + uv + dora-rs one-click install
echo ============================================
echo.

REM --- 1. MSVC build tools ------------------------------------------------
REM  Delegated to _msvc_env.bat, which locates vcvars64.bat and LOADS it into
REM  this session, then verifies by actually compiling and linking a probe.
REM  Keep that helper next to this script - it must ship with the kit.
echo [1/6] Checking MSVC C++ build tools...
set "_MSVC_HELPER=%~dp0_msvc_env.bat"
set "MSVC_OK="
if not exist "%_MSVC_HELPER%" goto msvc_helper_missing
call "%_MSVC_HELPER%"
if not errorlevel 1 set "MSVC_OK=1"
if defined MSVC_OK goto msvc_ok
goto msvc_missing

:msvc_helper_missing
echo       [ERROR] _msvc_env.bat is missing from this folder.
echo       MSVC cannot be set up without it. Re-extract the complete
echo       Windows_Deploy_Scripts folder and run this script again.
pause
exit /b 1

:msvc_missing
echo       [WARNING] MSVC C++ build tools could not be set up.
echo       The Rust MSVC toolchain needs a working linker, so the build
echo       later in this kit will most likely fail.
echo.
echo       How to fix, pick one:
echo         1. Open https://visualstudio.microsoft.com/downloads/
echo            and download "Visual Studio Build Tools".
echo         2. In the installer, tick the workload
echo            "Desktop development with C++", install, then reboot.
echo         3. Re-run 1-Install_Env.bat afterwards.
echo.
echo       Continuing anyway - Rust can sometimes find MSVC on its own.
echo.

:msvc_ok
echo       MSVC build tools ready.

REM --- 2. Rust: verify what is installed, reinstall it when it is broken ---
REM  An existing rustup home is often half-damaged - rustc.exe is still on disk
REM  but has no default toolchain, or the toolchain is the GNU one, or it cannot
REM  link. Blindly skipping the install then surfaces as a confusing cargo
REM  failure 10 to 20 minutes later, so every install is verified here first
REM  and replaced when it does not check out.
echo.
echo [2/6] Checking Rust toolchain...
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"

REM  Rust downloads go through the Tsinghua mirror. The official servers are not
REM  usable from China at this size: static.rust-lang.org measured at 30 KB/s
REM  against a 1.5-2 GB toolchain is well over ten hours. rustup-init reads the
REM  first two variables; RUSTUP_INIT_URL is the installer itself, also mirrored.
set "RUSTUP_DIST_SERVER=https://mirrors.tuna.tsinghua.edu.cn/rustup"
set "RUSTUP_UPDATE_ROOT=https://mirrors.tuna.tsinghua.edu.cn/rustup/rustup"
set "RUSTUP_INIT_URL=https://mirrors.tuna.tsinghua.edu.cn/rustup/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe"

set "RUST_STATE="
set "RUST_HOST="
where rustc >nul 2>nul
if errorlevel 1 set "RUST_STATE=missing"
where cargo >nul 2>nul
if errorlevel 1 set "RUST_STATE=missing"
if defined RUST_STATE goto rust_decide

for /f "tokens=2" %%h in ('rustc -vV 2^>nul ^| findstr /b /c:"host:"') do set "RUST_HOST=%%h"
if not defined RUST_HOST set "RUST_STATE=no-default-toolchain"
if defined RUST_STATE goto rust_decide

echo !RUST_HOST! | findstr /i "windows-msvc" >nul
if errorlevel 1 set "RUST_STATE=wrong-toolchain"
if defined RUST_STATE goto rust_decide

call :rust_probe
if errorlevel 1 set "RUST_STATE=cannot-link"
goto rust_decide

:rust_decide
if not defined RUST_STATE goto rust_ok
if "!RUST_STATE!"=="missing" goto rust_install

echo       [WARNING] Existing Rust installation is not usable: !RUST_STATE!
echo                 Host detected: !RUST_HOST!
echo                 Removing it and reinstalling with the MSVC toolchain.
goto rust_uninstall

:rust_uninstall
taskkill /IM rustc.exe /F >nul 2>nul
taskkill /IM cargo.exe /F >nul 2>nul
taskkill /IM rustup.exe /F >nul 2>nul
where rustup >nul 2>nul
if not errorlevel 1 rustup self uninstall -y
REM  rustup self uninstall should have cleared these; sweep the leftovers in
REM  case rustup was absent or refused to run.
if exist "%USERPROFILE%\.rustup" rmdir /s /q "%USERPROFILE%\.rustup" >nul 2>nul
if exist "%USERPROFILE%\.cargo\bin" rmdir /s /q "%USERPROFILE%\.cargo\bin" >nul 2>nul
if exist "%USERPROFILE%\.cargo\registry" rmdir /s /q "%USERPROFILE%\.cargo\registry" >nul 2>nul
REM  Drop the cached installer as well, so a half-downloaded copy cannot
REM  reproduce the very same broken install.
del /q "%TEMP%\rustup-init.exe" >nul 2>nul
goto rust_install

:rust_install
if exist "%TEMP%\rustup-init.exe" goto rust_run
echo       Downloading rustup-init.exe from the Tsinghua mirror...
powershell -NoProfile -Command "Invoke-WebRequest -Uri '%RUSTUP_INIT_URL%' -OutFile ('%TEMP%\rustup-init.exe')"
if errorlevel 1 goto rust_dl_fail

:rust_run
echo       Installing Rust with the MSVC toolchain...
"%TEMP%\rustup-init.exe" -y --default-toolchain stable-x86_64-pc-windows-msvc --profile default
if errorlevel 1 goto rust_fail
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
rustup default stable-x86_64-pc-windows-msvc >nul 2>nul
goto rust_verify

:rust_verify
set "RUST_HOST="
for /f "tokens=2" %%h in ('rustc -vV 2^>nul ^| findstr /b /c:"host:"') do set "RUST_HOST=%%h"
if not defined RUST_HOST goto rust_fail
echo !RUST_HOST! | findstr /i "windows-msvc" >nul
if errorlevel 1 goto rust_fail
call :rust_probe
if errorlevel 1 goto rust_link_fail
goto rust_ok

:rust_dl_fail
echo       [ERROR] Failed to download rustup-init.exe.
echo       This script uses the Tsinghua mirror:
echo         %RUSTUP_INIT_URL%
echo       If that mirror is unreachable from here, download the installer
echo       yourself from https://win.rustup.rs/x86_64 and save it as
echo       %TEMP%\rustup-init.exe, then run this script again.
pause
exit /b 1

:rust_fail
echo       [ERROR] Rust installation failed. See https://www.rust-lang.org/tools/install
pause
exit /b 1

:rust_link_fail
echo       [ERROR] Rust is installed but cannot link a test program.
echo       The MSVC linker is not reachable. Install the
echo       "Desktop development with C++" workload from Visual Studio
echo       Build Tools, reboot, then run this script again.
pause
exit /b 1

:rust_ok
echo       Rust ready.

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

REM --- 5. Install dora-cli (force 0.5.0, remove old versions) ---
echo.
echo [5/6] Installing dora-cli (version 0.5.0, matching dora-node-api 0.5.0)...
set "DORA_FOUND="
REM  "dora --version" prints three lines (dora-cli / dora-message / dora-rs
REM  (Python)). Keep only the dora-cli one, so the Python package on PATH can
REM  never be mistaken for the CLI (that would skip a needed install).
for /f "usebackq delims=" %%v in (`dora --version 2^>nul ^| findstr /i /c:"dora-cli"`) do set "DORA_VER=%%v"
if not defined DORA_VER if exist "%USERPROFILE%\.cargo\bin\dora.exe" (
    for /f "usebackq delims=" %%v in (`"%USERPROFILE%\.cargo\bin\dora.exe" --version 2^>nul ^| findstr /i /c:"dora-cli"`) do set "DORA_VER=%%v"
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
echo       The dora-rs package will be installed into the venv by 3-Deploy_Demo.bat.

:ver_check
REM --- Version check ---
echo.
echo ============================================
echo   Environment setup finished. Versions:
echo ============================================
for /f "delims=" %%i in ('rustc --version 2^>nul') do set "VER_RUSTC=%%i"
for /f "delims=" %%i in ('cargo --version 2^>nul') do set "VER_CARGO=%%i"
for /f "delims=" %%i in ('uv --version 2^>nul') do set "VER_UV=%%i"
for /f "delims=" %%i in ('dora --version 2^>nul ^| findstr /i /c:"dora-cli"') do set "VER_DORA=%%i"
if not defined VER_DORA for /f "delims=" %%i in ('dora --version 2^>nul') do set "VER_DORA=%%i"
for /f "tokens=2" %%i in ('rustc -vV 2^>nul ^| findstr /b /c:"host:"') do set "VER_HOST=%%i"
echo   rustc : !VER_RUSTC!
echo   cargo : !VER_CARGO!
echo   rustc host : !VER_HOST!
echo   uv    : !VER_UV!
echo   dora  : !VER_DORA!
echo.
echo   NOTE: Close and reopen this terminal for PATH to take effect globally.
echo         If any version shows empty, re-run this script in a new terminal.
echo.
pause
exit /b 0

REM ============================================================================
REM  Subroutines
REM ============================================================================

REM  :rust_probe -- compile and link a trivial Rust program, to test the
REM  toolchain for real rather than trusting file paths. Sets errorlevel.
REM  "call" is deliberate: running a .bat without it transfers control away and
REM  would silently abort this script, if rustc ever resolves to a wrapper.
:rust_probe
set "_RP_OLD=%CD%"
cd /d "%TEMP%" 2>nul
echo fn main(){} > _ah_rs_probe.rs
call rustc -O _ah_rs_probe.rs -o _ah_rs_probe.exe >nul 2>&1
set "_RP_RC=%errorlevel%"
del /q _ah_rs_probe.rs >nul 2>nul
del /q _ah_rs_probe.exe >nul 2>nul
del /q _ah_rs_probe.pdb >nul 2>nul
cd /d "%_RP_OLD%" >nul 2>nul
exit /b %_RP_RC%
