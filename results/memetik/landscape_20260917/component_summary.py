import pathlib, json, sqlite3, sys, heapq, collections
import pynauty
sys.path.insert(0, str(pathlib.Path(__file__).parent / 'source'))
from core import decode_g6, vertices
out = {}
for p in pathlib.Path('analysis022').glob('*_sublevel.json'):
    r = json.loads(p.read_text())
    assert r['status'] == 'COMPONENT_CLOSED'
    obj = 'F' if r['task'].startswith('HoG') else 'W'
    states = {s['graph6']: s for s in r['states']}
    adj = {g: set() for g in states}
    for a, b in r['internal_edges']:
        adj[a].add(b)
    assert all((a in adj[b] for a in adj for b in adj[a]))
    assert all((all((v['complete'] for v in s['census'].values())) for s in states.values()))
    root = r['states'][0]['graph6']
    dist = {root: r['baseline']}
    q = [(r['baseline'], root)]
    while q:
        d, g = heapq.heappop(q)
        if d != dist[g]:
            continue
        for h in adj[g]:
            v = max(d, states[h]['metrics'][obj])
            if v < dist.get(h, 10 ** 9):
                dist[h] = v
                heapq.heappush(q, (v, h))
    assert len(dist) == len(states)
    groups = {}
    depths = collections.Counter()
    missing = 0
    improved_paths = 0
    c = sqlite3.connect('file:' + str(pathlib.Path('audit022', r['task'] + '.sqlite').resolve()) + '?mode=ro', uri=True)
    for g, s in states.items():
        rows = decode_g6(g)
        cert = pynauty.certificate(pynauty.Graph(99, adjacency_dict={i: list(vertices(v)) for i, v in enumerate(rows)}))
        groups.setdefault(cert, []).append(g)
        row = c.execute('select id,parent,depth,metrics from nodes where g6=?', (g,)).fetchone()
        if row is None:
            missing += 1
            continue
        depths[row[2]] += 1
        peak = 0
        while row:
            peak = max(peak, json.loads(row[3])[obj])
            row = c.execute('select id,parent,depth,metrics from nodes where id=?', (row[1],)).fetchone() if row[1] else None
        improved_paths += dist[g] < peak
    out[r['task']] = {k: v for k, v in r.items() if k not in ('states', 'internal_edges')}
    out[r['task']].update(necessary_barrier=r['minimum_boundary'] - r['baseline'], isomorphism_classes=len(groups), class_size_histogram=dict(collections.Counter(map(len, groups.values()))), depths_in_old_database=dict(depths), new_graphs=missing, states_with_lower_peak_than_stored_BFS_path=improved_paths, internal_undirected_edges=sum(map(len, adj.values())) // 2, minimax_barrier_histogram=dict(sorted(collections.Counter((v - r['baseline'] for v in dist.values())).items())))
print(json.dumps(out, indent=4))
pathlib.Path('analysis022/component_summary.json').write_text(json.dumps(out, indent=4))
