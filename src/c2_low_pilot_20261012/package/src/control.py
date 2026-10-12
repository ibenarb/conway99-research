"""Staged pilot controller; supervisors survive controller restart."""
import os
import subprocess
import sys
import time
from pathlib import Path
from common import alive, host, identity, lock, log_has, proc, read, require, save, sha
from encode import ROOT, model_values, verify_full, verify_x


def active(jobs, category):
    return sum(read(p / 'spec.json', {}).get('category') == category and not (p / 'result.json').exists()
               for p in jobs.iterdir() if p.is_dir())


def submit(ident, command, category, inputs, outputs, config):
    work = ROOT / 'work'
    d = work / 'jobs' / ident
    if d.exists():
        if (d / 'result.json').exists():
            return True
        state = read(d / 'state.json', {})
        require(alive(state.get('supervisor')), 'UNCLEAN_JOB_PRESERVED: ' + ident)
        require(state.get('phase') != 'ERROR_PRESERVED', 'WORKER_ERROR: ' + ident)
        return True
    h = host(work)
    needed = config['min_ram_gib'] + (config['cake_heap_mb'] + config['cake_stack_mb']) / 1024 if category == 'checker' else config['min_ram_gib'] + 2
    disks = [h['linux_free_gib']] + ([h['windows_c_free_gib']] if h['windows_c_free_gib'] is not None else [])
    if h['available_ram_gib'] < needed or min(disks) < config['min_disk_gib']:
        return False
    d.mkdir()
    save(d / 'spec.json', {'id': ident, 'root': str(ROOT), 'command': list(map(str, command)),
                          'category': category, 'inputs': list(map(str, inputs)), 'outputs': list(map(str, outputs)),
                          'target_cpu_s': config[category + '_target_cpu_s']})
    with (d / 'supervisor.log').open('ab') as stream:
        child = subprocess.Popen([sys.executable, '-u', str(ROOT / 'src/worker.py'), str(d)],
                                 stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
    for _ in range(100):
        if (d / 'state.json').exists():
            return True
        require(child.poll() is None, 'WORKER_START_FAILED')
        time.sleep(0.05)
    raise RuntimeError('WORKER_START_UNCERTAIN')


def receipt(ident, cache):
    d = ROOT / 'work/jobs' / ident
    r = read(d / 'result.json')
    if r and ident not in cache:
        require(r['reason'] is None, 'JOB_NOT_COMPLETED: ' + ident)
        spec = read(d / 'spec.json')
        require(r['command'] == spec['command'], 'JOB_COMMAND_CHANGED')
        for item in r['inputs'] + r['outputs'] + [r['log']]:
            require(identity(item['path']) == item, 'ARTIFACT_CHANGED: ' + item['path'])
        cache.add(ident)
    return r


def run(stage):
    work = ROOT / 'work'
    jobs = work / 'jobs'
    jobs.mkdir(parents=True, exist_ok=True)
    guard = lock(work / 'controller.lock')
    require(read(work / 'validation.json', {}).get('status') == 'PASS', 'VALIDATION_REQUIRED')
    require(read(work / 'prepare.json', {}).get('status') == 'PASS', 'PREPARATION_REQUIRED')
    tasks = [t for t in read(ROOT / 'inputs/pilot.json')['tasks'] if stage == 'all' or t['stage'] == 'initial']
    cache = set()
    checked_formulas = set()
    last = 0
    try:
        while True:
            require(not (work / 'STOP').exists(), 'EXPLICIT_STOP')
            config = read(ROOT / 'config.json')
            states = {}
            for t in tasks:
                ident = t['id']
                directory = work / 'cases' / ident
                formula = directory / 'formula.cnf'
                meta = read(directory / 'formula.json')
                if ident not in checked_formulas:
                    require(sha(formula) == meta['sha256'], 'PREPARED_FORMULA_CHANGED')
                    checked_formulas.add(ident)
                result = read(directory / 'verdict.json')
                if result:
                    require(identity(formula) == result['formula'], 'COMPLETED_FORMULA_CHANGED')
                    receipt(ident + '_solve', cache)
                    require(identity(jobs / (ident + '_solve') / 'result.json') == result['solver_receipt'], 'SOLVER_RECEIPT_CHANGED')
                    if result['status'] == 'UNSAT_CERTIFIED':
                        receipt(ident + '_check', cache)
                        require(identity(jobs / (ident + '_check') / 'result.json') == result['checker_receipt'], 'CHECKER_RECEIPT_CHANGED')
                    states[ident] = result['status']
                    if result['status'] == 'GRAPH_VERIFIED':
                        save(work / 'FOUND_GRAPH.json', result)
                        return
                    continue
                solve_id = ident + '_solve'
                proof = jobs / solve_id / 'proof.lrat'
                solved = receipt(solve_id, cache)
                if not solved:
                    states[ident] = 'SOLVING' if (jobs / solve_id).exists() else 'PENDING'
                    if states[ident] == 'SOLVING' or active(jobs, 'solver') < config['solver_slots']:
                        submit(solve_id, [ROOT / 'bin/solver', '--seed=0', '--lrat=1', formula, proof], 'solver',
                               [formula, ROOT / 'bin/solver'], [proof], config)
                    continue
                if solved['returncode'] == 10:
                    values = model_values(solved['log']['path'])
                    verdict = verify_x(values, meta['root'], meta) if t['mode'] == 'X' else verify_full(values, meta['root'], t['mode'])
                    save(directory / 'verdict.json', {**verdict, 'formula': identity(formula), 'solver_receipt': identity(jobs / solve_id / 'result.json')})
                    states[ident] = verdict['status']
                    if verdict['status'] == 'GRAPH_VERIFIED':
                        save(work / 'FOUND_GRAPH.json', {**verdict, 'task': ident})
                        return
                    continue
                require(solved['returncode'] == 20, 'SOLVER_UNKNOWN_OR_ERROR: ' + ident)
                check_id = ident + '_check'
                checked = receipt(check_id, cache)
                if not checked:
                    states[ident] = 'UNSAT_AWAITING_CHECKER'
                    if (jobs / check_id).exists() or active(jobs, 'checker') < config['checker_slots']:
                        submit(check_id, [ROOT / 'bin/cake', f"--CML_HEAP_SIZE={config['cake_heap_mb']}",
                               f"--CML_STACK_SIZE={config['cake_stack_mb']}", formula, proof], 'checker',
                               [formula, proof, ROOT / 'bin/cake'], [], config)
                    continue
                require(checked['returncode'] == 0 and log_has(checked['log']['path'], 's VERIFIED UNSAT'), 'PROOF_NOT_VERIFIED')
                save(directory / 'verdict.json', {'status': 'UNSAT_CERTIFIED', 'task': t,
                     'scope': 'Necessary X model exclusion' if t['mode'] == 'X' else 'Normalized full-model case exclusion',
                     'formula': identity(formula), 'solver_receipt': identity(jobs / solve_id / 'result.json'),
                     'checker_receipt': identity(jobs / check_id / 'result.json')})
                states[ident] = 'UNSAT_CERTIFIED'
            done = all(s in ('UNSAT_CERTIFIED', 'INTERFACE_VERIFIED_ONLY') for s in states.values())
            state = {'status': 'STAGE_COMPLETE' if done else 'RUNNING', 'stage': stage, 'tasks': states,
                     'controller': proc(os.getpid()), 'updated_unix': time.time(), 'ETA': None,
                     'resources': host(work), 'pilot_is_not_full_LOW_exclusion': True}
            save(work / 'status.json', state)
            if done or time.monotonic() - last >= config['status_s']:
                print('LOW_STATUS', state, flush=True)
                last = time.monotonic()
            if done:
                return
            time.sleep(config['poll_s'])
    except BaseException as error:
        save(work / 'controller_error.json', {'error': repr(error), 'time': time.time(),
             'note': 'Existing detached supervisors continue or preserve their child; no automatic restart.'})
        raise


if __name__ == '__main__':
    run(sys.argv[1])
