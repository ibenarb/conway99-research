"""Office C2 C4 lemma verification and complete profile_46 certification."""
import argparse
import collections
import fcntl
import gzip
import itertools
import json
import os
from pathlib import Path
import random
import shutil
import signal
import sys
import tarfile
import time

import anchor_profile as ap
from c2_reference import reconstruct, verify_graph
from coverage import cycle_edges
from model import augment, BASE_SHA, MAP_SHA
from runtime import Runtime, BudgetStop, save, sha, task, verified

ROOT = Path(__file__).resolve().parent
PROFILE_SHA = '5b251b4832904a3bd2ce7d804508e380794444f19c70ba8b26903cb1b4b02859'
SOLVER_SHA = '82c88e3027d35e7c60293ea9440fc97576e1161ee9e103785bdb6962748ba996'
CHECKER_SHA = '760e248a4dbafa9cd8834174cc8a2164e7f79dd60619f43070dba88cf8588130'
VERSION = '1.0.0'
SCOPE = ('Conditional on the C2 encoding and semantic frame invariance: profile_46 is UNSAT; '
         'some anchor has d <= 3 (using the matching exclusion of d=5). '
         'Rest type d=4 is excluded under priority (0,1,2,3,4,6). No full C2 exclusion.')


def header_variables(path):
    with Path(path).open() as stream:
        return int(stream.readline().split()[2])


def require(path, expected):
    if not Path(path).is_file() or sha(path) != expected:
        raise ValueError('Missing file or hash mismatch: ' + str(path))


def success(row):
    return row['returncode'] == 0 and row['reason'] is None


def lines(row):
    return Path(row['log']).read_text(errors='replace').splitlines()


def transfer(src, dst, rt):
    while block := src.read(4 * 1024 ** 2):
        dst.write(block)
        rt.guard()


def expand(source, target, expected, rt):
    if target.exists() and sha(target) == expected:
        return
    temp = target.with_suffix(target.suffix + '.writing')
    with gzip.open(source, 'rb') as src, temp.open('wb') as dst:
        transfer(src, dst, rt)
    require(temp, expected)
    temp.replace(target)


def archive_proof(proof, rt):
    expected = sha(proof)
    target = proof.with_suffix('.drat.gz')
    temp = target.with_suffix('.writing')
    with proof.open('rb') as src, gzip.open(temp, 'wb', compresslevel=3) as dst:
        transfer(src, dst, rt)
    import hashlib
    h = hashlib.sha256()
    with gzip.open(temp, 'rb') as src:
        while block := src.read(4 * 1024 ** 2):
            h.update(block)
            rt.guard()
    if h.hexdigest() != expected:
        raise ValueError('Proof compression round-trip failed')
    temp.replace(target)
    return {'file': str(target), 'gzip_sha256': sha(target), 'uncompressed_sha256': expected}


def check_sat(row, folder, cube):
    frame = ap.frame(14)
    values = {}
    for line in lines(row):
        if line.startswith('v '):
            for lit in map(int, line[2:].split()):
                if lit and abs(lit) <= len(frame.map):
                    if abs(lit) in values and values[abs(lit)] != (lit > 0):
                        raise ValueError('Conflicting SAT assignment')
                    values[abs(lit)] = lit > 0
    if set(values) != set(range(1, len(frame.map) + 1)):
        raise ValueError('Incomplete primary SAT model')
    if any(values[abs(v)] != (v > 0) for v in cube):
        raise ValueError('SAT model violates cube')
    graph = reconstruct(frame, values)
    if not verify_graph(graph, 14):
        raise ValueError('SAT graph check failed')
    involution = [0] + [1 + (a ^ 1) for a in range(14)]
    involution += [15 + ((a + frame.pairs) % (2 * frame.pairs)) for a in range(2 * frame.pairs)]
    assert sum(involution[i] == i for i in range(99)) == 1
    assert all(graph[a][b] == graph[involution[a]][involution[b]] for a in range(99) for b in range(99))
    save(folder / 'SAT_GRAPH.json', {'adjacency': graph, 'involution': involution})


def controls(rt, solver, checker):
    folder = rt.work / 'controls'
    folder.mkdir(exist_ok=True)
    cnf = folder / 'unsat.cnf'
    cnf.write_text('p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n')
    good = folder / 'valid.drat'
    bad = folder / 'invalid.drat'
    good.write_text('1 0\n0\n')
    bad.write_text('')
    a, b = [rt.batch([task('control_' + name, [checker, cnf, proof], 30)], 'checker-controls', 1)[0]
            for name, proof in [('positive', good), ('negative', bad)]]
    if not verified(a) or verified(b) or b['returncode'] != 1 or b['reason'] is not None:
        raise ValueError('Checker positive/negative controls failed')
    proof = folder / 'solver.drat'
    row = rt.batch([task('control_solver', [solver, '--seed=0', cnf, proof], 30, [proof])], 'solver-control', 1)[0]
    if row['reason'] is not None or row['returncode'] != 20 or 's UNSATISFIABLE' not in lines(row):
        raise ValueError('Solver UNSAT control failed')
    row = rt.batch([task('control_generated_proof', [checker, cnf, proof], 30)], 'solver-proof-control', 1)[0]
    if not verified(row):
        raise ValueError('Solver proof control failed')
    sat = folder / 'sat.cnf'
    sat.write_text('p cnf 2 2\n1 0\n-2 0\n')
    row = rt.batch([task('control_sat', [solver, '--seed=0', sat], 30)], 'solver-sat-control', 1)[0]
    model = {int(x) for line in lines(row) if line.startswith('v ') for x in line[2:].split()}
    if row['reason'] is not None or row['returncode'] != 10 or not {1, -2} <= model:
        raise ValueError('Solver SAT control failed')
    program = ('import time\ntime.sleep(1)\nn=0\nwhile True:\n    n+=1\n'
               '    if n%100000==0: print("CHILD_CPU",time.process_time(),flush=True)\n')
    rows = rt.batch([task('cpu_calibration_' + str(i), [sys.executable, '-u', '-c', program], 2)
                     for i in range(3)], 'cpu-calibration', 3)
    for row in rows:
        readings = [float(line.split()[1]) for line in lines(row) if line.startswith('CHILD_CPU ')]
        if not (row['reason'] == 'CPU_BUDGET' and 1.9 <= row['cpu_seconds'] <= 4
                and readings and abs(readings[-1] - row['cpu_seconds']) < 0.5):
            raise ValueError('CPU calibration failed')
    save(rt.work / 'controls.json', {'status': 'PASS', 'cpu_rows': rows,
                                    'scope': 'CPU accounting tested; host clock cause not asserted'})


def prepare(old, rt):
    base = old / 'work/base/base.cnf'
    profile = old / 'work/profile_46.cnf'
    solver = Path.home() / 'conway99_workspace/cadical_office_2.2.1/build/cadical'
    checker = old / 'work/drat-trim'
    for path, expected in [(base, BASE_SHA), (old / 'work/base/variables.json', MAP_SHA),
                           (profile, PROFILE_SHA), (solver, SOLVER_SHA), (checker, CHECKER_SHA)]:
        require(path, expected)
    rt.guard()
    controls(rt, solver, checker)
    group = rt.batch([task('frame_group', [sys.executable, ROOT / 'anchor_profile.py', 'check'], 300)],
                     'frame-invariance', 1)[0]
    if not success(group) or not any(x.startswith('ANCHOR_PROFILE_CHECK_PASS ') for x in lines(group)):
        raise ValueError('Frame invariance check failed')
    compiler = shutil.which('gcc')
    if compiler is None:
        raise RuntimeError('gcc is required for the finite labelled count')
    counter = rt.work / 'count46'
    compiled = rt.batch([task('compile_count', [compiler, '-O3', ROOT / 'count46.c', '-o', counter], 120,
                                     [counter])], 'coverage-compile', 1)[0]
    if not success(compiled):
        raise ValueError('Counter compilation failed')
    count = rt.batch([task('labelled_count', [counter], 600)], 'coverage-count', 1)[0]
    expected = ['C4 105  labelled 10690440', '  with 0 classes d=6: 10448730',
                '  with 1 classes d=6: 241710']
    if not success(count) or lines(count) != expected:
        raise ValueError('Labelled count mismatch')
    coverage_file = rt.work / 'coverage.json'
    cov = rt.batch([task('independent_orbits', [sys.executable, ROOT / 'coverage.py', coverage_file],
                        300, [coverage_file])], 'coverage-orbits', 1)[0]
    if not success(cov):
        raise ValueError('Independent orbit verification failed')
    meta = json.loads((ROOT / 'lemma_certificates.json').read_text())
    arcs = ap.arcs(ap.frame(14))
    formula = rt.work / 'bi_c4.cnf'
    units = [[arcs[e]] for e in sorted(cycle_edges((0, 1, 2, 3)))]
    augment(base, formula, header_variables(base), units)
    require(formula, meta['formula_sha256'])
    proof = rt.work / 'bi_c4.drat'
    require(ROOT / 'bi_c4_seed0.drat.gz', meta['proof_gz_sha256'])
    expand(ROOT / 'bi_c4_seed0.drat.gz', proof, meta['proof_sha256_uncompressed'], rt)
    row = rt.batch([task('c4_lemma_check', [checker, formula, proof], 1800, memory=3)], 'c4-proof', 1)[0]
    if not verified(row):
        raise ValueError('C4 lemma NOT verified; no cube certification started')
    lemma = {'status': 'UNSAT_VERIFIED', 'formula_sha256': sha(formula), 'units': units,
             'proof_archive': {'file': str(ROOT / 'bi_c4_seed0.drat.gz'),
                               'gzip_sha256': meta['proof_gz_sha256'],
                               'uncompressed_sha256': meta['proof_sha256_uncompressed']}, 'checker': row,
             'transport': 'work/coverage.json: 105 clauses, semantic class permutations'}
    save(rt.work / 'c4_certificate.json', lemma)
    save(rt.work / 'preflight.json', {'status': 'PASS', 'base_sha256': BASE_SHA,
          'profile_sha256': PROFILE_SHA, 'mapping_sha256': MAP_SHA,
          'solver': str(solver), 'solver_sha256': SOLVER_SHA, 'checker': str(checker),
          'checker_sha256': CHECKER_SHA, 'group_check': group, 'labelled_count': count,
          'orbit_check': cov, 'coverage_sha256': sha(coverage_file), 'lemma': lemma})
    rt.checkpoint()
    print('FULLCERT_PREFLIGHT_PASS', flush=True)
    return profile, solver, checker


def initial_state(work):
    path = work / 'round.json'
    identity = {'version': VERSION, 'manifest_sha256': sha(ROOT / 'MANIFEST.json'),
                'profile_sha256': PROFILE_SHA, 'cube_list_sha256': sha(ROOT / 'cubes46.txt'),
                'cpu_cap': 28800, 'solver_options': ['--seed=0']}
    state = json.loads(path.read_text()) if path.exists() else {'identity': identity, 'cubes': {}}
    if state['identity'] != identity:
        raise ValueError('Round identity mismatch')
    for cube in state['cubes'].values():
        if cube['status'] == 'UNSAT_VERIFIED':
            proof = cube['proof_archive']
            require(proof['file'], proof['gzip_sha256'])
            for key in ('solve', 'checker'):
                require(cube[key]['log'], cube[key]['log_sha256'])
            if not verified(cube['checker']):
                raise ValueError('Previously verified receipt changed')
    save(path, state)
    return state


def cube_order():
    rows = [line.split() for line in (ROOT / 'profile46_incremental_results.txt').read_text().splitlines()]
    hardest = [int(r[0]) for r in sorted(rows, key=lambda r: float(r[2]), reverse=True)[:20]]
    remaining = [i for i in range(2170) if i not in hardest]
    random.Random(20260926).shuffle(remaining)
    pilot = hardest + remaining[:20]
    return pilot + sorted(set(range(2170)) - set(pilot)), set(pilot)


def certify(rt, state, profile, solver, checker):
    cubes = [[int(x) for x in line.split()[:-1]] for line in (ROOT / 'cubes46.txt').read_text().splitlines()]
    order, pilot = cube_order()
    state['pilot_indices'] = sorted(pilot)
    round_file = rt.work / 'round.json'
    completed = state['cubes']
    # Open timed-out cases are retained and reported, not silently retried.
    pending = [i for i in order if str(i) not in completed or completed[str(i)]['status'] == 'UNSAT_UNCERTIFIED']
    while pending:
        rt.guard()
        batch, pending = pending[:3], pending[3:]
        solve_tasks = []
        folders = {}
        for i in batch:
            key = str(i)
            folder = rt.work / 'certificates' / ('cube_%04d' % i)
            folder.mkdir(parents=True, exist_ok=True)
            folders[i] = folder
            cnf = folder / 'formula.cnf'
            proof = folder / 'proof.drat'
            digest = augment(profile, cnf, header_variables(profile), [[v] for v in cubes[i]])
            existing = completed.get(key)
            if existing and existing['formula_sha256'] != digest:
                raise ValueError('Cube formula identity mismatch')
            if existing and existing['status'] == 'UNSAT_UNCERTIFIED':
                require(proof, existing['proof_sha256'])
            else:
                solve_tasks.append(task('cube_%04d_solve' % i,
                                        [solver, '--seed=0', cnf, proof], 600, [proof]))
            save(folder / 'formula.json', {'index': i, 'base_sha256': PROFILE_SHA,
                                         'units': cubes[i], 'formula_sha256': digest})
        rt.progress = {'certified': sum(c['status'] == 'UNSAT_VERIFIED' for c in completed.values()),
                       'total': 2170, 'pending_cases': len(pending) + len(batch)}
        rows = rt.batch(solve_tasks, 'cube-solve', 3)
        for row in rows:
            i = int(row['id'].split('_')[1])
            folder = folders[i]
            item = {'index': i, 'units': cubes[i], 'formula_sha256': sha(folder / 'formula.cnf'), 'solve': row}
            if row['reason'] is None and row['returncode'] == 20 and 's UNSATISFIABLE' in lines(row):
                item.update(status='UNSAT_UNCERTIFIED', proof_sha256=sha(folder / 'proof.drat'))
            elif row['reason'] is None and row['returncode'] == 10 and 's SATISFIABLE' in lines(row):
                check_sat(row, folder, cubes[i])
                item['status'] = 'SAT_GRAPH_VERIFIED'
                completed[str(i)] = item
                state['status'] = 'SAT_GRAPH_VERIFIED'
                save(round_file, state)
                return
            elif row['reason'] == 'CPU_BUDGET' or row['returncode'] == 0 and 's UNKNOWN' in lines(row):
                item['status'] = 'OPEN_SEARCH'
            else:
                item['status'] = 'EXECUTION_ERROR'
            completed[str(i)] = item
            save(round_file, state)
            if item['status'] == 'EXECUTION_ERROR':
                raise RuntimeError('Unexpected solver outcome for cube ' + str(i))
        checks = [task('cube_%04d_check' % i,
                       [checker, folders[i] / 'formula.cnf', folders[i] / 'proof.drat'], 1800, memory=3)
                  for i in batch if completed[str(i)]['status'] == 'UNSAT_UNCERTIFIED']
        checked = rt.batch(checks, 'cube-check', 3)
        for row in checked:
            i = int(row['id'].split('_')[1])
            item = completed[str(i)]
            item['checker'] = row
            if verified(row):
                item['proof_archive'] = archive_proof(folders[i] / 'proof.drat', rt)
                item['status'] = 'UNSAT_VERIFIED'
                save(round_file, state)
                # Only derived, reproducible CNFs and verified raw proof copies are removed.
                (folders[i] / 'proof.drat').unlink(missing_ok=True)
                (folders[i] / 'formula.cnf').unlink(missing_ok=True)
            elif row['reason'] == 'CPU_BUDGET':
                item['status'] = 'OPEN_CHECK'
                save(round_file, state)
            else:
                item['status'] = 'CHECKER_REJECTED'
                save(round_file, state)
                raise RuntimeError('Checker did not verify cube ' + str(i))
        if not state.get('pilot') and all(str(i) in completed and completed[str(i)]['status'] != 'UNSAT_UNCERTIFIED'
                                          for i in pilot):
            selected = [completed[str(i)] for i in sorted(pilot)]
            state['pilot'] = {'cases': len(selected),
                              'verified': sum(c['status'] == 'UNSAT_VERIFIED' for c in selected),
                              'solver_checker_cpu_s': sum(c['solve']['cpu_seconds'] + c.get('checker', {}).get('cpu_seconds', 0)
                                                        for c in selected),
                              'scope': '20 historically slow plus 20 random; not an unbiased runtime forecast'}
            print('FULLCERT_PILOT ' + json.dumps(state['pilot']), flush=True)
        save(round_file, state)
        rt.checkpoint()
    counts = dict(collections.Counter(c['status'] for c in completed.values()))
    state['counts'] = counts
    state['status'] = 'PROFILE46_UNSAT_VERIFIED' if counts == {'UNSAT_VERIFIED': 2170} else 'ROUND_INCOMPLETE'
    state['claim'] = SCOPE if state['status'] == 'PROFILE46_UNSAT_VERIFIED' else 'No profile exclusion claimed; unresolved cases remain.'
    state['dependencies'] = ['preflight.json', 'coverage.json', 'c4_certificate.json',
                             '2170 individual formula descriptions, proof archives and checker receipts']
    save(round_file, state)


def export(work):
    target = ROOT / ('C2_Profile46Cert_' + VERSION + '_results.tar.gz')
    temporary = target.with_suffix('.writing')
    with tarfile.open(temporary, 'w:gz') as out:
        for file in sorted(ROOT.iterdir()):
            if file.is_file() and file.suffix in ('.py', '.c', '.json', '.md', '.txt'):
                out.add(file, arcname=file.name)
        for file in sorted(work.rglob('*')):
            if file.is_file() and file.suffix in ('.json', '.log'):
                out.add(file, arcname=str(file.relative_to(ROOT)))
        if (ROOT / 'controller.log').is_file():
            out.add(ROOT / 'controller.log', arcname='controller.log')
    temporary.replace(target)
    print('RESULT_ARCHIVE ' + str(target), flush=True)
    print('PROOFS_RETAINED ' + str(work / 'certificates'), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--old', type=Path, default=Path.home() / 'conway99_workspace/Conway99_C2_AnchorProfile_1.0.0')
    args = parser.parse_args()
    if not (args.run or args.prepare):
        parser.error('Specify --prepare or --run')
    for name, expected in json.loads((ROOT / 'MANIFEST.json').read_text()).items():
        require(ROOT / name, expected)
    work = ROOT / 'work'
    work.mkdir(exist_ok=True)
    with (work / 'run.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('ALREADY_RUNNING', flush=True)
            return 0
        def interrupted(signum, frame):
            raise KeyboardInterrupt('Signal ' + str(signum))
        signal.signal(signal.SIGTERM, interrupted)
        rt = Runtime(work)
        state = None
        try:
            state = initial_state(work)
            if state.get('status') == 'SAT_GRAPH_VERIFIED':
                print('FULLCERT_RESULT SAT_GRAPH_VERIFIED: existing result retained', flush=True)
                return 0
            profile, solver, checker = prepare(args.old.resolve(), rt)
            if args.run:
                certify(rt, state, profile, solver, checker)
            else:
                if state.get('status') != 'PROFILE46_UNSAT_VERIFIED':
                    state['status'] = 'PREPARED'
                save(work / 'round.json', state)
            print('FULLCERT_RESULT ' + json.dumps({'status': state['status'], 'used_cpu_s': rt.used()}), flush=True)
            return 0
        except BaseException as exc:
            status = 'BUDGET_EXHAUSTED' if isinstance(exc, BudgetStop) else (
                'INTERRUPTED' if isinstance(exc, KeyboardInterrupt) else 'STOPPED_WITH_ERROR')
            save(work / 'last_error.json', {'status': status, 'error': type(exc).__name__, 'detail': str(exc)})
            if state is not None:
                state['status'] = status
                save(work / 'round.json', state)
            print('FULLCERT_RESULT ' + json.dumps({'status': status, 'detail': str(exc)}), flush=True)
            return 2
        finally:
            rt.checkpoint()
            export(work)
            rt.checkpoint()


if __name__ == '__main__':
    raise SystemExit(main())
