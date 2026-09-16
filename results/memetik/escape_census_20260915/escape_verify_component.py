"""Replay all component edges and verify its cube certificate."""
import itertools
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent/'escape_build'))
from core import apply_move, decode_g6, encode_g6, validate
from runner import independent, key
ROOT=pathlib.Path(__file__).resolve().parent

def main():
    report=json.loads((ROOT/'escape_A_component_result.json').read_text())
    assert report['complete'] and report['nodes_discovered']==report['nodes_expanded']==8
    nodes={n['graph6']:n for n in report['nodes']};root=report['nodes'][0]['graph6'];rows=decode_g6(root)
    deltas=[tuple(a^b for a,b in zip(rows,decode_g6(g))) for g in nodes[root]['edges']]
    assert len(deltas)==3
    labels={}
    for bits in itertools.product([0,1],repeat=3):
        child=list(rows)
        for flag,delta in zip(bits,deltas):
            if flag:child=[a^b for a,b in zip(child,delta)]
        graph=encode_g6(child);assert graph in nodes;labels[graph]=''.join(map(str,bits))
    assert len(labels)==8
    for g,node in nodes.items():
        validate(decode_g6(g),'omega')
        assert all(node['metrics'][k]==v for k,v in independent(decode_g6(g)).items())
        assert len(node['edges'])==3 and all(f['complete'] for f in node['families'].values())
        for target,move in node['edges'].items():
            child=apply_move(decode_g6(g),(tuple(map(tuple,move['deleted'])),tuple(map(tuple,move['added']))))
            assert child==decode_g6(target)
            assert sum(a!=b for a,b in zip(labels[g],labels[target]))==1
        if g!=root:
            assert all(key(node['metrics'],o)>key(nodes[root]['metrics'],o) for o in ['W','L1','F','Linf'])
    print('PASS: eight-node closed enumerated component, cube edges, unique best root in all four criteria. Completeness scope is the frozen generator families.')

if __name__=='__main__':main()
