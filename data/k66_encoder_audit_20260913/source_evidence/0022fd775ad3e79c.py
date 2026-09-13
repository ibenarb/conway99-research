"""Prepare all-root carrier bridges and exact RUP coverage; no production run."""
import argparse
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]

def prepare(source, root, output):
    models = json.loads((source/'analysis/profile_models.json').read_text())
    model = models[root]
    plan = json.loads((source/'analysis/coupled_certification_plan.json').read_text())['roots'][root]
    filename = 'coupled_pilot_original_0.json' if root == 'v4_09333' else f'coupled_{root}_original_0.json'
    tree = json.loads((source/'analysis'/filename).read_text())
    assert tree['status'] == 'EXACT_UNSAT' and tree['initial_excluded'] == []
    raw = (source/plan['cnf_path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == plan['cnf_sha256']
    lines = raw.decode().splitlines()
    nvars, original_count = map(int,lines[0].split()[2:])
    assert original_count == len(lines)-1
    n = len(model['profiles'])
    clauses = {}
    edges = {}
    for index, line in enumerate(lines[1:],1):
        parts = line.split()
        if len(parts) == 3:
            a,b = map(int,parts[:2])
            if -n <= a < 0 and -n <= b < 0:
                edges[tuple(sorted((-a,-b)))] = index
                clauses[index] = [a,b]
    classes = [[p['variable'] for p in model['profiles'] if p['z'][i] == 2] for i in range(12)]
    bridges, added, class_ids = [], [], []
    coords = [(i,j) for i in range(14) for j in range(i,14)]
    block_map = {coords[b['index']]:b for b in model['constraint_blocks'] if b['kind']=='gram'}
    for i, group in enumerate(classes):
        Q = range(4*(i//4),4*(i//4)+4)
        assert model['G'][i][i]-sum(model['G'][i][j] for j in Q if j != i) == 4
        for p in model['profiles']:
            z = p['z']
            assert z[i]**2-sum(z[i]*z[j] for j in Q if j != i) == 4*int(z[i]==2)
            if z[i] == 2:
                assert p['capacity'] == 1
        blocks = [block_map[tuple(sorted((i,j)))] for j in Q]
        added.append(group)
        class_ids.append(original_count+len(added))
        bridges.append({'id':f'carrier_cover_{i+1:02d}','kind':'AT_LEAST_ONE', 'assumptions':[-v for v in group],
                        'lemma':group,'four_original_gram_blocks':blocks})
    for coord, group in enumerate(classes):
        for t,a in enumerate(group):
            for b in group[t+1:]:
                pair = tuple(sorted((a,b)))
                if pair not in edges:
                    added.append([-a,-b])
                    edges[pair] = original_count+len(added)
                    bridges.append({'id':f'carrier_amo_{a:04d}_{b:04d}', 'kind':'AT_MOST_ONE',
                                    'assumptions':[a,b], 'lemma':[-a,-b], 'coordinate':coord,
                                    'four_original_gram_blocks':bridges[coord]['four_original_gram_blocks']})
    leaf_ids = {}
    for job in plan['leaf_jobs']:
        added.append([-v for v in job['assumptions']])
        leaf_ids[tuple(job['assumptions'])] = original_count+len(added)
    for offset,clause in enumerate(added,original_count+1):
        clauses[offset] = clause
    last_id = original_count+len(added)
    proof = []
    visited = set()
    def prove(index):
        nonlocal last_id
        assert index not in visited
        visited.add(index)
        node = tree['nodes'][index]
        selected = node['selected']
        if node['kind'] != 'BRANCH':
            return leaf_ids[tuple(selected)]
        children = {c['variable']:prove(c['node']) for c in node['children']}
        assert set(children) == set(node['candidates'])
        hints = []
        for v in classes[node['coordinate']]:
            if v in children:
                hints.append(children[v])
            else:
                pair = next(tuple(sorted((v,s))) for s in selected if tuple(sorted((v,s))) in edges)
                hints.append(edges[pair])
        hints.append(class_ids[node['coordinate']])
        assigned = set(selected)
        contradicted = False
        for h in hints:
            cl = clauses[h]
            assert not any(v in assigned for v in cl)
            free = [v for v in cl if -v not in assigned]
            assert len(free) <= 1
            if not free:
                contradicted = True
                break
            assigned.add(free[0])
        assert contradicted
        last_id += 1
        clauses[last_id] = [-v for v in selected]
        proof.append(f'{last_id} ' + ' '.join(map(str,clauses[last_id]))+' 0 '+' '.join(map(str,hints))+' 0\n')
        return last_id
    final = prove(tree['entry_node'])
    assert not clauses[final] and len(visited) == len(tree['nodes'])
    proof_text = ''.join(proof)
    (output/f'{root}_coverage.lrat').write_text(proof_text)
    result = {'root':root, 'status':'EXACT_RUP_COVERAGE_CHECKED_BRIDGES_AND_LEAVES_OWED',
              'base_cnf_sha256':plan['cnf_sha256'], 'base_cnf_path_in_input_bundle':plan['cnf_path'],
              'bridge_count':len(bridges), 'leaf_count':len(plan['leaf_jobs']),
              'coverage_RUP_additions':len(proof), 'coverage_proof_sha256':hashlib.sha256(proof_text.encode()).hexdigest(),
              'bridges':bridges, 'leaves':plan['leaf_jobs'], 'coverage_added_clauses':added,
              'note':'Coverage assumes all listed bridge and leaf clauses. Does not certify these assumptions.'}
    (output/f'{root}_plan.json').write_text(json.dumps(result,indent=4)+'\n')
    return {k:v for k,v in result.items() if k not in ('bridges','leaves','coverage_added_clauses')}

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('source',type=Path)
    args=parser.parse_args()
    output=BASE/'results/research_20260912/k66'
    output.mkdir(parents=True,exist_ok=True)
    result=[prepare(args.source,root,output) for root in ('v4_09322','v4_09323','v4_09332','v4_09333')]
    (output/'summary.json').write_text(json.dumps(result,indent=4)+'\n')
    print(json.dumps(result,indent=4))
