# AmazingHand serial port auto-config (Windows)
# Detect COM ports -> confirm -> write into dataflow yml and AHControl/src/main.rs
$ErrorActionPreference = 'Stop'

# Change to this script's folder (Demo\Windows_Deploy_Scripts)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

# dataflow yml files are in the Demo folder, i.e. the parent of this script folder
$DemoDir = Split-Path -Parent $Root

$YmlFiles = @(
    'dataflow_tracking_real_right.yml',
    'dataflow_tracking_real_left.yml',
    'dataflow_tracking_real_2hands.yml'
)
$MainRs = Join-Path $DemoDir 'AHControl\src\main.rs'

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Write-Step([string]$msg) { Write-Host "[$msg]" -ForegroundColor Cyan }
function Write-OK([string]$msg)   { Write-Host "  $msg" -ForegroundColor Green }
function Write-Warn([string]$msg) { Write-Host "  $msg" -ForegroundColor Yellow }

function Get-ComPorts {
    # Prefer device-manager info (with device name); fall back to SerialPort.GetPortNames
    $cim = Get-CimInstance Win32_PnPEntity -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '\((COM\d+)\)\s*$' } |
        ForEach-Object {
            [PSCustomObject]@{
                Port   = $_.Name -replace '^.*\((COM\d+)\)\s*$', '$1'
                Device = $_.Name
            }
        }
    $raw = [System.IO.Ports.SerialPort]::GetPortNames() | ForEach-Object {
        [PSCustomObject]@{ Port = $_; Device = $_ }
    }
    # Merge and de-duplicate, device description preferred
    $seen = @{}
    $result = @()
    foreach ($p in @($cim) + @($raw)) {
        if ($p.Port -and -not $seen.ContainsKey($p.Port)) {
            $seen[$p.Port] = $true
            $result += $p
        }
    }
    return $result
}

function Backup-File([string]$path) {
    if (Test-Path $path) {
        Copy-Item -Path $path -Destination "$path.bak" -Force
        Write-OK "Backed up $([System.IO.Path]::GetFileName($path)) -> $([System.IO.Path]::GetFileName($path)).bak"
    }
}

function Write-Port {
    param([string]$Port)
    $ok = 0
    foreach ($f in $YmlFiles) {
        $path = Join-Path $DemoDir $f
        if (-not (Test-Path $path)) { Write-Warn "Skipped (not found): $f"; continue }
        Backup-File $path
        $content = [System.IO.File]::ReadAllText($path)
        # Replace the value after --serialport (args line and trailing comment stay consistent)
        $newContent = $content -replace '--serialport\s+\S+', ('--serialport ' + $Port)
        [System.IO.File]::WriteAllText($path, $newContent, $utf8NoBom)
        Write-OK "Updated $f : --serialport $Port"
        $ok++
    }

    if (Test-Path $MainRs) {
        Backup-File $MainRs
        $content = [System.IO.File]::ReadAllText($MainRs)
        # Only replace the serialport default_value; leave baudrate(default_value_t) and config path alone
        $newContent = [regex]::Replace($content, '#\[arg\(short, long, default_value = "(?!config/)[^"]*"\)\]', ('#[arg(short, long, default_value = "' + $Port + '")]'))
        [System.IO.File]::WriteAllText($MainRs, $newContent, $utf8NoBom)
        Write-OK "Updated AHControl\src\main.rs : serialport default = $Port"
        $ok++
    } else {
        Write-Warn "AHControl\src\main.rs not found, skipped (check Demo folder structure)"
    }

    Write-Host ""
    if ($ok -gt 0) {
        Write-OK "Serial port configured ($ok file(s))."
        Write-Warn "Hint: if AHControl was built before, re-run 3-Deploy_Demo.bat so the main.rs change takes effect."
    } else {
        Write-Warn "Nothing was written. Check the project structure."
    }
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AmazingHand Serial Port Setup (Windows)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Interaction loop: wait for connection -> detect -> confirm -> write
$port = $null
while ($true) {
    Write-Step "Waiting for the hand to connect"
    Write-Host "  Connect the servo driver board to the PC with USB, then press Enter to scan..." -ForegroundColor Yellow
    Read-Host "  Press Enter to continue" | Out-Null

    Write-Step "Detecting COM ports"
    $ports = @(Get-ComPorts)
    if ($ports.Count -eq 0) {
        Write-Warn "No COM port detected. Please check:"
        Write-Warn "  1) The driver board is powered and the USB cable is connected;"
        Write-Warn "  2) The device shows under Device Manager -> Ports (COM & LPT)."
        $ans = Read-Host "  Press Enter to re-scan, type q to quit"
        if ($ans -eq 'q' -or $ans -eq 'Q') { exit 0 }
        continue
    }

    Write-OK "Detected ports:"
    for ($i = 0; $i -lt $ports.Count; $i++) {
        Write-Host ("    [{0}] {1}  ({2})" -f $i, $ports[$i].Port, $ports[$i].Device) -ForegroundColor Green
    }

    if ($ports.Count -eq 1) {
        $candidate = $ports[0].Port
        Write-Host ""
        Write-Step "Confirm port"
        $ans = Read-Host "  Detected port is $candidate. Use this one? [Enter=yes, or type another port]"
        if ($ans -eq '') { $port = $candidate } else { $port = $ans }
    } else {
        Write-Host ""
        Write-Step "Select port"
        $ans = Read-Host "  Enter port number [0-$($ports.Count-1)], or type another COM port"
        $num = 0
        if ([int]::TryParse($ans, [ref]$num)) {
            if ($num -ge 0 -and $num -lt $ports.Count) { $port = $ports[$num].Port }
            else { Write-Warn "Index out of range, try again."; continue }
        } elseif ($ans -match '^COM\d+$') {
            $port = $ans
        } else {
            Write-Warn "Could not understand input, try again."; continue
        }
    }

    if ($port -match '^COM\d+$') {
        Write-OK "Using port: $port"
        break
    } else {
        Write-Warn "Port must look like COM followed by digits (e.g. COM11). Got: $port , try again."
    }
}

Write-Host ""
Write-Step "Writing configuration"
Write-Port -Port $port
Write-Host ""
Write-Warn "Port written as a COM name. To run, use 4-Run_Demo.bat, or re-run 3-Deploy_Demo.bat."
