"""Build a small standalone ZIP with byte-pinned historical kernels."""
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
    names = sorted(set(pins) | {str(p.relative_to(ROOT)) for p in HERE.iterdir() if p.is_file() and p.name != 'PACKAGE.json'})
    package = {'version': 'lambda-radius-1.0.0', 'parent_commit': 'd7e3a83aab28dddee9ab02faf0e98f6d3a66e330',
               'cpu_limits_hours': {'aux': 2, '2076': 20, '2077': 20}, 'host_wall_limit_hours': 8,
               'files': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names}}
    (HERE / 'PACKAGE.json').write_text(json.dumps(package, indent=2) + '\n')
    names.append(str((HERE / 'PACKAGE.json').relative_to(ROOT)))
    target = ROOT / 'releases/memetik/lambda_radius_1_0_0.zip'
    start = '''from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parent
cli = root / "experiments/memetik/lambda_radius_1_0_0/run.py"
run = Path.home() / "conway99_workspace/ryzen_lambda_radius_100_20260926"
if run.exists():
    raise SystemExit("Run exists; use its frozen run.py launch/status. No overwrite performed.")
for action in ("prepare", "launch"):
    subprocess.run([sys.executable, str(cli), action, str(run)], check=True)
print("Autonomous controls, depth3, depth4 launched. Log:", run / "controller.log")
'''
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in names:
            info = zipfile.ZipInfo('lambda_radius_1_0_0/' + name, date_time=(2026, 9, 26, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, (ROOT / name).read_bytes())
        info = zipfile.ZipInfo('lambda_radius_1_0_0/start.py', date_time=(2026, 9, 26, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, start)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    Path(str(target) + '.sha256').write_text(digest + '  ' + target.name + '\n')
    print(json.dumps({'file': str(target), 'bytes': target.stat().st_size, 'sha256': digest}))


if __name__ == '__main__':
    main()
