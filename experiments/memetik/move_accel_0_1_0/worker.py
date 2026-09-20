"""Use the frozen comparison worker; replace only its move source in fast jobs."""
import importlib.util
import json
import resource
import sys
from pathlib import Path

import bootstrap
from common import atomic


def main():
    directory = Path(sys.argv[1])
    task = json.loads((directory / 'task.json').read_text())
    if task['kind'] == 'controls':
        resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
        resource.setrlimit(resource.RLIMIT_CPU, (600, 602))
        from controls import check_cases
        import unittest
        import test_fast
        tests = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromModule(test_fast))
        if not tests.wasSuccessful():
            raise RuntimeError('Positive family fixture failed')
        report = check_cases(task['cases'], 570)
        report['positive_fixture_tests'] = tests.testsRun
        atomic(directory / 'result.json', report)
        return
    if task['engine'] not in ('reference', 'fast'):
        raise ValueError('Unknown engine')
    import search
    if task['engine'] == 'fast':
        from fast_moves import MoveSource
        search.MoveSource = MoveSource
    spec = importlib.util.spec_from_file_location('frozen_comparison_worker', bootstrap.BASELINE / 'worker.py')
    worker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(worker)
    worker.main()


if __name__ == '__main__':
    main()
