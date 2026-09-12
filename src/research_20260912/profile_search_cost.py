"""Bounded cost attribution on pinned founders, not a convergence experiment."""
from pathlib import Path
import json
import random
import sys
import time

BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'src/memetic_v2'))
import core
from operators import MoveSource

items=json.loads((BASE/'data/memetic_v2/reference/population64.json').read_text())['candidates']
speeds={r['founder']:r.get('speedup_scoring_only',1) for r in json.loads((BASE/'results/research_20260912/memetic_scoring.json').read_text())['results']}
seen=set(); output=[]
for item in items:
    if item['founder'] in seen:
        continue
    seen.add(item['founder'])
    rows=core.decode_g6(item['g6'])
    for seed in range(3):
        budget=core.Budget(2.0,256)
        source=MoveSource(rows,item['arm'],random.Random(2026091200+seed),budget)
        generation=scoring=0.0
        count=0
        status='MAX32'
        try:
            while count<32:
                start=time.process_time()
                try:
                    move=source.next()
                finally:
                    generation+=time.process_time()-start
                if move is None:
                    status='EXHAUSTED'
                    break
                child=core.apply_move(rows,move[1])
                start=time.process_time()
                core.metrics(child)
                scoring+=time.process_time()-start
                count+=1
        except core.BudgetEnd:
            status='CPU_BUDGET'
        fraction=scoring/(scoring+generation) if scoring+generation else 0
        gain=1/(1-fraction+fraction/speeds[item['founder']])
        output.append({'founder':item['founder'],'arm':item['arm'],'seed':seed,'moves':count,'status':status,
                       'generation_cpu':generation,'scoring_cpu':scoring,'scoring_fraction':fraction,
                       'optimistic_speedup_generation_plus_scoring':gain})
result={'status':'BOUNDED_COST_PROFILE','runs':output,'scope':'Static-parent move stream. Excludes alignment, canonicalization, CP-SAT crossover and worker management. No full-campaign speedup claim.'}
(BASE/'results/research_20260912/search_cost.json').write_text(json.dumps(result,indent=4)+'\n')
print(json.dumps(output,indent=4))
