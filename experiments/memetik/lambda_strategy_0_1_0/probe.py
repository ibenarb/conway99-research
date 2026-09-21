"""Bounded development probe; no search campaign and no exhaustive cycle claim."""
import bootstrap
from common import core, checked, atomic, cpu
from search import key
from strategy import cycle_move
from diagnose import census
import fast_moves
import random
import json
from pathlib import Path
import sys

p = Path(sys.argv[1])
split = json.loads((p / 'founder_split.json').read_text())
founders = split['confirmation']['lambda']
results = [json.loads(x.read_text())['best'] for x in sorted((p / 'tasks').glob('lambda-*/result.json'))]
wbest = min(results, key=lambda f: key(f['scores'], 'W'))
lbest = min(results, key=lambda f: key(f['scores'], 'Linf'))
selected = [next(f for f in founders if f['family'] == family) for family in ('HoG', 'Z33_lift', 'triangle_packing')]
selected += [wbest, lbest, split['holdout']['lambda']]
report = []
for item in selected:
    out = census(item)
    rows, _ = checked(item['graph6'], 'lambda')
    ts = fast_moves.reference.triangles(rows)
    rng = random.Random(921031)
    count, unique, improvements = 0, {}, dict.fromkeys(('W', 'L1', 'F', 'Linf'), 0)
    start = cpu()
    for trial in range(100000):
        triples = rng.sample(ts, 3)
        tips = [rng.choice(t) for t in triples]
        move = cycle_move(rows, triples, tips, rng.choice((-1, 1)))
        if move is not None:
            count += 1
            if move not in unique:
                child = core.apply_move(rows, move)
                text = core.encode_g6(child)
                _, scores = checked(text, 'lambda')
                assert core.apply_move(child, move[::-1]) == rows
                unique[move] = text
                for target in improvements:
                    improvements[target] += int(key(scores, target) < key(item['scores'], target))
    out['cycle3_sample'] = {'proposals': 100000, 'valid': count, 'distinct': len(unique), 'improvements': improvements, 'cpu_seconds': cpu()-start, 'complete': False}
    report.append(out)
    print(item['line'], out['cycle3_sample'], flush=True)
atomic(Path(sys.argv[2]), report)
