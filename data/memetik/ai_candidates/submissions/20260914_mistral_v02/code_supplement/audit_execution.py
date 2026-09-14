import collections
import json
import platform
import numpy as np
import scipy
import generators_transcribed as supplied

results = []
for name in ['generate_omega_conway', 'generate_tridecomp', 'generate_randfill']:
    function = getattr(supplied, name)
    np.random.seed(42)
    try:
        graph6, matrix = function()
        outcome = 'returned'
    except Exception as error:
        outcome = type(error).__name__
        trace = error.__traceback__
        matrix = None
        while trace:
            if trace.tb_frame.f_code.co_name == name:
                matrix = trace.tb_frame.f_locals.get('A')
            trace = trace.tb_next
        if matrix is None:
            raise
    adjacency = [set(np.flatnonzero(row)) for row in matrix]
    histogram = collections.Counter()
    bad_edges = 0
    for i in range(99):
        for j in range(i + 1, 99):
            common = len(adjacency[i] & adjacency[j])
            edge = j in adjacency[i]
            histogram[common + int(edge) - 2] += 1
            bad_edges += int(edge and common != 1)
    independent = (sum(v for r, v in histogram.items() if r),
                   sum(abs(r)*v for r, v in histogram.items()),
                   sum(r*r*v for r, v in histogram.items()), max(map(abs, histogram)))
    results.append({'function': name, 'outcome': outcome,
                    'degree_histogram': dict(collections.Counter(map(len, adjacency))),
                    'edge_count': sum(map(len, adjacency))//2,
                    'lambda_bad_edges': bad_edges,
                    'supplied_metrics': list(map(int, supplied.compute_metrics(matrix))),
                    'independent_metrics': independent,
                    'metrics_match': tuple(supplied.compute_metrics(matrix)) == independent})
print(json.dumps({'python': platform.python_version(), 'numpy': np.__version__,
                  'scipy': scipy.__version__, 'seed': 42, 'results': results}, indent=4))
