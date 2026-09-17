"""Materialize complete boundary edges for the two already closed components."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / 'analysis022/source'))
from core import decode_g6, encode_g6
from search import neighbors, short, independent

class Unlimited:
    def check(self):
        pass

report = {}
for name, arm, objective in [('HoG57338__bfs_F', 'lambda', 'F'), ('B_escape_W2082__bfs_W', 'omega', 'W')]:
    source = HERE.parent / 'analysis022' / (name + '_sublevel.json')
    old = json.loads(source.read_text())
    assert old['status'] == 'COMPONENT_CLOSED'
    started = time.process_time()
    states = old['states']
    values = {s['graph6']: s['metrics'] for s in states}
    all_values = dict(values)
    edges = []
    censuses = {}
    for index, state in enumerate(states):
        g = state['graph6']
        row = decode_g6(g)
        assert short(row) == independent(row) == state['metrics']
        census = {}
        for family, move, child in neighbors(row, arm, Unlimited(), census):
            h = encode_g6(child)
            if h not in all_values:
                all_values[h] = independent(child)
                assert all_values[h] == short(child)
            edges.append([g, h, {'family': family, 'deleted': move[0], 'added': move[1]}])
        assert census == state['census']
        censuses[g] = census
        print(name, 'cached', index + 1, '/', len(states), flush=True)
    inside = set(values)
    assert {g for g, m in all_values.items() if m[objective] < old['strict_threshold']} == inside
    assert min(m[objective] for g, m in all_values.items() if g not in inside) == old['minimum_boundary']
    seed = {'name': name, 'arm': arm, 'objective': objective, 'root': states[0]['graph6'], 'baseline': old['baseline'], 'strict_threshold': old['strict_threshold'], 'inside': sorted(inside), 'metrics': all_values, 'edges': edges, 'censuses': censuses, 'source_certificate_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
    target = HERE / (name + '.seed.json.gz')
    target.write_bytes(gzip.compress(json.dumps(seed, separators=(',', ':')).encode(), mtime=0))
    report[name] = {'inside': len(inside), 'all_seed_nodes': len(all_values), 'directed_trades': len(edges), 'all_scores_independently_checked': True, 'all_censuses_match': True, 'cpu_seconds': time.process_time() - started, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes': target.stat().st_size}
    (HERE / 'seed_build_report.json').write_text(json.dumps(report, indent=4) + '\n')
    print(json.dumps(report[name]), flush=True)
