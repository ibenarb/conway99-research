"""Bounded component closure with all existing Omega generator families."""
import concurrent.futures
import hashlib
import json
import pathlib
import random
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent/'escape_build'))
from core import Budget, BudgetEnd, apply_move, decode_g6, encode_g6, metrics, validate
from operators import omega_moves
from runner import independent, key
ROOT=pathlib.Path(__file__).resolve().parent

def inspect_graph(g6):
    rows=decode_g6(g6);budget=Budget(seconds=120,evaluations=10**12);edges={};families={}
    for family in ['4x4','4x6','6x6']:
        count=0;complete=False
        try:
            for move in omega_moves(rows,family,random.Random(20260915),budget):
                budget.check();child=apply_move(rows,move);validate(child,'omega');target=encode_g6(child);count+=1
                edges[target]={'family':family,'deleted':move[0],'added':move[1]}
            complete=True
        except BudgetEnd:
            pass
        families[family]={'trades':count,'complete':complete}
    m=metrics(rows);assert all(m[k]==v for k,v in independent(rows).items())
    return {'graph6':g6,'sha256':hashlib.sha256((g6+'\n').encode()).hexdigest(),'metrics':m,'families':families,'edges':edges}

if __name__=='__main__':
    config=json.loads((ROOT/'escape_office_result/config.json').read_text());founder=next(x for x in config['founders'] if x['id']=='A_legacy');start=founder['graph6'];seen={start};pending=[start];nodes={}
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
        while pending and len(seen)<=64:
            batch=pending[:3];pending=pending[3:]
            for node in pool.map(inspect_graph,batch):
                nodes[node['graph6']]=node
                for target in node['edges']:
                    if target not in seen:seen.add(target);pending.append(target)
    complete=not pending and all(f['complete'] for n in nodes.values() for f in n['families'].values())
    improvements={k:sum(key(n['metrics'],k)<key(founder['metrics'],k) for n in nodes.values()) for k in ['W','L1','F','Linf']}
    report={'scope':'Labelled fixed-frame component under the existing 4x4,4x6,6x6 families only. No claim for all Omega-preserving moves.','complete':complete,'nodes_discovered':len(seen),'nodes_expanded':len(nodes),'improving_nodes':improvements,'nodes':list(nodes.values())}
    (ROOT/'escape_A_component_result.json').write_text(json.dumps(report,indent=4)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='nodes'}))
