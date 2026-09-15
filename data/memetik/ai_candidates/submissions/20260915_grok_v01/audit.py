"""Independent bounded audit; source scripts are imported without modification."""
import collections
import hashlib
import importlib.util
import inspect
import itertools
import json
import pathlib
import subprocess
import sys
import time
import networkx as nx
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent

def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def attempt(call):
    try:
        value = call()
        return {'status': 'RETURNED', 'value': repr(value)}
    except Exception as error:
        return {'status': 'ERROR', 'type': type(error).__name__, 'message': str(error)}

def main():
    f1, f2, helpers, verifier = [module(n) for n in ['gen_F01', 'gen_F02', 'helpers', 'verify_candidates']]
    report = {'versions': {'python': sys.version, 'networkx': nx.__version__, 'numpy': np.__version__}}
    g = nx.empty_graph(99)
    for triangle in [(0, 1, 2), (0, 3, 4), (1, 3, 5)]:
        assert not any(g.has_edge(a, b) for a, b in itertools.combinations(triangle, 2))
        g.add_edges_from(itertools.combinations(triangle, 2))
    report['F01_linear_hypergraph_counterexample'] = {'triples': [[0,1,2],[0,3,4],[1,3,5]], 'common_neighbors_edge_0_1': sorted(set(g[0]) & set(g[1])), 'lambda_check': bool(f1.is_lambda1(g))}
    report['networkx_is_regular_signature'] = str(inspect.signature(nx.is_regular))
    report['networkx_is_simple_path_signature'] = str(inspect.signature(nx.is_simple_path))
    report['F02_direct_regularity_call'] = attempt(lambda: nx.is_regular(f2.cayley({1,98}), 14))
    report['verifier_check_hard'] = attempt(lambda: verifier.check_hard(g, 'lambda'))
    report['helper_encoder_placeholder'] = attempt(lambda: helpers.to_graph6(g))
    encoded = f1.graph_to_graph6(g)
    report['F01_encoder_matches_networkx_on_99_vertex_fixture'] = encoded + '\n' == nx.to_graph6_bytes(g, header=False).decode()
    independent = collections.Counter(len(set(g[i]) & set(g[j])) + int(g.has_edge(i,j)) - 2 for i in range(99) for j in range(i+1,99))
    linf = max(map(abs,independent))
    expected = {'W': sum(v for k,v in independent.items() if k), 'L1': sum(abs(k)*v for k,v in independent.items()), 'F': sum(k*k*v for k,v in independent.items()), 'Linf': linf, 'Nmax': sum(v for k,v in independent.items() if abs(k)==linf), 'lambda_bad_edges': sum(len(set(g[u]) & set(g[v])) != 1 for u,v in g.edges()), 'residual_histogram': {str(k):v for k,v in independent.items()}}
    report['score_helpers_agree_with_independent_fixture'] = helpers.full_scores(g) == expected and verifier.recompute_scores(g) == expected
    report['bounded_runs'] = []
    for script, args in [('gen_F01.py',['--seed','42','--max_tries','1']), ('gen_F02.py',['--seed','1','--max_tries','1']), ('verify_candidates.py',[str(ROOT/'original.md')])]:
        start = time.perf_counter()
        result = subprocess.run([sys.executable,str(ROOT/script),*args],capture_output=True,text=True,timeout=20)
        report['bounded_runs'].append({'script':script,'args':args,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'wall_seconds':time.perf_counter()-start})
    report['Z99_elements_satisfying_3d_equals_0_nonzero'] = [d for d in range(1,99) if 3*d % 99 == 0]
    report['source_sha256'] = hashlib.sha256((ROOT/'original.md').read_bytes()).hexdigest()
    (ROOT/'audit.json').write_text(json.dumps(report,indent=4)+'\n')
    print(json.dumps(report,indent=4))

if __name__ == '__main__':
    main()
