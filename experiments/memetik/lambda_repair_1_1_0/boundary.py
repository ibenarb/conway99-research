"""Set-based necessary-condition propagation with a replayable assignment trace."""

def propagate(rows, vertices):
    inside = set(vertices)
    outside = set(range(len(rows))) - inside
    pairs = [(u, v) for v in sorted(inside) for u in sorted(inside) if u < v]
    values, trace, constraints = {}, [], []
    for u, v in pairs:
        if len(rows[u] & rows[v] & outside) > 1:
            values[u, v] = 0
            trace.append({'pair': [u, v], 'value': 0, 'reason': 'two_common_outside'})
    for u in sorted(inside):
        constraints.append(([(min(u, v), max(u, v)) for v in sorted(inside) if v != u],
                            len(rows[u] & inside), f'degree:{u}'))
        for o in sorted(rows[u] & outside):
            constraints.append(([(min(u, v), max(u, v)) for v in sorted(rows[o] & inside) if v != u],
                                1 - len(rows[u] & rows[o] & outside), f'boundary_lambda:{u}:{o}'))
    changed = True
    while changed:
        changed = False
        for variables, total, reason in constraints:
            missing = [p for p in variables if p not in values]
            remaining = total - sum(values.get(p, 0) for p in variables)
            if not 0 <= remaining <= len(missing):
                raise ValueError('Necessary conditions exclude the known start')
            if missing and remaining in (0, len(missing)):
                value = int(remaining != 0)
                for pair in missing:
                    values[pair] = value
                    trace.append({'pair': list(pair), 'value': value, 'reason': reason})
                changed = True
    assert all(value == int(v in rows[u]) for (u, v), value in values.items())
    return {'rigid': len(values) == len(pairs), 'unfixed': len(pairs) - len(values), 'trace': trace}
