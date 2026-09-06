"""Small three-orbit quotient core using exactly the production core schema."""
from __future__ import annotations
from .core import canon,sha
def core():
 edges=[(0,1),(0,2),(1,2)]; prods=[]; eq=[]
 for pid,(i,j) in enumerate(edges):
  k=({0,1,2}-{i,j}).pop(); a=tuple(sorted((i,k)));b=tuple(sorted((j,k)))
  prods.append({'id':pid,'factors':[list(a),list(b)]})
  eq.append({'pair':[i,j],'rhs':6,'terms':[['p',pid,1],['s',(i,j),5]]})
 x={'format':'O3-QSAT-CORE-0.1','n':3,'T':[0,1,2],'U':[],'cycle_type':[],'L':[],
 'candidate_edges':edges,'degree_targets':{'0':2,'1':2,'2':2},'products':prods,
 'pair_equations':eq,'matrix':{'identity':'Q^2+Q=2I+6J','Q':'2I+S'}};x['sha256']=sha(x);return x
def verify(c,chosen):
 s={tuple(e) for e in chosen}
 if not set(c['candidate_edges'])>=s: raise ValueError('foreign Rook edge')
 if [sum(i in e for e in s) for i in range(3)] != [2]*3: raise ValueError('Rook degree')
 q=[[2 if i==j else int(tuple(sorted((i,j))) in s) for j in range(3)] for i in range(3)]
 for i in range(3):
  for j in range(3):
   if sum(q[i][k]*q[k][j] for k in range(3))+q[i][j] != (8 if i==j else 6): raise ValueError('Rook matrix')
 return True
