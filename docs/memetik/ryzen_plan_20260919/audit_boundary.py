import collections, gzip, hashlib, json, pathlib, sys, zipfile
from verify_results import check
p = pathlib.Path(sys.argv[1]); report = {'archive':p.name,'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'scope':'All supplied boundary graph scores and arm conditions; parent graphs checked, but no independent complete boundary regeneration or catalogue membership proof.' ,'tasks':{}}
with zipfile.ZipFile(p) as z:
    for name in z.namelist():
        raw=z.read(name); d=json.loads(gzip.decompress(raw)); graphs=set(); parents={}; hist=collections.Counter()
        for item in d['boundary']:
            g=item['graph6']; assert g not in graphs; graphs.add(g)
            _,m=check(g,d['arm']); assert m==item['metrics']; hist[m[d['objective']]]+=1
            parent=item['reached_from']
            if parent not in parents: parents[parent]=check(parent,d['arm'])[1]
            assert parents[parent][d['objective']]<d['strict_threshold']
        assert len(graphs)==d['boundary_states']; assert min(hist)==d['minimum_boundary']==d['strict_threshold']
        assert d['necessary_barrier_at_least']==min(hist)-d['baseline']
        report['tasks'][d['task']]={'file_sha256':hashlib.sha256(raw).hexdigest(),'graphs_checked':len(graphs),'different_parents_checked':len(parents),'minimum':min(hist),'histogram':dict(sorted(hist.items())),'claimed_previous_independently_rechecked':d['independently_rechecked']}
        print(d['task'],len(graphs),'PASS',flush=True)
pathlib.Path(__file__).with_name('BOUNDARY_AUDIT.json').write_text(json.dumps(report,indent=4)+'\n')
