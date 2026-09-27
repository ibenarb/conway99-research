"""Positive control plus trajectory agreement with frozen production Engine."""
import boot
from support import *
from episodes import new_episode, advance
from kernel import Scorer
from engine import Engine
from search import tuple_state
import copy
import random


def reference(ep, task, guard):
    """Run an episode with original Engine; inject fixed parent and length only."""
    item = dict(task['start'], family='fixed', line='fixed', parent=task['start']['state'])
    state = {'episode': {'parent': item, 'current': item, 'phase': 'perturb',
                        'requested': task['k'], 'perturb': 0, 'descent': 0, 'phase_cpu': 0.0,
                        'maxima': dict(item['scores']), 'operators': {}, 'recipe': 0},
             'batch': None, 'histogram': {}, 'episodes': 0, 'children': [], 'replayed_moves': 0,
             'complete_batches': 0}
    class DummyArchive:
        def put(self, *args, **kwargs):
            pass
    class Observer:
        archive = DummyArchive()
        trace = []
        def evaluated(self, *args):
            pass
        def adopt(self, rows, scores, name, origin, guard):
            g6 = core.encode_g6(rows)
            self.trace.append((name, g6))
            return {**origin, 'graph6': g6, 'scores': scores, 'state': sha(g6.encode()), 'class': core.canonical(rows)}
        def endpoint(self, *args):
            pass
    obs = Observer()
    rng = random.Random()
    rng.setstate(tuple_state(ep['rng']))
    engine = Engine({'variant': 'P', 'target': 'W', 'config': {}}, state, rng, obs)
    while state['episodes'] == 0:
        engine.step_episode(guard)
    return obs.trace, rng.getstate()


def controls(guard):
    starts = read(boot.HERE / 'STARTS.json')
    for s in starts.values():
        rows, scores = checked(s['graph6'], 'lambda')
        assert scores == s['scores'] and sha(s['graph6'].encode()) == s['state']
        assert core.canonical(rows) == s['class']
    proof = read(boot.HERE / 'CONTROL_WITNESS.json')
    replay = witness(starts['2079'], [x['move'] for x in proof['steps']], guard)
    assert replay['state'] == starts['2076']['state']
    midpoint = dict(starts['2079'], graph6=proof['steps'][1]['graph6'], scores=proof['steps'][1]['scores'])
    task = {'start': midpoint, 'k': 0}
    ep = new_episode(task, 0)
    while ep['phase'] != 'verify':
        advance(ep, task, guard)
    assert ep['graph6'] == starts['2076']['graph6'] and ep['descent'] == 2
    comparisons = []
    for label, length in (('2076', 2), ('2077', 3)):
        task = {'start': starts[label], 'k': length}
        ep = new_episode(task, 0)
        expected, expected_rng = reference(copy.deepcopy(ep), task, guard)
        observed = []
        while ep['phase'] != 'verify':
            n = len(ep['path'])
            advance(ep, task, guard)
            if len(ep['path']) > n:
                observed.append((ep['path'][-1]['operator'], ep['graph6']))
        assert observed == expected and tuple_state(ep['rng']) == expected_rng
        _, score = checked(ep['graph6'], 'lambda')
        assert score == ep['scores']
        comparisons.append({'arm': label, 'k': length, 'moves': len(observed), 'same_trace_and_rng': True})
    return {'status': 'DONE', 'control_status': 'CONTROLS_PASS', 'reference_comparisons': comparisons,
            'positive_midpoint_descent': True, 'four_move_witness_replayed': True}
