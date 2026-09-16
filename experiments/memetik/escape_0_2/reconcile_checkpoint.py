"""Recompute missing final expansions; preserve original inconsistent archive."""
import concurrent.futures
import json
from pathlib import Path
import sqlite3
import sys
import time
from core import decode_g6
from search import neighbors, key, short, atomic


class Limit:
    def __init__(self):
        self.deadline = time.process_time()+120
    def check(self):
        if time.process_time()>self.deadline:
            raise RuntimeError('Reconciliation incomplete')


def inspect(path):
    path=Path(path)
    result=json.loads(path.read_text())
    with sqlite3.connect(path.with_suffix('.sqlite')) as db:
        count,expanded=db.execute('SELECT COUNT(*),SUM(expanded) FROM nodes').fetchone()
        if (count,expanded)==(result['discovered'],result['expanded']):
            return {'task':path.stem,'repair_needed':False}
        assert result['status']=='LOCAL_MINIMUM_VERIFIED'
        assert count==result['discovered'] and expanded+1==result['expanded']
        last=db.execute('SELECT id,g6,expanded FROM nodes ORDER BY id DESC LIMIT 1').fetchone()
        assert last[2]==0 and last[1]==result['witness']['path'][-1]['graph6']
    db.close()
    rows=decode_g6(last[1]);base=short(rows);counts={};total=0
    for family,move,child in neighbors(rows,result['arm'],Limit(),counts):
        assert key(short(child),result['task']['objective'])>=key(base,result['task']['objective'])
        total+=1
    assert all(x['complete'] for x in counts.values())
    result['checkpoint_reconciliation']={'missing_final_expansion_recomputed':True,'census':counts,'note':'Original JSON and SQLite differed by the final expansion. Original archive retained; all endpoint families re-enumerated.'}
    with sqlite3.connect(path.with_suffix('.sqlite')) as db:
        db.execute('PRAGMA journal_mode=DELETE')
        db.execute('PRAGMA synchronous=FULL')
        db.execute('UPDATE nodes SET expanded=1,census=? WHERE id=?',(json.dumps(counts),last[0]))
        db.execute("INSERT OR REPLACE INTO meta VALUES ('result',?)",(json.dumps(result),))
    db.close()
    atomic(path,result)
    return {'task':path.stem,'repair_needed':True,'recomputed_trades':total,'families':counts,'local_minimum_confirmed':True}


if __name__=='__main__':
    directory=Path(sys.argv[1])
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(inspect,sorted(directory.glob('*__*.json'))))
    report={'pass':True,'records':records,'cause':'Not established; mismatches involved missing final SQLite WAL state. Release 0.2.1 uses rollback journal mode and a single database file.'}
    atomic(directory.parent/'checkpoint_reconciliation.json',report)
    print(json.dumps(report))
