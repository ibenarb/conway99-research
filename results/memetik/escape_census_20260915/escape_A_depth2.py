"""Exhaust all length-two paths from A_legacy in the frozen existing families."""
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

def branch(index):
    starters=json.loads((ROOT/'escape_A_neighbors.json').read_text())
    config=json.loads((ROOT/'escape_office_result/config.json').read_text())
    parent=next(x for x in config['founders'] if x['id']=='A_legacy')
    first=starters[index];rows=decode_g6(first['graph6']);budget=Budget(seconds=3600,evaluations=10**12)
    result={'first_index':index,'first_trade':{'deleted':first['deleted'],'added':first['added']},'first_metrics':first['metrics'],'families':{},'best':{},'improving_paths':dict.fromkeys(['W','L1','F','Linf'],0),'neutral_paths':dict.fromkeys(['W','L1','F','Linf'],0),'root_returns':0}
    for family in ['4x4','4x6','6x6']:
        count=0;complete=False
        try:
            for move in omega_moves(rows,family,random.Random(20260915),budget):
                budget.check();child=apply_move(rows,move);validate(child,'omega');m=metrics(child);count+=1
                is_root=child==decode_g6(parent['graph6'])
                result['root_returns']+=is_root
                for objective in result['improving_paths']:
                    if key(m,objective)==key(parent['metrics'],objective):result['neutral_paths'][objective]+=1
                    if key(m,objective)<key(parent['metrics'],objective):
                        result['improving_paths'][objective]+=1
                        previous=result['best'].get(objective)
                        if previous is None or key(m,objective)<key(previous['metrics'],objective):
                            assert all(m[k]==v for k,v in independent(child).items())
                            result['best'][objective]={'metrics':m,'graph6':encode_g6(child),'second_trade':{'family':family,'deleted':move[0],'added':move[1]}}
            complete=True
        except BudgetEnd as error:
            result['budget_stop']=str(error)
        result['families'][family]={'trades':count,'complete':complete}
    return result

if __name__=='__main__':
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(branch,range(3)))
    complete=all(f['complete'] for r in results for f in r['families'].values())
    totals={k:sum(r['improving_paths'][k] for r in results) for k in ['W','L1','F','Linf']}
    report={'scope':'All length-two sequences in existing 4x4,4x6,6x6 families; labelled graphs, frozen Omega frame. Not all conceivable arm-preserving moves.','complete':complete,'improving_paths':totals,'branches':results}
    (ROOT/'escape_A_depth2_result.json').write_text(json.dumps(report,indent=4)+'\n')
    print(json.dumps({'complete':complete,'improving_paths':totals,'branch_counts':[r['families'] for r in results],'best_scores':[{k:{s:v['metrics'][s] for s in ['W','L1','F','Linf','Nmax']} for k,v in r['best'].items()} for r in results]}))
