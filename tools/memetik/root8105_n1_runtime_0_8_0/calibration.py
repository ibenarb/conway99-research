"""Prepare only the two approved N1 cases; preparation never starts a solver."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import calibration_gate as gate
import runtime as r


def prepare(output):
    if importlib.metadata.version('python-sat') != '1.9.dev15' or importlib.metadata.version('six') != '1.17.0':
        raise ValueError('Pinned Python dependencies required')
    workspace = Path.home() / 'conway99_workspace'
    inputs = workspace / 'ROOT8105_N1_Kalibrierung_Eingaben_1.0'
    native = workspace / 'ROOT8105_N1_native_072'
    worker, checker = native / 'n1-worker', native / 'drat-trim'
    if r.sha(worker) != gate.WORKER_SHA or r.sha(checker) != gate.CHECKER_SHA:
        raise ValueError('Native build differs from accepted Ryzen build')
    gate.evidence()
    output.mkdir(exist_ok=False)
    results = []
    for root_id in (210, 6682):
        name = 'r' + str(root_id) + '_class000'
        root = output / name
        argv = [sys.executable, str(Path(__file__).with_name('runtime.py')), 'init', str(root),
                '--profile', 'n1-production', '--platform-wsl',
                '--cnf', str(inputs / (name + '.cnf')), '--binding', str(inputs / (name + '_binding.json')),
                '--catalog', str(inputs / 'CATALOG_RECEIPT.json'),
                '--worker', str(worker), '--checker', str(checker),
                '--budget', '21600', '--total-budget', '28800',
                '--max-rss-bytes', str(24*gate.GIB), '--min-available-bytes', str(8*gate.GIB),
                '--min-free-bytes', str(100*gate.GIB)]
        with (output / (name + '-init.log')).open('xb') as log:
            subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT, check=True)
        logpath = output / (name + '-preflight.log')
        with logpath.open('xb') as log:
            subprocess.run([sys.executable, str(Path(__file__).with_name('runtime.py')), 'preflight', str(root)],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        report = json.loads(logpath.read_text())
        r.raw_atomic(output / (name + '-PREFLIGHT.json'), report)
        if not report['allowed'] or report['status'] != 'CALIBRATION_READY':
            raise ValueError(name + ': ' + ', '.join(report['blockers']))
        import accounting
        accounts = accounting.inventory(root)
        if not accounts['observed_commands_complete']:
            raise ValueError('Preparation accounts incomplete: ' + name)
        state = r.read(root / 'state.json')
        if state['status'] != 'READY' or state['attempts']:
            raise ValueError('Unexpected search during preparation')
        results.append(dict(root_id=root_id, class_id=0, status='READY',
                            preflight='CALIBRATION_READY', preparation_accounts_complete=True))
    receipt = dict(status='CALIBRATION_PREPARED', tasks=results, solver_started=False,
                   native_budget_seconds_per_case=21600, aggregate_budget_seconds_per_case=28800,
                   budgets_are_extension_decision_points=True, parallel_calibrations=False,
                   runtime=str(Path(__file__).with_name('runtime.py')), output=str(output))
    r.raw_atomic(output / 'PREPARED.json', receipt)
    print(json.dumps(receipt, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    prepare(args.output.resolve())


if __name__ == '__main__':
    main()
