import collections,itertools,json,math,pathlib,random
from core import OUTER,decode_g6
from operators import signed_vectors,restricted_vectors
p=pathlib.Path(__file__).parent
founders=json.loads((p/'founders.json').read_text()); root=next(x for x in founders if x['id']=='A_legacy');rows=decode_g6(root['graph6']); columns=[rows[v+15]>>15 for v in range(84)]
r={}
for length in (4,6):
    histogram=collections.Counter();seen=set();right_counts=collections.Counter()
    for x in signed_vectors(length,random.Random(0)):
        plus=sum(1<<u for u,s in x if s==1);minus=sum(1<<u for u,s in x if s==-1);mask=plus|minus
        assert mask.bit_count()==length
        key=min((plus,minus),(minus,plus));assert key not in seen;seen.add(key)
        balances=[0]*14
        for u,s in x:
            for a in OUTER[u]:balances[a]+=s
        assert balances==[0]*14
        signs={v:(1 if (c&mask)==minus else -1) for v,c in enumerate(columns) if not (mask>>v)&1 and (c&mask) in (plus,minus)}
        histogram[len(signs)]+=1
        if length==4:
            for k in (4,6,8):
                if len(signs)>=k:right_counts[k]+=sum(1 for _ in restricted_vectors(signs,k))
    r[str(length)]={'signed_vectors_mod_sign':len(seen),'compatible_label_histogram':dict(sorted(histogram.items())),'right_vector_counts':dict(right_counts)}
    print(length,r[str(length)],flush=True)
for k in (4,6):
    r['cycle_count_'+str(k)]=sum((-1)**m*math.comb(7,m)*math.comb(14-2*m,k-2*m)*math.factorial(k-m-1)*2**m for m in range(k//2+1))//2
valid=lambda a,b:a!=b and abs(a-b)!=7
r['bowtie_count']=sum(sum(valid(x,y) and valid(z,w) for (x,y),(z,w) in [((b,c),(d,e)),((b,d),(c,e)),((b,e),(c,d))]) for a in range(14) for b,c,d,e in itertools.combinations([v for v in range(14) if valid(a,v)],4))
r['scope']='Counts matched using archived vector enumeration; cycle/bowtie counts independently combinatorial. Compatibility covers initial A only, not all eight states. No new graph search.'
(p/'CATALOG_CHECK.json').write_text(json.dumps(r,indent=4)+'\n')
