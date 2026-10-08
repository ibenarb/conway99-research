param([Parameter(Mandatory=$true)][string]$Directory, [Parameter(Mandatory=$true)][string]$Session, [switch]$Sampler)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
public class N1AtomicFile {
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, ExactSpelling=true, SetLastError=true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool MoveFileExW(string source, string target, uint flags);
}
'@
function Write-Atomic([string]$Name, $Value) {
    $target = Join-Path $Directory $Name
    $temp = $target + '.' + [guid]::NewGuid().ToString('N') + '.tmp'
    $bytes = [Text.Encoding]::UTF8.GetBytes(($Value | ConvertTo-Json -Depth 10 -Compress))
    $stream = [IO.File]::Open($temp, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
    # Same-directory rename with replacement; never pre-delete or enable copy fallback.
    if (-not [N1AtomicFile]::MoveFileExW($temp, $target, 1)) {
        $code = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
        throw [ComponentModel.Win32Exception]::new($code)
    }
}
if ($Sampler) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class N1Memory {
    [StructLayout(LayoutKind.Sequential)]
    public struct Status {
        public uint Length, Load;
        public ulong TotalPhysical, AvailablePhysical, TotalPage, AvailablePage, TotalVirtual, AvailableVirtual, Extended;
    }
    [DllImport("kernel32.dll", SetLastError=true)]
    static extern bool GlobalMemoryStatusEx(ref Status status);
    public static ulong Available() {
        Status s = new Status(); s.Length = (uint)Marshal.SizeOf(typeof(Status));
        if (!GlobalMemoryStatusEx(ref s)) throw new System.ComponentModel.Win32Exception();
        return s.AvailablePhysical;
    }
}
'@
    $self = [Diagnostics.Process]::GetCurrentProcess()
    $birth = $self.StartTime.ToUniversalTime().Ticks.ToString()
    $sequence = 0
    do {
        $self.Refresh()
        $record = @{
            schema='N1_WINDOWS_CLOCK_1'; session_id=$Session; sequence=$sequence;
            pid=$PID; birth=$birth; frequency=[Diagnostics.Stopwatch]::Frequency;
            ticks=[Diagnostics.Stopwatch]::GetTimestamp(); utc_ticks=[DateTime]::UtcNow.Ticks;
            high_resolution=[Diagnostics.Stopwatch]::IsHighResolution;
            cpu_lower_bound_s=$self.TotalProcessorTime.TotalSeconds;
            available_physical_bytes=[N1Memory]::Available(); synthetic=$false
        }
        Write-Atomic 'heartbeat.json' $record
        $sequence += 1
        Start-Sleep -Milliseconds 250
    } while (-not [IO.File]::Exists((Join-Path $Directory 'STOP')))
    Write-Atomic 'sampler-final.json' $record
    exit 0
}
$proc = New-Object Diagnostics.Process
$proc.StartInfo.FileName = Join-Path $PSHOME 'powershell.exe'
$script64 = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($PSCommandPath))
$dir64 = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Directory))
$command = "& ([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('$script64'))) -Directory ([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('$dir64'))) -Session '$Session' -Sampler"
$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
$proc.StartInfo.Arguments = '-NoLogo -NoProfile -NonInteractive -EncodedCommand ' + $encoded
$proc.StartInfo.UseShellExecute = $false
$proc.StartInfo.CreateNoWindow = $true
$proc.StartInfo.RedirectStandardError = $true
if (-not $proc.Start()) { throw 'Host sampler failed to start' }
$stderrTask = $proc.StandardError.ReadToEndAsync()
$handle = $proc.Handle
$childId = $proc.Id
$childBirth = $proc.StartTime.ToUniversalTime().Ticks.ToString()
$proc.WaitForExit()
$stderrText = $stderrTask.GetAwaiter().GetResult()
[IO.File]::WriteAllText((Join-Path $Directory 'sampler-stderr.log'), $stderrText, [Text.Encoding]::UTF8)
$cpu = $proc.TotalProcessorTime.TotalSeconds
$owner = [Diagnostics.Process]::GetCurrentProcess()
Write-Atomic 'receipt.json' @{
    schema='N1_WINDOWS_END_1'; session_id=$Session; pid=$childId; birth=$childBirth;
    exit_code=$proc.ExitCode; sampler_cpu_end_s=$cpu;
    owner_cpu_lower_bound_s=$owner.TotalProcessorTime.TotalSeconds;
    owner_pid=$PID; owner_birth=$owner.StartTime.ToUniversalTime().Ticks.ToString();
    owner_tail_complete=$false; synthetic=$false
}
$code = $proc.ExitCode
$proc.Dispose()
exit $code
