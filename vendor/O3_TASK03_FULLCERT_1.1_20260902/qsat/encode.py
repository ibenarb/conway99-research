"""Encoders consume only JSON cores; cardinality is a deterministic Sinz encoding."""
from __future__ import annotations
import json
class CNF:
 def __init__(self): self.cl=[];self.n=0;self.names=[]
 def var(self,name):self.n+=1;self.names.append(name);return self.n
 def add(self,*x): self.cl.append(list(x))
 def clause(self,*x):
  # Boolean constants are represented by True/False in the BDD simplifier.
  if any(a is True for a in x): return
  self.add(*[a for a in x if a is not False])
 def atmost(self,x,k):
  n=len(x)
  if k<0:self.add();return
  if k>=n:return
  if k==0:
   for a in x:self.add(-a)
   return
  s=[[self.var('sc') for _ in range(k)] for _ in range(n-1)]
  self.add(-x[0],s[0][0])
  for j in range(1,k):self.add(-s[0][j])
  for i in range(1,n-1):
   self.add(-x[i],s[i][0]);self.add(-s[i-1][0],s[i][0])
   for j in range(1,k):self.add(-x[i],-s[i-1][j-1],s[i][j]);self.add(-s[i-1][j],s[i][j])
   self.add(-x[i],-s[i-1][k-1])
  self.add(-x[-1],-s[-1][k-1])
 def exactly(self,x,k):self.atmost(x,k);self.atmost([-a for a in x],len(x)-k)
 def weighted_eq(self,items,r):
  """Canonical reduced BDD for sum(w*x)=r; items must have positive weights."""
  ws={}
  for v,w in items: ws[v]=ws.get(v,0)+w
  a=sorted(ws.items()); suffix=[0]*(len(a)+1)
  for i in range(len(a)-1,-1,-1):suffix[i]=suffix[i+1]+a[i][1]
  memo={}
  def neg(v): return (not v) if isinstance(v,bool) else -v
  def node(i,rest):
   if rest<0 or rest>suffix[i]: return False
   if i==len(a): return rest==0
   key=(i,rest)
   if key in memo:return memo[key]
   x,w=a[i]; lo=node(i+1,rest); hi=node(i+1,rest-w)
   if lo is hi: memo[key]=lo;return lo
   v=self.var('bdd_%d_%d'%(i,rest));memo[key]=v
   # v <-> ITE(x,hi,lo), including all four implication directions.
   self.clause(-v,-x,hi);self.clause(-v,x,lo);self.clause(-x,neg(hi),v);self.clause(x,neg(lo),v)
   return v
  root=node(0,r); self.clause(root)
def triangle_components(core):
 out=[];p=6
 for length in core['cycle_type']:
  if length==3:out.append(tuple(range(p,p+3)))
  p+=length
 return out

def add_triangle_exactly_one(c,core,sv):
 groups=0
 for tri in triangle_components(core):
  inside=set(tri)
  for v in range(core['n']):
   if v in inside:continue
   x=[sv[tuple(sorted((v,t)))] for t in tri]
   c.add(*x)
   c.add(-x[0],-x[1]);c.add(-x[0],-x[2]);c.add(-x[1],-x[2])
   groups+=1
 return groups

def cnf_from_core(core,lemma_triangle_eo=False):
 c=CNF(); sv={tuple(e):c.var('s_%d_%d'%tuple(e)) for e in core['candidate_edges']}
 pv={}
 for p in core['products']:
  a,b=map(tuple,p['factors']);z=c.var('p_%d'%p['id']);pv[p['id']]=z;c.add(-z,sv[a]);c.add(-z,sv[b]);c.add(z,-sv[a],-sv[b])
 for i in range(core['n']):c.weighted_eq([(v,1) for e,v in sv.items() if i in e],core['degree_targets'][str(i)])
 for eq in core['pair_equations']:
  xs=[]
  for typ,key,w in eq['terms']:
   v=pv[key] if typ=='p' else sv[tuple(key)]
   xs.append((v,w))
  c.weighted_eq(xs,eq['rhs'])
 if lemma_triangle_eo:add_triangle_exactly_one(c,core,sv)
 return c,sv
def write_cnf(core,path,lemma_triangle_eo=False):
 c,_=cnf_from_core(core,lemma_triangle_eo=lemma_triangle_eo)
 with open(path,'w') as f:
  f.write('p cnf %d %d\n'%(c.n,len(c.cl)))
  for z in c.cl:f.write(' '.join(map(str,z))+' 0\n')
 return {'variables':c.n,'clauses':len(c.cl)}
def write_opb(core,path):
 # native pseudo-Boolean syntax; products are constrained explicitly.
 with open(path,'w') as f:
  f.write('* #variable= %d #constraint= %d\n'%(501+14721,33+528+3*14721))
  for p in core['products']:
   z='p%d'%p['id'];a='s%d_%d'%tuple(p['factors'][0]);b='s%d_%d'%tuple(p['factors'][1])
   f.write('1 %s -1 %s >= 0 ;\n'%(a,z));f.write('1 %s -1 %s >= 0 ;\n'%(b,z));f.write('1 %s -1 %s -1 %s >= -1 ;\n'%(z,a,b))
  for i in range(core['n']):
   f.write(' '.join('1 s%d_%d'%tuple(e) for e in core['candidate_edges'] if i in e)+' = %d ;\n'%core['degree_targets'][str(i)])
  for q in core['pair_equations']:
   f.write(' '.join('%d %s'%(w,'p%d'%k if t=='p' else 's%d_%d'%tuple(k)) for t,k,w in q['terms'])+' = %d ;\n'%q['rhs'])
