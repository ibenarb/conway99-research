import sqlite3, json, collections, pathlib
out = {}
for p in pathlib.Path('audit022').glob('*.sqlite'):
    c = sqlite3.connect('file:' + str(p.resolve()) + '?mode=ro', uri=True)
    c.row_factory = sqlite3.Row
    obj = 'F' if p.name.startswith('HoG') else 'W'
    base = 2836 if obj == 'F' else 2082
    peak = {}
    hist = collections.Counter()
    layers = {}
    best = {}
    candidates = []
    for r in c.execute('select id,parent,depth,metrics,expanded from nodes order by id'):
        m = json.loads(r['metrics'])
        v = m[obj]
        b = max(v, peak.get(r['parent'], base))
        peak[r['id']] = b
        hist[r['depth'], b - base] += 1
        layer = layers.setdefault(r['depth'], {'n': 0, 'min': v, 'max': v, 'equal_root': 0, 'unexpanded': 0, 'min_unexpanded_peak': None})
        layer['n'] += 1
        layer['min'] = min(layer['min'], v)
        layer['max'] = max(layer['max'], v)
        layer['equal_root'] += v == base
        layer['unexpanded'] += not r['expanded']
        if not r['expanded']:
            layer['min_unexpanded_peak'] = min(layer['min_unexpanded_peak'] or b, b)
        for k in ['W', 'L1', 'F', 'Linf']:
            if k not in best or m[k] < best[k]['metrics'][k]:
                best[k] = {'id': r['id'], 'metrics': m, 'depth': r['depth'], 'tree_barrier': b - base}
        if v == base or (not r['expanded'] and b <= base + (100 if obj == 'F' else 8)):
            candidates.append({'id': r['id'], 'depth': r['depth'], 'expanded': r['expanded'], 'metrics': m, 'tree_barrier': b - base})
    out[p.stem] = {'layers': layers, 'metric_minima_separate_graphs': best, 'tree_barrier_histogram': [{'depth': d, 'barrier': b, 'count': n} for (d, b), n in sorted(hist.items())], 'candidates': candidates}
    print(p.stem, json.dumps({'layers': layers, 'best': best, 'candidate_count': len(candidates)}), flush=True)
pathlib.Path('analysis022/scan.json').write_text(json.dumps(out, indent=4))
