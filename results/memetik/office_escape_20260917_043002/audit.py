"""Read-only end-state audit; no full neighborhood replay or all-state score audit."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import sqlite3
import sys
import zipfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--old-run', type=Path, required=True)
    parser.add_argument('--verifier-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.verifier_dir))
    from verify_results import check
    root = args.run_dir
    config = json.loads((root / 'config.json').read_text())
    summary = json.loads((root / 'summary.json').read_text())
    report = {'scope': 'All SQL structure/census records; deterministic sample of graphs and parent transitions. No complete replay of neighborhoods or independent scoring of all states.', 'tasks': {}}
    with zipfile.ZipFile(root / 'Conway99_Escape_Office_0.2.2.pyz') as z:
        manifest = json.loads(z.read('manifest.json'))
        assert manifest == config['manifest']
        for name, digest in manifest['files'].items():
            assert hashlib.sha256(z.read(name)).hexdigest() == digest
        founders = {f['id']: f for f in json.loads(z.read('founders.json'))}
    report['manifest'] = 'PASS'
    for task in config['tasks']:
        name = task['id']
        result = json.loads((root / (name + '.json')).read_text())
        assert summary[name] == result
        with sqlite3.connect('file:' + str((root / (name + '.sqlite')).resolve()) + '?mode=ro', uri=True) as db:
            db.row_factory = sqlite3.Row
            assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
            assert json.loads(db.execute("SELECT value FROM meta WHERE name='result'").fetchone()[0]) == result
            dbconfig = json.loads(db.execute("SELECT value FROM meta WHERE name='config'").fetchone()[0])
            assert dbconfig['limits'] == config['limits'] and dbconfig['task'] == task
            counts = [dict(r) for r in db.execute('SELECT depth,COUNT(*) AS discovered,SUM(expanded) AS expanded FROM nodes GROUP BY depth ORDER BY depth')]
            assert counts == result['depth_counts']
            assert sum(r['discovered'] for r in counts) == result['discovered']
            assert sum(r['expanded'] for r in counts) == result['expanded']
            assert db.execute('SELECT COUNT(*) FROM nodes n LEFT JOIN nodes p ON n.parent=p.id WHERE n.depth>0 AND (p.id IS NULL OR n.depth!=p.depth+1 OR p.id>=n.id)').fetchone()[0] == 0
            assert db.execute('SELECT COUNT(*) FROM nodes WHERE depth=0').fetchone()[0] == 1
            start = db.execute('SELECT * FROM nodes WHERE depth=0').fetchone()
            assert start['g6'] == founders[task['founder']]['graph6']
            assert hashlib.sha256((start['g6']+'\n').encode()).hexdigest() == result['source_sha256']
            first = db.execute('SELECT MIN(depth) FROM nodes WHERE expanded=0').fetchone()[0]
            assert first == result['no_improvement_through_depth'] == result['fully_expanded_through_depth'] + 1
            assert db.execute('SELECT MAX(id) FROM nodes WHERE expanded=1').fetchone()[0] < db.execute('SELECT MIN(id) FROM nodes WHERE expanded=0').fetchone()[0]
            expected = {'4x4','4x6','6x6'} if result['arm']=='omega' else {'apex','rotation'}
            for row in db.execute('SELECT census FROM nodes WHERE expanded=1'):
                census = json.loads(row[0])
                assert set(census) == expected and all(v['complete'] for v in census.values())
            objective = task['objective']
            minimum = db.execute("SELECT MIN(json_extract(metrics, ?)) FROM nodes", ('$.'+objective,)).fetchone()[0]
            assert minimum == json.loads(start['metrics'])[objective]
            ids = [r[0] for r in db.execute('SELECT id FROM nodes ORDER BY id')]
            chosen = sorted(set([ids[0],ids[-1]] + random.Random(20260917).sample(ids,30)))
            for ident in chosen:
                row = db.execute('SELECT * FROM nodes WHERE id=?',(ident,)).fetchone()
                adj, metrics = check(row['g6'], result['arm'])
                assert metrics == json.loads(row['metrics'])
                if row['parent'] is not None:
                    parent = db.execute('SELECT * FROM nodes WHERE id=?',(row['parent'],)).fetchone()
                    before, parentmetrics = check(parent['g6'], result['arm'])
                    assert parentmetrics == json.loads(parent['metrics'])
                    move = json.loads(row['move'])
                    assert move['family'] in expected
                    for i,j in move['deleted']:
                        before[i].remove(j)
                        before[j].remove(i)
                    for i,j in move['added']:
                        assert j not in before[i]
                        before[i].add(j)
                        before[j].add(i)
                    assert before == adj
            entry = {'status': result['status'], 'integrity': 'ok', 'JSON_SQL_summary_match': True, 'depth_counts': counts, 'fully_expanded_through_depth': first-1, 'no_improvement_through_depth': first, 'stored_minimum_objective': minimum, 'sample_ids': chosen, 'sample_arms_metrics_parent_transitions': 'PASS', 'all_expanded_censuses_complete': True}
            if task['founder'] == 'HoG57338':
                old = args.old_run / (name+'.sqlite')
                assert hashlib.sha256(old.read_bytes()).hexdigest() == '809de35c655e4fdd796903a22c4aa0d01671e27d0df91114d3adaee3201985c4'
                db.execute('ATTACH DATABASE ? AS old', ('file:'+str(old.resolve())+'?mode=ro',))
                assert db.execute('SELECT COUNT(*) FROM old.nodes').fetchone()[0] == 99995
                assert db.execute('SELECT COUNT(*) FROM old.nodes o LEFT JOIN nodes n ON n.id=o.id WHERE n.id IS NULL OR n.g6!=o.g6 OR n.parent IS NOT o.parent OR n.depth!=o.depth OR n.move IS NOT o.move OR n.metrics!=o.metrics OR (o.expanded=1 AND (n.expanded!=1 OR n.census!=o.census))').fetchone()[0] == 0
                entry['all_imported_states_and_completed_expansions_preserved'] = True
            report['tasks'][name] = entry
    report['pass'] = True
    args.output.write_text(json.dumps(report,indent=4)+'\n')
    print(json.dumps(report,indent=4))


if __name__ == '__main__':
    main()
