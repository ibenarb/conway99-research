"""Package only pinned dependencies and this experiment; no research history."""
from pathlib import Path
import hashlib
import json
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    pins = json.loads((HERE / 'SOURCE_PINS.json').read_text())
    for name, expected in pins.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    names = sorted(set(pins) | {str(p.relative_to(ROOT)) for p in HERE.iterdir()
                               if p.is_file() and p.name != 'PACKAGE.json'})
    package = {'version': 'lambda-decision-1.0.0', 'search_cpu_hours': 60, 'maximum_total_cpu_hours': 62, 'jobs': 14,
               'files': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names}}
    (HERE / 'PACKAGE.json').write_text(json.dumps(package, indent=2) + '\n')
    names.append(str((HERE / 'PACKAGE.json').relative_to(ROOT)))
    dest = ROOT / 'releases/memetik/lambda_decision_1_0_0.zip'
    start = '''from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parent
cli = root / "experiments/memetik/lambda_decision_1_0_0/run.py"
run = Path.home() / "conway99_workspace/ryzen_lambda_decision_100_20260924"
if run.exists():
    raise SystemExit("Run already exists: use status/check/launch, do not overwrite")
for action in ("prepare", "check", "launch"):
    subprocess.run([sys.executable, str(cli), action, str(run)], check=True)
print("Background run launched. Log:", run / "controller.log")
'''
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in names:
            z.write(ROOT / name, 'lambda_decision_1_0_0/' + name)
        z.writestr('lambda_decision_1_0_0/start.py', start)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    Path(str(dest) + '.sha256').write_text(digest + '  ' + dest.name + '\n')
    print(json.dumps({'file': str(dest), 'bytes': dest.stat().st_size, 'sha256': digest, 'files': len(names) + 1}))


if __name__ == '__main__':
    main()
