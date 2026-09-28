"""Rebuild the deterministic 1.2.0 PYZ from checked-in sources and reports."""
import hashlib
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOCS = ROOT / 'docs/memetik/lambda_repair_night_20260928'
WRAPPER = '''from pathlib import Path
import runpy
import sys
import tempfile
import zipfile

with tempfile.TemporaryDirectory(prefix="conway99_repair_120_") as temporary:
    with zipfile.ZipFile(sys.argv[0]) as archive:
        archive.extractall(temporary)
    sys.path.insert(0, temporary)
    runpy.run_path(str(Path(temporary) / "start.py"), run_name="__main__")
'''


def main():
    files = [p for p in sorted(HERE.iterdir()) if p.is_file() and p.name != 'PACKAGE.json']
    package = {'version': '1.2.0', 'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    (HERE / 'PACKAGE.json').write_text(json.dumps(package, sort_keys=True, indent=2) + '\n')
    release = ROOT / 'releases/memetik/Conway99_Lambda_Repair_1.2.0.pyz'
    content = {p.name: p.read_bytes() for p in files + [HERE / 'PACKAGE.json']}
    content['__main__.py'] = WRAPPER.encode()
    for name in ('PLAN_UND_BEFUND.md', 'INTEGRATION_TEST_RESULTS.json', 'VALIDATION_SCOPE.json'):
        content['validation/' + name] = (DOCS / name).read_bytes()
    content['validation/EXPERIMENT_RULES.md'] = (ROOT / 'docs/EXPERIMENT_RULES.md').read_bytes()
    content['validation/GLOBAL_CONCLUSIONS.md'] = (ROOT / 'docs/operations/GLOBAL_CONCLUSIONS.md').read_bytes()
    with zipfile.ZipFile(release, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(content.items()):
            info = zipfile.ZipInfo(name, (2026, 9, 28, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    value = hashlib.sha256(release.read_bytes()).hexdigest()
    Path(str(release) + '.sha256').write_text(value + '  ' + release.name + '\n')
    report = {'release_path': str(release.relative_to(ROOT)), 'sha256': value, 'bytes': release.stat().st_size,
              'target_host_gate': 'NOT_YET_RUN', 'cloud_tests': 'PASS', 'version': '1.2.0'}
    (DOCS / 'RELEASE.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
