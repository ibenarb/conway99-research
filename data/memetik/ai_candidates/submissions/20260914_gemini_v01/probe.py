"""Run supplied generator; override only solver time/workers for a bounded probe."""
import contextlib
import json
import pathlib
import platform
import sys
import time
import networkx as nx
import numpy as np
import ortools
from ortools.sat.python import cp_model
import generator

record = {'python': platform.python_version(), 'numpy': np.__version__,
          'networkx': nx.__version__, 'ortools': ortools.__version__,
          'probe_overrides': {'max_time_in_seconds': 45.0, 'num_search_workers': 1},
          'seed': 42, 'model_changes': 'none'}
original = cp_model.CpSolver.Solve

def bounded(self, model, *args, **kwargs):
    self.parameters.max_time_in_seconds = 45.0
    self.parameters.num_search_workers = 1
    record['model_validation'] = model.Validate()
    record['model_stats'] = model.ModelStats()
    started = time.monotonic()
    status = original(self, model, *args, **kwargs)
    record['elapsed_solve_seconds'] = time.monotonic() - started
    record['solver_status'] = self.StatusName(status)
    record['solver_response_stats'] = self.ResponseStats()
    return status

cp_model.CpSolver.Solve = bounded
sys.argv = ['generator.py', '42']
with open('probe_console.log', 'w') as log, contextlib.redirect_stdout(log):
    generator.main()
pathlib.Path('probe.json').write_text(json.dumps(record, indent=4)+'\n')
print(json.dumps(record, indent=4))
