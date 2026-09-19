"""Freeze complete depth-three cube trees using only totalizer UP, never Lex results."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess

CASES = ('matching_1_1_1_1_1_1', 'matching_2_2_2', 'matching_6')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_tree(tree):
    leaves = []
    def visit(node, cube, depth):
        if node['cube'] != cube:
            raise ValueError('Incorrect cube path')
        if 'children' not in node:
            if depth != 3:
                raise ValueError('Unexpected leaf depth')
            leaves.append(cube)
            return
        v = node['split']
        if not 1 <= v <= 1722 or v in {abs(x) for x in cube}:
            raise ValueError('Invalid/repeated split')
        children = node['children']
        if len(children) != 2:
            raise ValueError('Missing split side')
        visit(children[0], cube + [v], depth+1)
        visit(children[1], cube + [-v], depth+1)
    visit(tree, [], 0)
    if len(leaves) != 8 or sum(Fraction(1, 2**len(c)) for c in leaves) != 1:
        raise ValueError('Incomplete cover')
    return leaves


def build(binary, directory):
    records = {}
    for case in CASES:
        file = directory / (case + '__totalizer.cnf')
        cache = {}
        def query(cube):
            key = tuple(cube)
            if key not in cache:
                cache[key] = json.loads(subprocess.check_output(
                    [str(binary), str(file), *map(str, cube)], text=True, timeout=60))
            return cache[key]
        def node(cube, depth):
            baseline = query(cube)
            row = {'cube': cube, 'up_conflict': baseline['conflict'],
                   'up_primary_count': len(baseline['primary_literals'])}
            if depth == 3:
                return row
            fixed = {abs(x) for x in baseline['primary_literals']} | {abs(x) for x in cube}
            free = [v for v in range(1,1723) if v not in fixed]
            if not free:
                raise RuntimeError('No free split variable')
            candidates = sorted({free[i*(len(free)-1)//7] for i in range(8)})
            trials = []
            for v in candidates:
                plus, minus = query(cube+[v]), query(cube+[-v])
                counts = [len(x['primary_literals']) for x in (plus, minus)]
                conflicts = sum(x['conflict'] for x in (plus, minus))
                score = (-conflicts, min(counts), -abs(counts[0]-counts[1]), -v)
                trials.append((score, v, counts, conflicts))
            _, v, _, _ = max(trials)
            row['split'] = v
            row['candidate_diagnostics'] = [
                {'variable': t[1], 'primary_counts': t[2], 'up_conflicts': t[3]} for t in trials]
            row['children'] = [node(cube+[v], depth+1), node(cube+[-v], depth+1)]
            print(case, cube, 'split', v, flush=True)
            return row
        tree = node([], 0)
        leaves = validate_tree(tree)
        open_leaves = sum(not query(c)['conflict'] for c in leaves)
        records[case] = {'base_sha256': digest(file), 'tree': tree, 'leaves': leaves,
                         'up_open_leaves': open_leaves, 'cube_gate': open_leaves >= 4,
                         'up_queries': len(cache)}
    return {'version': '1.1.0', 'selection': 'Eight evenly spread free primary variables per node; prefer both UP-open, then larger minimum closure, then balance, then lower ID.',
            'scope': 'Complete labelled primary cover, not a percentage of graph solutions. No SAT searches used.',
            'cases': records, 'up_binary_sha256': digest(binary)}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--variants', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    result = build(a.binary.resolve(), a.variants)
    a.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: {'leaves': len(v['leaves']), 'open': v['up_open_leaves'], 'gate': v['cube_gate']} for k,v in result['cases'].items()}))
