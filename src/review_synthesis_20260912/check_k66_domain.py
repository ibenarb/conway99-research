"""Audit the actual four K66 profile domains; source bundle required."""
from pathlib import Path
from collections import Counter
import argparse,json,hashlib
parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);args=parser.parse_args()
path=args.source/'analysis/profile_models.json';models=json.loads(path.read_text());out=[]
for root in ('v4_09322','v4_09323','v4_09332','v4_09333'):
    d=models[root];sums=Counter();checks=0
    for p in d['profiles']:
        z=p['z']
        for start in (0,4,8):
            group=range(start,start+4);sums[sum(z[i] for i in group)]+=1
            for i in group:
                assert z[i]**2-sum(z[i]*z[j] for j in group if i!=j)==4*int(z[i]==2)
                checks+=1
    assert set(sums)=={2}
    out.append({'root':root,'profiles':len(d['profiles']),'group_sum_histogram':dict(sums),'coordinate_identities_verified':checks})
# At a single zero coordinate the identity holds for any group sum.
assert 2*0**2-0*1==4*int(0==2)
base=Path(__file__).resolve().parents[2]
result={'status':'PASS_ALL_FOUR_ACTUAL_DOMAINS','profile_models_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'roots':out,'scope':'Identities on supplied domains; upstream completeness and CNF certification remain separate.'}
(base/'results/review_synthesis_20260912/k66_domain.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
