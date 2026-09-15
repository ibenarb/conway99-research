"""Independent checks; custom decoding is diagnostic only, never graph6 admission."""
import collections
import contextlib
import hashlib
import importlib.util
import io
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent

def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def measures(adj):
    n = len(adj)
    neighbors = [{j for j in range(n) if adj[i][j]} for i in range(n)]
    hist = collections.Counter(len(neighbors[i] & neighbors[j]) + int(j in neighbors[i]) - 2 for i in range(n) for j in range(i + 1, n))
    linf = max(map(abs, hist))
    return {'order': n, 'edges': sum(j in neighbors[i] for i in range(n) for j in range(i + 1,n)), 'degree_histogram': dict(sorted(collections.Counter(map(len,neighbors)).items())), 'W': sum(v for k,v in hist.items() if k), 'L1': sum(abs(k)*v for k,v in hist.items()), 'F': sum(k*k*v for k,v in hist.items()), 'Linf': linf, 'Nmax': sum(v for k,v in hist.items() if abs(k)==linf), 'lambda_bad_edges': sum(len(neighbors[i]&neighbors[j]) != 1 for i in range(n) for j in neighbors[i] if i<j), 'residual_sum': sum(k*v for k,v in hist.items()), 'residual_histogram': dict(sorted(hist.items()))}

def main():
    verifier = module('conway99_verifier')
    report = {'python':sys.version,'source_sha256':hashlib.sha256((ROOT/'original.txt').read_bytes()).hexdigest(),'candidates':{}}
    for c in json.loads((ROOT/'submission.json').read_text())['candidates']:
        s = c['graph6']
        actual = hashlib.sha256((s+'\n').encode('ascii')).hexdigest()
        hist = {int(k):v for k,v in c['scores']['residual_histogram'].items()}
        linf = max(map(abs,hist))
        standard_order = ((ord(s[1])-63)<<12) | ((ord(s[2])-63)<<6) | (ord(s[3])-63)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            verdict = verifier.verify_candidate(c)
        report['candidates'][c['candidate_id']] = {'arm':c['arm'],'declared_hard_checks':c['hard_checks'],'graph6_characters':len(s),'standard_graph6_order':standard_order,'expected_standard_characters_order99':813,'custom_payload_bits':6*(len(s)-5),'required_bits_order99':4851,'sha256_actual':actual,'sha256_claimed':c['graph6_sha256'],'sha256_matches':actual==c['graph6_sha256'],'supplied_verifier_result':verdict,'declared_histogram_derived':{'pairs':sum(hist.values()),'W':sum(v for k,v in hist.items() if k),'L1':sum(abs(k)*v for k,v in hist.items()),'F':sum(k*k*v for k,v in hist.items()),'Linf':linf,'Nmax':sum(v for k,v in hist.items() if abs(k)==linf),'residual_sum':sum(k*v for k,v in hist.items())},'diagnostic_using_supplied_nonstandard_decoder':measures(verifier.graph6_to_adj(s))}
    n=99
    adj=[[0]*n for _ in range(n)]
    for i in range(n):
        for s in [1,2,4,10,20,40,47]:
            adj[i][(i+s)%n]=adj[(i+s)%n][i]=1
    report['F02_declared_generators_independent_construction']=measures(adj)
    report['F03_tuple_predicate_counterexample']={}
    a=[[0]*2 for _ in range(2)]
    stubs=[0,0]
    valid=all((u:=stubs[i],v:=stubs[i+1],u!=v,not a[u][v],a[u].__setitem__(v,1),a[v].__setitem__(u,1),True)[-1] for i in range(0,len(stubs),2))
    report['F03_tuple_predicate_counterexample']={'valid_returned':valid,'self_loop_inserted':a[0][0]==1}
    fixture=[[0]*3 for _ in range(3)]
    fixture[0][2]=fixture[2][0]=1
    fixture[1][2]=fixture[2][1]=1
    n=3
    A2=[[0]*n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if fixture[i][k]:
                for j in range(k,n):
                    if fixture[k][j]:
                        A2[i][j]+=1
                        if i!=j:A2[j][i]=A2[i][j]
    expected=[[sum(fixture[i][k]*fixture[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    report['verifier_matrix_square_counterexample']={'computed':A2,'expected':expected,'equal':A2==expected}
    (ROOT/'audit.json').write_text(json.dumps(report,indent=4)+'\n')
    print(json.dumps(report,indent=4))

if __name__=='__main__':
    main()
