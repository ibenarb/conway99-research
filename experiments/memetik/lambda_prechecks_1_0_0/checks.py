"""Finite mechanism, graph, provenance and resume controls."""
import boot
from util import *
from experiment_engine import ExperimentEngine
from engine import Engine as FrozenEngine
from worker import initial
from archive import Archive, make_item
from kernel import catalogue, Scorer
from search import key, tuple_state
from prepare import ORIGINS, specifications, validate_founders
import controls as frozen_checks
import experiment_engine
import copy
import random
import tempfile
from unittest.mock import patch


def bank_controls():
    banks = read(boot.HERE / 'ISOLATED_BANKS.json')
    checked_steps = 0
    for origin in ORIGINS:
        bank = banks[origin]
        validate_founders(bank['population'])
        current = bank['origin']
        seen = {current['graph6']}
        for step in bank['trace']:
            rows = core.decode_g6(current['graph6'])
            move = tuple(tuple(tuple(e) for e in part) for part in step['move'])
            assert (step['operator'], move) in list(catalogue(rows, False, frozen_checks.Guard()))
            child = core.apply_move(rows, move)
            assert core.encode_g6(child) == step['graph6']
            assert checked(step['graph6'], 'lambda')[1] == step['scores']
            current = step
            seen.add(step['graph6'])
            checked_steps += 1
        assert all(p['graph6'] in seen and p['line'] == origin and p['family'] != 'HoG'
                   for p in bank['population'])
    return {'populations': 4, 'canonical_distinct_per_population': 16,
            'replayed_AP_steps': checked_steps, 'no_HoG': True}


def differential(founders):
    traces, finals, rngs = [], [], []
    with tempfile.TemporaryDirectory() as tmp:
        for variant, cls in [('P', FrozenEngine), ('P', ExperimentEngine), ('PCesc', ExperimentEngine)]:
            task = frozen_checks.task_for(founders, variant, 240924)
            task['config']['perturb_ranges'] = [[2, 2]] * 3
            state = initial(task)
            rng = random.Random(task['seed'])
            archive = Archive(Path(tmp) / f'{len(traces)}.sqlite')
            observer = frozen_checks.Observation(task, state, archive)
            engine = cls(task, state, rng, observer)
            with patch.object(experiment_engine, 'cycle_moves', return_value=iter(())):
                while state['episodes'] < 17:
                    engine.step(frozen_checks.Guard())
            traces.append(observer.trace)
            rngs.append(rng.getstate())
            finals.append(([p['state'] for p in state['population']], state['best']['state'], state['epoch']))
            archive.close()
    assert traces[0] == traces[1] == traces[2]
    assert rngs[0] == rngs[1] == rngs[2] and finals[0] == finals[1] == finals[2]
    return {'episodes': 17, 'frozen_P_equals_instrumented_P': True,
            'disabled_cycle_same_moves_rng_population': True}


def scheduling_controls(founders):
    """Controlled catalogue fixture tests dispatch and persistence, not graph maths."""
    from types import SimpleNamespace
    task = frozen_checks.task_for(founders, 'PCesc')
    source = min(founders, key=lambda p: key(p['scores'], 'W'))
    dummy = (((0, 1),), ((0, 2),))
    better = {**source['scores'], 'W': source['scores']['W'] - 1}
    def fake_ap(this, current, guard, sample_size=None):
        this.s['batch'] = {'state': current['state'], 'items': [], 'complete': True}
        return this.s['batch']['items']
    def fake_score(this, move):
        return core.decode_g6(source['graph6']), better
    for phase, ap_improves in [('perturb', False), ('descent', True)]:
        state = initial(task)
        state['episode'] = {'phase': phase}
        engine = ExperimentEngine(task, state, random.Random(1), SimpleNamespace(evaluated=lambda *a: None))
        def ap(this, current, guard, sample_size=None):
            choices = fake_ap(this, current, guard)
            if ap_improves:
                choices.append({'operator': 'pivot', 'move': dummy, 'scores': better})
            return choices
        with patch.object(FrozenEngine, 'batch', ap), patch.object(experiment_engine, 'cycle_moves', side_effect=AssertionError('Unexpected cycle query')):
            engine.batch(source, frozen_checks.Guard())
    state = initial(task)
    state['episode'] = {'phase': 'descent'}
    engine = ExperimentEngine(task, state, random.Random(1), SimpleNamespace(evaluated=lambda *a: None))
    class PauseAfterPrefix:
        def check(self):
            batch = state.get('batch')
            if batch and len(batch['items']) == 1:
                raise frozen_checks.Interrupted()
    def cycles(*args):
        yield dummy
        yield (((2, 3),), ((2, 4),))
    with patch.object(FrozenEngine, 'batch', fake_ap), patch.object(experiment_engine, 'cycle_moves', cycles), patch.object(Scorer, 'evaluate', fake_score):
        try:
            engine.batch(source, PauseAfterPrefix())
        except frozen_checks.Interrupted:
            pass
        else:
            raise AssertionError('Cycle prefix was not interrupted')
        assert not state['batch']['cycle_complete']
        state = json.loads(json.dumps(state))
        engine = ExperimentEngine(task, state, random.Random(1), SimpleNamespace(evaluated=lambda *a: None))
        got = engine.batch(source, frozen_checks.Guard())
        assert len(got) == 2 and state['batch']['cycle_complete']
        assert state['experiment_metrics']['cycle_queries_started'] == 1
        assert state['experiment_metrics']['cycle_queries_with_improvement'] == 1
        assert state['experiment_metrics']['cycle_replayed_moves'] == 1
    return {'no_cycle_in_perturbation': True, 'no_cycle_before_AP_minimum': True,
            'cycle_prefix_resume_without_duplicate_adoption': True}


def witness_control():
    witness = read(boot.HERE / 'CONTROL_WITNESS.json')
    rows, _ = checked(witness['start_graph6'], 'lambda')
    for field in ('step1', 'step2'):
        point = witness[field]
        move = tuple(tuple(tuple(e) for e in part) for part in point['move'])
        assert (point['operator'], move) in list(catalogue(rows, True, frozen_checks.Guard()))
        before = rows
        rows = core.apply_move(rows, move)
        checked(core.encode_g6(rows), 'lambda')
        assert core.apply_move(rows, move[::-1]) == before
    assert core.encode_g6(rows) == witness['graph6']
    assert checked(witness['graph6'], 'lambda')[1] == witness['scores']
    return {'real_pivot_cycle_witness_replayed': True, 'reverse_moves_valid': True}


def run_checks(run=None):
    started = own_cpu()
    founders = read(boot.FROZEN / 'founders.json')
    validate_founders(founders)
    jobs = specifications()
    assert len(jobs) == 24 and sum(j['additional_cpu_seconds'] for j in jobs) == 32 * 3600
    assert sum(AUX_LIMITS.values()) == 7200
    for a, b in zip(jobs[:16:2], jobs[1:16:2]):
        assert a['seed'] == b['seed'] and a['variant'] == 'P' and b['variant'] == 'PCesc'
    report = {'status': 'CONTROLS_PASS', 'bank': bank_controls(),
              'scheduling': scheduling_controls(founders), 'witness': witness_control(),
              'differential': differential(founders), 'budget_cpu_hours': 34,
              'scope': 'Finite controls, not a production WSL host calibration'}
    report['cpu_seconds'] = own_cpu() - started
    return report


if __name__ == '__main__':
    print(json.dumps(run_checks(), indent=2))
