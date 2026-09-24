"""Narrow controls for the new preparation and continuation contract."""
import boot
from util import *
from prepare import verify, validate_founders


def run_checks(run):
    before = own_cpu()
    plan = verify(run)
    counts = {'V2': 0, 'V3': 0}
    for job in plan['jobs']:
        d = run / job['directory']
        task = read(d / 'task.json')
        validate_founders(task['founders'])
        counts[job['group']] += 1
        if task['variant'] != 'P' or task['target'] != 'W':
            raise RuntimeError('Unexpected search method')
        if job['group'] == 'V3':
            baseline = run / 'baseline' / job['id']
            for name in ('task.json', 'result.json', 'checkpoint.json', 'receipt.json'):
                if (baseline / name).read_bytes() != (d / name).read_bytes():
                    raise RuntimeError('Initial continuation is not byte-identical')
            receipt_valid(d)
            sqlite_frozen(d / 'archive.sqlite')
            state = read(d / 'checkpoint.json')['state']
            if not state.get('rng') or state['task_sha256'] != file_sha(d / 'task.json'):
                raise RuntimeError('Missing continuation state')
            for c in [state['best'], *state['population']]:
                if c['family'] == 'HoG' or c['line'] != task['origin']:
                    raise RuntimeError('V3 ancestry mismatch')
                if checked(c['graph6'], 'lambda')[1] != c['scores']:
                    raise RuntimeError('Checkpoint score mismatch')
        else:
            if min(c['scores']['W'] for c in task['founders']) != job['frontier_W']:
                raise RuntimeError('Incorrect V2 starting frontier')
            if any(c['family'] != 'HoG' for c in task['founders']):
                raise RuntimeError('Non-HoG frontier input')
    if counts != {'V2': 6, 'V3': 8}:
        raise RuntimeError('Wrong job counts')
    return {'status': 'CONTROLS_PASS', 'counts': counts, 'initial_v3_state_byte_identical': True,
            'cpu_seconds': own_cpu() - before, 'scope': 'new inputs and continuation; frozen operators already tested'}
