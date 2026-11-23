from pathlib import Path
import hashlib
import json
import own_local

BASE = Path(__file__).resolve().parent
counts = json.loads((BASE/'star_counts_own.json').read_text())
entries, jobs = [], []
for cid,row in enumerate(own_local.LAY):
    if row[0] not in (8,9):
        continue
    chart = own_local.Chart(cid,0)
    assert chart.rank == row[0]
    for parity in (0,1):
        expected = counts[f'{cid},{parity}']
        record = dict(id=f'{cid}.{1-parity}',chart=cid,rank=chart.rank,own_parity=parity,
                      packet_parity=1-parity,stars=expected,determinant=chart.detQ)
        if not chart.physical:
            record['status'] = 'NONPHYSICAL_BASE'
        elif expected == 0:
            record['status'] = 'NO_SIGNED_STAR'
        else:
            record['status'] = 'FULL_SEARCH_REQUIRED'
            record['common_image'] = '57_planes' if chart.rank == 8 else ('split_all_images' if chart.detQ in (1,2,4) else '8_lines')
            jobs.append(record.copy())
        entries.append(record)
assert len(entries) == 204 and len(jobs) == 92
assert len({j['id'] for j in jobs}) == 92
assert sum(j['rank'] == 8 for j in jobs) == 6
assert sum(j['rank'] == 9 and j['determinant'] in (1,2,4) for j in jobs) == 22
assert sum(j['rank'] == 9 and j['determinant'] not in (1,2,4) for j in jobs) == 64
report = dict(status='COVERAGE_MANIFEST_PASS',jobs=jobs,all_rank8_rank9_entries=entries,
              coverage=dict(raw=204,live=92,rank8=6,rank9_nonsplit=64,rank9_split=22),
              parity='own parity = 1 - frozen packet parity',
              split_scope='One unrestricted common-image search contains both <=1 and dimension2 anchor images')
report['source_hashes'] = {p:hashlib.sha256((BASE/p).read_bytes()).hexdigest() for p in
                         ['layouts.tsv','star_counts_own.json','own_local.py','make_low_manifest_v1.py']}
target = BASE/'jobs_manifest.json'
with target.open('x') as output:
    json.dump(report,output,indent=4)
print(json.dumps(report['coverage']))
