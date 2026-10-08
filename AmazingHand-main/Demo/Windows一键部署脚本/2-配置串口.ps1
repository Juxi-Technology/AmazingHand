# AmazingHand 串口自动配置脚本 (Windows)
# 检测舵机驱动板 COM 端口 -> 交互确认 -> 写入 dataflow yml 与 AHControl/src/main.rs
$ErrorActionPreference = 'Stop'

# 切换到脚本所在目录（Demo/Windows一键部署脚本）
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

# dataflow yml 位于 Demo 目录，即脚本所在文件夹的上一级
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
    # 优先用设备管理器信息（带设备名），兜底用 SerialPort.GetPortNames
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
    # 合并去重，保留设备描述优先
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
        Write-OK "已备份 $([System.IO.Path]::GetFileName($path)) -> $([System.IO.Path]::GetFileName($path)).bak"
    }
}

function Write-Port {
    param([string]$Port)
    $ok = 0
    foreach ($f in $YmlFiles) {
        $path = Join-Path $DemoDir $f
        if (-not (Test-Path $path)) { Write-Warn "跳过（文件不存在）：$f"; continue }
        Backup-File $path
        $content = [System.IO.File]::ReadAllText($path)
        # 替换 args: 行中的 --serialport 值（含行尾注释中相同的写法，保持一致）
        $newContent = $content -replace '--serialport\s+\S+', ('--serialport ' + $Port)
        [System.IO.File]::WriteAllText($path, $newContent, $utf8NoBom)
        Write-OK "已写入 $f : --serialport $Port"
        $ok++
    }

    if (Test-Path $MainRs) {
        Backup-File $MainRs
        $content = [System.IO.File]::ReadAllText($MainRs)
        # 仅替换 serialport 字段的 default_value；不触碰 baudrate(default_value_t) 与 config 路径
        $newContent = [regex]::Replace($content, '#\[arg\(short, long, default_value = "(?!config/)[^"]*"\)\]', ('#[arg(short, long, default_value = "' + $Port + '")]'))
        [System.IO.File]::WriteAllText($MainRs, $newContent, $utf8NoBom)
        Write-OK "已写入 AHControl\src\main.rs : serialport 默认值 = $Port"
        $ok++
    } else {
        Write-Warn "未找到 AHControl\src\main.rs，跳过（检查 Demo 目录完整性）"
    }

    Write-Host ""
    if ($ok -gt 0) {
        Write-OK "串口配置完成（共写入 $ok 个文件）。"
        Write-Warn "提示：若之前已 build 过 AHControl，请重新运行 3-部署代码.bat 使 main.rs 改动生效。"
    } else {
        Write-Warn "未写入任何文件，请检查项目结构。"
    }
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AmazingHand 串口自动配置 (Windows)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 交互循环：等待连接 -> 检测 -> 确认 -> 写入
$port = $null
while ($true) {
    Write-Step "等待灵巧手连接"
    Write-Host "  请将灵巧手舵机驱动板【用 USB 连接到电脑】，然后按回车开始检测..." -ForegroundColor Yellow
    Read-Host "  按回车继续" | Out-Null

    Write-Step "检测 COM 端口"
    $ports = @(Get-ComPorts)
    if ($ports.Count -eq 0) {
        Write-Warn "未检测到任何 COM 端口。请确认："
        Write-Warn "  1) 舵机驱动板已通电且 USB 线已连接；"
        Write-Warn "  2) 可在【设备管理器 -> 端口(COM和LPT)】中看到设备。"
        $ans = Read-Host "  按回车重新检测，输入 q 退出"
        if ($ans -eq 'q' -or $ans -eq 'Q') { exit 0 }
        continue
    }

    Write-OK "检测到以下端口："
    for ($i = 0; $i -lt $ports.Count; $i++) {
        Write-Host ("    [{0}] {1}  ({2})" -f $i, $ports[$i].Port, $ports[$i].Device) -ForegroundColor Green
    }

    if ($ports.Count -eq 1) {
        $candidate = $ports[0].Port
        Write-Host ""
        Write-Step "确认端口"
        $ans = Read-Host "  检测到的端口为 $candidate，是否为该端口？[回车=确认，或输入其它端口号]"
        if ($ans -eq '') { $port = $candidate } else { $port = $ans }
    } else {
        Write-Host ""
        Write-Step "选择端口"
        $ans = Read-Host "  输入端口编号 [0-$($ports.Count-1)]，或直接输入其它端口号"
        $num = 0
        if ([int]::TryParse($ans, [ref]$num)) {
            if ($num -ge 0 -and $num -lt $ports.Count) { $port = $ports[$num].Port }
            else { Write-Warn "编号超出范围，请重试。"; continue }
        } elseif ($ans -match '^COM\d+$') {
            $port = $ans
        } else {
            Write-Warn "无法识别输入，请重试。"; continue
        }
    }

    if ($port -match '^COM\d+$') {
        Write-OK "确认使用端口：$port"
        break
    } else {
        Write-Warn "端口号格式应为 COM 后跟数字（如 COM11），输入的内容为：$port ，请重试。"
    }
}

Write-Host ""
Write-Step "写入配置文件"
Write-Port -Port $port
Write-Host ""
Write-Warn "Windows 端口名以 COM 形式写入。如需运行，请执行 4-运行代码.bat 或重新执行 3-部署代码.bat。"
