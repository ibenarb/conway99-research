"""Independent post-run audit. Standard library only; never imports search code.

Usage: python audit.py EXTRACTED_RUN OUTPUT_DIRECTORY [ARCHIVE]
Validates all hashes and reported candidates; SQLite integrity/counts but not
all 1.49 million archive entries' graph invariants or canonical certificates.
"""
import collections
import datetime
import hashlib
import json
from pathlib import Path
import sqlite3
import statistics
import sys


def read(path):
    return json.loads(path.read_text())


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def key(scores,target):
    fields = {'W':('W','L1'),'L1':('L1',),'F':('F',),'Linf':('Linf','Nmax','L1')}[target]
    return tuple(scores[f] for f in fields)


CACHE = {}


def check_graph(text):
    if text in CACHE:
        return CACHE[text]
    values = [ord(c)-63 for c in text]
    assert values[0]==63 and all(0<=x<64 for x in values)
    n = values[1]*4096+values[2]*64+values[3]
    assert n==99 and len(values)==4+(n*(n-1)//2+5)//6
    bits = [(x>>i)&1 for x in values[4:] for i in range(5,-1,-1)]
    neighbors = [set() for _ in range(n)]
    k = 0
    for v in range(n):
        for u in range(v):
            if bits[k]:
                neighbors[u].add(v)
                neighbors[v].add(u)
            k += 1
    assert not any(bits[k:])
    assert all(len(s)==14 for s in neighbors)
    residuals = collections.Counter()
    for v in range(n):
        for u in range(v):
            common = len(neighbors[u].intersection(neighbors[v]))
            adjacent = v in neighbors[u]
            if adjacent:
                assert common==1
            residuals[common+int(adjacent)-2] += 1
    maximum = max(map(abs,residuals))
    scores = {'W':sum(c for r,c in residuals.items() if r),'L1':sum(abs(r)*c for r,c in residuals.items()),
              'F':sum(r*r*c for r,c in residuals.items()),'Linf':maximum,
              'Nmax':sum(c for r,c in residuals.items() if abs(r)==maximum)}
    CACHE[text] = scores
    return scores


def validate_items(value):
    if isinstance(value,dict):
        if 'graph6' in value and 'scores' in value:
            assert check_graph(value['graph6'])==value['scores']
            if 'state' in value:
                assert hashlib.sha256(value['graph6'].encode()).hexdigest()==value['state']
        for child in value.values():
            validate_items(child)
    elif isinstance(value,list):
        for child in value:
            validate_items(child)


def main(root,out,archive=None):
    out.mkdir(parents=True,exist_ok=True)
    expected = 'c9856a662d4b6438b1edc42f930a3b77c3d60dd2f15b7b167a0901893c32b382'
    if archive:
        assert digest(archive)==expected
    exported = read(root/'export_manifest.json')['files']
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name!='export_manifest.json'}
    assert actual==set(exported)
    for name,checksum in exported.items():
        assert digest(root/name)==checksum,name
    signature = read(root/'fingerprint.json')
    assert digest(root/'manifest.json')==signature['manifest_sha256']
    for name,checksum in signature['files'].items():
        assert digest(root/'bundle'/name)==checksum
    manifest = read(root/'manifest.json')
    evaluation = read(root/'evaluation.json')
    assert len(manifest['jobs'])==192 and manifest['workers']==18
    budget = read(root/'budget.json')
    assert budget['revision']==0 and budget['per_job_cpu_seconds']==3600
    assert not list(root.glob('tasks/*/active.json'))
    assert read(root/'comparison_timing.json')['clean']
    data,receipts,archive_counts = {},{},{}
    founders_hashes,seeds = set(),{}
    for task in [manifest['controls']]+manifest['jobs']:
        d = root/'tasks'/task['id']
        assert read(d/'task.json')==task
        receipt = read(d/'receipt.json')
        result = read(d/'result.json')
        for filename,field in [('task.json','task_sha256'),('result.json','result_sha256')]:
            assert digest(d/filename)==receipt[field]
        assert receipt['exit_code']==0 and len(receipt['sessions'])==1
        assert abs(sum(s['cpu_seconds'] for s in receipt['sessions'])-receipt['cpu_seconds'])<1e-8
        assert receipt['budget_cpu_seconds']==receipt['cpu_seconds'] and receipt['closed_reserve_cpu_seconds']==0
        receipts[task['id']] = receipt
        if task['kind']=='controls':
            assert result['status']=='CONTROLS_PASS' and receipt['cpu_seconds']<=3600
            continue
        assert receipt['status']==result['status']=='COMPLETE'
        assert 3595<=receipt['cpu_seconds']<=3600 and result['endpoint_cpu_seconds']==3600
        for filename,field in [('checkpoint.json','checkpoint_sha256'),('archive.sqlite','archive_sha256')]:
            assert digest(d/filename)==receipt[field]
        wrapper = read(d/'checkpoint.json')
        state = wrapper['state']
        assert hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest()==wrapper['sha256']
        assert state['task_sha256']==receipt['task_sha256']
        assert result==evaluation['results'][task['id']]
        validate_items(task['founders'])
        validate_items(result)
        validate_items(state)
        curves = result['curves']
        assert curves[0]['cpu']==0 and all(0<=p['cpu']<=3600 for p in curves)
        assert all(a['cpu']<=b['cpu'] and key(a['scores'],task['target'])>key(b['scores'],task['target']) for a,b in zip(curves,curves[1:]))
        assert curves[-1]['graph6']==result['best']['graph6']
        for mark in (600,1800,3600):
            point = next(p for p in reversed(curves) if p['cpu']<=mark)
            assert result['milestones'][str(mark)]['graph6']==point['graph6']
        db = sqlite3.connect('file:'+str((d/'archive.sqlite').resolve())+'?mode=ro&immutable=1',uri=True)
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        count = db.execute('SELECT COUNT(*) FROM graphs').fetchone()[0]
        endpoints = db.execute('SELECT COUNT(*) FROM graphs WHERE endpoint=1').fetchone()[0]
        assert count==result['archive_classes'] and endpoints==result['endpoint_classes']
        db.close()
        archive_counts[task['id']] = count
        founders_hashes.add(hashlib.sha256(json.dumps(task['founders'],sort_keys=True).encode()).hexdigest())
        seeds.setdefault(task['replicate'],set()).add(task['seed'])
        data[task['id']] = {'target':task['target'],'variant':task['variant'],'replicate':task['replicate'],
                           'seed':task['seed'],'best':result['best'],'observed_best':result['observed_best'],
                           'curves':curves,'milestones':result['milestones'],'cpu_seconds':receipt['cpu_seconds'],
                           'episodes':result['episodes'],'iterations':result['iterations'],'restarts':result['restarts'],
                           'histogram':result['histogram'],'adopted_moves':result['adopted_moves'],
                           'evaluated_moves':result['evaluated_moves'],'archive_classes':count,'endpoint_classes':endpoints}
    assert len(founders_hashes)==1 and len(seeds)==12 and all(len(s)==1 for s in seeds.values())
    assert len(set.union(*seeds.values()))==12
    assert {(t['variant'],t['target'],t['replicate']) for t in manifest['jobs']}=={(v,t,i) for v in ('B0','P','T','TC') for t in ('W','L1','F','Linf') for i in range(12)}
    comparisons = []
    for original in evaluation['groups']:
        target,v,c,mark = (original[x] for x in ('target','variant','comparator','milestone_cpu'))
        pairs = [[data[f'{a}--lambda-{target}-{i:02d}']['milestones'][str(mark)]['scores'] for a in (c,v)] for i in range(12)]
        wins = sum(key(b,target)<key(a,target) for a,b in pairs)
        losses = sum(key(b,target)>key(a,target) for a,b in pairs)
        assert pairs==original['paired_scores']
        assert (wins,12-wins-losses,losses)==(original['wins'],original['ties'],original['losses'])
        comparisons.append(original)
    total = sum(r['cpu_seconds'] for r in receipts.values() if r['kind']=='compare')
    assert abs(total/3600-evaluation['actual_comparison_cpu_hours'])<1e-9
    groups = []
    for target in ('W','L1','F','Linf'):
        for variant in ('B0','P','T','TC'):
            jobs = [data[f'{variant}--lambda-{target}-{i:02d}'] for i in range(12)]
            scores = [j['best']['scores'] for j in jobs]
            winners = sorted(jobs,key=lambda j:key(j['best']['scores'],target))
            groups.append({'target':target,'variant':variant,'scores_by_seed':scores,
                           'best_scores':winners[0]['best']['scores'],'best_job':winners[0]['replicate'],
                           'distinct_endpoint_certificates':len({j['best']['class'] for j in jobs}),
                           'median_each_score':{m:statistics.median(s[m] for s in scores) for m in ('W','L1','F','Linf','Nmax')},
                           'median_episodes':statistics.median(j['episodes'] for j in jobs),
                           'median_iterations':statistics.median(j['iterations'] for j in jobs),
                           'restarts_total':sum(j['restarts'] for j in jobs),
                           'last_active_improvement_cpu_by_seed':[j['curves'][-1]['cpu'] for j in jobs],
                           'milestone_median_each_score':{str(mark):{m:statistics.median(j['milestones'][str(mark)]['scores'][m] for j in jobs) for m in ('W','L1','F','Linf','Nmax')} for mark in (600,1800,3600)}})
    records = {}
    for target in ('W','L1','F','Linf'):
        candidates = [(j['observed_best'][target],j['variant'],j['target'],j['replicate']) for j in data.values()]
        item,v,t,i = min(candidates,key=lambda x:key(x[0]['scores'],target))
        records[target] = {'candidate':item,'variant':v,'active_target':t,'replicate':i}
    statuses = [json.loads(line) for line in (root/'controller.log').read_text().splitlines() if line.startswith('{"utc"')]
    first,last = statuses[1],statuses[-1]
    real_elapsed = (datetime.datetime.fromisoformat(last['utc'].replace('Z','+00:00'))-datetime.datetime.fromisoformat(first['utc'].replace('Z','+00:00'))).total_seconds()
    monotonic = read(root/'comparison_timing.json')['wall_seconds']
    report = {'status':'HASH_RECEIPT_GRAPH_AND_PAIRING_PASS_WITH_TIMING_CAVEAT','archive_sha256':expected,
              'hashed_export_files':len(exported),'frozen_source_files':len(signature['files']),
              'jobs':192,'unique_reported_labelled_graphs_independently_checked':len(CACHE),
              'graph_check':'new graph6 decoder and set-intersection verifier; n99 degree14 edge CN1 and all five scores',
              'sqlite_integrity_checked':192,'archive_rows_across_jobs':sum(archive_counts.values()),
              'not_rechecked':'all archived graph rows and canonical certificate correctness; no full trajectory replay',
              'comparison_cpu_hours':total/3600,'controls_cpu_seconds':receipts['controls']['cpu_seconds'],
              'per_job_cpu_range':[min(d['cpu_seconds'] for d in data.values()),max(d['cpu_seconds'] for d in data.values())],
              'comparison_monotonic_seconds':monotonic,'comparison_utc_elapsed_seconds':real_elapsed,
              'utc_minus_monotonic_seconds':real_elapsed-monotonic,'cpu_per_monotonic_second':total/monotonic,
              'timing_caveat':'UTC and monotonic durations disagree; CPU/monotonic exceeds 18 slots. Cause not established; do not infer throughput or speedup from that clock.',
              'comparisons':comparisons,'groups':groups,'observed_records_all_targets':records}
    for name,value in [('AUDIT.json',report),('PAIRED_RESULTS.json',data),('RECEIPTS.json',receipts)]:
        (out/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('comparisons','groups','observed_records_all_targets')},indent=2))


if __name__=='__main__':
    main(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]) if len(sys.argv)>3 else None)
