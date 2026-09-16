"""Verify the saved census witnesses and task accounting; standard library only."""
import hashlib
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent/'escape_build'))
from core import apply_move, decode_g6, metrics, validate
from runner import independent, summarize
ROOT=pathlib.Path(__file__).resolve().parent

def main():
    folder=ROOT/'escape_office_result';config=json.loads((folder/'config.json').read_text());items=config['founders'];founders={x['id']:x for x in items};results={};witnesses=0;unique=set()
    for path in folder.glob('*__*.json'):
        data=json.loads(path.read_text());parent=founders[data['founder']];rows=decode_g6(parent['graph6']);validate(rows,parent['arm'])
        assert hashlib.sha256((parent['graph6']+'\n').encode()).hexdigest()==data['source_sha256']
        assert json.loads(json.dumps(metrics(rows)))==data['baseline']==parent['metrics']
        assert data['complete'] and data['status']=='EXHAUSTED'
        for objective in ['W','L1','F','Linf']:
            assert sum(data[k][objective] for k in ['better','equal','worse'])==data['valid_trades']
        for witness in data['best_witness'].values():
            child=apply_move(rows,(tuple(map(tuple,witness['deleted'])),tuple(map(tuple,witness['added']))));validate(child,parent['arm'])
            assert child==decode_g6(witness['graph6'])
            assert hashlib.sha256((witness['graph6']+'\n').encode()).hexdigest()==witness['sha256']
            assert json.loads(json.dumps(metrics(child)))==witness['metrics']
            assert all(witness['metrics'][k]==v for k,v in independent(child).items())
            witnesses+=1;unique.add(witness['sha256'])
        results[data['task']]=data
    assert len(results)==20
    assert summarize(items,results)==json.loads((folder/'summary.json').read_text())
    print(json.dumps({'tasks':len(results),'witness_records':witnesses,'distinct_graph6':len(unique),'valid_trades':sum(x['valid_trades'] for x in results.values())}))

if __name__=='__main__':main()
