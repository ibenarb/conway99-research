"""Install a fresh C2 LOW pilot; preflight only, no production launch."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination', type=Path, default=Path.home() / 'conway99_workspace/C2_LOW_Pilot_1.0.1')
    args = p.parse_args()
    target = args.destination.resolve()
    if not target.exists():
        target.mkdir(parents=True)
        with zipfile.ZipFile(sys.argv[0]) as archive:
            for info in archive.infolist():
                if not info.filename.startswith('payload/') or info.is_dir():
                    continue
                relative = Path(info.filename).relative_to('payload')
                if '..' in relative.parts or relative.is_absolute():
                    raise RuntimeError('Invalid archive member')
                output = target / relative
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(archive.read(info))
    manifest = json.loads((target / 'MANIFEST.json').read_text())
    for relative, expected in manifest.items():
        if digest(target / relative) != expected:
            raise RuntimeError('Existing/incomplete installation differs: ' + relative)
    for binary in (target / 'bin').iterdir():
        binary.chmod(binary.stat().st_mode | 0o100)
    print('INSTALLATION_VERIFIED', target, flush=True)
    print('Preparing and checking only; no production pilot is started.', flush=True)
    subprocess.run([sys.executable, str(target / 'run.py'), 'preflight'], check=True)


if __name__ == '__main__':
    main()
