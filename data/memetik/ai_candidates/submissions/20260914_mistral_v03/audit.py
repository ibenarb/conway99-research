import collections
import itertools
import json
import pathlib
import subprocess
import sys
import numpy as np
import lambda_transcribed as lam
import omega_transcribed as omg

root = pathlib.Path(__file__).resolve().parent
runs = []
for name in ['lambda_transcribed.py', 'omega_transcribed.py']:
    result = subprocess.run([sys.executable, str(root/name)], capture_output=True, text=True)
    runs.append({'file': name, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
D = [1, 2, 4, 8, 16, 32, 64]
sums = collections.defaultdict(list)
for pair in itertools.combinations_with_replacement(D, 2):
    sums[sum(pair) % 99].append(pair)
A = lam.construct_circular_graph()
A2 = A @ A
edge_common = collections.Counter(int(A2[i,j]) for i in range(99) for j in range(i+1,99) if A[i,j])
try:
    omg.generate_omega_candidate()
except AssertionError as error:
    trace = error.__traceback__
    while trace.tb_frame.f_code.co_name != 'generate_omega_candidate':
        trace = trace.tb_next
    frame = trace.tb_frame.f_locals
    H, P, C = (frame[k] for k in ['H', 'P', 'C'])
unseen = set(range(1,99))
orbits = []
while unseen:
    x = min(unseen)
    orbit = []
    while x not in orbit:
        orbit.append(x)
        x = 2*x % 99
    unseen.difference_update(orbit)
    orbits.append(orbit)
reachable = {0}
for orbit in orbits:
    reachable |= {s + len(orbit) for s in list(reachable)}
output = {'runs': runs, 'sidon_unordered_sums_including_repeats': len(sums)==28,
          'lambda_edge_common_histogram': dict(edge_common),
          'lambda_bad_edges': sum(v for k,v in edge_common.items() if k!=1),
          'edge_0_1_common_neighbors': list(map(int,np.flatnonzero(A[0] & A[1]))),
          'omega_H_degrees': sorted(set(map(int,H.sum(1)))),
          'omega_PH_violations': int(np.count_nonzero(P@H != 2-(C+np.eye(14,dtype=int))@P)),
          'doubling_orbits': orbits, 'orbit_size_subset_can_equal14': 14 in reachable,
          'supplied_graph6_header99': lam.matrix_to_graph6(A)[:2],
          'supplied_graph6_length99': len(lam.matrix_to_graph6(A)),
          'expected_graph6_header99': '~?@b', 'expected_graph6_length99': 813}
print(json.dumps(output, indent=4))
