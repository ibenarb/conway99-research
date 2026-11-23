"""Identity-safe resource observation without mandatory historical processes."""
from pathlib import Path
from ctypes import wintypes
import ctypes
import math
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'work/C2_K4_Methodenpilot_20261117'))
from observe_cpu_retained_handles_v4 import kernel, ticks, process_times, process_table
from c2_shared_measurement_20261118_v1 import intervals_from
from c2_serial_admission_core_20261118_v1 import identity
from h_portable_v1 import resources


def live(expected):
    try:
        return identity(expected['pid']) == expected
    except (OSError, AssertionError, ProcessLookupError):
        return False


def budget(other):
    return max(0, math.floor(24 - 4 - max(other)))


def measure(roots=()):
    assert os.cpu_count() == 24
    requested = list(roots) + [identity(os.getpid())]
    handles, known, samples = {}, set(), []
    try:
        for step in range(3):
            table = process_table()
            for pid in table:
                if pid not in handles:
                    handle = kernel.OpenProcess(0x1000, False, pid)
                    if handle:
                        handles[pid] = handle
            data = {pid: process_times(handle) for pid, handle in handles.items()}
            data = {pid: row for pid, row in data.items() if row is not None}
            current = {r['pid'] for r in requested if r['pid'] in data and
                       data[r['pid']]['created'] == r['created']}
            while True:
                larger = current | {pid for pid, row in table.items() if pid in data and
                          row['parent'] in current and row['parent'] in data and
                          data[pid]['created'] >= data[row['parent']]['created']}
                if larger == current:
                    break
                current = larger
            known.update((pid, data[pid]['created']) for pid in current)
            idle, kt, ut, clock = [wintypes.FILETIME() for _ in range(4)]
            assert kernel.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kt), ctypes.byref(ut))
            kernel.GetSystemTimeAsFileTime(ctypes.byref(clock))
            samples.append(dict(wall=time.perf_counter(), utc=ticks(clock),
                                total=ticks(kt)+ticks(ut), idle=ticks(idle),
                                processes={pid: dict(**row, name=table.get(pid, {}).get('name', 'exited-retained'))
                                           for pid, row in data.items()}))
            if step < 2:
                time.sleep(2)
    finally:
        for handle in handles.values():
            kernel.CloseHandle(handle)
    intervals = intervals_from(samples, known)
    ram, disk = resources()
    other = [r['conservative_other_cpu'] for r in intervals]
    return dict(measured_at=time.monotonic(), intervals=intervals, foreign_samples=other,
                c2_worker_budget=budget(other), ram_free_gib=ram, disk_free_gib=disk,
                reserve_cpu_equivalents=4, roots_requested=requested,
                missing_roots=[r for r in requested if not live(r)],
                limitations='Unattributed VM/Linux CPU remains conservatively foreign. Missing historical processes never imply a mathematical result or authorize a restart.')
