"""Exact linear relaxation and row projection; no heuristic rejection."""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import threading
import time
from pathlib import Path

import pynauty
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Glucose4


class Geometry:
    def __init__(self, m=7):
        self.m = m
        self.b = 2 * m
        self.labels = tuple((a, b) for a, b in itertools.combinations(range(self.b), 2)
                            if b - a != m)
        self.n = len(self.labels)
        self.index = {p: i for i, p in enumerate(self.labels)}
        self.degree = 2 * m - 2
        self.sets = tuple(map(frozenset, self.labels))
        self.inc = [[i for i, p in enumerate(self.labels) if a in p] for a in range(self.b)]

    def margins(self, u):
        a, b = self.labels[u]
        special = {a, b, (a + self.m) % self.b, (b + self.m) % self.b}
        return [1 if x in special else 2 for x in range(self.b)]

    def verify(self, rows):
        for u, r in rows.items():
            if not 0 <= u < self.n or r < 0 or r >> self.n or (r >> u) & 1:
                raise ValueError('row identity, bounds or diagonal')
            if r.bit_count() != self.degree:
                raise ValueError('row degree')
            counts = [sum((r >> j) & 1 for j in self.inc[a]) for a in range(self.b)]
            if counts != self.margins(u):
                raise ValueError('border margins')
            for v, s in rows.items():
                if v >= u:
                    continue
                e = (r >> v) & 1
                if e != ((s >> u) & 1):
                    raise ValueError('symmetry')
                if (r & s).bit_count() != 2 - e - len(self.sets[u] & self.sets[v]):
                    raise ValueError('common neighbors')

    def graph(self, rows):
        adj = {i: set() for i in range(self.b + self.n)}
        def edge(a, b):
            adj[a].add(b)
            adj[b].add(a)
        for a in range(self.m):
            edge(a, a + self.m)
        for u, pair in enumerate(self.labels):
            for a in pair:
                edge(a, self.b + u)
        for u, r in rows.items():
            for v in range(self.n):
                if (r >> v) & 1:
                    edge(self.b + u, self.b + v)
        colors = [set(range(self.b)), {self.b},
                  {self.b + u for u in rows if u != 0},
                  {self.b + u for u in range(self.n) if u not in rows}]
        return pynauty.Graph(self.b + self.n, adjacency_dict={u: list(v) for u, v in adj.items()},
                            vertex_coloring=[c for c in colors if c])

    def key(self, rows):
        return pynauty.certificate(self.graph(rows))

    def targets(self, rows, arm, rng, count=4):
        open_rows = sorted(set(range(self.n)) - rows.keys())
        if arm == 'ordered':
            return open_rows[:1]
        orbits = pynauty.autgrp(self.graph(rows))[3]
        representatives = {}
        for u in open_rows:
            representatives.setdefault(orbits[self.b + u], u)
        choices = list(representatives.values())
        rng.shuffle(choices)
        return choices[:count]


def encode(g, rows, target=None):
    """With target: its margins and pair equations, plus all completed stars.

    With target=None: all open margins and every pair touching a built row.
    Both are necessary relaxations. SAT is not an SRG witness. The full rows
    are always checked independently before encoding; all 84 built gives SRG.
    """
    g.verify(rows)
    pool = IDPool()
    cnf = CNF()
    variables = {}
    def edge(u, v):
        if u == v:
            return (False, 0)
        if u in rows:
            return (False, (rows[u] >> v) & 1)
        if v in rows:
            return (False, (rows[v] >> u) & 1)
        key = tuple(sorted((u, v)))
        if key not in variables:
            variables[key] = pool.id(key)
        return (True, variables[key])
    def exactly(terms, target):
        lits = [v for var, v in terms if var]
        residual = target - sum(v for var, v in terms if not var)
        if residual < 0 or residual > len(lits):
            cnf.append([])
        elif not lits:
            return
        elif residual == 0:
            cnf.extend([[-v] for v in lits])
        elif residual == len(lits):
            cnf.extend([[v] for v in lits])
        else:
            cnf.extend(CardEnc.equals(lits=lits, bound=residual, vpool=pool,
                                     encoding=EncType.seqcounter).clauses)
    for v in range(g.n):
        if v in rows or (target is not None and v != target):
            continue
        for a, margin in enumerate(g.margins(v)):
            exactly([edge(v, w) for w in g.inc[a]], margin)
    for u, row in rows.items():
        neighbors = [w for w in range(g.n) if (row >> w) & 1]
        for v in range(g.n):
            if v in rows:
                continue
            if target is not None and v != target and not ((row >> v) & 1):
                continue
            common = 2 - ((row >> v) & 1) - len(g.sets[u] & g.sets[v])
            exactly([edge(v, w) for w in neighbors], common)
    cnf.nv = max(cnf.nv, pool.top)
    return cnf, variables


def projection(g, rows, target, variables):
    fixed = sum(1 << u for u, r in rows.items() if (r >> target) & 1)
    free = [(v, variables[tuple(sorted((v, target)))])
            for v in range(g.n) if v not in rows and v != target]
    return fixed, free


class Deadline:
    """Glucose interruption also works while native solve holds the main thread."""
    def __init__(self, solver, cpu_end, wall_end):
        self.solver = solver
        self.cpu_end = cpu_end
        self.wall_end = wall_end
        self.done = threading.Event()
        self.expired = False
        self.thread = threading.Thread(target=self.watch, daemon=True)

    def watch(self):
        while not self.done.wait(0.025):
            if time.process_time() >= self.cpu_end or time.monotonic() >= self.wall_end:
                self.expired = True
                self.solver.interrupt()
                return

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.done.set()
        self.thread.join()


def enumerate_projection(g, rows, target, cnf, variables, cpu_s, wall_s, cap,
                         reservoir_size, seed, artifact=None):
    start_cpu = time.process_time()
    start_wall = time.monotonic()
    fixed, free = projection(g, rows, target, variables)
    rng = random.Random(seed)
    sample = []
    count = 0
    status = 'LIMIT_UNRESOLVED'
    digest = hashlib.sha256()
    output = None
    if artifact:
        artifact = Path(artifact)
        artifact.mkdir(parents=True, exist_ok=False)
        atomic(artifact / 'state.json', {'m': g.m, 'rows': pack(rows), 'target': target, 'encoding': 'row_and_stars'})
        output = (artifact / 'rows.txt').open('w')
    try:
        with Glucose4(bootstrap_with=cnf.clauses) as solver:
            with Deadline(solver, start_cpu + cpu_s, start_wall + wall_s) as deadline:
                while count < cap and not deadline.expired:
                    if time.process_time() >= start_cpu + cpu_s:
                        break
                    result = solver.solve_limited(expect_interrupt=True)
                    if result is None:
                        break
                    if result is False:
                        status = 'PROJECTED_ENUMERATION_COMPLETE'
                        break
                    positive = {v for v in solver.get_model() if v > 0}
                    row = fixed | sum(1 << v for v, literal in free if literal in positive)
                    child = dict(rows)
                    child[target] = row
                    g.verify(child)
                    raw = (hex(row) + '\n').encode()
                    digest.update(raw)
                    if output:
                        output.write(raw.decode())
                        output.flush()
                    count += 1
                    if len(sample) < reservoir_size:
                        sample.append(row)
                    else:
                        j = rng.randrange(count)
                        if j < reservoir_size:
                            sample[j] = row
                    block = [-lit if lit in positive else lit for _, lit in free]
                    solver.add_clause(block)
                stats = solver.accum_stats()
        meta = {'target': target, 'depth': len(rows), 'count': count, 'status': status,
                'width_kind': 'EXACT_PROJECTED_RELAXATION' if status.endswith('COMPLETE') else 'LOWER_BOUND',
                'sample_uniform_over_full_projection': status.endswith('COMPLETE'),
                'sample_count': len(sample), 'rows_sha256': digest.hexdigest(),
                'cpu_s': time.process_time() - start_cpu, 'wall_s': time.monotonic() - start_wall,
                'sat_stats': stats, 'variables': cnf.nv, 'clauses': len(cnf.clauses),
                'artifact': str(artifact) if artifact else None, 'certified': False}
        if artifact:
            atomic(artifact / 'enumeration.json', meta)
        return sample, meta
    finally:
        if output:
            output.close()


def pack(rows):
    return [[u, hex(r)] for u, r in sorted(rows.items())]


def unpack(rows):
    return {int(u): int(r, 16) for u, r in rows}


def atomic(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.flush()
    tmp.replace(path)


def load_roots(path):
    g = Geometry()
    out = []
    for line in Path(path).read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        fields = line.split('\t')
        labels = [tuple(map(int, word.split('-'))) for word in fields[3:]]
        if len(labels) != 12 or len(set(labels)) != 12:
            raise ValueError('duplicate or incomplete root')
        row = sum(1 << g.index[p] for p in labels)
        g.verify({0: row})
        out.append({'id': int(fields[0]), 'stabilizer': int(fields[1]),
                    'orbit': int(fields[2]), 'row': hex(row)})
    if len(out) != 8105 or len({r['id'] for r in out}) != 8105:
        raise ValueError('root list size')
    if sum(r['orbit'] for r in out) != 56011010:
        raise ValueError('root coverage sum')
    return out
