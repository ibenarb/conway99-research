"""Standard-library endpoint re-evaluation; no graph/scoring project code."""
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path


def decode(text):
    data = [ord(c) - 63 for c in text.strip()]
    assert all(0 <= x < 64 for x in data)
    if data[0] == 63:
        n = (data[1] << 12) | (data[2] << 6) | data[3]
        bits = data[4:]
    else:
        n, bits = data[0], data[1:]
    assert n == 99
    rows = [0] * n
    index = 0
    for v in range(n):
        for u in range(v):
            if (bits[index // 6] >> (5 - index % 6)) & 1:
                rows[v] |= 1 << u
                rows[u] |= 1 << v
            index += 1
    return rows


def score(rows):
    assert all(x.bit_count() == 14 for x in rows)
    histogram = Counter()
    for v in range(99):
        for u in range(v):
            edge = (rows[v] >> u) & 1
            common = (rows[v] & rows[u]).bit_count()
            assert not edge or common == 1
            histogram[common + edge - 2] += 1
    bound = max(abs(x) for x in histogram)
    return {'W': sum(c for r, c in histogram.items() if r),
            'L1': sum(abs(r) * c for r, c in histogram.items()),
            'F': sum(r * r * c for r, c in histogram.items()), 'Linf': bound,
            'Nmax': sum(c for r, c in histogram.items() if abs(r) == bound)}


def quantile(values, p):
    x = sorted(values)
    if not x:
        return None
    h = (len(x) - 1) * p
    lo = int(h)
    return x[lo] + (h - lo) * (x[min(lo + 1, len(x) - 1)] - x[lo])


def distribution(values):
    return {name: quantile(values, p) for name, p in [('min', 0), ('q1', .25), ('median', .5), ('q3', .75), ('max', 1)]}


def main(run):
    cache = {}
    cells = {}
    near = {}
    verified = set()
    root_diagnostics = {}
    for path in sorted((run / 'jobs').glob('*_k*/episodes.jsonl')):
        task = json.loads((path.parent / 'task.json').read_text())
        start = task['start']
        root = decode(start['graph6'])
        assert score(root) == start['scores']
        if task['arm'] not in root_diagnostics:
            degrees = [0] * 99
            residual_sum = 0
            for v in range(99):
                for u in range(v):
                    r = (root[u] & root[v]).bit_count() + ((root[u] >> v) & 1) - 2
                    residual_sum += r
                    if r:
                        degrees[u] += 1
                        degrees[v] += 1
            root_diagnostics[task['arm']] = {'defect_degree': distribution(degrees), 'residual_sum': residual_sum, 'all_vertices_incident_to_defects': all(degrees)}
        values = [json.loads(line) for line in path.read_text().splitlines()]
        other = []
        for v in values:
            graph = v['graph6']
            if graph not in cache:
                rows = decode(graph)
                cache[graph] = (rows, score(rows))
            rows, actual = cache[graph]
            assert actual == v['scores']
            assert hashlib.sha256(graph.encode()).hexdigest() == v['state']
            if graph == start['graph6']:
                continue
            verified.add(graph)
            distance = sum((a ^ b).bit_count() for a, b in zip(root, rows)) // 4
            v = {**v, 'edge_replacements': distance, 'delta_W': actual['W'] - start['scores']['W']}
            other.append(v)
            if v['delta_W'] <= 10:
                e = near.setdefault(v['class'], {'scores': actual, 'state': v['state'], 'graph6': graph, 'observations': []})
                e['observations'].append([path.parent.name, v['index']])
        thresholds = {str(delta): {'episodes': sum(v['delta_W'] <= delta for v in other),
                                  'classes': len({v['class'] for v in other if v['delta_W'] <= delta})} for delta in (2, 5, 10)}
        n = len(other)
        perturb = [v['path'][v['actual_k']-1]['scores']['W']-start['scores']['W'] for v in values]
        cells[path.parent.name] = {'n': len(values), 'nonreturn': n,
            'classes_nonreturn': len({v['class'] for v in other}),
            'delta_W': distribution([v['delta_W'] for v in other]),
            'edge_replacements': distribution([v['edge_replacements'] for v in other]),
            'perturbed_delta_W_all_episodes': distribution(perturb), 'thresholds': thresholds,
            'reviewer_gate': task['k'] >= 8 and n > 0 and thresholds['5']['episodes'] / n >= .1 and thresholds['5']['classes'] >= 10}
    return {'status': 'PASS', 'scorer': 'independent standard-library bitset implementation',
        'quantiles': 'linear interpolation at (N-1)*p; endpoint episodes retain multiplicity',
        'distance': 'labelled edge replacements = |E(start) symmetric_difference E(end)|/2; not isomorphism-minimized',
        'verified_unique_nonreturn_graphs': len(verified), 'verified_unique_endpoints': len(cache),
        'cells': cells, 'near_classes_within_plus10': near, 'root_diagnostics': root_diagnostics}


if __name__ == '__main__':
    print(json.dumps(main(Path(sys.argv[1])), indent=2))
