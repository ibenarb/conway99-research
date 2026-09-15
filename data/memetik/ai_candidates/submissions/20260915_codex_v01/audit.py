"""Independent intake audit. Usage: python audit.py --reference-root REPOSITORY_ROOT"""
import argparse, collections, hashlib, itertools, json, pathlib
import networkx as nx
import pynauty
from audit_helpers import validate
ROOT=pathlib.Path(__file__).resolve().parent

def certificate(g):
    return pynauty.certificate(pynauty.Graph(len(g),adjacency_dict={i:list(g[i]) for i in g}))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reference-root',type=pathlib.Path,required=True);args=parser.parse_args()
    records=json.loads((ROOT/'submission.json').read_text())['candidates']
    manifest=json.loads((ROOT/'reference_manifest.json').read_text())
    refs={};reference_results=[]
    for item in manifest:
        raw=(args.reference_root/item['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==item['sha256']
        g=nx.from_graph6_bytes(raw.strip());cert=certificate(g)
        refs.setdefault(cert,[]).append(item['path'])
        reference_results.append({**item,'certificate_sha256':hashlib.sha256(cert).hexdigest()})
    report={};certs={}
    for c in records:
        name=c['candidate_id'];r,adj=validate(ROOT/(name+'.g6'),c['arm'])
        assert r['sha256']==c['graph6_sha256']
        hist=collections.Counter(len(adj[i]&adj[j])+int(j in adj[i])-2 for i in range(99) for j in range(i+1,99))
        r['residual_histogram']={str(k):v for k,v in sorted(hist.items())}
        for k in ['W','L1','F','Linf','Nmax','lambda_bad_edges','residual_histogram']:assert r[k]==c['scores'][k],(name,k)
        if c['arm']=='omega':assert c['omega_frame']['canonical_to_graph6']==list(range(99))
        g=nx.Graph({i:adj[i] for i in range(99)});cert=certificate(g);certs[name]=cert
        _,size,exponent,orbits,count=pynauty.autgrp(pynauty.Graph(99,adjacency_dict={i:list(adj[i]) for i in range(99)}))
        r.update(connected=nx.is_connected(g),automorphism_order=size*10**exponent,vertex_orbits=count,certificate_sha256=hashlib.sha256(cert).hexdigest(),reference_duplicates=refs.get(cert,[]))
        report[name]=r
    for name in report:report[name]['submission_duplicates']=[other for other in certs if other!=name and certs[other]==certs[name]]
    result={'scope':'18 explicitly enumerated reference files; no claim about unlisted archives or basin novelty','candidates':report,'references':reference_results,'versions':{'networkx':nx.__version__,'pynauty':pynauty.__version__}}
    (ROOT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'PASS':len(report),'reference_files':len(manifest),'reference_unique_certificates':len(refs),'duplicates':sum(bool(r['reference_duplicates'] or r['submission_duplicates']) for r in report.values()),'automorphism_orders':{k:r['automorphism_order'] for k,r in report.items()}}))
if __name__=='__main__':main()
