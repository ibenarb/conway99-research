"""Paired scoring benchmark on identical legal trades from pinned starters."""
from pathlib import Path
import hashlib
import json
import random
import statistics
import sys
import time

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'src/memetic_v2'))
import core
from operators import MoveSource
from memetic_incremental import prepare, update, metrics

items = json.loads((BASE / 'data/memetic_v2/reference/population64.json').read_text())['candidates']
selected = []
seen = set()
for item in items:
    key = item['founder']
    if key not in seen:
        selected.append(item)
        seen.add(key)
results = []
for index, item in enumerate(selected):
    parent = core.decode_g6(item['g6'])
    state = prepare(parent)
    assert metrics(state) == core.metrics(parent)
    moves = []
    budget = core.Budget(4, 100000)
    source = MoveSource(parent, item['arm'], random.Random(20260912+index), budget)
    try:
        while len(moves) < 24:
            option = source.next()
            if option is None:
                break
            family, move = option
            child = core.apply_move(parent, move)
            core.validate(child, item['arm'])
            touched = {v for side in move for edge in side for v in edge}
            new_state = update(parent, child, state, touched)
            assert metrics(new_state) == core.metrics(child)
            assert update(child, parent, new_state, touched) == state
            moves.append((child, touched, move))
    except core.BudgetEnd:
        pass
    if not moves:
        results.append({'founder': item['founder'], 'moves': 0})
        continue
    full_times, incremental_times = [], []
    # Alternate timing order; both methods evaluate the same pre-generated children.
    for repeat in range(6):
        for name in (['full', 'incremental'] if repeat % 2 == 0 else ['incremental', 'full']):
            started = time.process_time()
            for _ in range(8):
                for child, touched, _ in moves:
                    value = core.metrics(child) if name == 'full' else metrics(update(parent, child, state, touched))
            duration = time.process_time() - started
            (full_times if name == 'full' else incremental_times).append(duration)
    full, inc = statistics.median(full_times), statistics.median(incremental_times)
    result = {'founder': item['founder'], 'arm': item['arm'], 'moves': len(moves),
              'parent_g6_sha256': hashlib.sha256(item['g6'].encode()).hexdigest(),
              'median_full_cpu_seconds': full, 'median_incremental_cpu_seconds': inc,
              'speedup_scoring_only': full/inc,
              'strict_L1_improvements': sum(core.metrics(ch)['L1'] < core.metrics(parent)['L1'] for ch, _, _ in moves),
              'strict_L2_improvements': sum(core.metrics(ch)['F'] < item['F'] for ch, _, _ in moves),
              'trades': [move for _, _, move in moves]}
    results.append(result)
    print(json.dumps({k: v for k, v in result.items() if k != 'trades'}), flush=True)
out = {'status': 'PASS_IDENTICAL_METRICS_AND_INVERSE', 'seed': 20260912,
       'scope': 'Scoring microbenchmark only; excludes move generation and population management. No convergence speedup claim.',
       'results': results}
(BASE / 'results/research_20260912/memetic_scoring.json').write_text(json.dumps(out, indent=4)+'\n')
