"""Seek and exactly certify that relative frame alignment can change nullity."""
from pathlib import Path
import sys,json,random,time
import numpy as np
import sympy as sy
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'src/research_20260912'))
from crossover_audit import difference,constraint_matrix,rank_mod_prime
from core import decode_g6,random_frame,relabel,validate
items=json.loads((BASE/'data/memetic_v2/reference/population64.json').read_text())['candidates']
a=decode_g6(items[0]['g6']);result=None
for index in (15,25,38,46,54,57,62):
    b=decode_g6(items[index]['g6']);D=constraint_matrix(difference(a,b));d=D.shape[1]
    if not d:continue
    modular=rank_mod_prime(D)
    if d-modular<2:continue
    basis=sy.Matrix(D.tolist()).nullspace()
    assert len(basis)==d-modular
    for seed in range(3):
        perm=random_frame(random.Random(20260912+seed));c=relabel(b,perm);validate(c,'omega')
        C=constraint_matrix(difference(a,c));assert not np.any(C.sum(axis=1))
        rank=rank_mod_prime(C)
        if rank==C.shape[1]-1:
            result={'status':'EXACT_COUNTEREXAMPLE_TO_ALIGNMENT_INVARIANCE','first_population_index':0,'second_population_index':index,'original_d':d,'original_nullity':len(basis),'relative_permutation':perm,'aligned_d':C.shape[1],'aligned_nullity':1,'original_nullspace_basis':[[str(v) for v in col] for col in basis],'scope':'Same graph pair, different relative legal frame. Rational basis plus modular rank prove both dimensions. Does not establish benefit of random realignment.'}
            break
    if result:break
assert result is not None
(BASE/'results/review_synthesis_20260912/alignment.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:v for k,v in result.items() if k not in ('relative_permutation','original_nullspace_basis')})
