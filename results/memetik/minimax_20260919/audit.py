import json, sqlite3, pathlib, sys, hashlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from verify_results import check
base = pathlib.Path(__file__).parent
report = {'scope': 'Database consistency, all parent labels and census flags; independent graph checks on witness and deterministic sample. Not a complete regeneration of neighborhoods.', 'tasks': {}}
for name in ('B_escape_W2082__bfs_W', 'HoG57338__bfs_F'):
    result = json.loads((base / (name + '.json')).read_text())
    db = sqlite3.connect('file:' + str(base / (name + '.sqlite')) + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    counts = db.execute('SELECT COUNT(*), SUM(closed) FROM nodes').fetchone()
    assert tuple(counts) == (result['discovered'], result['expanded'])
    frontier = dict(db.execute('SELECT id,value,peak FROM nodes WHERE closed=0 ORDER BY peak,value,id LIMIT 1').fetchone())
    assert frontier['peak'] == result['frontier_peak']
    bad = db.execute('SELECT COUNT(*) FROM nodes n LEFT JOIN nodes p ON p.id=n.parent WHERE n.parent IS NOT NULL AND (p.id IS NULL OR p.id>=n.id OR p.closed!=1 OR n.peak!=max(p.peak,n.value))').fetchone()[0]
    assert bad == 0
    census_count = 0
    for row in db.execute('SELECT census FROM nodes WHERE closed=1'):
        c = json.loads(row[0]); assert set(c) == ({'apex','rotation'} if result['arm']=='lambda' else {'4x4','4x6','6x6'})
        assert all(v['complete'] for v in c.values()); census_count += 1
    minimum = db.execute('SELECT MIN(value) FROM nodes').fetchone()[0]
    sample_ids = sorted({1, counts[0], frontier['id']} | {1 + i*(counts[0]-1)//31 for i in range(32)})
    for ident in sample_ids:
        row = db.execute('SELECT g6,metrics,value FROM nodes WHERE id=?',(ident,)).fetchone()
        adj, metrics = check(row['g6'], result['arm']); assert metrics == json.loads(row['metrics']); assert metrics[result['objective']] == row['value']
    if 'witness' in result:
        prior = None
        for entry in result['witness']['path']:
            adj, metrics = check(entry['graph6'],result['arm']); assert metrics == entry['metrics']
            if prior is not None:
                revised = [set(r) for r in prior]
                for i,j in entry['transition']['deleted']:
                    assert j in revised[i]; revised[i].remove(j); revised[j].remove(i)
                for i,j in entry['transition']['added']:
                    assert j not in revised[i]; revised[i].add(j); revised[j].add(i)
                assert revised == adj
            prior = adj
    report['tasks'][name] = {'integrity':'ok','discovered':counts[0],'expanded':counts[1],'frontier':frontier,'minimum_stored_objective':minimum,'all_parent_labels_consistent':True,'complete_census_flags':census_count,'independent_graph_samples':len(sample_ids),'witness_graphs_checked':len(result.get('witness',{}).get('path',[]))}
    print(name, json.dumps(report['tasks'][name]), flush=True)
    db.close()
report['release_sha256'] = hashlib.file_digest((base/'Conway99_Minimax_Office_0.3.0.pyz').open('rb'),'sha256').hexdigest()
assert report['release_sha256']=='8bfc6d9f218e36d70e2194e532d601ab85c266aa4a437ba4007a1203a7454cf4'
(base/'AUDIT.json').write_text(json.dumps(report,indent=4)+'\n')
print('AUDIT_PASS',flush=True)
