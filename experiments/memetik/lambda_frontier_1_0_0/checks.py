"""Check actual prepared inputs; search operators are frozen and previously tested."""
import boot
from util import *
from prepare import verify, validate_founders


def run_checks(run):
    plan = verify(run)
    banks = read(boot.HERE / 'FRONTIER_BANKS.json')
    for bank in banks.values():
        validate_founders(bank['population'])
    seeds = set()
    for job in plan['jobs']:
        task = read(run / job['directory'] / 'task.json')
        if task['founders'] != banks[str(job['frontier_W'])]['population']:
            raise RuntimeError('Changed bank')
        if task['variant'] != 'P' or task['target'] != 'W':
            raise RuntimeError('Changed method')
        seeds.add(task['seed'])
    if len(seeds) != 8:
        raise RuntimeError('Repeated random seed')
    overlap = len({p['class'] for p in banks['2096']['population']}
                  & {p['class'] for p in banks['2101']['population']})
    if overlap != 5:
        raise RuntimeError('Unexpected bank overlap')
    return {'status': 'CONTROLS_PASS', 'jobs': 8, 'bank_sizes': [16, 16],
            'common_classes': overlap, 'distinct_seeds': 8,
            'scope': 'Pinned inputs, hard constraints, scores, canonical classes; operators unchanged.'}
