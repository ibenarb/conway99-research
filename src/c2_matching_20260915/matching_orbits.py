"""Exhaustive matching cover and explicit frame transporters, not a C2 exclusion."""
from collections import Counter
from itertools import combinations
from math import factorial
from c2_reference import CNF, Frame, reconstruct


def matchings(vertices):
    if not vertices:
        yield ()
        return
    a = vertices[0]
    for b in vertices[1:]:
        rest = tuple(x for x in vertices if x not in (a, b))
        for matching in matchings(rest):
            yield ((a, b),) + matching


def normalized(edges):
    return tuple(sorted(tuple(sorted(e)) for e in edges))


def canonical_matching(parts):
    edges, offset = [], 0
    for length in parts:
        for i in range(length):
            edges.append((offset+2*i+1, offset+2*((i+1) % length)))
        offset += 2*length
    return normalized(edges)


def transport(matching, n=6):
    mate = {}
    for a, b in matching:
        mate[a], mate[b] = b, a
    if set(mate) != set(range(2*n)) or any(a == b for a, b in matching):
        raise ValueError('Not a perfect matching')
    unseen, components = set(mate), []
    while unseen:
        start = min(unseen)
        walk, a = [], start
        while True:
            walk.extend((a, a ^ 1))
            unseen.remove(a)
            unseen.remove(a ^ 1)
            a = mate[a ^ 1]
            if a == start:
                break
        components.append(tuple(walk))
    components.sort(key=lambda row: (len(row), row))
    parts = tuple(len(row)//2 for row in components)
    permutation = [None]*(2*n)
    offset = 0
    for row in components:
        for i, old in enumerate(row):
            permutation[old] = offset+i
        offset += len(row)
    image = normalized((permutation[a], permutation[b]) for a, b in matching)
    if image != canonical_matching(parts):
        raise AssertionError('Transport does not map to representative')
    if sorted(permutation) != list(range(2*n)) or any(permutation[a ^ 1] != (permutation[a] ^ 1) for a in range(2*n)):
        raise AssertionError('Transport does not preserve the fixed pairing')
    return parts, tuple(permutation)


def generators():
    for a in range(2, 14, 2):
        p = list(range(14))
        p[a], p[a+1] = p[a+1], p[a]
        yield p
    for a in range(2, 12, 2):
        p = list(range(14))
        p[a:a+4] = [a+2, a+3, a, a+1]
        yield p


def frame_action(frame, p):
    lookup = {label: i for i, label in enumerate(frame.labels)}
    action = [lookup[tuple(sorted(p[a] for a in label))] for label in frame.labels]
    varmap = {}
    for x, y in combinations(range(len(frame.labels)), 2):
        old, new = frame.edge(x, y), frame.edge(action[x], action[y])
        if old is False:
            if new is not False:
                raise AssertionError('Forbidden partner edge changed')
        else:
            if new is False or varmap.setdefault(old, new) != new:
                raise AssertionError('Primary orbit action inconsistent')
    if set(varmap) != set(range(1, len(frame.map)+1)) or set(varmap.values()) != set(varmap):
        raise AssertionError('Primary map is not a permutation')
    for x, label in enumerate(frame.labels):
        for a in range(frame.k):
            if (a in label) != (p[a] in frame.labels[action[x]]):
                raise AssertionError('Frame incidence changed')
    return varmap


def check_cover():
    counts = Counter()
    for matching in matchings(tuple(range(12))):
        parts, permutation = transport(matching)
        counts[parts] += 1
    if sum(counts.values()) != 10395 or len(counts) != 11:
        raise AssertionError('Unexpected matching cover')
    rows = []
    for parts, count in sorted(counts.items()):
        denominator = 1
        for length in parts:
            denominator *= length
        for multiplicity in Counter(parts).values():
            denominator *= factorial(multiplicity)
        predicted = 2**(6-len(parts))*factorial(6)//denominator
        if count != predicted:
            raise AssertionError('Independent orbit-size formula disagrees')
        rows.append({'type': list(parts), 'labelled_count': count,
                     'matching': [list(e) for e in canonical_matching(parts)]})
    cnf, frame = CNF(), Frame(14)
    frame.allocate(cnf)
    try:
        values = {v: (v*1103515245+12345) % 17 < 8 for v in range(1, len(frame.map)+1)}
        graph = reconstruct(frame, values)
        lookup = {label: i for i, label in enumerate(frame.labels)}
        for p in generators():
            assert p[:2] == [0, 1] and all(p[a ^ 1] == (p[a] ^ 1) for a in range(14))
            varmap = frame_action(frame, p)
            image = reconstruct(frame, {varmap[v]: bit for v, bit in values.items()})
            outer = [lookup[tuple(sorted(p[a] for a in label))] for label in frame.labels]
            nodes = [0]+[1+a for a in p]+[15+x for x in outer]
            if any(graph[i][j] != image[nodes[i]][nodes[j]] for i in range(99) for j in range(99)):
                raise AssertionError('Full graph reconstruction not equivariant')
    finally:
        cnf.close()
    # Independent tiny control: only one matching on the two outer neighbors.
    assert list(matchings((0, 1))) == [((0, 1),)]
    assert transport(((0, 1),), n=1)[0] == (1,)
    return {'status': 'MATCHING_ORBIT_COVER_PASS', 'labelled_matchings': 10395,
            'orbit_count': 11, 'transports_checked': 10395, 'frame_generators_checked': 11,
            'stabilizer_order': 2**6*factorial(6), 'orbits': rows,
            'scope': 'Full local matching cover up to proved frame relabeling. No C2 UNSAT claim.'}


if __name__ == '__main__':
    import json
    print(json.dumps(check_cover(), indent=2))
