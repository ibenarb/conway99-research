"""Full uncolored automorphism groups; no quotienting of search states."""
import argparse
import hashlib
import json
from pathlib import Path
import pynauty
from core import decode_g6, vertices


def inspect(g6):
    rows = decode_g6(g6)
    graph = pynauty.Graph(99, adjacency_dict={i: list(vertices(r)) for i, r in enumerate(rows)})
    generators, mantissa, exponent, orbits, count = pynauty.autgrp(graph)
    for permutation in generators:
        assert sorted(permutation) == list(range(99))
        assert all(bool(rows[u] & (1 << v)) == bool(rows[permutation[u]] & (1 << permutation[v])) for u in range(99) for v in range(u))
    return {'sha256': hashlib.sha256((g6 + '\n').encode()).hexdigest(),
            'group_order': int(round(mantissa * 10 ** exponent)),
            'orbit_count': count, 'orbit_sizes': sorted(orbits.count(o) for o in set(orbits)),
            'generators': generators, 'generators_independently_checked': True,
            'canonical_certificate_hex': pynauty.certificate(graph).hex()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    base = args.repo / 'data/memetik/ai_candidates'
    registry = json.loads((base / 'registry.json').read_text())
    report = {'engine': 'pynauty ' + pynauty.__version__, 'scope': 'Full uncolored 99-vertex graphs. Group completeness relies on nauty.', 'candidates': {}, 'escape_founders': {}}
    for item in registry['accepted_candidates']:
        raw = (base / item['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item['sha256']
        report['candidates'][item['id']] = inspect(raw.decode().strip())
    founders = json.loads((Path(__file__).parent / 'founders.json').read_text())
    for item in founders:
        report['escape_founders'][item['id']] = inspect(item['graph6'])
    args.output.write_text(json.dumps(report, indent=4) + '\n')
    print(json.dumps({section: {name: data['group_order'] for name, data in report[section].items()} for section in ('candidates', 'escape_founders')}, indent=4))


if __name__ == '__main__':
    main()
