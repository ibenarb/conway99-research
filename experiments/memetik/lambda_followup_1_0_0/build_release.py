"""Build a complete small source release from exact repository files."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def main():
    source_pins = json.loads((ROOT / "docs/memetik/lambda_plan_codex_20260922/SOURCE_CHECK.json").read_text())["sha256"]
    for name, digest in source_pins.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    (HERE / "SOURCE_PINS.json").write_text(json.dumps(source_pins, indent=2) + "\n")
    names = list(source_pins)
    names += [str(p.relative_to(ROOT)) for p in HERE.iterdir()
              if p.is_file() and p.name not in ("PACKAGE.json",)]
    names += ["docs/memetik/lambda_synthesis_20260922/" + name for name in
              ("PROPOSED_MANIFEST.json", "RECORD_BANK.json", "WITNESS_CHECK.json")]
    names = sorted(set(names))
    payload = {"version": "1.0.0", "files": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names},
               "new_cpu_hours": 121, "jobs": 39, "requires": {"python": "original exact Python", "pynauty": "2.8.8.1"},
               "production_preflight": "WSL Windows host checks required"}
    (HERE / "PACKAGE.json").write_text(json.dumps(payload, indent=2) + "\n")
    names += [str((HERE / "PACKAGE.json").relative_to(ROOT))]
    out = ROOT / "releases/memetik"
    out.mkdir(parents=True, exist_ok=True)
    destination = out / "lambda_followup_1_0_0.zip"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name in names:
            info = zipfile.ZipInfo("lambda_followup_1_0_0/" + name, date_time=(2026, 9, 22, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, (ROOT / name).read_bytes())
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    Path(str(destination) + ".sha256").write_text(digest + "  " + destination.name + "\n")
    print(json.dumps({"archive": str(destination), "sha256": digest, "bytes": destination.stat().st_size, "files": len(names)}))

if __name__ == "__main__":
    main()
