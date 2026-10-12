"""Anchor-profile formulas for the C2 model (Conway99, involution with one fixed point).

Place next to the TwoAnchor package sources (c2_reference.py, model.py). Standard library only.

  python3 anchor_profile.py check [--solver PATH]
      Frame-group checks (transport of doubled-edge literals, invariance of E1/E2/E3
      specifications, transitivity, group order) and, with --solver, k=4 controls.
  python3 anchor_profile.py build --base base.cnf --out X.cnf --anchors 0,2,4,6
      Base + "type 1^6 at every listed anchor" (units).  All 7 classes = U6.
  python3 anchor_profile.py build --base base.cnf --out X.cnf --bidirected 0,1,2,3
      Base + all 12 arcs among the listed mate pairs (arc p->q = doubled edge at anchor
      class p towards pair q).  Refuting every 4-set gives: no bidirected K4.
      Add --omit 0-1 for "K4 minus arc 0->1" (11 units); refuting all 35x12 instances
      gives: among any four mate pairs at least two of the twelve arcs are absent.
  python3 anchor_profile.py build --base base.cnf --out X.cnf --profile 0,6
      Base + "every anchor has d in S" (d = number of doubled edges, S subset of 0..6).

d(a) counts the six edges {a,c}-{a,c^1}; type 1^6 at anchor a <=> d(a)=6.
The base CNF must be the pinned totalizer base (sha 7c105a67...3dd) or the reference
baseline; both share the primary numbering (variables.json sha cd78938c...).
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c2_reference import CNF, Frame, reconstruct, verify_graph  # noqa: E402
from model import augment, header_variables  # noqa: E402


def frame(k=14):
    cnf, f = CNF(), Frame(k)
    f.allocate(cnf)
    cnf.close()
    return f


def label_index(f):
    return {l: i for i, l in enumerate(f.labels)}


def doubled(f, a):
    idx = label_index(f)
    lab = lambda x, y: idx[tuple(sorted((x, y)))]
    return sorted({f.edge(lab(a, c), lab(a, c ^ 1))
                   for c in range(f.k) if c not in (a, a ^ 1) and c < (c ^ 1)})


def arc(f, p, q):
    """Doubled edge at anchor class p (pair index) towards pair q: {2p,2q}-{2p,2q+1}."""
    idx = label_index(f)
    return f.edge(idx[tuple(sorted((2 * p, 2 * q)))], idx[tuple(sorted((2 * p, 2 * q + 1)))])


def arcs(f):
    m = f.k // 2
    return {(p, q): arc(f, p, q) for p in range(m) for q in range(m) if p != q}


def generators(k=14):
    gens = []
    for j in range(1, k // 2):
        g = list(range(k))
        g[0], g[2 * j], g[1], g[2 * j + 1] = 2 * j, 0, 2 * j + 1, 1
        gens.append(('swap0-%d' % j, g))
    g = list(range(k))
    g[0], g[1] = 1, 0
    gens.append(('flip0', g))
    return gens


def varmap(f, g):
    idx, n = label_index(f), len(f.labels)
    image = [idx[tuple(sorted((g[a], g[b])))] for a, b in f.labels]
    pm = {}
    for x in range(n):
        for y in range(n):
            v, w = f.edge(x, y), f.edge(image[x], image[y])
            if v is False:
                if w is not False:
                    raise AssertionError('zero pattern not preserved')
                continue
            if pm.setdefault(v, w) != w:
                raise AssertionError('variable map not well defined')
    count = len(f.map)
    if sorted(pm) != list(range(1, count + 1)) or sorted(pm.values()) != list(range(1, count + 1)):
        raise AssertionError('variable map not a bijection')
    return pm


def specs(f):
    L, n, k = f.labels, len(f.labels), f.k
    out = set()
    for x in range(n):
        out.add(('E1', frozenset(Counter(v for v in (f.edge(x, z) for z in range(n)) if v).items()), k - 2))
        for a in range(k):
            t = Counter(v for v in (f.edge(x, z) for z in range(n) if a in L[z]) if v)
            out.add(('E2', frozenset(t.items()), 2 - int(a in L[x]) - int((a ^ 1) in L[x])))
        for y in range(x + 1, n):
            t = Counter()
            for z in range(n):
                u, w = f.edge(x, z), f.edge(z, y)
                if u and w:
                    t[frozenset((u, w))] += 1
            if f.edge(x, y):
                t[frozenset((f.edge(x, y),))] += 1
            out.add(('E3', frozenset(t.items()), 2 - len(set(L[x]) & set(L[y]))))
    return out


def map_spec(s, pm):
    kind, terms, target = s
    if kind == 'E3':
        terms = frozenset((frozenset(pm[v] for v in term), c) for term, c in terms)
    else:
        terms = frozenset((pm[v], c) for v, c in terms)
    return kind, terms, target


def check(solver=None):
    report = {}
    f = frame(14)
    gens = generators(14)
    S = specs(f)
    for name, g in gens:
        if any(g[a ^ 1] != g[a] ^ 1 for a in range(14)):
            raise AssertionError('generator does not commute with the involution')
        pm = varmap(f, g)
        for b in range(14):
            if sorted(pm[v] for v in doubled(f, b)) != doubled(f, g[b]):
                raise AssertionError('doubled literals not transported: %s %d' % (name, b))
        A = arcs(f)
        for (p, q), v in A.items():
            if pm[v] != A[(g[2 * p] // 2, g[2 * q] // 2)]:
                raise AssertionError('arc not transported: %s %d->%d' % (name, p, q))
        if not all(map_spec(s, pm) in S for s in S):
            raise AssertionError('E1/E2/E3 not invariant under ' + name)
    orbit, todo = {0}, [0]
    while todo:
        a = todo.pop()
        for _, g in gens:
            if g[a] not in orbit:
                orbit.add(g[a]); todo.append(g[a])
    group, todo = {tuple(range(14))}, [tuple(range(14))]
    while todo:
        p = todo.pop()
        for _, g in gens:
            q = tuple(g[p[i]] for i in range(14))
            if q not in group:
                group.add(q); todo.append(q)
    for a in range(0, 14, 2):
        if doubled(f, a) != doubled(f, a ^ 1):
            raise AssertionError('sigma does not identify anchors %d,%d' % (a, a ^ 1))
    A = arcs(f)
    if len(set(A.values())) != 42 or any(sorted(A[(a // 2, c // 2)] for c in range(0, 14, 2) if c // 2 != a // 2) != doubled(f, a) for a in range(14)):
        raise AssertionError('arc literals inconsistent with doubled literals')
    report.update(generators=len(gens), specs=len(S), orbit_of_0=len(orbit), group_order=len(group),
                  anchor0_literals=doubled(f, 0))
    if len(orbit) != 14 or len(group) != 2 ** 7 * 5040:
        raise AssertionError('unexpected group')
    if solver:
        report['k4'] = k4_controls(solver)
    print('ANCHOR_PROFILE_CHECK_PASS ' + json.dumps(report), flush=True)


def k4_controls(solver, work=Path('k4_control')):
    from model import build_base
    work.mkdir(exist_ok=True)
    build_base(work, k=4)
    f = frame(4)
    lits = sorted({v for a in range(4) for v in doubled(f, a)})
    result = {}
    for name, clauses, expect in (('all_d0', [[-v] for v in lits], 20), ('all_d1', [[v] for v in lits], 10)):
        target = work / (name + '.cnf')
        augment(work / 'base.cnf', target, header_variables(work / 'base.cnf'), clauses)
        run = subprocess.run([solver, '-q', str(target)], capture_output=True, text=True)
        if run.returncode != expect:
            raise AssertionError('k=4 control failed: ' + name)
        if expect == 10:
            values = {}
            for line in run.stdout.splitlines():
                if line.startswith('v '):
                    for t in map(int, line[2:].split()):
                        if t and abs(t) <= len(f.map):
                            values[abs(t)] = t > 0
            if not verify_graph(reconstruct(f, values), 4):
                raise AssertionError('k=4 SAT model fails graph check')
        result[name] = 'SAT_GRAPH_VERIFIED' if expect == 10 else 'UNSAT'
    return result


def profile_clauses(lits, allowed):
    """Forbid d = v for every v not in allowed, directly on the six literals (no auxiliaries)."""
    clauses = []
    for v in range(len(lits) + 1):
        if v in allowed:
            continue
        for true_set in itertools.combinations(lits, v):
            clauses.append([-x for x in true_set] + [x for x in lits if x not in true_set])
    return clauses


def build(base, out, anchors=None, profile=None, bidirected=None, omit_arcs=None):
    f = frame(14)
    if bidirected is not None:
        A = arcs(f)
        omit = set(omit_arcs or [])
        clauses = [[A[(p, q)]] for p in bidirected for q in bidirected if p != q and (p, q) not in omit]
        kind = {'bidirected_pairs': bidirected, 'omitted_arcs': sorted(omit)}
    elif anchors is not None:
        clauses = [[v] for v in sorted({v for a in anchors for v in doubled(f, a)})]
        kind = {'anchors': anchors}
    else:
        clauses = []
        for a in range(0, 14, 2):
            clauses += profile_clauses(doubled(f, a), set(profile))
        kind = {'profile': sorted(profile)}
    sha = augment(base, out, header_variables(base), clauses)
    meta = {**kind, 'base': str(base), 'out': str(out), 'added_clauses': len(clauses), 'sha256': sha,
            'base_sha256': hashlib.sha256(Path(base).read_bytes()).hexdigest()}
    Path(str(out) + '.json').write_text(json.dumps(meta, sort_keys=True, indent=1) + '\n')
    print('ANCHOR_PROFILE_BUILT ' + json.dumps(meta), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('check')
    c.add_argument('--solver')
    b = sub.add_parser('build')
    b.add_argument('--base', type=Path, required=True)
    b.add_argument('--out', type=Path, required=True)
    g = b.add_mutually_exclusive_group(required=True)
    g.add_argument('--anchors')
    g.add_argument('--profile')
    g.add_argument('--bidirected', help='pair indices 0..6, e.g. 0,1,2,3 = bidirected K4 on these mate pairs')
    b.add_argument('--omit', help='with --bidirected: arcs to leave out, e.g. 0-1 or 0-1,2-3')
    a = p.parse_args()
    if a.cmd == 'check':
        check(a.solver)
    else:
        if a.out.exists():
            p.error('output exists')
        anchors = [int(x) for x in a.anchors.split(',')] if a.anchors else None
        profile = [int(x) for x in a.profile.split(',')] if a.profile else None
        if anchors and any(x not in range(14) for x in anchors):
            p.error('anchors must be frame labels 0..13')
        if profile and any(x not in range(7) for x in profile):
            p.error('profile values must be 0..6')
        bidir = [int(x) for x in a.bidirected.split(',')] if a.bidirected else None
        if bidir and (any(x not in range(7) for x in bidir) or len(set(bidir)) != len(bidir)):
            p.error('bidirected: distinct pair indices 0..6')
        omit = [tuple(int(y) for y in x.split('-')) for x in a.omit.split(',')] if a.omit else None
        if omit and (not bidir or any(len(x) != 2 or x[0] not in bidir or x[1] not in bidir or x[0] == x[1] for x in omit)):
            p.error('--omit needs --bidirected and arcs p-q between listed pairs')
        build(a.base, a.out, anchors, profile, bidir, omit)


if __name__ == '__main__':
    main()
