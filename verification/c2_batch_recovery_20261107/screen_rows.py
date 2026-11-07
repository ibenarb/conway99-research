"""Exact pure-row automorphism screen for the current 62 algebraic contracts."""
from pathlib import Path
import json
import sys
P=Path(__file__).resolve().parent
def specification(record):
    m,e=record['M'],record['E']
    delta=[[2-int(i==j)-int((i^1)==j)-int(m[i]==j)-int((e[i]^1)==j) for j in range(12)] for i in range(12)]
    gram=[[9*int(i==j)+1-int(m[i]==j) for j in range(12)] for i in range(12)]
    twisted=[[2-int((i^1)==j)-int(e[i]==j)-int(e[m[i]]==j)-int(m[e[i]]==j) for j in range(12)] for i in range(12)]
    return delta,gram,twisted

inputs=json.loads((P/'row_screen_inputs.json').read_text())
ids={r['id'] for r in inputs['records']}
results=[]
for record in inputs['records']:
    if record['id'] not in ids:continue
    delta,g,k=specification(record)
    colours=[(tuple(delta[r]),g[r][r],k[r][r]) for r in range(12)]
    choices={r:[s for s in range(2,12) if colours[r]==colours[s]] for r in range(2,12)}
    mapping={0:0,1:1};used={0,1};actions=[];nodes=[0]
    def visit():
        nodes[0]+=1
        assert nodes[0]<1000000,'Explicit screen budget reached'
        if len(mapping)==12:
            action=[mapping[r] for r in range(12)]
            assert all(delta[r]==delta[action[r]] for r in range(12))
            assert all(g[r][s]==g[action[r]][action[s]] and k[r][s]==k[action[r]][action[s]] for r in range(12) for s in range(12))
            actions.append(action);return
        r=min((r for r in choices if r not in mapping),key=lambda r:sum(s not in used for s in choices[r]))
        for s in choices[r]:
            if s in used:continue
            if not all(g[r][t]==g[s][u] and g[t][r]==g[u][s] and k[r][t]==k[s][u] and k[t][r]==k[u][s] for t,u in mapping.items()):continue
            mapping[r]=s;used.add(s);visit();used.remove(s);del mapping[r]
    visit()
    results.append(dict(case=record['id'],group_order=len(actions),backtrack_nodes=nodes[0],actions=actions))
answer=dict(status='COMPLETE',cases=len(results),scope='Pure row actions fixing boundary rows pointwise and preserving exact degree targets plus full Gram/twisted matrices. This does not enumerate coupled row/column actions or prove complete domain equality beyond identical defining targets.',results=results)
(P/'PURE_ROW_SCREEN_PORTABLE.json').write_text(json.dumps(answer,indent=4)+'\n')
print(json.dumps(dict(cases=len(results),orders={str(order):sum(x['group_order']==order for x in results) for order in sorted(set(x['group_order'] for x in results))},larger=[x['case'] for x in results if x['group_order']>2])))
