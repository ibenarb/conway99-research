from pathlib import Path
import hashlib
import json
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'root'
DOWNLOADS = ROOT / 'downloads'
DOWNLOADS.mkdir(parents=True, exist_ok=True)
packages = ['pari-gp', 'libpari-gmp-tls8t64', 'python3-cypari2', 'python3-cysignals-pari', 'python3-numpy', 'libblas3', 'liblapack3', 'libgfortran5', 'libgmp10', 'bubblewrap', 'libcap2', 'libselinux1', 'libreadline8t64', 'libtinfo6', 'libquadmath0']
records = []
for package in packages:
    text = subprocess.check_output(['apt-cache', 'show', package], text=True).split('\n\n')[0]
    meta = dict(line.split(': ', 1) for line in text.splitlines() if ': ' in line and not line.startswith(' '))
    url = 'https://archive.ubuntu.com/ubuntu/' + meta['Filename']
    target = DOWNLOADS / Path(meta['Filename']).name
    if not target.exists():
        urllib.request.urlretrieve(url, target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    assert digest == meta['SHA256'] and target.stat().st_size == int(meta['Size'])
    subprocess.run(['dpkg-deb', '-x', str(target), str(DEST)], check=True)
    records.append(dict(package=package, version=meta['Version'], url=url, sha256=digest, bytes=target.stat().st_size))
    (ROOT / 'packages_verified.json').write_text(json.dumps(records, indent=4))
    print(package, meta['Version'], 'hash verified, extracted only into task directory', flush=True)
