"""Necessary weighted profile relaxation for tau=6. Solver infeasibility is NOT certified."""
from pathlib import Path
from itertools import combinations, combinations_with_replacement
import json
import time
import numpy as np
import networkx as nx
import sympy as sy
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import coo_matrix

BASE = Path(__file__).resolve().parents[2]

def exact_psd(G):
    for size in range(1, 7):
        for indices in combinations(range(6), size):
            determinant = int(sy.Matrix(G[np.ix_(indices, indices)].tolist()).det())
            if determinant < 0:
                return False, {'indices': indices, 'determinant': determinant}
    return True, None


def build(X):
    G = 6*np.eye(6, dtype=np.int64)+6-X@X-5*X
    profiles = []
    for mask in range(64):
        r = np.array([(mask >> j) & 1 for j in range(6)], dtype=np.int64)
        demand = 6-3*r-r@X
        if np.all(demand >= 0) and np.all(demand <= 14-sum(r)):
            profiles.append((mask, r, demand))
    m = len(profiles)
    columns = [('n', i, i) for i in range(m)]
    for kind, threshold in [('s', 5), ('l', 4)]:
        columns += [(kind, i, j) for i in range(m) for j in range(i, m) if profiles[i][1]@profiles[j][1] <= threshold]
    row_specs = [('total', 0, 0)] + [('gram', i, j) for i, j in combinations_with_replacement(range(6), 2)]
    row_specs += [(kind, i, j) for i in range(m) for kind, js in [('ds', [0]), ('dl', [0]), ('cross', range(6))] for j in js]
    rid = {v: i for i, v in enumerate(row_specs)}
    entries = []
    rhs = [27] + [int(G[i,j]) for i,j in combinations_with_replacement(range(6),2)] + [0]*(8*m)
    upper = []
    for c, (kind, i, j) in enumerate(columns):
        r = profiles[i][1]
        if kind == 'n':
            vals = {('total',0,0): 1, ('ds',i,0): -(10-int(sum(r))), ('dl',i,0): -2}
            vals.update({('gram',a,b): int(r[a]*r[b]) for a,b in combinations_with_replacement(range(6),2)})
            vals.update({('cross',i,a): -int(profiles[i][2][a]) for a in range(6)})
            upper.append(27)
        else:
            vals = {}
            for a, b in [(i,j),(j,i)]:
                key = ('d'+kind,a,0)
                vals[key] = vals.get(key,0)+1
                for q in range(6):
                    key = ('cross',a,q)
                    vals[key] = vals.get(key,0)+(2 if kind == 'l' else 1)*int(profiles[b][1][q])
            upper.append(135 if kind == 's' else 27)
        entries.extend((rid[key], c, value) for key,value in vals.items() if value)
    rows, cols, values = zip(*entries)
    A = coo_matrix((np.array(values,dtype=float),(rows,cols)),shape=(len(rhs),len(columns))).tocsc()
    return A, np.array(rhs,dtype=float), np.array(upper,dtype=float), columns, profiles


def main():
    graphs = [g for g in nx.graph_atlas_g() if len(g) == 6]
    assert len(graphs) == 156
    results = []
    for index, graph in enumerate(graphs):
        X = nx.to_numpy_array(graph,dtype=np.int64)
        G = 6*np.eye(6,dtype=np.int64)+6-X@X-5*X
        item = {'atlas6_index': index, 'X': X.tolist(), 'edges': int(X.sum()//2)}
        if np.any(G < 0):
            item['status'] = 'EXACT_NEGATIVE_GRAM_ENTRY'
        else:
            psd, witness = exact_psd(G)
            if not psd:
                item.update(status='EXACT_NEGATIVE_PRINCIPAL_MINOR', witness=witness)
            else:
                A,b,ub,columns,profiles = build(X)
                start = time.monotonic()
                solved = milp(np.zeros(A.shape[1]), integrality=np.ones(A.shape[1]), bounds=Bounds(np.zeros(A.shape[1]),ub), constraints=LinearConstraint(A,b,b), options={'time_limit':2.0})
                item.update(status='UNRESOLVED', solver_status=int(solved.status), seconds=time.monotonic()-start,
                            variables=A.shape[1], equations=A.shape[0], profile_count=len(profiles))
                if solved.x is not None:
                    z = np.rint(solved.x).astype(np.int64)
                    dense = A.toarray().astype(np.int64)
                    if np.array_equal(dense@z,b.astype(np.int64)) and np.all(z>=0) and np.all(z<=ub):
                        item.update(status='EXACT_AGGREGATE_FEASIBLE', witness=[int(v) for v in z],
                                    columns=columns, profile_masks=[p[0] for p in profiles])
                if solved.status == 2:
                    item['status'] = 'SOLVER_INFEASIBLE_UNCERTIFIED'
                print(index, item['status'], 'profiles',len(profiles),'vars',A.shape[1],flush=True)
        results.append(item)
    from collections import Counter
    out = {'status':'BOUNDED_AGGREGATE_SCOUT', 'X_classes':156,
           'counts':dict(Counter(v['status'] for v in results)),
           'scope':'No prescribed L cycle partition, no actual 27-vertex U realization, no phase lift. Numerical infeasibility is not a certificate.',
           'results':results}
    (BASE/'results/research_20260912/tau6_aggregate.json').write_text(json.dumps(out,indent=4)+'\n')
    print(json.dumps(out['counts']),flush=True)

if __name__ == '__main__':
    main()
