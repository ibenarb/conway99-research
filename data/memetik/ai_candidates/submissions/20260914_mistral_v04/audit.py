import collections
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import numpy as np

root = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('supplied', root/'generator_normalized.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
P,C,pairs = m.build_omega_frame()
H = np.zeros((84,84), dtype=int)
H[0,1] = H[1,0] = 1
first = bool(m.check_omega_conditions(H,P,C,0,1))
target = 2-(C+np.eye(14,dtype=int))@P
calls = []
original = m.check_omega_conditions
def logged(H,P,C,i,j):
    calls.append((int(i),int(j)))
    return original(H,P,C,i,j)
m.check_omega_conditions = logged
result = m.backtrack_omega(np.zeros((84,84),dtype=int),P,C,np.zeros(84,dtype=int),0,20)
runs = []
for budget in [20,1000000]:
    run = subprocess.run([sys.executable,str(root/'generator_normalized.py'),'42',str(budget)],capture_output=True,text=True,timeout=15)
    runs.append({'budget':budget,'exit_code':run.returncode,'stdout':run.stdout,'stderr_tail':run.stderr[-1800:]})
# Direct roundtrip test for intended n=99 using standard columnwise graph6 decoding.
A = np.zeros((99,99),dtype=int)
A[0,3] = A[3,0] = 1
encoded = m.matrix_to_graph6(A)
bits = [(ord(ch)-63 >> bit)&1 for ch in encoded[4:] for bit in range(5,-1,-1)]
decoded = np.zeros_like(A)
k = 0
for j in range(1,99):
    for i in range(j):
        decoded[i,j] = decoded[j,i] = bits[k]
        k += 1
out = {'first_edge_accepted': first,'target_entry_range':[int(target.min()),int(target.max())],
       'bounded_result_is_none':result is None,'bounded_check_calls':len(calls),
       'bounded_distinct_edges':sorted(set(calls)), 'runs':runs,
       'graph6_header99':encoded[:4], 'graph6_length99':len(encoded),
       'encoder_roundtrip_equal':bool(np.array_equal(A,decoded)),
       'input_edges':[[0,3]], 'decoded_edges':np.argwhere(np.triu(decoded,1)).tolist()}
print(json.dumps(out,indent=4))
