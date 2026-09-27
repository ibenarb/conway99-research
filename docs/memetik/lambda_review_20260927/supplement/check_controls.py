"""Replay the existing control's midpoint descent; no new campaign."""
from pathlib import Path
import json
import math
import sys
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/memetik/lambda_radius_1_0_0'))
import boot
from support import core, Guard
from kernel import Scorer, catalogue
p = ROOT / 'experiments/memetik/lambda_radius_1_0_0/TEST_RESULTS.json'
w = json.loads(p.read_text())['controls']['positive_depth4_witness']
start = w['steps'][1]['graph6']
rows = tuple(core.decode_g6(start))
trace = []
while True:
    base = Scorer(rows).scores
    scorer = Scorer(rows)
    choices = []
    for name, move in catalogue(rows, False, Guard()):
        child, scores = scorer.evaluate(move)
        if (scores['W'], scores['L1']) < (base['W'], base['L1']):
            choices.append((name, move, tuple(child), scores))
    if not choices:
        break
    name, move, rows, scores = min(choices, key=lambda c: (c[3]['W'], c[3]['L1']))
    # P chooses the first minimum in catalogue order, not sorted move-tuple order.
    adj = [{v for v in range(99) if row >> v & 1} for row in rows]
    residues = [len(adj[u] & adj[v]) + int(v in adj[u]) - 2 for u in range(99) for v in range(u)]
    assert scores['W'] == sum(r != 0 for r in residues)
    assert scores['L1'] == sum(abs(r) for r in residues)
    assert all(len(a) == 14 for a in adj)
    assert all(len(adj[u] & adj[v]) == 1 for u in range(99) for v in adj[u])
    trace.append(dict(operator=name, move=move, scores=scores))
    assert len(trace) < 100
out = dict(midpoint_scores=Scorer(core.decode_g6(start)).scores, descent_trace=trace,
           endpoint_scores=Scorer(rows).scores, endpoint_is_2076=core.encode_g6(rows) == w['graph6'],
           zero_of_300_one_sided_95=1 - .05 ** (1 / 300),
           zero_of_300_20_cells_bonferroni=1 - (.05 / 20) ** (1 / 300),
           reviewer_state_bytes_GB=7400000 * 1287 / 1e9,
           reviewer_state_bytes_GiB=7400000 * 1287 / 2**30,
           one_arm_depth5_hours_at_factor37=37 * 18.17643,
           both_arms_hours_at_factor37=37 * (18.17643 + 15.57459))
Path(sys.argv[1]).write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out))
