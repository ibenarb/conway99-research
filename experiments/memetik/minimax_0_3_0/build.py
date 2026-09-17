"""Build a deterministic, standard-library-only Office zipapp."""
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).parent
names = ['__main__.py', 'office.py', 'minimax.py', 'core.py', 'operators.py', 'search.py', 'HoG57338__bfs_F.seed.json.gz', 'B_escape_W2082__bfs_W.seed.json.gz']
manifest = {'version': 'minimax-0.3.0', 'base_research_commit': '56c1df71e0fdee8c2ca7795d19ccc63db99e7a09', 'files': {n: hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names}}
(root/'manifest.json').write_text(json.dumps(manifest, indent=4)+'\n')
target = root/'Conway99_Minimax_Office_0.3.0.pyz'
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
    for name in names+['manifest.json']:
        info = zipfile.ZipInfo(name, (2026, 9, 17, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, (root/name).read_bytes())
print(json.dumps({'file': str(target), 'bytes': target.stat().st_size, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}))
