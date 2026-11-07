"""Bounded crash/integrity tests of the isolated controller. Not case proofs."""
from pathlib import Path
from itertools import combinations, product
import fcntl
import json
import os
import shutil
import subprocess
import sys
import batch_recovery as b

P = Path(__file__).resolve().parent
OUT = P / 'controls_v2'


class FixtureSensor:
    def resources(self):
        return {'scope': 'tiny_fixture_only'}, []


class HoldSensor:
    def resources(self):
        return {}, ['injected resource hold']


class Crash(Exception):
    pass


def model(path, cols, gram, domains, bounds):
    text = [f'4 {cols}', ' '.join(map(str, range(cols)))]
    text += [' '.join(map(str, row)) for row in gram] * 2
    for domain in domains:
        text += [str(len(domain)), ' '.join(map(str, domain))]
    text += [str(len(bounds))] + [f'{a} {c}' for a, c in bounds]
    path.write_text('\n'.join(text) + '\n')


def fixture(name, kind='unsat', tasks=None):
    root = OUT / name
    return b.initialise(root, kind + '-synthetic', 3, tasks or [0, 1, 2],
                        dict(zip(b.NAMES, [OUT / (kind + '.txt'), OUT / (kind + '.action'),
                                           P / 'batch-engine', P / 'batch-verify'])))


def run(name, **kwargs):
    return b.run(OUT / name, sensor=FixtureSensor(), **kwargs)


def rejected(call, message=None):
    try:
        call()
    except (RuntimeError, FileNotFoundError, BlockingIOError, ValueError, OSError) as error:
        if message:
            assert message in str(error), str(error)
        return str(error)
    raise AssertionError('Expected rejection')


def prepare():
    OUT.mkdir(exist_ok=False)
    gram = [[2,0,1,1],[0,2,1,1],[1,1,2,0],[1,1,0,2]]
    for kind, domain in [('unsat', [3]), ('sat', [5,6,9,10])]:
        model(OUT / (kind + '.txt'), 4, gram, [[3,12],[3,12],domain,domain], [(3,12),(12,3),(3,12)])
        (OUT / (kind + '.action')).write_text('1 0 2 3')
    # Find a model with a true UNSAT boundary followed by a true SAT boundary.
    cols = 6
    vals = [sum(1 << i for i in t) for t in combinations(range(cols), 4)]
    action = [1,0,2,3,4,5]
    image = lambda x: sum(1 << action[i] for i in range(cols) if x >> i & 1)
    rows01 = [sum(1 << i for i in t) for t in combinations(range(cols), 2)]
    fixed = [x for x in rows01 if image(x) == x]
    bounds = [(a,c) for a in fixed for c in fixed if a & c == 0]
    gram = [[2,0,1,1],[0,2,1,1],[1,1,4,2],[1,1,2,4]]
    orbits = sorted(set(tuple(sorted({value, image(value)})) for value in vals))
    for chosen in combinations(orbits, 2):
        domain = sorted(set(x for orbit in chosen for x in orbit))
        satisfiable = {}
        for a,c in bounds:
            satisfiable[(a,c)] = any(all((rows[r] & rows[s]).bit_count() == gram[r][s]
                                        for r in range(4) for s in range(4)) and
                                    all(sum(x >> j & 1 for x in rows) == 2 for j in range(cols))
                                    for x,y in product(domain, repeat=2) for rows in [[a,c,x,y]])
        yes = [pair for pair, answer in satisfiable.items() if answer]
        no = [pair for pair, answer in satisfiable.items() if not answer]
        if yes and no:
            model(OUT / 'mixed.txt', cols, gram, [sorted(fixed),sorted(fixed),domain,domain], [no[0],yes[0],no[0]])
            (OUT / 'mixed.action').write_text(' '.join(map(str, action)))
            return
    raise AssertionError('No mixed fixture found')


def main():
    prepare()
    results = []
    fixture('normal', tasks=[2,1,0])
    assert run('normal')['tasks'] == [0,1,2]
    before = sorted(str(x) for x in (OUT / 'normal').rglob('*'))
    assert run('normal')['tasks'] == [0,1,2]
    assert before == sorted(str(x) for x in (OUT / 'normal').rglob('*'))
    results.append('ABA/reverse/idempotent')
    for phase in ('search_closed','snapshot','checked','packed','committed'):
        name = 'crash_' + phase
        fixture(name)
        def hook(where, index):
            if where == phase:
                raise Crash(phase)
        try:
            run(name, hook=hook)
        except Crash:
            pass
        else:
            raise AssertionError('Crash not injected')
        prior = list((OUT / name / 'receipts').glob('*.json'))
        assert len(prior) == (1 if phase == 'committed' else 0)
        assert run(name)['tasks'] == [0,1,2]
        # A closed producer is not searched again after controller failure.
        assert len(list((OUT / name / 'attempts').glob('*/search_intent.json'))) == 1
        results.append('recovery_' + phase)
    for kind, budget in [('sat',60),('unsat',0)]:
        name = 'unresolved_' + kind
        fixture(name, kind)
        def hook(where, index):
            if where == 'search_exit':
                raise Crash(where)
        try:
            run(name, seconds=budget, hook=hook)
        except Crash:
            pass
        rejected(lambda: run(name), 'UNRESOLVED_SEARCH')
        assert not list((OUT / name / 'receipts').glob('*.json'))
        assert len(list((OUT / name / 'attempts').glob('*/search_intent.json'))) == 1
        results.append('unresolved_' + kind)
    fixture('mixed', 'mixed')
    state = run('mixed')
    assert state['state'] == 'STOPPED' and state['verified'] == [0], state
    assert state['stop']['reason'] == 'SAT_VALIDATED_AGAINST_SUPPLIED_MATRIX'
    assert run('mixed')['verified'] == [0]
    assert not list((OUT / 'mixed' / 'attempts').glob('*/boundary_2.proof'))
    results.append('UNSAT_SAT_open_original_matrix_validation')
    fixture('unknown')
    state = run('unknown', seconds=0)
    assert state['state'] == 'STOPPED' and state['verified'] == []
    assert state['stop']['reason'] == 'UNKNOWN'
    assert run('unknown')['verified'] == []
    results.append('UNKNOWN_open')
    fixture('hold')
    rejected(lambda: b.run(OUT / 'hold', sensor=HoldSensor()), 'RESOURCE_HOLD')
    rejected(lambda: run('hold'), 'UNRESOLVED_SEARCH')
    results.append('resource_hold_not_blindly_restarted')
    for change in ('gzip','missing_gzip','snapshot','native','log','context','duplicate','binary','model','action'):
        root = OUT / ('tamper_' + change)
        shutil.copytree(OUT / 'normal', root)
        receipt = b.read(root / 'receipts/00000.json')
        folder = root / 'attempts' / receipt['attempt']
        paths = {'gzip':root/'receipts/00000.proof.gz', 'snapshot':folder/'snapshot/boundary_0.proof',
                 'native':folder/'snapshot/boundary_0.verified.json', 'log':folder/'verify.log',
                 'binary':root/'batch-verify', 'model':root/'model.txt', 'action':root/'action.txt'}
        if change == 'missing_gzip':
            (root / 'receipts/00000.proof.gz').unlink()
        elif change == 'context':
            receipt['context'] = '0'*64
            (root / 'receipts/00000.json').write_text(json.dumps(receipt))
        elif change == 'duplicate':
            shutil.copyfile(root/'receipts/00000.json',root/'receipts/duplicate.json')
        else:
            with paths[change].open('ab') as stream:
                stream.write(b'X')
        rejected(lambda: b.run(root, sensor=FixtureSensor()))
        results.append('reject_' + change)
    fixture('invalidproof')
    def badproof(where, index):
        if where == 'search_closed':
            path = next((OUT/'invalidproof'/'attempts').glob('*/boundary_1.proof'))
            with path.open('ab') as stream:
                stream.write(b'X')
    rejected(lambda: run('invalidproof', hook=badproof), 'replay rejected')
    assert not list((OUT/'invalidproof/receipts').glob('*.json'))
    results.append('invalid_second_proof_no_receipts')
    fixture('postreplay')
    def changed(where, index):
        if where == 'checked':
            path = next((OUT/'postreplay/attempts').glob('*/snapshot/boundary_0.proof'))
            with path.open('ab') as stream:
                stream.write(b'X')
    rejected(lambda: run('postreplay', hook=changed), 'Proof changed before commit')
    assert not list((OUT/'postreplay/receipts').glob('*.json'))
    results.append('post_replay_mutation')
    fixture('symlink')
    (OUT/'symlink/receipts/escape').symlink_to(OUT/'normal',target_is_directory=True)
    rejected(lambda: run('symlink'), 'Symlink')
    results.append('symlink_rejected')
    with (P/'research.lock').open('a+b') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        rejected(lambda: run('normal'))
    results.append('second_controller_rejected')
    rejected(lambda: fixture('duplicate', tasks=[0,0]), 'duplicate')
    results.append('duplicate_request_rejected')
    result = dict(status='PASS', tests=results, count=len(results),
                  native_receipts=True, fixture_sensor=True, production_modified=False,
                  scope='Process crash/integrity tests; no hardware power-loss guarantee or global exclusion')
    (P/'CONTROLS.json').write_text(json.dumps(result,indent=4)+'\n')
    print(json.dumps(result,indent=4))


if __name__ == '__main__':
    main()
