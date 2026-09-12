"""Alternating difference circuits and an exact sufficient no-crossover test."""
from pathlib import Path
import json
import random
import sys
import time
import numpy as np

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'src/memetic_v2'))
from core import OUTER, decode_g6, apply_move, validate


def difference(first, second):
    return [(i,j, -1 if first[i] & (1<<j) else 1) for i in range(len(first)) for j in range(i+1,len(first)) if bool(first[i] & (1<<j)) != bool(second[i] & (1<<j))]


def circuits(first, second, seed):
    edges = difference(first,second)
    rng = random.Random(seed)
    pairing = {}
    for v in range(len(first)):
        red = [e for e,(a,b,sgn) in enumerate(edges) if v in (a,b) and sgn == -1]
        blue = [e for e,(a,b,sgn) in enumerate(edges) if v in (a,b) and sgn == 1]
        assert len(red)==len(blue)
        rng.shuffle(blue)
        for a,b in zip(red,blue):
            pairing[v,a]=b
            pairing[v,b]=a
    unused = set(range(len(edges)))
    result = []
    while unused:
        start = min(unused)
        e, v = start, edges[start][0]
        group = []
        while e in unused:
            unused.remove(e)
            group.append(e)
            e = pairing[v,e]
            a,b,_ = edges[e]
            v = b if v == a else a
        assert e == start and len(group)%2 == 0
        result.append(group)
    return edges,result


def constraint_matrix(edges):
    A = np.zeros((84*14,len(edges)),dtype=np.int64)
    for c,(i,j,sign) in enumerate(edges):
        assert i>=15 and j>=15
        for label in OUTER[j-15]:
            A[(i-15)*14+label,c] += sign
        for label in OUTER[i-15]:
            A[(j-15)*14+label,c] += sign
    return A[np.any(A,axis=1)]


def rank_mod_prime(A, prime=1000003):
    a=A.copy()%prime
    r=0
    for col in range(a.shape[1]):
        choices=np.flatnonzero(a[r:,col])
        if not len(choices):
            continue
        p=r+int(choices[0])
        a[[r,p]]=a[[p,r]]
        a[r]=(a[r]*pow(int(a[r,col]),-1,prime))%prime
        # Row echelon suffices for a rank certificate replay.
        for block in range(r+1,len(a),64):
            end=min(len(a),block+64)
            a[block:end]=(a[block:end]-a[block:end,col,None]*a[r])%prime
        r+=1
        if r==a.shape[0]:
            break
    return r


def main():
    items=json.loads((BASE/'data/memetic_v2/reference/population64.json').read_text())['candidates']
    omega=[x for x in items if x['arm']=='omega']
    lambda_items=[x for x in items if x['arm']=='lambda']
    outputs=[]
    # Nearby same-founder parents and several distinct founder pairs.
    pairs=[(omega[0],omega[1]),(omega[-1],omega[-2])]
    refs=BASE/'data/memetic_v2/reference'
    first=decode_g6((refs/'H_minus_Z2_template_A99.g6').read_text())
    second=decode_g6((refs/'H_plus_Z2_template_A99.g6').read_text())
    explicit=[('H_minus_H_plus',first,second,'omega')]
    explicit += [(f'omega_pair_{i}',decode_g6(a['g6']),decode_g6(b['g6']),'omega') for i,(a,b) in enumerate(pairs)]
    explicit += [('lambda_distinct',decode_g6(lambda_items[0]['g6']),decode_g6(lambda_items[-1]['g6']),'lambda')]
    for name,a,b,arm in explicit:
        validate(a,arm);validate(b,arm)
        edges,groups=circuits(a,b,20260912)
        valid_arm=0
        for group in groups:
            deleted=tuple((edges[e][0],edges[e][1]) for e in group if edges[e][2]<0)
            added=tuple((edges[e][0],edges[e][1]) for e in group if edges[e][2]>0)
            child=apply_move(a,(deleted,added))
            validate(child)
            try:
                validate(child,arm)
                valid_arm+=1
            except ValueError:
                pass
        item={'pair':name,'arm':arm,'differing_edges':len(edges),'alternating_components':len(groups),
              'component_lengths':[len(g) for g in groups], 'individual_components_preserving_full_arm':valid_arm}
        if arm=='omega':
            A=constraint_matrix(edges)
            assert not np.any(A.sum(axis=1))
            r=rank_mod_prime(A)
            item.update(rank_mod_prime=r,prime=1000003,
                        exact_no_proper_child=(r==len(edges)-1),
                        rank_test_scope='If rank=d-1, rational kernel is precisely span(all-ones); no proper binary subset. Otherwise undecided.')
        outputs.append(item)
    out={'status':'PASS_DEGREE_PRESERVATION_ALL_COMPONENTS','results':outputs,
         'scope':'Alternating circuits preserve degrees; lambda and P-margins need extra checks. No claim of new superior crossover.'}
    (BASE/'results/research_20260912/crossover.json').write_text(json.dumps(out,indent=4)+'\n')
    print(json.dumps(out,indent=4))

if __name__=='__main__':
    main()
