"""Finite move-count diagnostic of the frozen Engine, not a timed run replay.

Archive/canonicalization and wall-clock callbacks are omitted. Before the first
restart they cannot affect TC's choice or RNG. Every adopted graph is checked
independently. Labels in this diagnostic are not canonical certificates.
"""
from pathlib import Path
import copy
import hashlib
import json
import random
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from analyse import check, key, load
sys.path.insert(0, str(ROOT / 'experiments/memetik/lambda_compare_0_2_0'))
import bootstrap
from common import core
from engine import Engine
from worker import initial


class Guard:
    def check(self):
        pass


class Observer:
    def __init__(self, state):
        self.s = state
        self.trace = []

    def evaluated(self, rows, scores, name, origin):
        pass

    def adopt(self, rows, scores, name, origin, guard):
        text = core.encode_g6(rows)
        assert check(text) == scores
        item = {**origin, 'graph6': text, 'scores': scores,
                'state': hashlib.sha256(text.encode()).hexdigest()}
        if key(scores, 'W') < key(self.s['best']['scores'], 'W'):
            self.s['best'] = item
        self.trace.append({'operator': name, 'state': item['state'], 'scores': scores,
                           'best': key(self.s['best']['scores'], 'W')})
        return item

    def endpoint(self, item, reason):
        raise AssertionError('Restart encountered: this prefix diagnostic would be invalid')


class TracedEngine(Engine):
    def batch(self, current, guard, sample_size=None):
        result = super().batch(current, guard, sample_size)
        self.last_catalogue_size = len(result)
        return result


def run(seed, founders, config):
    task = {'variant': 'TC', 'target': 'W', 'seed': seed,
            'config': config, 'founders': copy.deepcopy(founders)}
    state = initial(task)
    observer = Observer(state)
    rng = random.Random(seed)
    engine = TracedEngine(task, state, rng, observer)
    while len(observer.trace) < 32:
        engine.step(Guard())
        assert state['restarts'] == 0
    return observer.trace, state, rng.getstate()


def main():
    started = time.process_time()
    source = ROOT / 'experiments/memetik/lambda_compare_0_2_0'
    founders, config = load(source / 'founders.json'), load(source / 'config.json')
    endpoints = load(ROOT / 'docs/memetik/lambda_results_20260922/ENDPOINTS.json.gz')
    results = {}
    for i in range(12):
        seed = endpoints[f'TC--lambda-W-{i:02d}']['seed']
        trace, state, rng = run(seed, founders, config)
        results[str(i)] = {'seed': seed, 'trace': trace,
                           'best': state['best']['scores'],
                           'best_state': state['best']['state'],
                           'tabu': state['tabu'], 'iterations': state['iterations']}
        if i == 0:
            second = run(seed, founders, config)
            assert trace == second[0] and rng == second[2]
    strings = [json.dumps(r['trace'], sort_keys=True) for r in results.values()]
    shared = 0
    for i in range(32):
        if len({r['trace'][i]['state'] for r in results.values()}) == 1:
            shared += 1
        else:
            break
    report = {'scope': '32 accepted moves, 12 historical seeds, no restart; no historical timed path replay',
              'instrumentation': 'Frozen Engine; independent graph verifier; no SQLite/canonicalization/wall callbacks',
              'same_seed_repeat_equal': True, 'distinct_trace_sequences': len(set(strings)),
              'shared_initial_moves_across_all_seeds': shared,
              'distinct_best_labelled_graphs': len({r['best_state'] for r in results.values()}),
              'cpu_seconds': time.process_time() - started, 'results': results}
    out = ROOT / 'docs/memetik/lambda_plan_codex_20260922/TC_PREFIX.json'
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'results'}, indent=2))
    print(json.dumps({i: r['best'] for i, r in results.items()}))


if __name__ == '__main__':
    main()
