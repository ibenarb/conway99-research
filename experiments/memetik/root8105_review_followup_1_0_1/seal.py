"""One self-contained final receipt; live SQLite is not the sole result carrier."""
import bootstrap
import json
from pathlib import Path
from runtime import atomic, digest, get


def seal(con, path, summary):
    results = []
    for r in con.execute('SELECT root,payload,digest FROM results ORDER BY root'):
        value = json.loads(r['payload'])
        if digest(value) != r['digest'] or value['state'] != 'COMPLETE':
            raise ValueError('cannot seal corrupt/non-complete result')
        results.append({'root': r['root'], 'digest': r['digest'], 'result': value})
    roots = [dict(r) for r in con.execute('SELECT * FROM roots ORDER BY id')]
    attempts = [dict(r) for r in con.execute('SELECT * FROM attempts ORDER BY id')]
    sessions = [dict(r) for r in con.execute('SELECT * FROM sessions ORDER BY id')]
    complete = all(r['state'] == 'DONE' for r in roots)
    if complete and (len(results) != len(roots) or any(r['ended'] is None for r in attempts + sessions)):
        raise ValueError('complete receipt requires closed attempts and sessions')
    payload = {'run_id': get(con, 'run_id'), 'fingerprint': get(con, 'fingerprint'),
               'model': get(con, 'model'), 'complete': complete, 'roots': roots,
               'attempts': attempts, 'sessions': sessions, 'results': results, 'summary': summary,
               'purpose': 'self-contained audit/result evidence; never silently repairs a live ledger'}
    envelope = {'sha256': digest(payload), 'payload': payload}
    atomic(Path(path), envelope)
    verify(path)
    return envelope['sha256']


def verify(path):
    envelope = json.loads(Path(path).read_text())
    payload = envelope['payload']
    if digest(payload) != envelope['sha256']:
        raise ValueError('final receipt digest mismatch')
    for r in payload['results']:
        if digest(r['result']) != r['digest'] or r['result']['root'] != r['root']:
            raise ValueError('final result digest/identity mismatch')
    if payload['complete'] and len(payload['roots']) != len(payload['results']):
        raise ValueError('final receipt omits completed results')
    return payload


def regression():
    import sqlite3, tempfile
    from runtime import schema, put
    with tempfile.TemporaryDirectory(prefix='final-receipt-') as directory:
        con=sqlite3.connect(':memory:');con.row_factory=sqlite3.Row;schema(con)
        for k,v in {'run_id':'TEST_ONLY','fingerprint':{},'model':'TEST_ONLY'}.items():put(con,k,v)
        result={'root':1,'state':'COMPLETE','counts':{'1':{'width':7}}}
        con.execute("INSERT INTO roots(id,spec,state) VALUES(1,'{}','DONE')")
        # Use the actual results schema, including its creation timestamp.
        cols=[r[1] for r in con.execute('PRAGMA table_info(results)')]
        values={'root':1,'payload':json.dumps(result),'digest':digest(result),'created':1.0}
        con.execute('INSERT INTO results('+','.join(cols)+') VALUES('+','.join('?' for _ in cols)+')',[values.get(k) for k in cols])
        path=Path(directory)/'final.json';seal(con,path,{'status':'COMPLETE'})
        con.execute('DELETE FROM results');con.execute("UPDATE roots SET state='RUNNING'")
        assert verify(path)['results'][0]['result']==result
        data=json.loads(path.read_text());data['payload']['results'][0]['result']['counts']['1']['width']=8
        path.write_text(json.dumps(data))
        try:verify(path)
        except ValueError:pass
        else:raise AssertionError('tampered receipt accepted')
    return {'status':'PASS','stale_live_database_does_not_erase_sealed_result':True,'tamper_rejected':True}
