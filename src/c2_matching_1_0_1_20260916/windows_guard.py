"""Independent Windows disk/heartbeat observer; targets only this campaign group."""
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid


def ps_quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def encoded(script):
    return base64.b64encode(script.encode('utf-16le')).decode()


def powershell():
    candidate = shutil.which('powershell.exe')
    if not candidate:
        candidate = '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
    if not Path(candidate).is_file():
        raise RuntimeError('Windows PowerShell unavailable; no campaign started')
    return candidate


def host_probe():
    distro = os.environ.get('WSL_DISTRO_NAME', '')
    if not distro or not distro.replace('-', '').replace('_', '').isalnum():
        raise RuntimeError('Cannot identify current WSL distribution')
    script = "$ErrorActionPreference='Stop'; $d=" + ps_quote(distro) + r""";
$r=@(Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss' | Get-ItemProperty | Where-Object DistributionName -eq $d);
if($r.Count -ne 1){throw 'Distribution registry entry missing/ambiguous'};
$letter=[regex]::Match($r[0].BasePath,'([A-Za-z]):\\').Groups[1].Value;
if(!$letter){throw 'Unsupported distribution storage path'};
$v=[System.IO.DriveInfo]::new($letter+':\');
@{distribution=$d;drive=$letter;free_bytes=$v.AvailableFreeSpace;temp=$env:TEMP;local_app_data=$env:LOCALAPPDATA;utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Compress
"""
    result = subprocess.run([powershell(), '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded(script)],
                            capture_output=True, timeout=20)
    if result.returncode:
        raise RuntimeError('Windows host probe failed: '+result.stderr.decode(errors='replace')[-1000:])
    return json.loads(result.stdout.decode('utf-8-sig').strip())


def linux_path(windows):
    if len(windows) < 3 or windows[1:3] != ':\\':
        raise ValueError('Expected absolute Windows drive path')
    return Path('/mnt') / windows[0].lower() / windows[3:].replace('\\', '/')


def make_script(directory, info, pid, run_path, floor_gib):
    killer = f"""import os,signal
p={pid}
try:
    cmd=open('/proc/'+str(p)+'/cmdline','rb').read()
    if {str(run_path).encode()!r} in cmd and os.getpgid(p)==p:
        os.killpg(p,signal.SIGTERM)
except ProcessLookupError:
    pass
except FileNotFoundError:
    pass
"""
    py = "exec(__import__('base64').b64decode('"+base64.b64encode(killer.encode()).decode()+"'))"
    prefix = '\n'.join([
        "$ErrorActionPreference='Stop'", '$dir='+ps_quote(directory), '$drive='+ps_quote(info['drive']),
        '$distro='+ps_quote(info['distribution']), '$killer='+ps_quote(py), '$floor='+str(int(floor_gib*1024**3)),
    ])
    return prefix + r"""
function State($obj) {
    $text=$obj | ConvertTo-Json -Compress
    [IO.File]::WriteAllText((Join-Path $dir 'state.tmp'),$text)
    $src=Join-Path $dir 'state.tmp'
    $dst=Join-Path $dir 'state.json'
    for($attempt=0; $attempt -lt 40; $attempt++) {
        try {
            if([IO.File]::Exists($dst)){[IO.File]::Replace($src,$dst,$null)}
            else{[IO.File]::Move($src,$dst)}
            return
        } catch [IO.IOException] {
            if($attempt -eq 39){throw}
            Start-Sleep -Milliseconds 50
        }
    }
}
while(!(Test-Path -LiteralPath (Join-Path $dir 'stop'))) {
    $reason=$null
    try {
        $free=[IO.DriveInfo]::new($drive+':\').AvailableFreeSpace
        $now=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        for($attempt=0; $attempt -lt 40; $attempt++) {
            try {
                $heartbeat=[long]([IO.File]::ReadAllText((Join-Path $dir 'heartbeat')))
                break
            } catch [IO.IOException] {
                if($attempt -eq 39){throw}
                Start-Sleep -Milliseconds 50
            }
        }
        if($free -lt $floor){$reason='WINDOWS_DISK_RESERVE'}
        elseif(($now-$heartbeat) -gt 90){$reason='CONTROLLER_HEARTBEAT_STALE'}
        State @{utc=[DateTime]::UtcNow.ToString('o');unix=$now;drive=$drive;free_bytes=$free;stop_reason=$reason}
    } catch {
        $reason='WINDOWS_GUARD_ERROR: '+$_.Exception.Message
        try {State @{utc=[DateTime]::UtcNow.ToString('o');stop_reason=$reason}} catch {}
    }
    if($reason) {
        try {
            $s=[Diagnostics.ProcessStartInfo]::new()
            $s.FileName='wsl.exe'
            $s.Arguments='-d '+$distro+' -u root --exec /usr/bin/python3 -c '+$killer
            $s.UseShellExecute=$false
            $s.CreateNoWindow=$true
            $p=[Diagnostics.Process]::Start($s)
            if(!$p.WaitForExit(15000)){$p.Kill()}
        } catch {
            try {[IO.File]::WriteAllText((Join-Path $dir 'stop_error.txt'),$_.Exception.Message)} catch {}
        }
        break
    }
    Start-Sleep -Seconds 3
}
"""


class Guard:
    def __init__(self, out, floor_gib=50):
        self.info = host_probe()
        if self.info['free_bytes'] < floor_gib*1024**3:
            raise RuntimeError('Windows disk below reserve before startup')
        self.windows_dir = self.info['local_app_data'].rstrip('\\') + '\\Conway99\\guards\\' + uuid.uuid4().hex
        self.directory = linux_path(self.windows_dir)
        self.directory.mkdir(parents=True)
        self.read_retries = 0
        self.floor_bytes = floor_gib*1024**3
        self.beat()
        script = make_script(self.windows_dir, self.info, os.getpid(), str(out), floor_gib)
        (self.directory/'watch.ps1').write_text(script)
        self.log = (self.directory/'watch.log').open('wb')
        self.proc = subprocess.Popen([powershell(), '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded(script)],
                                     stdin=subprocess.DEVNULL, stdout=self.log, stderr=subprocess.STDOUT,
                                     start_new_session=True)
        for _ in range(60):
            if (self.directory/'state.json').exists():
                try:
                    self.read()
                except BaseException:
                    self.close()
                    raise
                return
            if self.proc.poll() is not None:
                break
            time.sleep(0.25)
        self.close()
        raise RuntimeError('Independent Windows guard did not become ready')

    def beat(self):
        temporary = self.directory/'heartbeat.tmp'
        temporary.write_text(str(int(time.time())))
        temporary.replace(self.directory/'heartbeat')

    def read(self):
        path = self.directory/'state.json'
        deadline = time.monotonic()+2.0
        while True:
            try:
                state = json.loads(path.read_text(encoding='utf-8-sig'))
                break
            except (FileNotFoundError, PermissionError, json.JSONDecodeError) as exc:
                if time.monotonic() >= deadline:
                    raise RuntimeError(f'WINDOWS_GUARD_READ_FAILED path={path}: {exc}') from exc
                self.read_retries += 1
                time.sleep(0.05)
        if state.get('stop_reason'):
            raise RuntimeError(str(state['stop_reason']))
        if abs(time.time()-state['unix']) > 30:
            raise RuntimeError(f'Windows guard telemetry stale: {path}')
        if state['free_bytes'] < self.floor_bytes:
            raise RuntimeError('WINDOWS_DISK_RESERVE')
        return state

    def close(self):
        try:
            (self.directory/'stop').touch()
        finally:
            self.log.close()
