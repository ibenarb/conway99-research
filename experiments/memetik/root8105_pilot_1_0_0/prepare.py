"""Root audit, matching strata and frozen sampling manifest."""
import functools
import hashlib
import itertools
import json
import random
import time
from collections import Counter, defaultdict
from pathlib import Path

import pynauty
from core import Geometry, atomic, load_roots

BASE = Path(__file__).resolve().parent


def independent_root_count():
    # Vertex-elimination DP, independent of the SAT encoder and edge-by-edge DP.
    @functools.lru_cache(None)
    def rec(degrees):
        active = [i for i, d in enumerate(degrees) if d]
        if not active:
            return 1
        u = active[0]
        candidates = [v for v in active[1:] if abs(v - u) != 7 and (u, v) != (0, 1)]
        total = 0
        for chosen in itertools.combinations(candidates, degrees[u]):
            rest = list(degrees)
            rest[u] = 0
            for v in chosen:
                rest[v] -= 1
            total += rec(tuple(rest))
        return total
    return rec(tuple(1 if i in (0, 1, 7, 8) else 2 for i in range(14)))


def matching_count(g, row):
    remaining = [v for v in range(g.n) if (row >> v) & 1 and not (g.sets[v] & g.sets[0])]
    def rec(items):
        if not items:
            return 1
        u = items[0]
        return sum(rec(items[1:i] + items[i + 1:]) for i, v in enumerate(items[1:], 1)
                   if not (g.sets[u] & g.sets[v]))
    return rec(remaining)


def root_audit():
    g = Geometry()
    roots = load_roots(BASE / 'roots.tsv')
    certs = set()
    for item in roots:
        rows = {0: int(item['row'], 16)}
        graph = g.graph(rows)
        cert = pynauty.certificate(graph)
        if cert in certs:
            raise ValueError('equivalent root representatives')
        certs.add(cert)
        group = pynauty.autgrp(graph)
        order = round(group[1] * 10**group[2])
        if order != item['stabilizer'] or item['orbit'] * order != 7680:
            raise ValueError('root stabilizer or orbit mismatch')
        item['matchings'] = matching_count(g, int(item['row'], 16))
    total = independent_root_count()
    if total != sum(r['orbit'] for r in roots):
        raise ValueError('independent DP coverage failed')
    result = {'status': 'PASS', 'roots': len(roots), 'canonical_classes': len(certs),
              'independent_vertex_dp': total, 'orbit_sum': sum(r['orbit'] for r in roots),
              'matching_sum': sum(r['matchings'] for r in roots),
              'matching_range': [min(r['matchings'] for r in roots), max(r['matchings'] for r in roots)],
              'root_list_sha256': hashlib.sha256((BASE / 'roots.tsv').read_bytes()).hexdigest(),
              'stabilizers': dict(Counter(r['stabilizer'] for r in roots))}
    if result['matching_sum'] != 2944568 or result['matching_range'] != [292, 372]:
        raise ValueError('matching census mismatch')
    return roots, result


def select(roots, count=128):
    strata = defaultdict(list)
    for r in roots:
        strata[(r['stabilizer'], r['matchings'])].append(r)
    if len(strata) > count:
        raise ValueError('not enough slots for every stratum')
    rng = random.Random(810520261003)
    selected = []
    # At least one per exact (stabilizer, local matching count) stratum, then
    # proportional allocation by largest remaining population per allocated slot.
    allocation = {k: 1 for k in strata}
    while sum(allocation.values()) < count:
        eligible = [k for k in strata if allocation[k] < len(strata[k])]
        k = max(eligible, key=lambda x: (len(strata[x]) / (allocation[x] + 1), x))
        allocation[k] += 1
    for k, population in sorted(strata.items()):
        chosen = rng.sample(population, allocation[k])
        for r in chosen:
            selected.append({**r, 'stratum_population': len(population),
                             'stratum_sample': allocation[k],
                             'root_sampling_weight': len(population) / allocation[k]})
    return sorted(selected, key=lambda r: r['id'])


def prepare(directory, config):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    roots, audit = root_audit()
    selected = select(roots, config['roots'])
    atomic(directory / 'root_audit.json', audit)
    atomic(directory / 'selected_roots.json', selected)
    (directory / 'jobs').mkdir()
    jobs = []
    for root in selected:
        for arm in ('ordered', 'dynamic'):
            name = f"r{root['id']:04d}_{arm}"
            data = {'root_id': root['id'], 'row': root['row'], 'arm': arm,
                    'seed': 810500000 + root['id'], 'config': config,
                    'stratum': {k: root[k] for k in ('stabilizer', 'matchings', 'root_sampling_weight')}}
            atomic(directory / 'jobs' / (name + '.json'), data)
            jobs.append(name)
    job_hashes = {name: hashlib.sha256((directory / 'jobs' / (name + '.json')).read_bytes()).hexdigest() for name in jobs}
    atomic(directory / 'manifest.json', {'jobs': jobs, 'config': config, 'job_sha256': job_hashes,
                                        'source_commit': '002dc628005ee2c819bbc17d26498d1f06d28ca7',
                                        'rules': ['GC-01', 'GC-02', 'GC-05', 'GC-08', 'GC-10', 'GC-11',
                                                  'GC-14', 'GC-15', 'GC-16', 'GC-17']})
    atomic(directory / 'aux_ledger.json', {'cpu_s': time.process_time()})
    return audit


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    ap.add_argument('--config', default=str(BASE / 'config.json'))
    args = ap.parse_args()
    print(json.dumps(prepare(args.directory, json.loads(Path(args.config).read_text()))))
