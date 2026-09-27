"""Build deterministic source ZIP. Run from this checked-in directory."""
import hashlib
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
files = [p for p in sorted(HERE.iterdir()) if p.is_file() and p.name not in ('PACKAGE.json', 'build_release.py')]
manifest = {'version': '1.0.0', 'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(HERE / 'PACKAGE.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
release = ROOT / 'releases/memetik/lambda_repair_1_0_0.zip'
release.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(release, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in sorted(files + [HERE / 'PACKAGE.json']):
        info = zipfile.ZipInfo('lambda_repair_1_0_0/' + path.name, (2026, 9, 27, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, path.read_bytes())
value = hashlib.sha256(release.read_bytes()).hexdigest()
release.with_suffix('.zip.sha256').write_text(value + '  ' + release.name + '\n')
print(json.dumps({'archive': str(release), 'sha256': value, 'bytes': release.stat().st_size}))
