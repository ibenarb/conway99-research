"""Prepare and verify C2 reference inputs; never starts a production solver."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

EXPECTED = {
    "baseline": "f9d6011c5e6eb8a0fab971fa324d159e94b8bc4526b7b17dc31ee55aee1c25ba",
    "matching": "f9d6011c5e6eb8a0fab971fa324d159e94b8bc4526b7b17dc31ee55aee1c25ba"
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    out = args.out or Path.home() / "conway99_workspace" / "c2_reference_v1" / ("prepare_" + stamp)
    out.mkdir(parents=True, exist_ok=False)
    if shutil.disk_usage(out).free < 256 * 1024**2:
        raise RuntimeError("Insufficient free disk for input generation: need 256 MiB")
    started = time.monotonic()
    steps = [
        ["test_reference.py", "--out", str(out / "controls.json")],
        ["c2_reference.py", "--k", "14", "--out", str(out / "k14")],
        ["test_reference.py", "--audit-generated", str(out / "k14"),
         "--out", str(out / "dimacs_check.json")]
    ]
    for index, step in enumerate(steps, 1):
        print("PREPARE_STATUS " + json.dumps({"step": index, "total": len(steps),
              "elapsed_seconds": round(time.monotonic() - started, 2),
              "ETA": "usually under 3 minutes; generation and checking only"}), flush=True)
        subprocess.run([sys.executable, str(source / step[0])] + step[1:], check=True)
    manifest = json.loads((out / "k14/manifest.json").read_text())
    for key, expected in EXPECTED.items():
        if manifest[key]["sha256"] != expected:
            raise RuntimeError("Reproduction hash mismatch: " + key)
    result = {"status": "C2_REFERENCE_PREPARED", "output": str(out),
              "seconds": round(time.monotonic() - started, 2), "python": platform.python_version(),
              "primary_variables": manifest["primary_variables"],
              "baseline": manifest["baseline"], "matching": manifest["matching"],
              "production_solver_runs": 0, "UNSAT_proofs": 0}
    (out / "prepare_result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("C2_REFERENCE_PREPARED " + json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
