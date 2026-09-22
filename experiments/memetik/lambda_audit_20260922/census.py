"""Read-only complete neighbour census of audited records, no search campaign."""
from pathlib import Path
import sys
import json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lambda_compare_0_2_0'))
import bootstrap
from common import core, checked
from kernel import catalogue, Scorer
from search import key


class Guard:
    def check(self):
        pass


def main(directory):
    audit = json.loads((directory/'AUDIT.json').read_text())
    jobs = json.loads((directory/'PAIRED_RESULTS.json').read_text())
    candidates = {f'observed_{t}':r['candidate'] for t,r in audit['observed_records_all_targets'].items()}
    candidates['active_W'] = min((j['best'] for j in jobs.values() if j['target']=='W'),key=lambda x:key(x['scores'],'W'))
    candidates['TC_W'] = jobs['TC--lambda-W-00']['best']
    report = {}
    for label,item in candidates.items():
        rows,scores = checked(item['graph6'],'lambda')
        scorer = Scorer(rows)
        counts = {}
        witnesses = {}
        for operator,move in catalogue(rows,True,Guard()):
            child,values = scorer.evaluate(move)
            core.validate(child,'lambda')
            counts.setdefault(operator,{'moves':0,'improving':dict.fromkeys(('W','L1','F','Linf'),0)})
            counts[operator]['moves'] += 1
            for target in ('W','L1','F','Linf'):
                counts[operator]['improving'][target] += key(values,target)<key(scores,target)
                if key(values,target)<key(scores,target) and (target not in witnesses or key(values,target)<key(witnesses[target]['scores'],target)):
                    text = core.encode_g6(child)
                    assert checked(text,'lambda')[1]==values
                    witnesses[target] = {'operator':operator,'move':move,'scores':values,'graph6':text,
                                         'scope':'post-run one-step diagnostic; not part of campaign endpoint'}
        report[label] = {'scores':scores,'catalogue':counts,'graph6':item['graph6'],'improving_witnesses':witnesses}
    (directory/'RECORD_CENSUS.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:{x:y for x,y in v.items() if x!='graph6'} for k,v in report.items()},indent=2))


if __name__=='__main__':
    main(Path(sys.argv[1]))
