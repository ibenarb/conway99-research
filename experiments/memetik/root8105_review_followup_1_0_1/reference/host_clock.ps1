param([string]$OutputPath, [string]$StopPath)
$clock = [System.Diagnostics.Stopwatch]::StartNew()
while ($true) {
    $p = Get-Process -Id $PID
    $data = @{ pid=$PID; stopwatch_s=$clock.Elapsed.TotalSeconds; utc_s=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000.0; cpu_s=$p.TotalProcessorTime.TotalSeconds; source="Windows Stopwatch" }
    $temp = $OutputPath + ".tmp"
    [System.IO.File]::WriteAllText($temp, ($data | ConvertTo-Json -Compress))
    Move-Item -LiteralPath $temp -Destination $OutputPath -Force
    if (Test-Path -LiteralPath $StopPath) { break }
    Start-Sleep -Seconds 2
}
