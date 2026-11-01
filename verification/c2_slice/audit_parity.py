from itertools import combinations, product
from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
EDGES = [(u, v) for u in range(12) for v in range(u + 1, 12) if u // 2 != v // 2]
index = {edge: i for i, edge in enumerate(EDGES)}
orbits = []
for b, c in combinations(range(6), 2):
    orbits.append((index[(2*b, 2*c)], index[(2*b+1, 2*c+1)]))
    orbits.append((index[(2*b, 2*c+1)], index[(2*b+1, 2*c)]))

# Affine polynomials over F_2 represented by bitsets; bit 0 is the constant.
variable_names = []
y = [[0] * 60 for _ in range(3)]
for b in range(3):
    for orbit_id, (c, gc) in enumerate(orbits):
        if any(v // 2 == b for v in EDGES[c]):
            continue
        variable_names.append({'type1_block': b, 'column_orbit': orbit_id})
        term = 1 << len(variable_names)
        y[b][c] = term
        y[b][gc] = term ^ 1
assert len(variable_names) == 60

s = 0
for c, gc in orbits:
    active = [b for b in range(3) if y[b][c]]
    if len(active) == 3:
        # Three binary choices have an odd number of pairwise agreements.
        for choices in product((0, 1), repeat=3):
            assert sum(choices[i] == choices[j] for i, j in combinations(range(3), 2)) % 2 == 1
        s ^= 1
    elif len(active) == 2:
        b, d = active
        s ^= 1 ^ y[b][c] ^ y[d][c]

selected_degrees = []
degree_sum = 0
for b in range(3):
    for d in range(3):
        if d == b:
            continue
        anchor = 2*d + 1
        degree = 0
        for c, edge in enumerate(EDGES):
            if anchor in edge:
                degree ^= y[b][c]
        degree_sum ^= degree
        selected_degrees.append({'type1_block': b, 'anchor': anchor, 'rhs_degree': 4, 'affine_bitset_hex': hex(degree)})

assert s ^ degree_sum == 1
# Each selected degree equals 4, and S is the sum of three pairwise overlaps, each 4.
# All these integers are even; their affine XOR equals 1. Contradiction.
result = {'variables': len(variable_names), 'selected_degree_equations': selected_degrees,
          'pair_overlap_rhs': [4, 4, 4], 'S_affine_bitset_hex': hex(s),
          'xor_of_even_left_sides_hex': hex(s ^ degree_sum),
          'conclusion': 'Three type-I blocks are impossible under the necessary slice identities.',
          'variable_names': variable_names, 'column_edges': EDGES, 'column_orbits': orbits}
(OUT / 'triple_parity_certificate.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print('PASS: 60-variable affine F_2 certificate: XOR of seven even quantities equals 1.')
