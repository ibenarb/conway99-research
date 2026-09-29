import sys,json,pathlib,collections,hashlib,time
import pynauty
ROOT=pathlib.Path('/workspace/scratch/d1de4c340b15')
sys.path.insert(0,str(ROOT/'analysis120/ryzen_lambda_repair_120_20260928/program'))
from verify import decode,encode,checked,window_check
pool=json.loads((ROOT/'research-repo/docs/memetik/lambda_repair_results_20260929/CANDIDATES_25.json').read_text())
m=json.loads((ROOT/'analysis120/ryzen_lambda_repair_120_20260928/program/MANIFEST.json').read_text())
review=pathlib.Path('/tmp/review15/checks')

def variants(rows):
    for p,neighbours in enumerate(rows):
        N=set(neighbours)
        old={tuple(sorted((x,y))) for x in N for y in rows[x]&N}
        # Independently construct compatibility from whole common-neighbor sets.
        allowed={x:{y for y in N-{x} if (rows[x]&rows[y])=={p}} for x in N}
        def match(left,edges):
            if not left:
                if set(edges)!=old:
                    changed=old.symmetric_difference(edges)
                    new=[set(x) for x in rows]
                    for x,y in changed:
                        if y in new[x]:new[x].remove(y);new[y].remove(x)
                        else:new[x].add(y);new[y].add(x)
                    yield p,new,changed
                return
            x=min(left)
            for y in sorted(allowed[x]&left):
                yield from match(left-{x,y},edges+[(min(x,y),max(x,y))])
        yield from match(N,[])

def cert(g):
    rows=decode(g)
    return pynauty.certificate(pynauty.Graph(len(rows),adjacency_dict={i:list(v) for i,v in enumerate(rows)}))

expected={x['state']:x for x in json.loads((review/'star_census.json').read_text())}
counts=[];improving=[]
for v in pool:
    rows=decode(v['graph6']);base=(v['scores']['W'],v['scores']['L1']);n=ni=0;best=None
    for p,new,changed in variants(rows):
        _,s=checked(encode(new));score=(s['W'],s['L1']);n+=1;ni+=score<base;best=score if best is None else min(best,score)
        if score<base:improving.append({'state':v['state'],'pivot':p,'score':score,'graph6':encode(new),'changed':sorted(changed)})
    e=expected[v['state']];assert (n,ni,list(best))==(e['valid_moves'],e['improving'],e['best'])
    counts.append({'state':v['state'],'valid':n,'improving':ni,'best':best})
    print('PASS',base,n,ni,flush=True)
roots={x['id']:x for x in m['founders']};rootstates={x['state']:x['id'] for x in m['founders']}
founder_improvements=[x for x in improving if x['state'] in rootstates]
contained=[]
for x in founder_improvements:
    founder=rootstates[x['state']];support={u for edge in x['changed'] for u in edge}
    ts=[t['id'] for t in m['tasks'] if t['founder']==founder and support<=set(t['vertices'])]
    if ts:contained.append({'founder':founder,'score':x['score'],'tasks':ts});[window_check(x['graph6'],roots[founder]['graph6'],next(t['vertices'] for t in m['tasks'] if t['id']==tid)) for tid in ts]
endpoints=json.loads((review/'star_descent_endpoints.json').read_text());oldclasses={cert(v['graph6']) for v in pool};ec=set()
for x in endpoints:
    _,s=checked(x['graph6']);assert [s['W'],s['L1']]==x['end'];ec.add(cert(x['graph6']))
for name in review.glob('best_*.json'):
    rows=[set(x) for x in json.loads(name.read_text())];_,s=checked(encode(rows));print(name.name,s)
rook=[{j for j in range(9) if j!=i and (j//3==i//3 or j%3==i%3)} for i in range(9)]
assert not list(variants(rook))
out={'census_independently_reproduced':counts,'founder_improvement_count':len(founder_improvements),'founders_improved':len({x['state'] for x in founder_improvements}),'contained':contained,'review_endpoint_classes':len(ec),'new_endpoint_classes_vs_pool':len(ec-oldclasses),'rook_nontrivial_stars':0,'scope':'All first-step stars fully checked independently; descent endpoint validity and classes checked; depth-2 census and timed solver runs not reproduced.'}
pathlib.Path('/tmp/review15/own/VALIDATION.json').write_text(json.dumps(out,indent=2));pathlib.Path('/tmp/review15/own/STAR_WITNESSES.json').write_text(json.dumps(improving,indent=2));print(out)
