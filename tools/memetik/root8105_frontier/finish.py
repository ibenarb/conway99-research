"""Complete missing records in private local staging, then seal one final receipt."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from widths import save

repo = Path(__file__).resolve().parents[3]
output = repo / 'docs/augmentation/root8105_frontier_20261006'
staging = Path(tempfile.mkdtemp(prefix='root8105-frontier-'))
archive = output / 'FRONTIER_DATA.zip'
if archive.exists():
    with zipfile.ZipFile(archive) as saved:
        assert all('/' not in name and '\\' not in name for name in saved.namelist())
        saved.extractall(staging)
for path in output.iterdir():
    if path.is_file() and path.name != 'FRONTIER_DATA.zip' and not (staging / path.name).exists():
        shutil.copyfile(path, staging / path.name)
records = {}
for path in sorted(staging.glob('*.json')):
    value = json.loads(path.read_text())
    if value.get('complete') is False:
        records[path.name] = {'saved_records': len(value['results']),
                              'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
save(staging / 'RESUME_STATE.json', {
    'incomplete_inputs': records,
    'missing_F_records': sum(71-r['saved_records'] for n,r in records.items() if n.endswith('_F.json')),
    'action': 'private temporary staging; preserve completed records; compute only missing records'})
for script in ['widths.py', 'membership.py', 'certify_dead.py']:
    subprocess.run([sys.executable, str(Path(__file__).with_name(script)), '--repo', str(repo),
                    '--output', str(staging)], check=True)
widths = [json.loads(p.read_text()) for p in sorted(staging.glob('*_widths.json'))]
counts = [json.loads(p.read_text()) for p in sorted(staging.glob('*_F.json'))]
proofs = [json.loads(p.read_text()) for p in sorted(staging.glob('*_exclusion.json'))]
assert len(widths) == len(counts) == len(proofs) == 17
assert all(r['complete'] and len(r['results']) == 71 for r in widths + counts)
assert all(p['status'] == 'RUP_VERIFIED_UNSAT' for p in proofs)
receipt = {'complete': True, 'widths': widths, 'F_counts': counts, 'exclusions': proofs,
           'artifact_sha256': {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(staging.iterdir()) if p.is_file() and p.name != 'FINAL_RECEIPT.json'}}
receipt['payload_sha256'] = hashlib.sha256(json.dumps(receipt, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
save(staging / 'FINAL_RECEIPT.json', receipt)
for path in staging.iterdir():
    if path.is_file():
        shutil.copyfile(path, output / path.name)
assert json.loads((output / 'FINAL_RECEIPT.json').read_text()) == receipt
assert all(hashlib.sha256((output / name).read_bytes()).hexdigest() == value
           for name, value in receipt['artifact_sha256'].items())
print(json.dumps({'status':'FRONTIER_COMPLETE_SEALED','prefixes':17,'targets':1207,
                  'proposal_sum':sum(x['proposal_width'] for r in widths for x in r['results']),
                  'F_sum':sum(x['F_width'] for r in counts for x in r['results']),
                  'zero_targets':sum(x['proposal_width']==0 for r in widths for x in r['results']),
                  'independent_prefix_exclusions':len(proofs), 'staging':str(staging)}),flush=True)
