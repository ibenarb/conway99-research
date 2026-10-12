import gzip
import json
import sys
import time
from monitor import finite_eta
from pathlib import Path
from common import read, save, sha, require
from encode import ROOT, full, interface
from model import BASE_SHA, MAP_SHA


def prepare():
    work = ROOT / 'work'
    work.mkdir(exist_ok=True)
    base = work / 'base.cnf'
    if not base.exists():
        temp = base.with_suffix('.writing')
        with gzip.open(ROOT / 'inputs/base.cnf.gz', 'rb') as src, temp.open('wb') as dst:
            import shutil
            shutil.copyfileobj(src, dst)
        temp.replace(base)
    require(sha(base) == BASE_SHA, 'F0_HASH_MISMATCH')
    require(sha(ROOT / 'inputs/variables.json') == MAP_SHA, 'MAP_HASH_MISMATCH')
    rows = {r['id']: r for r in read(ROOT / 'inputs/roots.json')}
    plan = read(ROOT / 'inputs/pilot.json')
    receipts = []
    started = time.monotonic()
    for task in plan['tasks']:
        directory = work / 'cases' / task['id']
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / 'formula.cnf'
        old = read(directory / 'formula.json')
        if old:
            require(sha(target) == old['sha256'], 'FORMULA_CHANGED')
            receipts.append(old)
            continue
        row = rows[task['root_id']]
        result = interface(row, target) if task['mode'] == 'X' else full(base, row, task['mode'], target)
        result.update(task=task, root=row, base_sha256=BASE_SHA if task['mode'] != 'X' else None)
        save(directory / 'formula.json', result)
        receipts.append(result)
        print('PREPARED', task['id'], result['variables'], 'Vorbereitung-ETA', finite_eta(len(receipts), len(plan['tasks']), time.monotonic()-started), flush=True)
    expected = read(ROOT / 'evidence/prepared_reference.json')
    if expected:
        require({r['task']['id']: r['sha256'] for r in receipts} == expected['formula_sha256'], 'REFERENCE_FORMULA_HASH_MISMATCH')
    save(work / 'prepare.json', {'status': 'PASS', 'tasks': len(receipts),
         'formula_sha256': {r['task']['id']: r['sha256'] for r in receipts}})
    return receipts


if __name__ == '__main__':
    prepare()
