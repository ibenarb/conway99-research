"""Fail-closed WSL disk guard, including the physical VHDX backing volume.

No mount, resize, shutdown, process termination or system configuration changes.
The former failure was reported by the owner as host-volume exhaustion despite
free virtual ext4 space. Linux-only free-space checks are insufficient.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

GIB = 1024**3
LINUX_RESERVE = 20 * GIB
HOST_RESERVE = 50 * GIB
RAM_RESERVE = 6 * GIB
GROUP_LIMIT = 36 * GIB

# Select by the current distribution name, not a stale block-device number.
# Read the registration and the Windows filesystem directly. Do not mistake an
# absent /mnt/c mount for a filesystem with adequate free space.
WINDOWS_PROBE = r'''
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$name = '__DISTRO__'
$d = @(Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss' | ForEach-Object { Get-ItemProperty $_.PSPath } | Where-Object { $_.DistributionName -eq $name })
if ($d.Count -ne 1) { throw 'Cannot identify unique WSL registration' }
$base = [Environment]::ExpandEnvironmentVariables($d[0].BasePath)
$file = $d[0].VhdFileName
if (-not $file) { $file = 'ext4.vhdx' }
$vhd = Join-Path $base $file
if (-not (Test-Path -LiteralPath $vhd -PathType Leaf)) { throw 'VHDX not found' }
$volumes = @(Get-Volume -FilePath $vhd)
if ($volumes.Count -ne 1) { throw 'Cannot identify unique VHDX backing volume' }
$vol = $volumes[0]
[PSCustomObject]@{ distribution=$name; vhdx=$vhd; volume=$vol.UniqueId; drive_letter=[string]$vol.DriveLetter; physical_free_bytes=[long]$vol.SizeRemaining; physical_total_bytes=[long]$vol.Size } | ConvertTo-Json -Compress
'''


def physical_volume():
    distro = os.environ.get("WSL_DISTRO_NAME", "")
    if not distro or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_. " for c in distro):
        raise RuntimeError("Expected a named WSL distribution")
    command = WINDOWS_PROBE.replace("__DISTRO__", distro)
    result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                            capture_output=True, timeout=20, check=True)
    data = json.loads(result.stdout.decode("utf-8-sig"))
    if data["distribution"] != distro or not 0 <= data["physical_free_bytes"] <= data["physical_total_bytes"]:
        raise RuntimeError("Invalid host-volume response")
    return data


def memory():
    return {line.split(":")[0]: int(line.split()[1]) * 1024
            for line in Path("/proc/meminfo").read_text().splitlines()
            if line.startswith(("MemTotal:", "MemAvailable:", "SwapTotal:", "SwapFree:"))}


def snapshot(directory, *, host_probe=physical_volume):
    report = {"monotonic": time.monotonic(), "hazards": [], "may_launch": False}
    try:
        report["linux_free_bytes"] = shutil.disk_usage(directory).free
        report["host"] = host_probe()
        report["memory"] = memory()
        if report["linux_free_bytes"] < LINUX_RESERVE:
            report["hazards"].append("LINUX_DISK_RESERVE")
        if report["host"]["physical_free_bytes"] < HOST_RESERVE:
            report["hazards"].append("WINDOWS_PHYSICAL_DISK_RESERVE")
        if report["memory"]["MemAvailable"] < RAM_RESERVE:
            report["hazards"].append("HOST_RAM_RESERVE")
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        report["hazards"].append("RESOURCE_PROBE_FAILED")
        report["error"] = str(error)
    report["may_launch"] = not report["hazards"]
    return report
