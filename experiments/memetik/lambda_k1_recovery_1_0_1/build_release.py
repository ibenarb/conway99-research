"""Deterministic linked K1 recovery release."""
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOCS = ROOT / 'docs/memetik/lambda_k1_recovery_20261001'
WRAPPER = '''from pathlib import Path
import runpy,sys,tempfile,zipfile
with tempfile.TemporaryDirectory(prefix="conway99_k1_recovery_101_") as temporary:
    with zipfile.ZipFile(sys.argv[0]) as archive:
        archive.extractall(temporary)
    sys.path.insert(0,temporary)
    runpy.run_path(str(Path(temporary)/"start.py"),run_name="__main__")
'''


def main():
    content = {p.name: p.read_bytes() for p in sorted(HERE.iterdir())
               if p.is_file() and p.name != 'PACKAGE.json'}
    for name in ('PLAN.md', 'VALIDATION.json'):
        content['validation/' + name] = (DOCS / name).read_bytes()
    for name, path in [('EXPERIMENT_RULES.md', ROOT / 'docs/EXPERIMENT_RULES.md'),
                       ('GLOBAL_CONCLUSIONS.md', ROOT / 'docs/operations/GLOBAL_CONCLUSIONS.md')]:
        content['validation/' + name] = path.read_bytes()
    for name, data in content.items():
        if '/' in name:
            (HERE / name).parent.mkdir(parents=True, exist_ok=True)
            (HERE / name).write_bytes(data)
    package = {'version': 'K1-recovery-1.0.1',
               'files': {n: hashlib.sha256(b).hexdigest() for n, b in content.items()}}
    (HERE / 'PACKAGE.json').write_text(json.dumps(package, sort_keys=True, indent=2) + '\n')
    content['PACKAGE.json'] = (HERE / 'PACKAGE.json').read_bytes()
    content['__main__.py'] = WRAPPER.encode()
    out = ROOT / 'releases/memetik/Conway99_Lambda_K1_Recovery_1.0.1.pyz'
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(content.items()):
            info = zipfile.ZipInfo(name, (2026, 10, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    value = hashlib.sha256(out.read_bytes()).hexdigest()
    Path(str(out) + '.sha256').write_text(value + '  ' + out.name + '\n')
    report = {'version': package['version'], 'sha256': value, 'bytes': out.stat().st_size}
    (DOCS / 'RELEASE.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
