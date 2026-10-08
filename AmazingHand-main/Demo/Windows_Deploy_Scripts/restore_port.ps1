# AmazingHand cleanup helper: restore default port in dataflow yml and AHControl/src/main.rs
# Called by 0-Cleanup_Project.bat
param([string]$DemoDir)

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

# Restore --serialport to the default value in the yml files
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
    Write-Output ("Restored {0}" -f $f)
}

# Restore the serialport default in main.rs (leave baudrate and config path alone)
$mainRs = Join-Path $DemoDir 'AHControl\src\main.rs'
if (Test-Path $mainRs) {
    $content = [System.IO.File]::ReadAllText($mainRs)
    $newContent = [regex]::Replace(
        $content,
        '#\[arg\(short, long, default_value = "(?!config/)[^"]*"\)\]',
        '#[arg(short, long, default_value = "/dev/ttyACM0")]'
    )
    [System.IO.File]::WriteAllText($mainRs, $newContent, $utf8NoBom)
    Write-Output 'Restored AHControl\src\main.rs'
}
