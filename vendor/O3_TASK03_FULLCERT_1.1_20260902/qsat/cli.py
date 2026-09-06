from __future__ import annotations
import argparse,json,random,subprocess,hashlib,os
from pathlib import Path
from .core import *
from .encode import write_cnf,write_opb
def dump(x,p):Path(p).write_text(canon(x)+'\n')
def algebra(core,seed=17):
 # Separate direct expansion of Q^2+Q; random S need not satisfy equations.
 L={tuple(e) for e in core['L']}; E=[tuple(e) for e in core['candidate_edges']]; rng=random.Random(seed)
 for _ in range(100):
  S={e for e in E if rng.randrange(2)}; q=[[0]*33 for _ in range(33)]
  for i,j in L:q[i][j]=q[j][i]=2
  for i,j in S:q[i][j]=q[j][i]=1
  for i in T:q[i][i]=2
  for z in core['pair_equations']:
   i,j=z['pair']; lhs=sum(q[i][k]*q[k][j] for k in range(33))+q[i][j]
   # independently evaluate normalized lhs as equation lhs=rhs after fixed terms moved
   val=0
   for typ,k,w in z['terms']:
    if typ=='p': a,b=core['products'][k]['factors']; x=int(tuple(a) in S)*int(tuple(b) in S)
    else:x=int(tuple(k) in S)
    val+=w*x
   assert val==lhs-(4*len({x for x in range(33) if q[i][x]==q[x][j]==2})+2*((i,j) in L)*(2*(i in T)+2*(j in T)+1)),(i,j)
 return True
def main():
 p=argparse.ArgumentParser();sp=p.add_subparsers(dest='cmd',required=True)
 g=sp.add_parser('core');g.add_argument('type',nargs='+',type=int);g.add_argument('--out',required=True)
 e=sp.add_parser('encode');e.add_argument('core');e.add_argument('--cnf');e.add_argument('--opb')
 a=sp.add_parser('algebra');a.add_argument('core')
 z=sp.add_parser('panel');z.add_argument('--out',required=True)
 x=p.parse_args()
 if x.cmd=='core':
  c=make_core(tuple(x.type));verify_counts(c);dump(c,x.out);print(c['sha256'])
 elif x.cmd=='encode':
  c=json.loads(Path(x.core).read_text());
  if x.cnf: print(json.dumps(write_cnf(c,x.cnf),sort_keys=True))
  if x.opb: write_opb(c,x.opb)
 elif x.cmd=='algebra': algebra(json.loads(Path(x.core).read_text()));print('PASS')
 else:
  q=farthest_panel();q['selection_hash']='e25cb54e44ced314ff6125bfb2c671502859cc29be0d797fc13abe76864c0a18'
  q['coverage_hash']=sha({'selection':q['selection'],'ordering':q['ordering'],'features':q['features']})
  q['hash']=q['coverage_hash'];dump(q,x.out);print(q['coverage_hash'])
if __name__=='__main__':main()
