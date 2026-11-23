"""Compare C++ cross-product options to direct Fraction arithmetic and literal set-neighbourhood capacities."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import random
import subprocess
import own_local

BASE = Path(__file__).resolve().parent
def main():
    cid,parity = 306,1
    chart = own_local.Chart(cid,parity)
    rows = (BASE/'jobs/306.0/setup.txt').read_text().splitlines()
    count = int(rows[16])
    data = []
    r,m = chart.rank,11-chart.rank
    for line in rows[17:17+count]:
        row = list(map(int,line.split()))
        y,positive,negative,norm,real_norm = row[:5]
        key = tuple(row[5+m:17+m])
        fstart = 17+m+2*r
        f = row[fstart:fstart+12]
        data.append(dict(label=y,positive=positive,negative=negative,key=key,f=f))
    assert len(data) == count
    first = tuple(map(int,(BASE/'jobs/306.0/stars.txt').read_text().splitlines()[0].split()))
    star = [first[2*i:2*i+2] for i in range(12)]
    keys = {y:chart.outer_keys(star,y) for y in own_local.OUTER}
    choices = [[] for _ in own_local.OUTER]
    for index,a in enumerate(data):
        y = own_local.OUTER[a['label']]
        for support,signs in keys[y].get(a['key'],[]):
            choices[a['label']].append((index,support,signs))
    assert all(choices)
    rng = random.Random(20261122)
    queries = []
    for _ in range(1600):
        i,j = rng.sample(range(30),2)
        queries.append((rng.choice(choices[i]),rng.choice(choices[j])))
    # Also check symmetry and cached versus uncached order.
    queries += [(b,a) for a,b in queries]
    def reference(x,y):
        a,b = data[x[0]],data[y[0]]
        ya,yb = own_local.OUTER[a['label']],own_local.OUTER[b['label']]
        va = [int(k == ya[0])+(-1)**ya[2]*int(k == ya[1]) for k in range(6)]
        vb = [int(k == yb[0])+(-1)**yb[2]*int(k == yb[1]) for k in range(6)]
        z = sum(u*v for u,v in zip(va,vb))
        common_axes = len(set(ya[:2]) & set(yb[:2]))
        overlap = x[1]&y[1]
        dot = overlap.bit_count()-2*((x[2]^y[2])&overlap).bit_count()
        twice = 1-common_axes-dot
        if twice < 0 or twice > 4 or twice%2:
            return 0
        t = twice//2
        qa = sum(a['f'][i]*chart.Finv[i][j]*a['f'][j] for i in range(12) for j in range(12))
        qb = sum(b['f'][i]*chart.Finv[i][j]*b['f'][j] for i in range(12) for j in range(12))
        cross = sum(a['f'][i]*chart.Finv[i][j]*b['f'][j] for i in range(12) for j in range(12))
        pivot = sum(a['f'][i]*chart.Qinv[ii][jj]*b['f'][j] for ii,i in enumerate(chart.piv) for jj,j in enumerate(chart.piv))%7
        answer = 0
        for link in (-1,1) if t == 1 else (0,):
            if (-4*link-z-cross)**2 > (10-qa)*(10-qb):
                continue
            graph = [set(j for j in range(39) if row>>j&1) for row in chart.A]+[set() for _ in range(4)]
            for index,mask in enumerate([a['positive'],a['negative'],b['positive'],b['negative']],39):
                for vertex in range(39):
                    if mask>>vertex&1:
                        graph[index].add(vertex)
                        graph[vertex].add(index)
            edges = []
            if t == 2 or link == 1:
                edges += [(39,41),(40,42)]
            if t == 2 or link == -1:
                edges += [(39,42),(40,41)]
            for i,j in edges:
                graph[i].add(j)
                graph[j].add(i)
            if any(len(graph[i]&graph[j]) > (1 if j in graph[i] else 2) for i in range(43) for j in range(i+1,43)):
                continue
            answer |= 1 << ((-4*link-z-pivot)%7)
        return answer
    query_text = ''.join(' '.join(map(str,a+b))+'\n' for a,b in queries)
    (BASE/'pair_controls_input.txt').write_text(query_text)
    command = ['wsl.exe','--distribution','Ubuntu-24.04','--cd',str(BASE),'--exec',
               './pair_probe_v1_checked','jobs/306.0/setup.txt']
    result = subprocess.run(command,input=query_text,text=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    (BASE/'pair_controls.stdout').write_text(result.stdout)
    (BASE/'pair_controls.stderr').write_text(result.stderr)
    assert result.returncode == 0 and 'runtime error:' not in result.stderr
    actual = list(map(int,result.stdout.split()))
    assert len(actual) == len(queries)
    positive = 0
    for index,(a,b) in enumerate(queries):
        expected = reference(a,b)
        assert actual[index] == expected, (index,a,b,actual[index],expected)
        positive += expected != 0
    assert positive > 0 and positive < len(queries)
    report = dict(status='EXACT_PAIR_CONTROLS_PASS',cases=len(queries),positive=positive,negative=len(queries)-positive,
                  method='Direct Fraction projection, set-neighbourhood graph, exact modular pivot product; includes reversed pairs/cache reuse')
    report['hashes'] = {p:hashlib.sha256((BASE/p).read_bytes()).hexdigest() for p in
                       ['residual_gram_v1.cpp','pair_probe_v1.cpp','pair_probe_v1_checked','validate_pairs_v1.py',
                        'pair_controls_input.txt','pair_controls.stdout']}
    (BASE/'pair_controls_result.json').write_text(json.dumps(report,indent=4))
    print(json.dumps(report))

if __name__ == '__main__':
    main()
