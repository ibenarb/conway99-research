"""Independent singleton setup from the referee's literal local model.
No Hamming-word or signed-rank branch assumption is made here.
The original search programs are neither imported nor linked.
"""
from pathlib import Path
from fractions import Fraction
from itertools import permutations
import hashlib
import json
import sys
import time
import numpy as np
import own_local
from own_local import Chart, OUTER
from own_setup import attachments_fast

BASE = Path(__file__).resolve().parent

def determinant(matrix):
    a = [[Fraction(v) for v in row] for row in matrix]
    answer = Fraction(1)
    for i in range(len(a)):
        p = next((j for j in range(i,len(a)) if a[j][i]),None)
        if p is None:
            return Fraction(0)
        if p != i:
            a[i],a[p] = a[p],a[i]
            answer = -answer
        d = a[i][i]
        answer *= d
        for j in range(i+1,len(a)):
            ratio = a[j][i]/d
            for k in range(i+1,len(a)):
                a[j][k] -= ratio*a[i][k]
    return answer

def wreath_permutations():
    rows = []
    for axes in permutations(range(6)):
        for mask in range(64):
            rows.append([2*axes[i//2]+((i%2)^((mask>>(i//2))&1)) for i in range(12)])
    result = np.array(rows,dtype=np.int16)
    assert result.shape == (46080,12)
    return result

def root_orbits(chart, retained):
    all_maps = wreath_permutations()
    p,n = np.array(chart.P),np.array(chart.N)
    group = all_maps[((all_maps[:,p] == p[all_maps]).all(axis=1)) &
                     ((all_maps[:,n] == n[all_maps]).all(axis=1))]
    assert len(group) and 46080 % len(group) == 0
    unseen = set(retained)
    representatives = []
    orbit_records = []
    while unseen:
        root = min(unseen)
        positive = [i for i in range(12) if root>>i&1]
        images = {sum(1<<int(row[i]) for i in positive) for row in group}
        images |= {4095^x for x in list(images)}
        assert images <= set(retained)
        assert images <= unseen
        representative = min(images)
        representatives.append(representative)
        orbit_records.append(dict(representative=representative,members=sorted(images)))
        unseen -= images
    assert sum(len(x['members']) for x in orbit_records) == len(retained)
    return representatives,dict(stabilizer_order=len(group),orbits=orbit_records)

def write_setup(cid, output):
    start = time.time()
    chart = Chart(cid,0)
    source = json.loads((BASE.parent/'singleton_v1/unary_result_v2.json').read_text())
    row = source['charts'][cid]
    assert row['chart'] == cid and row['physical'] == chart.physical
    if not chart.physical:
        raise ValueError('Nonphysical chart does not need a search.')
    retained = row['surviving_sign_masks']
    for mask in retained:
        g = [1 if mask>>i&1 else -1 for i in range(12)]
        assert sum(g) == 0
        assert all(sum(g[i] for i in range(12) if chart.comp[i] == c) == 0 for c in range(chart.ncomp))
        assert sum(g[i]*chart.Hinv[i][j]*g[j] for i in range(12) for j in range(12)) <= 2
        assert sum(int(g[i] == g[chart.P[i]])+int(g[i] == g[chart.N[i]]) for i in range(12))//2 in (0,2)
    roots,orbits = root_orbits(chart,retained)
    h_basis = [i for i in range(12) if i != max(j for j in range(12) if chart.comp[j] == chart.comp[i])]
    assert len(h_basis) == 12-chart.ncomp
    dh = determinant([[chart.HA[i][j] for j in h_basis] for i in h_basis])
    df = determinant([row[:11] for row in chart.FA[:11]])
    assert dh > 0 and df > 0 and dh.denominator == df.denominator == 1
    domains = attachments_fast(chart)
    entries = []
    for yi,label in enumerate(OUTER):
        for a in domains[label]:
            u = [1-int((i//2) in label[:2])-2*a['key'][i] for i in range(12)]
            assert sum(a['f']) == 0
            assert all(sum(u[i] for i in range(12) if chart.comp[i] == c) == 0 for c in range(chart.ncomp))
            entries.append((yi,a,u))
    with Path(output).open('x') as stream:
        def line(values):
            stream.write(' '.join(map(str,values))+'\n')
        line([cid,len(h_basis),dh,df,len(roots),len(entries)])
        line(roots)
        line(chart.P)
        line(chart.N)
        line(chart.A)
        for row in chart.Hinv:
            line(row)
        for row in chart.Finv:
            line(row)
        for row in chart.FA:
            line(row)
        for yi,a,u in entries:
            line([yi,a['mask'],a['twin']]+list(a['key'])+a['f']+u)
    record = dict(chart=cid,raw_root_signs=len(retained),root_representatives=len(roots),
                  orbit_audit=orbits,attachments=len(entries),
                  unsigned_patterns=len({(yi,tuple(a['key'])) for yi,a,u in entries}),
                  unsigned_star_rank=len(h_basis),signed_star_rank=11,
                  unsigned_basis_determinant=str(dh),signed_basis_determinant=str(df),
                  setup_sha256=hashlib.sha256(Path(output).read_bytes()).hexdigest(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  catalogue_sha256=hashlib.sha256((BASE/'layouts.tsv').read_bytes()).hexdigest(),
                  elapsed_seconds=time.time()-start)
    Path(str(output)+'.json').write_text(json.dumps(record,indent=4))
    print(json.dumps({k:v for k,v in record.items() if k != 'orbit_audit'}),flush=True)

if __name__ == '__main__':
    write_setup(int(sys.argv[1]),sys.argv[2])
