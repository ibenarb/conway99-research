"""Replay the two-move near endpoint and independently score its full AP neighbourhood."""
import sys,json
from pathlib import Path
run=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(run/'program/experiments/memetik/lambda_profile_1_0_0'))
from support import read,checked,core,witness,Guard,key
from kernel import catalogue
values=[json.loads(line) for line in (run/'jobs/2076_k02/episodes.jsonl').read_text().splitlines()]
ep=values[183]
task=read(run/'jobs/2076_k02/task.json')
proof=witness(task['start'],[p['move'] for p in ep['path']])
assert proof['graph6']==ep['graph6'] and proof['scores']==ep['scores']
rows,scores=checked(ep['graph6'],'lambda')
neighbours=[]
for name,move in catalogue(rows,False,Guard()):
    _,s=checked(core.encode_g6(core.apply_move(rows,move)),'lambda')
    neighbours.append(s)
assert not any(key(s)<key(scores) for s in neighbours)
print(json.dumps({'status':'PASS','path':proof,'neighbours_independently_scored':len(neighbours),
                  'strictly_better_neighbours':0,'equal_key_neighbours':sum(key(s)==key(scores) for s in neighbours)},indent=2))
