import pathlib, sys, sqlite3, json, random, collections, time, hashlib
import pynauty
sys.path.insert(0, str(pathlib.Path(__file__).parent / 'source'))
from core import decode_g6, vertices
report = {'engine': 'pynauty ' + pynauty.__version__, 'scope': 'Exact full uncolored graph certificates within explicitly selected cohorts; not all database states. No search quotient.', 'tasks': {}}
for p in pathlib.Path('audit022').glob('*.sqlite'):
    c = sqlite3.connect('file:' + str(p.resolve()) + '?mode=ro', uri=True)
    c.row_factory = sqlite3.Row
    hog = p.name.startswith('HoG')
    obj = 'F' if hog else 'W'
    cut = 2932 if hog else 2100
    cohorts = {'first_shell_including_root': [r[0] for r in c.execute('select id from nodes where depth<=1')], 'low_score_all_saved': [r[0] for r in c.execute('select id from nodes where json_extract(metrics,?)<=?', ('$.' + obj, cut))]}
    frontier = [r[0] for r in c.execute('select id from nodes where expanded=0')]
    cohorts['frontier_sample_seed20260917'] = random.Random(20260917).sample(frontier, min(256, len(frontier)))
    ids = sorted(set(sum(cohorts.values(), [])))
    certs = {}
    aut = {}
    metrics = {}
    start = time.time()
    print(p.stem, 'selected', len(ids), 'cohort_sizes', {k: len(v) for k, v in cohorts.items()}, flush=True)
    for i, ident in enumerate(ids):
        row = c.execute('select g6,metrics from nodes where id=?', (ident,)).fetchone()
        rows = decode_g6(row['g6'])
        graph = pynauty.Graph(99, adjacency_dict={j: list(vertices(r)) for j, r in enumerate(rows)})
        certs[ident] = pynauty.certificate(graph)
        generators, mantissa, exponent, orbits, _ = pynauty.autgrp(graph)
        for permutation in generators:
            assert sorted(permutation) == list(range(99))
            assert all((bool(rows[u] & 1 << v) == bool(rows[permutation[u]] & 1 << permutation[v]) for u in range(99) for v in range(u)))
        aut[ident] = int(round(mantissa * 10 ** exponent))
        metrics[ident] = json.loads(row['metrics'])
        if (i + 1) % 250 == 0:
            print(p.stem, i + 1, round(time.time() - start, 1), flush=True)
    groups = {}
    for ident, cert in certs.items():
        groups.setdefault(cert, []).append(ident)
    records = {}
    for name, cohort in cohorts.items():
        counts = collections.Counter((certs[i] for i in cohort))
        records[name] = {'labelled': len(cohort), 'isomorphism_classes': len(counts), 'class_size_histogram': dict(sorted(collections.Counter(counts.values()).items())), 'automorphism_order_histogram': dict(sorted(collections.Counter((aut[i] for i in cohort)).items())), 'ids': cohort}
    report['tasks'][p.stem] = {'low_score_threshold': cut, 'cohorts': records, 'selected_total': len(ids), 'classes_total': len(groups), 'repeated_classes': [{'ids': v, 'metrics': [metrics[i] for i in v], 'certificate_sha256': hashlib.sha256(k).hexdigest()} for k, v in groups.items() if len(v) > 1], 'seconds': time.time() - start}
    print(p.stem, json.dumps({k: {a: b for a, b in v.items() if a != 'ids'} for k, v in records.items()}), flush=True)
pathlib.Path('analysis022/diversity.json').write_text(json.dumps(report, indent=4))
