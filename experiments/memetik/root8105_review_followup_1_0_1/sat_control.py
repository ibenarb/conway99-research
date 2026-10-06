import bootstrap
"""Independent necessary-condition CNFs. No calls to kernel.constraints or filters.

LD follows from the pair equation of a built centre u and its neighbour v:
if their labels intersect, their H-codegree is 2-1-1=0. Each forbidden edge
is a nonnegative summand in such a zero sum. CAP uses a single open row's
necessary degree, border, and built-row codegree equations. This is a
relaxation, not a full SRG encoding. UNSAT checks are not formal certificates.
"""
import itertools
import time
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Glucose4


def geometry(m):
    return [(a, b) for a in range(2 * m) for b in range(a + 1, 2 * m) if b - a != m]


def encode(rows, m, ld, cap, target=None):
    labels = geometry(m)
    n = len(labels)
    pool, cnf, edges = IDPool(), CNF(), {}

    def edge(a, b):
        if a == b:
            return False
        if a in rows:
            return bool(rows[a] & (1 << b))
        if b in rows:
            return bool(rows[b] & (1 << a))
        pair = tuple(sorted((a, b)))
        if pair not in edges:
            edges[pair] = pool.id(pair)
        return edges[pair]

    def exactly(terms, bound):
        fixed = sum(x for x in terms if type(x) is bool)
        literals = [x for x in terms if type(x) is int]
        bound -= fixed
        if bound < 0 or bound > len(literals):
            cnf.append([])
        elif literals:
            cnf.extend(CardEnc.equals(lits=literals, bound=bound, vpool=pool,
                                     encoding=EncType.totalizer).clauses)

    if ld:
        # Derive zero-codegree equations directly, without the filter's banned set.
        for u, mask in sorted(rows.items()):
            neighbors = [w for w in range(n) if mask & (1 << w)]
            for v in neighbors:
                if set(labels[u]).intersection(labels[v]):
                    exactly([edge(v, w) for w in neighbors], 0)
            # The label-disjoint rule also applies to any two neighbours v,w
            # of u sharing a border label. They already share u and that label,
            # so their adjacency would demand codegree 1, a contradiction.
            for v, w in itertools.combinations(neighbors, 2):
                if set(labels[v]).intersection(labels[w]):
                    exactly([edge(v, w)], 0)
    if cap:
        if target is None or target in rows:
            raise ValueError('CAP control requires an open target row')
        v = target
        exactly([edge(v, w) for w in range(n)], 2 * m - 2)
        special = set(labels[v]) | {(x + m) % (2 * m) for x in labels[v]}
        for a in range(2 * m):
            exactly([edge(v, w) for w in range(n) if a in labels[w]], 1 if a in special else 2)
        for u, mask in sorted(rows.items()):
            bound = 2 - int(bool(mask & (1 << v))) - len(set(labels[u]).intersection(labels[v]))
            exactly([edge(v, w) for w in range(n) if mask & (1 << w)], bound)
    return cnf, edges


def check(rows, m, ld, cap, target=None, witness=None):
    started = time.process_time()
    cnf, edges = encode(rows, m, ld, cap, target)
    encoding_cpu = time.process_time() - started
    assumptions = []
    if witness is not None:
        assumptions = [lit if witness[a] & (1 << b) else -lit for (a, b), lit in edges.items()]
    started = time.process_time()
    with Glucose4(bootstrap_with=cnf.clauses) as solver:
        result = solver.solve(assumptions=assumptions)
        stats = solver.accum_stats()
    return {'status': 'SAT' if result is True else ('UNSAT_UNCERTIFIED' if result is False else 'UNKNOWN'),
            'encoding_cpu_s': encoding_cpu, 'solve_cpu_s': time.process_time() - started,
            'variables': cnf.nv, 'clauses': len(cnf.clauses), 'solver_stats': stats,
            'certified': False, 'model': 'independent-local-necessary-CNF-v1'}
