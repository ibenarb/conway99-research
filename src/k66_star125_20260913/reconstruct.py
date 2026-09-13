"""Reproduce all submitted star CNFs from the original deterministic generator."""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import original_preflight as g

base, source, output = map(Path, sys.argv[1:4])
root_manifest = json.loads(Path(sys.argv[4]).read_text())
root_records = []
manifest = json.loads(source.read_text())
raw, e0 = g.make_profiles(np)
Z = np.concatenate([np.column_stack((raw, np.tile(c, (936, 1)))) for c in [(1, 1), (1, 0), (0, 1), (0, 0)]])
ell = np.tile(e0, 4)
q = Z[:, 12:].sum(axis=1)
caps = np.where((ell + q) > 0, 1, 2)
cells = np.repeat(np.arange(4), 936)
coords = list(zip(*np.triu_indices(14)))
products = np.array([Z[:, i] * Z[:, j] for i, j in coords]).T
target = 12*np.eye(14, dtype=np.int64) + 6*np.ones((14, 14), dtype=np.int64)
for r in range(3):
    target[4*r:4*r+4, 4*r:4*r+4] -= 3
common = (Z, ell, q, caps, cells, products, coords, target)
jobs = {j['id']: j for j in manifest['jobs']}
roots = sorted(p.name for p in (base/'star_round_1').iterdir() if p.is_dir())
records = []
for root in roots:
    d = g.prepare_case(np, manifest['case_summary'], jobs[root], common)
    assert len(d['ids']) == g.EXPECTED_PROFILES[root]
    g.CASE_DATA[root] = d
    g.ACTIVE[root] = set(range(len(d['ids'])))
    indices = {int(gid): i for i, gid in enumerate(d['ids'])}
    for round_no in (1, 2, 3):
        removed = []
        for path in sorted((base/f'star_round_{round_no}'/root).glob('*.cnf')):
            gid = int(path.stem.split('_')[1])
            idx = indices[gid]
            assert idx in g.ACTIVE[root]
            c = g.build_star_cnf(np, root, idx)
            text = f'p cnf {c.n} {len(c.cl)}\n'+''.join(' '.join(map(str, cl))+' 0\n' for cl in c.cl)
            assert text.encode() == path.read_bytes(), str(path)
            records.append(dict(path=str(path.relative_to(base)), global_id=gid,
                                active_profiles=len(g.ACTIVE[root]), sha256=hashlib.sha256(text.encode()).hexdigest()))
            removed.append(idx)
        g.ACTIVE[root].difference_update(removed)
        summary = json.loads((base/f'star_round_{round_no}_summary.json').read_text())[root]
        assert summary['active_profiles'] == len(g.ACTIVE[root])
        assert summary['removed_this_round'] == len(removed)
    c, _, _, _ = g.encode_global(np, d, g.ACTIVE[root])
    digest = hashlib.sha256(f'p cnf {c.n} {len(c.cl)}\n'.encode())
    for clause in c.cl:
        digest.update((' '.join(map(str, clause))+' 0\n').encode())
    assert digest.hexdigest() == root_manifest['root_hashes'][root], root
    root_records.append(dict(root=root, sha256=digest.hexdigest(), active_profiles=len(g.ACTIVE[root])))
    print(root, 'STAR_AND_ROOT_RECONSTRUCTION_PASS', flush=True)
assert len(records) == 125
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(dict(status='ALL_125_BYTE_IDENTICAL_AND_7_ROOT_HASHES_MATCH', records=records, roots=root_records,
    scope='Same-generator reproduction and round dependency audit; not independent mathematical encoder proof.'), indent=2)+'\n')
