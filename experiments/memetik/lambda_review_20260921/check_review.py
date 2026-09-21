"""Independent reproduction of review records and the pivot neighbourhood.

Read-only diagnostic search, no campaign launcher. Requires repository kernels.
"""
from pathlib import Path
import sys
import json
import re
import hashlib
from itertools import combinations
from collections import defaultdict
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'lambda_strategy_0_1_0'))
import bootstrap
from common import core, checked, atomic
from search import key
from strategy import cycle_moves
import fast_moves


def pivot_candidates(rows):
    by_point = defaultdict(list)
    for triple in fast_moves.reference.triangles(rows):
        for point in triple:
            by_point[point].append(tuple(v for v in triple if v != point))
    for point, pairs in sorted(by_point.items()):
        for (x, y), (u, v) in combinations(pairs, 2):
            for a, b in ((x, y), (y, x)):
                deleted = tuple(sorted((core.edge(a,b),core.edge(u,v))))
                added = tuple(sorted((core.edge(a,u),core.edge(b,v))))
                yield (point,a,b,u,v), (deleted,added)


def pivots(rows):
    for label, move in pivot_candidates(rows):
        p, x, y, u, v = label
        if rows[x] & (1 << u) or rows[y] & (1 << v):
            continue
        # In a valid lambda graph N(p) is exactly 7 disjoint edges, hence
        # all cross-base adjacency terms of reviewer M6 are zero.
        if (rows[x] & rows[u]).bit_count() != 1 or (rows[y] & rows[v]).bit_count() != 1:
            continue
        yield move


def brute_pivots(rows):
    valid = set()
    proposals = 0
    for label, move in pivot_candidates(rows):
        proposals += 1
        try:
            child = core.apply_move(rows, move)
            core.validate(child, 'lambda')
        except ValueError:
            continue
        valid.add(move)
    assert proposals == 4158
    return valid


def census(rows, target='W', use_cycles=False):
    moves = [('apex', m) for m in fast_moves.apex_moves(rows)]
    moves += [('pivot', m) for m in pivots(rows)]
    if use_cycles:
        moves += [('cycle3', m) for m in cycle_moves(rows)]
    start = core.metrics(rows)
    records = []
    for name, move in moves:
        child = core.apply_move(rows, move)
        scores = core.metrics(child)
        records.append((name, move, child, scores))
    stats = {}
    for name in ('apex', 'pivot', 'cycle3'):
        sub = [r for r in records if r[0] == name]
        if sub or name != 'cycle3' or use_cycles:
            stats[name] = {'moves':len(sub), 'improvements':{t:sum(key(r[3],t)<key(start,t) for r in sub) for t in ('W','L1','F','Linf')}}
    return stats, records


def descent(rows, target, use_cycles=False, max_steps=100):
    original = rows
    trace = []
    for iteration in range(max_steps):
        stats, candidates = census(rows,target,use_cycles)
        current = core.metrics(rows)
        better = [r for r in candidates if key(r[3],target) < key(current,target)]
        if not better:
            text = core.encode_g6(rows)
            _, scores = checked(text, 'lambda')
            return {'status':'LOCAL_MIN_EXACT_IN_DECLARED_CATALOG','target':target,
                    'catalog':['apex','pivot']+(['cycle3'] if use_cycles else []),
                    'scores':scores,'graph6':text,'class':core.canonical(rows),
                    'trace':trace,'last_census':stats}
        # Explicit reproducible tie break: trade's edge lists, not provenance.
        name, move, child, scores = min(better,key=lambda r:(key(r[3],target),r[1]))
        checked(core.encode_g6(child),'lambda')
        trace.append({'operator':name,'move':move,'scores':{k:scores[k] for k in ('W','L1','F','Linf','Nmax')}})
        rows = child
    return {'status':'STEP_LIMIT','trace':trace}


def main():
    source, comparison, out = map(Path,sys.argv[1:])
    raw = source.read_text()
    matches = re.findall(r'\*\*([^*]+\.g6)\*\*[^\n]*?True ([a-f0-9]{64})\s*```\s*([^\n]+)\s*```',raw)
    assert len(matches) == 3
    records = []
    for name, digest, graph6 in matches:
        assert hashlib.sha256(graph6.encode()).hexdigest() == digest
        rows, scores = checked(graph6,'lambda')
        stats, neighbours = census(rows,use_cycles=True)
        records.append({'name':name,'sha256_graph6':digest,'scores':scores,'graph6':graph6,
                        'class':core.canonical(rows),'census':stats})
        print(name,scores,stats,flush=True)
    split = json.loads((comparison/'founder_split.json').read_text())['confirmation']['lambda']
    hog = next(x for x in split if x['line']=='hog57338')
    original = core.decode_g6(hog['graph6'])
    counts = []
    cases = ['hog57338','claude_v01_c','gen-lambda-11','gen-lambda-03','gen-lambda-13','gen-lambda-17']
    for line in cases:
        f = next(x for x in split if x['line']==line)
        rows = core.decode_g6(f['graph6'])
        fast = set(pivots(rows))
        brute = brute_pivots(rows)
        assert fast == brute
        for move in fast:
            child = core.apply_move(rows,move)
            checked(core.encode_g6(child),'lambda')
            assert core.apply_move(child,move[::-1])==rows
        counts.append({'line':line,'candidates':4158,'valid_pivots':len(fast),'bruteforce_equal':True})
        print('pivot',line,len(fast),flush=True)
    historical = json.loads((comparison/'tasks/lambda-W-06-A1/result.json').read_text())['best']
    target = core.decode_g6(historical['graph6'])
    witnesses = [move for move in pivots(original) if core.apply_move(original,move)==target]
    assert len(witnesses)==1
    descents = {}
    for objective in ('W','L1','F','Linf'):
        result = descent(original,objective)
        descents[objective] = result
        print('descent',objective,result.get('scores'),len(result['trace']),flush=True)
    report = {'review_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'review_graphs':records,'pivot_controls':counts,'historical_pivot':witnesses[0],
              'hog_census':census(original)[0],'hog_descents':descents,
              'not_reproduced':['depth-4 BFS','240 CPU-second tabu trajectory','all Linf-transfer trajectories',
                                'review numpy Apex accelerator','timing claims in reviewer environment']}
    atomic(out,report)


if __name__=='__main__':
    main()
