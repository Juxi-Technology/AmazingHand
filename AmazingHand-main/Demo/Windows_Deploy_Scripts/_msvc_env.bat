@echo off
REM ============================================================================
REM  _msvc_env.bat  --  internal helper for the AmazingHand Windows deploy kit
REM
REM  Loads the MSVC C++ toolchain (cl.exe / link.exe / headers / libs) into the
REM  CURRENT cmd session. The Rust MSVC toolchain needs a working linker to
REM  build AHControl, and dora build runs cargo for you.
REM
REM  Called by: 1-Install_Env.bat, 3-Deploy_Demo.bat, 4-Run_Demo.bat
REM
REM  NOTE: do NOT add setlocal to this file. PATH/LIB/INCLUDE are set here and
REM  must propagate back to the caller; setlocal would throw them away. For the
REM  same reason this file uses plain %VAR% expansion, never !VAR!.
REM
REM  Exit code: 0 = MSVC usable in this session, 1 = not usable
REM ============================================================================

set "_MSVC_RC=1"
set "_VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
set "_VCVARS="

REM --- 1. Locate vcvars64.bat -------------------------------------------------
if not exist "%_VSWHERE%" goto have_vcvars
REM  "-products *" is REQUIRED. A standalone "Build Tools" install is hidden from
REM  vswhere by default, so without it vswhere prints nothing and MSVC is wrongly
REM  reported as missing. Most machines with only Build Tools hit exactly that.
for /f "usebackq delims=" %%i in (`"%_VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2^>nul`) do call :take_vcvars "%%i"

:have_vcvars
if not defined _VCVARS call :scan_vcvars

REM --- 2. Load it -------------------------------------------------------------
REM  Loaded whenever it was found, even if cl.exe already happens to be on PATH:
REM  cl.exe alone does not mean INCLUDE/LIB are set, so a bare cl check is not
REM  enough to call the environment ready. Calling vcvars twice is harmless.
if not defined _VCVARS goto msvc_env_check
echo       Loading MSVC environment: %_VCVARS%
call "%_VCVARS%" >nul 2>nul

REM --- 3. Verify by actually compiling and linking ----------------------------
:msvc_env_check
call :cl_probe
if not errorlevel 1 set "_MSVC_RC=0"

exit /b %_MSVC_RC%

REM ============================================================================
REM  :take_vcvars <vs-install-path> -- remember vcvars64.bat if it is there.
REM ============================================================================
:take_vcvars
if exist "%~1\VC\Auxiliary\Build\vcvars64.bat" set "_VCVARS=%~1\VC\Auxiliary\Build\vcvars64.bat"
goto :eof

REM ============================================================================
REM  :cl_probe -- compile and link a trivial C program, to test the toolchain
REM  for real rather than guessing from file paths. Sets errorlevel from cl.
REM ============================================================================
:cl_probe
set "_CL_PROBE_OLD=%CD%"
cd /d "%TEMP%" 2>nul
echo int ah_helper(void){return 7;} > _ah_cl_a.c
echo int ah_helper(void);int main(void){return ah_helper();} > _ah_cl_b.c
cl /nologo _ah_cl_a.c _ah_cl_b.c /Fe:_ah_cl.exe >nul 2>&1
set "_CL_PROBE_RC=%errorlevel%"
del /q _ah_cl_a.c >nul 2>nul
del /q _ah_cl_b.c >nul 2>nul
del /q _ah_cl_a.obj >nul 2>nul
del /q _ah_cl_b.obj >nul 2>nul
del /q _ah_cl.exe >nul 2>nul
cd /d "%_CL_PROBE_OLD%" >nul 2>nul
exit /b %_CL_PROBE_RC%

REM ============================================================================
REM  :scan_vcvars -- fallback when vswhere is absent or silent.
REM  Walks a short list of usual install roots looking for vcvars64.bat.
REM ============================================================================
:scan_vcvars
for %%r in ("%ProgramFiles%" "%ProgramFiles(x86)%" "D:\Microsoft Visual Studio" "D:\Program Files" "D:\Program Files (x86)") do call :scan_root "%%~r"
goto :eof

:scan_root
if defined _VCVARS goto :eof
if not exist "%~1" goto :eof
for /d %%y in ("%~1\Microsoft Visual Studio\*") do call :take_vcvars "%%~y"
if defined _VCVARS goto :eof
for /d %%y in ("%~1\BuildTools\*") do call :take_vcvars "%%~y"
if defined _VCVARS goto :eof
for /d %%y in ("%~1\Microsoft Visual Studio\*") do call :scan_nested "%%~y"
goto :eof

:scan_nested
if defined _VCVARS goto :eof
if not exist "%~1\" goto :eof
for /d %%y in ("%~1\*") do call :take_vcvars "%%~y"
goto :eof
