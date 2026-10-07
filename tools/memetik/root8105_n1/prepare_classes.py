"""Prepare two diagnostic roots, independently verify matching orbit coverage.

Build one N1 CNF per root for size measurement only; no class solver invocation.
"""
import argparse
import gzip
import hashlib
import itertools
import json
import resource
import sys
import time
from pathlib import Path
from model import encode, labels_for


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def all_pairings(vertices):
    if not vertices:
        yield ()
    else:
        u = min(vertices)
        for v in sorted(set(vertices) - {u}):
            for tail in all_pairings(set(vertices) - {u, v}):
                yield tuple(sorted(((u, v),) + tail))


def coverage(g, root, objects):
    import pynauty
    import historical_core as core
    labels = labels_for(7)
    ns = {v for v in range(84) if root >> v & 1}
    residual = {v for v in ns if not labels[v] & labels[0]}
    raw = {pairs for pairs in all_pairings(residual)
           if all(not labels[u] & labels[v] for u, v in pairs)}
    generators = pynauty.autgrp(core.Geometry().graph({0: root}))[0]
    images = []
    for permutation in generators:
        bp = permutation[:14]
        hp = [permutation[14 + v] - 14 for v in range(84)]
        assert sorted(bp) == list(range(14)) and sorted(hp) == list(range(84))
        assert all(bp[(c + 7) % 14] == (bp[c] + 7) % 14 for c in range(14))
        assert all({bp[c] for c in labels[v]} == labels[hp[v]] for v in range(84))
        assert hp[0] == 0 and {hp[v] for v in ns} == ns
        images.append(hp)
    union, classes = set(), []
    for number, entry in enumerate(objects['classes']):
        representative = tuple(tuple(p) for p in entry['matching'])
        orbit, queue = {representative}, [representative]
        while queue:
            member = queue.pop()
            for image in images:
                other = tuple(sorted(tuple(sorted((image[u], image[v]))) for u, v in member))
                assert other in raw
                if other not in orbit:
                    orbit.add(other)
                    queue.append(other)
        assert not union & orbit and len(orbit) == entry['orbit_size']
        union |= orbit
        classes.append({'id': number, 'representative': representative,
                        'orbit_size': len(orbit), 'members': sorted(orbit)})
    assert union == raw and len(raw) == objects['raw_count']
    return {'status': 'EXHAUSTIVE_MATCHING_COVERAGE_PASS', 'raw_count': len(raw),
            'class_count': len(classes), 'generators_verified': len(images),
            'border_and_H_generators': generators, 'classes': classes,
            'full_automorphism_group_required_for_soundness': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.repo / 'experiments/memetik/root8105_review_followup_1_0_1'
    sys.path.insert(0, str(source))
    import bootstrap
    from kernel import Geo
    from matching import root_objects
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    selected = json.loads(gzip.decompress((args.repo / 'docs/augmentation/root8105_early_diagnostic_20261006/SELECTED_PATHS.json.gz').read_bytes()))
    reports = []
    for rid in (210, 6682):
        start = time.process_time()
        spec = next(x['spec'] for x in selected if x['spec']['root_id'] == rid)
        root = int(spec['row'], 16)
        objects = root_objects(Geo(), root)
        cover = coverage(Geo(), root, objects)
        save(output / ('r%d_coverage.json' % rid), cover)
        rows = {0: {v for v in range(84) if root >> v & 1}}
        matching = objects['classes'][0]['matching']
        cnf, variables, meta = encode(7, rows, matching)
        cp = output / ('r%d_class000.cnf' % rid)
        cnf.to_file(str(cp))
        save(output / ('r%d_class000_edges.json' % rid), [[u, v, lit] for (u, v), lit in variables.items()])
        report = {'root_id': rid, 'root_row_hex': spec['row'], 'classes': cover['class_count'],
                  'raw_matchings': cover['raw_count'], 'coverage': cover['status'], 'metadata': meta,
                  'cpu_s': time.process_time() - start, 'cnf_bytes': cp.stat().st_size,
                  'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  'solved_classes': 0, 'scope': 'cloud encoding calibration, not solver hardness'}
        reports.append(report)
        print(json.dumps(report), flush=True)
        del cnf
    save(output / 'FINAL_RECEIPT.json', {'complete': True, 'reports': reports,
        'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir())}})


if __name__ == '__main__':
    main()
