# AmazingHand 清理辅助：恢复 dataflow 与 main.rs 的默认端口配置
# 由 0-清理项目.bat 调用
param([string]$DemoDir)

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

# 恢复 yml 的 --serialport 为默认值
$ymlFiles = @(
    'dataflow_tracking_real_right.yml',
    'dataflow_tracking_real_left.yml',
    'dataflow_tracking_real_2hands.yml'
)
foreach ($f in $ymlFiles) {
    $path = Join-Path $DemoDir $f
    if (-not (Test-Path $path)) { continue }
    $content = [System.IO.File]::ReadAllText($path)
    $newContent = $content -replace '--serialport\s+\S+', '--serialport /dev/ttyACM0'
    [System.IO.File]::WriteAllText($path, $newContent, $utf8NoBom)
    Write-Output ("已恢复 {0}" -f $f)
}

# 恢复 main.rs 的 serialport 默认值（不触碰 baudrate 与 config 路径）
$mainRs = Join-Path $DemoDir 'AHControl\src\main.rs'
if (Test-Path $mainRs) {
    $content = [System.IO.File]::ReadAllText($mainRs)
    $newContent = [regex]::Replace(
        $content,
        '#\[arg\(short, long, default_value = "(?!config/)[^"]*"\)\]',
        '#[arg(short, long, default_value = "/dev/ttyACM0")]'
    )
    [System.IO.File]::WriteAllText($mainRs, $newContent, $utf8NoBom)
    Write-Output '已恢复 AHControl\src\main.rs'
}
