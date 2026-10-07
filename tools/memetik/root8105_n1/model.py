"""N1: shared symmetric H-edges, all margins, codegrees touching N_H[a]."""
import itertools
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool, Formula


def labels_for(m):
    return [set(p) for p in itertools.combinations(range(2 * m), 2) if p[1] - p[0] != m]


def fixed_edges(m, rows, matching, anchor=0):
    labels = labels_for(m)
    n = len(labels)
    assert anchor in rows
    fixed = {(v, v): 0 for v in range(n)}
    def impose(u, v, bit):
        pair = tuple(sorted((u, v)))
        if pair in fixed and fixed[pair] != bit:
            raise ValueError('inconsistent fixed edge')
        fixed[pair] = bit
    for u, ns in rows.items():
        assert len(ns) == 2 * m - 2 and u not in ns
        assert all(0 <= v < n for v in ns)
        for v in range(n):
            impose(u, v, int(v in ns))
    ns = rows[anchor]
    special = {v for v in ns if labels[v] & labels[anchor]}
    assert len(special) == 2
    pairs = {tuple(sorted(p)) for p in matching}
    endpoints = [v for p in pairs for v in p]
    assert len(endpoints) == len(set(endpoints)) and set(endpoints) == set(ns) - special
    assert all(not labels[u] & labels[v] for u, v in pairs)
    for u, v in itertools.combinations(sorted(ns), 2):
        impose(u, v, int((u, v) in pairs))
    return labels, fixed


def encode(m, rows, matching, anchor=0):
    Formula.attach_vpool(IDPool())
    labels, fixed = fixed_edges(m, rows, matching, anchor)
    n = len(labels)
    pool, cnf = IDPool(), CNF()
    variables = {p: pool.id(('e', *p)) for p in itertools.combinations(range(n), 2) if p not in fixed}
    products = {}
    def edge(u, v):
        pair = tuple(sorted((u, v)))
        return bool(fixed[pair]) if pair in fixed else variables[pair]
    def product(x, y):
        if type(x) is bool:
            return y if x else False
        if type(y) is bool:
            return x if y else False
        if x == y:
            return x
        pair = tuple(sorted((x, y)))
        if pair not in products:
            z = pool.id(('and', *pair))
            products[pair] = z
            cnf.extend([[-z, x], [-z, y], [z, -x, -y]])
        return products[pair]
    def exactly(terms, rhs):
        rhs -= sum(x for x in terms if type(x) is bool)
        literals = [x for x in terms if type(x) is int]
        if rhs < 0 or rhs > len(literals):
            cnf.append([])
        elif literals:
            cnf.extend(CardEnc.equals(lits=literals, bound=rhs, vpool=pool,
                                     encoding=EncType.seqcounter).clauses)
    for u in range(n):
        special = labels[u] | {(c + m) % (2 * m) for c in labels[u]}
        for c in range(2 * m):
            exactly([edge(u, v) for v in range(n) if c in labels[v]], 1 if c in special else 2)
    scope = {anchor} | set(rows[anchor])
    pair_count = 0
    for u, v in itertools.combinations(range(n), 2):
        if u not in scope and v not in scope:
            continue
        pair_count += 1
        exactly([product(edge(u, w), edge(v, w)) for w in range(n)] + [edge(u, v)],
                2 - len(labels[u] & labels[v]))
    cnf.nv = max(cnf.nv, pool.top)
    metadata = {'m': m, 'H_vertices': n, 'scope': sorted(scope), 'fixed_rows': sorted(rows),
                'free_edges': len(variables), 'products': len(products), 'variables': cnf.nv,
                'clauses': len(cnf.clauses), 'pair_equations': pair_count, 'margin_equations': n * 2 * m}
    return cnf, variables, metadata


def check(m, rows, matching, witness, anchor=0):
    """Full matrix check; no CNF, auxiliary variables or encoder helpers."""
    labels = labels_for(m)
    n = len(labels)
    if len(witness) != n or any(len(row) != n for row in witness):
        raise ValueError('matrix shape')
    if any(type(bit) is not int or bit not in (0, 1) for row in witness for bit in row):
        raise ValueError('matrix bit')
    for u in range(n):
        assert witness[u][u] == 0
        assert all(witness[u][v] == witness[v][u] for v in range(n))
        if u in rows:
            assert {v for v in range(n) if witness[u][v]} == set(rows[u])
        assert sum(witness[u]) == 2 * m - 2
        special = labels[u] | {(c + m) % (2 * m) for c in labels[u]}
        for c in range(2 * m):
            assert sum(witness[u][v] for v in range(n) if c in labels[v]) == (1 if c in special else 2)
    ns = set(rows[anchor])
    residual = {v for v in ns if not labels[v] & labels[anchor]}
    endpoints = [v for p in matching for v in p]
    assert len(endpoints) == len(set(endpoints)) and set(endpoints) == residual
    pairs = {tuple(sorted(p)) for p in matching}
    for u, v in itertools.combinations(sorted(ns), 2):
        assert witness[u][v] == int((u, v) in pairs)
    scope = ns | {anchor}
    count = 0
    for u, v in itertools.combinations(range(n), 2):
        if u in scope or v in scope:
            assert sum(witness[u][w] * witness[v][w] for w in range(n)) == 2 - witness[u][v] - len(labels[u] & labels[v])
            count += 1
    return {'status': 'DIRECT_N1_CHECK_PASS', 'pair_equations': count, 'SRG_claim': False}


def decode(m, rows, matching, variables, model, anchor=0):
    labels, fixed = fixed_edges(m, rows, matching, anchor)
    n = len(labels)
    positive = {lit for lit in model if lit > 0}
    witness = [[0] * n for _ in range(n)]
    for u, v in itertools.combinations(range(n), 2):
        pair = (u, v)
        witness[u][v] = witness[v][u] = fixed[pair] if pair in fixed else int(variables[pair] in positive)
    return witness
