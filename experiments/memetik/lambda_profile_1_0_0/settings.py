"""Predeclared, immutable v2 profile cells and budgets."""
LENGTHS = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32)
ARMS = ('2076', '2077')
N = 300
CHUNK = 10
CELLS = tuple(f'{a}_k{k:02d}' for k in LENGTHS for a in ARMS)
LIMITS = {'aux': 7200, **{c: 3600 for c in CELLS}}
