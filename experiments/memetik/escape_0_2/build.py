"""Reproducible dependency-free Office zipapp; optional analysis tools excluded."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
FILES = ('__main__.py', 'core.py', 'operators.py', 'search.py', 'runner.py', 'founders.json')
manifest = {'version': 'escape-0.2.1', 'base_commit': 'abc752d04bd0d72c3fd83fe8aaf4fe5ae3caa37e', 'files': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES}}
(ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=4) + '\n')
output = ROOT.parents[2] / 'releases/Conway99_Escape_Office_0.2.1.pyz'
with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for name in FILES + ('manifest.json',):
        info = zipfile.ZipInfo(name, (2026, 9, 16, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, (ROOT / name).read_bytes())
print(str(output))
print(hashlib.sha256(output.read_bytes()).hexdigest())
