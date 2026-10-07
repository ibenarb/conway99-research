"""Non-search regression for the global PySAT interval-pool accumulation."""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo / 'tools/memetik/root8105_frontier'))
    from certify_dead import encode
    from pysat.formula import Formula, IDPool
    data = json.loads((args.repo / 'docs/augmentation/root8105_prefix_audit_20261006/prefix_r6682_w290.json').read_text())
    Formula.attach_vpool(IDPool())
    counts = []
    for batch in range(3):
        for _ in range(20):
            encode(data, 13)
        counts.append(len(Formula.export_vpool()._occupied))
    assert counts[0] < counts[1] < counts[2]
    before, _ = encode(data, 13)
    Formula.attach_vpool(IDPool())
    after, _ = encode(data, 13)
    assert before.nv == after.nv and before.clauses == after.clauses
    report = {'status': 'PASS', 'occupied_intervals_after_20_40_60': counts,
              'occupied_after_reset_and_encode': len(Formula.export_vpool()._occupied),
              'exact_CNF_equal': True,
              'cnf_sha256': hashlib.sha256(after.to_dimacs().encode()).hexdigest()}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
