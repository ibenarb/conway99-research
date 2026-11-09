"""Read-only independent resource sensor; no T20 dependency."""
from pathlib import Path
import datetime
import json
import shutil
import subprocess
import threading
import time

GIB = 1024 ** 3


def assess(sample, expected_boot, age, duration):
    reasons = []
    if not 0 <= age <= 15 or not 0 <= duration <= 10:
        reasons.append('Resource measurement stale or slow')
    if sample['boot'] != expected_boot:
        reasons.append('Boot identity changed')
    r = sample['resources']
    limits = {'linux_available': 32 * GIB, 'windows_available': 12 * GIB,
              'free_bytes': 20 * GIB}
    for key, minimum in limits.items():
        if type(r[key]) is not int or r[key] < minimum:
            reasons.append(key + ' reserve reached')
    if type(r['swap_used']) is not int or r['swap_used'] != 0:
        reasons.append('Swap in use or invalid')
    return reasons


class Sensor:
    def __init__(self, volume):
        self.volume = Path(volume).resolve()
        self.lock = threading.Lock()
        self.sample = None
        self.measured = None
        self.boot = None
        self.duration = None

    def measure(self):
        begin = time.monotonic()
        boot_before = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        command = "$x=Get-CimInstance Win32_OperatingSystem -ErrorAction Stop; @{available=([long]$x.FreePhysicalMemory*1024);boot=$x.LastBootUpTime.ToUniversalTime().ToString('o')} | ConvertTo-Json -Compress"
        result = subprocess.run([
            '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe',
            '-NoProfile', '-NonInteractive', '-Command', command],
            capture_output=True, timeout=8, check=True)
        host = json.loads(result.stdout.decode('utf-8-sig'))
        memory = {line.split(':')[0]: int(line.split()[1]) * 1024
                  for line in Path('/proc/meminfo').read_text().splitlines()}
        boot_after = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        if boot_before != boot_after or not host['boot'] or not boot_after:
            raise RuntimeError('Unstable or missing boot identity')
        sample = {
            'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source': 'independent_read_only_sensor_v1',
            'boot': {'linux': boot_after, 'windows': host['boot']},
            'volume': str(self.volume),
            'resources': {
                'linux_available': memory['MemAvailable'],
                'windows_available': host['available'],
                'free_bytes': shutil.disk_usage(self.volume).free,
                'swap_used': memory['SwapTotal'] - memory['SwapFree']}}
        return sample, time.monotonic() - begin

    def resources(self):
        with self.lock:
            try:
                if self.sample is None or time.monotonic() - self.measured >= 5:
                    sample, duration = self.measure()
                    if self.boot is None:
                        self.boot = dict(sample['boot'])
                    self.sample, self.duration = sample, duration
                    self.measured = time.monotonic()
                return self.sample, assess(self.sample, self.boot,
                    time.monotonic() - self.measured, self.duration)
            except Exception as error:
                return {'source': 'independent_read_only_sensor_v1',
                        'host_error': type(error).__name__ + ': ' + str(error),
                        'resources': {'linux_available': 0, 'windows_available': 0,
                                      'free_bytes': 0, 'swap_used': 0}}, [
                        'Resource measurement failed: ' + type(error).__name__]


if __name__ == '__main__':
    print(json.dumps(Sensor(Path(__file__).parent).resources(), indent=4))
