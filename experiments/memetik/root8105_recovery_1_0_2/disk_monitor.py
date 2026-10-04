"""Incremental, bounded directory scanning; OS free-space checks remain per tick."""
import json
import os
import time
from pathlib import Path


class DiskMonitor:
    def __init__(self, directory, max_entries=4096, slice_s=0.05, interval_s=300):
        self.directory = Path(directory)
        previous = self.directory / 'status.json'
        self.high_water = json.loads(previous.read_text()).get('run_disk_bytes', 0) if previous.exists() else 0
        self.max_entries = max_entries
        self.slice_s = slice_s
        self.interval_s = interval_s
        self.iterator = None
        self.next_scan = 0
        self.partial = 0
        self.entries = 0
        self.scans = 0
        self.last_complete_unix = None
        self.cpu_s = 0.0

    def walk(self, directory):
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    try:
                        is_dir = entry.is_dir(follow_symlinks=False)
                        size = 0 if is_dir else entry.stat(follow_symlinks=False).st_size
                    except FileNotFoundError:
                        continue
                    yield size
                    if is_dir:
                        yield from self.walk(entry.path)
        except FileNotFoundError:
            return

    def step(self):
        started_cpu = time.process_time()
        started_wall = time.monotonic()
        if self.iterator is None:
            if started_wall < self.next_scan:
                return self.high_water
            self.iterator = self.walk(self.directory)
            self.partial = 0
            self.entries = 0
        try:
            for _ in range(self.max_entries):
                self.partial += next(self.iterator)
                self.entries += 1
                if time.monotonic() - started_wall >= self.slice_s:
                    break
        except StopIteration:
            self.high_water = max(self.high_water, self.partial)
            self.iterator = None
            self.scans += 1
            self.last_complete_unix = time.time()
            self.next_scan = time.monotonic() + self.interval_s
        self.high_water = max(self.high_water, self.partial)
        self.cpu_s += time.process_time() - started_cpu
        return self.high_water

    def status(self):
        return {'mode': 'incremental_sampled_high_water', 'scan_in_progress': self.iterator is not None,
                'scanned_entries': self.entries, 'completed_scans': self.scans,
                'last_complete_unix': self.last_complete_unix, 'scanner_cpu_s': self.cpu_s,
                'max_entries_per_tick': self.max_entries, 'slice_wall_target_s': self.slice_s,
                'note': 'Sampled file sizes, not an instantaneous filesystem quota.'}
