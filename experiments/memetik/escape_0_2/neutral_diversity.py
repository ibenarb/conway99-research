"""Compare all first neutral C08 neighbors, without quotienting any search."""
import argparse
import json
from pathlib import Path
import time
from core import decode_g6, encode_g6, metrics
from search import neighbors, key
from symmetry_audit import inspect


class Timed:
    def __init__(self):
        self.deadline = time.process_time() + 120
    def check(self):
        if time.process_time() >= self.deadline:
            raise RuntimeError('Incomplete enumeration; no diversity total permitted')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    founder = next(f for f in json.loads((Path(__file__).parent / 'founders.json').read_text()) if f['id'] == 'Codex_C08')
    rows = decode_g6(founder['graph6'])
    baseline = metrics(rows)
    groups = {}
    census = {}
    entries = []
    for family, move, child in neighbors(rows, founder['arm'], Timed(), census):
        data = metrics(child)
        if key(data, 'W') != key(baseline, 'W'):
            continue
        g6 = encode_g6(child)
        aut = inspect(g6)
        certificate = aut.pop('canonical_certificate_hex')
        if certificate not in groups:
            groups[certificate] = len(groups) + 1
        entries.append({'graph6': g6, 'family': family, 'deleted': move[0], 'added': move[1], 'metrics': {k: data[k] for k in ('W', 'L1', 'F', 'Linf', 'Nmax')}, 'isomorphism_class': groups[certificate], **aut})
    assert len({e['graph6'] for e in entries}) == len(entries)
    report = {'scope': 'Uncolored full-graph isomorphism of immediate W-neutral neighbors only. No search quotient used.', 'census': census, 'labelled_neighbors': len(entries), 'uncolored_isomorphism_classes': len(groups), 'class_sizes': {i: sum(e['isomorphism_class'] == i for e in entries) for i in groups.values()}, 'neighbors': entries}
    args.output.write_text(json.dumps(report, indent=4) + '\n')
    print({k: v for k, v in report.items() if k != 'neighbors'})


if __name__ == '__main__':
    main()
