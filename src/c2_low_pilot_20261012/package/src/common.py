"""Durable records and Linux identity/resource helpers; no time-limit killing."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import time

GIB = 1024 ** 3


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + str(os.getpid()) + '.writing')
    with temporary.open('w') as stream:
        json.dump(data, stream, indent=4, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def read(path, default=None):
    return json.loads(Path(path).read_text()) if Path(path).exists() else default


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 ** 2), b''):
            result.update(block)
    return result.hexdigest()


def identity(path):
    path = Path(path).resolve()
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def lock(path):
    stream = Path(path).open('a+')
    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return stream


def proc(pid):
    """Resolve namespace PID also in the development environment's host /proc."""
    try:
        own_host = int(Path('/proc/self/stat').read_text().split()[0])
        actual = pid
        if own_host != os.getpid():
            own_ns = os.readlink('/proc/self/ns/pid')
            actual = None
            for path in Path('/proc').iterdir():
                if not path.name.isdigit():
                    continue
                try:
                    if os.readlink(path / 'ns/pid') != own_ns:
                        continue
                    status = (path / 'status').read_text().splitlines()
                    ns = next(line for line in status if line.startswith('NSpid:'))
                    if int(ns.split()[-1]) == pid:
                        actual = int(path.name)
                        break
                except (OSError, StopIteration, ValueError):
                    continue
            if actual is None:
                return None
        data = Path(f'/proc/{actual}/stat').read_text()
        fields = data[data.rfind(')') + 2:].split()
        try:
            io = {k: int(v) for k,v in (line.split(':') for line in Path(f'/proc/{actual}/io').read_text().splitlines())}
        except OSError:
            io = {}
        return {'io': io, 'pid': pid, 'birth': fields[19], 'state': fields[0],
                'boot': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                'namespace': os.readlink('/proc/self/ns/pid'),
                'cpu_s': (int(fields[11]) + int(fields[12])) / os.sysconf('SC_CLK_TCK'),
                'rss_bytes': int(fields[21]) * os.sysconf('SC_PAGE_SIZE')}
    except (OSError, ValueError):
        return None


def alive(saved):
    if not saved:
        return False
    live = proc(saved['pid'])
    return bool(live and live['birth'] == saved['birth'] and live.get('boot') == saved.get('boot') and live.get('namespace') == saved.get('namespace') and live['state'] not in ('Z', 'X'))


_windows_cache = [0.0, None]

def host(work):
    values = dict((line.split(':')[0], line.split(':')[1].strip())
                  for line in Path('/proc/meminfo').read_text().splitlines())
    wsl = 'microsoft' in Path('/proc/sys/kernel/osrelease').read_text().lower()
    if wsl and not Path('/mnt/c').is_mount():
        raise RuntimeError('WSL Windows C mount missing; cannot monitor physical disk')
    linux_ram = int(values['MemAvailable'].split()[0]) * 1024 / GIB
    linux_available = linux_ram
    if wsl:
        import subprocess
        if time.monotonic() - _windows_cache[0] > 10:
            exe = '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
            result = subprocess.run([exe, '-NoProfile', '-NonInteractive', '-Command',
                '[Console]::Write((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory)'],
                capture_output=True, text=True, timeout=8, check=True)
            _windows_cache[:] = [time.monotonic(), int(result.stdout.strip()) * 1024 / GIB]
        linux_ram = min(linux_ram, _windows_cache[1])
    vm = dict(line.split() for line in Path('/proc/vmstat').read_text().splitlines())
    pressure = {}
    try:
        for line in Path('/proc/pressure/memory').read_text().splitlines():
            parts = line.split()
            pressure[parts[0]] = dict(x.split('=') for x in parts[1:])
    except OSError:
        pressure = {'unavailable': True}
    return {'available_ram_gib': linux_ram,
            'linux_available_ram_gib': linux_available,
            'windows_available_ram_gib': _windows_cache[1] if wsl else None,
            'swap_used_gib': (int(values['SwapTotal'].split()[0]) - int(values['SwapFree'].split()[0])) * 1024 / GIB,
            'swap_in_pages': int(vm.get('pswpin', 0)), 'swap_out_pages': int(vm.get('pswpout', 0)),
            'memory_pressure': pressure,
            'linux_free_gib': shutil.disk_usage(work).free / GIB,
            'windows_c_free_gib': shutil.disk_usage('/mnt/c').free / GIB if wsl else None,
            'loadavg': list(os.getloadavg()), 'logical_cpus': os.cpu_count()}


def cpu_clock():
    numbers = list(map(int, Path('/proc/stat').read_text().splitlines()[0].split()[1:9]))
    return sum(numbers), numbers[3] + numbers[4]


def busy_cpu(previous, current):
    total = current[0] - previous[0]
    idle = current[1] - previous[1]
    return (os.cpu_count() or 1) * max(0, total - idle) / max(1, total)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def log_has(path, marker):
    with Path(path).open(errors='replace') as stream:
        return any(part.strip() == marker for line in stream for part in line.split('\r'))


def verify_manifest(root):
    manifest = read(Path(root) / 'MANIFEST.json')
    require(isinstance(manifest, dict), 'Missing package manifest')
    for relative, expected in manifest.items():
        require(sha(Path(root) / relative) == expected, 'PACKAGE_HASH_MISMATCH: ' + relative)
