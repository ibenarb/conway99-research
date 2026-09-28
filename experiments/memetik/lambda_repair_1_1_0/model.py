"""CP-SAT joint repair. All pair residuals, global hard degree and lambda."""
from ortools.sat.python import cp_model


def build(rows, vertices, hint_rows=None, degree=14, lam=1, target=2, guard=None):
    n = len(rows)
    inside = set(vertices)
    hint_rows = hint_rows if hint_rows is not None else rows
    m = cp_model.CpModel()
    edges = {}
    hints = {}

    def new_bool(name, value):
        var = m.new_bool_var(name)
        hints[var.index] = int(value)
        m.add_hint(var, int(value))
        return var

    def new_int(lo, hi, name, value):
        var = m.new_int_var(lo, hi, name)
        hints[var.index] = int(value)
        m.add_hint(var, int(value))
        return var

    for v in range(n):
        for u in range(v):
            if guard is not None:
                guard()
            if u in inside and v in inside:
                edges[u, v] = new_bool(f'e_{u}_{v}', v in hint_rows[u])
            else:
                edges[u, v] = int(v in rows[u])

    def edge(u, v):
        return 0 if u == v else edges[min(u, v), max(u, v)]

    for u in range(n):
        m.add(sum(edge(u, v) for v in range(n)) == degree)
    bads, absolute = [], []
    multiplier = 50000 if (n, degree, lam, target) == (99, 14, 1, 2) else n * (n - 1) // 2 * (degree + target + 1) + 1
    for v in range(n):
        for u in range(v):
            if guard is not None:
                guard()
            terms = []
            hint_common = len(hint_rows[u] & hint_rows[v])
            for k in range(n):
                a, b = edge(u, k), edge(v, k)
                if isinstance(a, int):
                    if a:
                        terms.append(b)
                elif isinstance(b, int):
                    if b:
                        terms.append(a)
                else:
                    product = new_bool(f'p_{u}_{v}_{k}', hints[a.index] * hints[b.index])
                    m.add(product <= a)
                    m.add(product <= b)
                    m.add(product >= a + b - 1)
                    terms.append(product)
            e = edge(u, v)
            if all(isinstance(t, int) for t in terms) and isinstance(e, int):
                cn = sum(terms)
                if e and cn != lam:
                    raise ValueError('Frozen lambda violation')
                residue = cn + e - target
                bads.append(int(residue != 0))
                absolute.append(abs(residue))
                continue
            common = new_int(0, degree, f'c_{u}_{v}', hint_common)
            m.add(common == sum(terms))
            if isinstance(e, int):
                if e:
                    m.add(common == lam)
            else:
                m.add(common == lam).only_enforce_if(e)
            hint_residue = hint_common + int(v in hint_rows[u]) - target
            residue = new_int(-target, degree + 1, f'r_{u}_{v}', hint_residue)
            m.add(residue == common + e - target)
            bad = new_bool(f'b_{u}_{v}', hint_residue != 0)
            m.add(residue != 0).only_enforce_if(bad)
            m.add(residue == 0).only_enforce_if(bad.negated())
            magnitude = new_int(0, degree + target, f'a_{u}_{v}', abs(hint_residue))
            m.add_abs_equality(magnitude, residue)
            bads.append(bad)
            absolute.append(magnitude)
    objective = multiplier * sum(bads) + sum(absolute)
    m.minimize(objective)
    for index, var in enumerate(m.proto.variables):
        if index not in hints:
            assert len(var.domain) == 2 and var.domain[0] == var.domain[1]
            hints[index] = var.domain[0]
            m.add_hint(m.get_int_var_from_proto_index(index), var.domain[0])
    error = m.validate()
    if error:
        raise RuntimeError(error)
    return m, edges, objective, multiplier, hints


def extract(rows, edges, value):
    result = [set(row) for row in rows]
    for (u, v), variable in edges.items():
        present = variable if isinstance(variable, int) else value(variable)
        if present:
            result[u].add(v)
            result[v].add(u)
        else:
            result[u].discard(v)
            result[v].discard(u)
    return result
