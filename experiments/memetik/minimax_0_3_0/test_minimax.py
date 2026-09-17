"""Targeted algorithm, seed, process-kill and resume tests."""
import gzip
import json
import multiprocessing
import os
from pathlib import Path
import signal
import sqlite3
import sys
import tempfile
import time

from minimax import connect, front, relax, seed_database, run_worker, getmeta, putmeta

ROOT = Path(__file__).parent
REPORT = {}


def require(condition, text):
    if not condition:
        raise AssertionError(text)


def toy_test(directory):
    path = directory/'toy.sqlite'
    db = connect(path)
    values = {'r': 0, 'a': 9, 'b': 2, 'c': 2, 'd': 2, 'z': -1}
    graph = {'r': ['a', 'b'], 'a': ['r', 'z'], 'b': ['r', 'c'], 'c': ['b', 'd'], 'd': ['c', 'z'], 'z': ['a', 'd']}
    db.execute('INSERT INTO nodes(g6,value,metrics,peak) VALUES(?,?,?,?)', ('r',0,'{"W":0}',0))
    db.commit()
    while (node := front(db)) is not None:
        for child in graph[node['g6']]:
            relax(db,node,child,{'W': values[child]}, {}, 'W')
        db.execute('UPDATE nodes SET closed=1 WHERE id=?',(node['id'],))
        db.commit()
    actual = {r['g6']: r['peak'] for r in db.execute('SELECT * FROM nodes')}
    expected = {}
    for threshold in sorted(set(values.values()) | {0}):
        if threshold < 0:
            continue
        reachable = {'r'}
        queue = ['r']
        for parent in queue:
            for child in graph[parent]:
                if values[child] <= threshold and child not in reachable:
                    reachable.add(child)
                    queue.append(child)
        for name in reachable:
            expected.setdefault(name, threshold)
    require(actual == expected, 'Compare against independent threshold reachability')
    require(actual['z'] == 2, 'Long lower-barrier path must beat short barrier-9 path')
    db.execute("UPDATE nodes SET closed=0,peak=9 WHERE g6='z'")
    parent = db.execute("SELECT * FROM nodes WHERE g6='d'").fetchone()
    require(relax(db,parent,'z',{'W':-1},{},'W') == (0,1), 'Previously known larger label must decrease')
    db.commit()
    db.execute('BEGIN')
    relax(db,parent,'temporary',{'W':3},{},'W')
    db.rollback()
    require(db.execute("SELECT COUNT(*) FROM nodes WHERE g6='temporary'").fetchone()[0] == 0, 'Unfinished expansion rollback')
    db.close()
    return {'independent_threshold_reference': True, 'lower_barrier_longer_path': True, 'decreased_known_label': True, 'transaction_rollback': True}


def data_fingerprint(db):
    import hashlib
    h = hashlib.sha256()
    for row in db.execute('SELECT * FROM nodes ORDER BY id'):
        h.update(json.dumps(list(row),sort_keys=True).encode())
    return h.hexdigest()


def main():
    directory = Path(tempfile.mkdtemp(prefix='minimax_tests_', dir=str(ROOT)))
    REPORT['toy'] = toy_test(directory)
    seed_reports = {}
    for name in ('HoG57338__bfs_F','B_escape_W2082__bfs_W'):
        seed = json.loads(gzip.decompress((ROOT/(name+'.seed.json.gz')).read_bytes()))
        target = directory/name
        target.mkdir()
        config = {'deadline_epoch':time.time()+60,'test':True}
        status = seed_database(target/(name+'.sqlite'),seed,config)
        (target/(name+'.json')).write_text(json.dumps(status))
        db = connect(target/(name+'.sqlite'))
        require(db.execute('PRAGMA integrity_check').fetchone()[0]=='ok', 'Seed SQLite')
        require(status['expanded']==len(seed['inside']), 'All old internal nodes closed without rerunning generators')
        require(status['frontier_peak']==seed['strict_threshold'], 'Expected next minimax height')
        before = data_fingerprint(db)
        db.close()
        seed_reports[name] = {'inside':status['expanded'],'discovered':status['discovered'],'frontier_peak':status['frontier_peak'],'fingerprint':before}
        if name.startswith('HoG'):
            context = multiprocessing.get_context('fork')
            process = context.Process(target=run_worker,args=(str(target),seed,config))
            process.start()
            deadline = time.monotonic()+20
            killed = False
            while time.monotonic()<deadline and process.is_alive():
                journal = target/(name+'.sqlite-journal')
                if journal.exists() and journal.stat().st_size>0:
                    os.kill(process.pid,signal.SIGKILL)
                    killed=True
                    break
                time.sleep(0.02)
            if not killed:
                process.terminate()
            process.join(10)
            require(killed,'Kill during a real SQLite expansion')
            # Opening with the normal connection recovers the interrupted journal.
            db = connect(target/(name+'.sqlite'))
            require(db.execute('PRAGMA integrity_check').fetchone()[0]=='ok','Recovery after SIGKILL')
            require(data_fingerprint(db)==before,'No partial expansion committed')
            db.close()
            resumed = context.Process(target=run_worker,args=(str(target),seed,config))
            resumed.start()
            deadline = time.monotonic()+35
            progress=False
            while time.monotonic()<deadline and resumed.is_alive():
                with sqlite3.connect('file:'+str(target/(name+'.sqlite'))+'?mode=ro',uri=True) as observer:
                    count=observer.execute('SELECT COUNT(*) FROM nodes WHERE closed=1').fetchone()[0]
                if count>len(seed['inside']):
                    progress=True
                    os.kill(resumed.pid,signal.SIGTERM)
                    break
                time.sleep(0.1)
            if resumed.is_alive() and not progress:
                resumed.terminate()
            resumed.join(15)
            require(not resumed.is_alive() and progress,'Resume must commit real new progress')
            result=json.loads((target/(name+'.json')).read_text())
            require(result['status']=='INTERRUPTED','Graceful stop after resumed progress')
            db=connect(target/(name+'.sqlite'))
            require(db.execute('PRAGMA integrity_check').fetchone()[0]=='ok','Final recovery integrity')
            require(getmeta(db,'counts')['expanded']==db.execute('SELECT COUNT(*) FROM nodes WHERE closed=1').fetchone()[0], 'Exact checkpoint counts')
            db.close()
            REPORT['process_kill_resume']={'SIGKILL_during_expansion':True,'exact_rollback':True,'resume_makes_progress':True,'graceful_SIGTERM':True,'expanded_after_resume':result['expanded']}
    REPORT['seeds']=seed_reports
    REPORT['pass']=True
    (ROOT/'test_report.json').write_text(json.dumps(REPORT,indent=4)+'\n')
    print(json.dumps(REPORT,indent=4))


if __name__=='__main__':
    main()
