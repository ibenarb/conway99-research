"""Balanced 2x2 plan on the SAME (a,M) representative forest in every cell."""
import bootstrap
import os
from plan import selection, VARIANTS, choose_controls, PLAN_SHA, RULES_COMMIT
from kernel import load_roots

DRAWS = int(os.environ.get('ROOT8105_TREE_DRAWS', '10000'))
DEPTH = int(os.environ.get('ROOT8105_TREE_DEPTH', '13'))
MODEL = f'ROOT8105-matching-forest-importance-v1-draws{DRAWS}-depth{DEPTH}'


def jobs():
    if DRAWS < 24 or not 2 <= DEPTH <= 13:
        raise ValueError('need >=24 draws per cell and depth 2..13')
    roots = {r['id']: r for r in load_roots()}
    selected = sorted(r['root'] for r in selection()['roots'])
    out = []
    for cell in range(4):
        for i, rid in enumerate(selected):
            root = roots[rid]
            out.append(root | {'id': cell * 24 + i + 1, 'root_id': rid, 'kind': 'tree',
                'cell': cell, 'order': 'numeric' if cell < 2 else 'neighborhood',
                'propagation': bool(cell % 2), 'walks': DRAWS // 24 + int(i < DRAWS % 24),
                'max_depth': DEPTH, 'seed': 810520261009 + rid * 1000003,
                'common_matching_forest': True})
    return out


def keys(root, test=False):
    return set(map(str, range(1, 84))) if test else {'1'}
