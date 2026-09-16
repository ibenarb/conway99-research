"""Bounded A probe of three additional right-support product sizes."""
import argparse
import json
from pathlib import Path
import random
from core import Budget, BudgetEnd, apply_move, decode_g6, encode_g6, metrics, validate
from operators import omega_moves


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    founder = next(f for f in json.loads((Path(__file__).parent / 'founders.json').read_text()) if f['id'] == 'A_legacy')
    rows = decode_g6(founder['graph6'])
    budget = Budget(seconds=20, evaluations=10**12)
    report = {}
    for family in ('4x8', '4x10', '4x12'):
        count = 0
        try:
            for move in omega_moves(rows, family, random.Random(20260915), budget):
                child = apply_move(rows, move)
                validate(child, 'omega')
                count += 1
                report['witness'] = {'family': family, 'graph6': encode_g6(child), 'deleted': move[0], 'added': move[1], 'metrics': metrics(child)}
                break
            report[family] = {'found': count, 'complete': count == 0}
        except BudgetEnd:
            report[family] = {'found': count, 'complete': False}
        if count:
            break
    args.output.write_text(json.dumps(report, indent=4) + '\n')


if __name__ == '__main__':
    main()
