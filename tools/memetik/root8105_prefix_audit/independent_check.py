"""Direct partial-SRG checks and joint completed-star feasibility.

No imports from the historical search, geometry, sampler or propagation modules.
SAT witnesses are checked against integer equations without trusting CNF helpers.
This is a necessary relaxation; a witness is not a complete SRG.
"""
import itertools
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Glucose4


def require(condition, message):
    if not condition:
        raise ValueError(message)


def construct(data):
    m = data.get('m', 7)
    b = 2 * m
    labels = [[a, c] for a in range(b) for c in range(a + 1, b) if c - a != m]
    require(data['labels'] == labels, 'label_mapping')
    h = len(labels)
    n = 1 + b + h
    rows = {int(u): list(vs) for u, vs in data['rows'].items()}
    require(0 in rows, 'missing_root')
    a = [[None] * n for _ in range(n)]
    for u in range(n):
        a[u][u] = 0

    def set_edge(u, v, bit):
        require(a[u][v] is None or a[u][v] == bit, 'symmetry_or_assignment')
        a[u][v] = a[v][u] = bit

    for v in range(1, n):
        set_edge(0, v, int(v <= b))
    for u in range(b):
        for v in range(u + 1, b):
            set_edge(1 + u, 1 + v, int(v - u == m))
        for v, pair in enumerate(labels):
            set_edge(1 + u, 1 + b + v, int(u in pair))
    for u, neighbors in rows.items():
        require(0 <= u < h, 'row_bounds')
        require(len(neighbors) == len(set(neighbors)), 'duplicate_neighbor')
        require(all(isinstance(v, int) and 0 <= v < h for v in neighbors), 'neighbor_bounds')
        require(u not in neighbors, 'loop')
        require(len(neighbors) == b - 2, 'H_degree')
        for v in range(h):
            set_edge(1 + b + u, 1 + b + v, int(v in neighbors))
    matching = [tuple(p) for p in data['matching']]
    require(all(len(p) == 2 and p[0] < p[1] for p in matching), 'matching_format')
    special = [v for v in rows[0] if set(labels[v]) & set(labels[0])]
    residual = set(rows[0]) - set(special)
    require(len(special) == 2, 'root_border_paired')
    endpoints = [v for p in matching for v in p]
    require(len(endpoints) == len(set(endpoints)) and set(endpoints) == residual, 'matching_coverage')
    for p in matching:
        require(not set(labels[p[0]]) & set(labels[p[1]]), 'matching_label_overlap')
    mset = set(matching)
    for u, v in itertools.combinations(sorted(rows[0]), 2):
        set_edge(1 + b + u, 1 + b + v, int((u, v) in mset))
    for u, v, bit in data.get('assignments', []):
        require(0 <= u < v < h and bit in (0, 1), 'assignment_format')
        set_edge(1 + b + u, 1 + b + v, bit)
    full = set(range(1 + b)) | {1 + b + u for u in rows}
    return a, full, b


def equations_and_checks(data):
    a, full, degree = construct(data)
    n = len(a)
    for u in range(n):
        low = a[u].count(1)
        high = low + a[u].count(None)
        require(low <= degree <= high, 'degree_capacity')
        if u in full:
            require(None not in a[u] and low == degree, 'full_degree')
    pair_count = 0
    full_pairs = 0
    for u, v in itertools.combinations(range(n), 2):
        lower = sum(a[u][w] == 1 and a[v][w] == 1 for w in range(n))
        upper = sum(a[u][w] != 0 and a[v][w] != 0 for w in range(n))
        target = 1 if a[u][v] == 1 else 2
        if a[u][v] is None:
            require(lower <= 2 and upper >= 1, 'unknown_pair_capacity')
        else:
            require(lower <= target <= upper, 'pair_capacity')
        if u in full and v in full:
            require(lower == upper == target, 'full_pair')
            full_pairs += 1
        pair_count += 1
    equations = []
    for u in sorted(full):
        neighbors = [v for v in range(n) if a[u][v] == 1]
        for v in neighbors:
            fixed = sum(a[v][w] == 1 for w in neighbors)
            unknown = [tuple(sorted((v, w))) for w in neighbors if a[v][w] is None]
            require(fixed <= 1 <= fixed + len(unknown), 'star_capacity')
            equations.append((unknown, 1 - fixed))
    return a, equations, {'vertices': n, 'full_vertices': len(full),
                         'full_pairs': full_pairs, 'pair_capacity_checks': pair_count,
                         'star_equations': len(equations)}


def verify_witness(equations, witness):
    values = {tuple(p[:2]): p[2] for p in witness}
    require(len(values) == len(witness), 'duplicate_witness_edge')
    needed = {p for terms, _ in equations for p in terms}
    require(set(values) == needed, 'witness_edge_coverage')
    require(all(bit in (0, 1) for bit in values.values()), 'witness_bit')
    for terms, target in equations:
        require(sum(values[p] for p in terms) == target, 'witness_star_equation')
    return True


def check(data):
    _, equations, counts = equations_and_checks(data)
    edges = sorted({p for terms, _ in equations for p in terms})
    pool = IDPool(start_from=1)
    variables = {p: pool.id(p) for p in edges}
    clauses = []
    for terms, target in equations:
        literals = [variables[p] for p in terms]
        if not literals:
            require(target == 0, 'fixed_star')
        elif target == 0:
            clauses.extend([[-v] for v in literals])
        else:
            clauses.extend(CardEnc.equals(lits=literals, bound=target, vpool=pool,
                                          encoding=EncType.seqcounter).clauses)
    with Glucose4(bootstrap_with=clauses) as solver:
        sat = solver.solve()
        if not sat:
            return {'status': 'STAR_UNSAT_UNCERTIFIED', 'counts': counts}
        positive = {v for v in (solver.get_model() or []) if v > 0}
    witness = [[u, v, int(variables[(u, v)] in positive)] for u, v in edges]
    verify_witness(equations, witness)
    return {'status': 'PASS_NECESSARY_PREFIX_AND_JOINT_STARS', 'counts': counts,
            'witness': witness, 'solver': 'Glucose4',
            'witness_direct_integer_check': True, 'SRG_completion_claim': False}
