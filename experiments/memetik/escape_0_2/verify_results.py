"""Independent set-based checks of new graph witnesses and SQL checkpoints."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sqlite3


def decode(text):
    values = [ord(c)-63 for c in text.strip()]
    assert values[:1] == [63]
    n = (values[1] << 12) + (values[2] << 6) + values[3]
    assert n == 99 and len(values) == 813
    neighbors = [set() for _ in range(n)]
    bit = 0
    for j in range(1,n):
        for i in range(j):
            if values[4+bit//6] & (1 << (5-bit%6)):
                neighbors[i].add(j)
                neighbors[j].add(i)
            bit += 1
    return neighbors


def check(g6, arm):
    adj = decode(g6)
    assert all(len(row)==14 and i not in row and all(i in adj[j] for j in row) for i,row in enumerate(adj))
    if arm == 'lambda':
        assert all(len(adj[i]&adj[j])==1 for i in range(99) for j in adj[i])
    else:
        pairs = [p for p in itertools.combinations(range(14),2) if p[1]-p[0]!=7]
        assert adj[0] == set(range(1,15))
        for a in range(14):
            assert adj[a+1] == {0,(a+7)%14+1} | {i+15 for i,p in enumerate(pairs) if a in p}
        for u,pair in enumerate(pairs):
            assert adj[u+15] & set(range(15)) == {a+1 for a in pair}
            for a in range(14):
                target = 2-int(a in pair)-int((a+7)%14 in pair)
                assert sum(v+15 in adj[u+15] for v,p in enumerate(pairs) if a in p)==target
    residual = [len(adj[i]&adj[j])+int(j in adj[i])-2 for i in range(99) for j in range(i)]
    maximum = max(map(abs,residual))
    return adj, {'W':sum(r!=0 for r in residual),'L1':sum(map(abs,residual)),'F':sum(r*r for r in residual),'Linf':maximum,'Nmax':sum(abs(r)==maximum for r in residual)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    report = {'tasks':{},'witness_paths':0,'path_graph_occurrences':0,'verified_transitions':0}
    for path in sorted(args.run_dir.glob('*__*.json')):
        result = json.loads(path.read_text())
        with sqlite3.connect(path.with_suffix('.sqlite')) as db:
            assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
            count, expanded = db.execute('SELECT COUNT(*),SUM(expanded) FROM nodes').fetchone()
            assert (count,expanded)==(result['discovered'],result['expanded'])
            if result['status']=='LOCAL_MINIMUM_VERIFIED':
                census = json.loads(db.execute('SELECT census FROM nodes ORDER BY id DESC LIMIT 1').fetchone()[0])
                expected = {'4x4','4x6','6x6'} if result['arm']=='omega' else {'apex','rotation'}
                assert set(census)==expected and all(f['complete'] for f in census.values())
        witness = result.get('witness')
        if witness:
            report['witness_paths'] += 1
            prior = None
            metrics = []
            for entry in witness['path']:
                assert hashlib.sha256((entry['graph6']+'\n').encode()).hexdigest()==entry['sha256']
                adj, data = check(entry['graph6'],result['arm'])
                assert data == entry['metrics']
                metrics.append(data)
                if prior is not None:
                    revised = [set(row) for row in prior]
                    move = entry['transition']
                    for i,j in move['deleted']:
                        assert j in revised[i]
                        revised[i].remove(j)
                        revised[j].remove(i)
                    for i,j in move['added']:
                        assert j not in revised[i]
                        revised[i].add(j)
                        revised[j].add(i)
                    assert revised == adj
                    report['verified_transitions'] += 1
                prior = adj
                report['path_graph_occurrences'] += 1
            objective = result['task']['objective']
            keys = [(m['Linf'],m['Nmax'],m['L1']) if objective=='Linf' else (m[objective],) for m in metrics]
            assert len(keys)-1 == witness['path_length']
            assert list(max(keys)) == witness['maximum_objective_key_on_path']
            if objective!='Linf':
                assert max(k[0] for k in keys)-keys[0][0] == witness['barrier_above_start']
            if result['task']['mode']=='descent':
                assert all(b<a for a,b in zip(keys,keys[1:]))
            else:
                assert keys[-1]<keys[0]
                if result['task']['mode']=='neutral':
                    assert all(k==keys[0] for k in keys[:-1])
        report['tasks'][path.stem] = {'status':result['status'],'sqlite_integrity':'ok','witness_verified':bool(witness)}
    report['pass'] = True
    args.output.write_text(json.dumps(report,indent=4)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='tasks'}))


if __name__ == '__main__':
    main()
