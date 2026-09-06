"""Independent O3-QSAT instance core.  No encoder imports this module's algebra."""
from __future__ import annotations
import hashlib,json,math
from collections import Counter
N=33; T=tuple(range(6)); U=tuple(range(6,33))
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(x): return hashlib.sha256(canon(x).encode()).hexdigest()
def partitions(n,m=3):
    if n==0: yield (); return
    for a in range(min(n,n),m-1,-1):
        for r in partitions(n-a,m):
            if not r or a>=r[0]: yield (a,)+r
def all_types(): return list(partitions(27))
def ledges(part):
    out=[]; p=6
    for l in part:
        out += [tuple(sorted((p+i,p+(i+1)%l))) for i in range(l)]
        p+=l
    return sorted(out)
def features(p):
    c=Counter(p); aut=1
    for l,n in c.items(): aut*= (2*l)**n*math.factorial(n)
    return {'type':list(p),'c3':c[3],'components':len(p),'largest':p[0],
            'different_lengths':len(c),'log2_aut':math.log2(aut)}
def product_ids(cands):
    s=set(cands); q=set()
    for i in range(N):
      for j in range(i+1,N):
        for k in range(N):
            if k in (i,j): continue
            a=tuple(sorted((i,k))); b=tuple(sorted((k,j)))
            if a in s and b in s: q.add((a,b) if a<b else (b,a))
    return sorted(q)
def make_core(part):
    L=ledges(part); ls=set(L); cands=[(i,j) for i in range(N) for j in range(i+1,N) if (i,j) not in ls]; candset=set(cands)
    nbr={i:set() for i in range(N)}
    for i,j in L:nbr[i].add(j);nbr[j].add(i)
    prod=product_ids(cands); pid={x:n for n,x in enumerate(prod)}
    pairs=[]
    for i in range(N):
      for j in range(i+1,N):
        d=2*(i in T)+2*(j in T); cij=d+1; ell=(i,j) in ls
        terms=[]
        for k in range(N):
          if k in (i,j):continue
          a,b=tuple(sorted((i,k))),tuple(sorted((k,j)))
          if a in candset and b in candset:
            z=(a,b) if a<b else (b,a); terms.append(['p',pid[z],1])
        for k in nbr[j]:
          if k!=i and tuple(sorted((i,k))) in candset:terms.append(['s',tuple(sorted((i,k))),2])
        for k in nbr[i]:
          if k!=j and tuple(sorted((k,j))) in candset:terms.append(['s',tuple(sorted((k,j))),2])
        if not ell:terms.append(['s',(i,j),cij])
        rhs=6-4*len(nbr[i]&nbr[j])-2*ell*cij
        pairs.append({'pair':[i,j],'rhs':rhs,'terms':terms})
    x={'format':'O3-QSAT-CORE-0.1','n':N,'T':list(T),'U':list(U),'cycle_type':list(part),'L':L,
       'candidate_edges':cands,'degree_targets':{str(i):(12 if i in T else 10) for i in range(N)},
       'products':[{'id':i,'factors':[list(a),list(b)]} for i,(a,b) in enumerate(prod)],'pair_equations':pairs,
       'matrix':{'identity':'Q^2+Q=12I+6J','Q':'2D_T+S+2L'}}
    x['sha256']=sha(x); return x
def verify_counts(core):
    assert len(core['candidate_edges'])==501
    assert len(core['products'])==14721
    assert len(core['pair_equations'])==528
def farthest_panel():
    ts=[p for p in all_types() if 4 not in p]; fs={p:features(p) for p in ts}; keys=['c3','components','largest','different_lengths','log2_aut']
    lo={k:min(fs[p][k] for p in ts) for k in keys}; hi={k:max(fs[p][k] for p in ts) for k in keys}
    picked=[(3,)*9,(27,)]; sequence=[]
    while len(picked)<12:
      def dist(p,q): return sum(abs((fs[p][k]-lo[k])/(hi[k]-lo[k] or 1)-(fs[q][k]-lo[k])/(hi[k]-lo[k] or 1)) for k in keys)
      choice=max((min(dist(p,q) for q in picked),p) for p in ts if p not in picked)[1]
      picked.append(choice);sequence.append(list(choice))
    order=[]
    for i in range(6): order += [picked[i],picked[-1-i]]
    return {'features':[fs[p] for p in ts],'selection':[list(p) for p in picked],'selection_additions':sequence,
      'ordering': [list(p) for p in order], 'hash':None}
