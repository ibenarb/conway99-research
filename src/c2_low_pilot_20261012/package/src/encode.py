"""Pinned F0 extensions and necessary 720-bit interface model."""
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'legacy'))
from c2_reference import CNF, Frame, negate
from counter import CounterCNF
from model import threshold_counter, augment, header_variables


def frame(k=14):
    c = CNF()
    f = Frame(k)
    f.allocate(c)
    c.close()
    return f


def indexed_edge(f, first, second):
    positions = {tuple(label): i for i, label in enumerate(f.labels)}
    return f.edge(positions[tuple(sorted(first))], positions[tuple(sorted(second))])


def units(f, row):
    n = f.k - 2
    output = []
    for i, j in itertools.combinations(range(n), 2):
        b = indexed_edge(f, (0, i + 2), (0, j + 2))
        c = indexed_edge(f, (0, i + 2), (1, (j + 2) ^ 1))
        assert b is not False and c is not False
        output.extend([b if row['L'][i] == j else -b, c if row['N'][i] == j else -c])
    assert len({abs(v) for v in output}) == n * (n - 1)
    return output


def arc_variables(f):
    pairs = f.k // 2
    return {(p, q): indexed_edge(f, (2 * p, 2 * q), (2 * p, 2 * q + 1))
            for p in range(pairs) for q in range(pairs) if p != q}


def rule(c, f, row, mode):
    arcs = arc_variables(f)
    count = f.k // 2
    for q in range(1, count):
        out = [arcs[q, p] for p in range(count) if p != q]
        if mode == 'MIN':
            d = row['d_plus']
            if d:
                c.clause(threshold_counter(c, out)[d - 1])
        elif mode == 'R':
            # For k=4 the high branch d+>=3 is empty. The control still
            # tests a genuine maximum-D choice among all available LOW anchors.
            high = threshold_counter(c, out)[2] if len(out) >= 3 else False
            all_arcs = out + [arcs[p, q] for p in range(count) if p != q]
            d = row['d_plus'] + row['d_minus']
            if d < len(all_arcs):
                c.clause(high, negate(threshold_counter(c, all_arcs)[d]))
        else:
            raise ValueError(mode)


def full(base, row, mode, target, k=14):
    f = frame(k)
    c = CNF(retain=True)
    c.variables = header_variables(base)
    try:
        for lit in units(f, row):
            c.clause(lit)
        rule(c, f, row, mode)
        digest = augment(base, target, c.variables, c.saved)
        return {'kind': 'FULL', 'mode': mode, 'variables': c.variables,
                'added_clauses': c.clauses, 'sha256': digest, 'units': units(f, row)}
    finally:
        c.close()


def interface(row, target):
    n = len(row['L'])
    l, m = row['L'], row['N']
    labels = [(i, j) for i, j in itertools.combinations(range(n), 2) if j != (i ^ 1)]
    index = {z: i for i, z in enumerate(labels)}
    tau = [index[tuple(sorted((i ^ 1, j ^ 1)))] for i, j in labels]
    c = CounterCNF()
    x = [[c.variable() for z in labels] for i in range(n)]
    try:
        for i in range(n):
            c.exact(x[i], n - 2)
        for z in range(len(labels)):
            c.exact([x[i][z] for i in range(n)], 2)
        c.small = True
        for i, j in itertools.combinations(range(n), 2):
            c.exact([c.conjunction(x[i][z], x[j][z]) for z in range(len(labels))], 1 - int(l[i] == j))
        for i in range(n):
            for j in range(i, n):
                target_sum = 2 - int(j == (i ^ 1)) - int(m[i] == j) - int(l[m[i]] == j) - int(m[l[i]] == j)
                c.exact([c.conjunction(x[i][z], x[j][tau[z]]) for z in range(len(labels))], target_sum)
            for a in range(n):
                demand = 2 - int(a == i) - int(a == (i ^ 1)) - int(a == l[i]) - int(a == (m[i] ^ 1))
                c.exact([x[i][z] for z, label in enumerate(labels) if a in label], demand)
            for z, label in enumerate(labels):
                if i in label or (i ^ 1) in label:
                    c.clause(-x[i][z], -x[i ^ 1][tau[z]])
        result = c.write(target)
        return {**result, 'kind': 'X', 'mode': 'X', 'labels': labels, 'tau': tau,
                'primary_variables': x, 'scope': 'Necessary interface only; SAT is not a graph.'}
    finally:
        c.close()


def model_values(path):
    values = {}
    for line in Path(path).read_text(errors='replace').splitlines():
        if line.startswith('v '):
            for token in line.split()[1:]:
                lit = int(token)
                if lit:
                    assert abs(lit) not in values or values[abs(lit)] == (lit > 0)
                    values[abs(lit)] = lit > 0
    return values


def verify_full(values, row, mode, k=14):
    # Build adjacency from labels and the B/C map; direct integer common-neighbor
    # counts, independent of SAT auxiliaries and cardinality encoders.
    f = frame(k)
    assert all(v in values for v, *_ in f.map)
    size = 1 + k + len(f.labels)
    a = [set() for _ in range(size)]
    def edge(i, j):
        a[i].add(j)
        a[j].add(i)
    for i in range(k):
        edge(0, i + 1)
        edge(i + 1, (i ^ 1) + 1)
    for i, label in enumerate(f.labels):
        for anchor in label:
            edge(1 + k + i, 1 + anchor)
        for j in range(i + 1, len(f.labels)):
            v = f.edge(i, j)
            if v is not False and values[v]:
                edge(1 + k + i, 1 + k + j)
    assert all(len(s) == k for s in a)
    for i, j in itertools.combinations(range(size), 2):
        assert len(a[i] & a[j]) == (1 if j in a[i] else 2)
    assert all(values[abs(u)] == (u > 0) for u in units(f, row))
    arcs = arc_variables(f)
    ds = [sum(values[v] for (p, q), v in arcs.items() if p == i) for i in range(k // 2)]
    ins = [sum(values[v] for (p, q), v in arcs.items() if q == i) for i in range(k // 2)]
    if mode == 'MIN':
        assert all(d >= ds[0] for d in ds)
    else:
        assert all(d >= 3 or d + e <= ds[0] + ins[0] for d, e in zip(ds, ins))
    return {'status': 'GRAPH_VERIFIED', 'vertices': size}


def verify_x(values, row, metadata):
    labels = metadata['labels']
    n = len(row['L'])
    assert all(v in values for line in metadata['primary_variables'] for v in line)
    x = [[int(values[v]) for v in line] for line in metadata['primary_variables']]
    neighborhoods = [{i for i in range(n) if x[i][z]} for z in range(len(labels))]
    expected = {tuple(pair) for pair in itertools.combinations(range(n), 2) if row['L'][pair[0]] != pair[1]}
    actual = [tuple(sorted(s)) for s in neighborhoods]
    assert all(len(s) == 2 for s in neighborhoods)
    assert len(set(actual)) == len(actual) and set(actual) == expected
    # Explicit known-neighbor sets in both 12-vertex halves plus Z and anchors.
    for i in range(n):
        assert sum(x[i]) == n - 2
        left = {('A', 0), ('A', 2 + i), ('L', row['L'][i]), ('R', row['N'][i])}
        left |= {('Z', z) for z in range(len(labels)) if x[i][z]}
        for j in range(n):
            right = {('A', 1), ('A', 2 + (j ^ 1)), ('R', row['L'][j]), ('L', row['N'][j])}
            right |= {('Z', z) for z in range(len(labels)) if x[j][metadata['tau'][z]]}
            assert len(left & right) == (1 if row['N'][i] == j else 2)
        for a in range(n):
            known = int(a == (i ^ 1)) + int(a == row['L'][i]) + int(a == (row['N'][i] ^ 1))
            known += sum(x[i][z] for z, label in enumerate(labels) if a in label)
            assert known == (1 if a == i else 2)
        for z, label in enumerate(labels):
            known = x[i][z] + x[i ^ 1][metadata['tau'][z]] + int((i ^ 1) in label)
            assert known <= (1 if i in label else 2)
    return {'status': 'INTERFACE_VERIFIED_ONLY', 'graph_existence': False}
