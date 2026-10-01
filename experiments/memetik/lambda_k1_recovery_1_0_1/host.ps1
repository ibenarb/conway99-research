$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$dist = $env:CONWAY_WSL_DISTRO
if (-not $dist) { throw 'Missing WSL distro' }
$entries = @(Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss' | ForEach-Object { Get-ItemProperty $_.PSPath } | Where-Object { $_.DistributionName -eq $dist })
if ($entries.Count -ne 1) { throw 'Cannot identify unique WSL registration' }
$base = [Environment]::ExpandEnvironmentVariables($entries[0].BasePath)
$file = $entries[0].VhdFileName
if (-not $file) { $file = 'ext4.vhdx' }
$vhd = Join-Path $base $file
if (-not (Test-Path -LiteralPath $vhd -PathType Leaf)) { throw 'VHDX not found' }
$clock = [Diagnostics.Stopwatch]::StartNew()
$self = [Diagnostics.Process]::GetCurrentProcess()
$lastProbe = -100.0
$vol = $null
while ($null -ne ($line = [Console]::ReadLine())) {
    if (($clock.Elapsed.TotalSeconds - $lastProbe) -ge 15 -or $null -eq $vol) {
        $volumes = @(Get-Volume -FilePath $vhd)
        if ($volumes.Count -ne 1) { throw 'Cannot identify VHDX volume' }
        $vol = $volumes[0]
        $lastProbe = $clock.Elapsed.TotalSeconds
    }
    $self.Refresh()
    [PSCustomObject]@{
        host_seconds = $clock.Elapsed.TotalSeconds
        utc = [DateTime]::UtcNow.ToString('o')
        windows_cpu_seconds = $self.TotalProcessorTime.TotalSeconds
        windows_pid = $PID
        distribution = $dist
        vhdx = $vhd
        volume = [string]$vol.UniqueId
        physical_free_bytes = [long]$vol.SizeRemaining
        physical_total_bytes = [long]$vol.Size
    } | ConvertTo-Json -Compress
    [Console]::Out.Flush()
    if ($line -eq 'quit') { break }
}
