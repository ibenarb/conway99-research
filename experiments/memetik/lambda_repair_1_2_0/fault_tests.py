"""Destructive fault injection only in fresh disposable cloud test fixtures."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from common import *


def child(run, mode, control_source):
    from controller import Controller
    from tests import FakeHost
    from run import prepare
    from audit import audit
    prepare(run)
    shutil.copytree(control_source / 'controls', run / 'controls')
    shutil.copyfile(control_source / 'SCHEDULER_PREFLIGHT.json', run / 'SCHEDULER_PREFLIGHT.json')
    state = read(run / 'ledger.json')
    state['calibrated'] = True
    state['peak_worker_rss'] = 256 * 1024 ** 2
    atomic(run / 'ledger.json', state)
    c = Controller(run, host=FakeHost(), test=True)
    c.execute()
    result = read(run / 'RESULT.json')
    ledger = read(run / 'ledger.json')
    assert not ledger['active'] and not (run / 'session_active.json').exists()
    receipts = [read(run / 'receipts' / (t + '.json')) for t in ledger['receipts']]
    if mode == 'local':
        assert result['status'] == 'COMPLETED_WITH_LOCAL_ERRORS', result
        assert list(ledger['done'].values()).count('LOCAL_WORKER_ERROR') == 1
        assert len(ledger['done']) == 3
        audit(run)
    else:
        assert result['reason'] == 'RESULT_INTEGRITY_ERROR', result
        assert any(r.get('integrity_error') for r in receipts)
        assert any(r['category'] != 'aux' and r['cpu_seconds'] > 0 for r in receipts)
        try:
            audit(run)
            raise RuntimeError('Invalid output accepted by audit')
        except AssertionError:
            pass
    atomic(run / 'FAULT_TEST_RESULT.json', {'status': 'PASS', 'mode': mode,
                                           'terminal': result['status'], 'reason': result['reason'],
                                           'all_cpu_settled': True, 'clock': 'FakeHost'})


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path)
    p.add_argument('--controls-from', type=Path, required=True)
    p.add_argument('--child', type=Path)
    p.add_argument('--mode', choices=('local', 'invalid'))
    args = p.parse_args()
    if args.child:
        child(args.child, args.mode, args.controls_from)
        return
    root = args.out.resolve()
    root.mkdir(exist_ok=False)
    results = []
    for mode in ('local', 'invalid'):
        program = root / mode / 'fixture'
        shutil.copytree(HERE, program, ignore=shutil.ignore_patterns('__pycache__'))
        manifest = read(program / 'MANIFEST.json')
        manifest['tasks'] = [next(t for t in manifest['tasks'] if t['size'] == size) for size in (24, 40, 60)]
        for t in manifest['tasks']:
            t['cpu_limit_seconds'] = 15
        atomic(program / 'MANIFEST.json', manifest)
        wrapper = """import json,sys,time\nfrom pathlib import Path\nfrom common import *\ntask=read(sys.argv[1]);directory=Path(sys.argv[2]);target=float(sys.argv[-1])\nif task['size']==24:\n    if MODE=='invalid':\n        atomic(directory/'best.json',{'graph6':'?', 'scores':{}, 'state':'broken'})\n    raise SystemExit(7)\nwhile cpu()<target:\n    sum(i*i for i in range(10000))\natomic(directory/'result.json',{'status':'UNKNOWN_CPU_OR_PAUSE','process_cpu_seconds':cpu()})\n""".replace('MODE', repr(mode))
        (program / 'worker.py').write_text(wrapper)
        package = read(program / 'PACKAGE.json')
        package['files']['worker.py'] = digest(program / 'worker.py')
        package['files']['MANIFEST.json'] = digest(program / 'MANIFEST.json')
        atomic(program / 'PACKAGE.json', package)
        run = root / mode / 'run'
        with (root / (mode + '.log')).open('w') as log:
            subprocess.run([sys.executable, str(program / 'fault_tests.py'), '--child', str(run),
                            '--mode', mode, '--controls-from', str(args.controls_from.resolve())],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        results.append(read(run / 'FAULT_TEST_RESULT.json'))
    atomic(root / 'RESULT.json', {'status': 'PASS', 'tests': results})
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
