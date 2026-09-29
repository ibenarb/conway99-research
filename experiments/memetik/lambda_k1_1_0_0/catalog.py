"""Self-contained AP reference catalogue plus exact star rematching.

AP enumeration/order derives from lambda_compare_0_2_0/kernel.py.
All adopted graphs receive independent set-based verification.
"""
import json
import random
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import verify
from common import cpu, atomic, read


class BudgetEnd(Exception):
    pass


class Guard:
    def __init__(self, deadline=float('inf'), stop_event=None):
        self.deadline = deadline
        self.stop_event = stop_event

    def check(self):
        if cpu() >= self.deadline or (self.stop_event is not None and self.stop_event.is_set()):
            raise BudgetEnd()


def edge(a, b):
    return min(a, b), max(a, b)


def vertices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def triangles(rows):
    return [(a, b, c) for a, row in enumerate(rows)
            for b in vertices(row & ~((1 << (a + 1)) - 1))
            for c in vertices(row & rows[b] & ~((1 << (b + 1)) - 1))]


def apply_move(rows, move):
    child = list(rows)
    for a, b in move[0]:
        if not ((child[a] >> b) & 1):
            raise ValueError('Removing absent edge')
        child[a] &= ~(1 << b)
        child[b] &= ~(1 << a)
    for a, b in move[1]:
        if a == b or (child[a] >> b) & 1:
            raise ValueError('Adding invalid edge')
        child[a] |= 1 << b
        child[b] |= 1 << a
    return child


def bits(graph6):
    return [sum(1 << v for v in row) for row in verify.decode(graph6)]


def graph6(rows):
    return verify.encode([set(vertices(row)) for row in rows])


FIELDS = ('W', 'L1', 'F', 'Linf', 'Nmax')


def compact(histogram):
    maximum = max((abs(r) for r, n in histogram.items() if n), default=0)
    return {'W': sum(n for r, n in histogram.items() if r),
            'L1': sum(abs(r)*n for r, n in histogram.items()),
            'F': sum(r*r*n for r, n in histogram.items()), 'Linf': maximum,
            'Nmax': sum(n for r, n in histogram.items() if abs(r) == maximum)}


class Scorer:
    def __init__(self, rows):
        self.rows = rows
        self.residuals = {(i,j): (rows[i] & rows[j]).bit_count()+((rows[i] >> j) & 1)-2
                          for i in range(len(rows)) for j in range(i)}
        self.histogram = Counter(self.residuals.values())
        self.scores = compact(self.histogram)

    def evaluate(self, move):
        child = apply_move(self.rows, move)
        touched = {v for edges in move for edge in edges for v in edge}
        histogram = self.histogram.copy()
        for i in touched:
            for j in range(len(child)):
                if i == j or (j in touched and j > i):
                    continue
                pair = (max(i,j), min(i,j))
                histogram[self.residuals[pair]] -= 1
                histogram[(child[i] & child[j]).bit_count()+((child[i] >> j) & 1)-2] += 1
        return child, compact(histogram)


def pivot_candidates(rows):
    by_point = defaultdict(list)
    for triple in triangles(rows):
        for point in triple:
            by_point[point].append(tuple(v for v in triple if v != point))
    for point, pairs in sorted(by_point.items()):
        for (x,y), (u,v) in combinations(pairs,2):
            for a,b in ((x,y),(y,x)):
                yield point, a, b, u, v


def pivots(rows, guard):
    for i, (p,x,y,u,v) in enumerate(pivot_candidates(rows)):
        if i % 64 == 0:
            guard.check()
        if rows[x] & (1 << u) or rows[y] & (1 << v):
            continue
        if (rows[x] & rows[u]).bit_count() == 1 and (rows[y] & rows[v]).bit_count() == 1:
            yield (tuple(sorted((edge(x,y),edge(u,v)))),
                   tuple(sorted((edge(x,u),edge(y,v)))))


def apex_exact(rows, guard):
    """Reviewer M4, exact integer common-neighbor table; final tests independent."""
    ts = triangles(rows)
    cn = [[(a & b).bit_count() for b in rows] for a in rows]
    masks = {t: sum(1 << v for v in t) for t in ts}
    seen = set()
    for count, (left,right) in enumerate(combinations(ts,2)):
        if count % 64 == 0:
            guard.check()
        if masks[left] & masks[right]:
            continue
        for c in left:
            a,b = (v for v in left if v != c)
            for d in right:
                e,f = (v for v in right if v != d)
                if rows[d] & ((1 << a)|(1 << b)) or rows[c] & ((1 << e)|(1 << f)):
                    continue
                cd = (rows[c] >> d) & 1
                ae,af = (rows[a] >> e) & 1, (rows[a] >> f) & 1
                be,bf = (rows[b] >> e) & 1, (rows[b] >> f) & 1
                if (cn[a][d],cn[b][d],cn[c][e],cn[c][f]) != (cd+ae+af,cd+be+bf,ae+be+cd,af+bf+cd):
                    continue
                move = (tuple(sorted(edge(u,v) for u,v in ((a,c),(b,c),(d,e),(d,f)))),
                        tuple(sorted(edge(u,v) for u,v in ((a,d),(b,d),(c,e),(c,f)))))
                if move not in seen:
                    seen.add(move)
                    yield move


def star_moves(rows, guard):
    """Every valid replacement of the matching induced on N(p), except identity.

    In a lambda=1 graph N(p) induces a perfect matching. A replacement pair
    must have no common neighbor outside N[p]. These necessary/sufficient
    conditions preserve lambda on every affected edge, including outside edges.
    """
    for p in range(len(rows)):
        guard.check()
        neighbors = tuple(vertices(rows[p]))
        closed = rows[p] | (1 << p)
        old = {edge(x, y) for x in neighbors for y in vertices(rows[x] & rows[p])}
        if len(old) * 2 != len(neighbors):
            raise ValueError('Star input not a lambda=1 neighborhood')
        compatible = {x: tuple(y for y in neighbors if y > x and
                              ((rows[x] & rows[y]) & ~closed) == 0)
                      for x in neighbors}

        def match(left, pairs):
            guard.check()
            if not left:
                new = set(pairs)
                removed, added = old - new, new - old
                if removed:
                    yield tuple(sorted(removed)), tuple(sorted(added))
                return
            x = left[0]
            for y in compatible[x]:
                if y in left:
                    yield from match(tuple(v for v in left if v not in (x, y)),
                                     pairs + ((x, y),))

        yield from match(neighbors, ())


def catalogue(rows, include_star=False, guard=None):
    guard = guard or Guard()
    seen = set()
    sources = [('apex', apex_exact(rows, guard)), ('pivot', pivots(rows, guard))]
    if include_star:
        sources.append(('star', star_moves(rows, guard)))
    for name, stream in sources:
        for move in stream:
            guard.check()
            if move not in seen:
                seen.add(move)
                yield name, move


def run_task(founder, task, directory, allowance, stop_cpu, stop_event):
    """Seeded iterated steepest descent; same policy and budget in both arms.

    Each complete local census is exhaustive. A budget-truncated census never
    earns a local-optimum claim. Perturbations uniformly sample the current
    full catalogue; path lengths use the historical 4:3:2 interval mixture.
    """
    started = cpu()
    deadline = min(float(stop_cpu), started + float(allowance))
    guard = Guard(deadline, stop_event)
    arm = task['arm']
    if arm not in ('AP', 'AP_STAR'):
        raise ValueError('Unknown catalogue arm')
    include_star = arm == 'AP_STAR'
    seed = task['seed']
    rng = random.Random(seed)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    initial = verify.record(founder['graph6'])
    bestpath = directory / 'best.json'
    best = read(bestpath) if bestpath.exists() else initial
    independently_checked = verify.record(best['graph6'])
    if best != independently_checked or verify.key(best['scores']) > verify.key(initial['scores']):
        raise ValueError('Invalid or worse resumed incumbent')
    current = bits(best['graph6'])
    atomic(bestpath, best)
    atomic(directory / ('candidate_' + best['state'] + '.json'), best)
    archivepath = directory / 'catalog_archive.json'
    archive = {}
    if archivepath.exists():
        saved_archive = read(archivepath)
        if not isinstance(saved_archive, list) or len(saved_archive) > 128:
            raise ValueError('Invalid resumed archive')
        for rec in saved_archive:
            if verify.record(rec['graph6']) != rec:
                raise ValueError('Invalid archived candidate')
            archive[rec['state']] = rec
    archive[best['state']] = best
    if len(archive) > 128:
        del archive[max(archive, key=lambda k: (verify.key(archive[k]['scores']), k))]
    counts = Counter()
    evaluated = Counter()
    accepted = Counter()
    improvements = Counter()
    completed_censuses = 0
    local_optima = 0
    episodes = 0
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    log = (directory / 'catalog_events.jsonl').open('a', encoding='utf-8')

    def adopt(child, expected, operator, kind):
        nonlocal current, best
        guard.check()
        rec = verify.record(graph6(child))
        if rec['scores'] != expected:
            raise ValueError('Incremental/full score mismatch')
        current = child
        accepted[operator] += 1
        if verify.key(rec['scores']) < verify.key(best['scores']):
            best = rec
            atomic(bestpath, best)
            atomic(directory / ('candidate_' + best['state'] + '.json'), best)
            improvements[operator] += 1
        archive[rec['state']] = rec
        if len(archive) > 128:
            victim = max(archive, key=lambda k: (verify.key(archive[k]['scores']), k))
            del archive[victim]
        log.write(json.dumps({'kind': kind, 'operator': operator, 'state': rec['state'],
                              'scores': rec['scores'], 'cpu_seconds': cpu() - started}) + '\n')
        log.flush()

    reason = 'CPU_BUDGET'
    try:
        while True:
            guard.check()
            scorer = Scorer(current)
            winner = None
            moves = []
            for name, move in catalogue(current, include_star, guard):
                counts[name] += 1
                child, score = scorer.evaluate(move)
                evaluated[name] += 1
                moves.append((name, move))
                if verify.key(score) < verify.key(scorer.scores):
                    if winner is None or verify.key(score) < verify.key(winner[1]):
                        winner = child, score, name
            completed_censuses += 1
            if winner is not None:
                adopt(*winner, 'descent')
                if best['scores']['W'] == 0:
                    reason = 'SOLUTION_FOUND'
                    break
                continue
            local_optima += 1
            if not moves:
                reason = 'EMPTY_CATALOGUE'
                break
            episodes += 1
            interval = rng.choices(((2, 4), (5, 12), (13, 32)), weights=(4, 3, 2))[0]
            length = rng.randint(*interval)
            for step in range(length):
                guard.check()
                if step:
                    moves = list(catalogue(current, include_star, guard))
                    completed_censuses += 1
                    for name, _ in moves:
                        counts[name] += 1
                if not moves:
                    break
                name, move = rng.choice(moves)
                child, score = Scorer(current).evaluate(move)
                evaluated[name] += 1
                adopt(child, score, name, 'perturbation')
                if best['scores']['W'] == 0:
                    break
            if best['scores']['W'] == 0:
                reason = 'SOLUTION_FOUND'
                break
    except BudgetEnd:
        reason = 'STOP_REQUESTED' if stop_event is not None and stop_event.is_set() else 'CPU_BUDGET'
    finally:
        log.close()
        atomic(archivepath, sorted(archive.values(), key=lambda r: (verify.key(r['scores']), r['state'])))
    return {'status': reason, 'stop_reason': reason, 'arm': arm, 'seed': seed,
            'founder': verify.record(founder['graph6']), 'best': best,
            'cpu_seconds': cpu() - started, 'process_cpu_seconds': cpu(), 'completed_censuses': completed_censuses,
            'local_optimum_visits': local_optima, 'episodes_started': episodes,
            'enumerated_moves': dict(counts), 'evaluated_moves': dict(evaluated), 'accepted_moves': dict(accepted),
            'best_improvements': dict(improvements),
            'archive_capacity': 128, 'archive': sorted(archive.values(), key=lambda r: (verify.key(r['scores']), r['state'])),
            'resume_policy': 'Restart search from independently validated incumbent with original seed; preserve all prior controller CPU accounting',
            'scope': 'AP reference enumeration with identical iterated-descent policy in both arms; not a reproduction of historical population-P'}
