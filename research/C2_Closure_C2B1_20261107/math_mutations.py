from pathlib import Path
from functools import lru_cache
from copy import deepcopy
import json,gzip,shutil,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
import mathematical_audit as audit
original=audit.components
@lru_cache(None)
def complete_cached(degrees,expected,pairs,flip):
    return original(degrees,expected,pairs,flip)
def exact_cache(degrees,expected,pairs,flip):
    return complete_cached(tuple(degrees),expected,tuple(pairs),tuple(flip))
audit.components=exact_cache
O=P/'math_mutations';O.mkdir(exist_ok=False);root=O/'fixture';root.mkdir()
for name in ['record.json','representatives.json','model.txt','boundaries.json.gz','block_actions.txt','s2_action.txt']:
    shutil.copyfile(P/'bundle_20_v2'/name,root/name)
base={f.name:f.read_bytes() for f in root.iterdir()}
assert audit.validate(root)['boundary_count']==36288
results=[]
def test(label,mutate,expected):
    for name,data in base.items():(root/name).write_bytes(data)
    mutate()
    try:audit.validate(root)
    except ValueError as error:
        assert expected in str(error),(label,str(error))
        results.append(dict(test=label,rejection=str(error)))
        print(json.dumps(results[-1]),flush=True)
    else:raise RuntimeError('Accepted '+label)
def model_change(which):
    lines=(root/'model.txt').read_text().splitlines()
    if which=='matrix':
        row=lines[2].split();row[0]=str(int(row[0])+1);lines[2]=' '.join(row)
    else:
        lines[26]=str(int(lines[26])-1);lines[27]=' '.join(lines[27].split()[1:])
    (root/'model.txt').write_text('\n'.join(lines)+'\n')
def package_change(kind):
    with gzip.open(root/'boundaries.json.gz','rt') as f:package=json.load(f)
    if kind=='missing':package['coverage'].pop()
    if kind=='duplicate':package['coverage'][1]=package['coverage'][0]
    if kind=='group':package['group'][0][0],package['group'][0][2]=package['group'][0][2],package['group'][0][0]
    if kind=='transport':package['coverage'][0][2]=(package['coverage'][0][2]+1)%len(package['representatives'])
    with gzip.open(root/'boundaries.json.gz','wt') as f:json.dump(package,f)
def wrong_actions():
    tokens=(root/'block_actions.txt').read_text().split();tokens[1],tokens[2]=tokens[2],tokens[1];(root/'block_actions.txt').write_text(' '.join(tokens))
def bad_s2():
    tokens=(root/'s2_action.txt').read_text().split();tokens[0]=tokens[1];(root/'s2_action.txt').write_text(' '.join(tokens))
test('original matrix altered',lambda:model_change('matrix'),'Original matrix mismatch')
test('one valid domain value removed',lambda:model_change('domain'),'Incomplete or incorrect domain')
test('composed action altered',wrong_actions,'Wrong composed block actions')
test('invalid S2 permutation',bad_s2,'Invalid permutation')
test('invalid old coupled action',lambda:package_change('group'),'Boundary pair moved')
test('coverage entry removed',lambda:package_change('missing'),'Incomplete boundary coverage count')
test('duplicate ordered coverage pair',lambda:package_change('duplicate'),'Duplicate covered ordered pair')
test('wrong explicit transport',lambda:package_change('transport'),'Incorrect coupled transport')
def nonminimal():
    with gzip.open(root/'boundaries.json.gz','rt') as f:pkg=json.load(f)
    group=pkg['group'];pairs=[(a,b) for a in range(12) for b in range(a+1,12) if a^1!=b]
    chosen=None
    for index,(a,b) in enumerate(pkg['representatives']):
        for q in group:
            cp=[pairs.index(tuple(sorted((q[u],q[v])))) for u,v in pairs]
            new=(audit.image(a,cp),audit.image(b,cp))
            if q[0]==1:new=new[::-1]
            if new[0]<new[1] and new>(a,b):chosen=(index,q,new);break
        if chosen:break
    assert chosen
    index,q,new=chosen;inverse=[q.index(i) for i in range(12)]
    pkg['representatives'][index]=list(new)
    for row in pkg['coverage']:
        if row[2]==index:
            g=group[row[3]];h=[g[inverse[i]] for i in range(12)];row[3]=group.index(h)
    with gzip.open(root/'boundaries.json.gz','wt') as f:json.dump(pkg,f)
    lines=(root/'model.txt').read_text().splitlines();assert int(lines[50])==36288
    lines[51+index]=' '.join(map(str,new));(root/'model.txt').write_text('\n'.join(lines)+'\n')
test('valid transports but nonminimal representative',nonminimal,'Nonminimal old representative')
for name,data in base.items():(root/name).write_bytes(data)
result=dict(status='PASS',tests=results,scope='Actual mathematical validator; complete components enumeration memoised by exact arguments inside test process only; no fabricated domains and no closure claim')
(P/'MATH_MUTATIONS.json').write_text(json.dumps(result,indent=4)+'\n');print(json.dumps(result))
