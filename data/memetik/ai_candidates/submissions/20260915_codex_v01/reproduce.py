import json, pathlib, subprocess, sys, time
root=pathlib.Path(__file__).resolve().parent
outdir=root/'reproduction';outdir.mkdir(exist_ok=True)
report=[]
for c in json.loads((root/'submission.json').read_text())['candidates']:
    args=c['generator_args'].copy(); args[args.index('--out')+1]=str(outdir/(c['candidate_id']+'.json'))
    run=subprocess.run([sys.executable,str(root/'generate.py'),*args],capture_output=True,text=True,timeout=30)
    assert run.returncode==0,run.stderr
    result=json.loads((outdir/(c['candidate_id']+'.json')).read_text())
    same=result.get('graph6')==c['graph6'] and result.get('graph6_sha256')==c['graph6_sha256']
    report.append({'id':c['candidate_id'],'byte_identical':same,'result':result})
    assert same,c['candidate_id']
(root/'reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'reproduced':len(report),'byte_identical':all(r['byte_identical'] for r in report),'wall_seconds_sum':sum(r['result']['runtime']['wall_seconds'] for r in report)}))
