"""Task-local Lean release bootstrap. No system installation or settings change."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "work/C2_K4_Methodenpilot_20261117"))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity

sample = measure()
assert max(x["system_busy_cpu"] for x in sample["intervals"]) + 1 <= 20
assert sample["ram_free_gib"] >= 10 and sample["disk_free_gib"] >= 38
with (BASE / "bootstrap_identity_v1.json").open("x") as file:
    json.dump({"identity": identity(os.getpid()), "started": time.time(),
               "resource": sample}, file, indent=4)
metadata = json.loads((BASE / "lean_release_metadata.json").read_text())
assert metadata["tag"] == "v4.35.0-rc2"
asset = next(x for x in metadata["assets"] if x["name"] == "lean-4.35.0-rc2-linux.zip")
assert asset["digest"] == "sha256:a5a88e074c2f321ac06c63454358294b5d128b079d540aa0af27fda8597ca9b3"
target = BASE / asset["name"]
partial = BASE / (asset["name"] + ".part")
assert not target.exists() and not partial.exists()
digest = hashlib.sha256()
with urllib.request.urlopen(asset["browser_download_url"]) as response, partial.open("xb") as file:
    while True:
        block = response.read(4 * 1024 * 1024)
        if not block:
            break
        if shutil.disk_usage(BASE).free < 36 * 2 ** 30:
            raise RuntimeError("Disk reserve: partial download retained; no extraction.")
        file.write(block)
        digest.update(block)
assert partial.stat().st_size == asset["size"]
assert digest.hexdigest() == asset["digest"].split(":")[1]
os.replace(partial, target)
with zipfile.ZipFile(target) as archive:
    members = archive.infolist()
    total = sum(info.file_size for info in members)
    record = {"verified_sha256": digest.hexdigest(), "compressed_bytes": target.stat().st_size,
              "uncompressed_bytes": total, "files": len(members)}
    (BASE / "lean_archive_verified_v1.json").write_text(json.dumps(record, indent=4))
    if shutil.disk_usage(BASE).free - total < 35.5 * 2 ** 30:
        raise RuntimeError("Extraction held: verified archive retained, disk reserve would be too small.")
    destination = BASE / "toolchain"
    destination.mkdir()
    resolved = destination.resolve()
    for info in members:
        name = info.filename.replace("\\", "/")
        candidate = (destination / name).resolve()
        assert candidate.is_relative_to(resolved)
        assert not ((info.external_attr >> 16) & 0o170000) == 0o120000
    archive.extractall(destination)
tool = destination / "lean-4.35.0-rc2-linux" / "bin" / "lean"
assert tool.is_file()
linux_tool = "/mnt/c/" + str(tool.resolve())[3:].replace("\\", "/")
result = subprocess.run(["wsl.exe", "--distribution", "Ubuntu-24.04", "--exec",
                         linux_tool, "--version"], capture_output=True, text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW)
record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr,
              finished=time.time(), tool=str(tool))
(BASE / "lean_bootstrap_result_v1.json").write_text(json.dumps(record, indent=4))
assert result.returncode == 0 and "4.35.0-rc2" in result.stdout
print("PINNED_LEAN_TOOLCHAIN_READY", flush=True)
