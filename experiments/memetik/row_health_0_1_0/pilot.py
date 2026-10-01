#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, hashlib, os, random, time
from dataclasses import dataclass, asdict
from itertools import combinations
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

VERSION = '0.1.0'
N = 99
H0 = 15
OUTER = tuple((a,b) for a,b in combinations(range(14),2) if b-a != 7)

def vertices(bits):
    while bits:
        z = bits & -bits; yield z.bit_length()-1; bits ^= z

def decode_g6(text):
    text = text.strip().removeprefix('>>graph6<<')
    vals = [ord(c)-63 for c in text]
    if vals[0] < 63: n, off = vals[0], 1
    else: n, off = (vals[1]<<12)+(vals[2]<<6)+vals[3], 4
    rows=[0]*n; pos=0
    for j in range(1,n):
        for i in range(j):
            if vals[off+pos//6] & (1 << (5-pos%6)):
                rows[i] |= 1<<j; rows[j] |= 1<<i
            pos += 1
    return tuple(rows)

def encode_g6(rows):
    n=len(rows); pref=chr(n+63) if n<63 else '~'+''.join(chr(((n>>s)&63)+63) for s in (12,6,0))
    out=[]; v=0; k=0
    for j in range(1,n):
        for i in range(j):
            v=(v<<1)|((rows[i]>>j)&1); k+=1
            if k==6: out.append(chr(v+63)); v=k=0
    if k: out.append(chr((v<<(6-k))+63))
    return pref+''.join(out)

def sha_rows(rows): return hashlib.sha256(encode_g6(rows).encode()).hexdigest()

def common(rows,i,j): return (rows[i]&rows[j]).bit_count()
def healthy(rows,i,j): return common(rows,i,j)+((rows[i]>>j)&1)==2

def W(rows):
    return sum(not healthy(rows,i,j) for i in range(N) for j in range(i))

def row_bad(rows,i): return sum(not healthy(rows,i,j) for j in range(N) if j!=i)

def all_healthy_pairs(rows):
    return frozenset((i,j) if i<j else (j,i) for i in range(N) for j in range(i+1,N) if healthy(rows,i,j))

def validate(rows):
    if len(rows)!=N: raise ValueError('expected 99 vertices')
    for i,r in enumerate(rows):
        if r>>N or r&(1<<i) or r.bit_count()!=14: raise ValueError(f'degree/diagonal violation row {i}')
        for j in vertices(r):
            if not rows[j]&(1<<i): raise ValueError('asymmetry')

def frame_ok(rows):
    if rows[0] != sum(1<<i for i in range(1,15)): return False
    expected_inner=[set() for _ in range(84)]
    for u,(a,b) in enumerate(OUTER): expected_inner[u]={a+1,b+1}
    for u in range(84):
        v=H0+u
        if {j for j in range(15) if rows[v]&(1<<j)} != expected_inner[u]: return False
    for a in range(14):
        want={0,1+(a+7)%14} | {H0+u for u,p in enumerate(OUTER) if a in p}
        got={j for j in vertices(rows[1+a])}
        if got != want: return False
    return True

def changed_pairs(before,after):
    return {(i,j) for i in range(N) for j in range(i+1,N) if ((before[i]>>j)&1)!=((after[i]>>j)&1)}

def protection_ok(rows, protected): return all(healthy(rows,i,j) for i,j in protected)

def apply_toggle(rows, rem, add):
    r=list(rows)
    for a,b in rem:
        if a>b: a,b=b,a
        if not (r[a]>>b)&1: return None
        r[a]^=1<<b; r[b]^=1<<a
    for a,b in add:
        if a>b: a,b=b,a
        if (r[a]>>b)&1: return None
        r[a]^=1<<b; r[b]^=1<<a
    return tuple(r)

def random_switch(rows,rng,target=None):
    hv=list(range(H0,N)); edges=[]
    for a in hv:
        for b in vertices(rows[a] & ~((1<<H0)-1)):
            if a<b: edges.append((a,b))
    for _ in range(80):
        e1=rng.choice(edges); e2=rng.choice(edges)
        if len(set(e1+e2))!=4: continue
        if target is not None and target not in set(e1+e2) and rng.random()<0.8: continue
        a,b=e1; c,d=e2
        options=[((a,c),(b,d)),((a,d),(b,c))]
        rng.shuffle(options)
        for z1,z2 in options:
            z1=tuple(sorted(z1)); z2=tuple(sorted(z2))
            if z1==z2 or ((rows[z1[0]]>>z1[1])&1) or ((rows[z2[0]]>>z2[1])&1): continue
            return (tuple(sorted((tuple(sorted(e1)),tuple(sorted(e2))))), tuple(sorted((z1,z2))))
    return None

def move_once(rows,rng,target,protected,frozen,atomic2=False):
    sw1=random_switch(rows,rng,target)
    if not sw1: return None
    candidate=apply_toggle(rows,*sw1)
    if candidate is None: return None
    touched=changed_pairs(rows,candidate)
    if frozen & touched: return None
    if atomic2:
        sw2=random_switch(candidate,rng,target)
        if not sw2: return None
        candidate2=apply_toggle(candidate,*sw2)
        if candidate2 is None: return None
        touched=changed_pairs(rows,candidate2)
        if frozen & touched: return None
        candidate=candidate2
    if not protection_ok(candidate,protected): return None
    validate(candidate)
    if not frame_ok(candidate): raise RuntimeError('frame changed')
    return candidate

@dataclass
class State:
    rows: tuple
    protected: frozenset
    frozen: frozenset
    completed: tuple
    order: tuple
    backtracks: int=0
    attempts: int=0

def complete_row(state,target,rng,steps):
    best=state.rows; best_key=(row_bad(best,target),W(best)); noimp=0
    for t in range(steps):
        use2=(t%7==6)
        cand=move_once(best,rng,target,state.protected,state.frozen,atomic2=use2)
        state.attempts += 1
        if cand is None: continue
        key=(row_bad(cand,target),W(cand))
        accept = key < best_key or (key[0] <= best_key[0]+1 and rng.random()<0.015)
        if accept:
            best,best_key=cand,key; noimp=0
        else: noimp+=1
        if best_key[0]==0: break
        if noimp>5000: break
    if row_bad(best,target)!=0: return None
    prot=set(state.protected)
    prot.update((min(target,j),max(target,j)) for j in range(N) if j!=target)
    frozen=set(state.frozen)
    return best,frozenset(prot),frozenset(frozen)

def lane(task,outdir,checkpoint_s=60):
    rng=random.Random(task['seed']); rows=decode_g6(Path(task['source']).read_text())
    validate(rows)
    if not frame_ok(rows): return {'lane':task['id'],'status':'FRAME_INCOMPATIBLE','source':task['source']}
    mode=task['mode']
    protected=all_healthy_pairs(rows) if mode=='strict_initial' else frozenset()
    frozen=frozenset()
    order=list(range(H0,N)); rng.shuffle(order)
    cp_path=Path(outdir)/f"checkpoint_{task['id']}.json"
    if cp_path.exists():
        cp=json.loads(cp_path.read_text())
        rows=decode_g6(cp['g6']); validate(rows)
        completed=tuple(cp.get('completed',()))
        order=tuple(cp.get('order',order))
        prot=set(protected)
        for v in completed: prot.update((min(v,j),max(v,j)) for j in range(N) if j!=v)
        fr=set()
        if mode=='frozen_rows':
            for v in completed: fr.update((min(v,j),max(v,j)) for j in range(H0,N) if j!=v)
        st=State(rows,frozenset(prot),frozenset(fr),completed,order,int(cp.get('backtracks',0)),int(cp.get('attempts',0)))
    else:
        st=State(rows,protected,frozen,tuple(),tuple(order))
    t0=time.time(); deadline=t0+task['seconds']; last_cp=0
    stack=[]; depth_best=0
    while time.time()<deadline and len(st.completed)<84:
        target=st.order[len(st.completed)]
        before=State(st.rows,st.protected,st.frozen,st.completed,st.order,st.backtracks,st.attempts)
        got=complete_row(st,target,rng,task['steps_per_row'])
        if got:
            rows2,prot2,froz2=got
            if mode=='frozen_rows':
                fr=set(froz2)
                fr.update((min(target,j),max(target,j)) for j in range(H0,N) if j!=target)
                froz2=frozenset(fr)
            stack.append(before)
            st=State(rows2,prot2,froz2,st.completed+(target,),st.order,st.backtracks,st.attempts)
            depth_best=max(depth_best,len(st.completed))
        else:
            if stack and st.backtracks < task['backtrack_limit']:
                prev=stack.pop(); st=prev; st.backtracks += 1
                tail=list(st.order[len(st.completed):]); rng.shuffle(tail)
                st.order=st.order[:len(st.completed)]+tuple(tail)
            else: break
        if time.time()-last_cp>=checkpoint_s:
            cp={'version':VERSION,'task':task,'depth':len(st.completed),'depth_best':depth_best,'W':W(st.rows),'completed':st.completed,'order':st.order,'backtracks':st.backtracks,'attempts':st.attempts,'g6':encode_g6(st.rows),'rows_sha256':sha_rows(st.rows),'ts':time.time()}
            p=Path(outdir)/f"checkpoint_{task['id']}.json"; tmp=p.with_suffix('.tmp'); tmp.write_text(json.dumps(cp,indent=2)); os.replace(tmp,p); last_cp=time.time()
    result={'lane':task['id'],'status':'COMPLETE' if len(st.completed)==84 else ('TIME_BUDGET' if time.time()>=deadline else 'SEARCH_STUCK'),'mode':mode,'source':task['source'],'seed':task['seed'],'depth':len(st.completed),'depth_best':depth_best,'W':W(st.rows),'backtracks':st.backtracks,'attempts':st.attempts,'protected':len(st.protected),'frozen':len(st.frozen),'elapsed_s':time.time()-t0,'rows_sha256':sha_rows(st.rows),'g6':encode_g6(st.rows)}
    Path(outdir,f"result_{task['id']}.json").write_text(json.dumps(result,indent=2)); return result

def baseline(task,outdir):
    rng=random.Random(task['seed']); rows=decode_g6(Path(task['source']).read_text()); validate(rows)
    if not frame_ok(rows): return {'lane':task['id'],'status':'FRAME_INCOMPATIBLE'}
    best=rows; bw=W(rows); t0=time.time(); deadline=t0+task['seconds']; attempts=0
    while time.time()<deadline:
        cand=move_once(best,rng,None,frozenset(),frozenset(),atomic2=(attempts%7==6)); attempts+=1
        if cand is None: continue
        w=W(cand)
        if w<bw or (w<=bw+2 and rng.random()<0.002): best,bw=cand,w
    r={'lane':task['id'],'status':'TIME_BUDGET','mode':'baseline_W','source':task['source'],'seed':task['seed'],'depth':0,'W':bw,'attempts':attempts,'elapsed_s':time.time()-t0,'rows_sha256':sha_rows(best),'g6':encode_g6(best)}
    Path(outdir,f"result_{task['id']}.json").write_text(json.dumps(r,indent=2)); return r

def preflight(cfg):
    base=Path(cfg['repo_root'])
    resolved=[]; errors=[]
    for s in cfg['sources']:
        p=base/s['path'] if s.get('path') else None
        if s['id']=='M' and (p is None or not p.exists()):
            errors.append('M_SOURCE_MISSING')
            continue
        if p is None or not p.exists(): errors.append('MISSING:'+s['id']); continue
        rows=decode_g6(p.read_text()); validate(rows)
        if not frame_ok(rows): errors.append('FRAME_INCOMPATIBLE:'+s['id']); continue
        resolved.append({'id':s['id'],'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'W':W(rows)})
    return resolved,errors

def run(cfg_path,outdir):
    cfg=json.loads(Path(cfg_path).read_text()); out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    sources,errors=preflight(cfg)
    (out/'preflight.json').write_text(json.dumps({'version':VERSION,'sources':sources,'errors':errors},indent=2))
    if 'M_SOURCE_MISSING' in errors: raise SystemExit('PRECHECK FAIL: candidate M source unresolved; run discover_m.py')
    if errors: raise SystemExit('PRECHECK FAIL: '+','.join(errors))
    src=[s for s in sources if s['id']!='M']+[s for s in sources if s['id']=='M']
    tasks=[]; modes=['targeted','targeted','targeted','targeted','strict_initial','strict_initial','frozen_rows','baseline_W']
    wall=cfg['wall_seconds'];
    for i,mode in enumerate(modes):
        s=src[i%len(src)]
        tasks.append({'id':f'{i:02d}_{mode}','mode':mode,'source':s['path'],'seed':cfg['seed']+i*1009,'seconds':wall,'steps_per_row':cfg['steps_per_row'],'backtrack_limit':cfg['backtrack_limit']})
    (out/'tasks.json').write_text(json.dumps(tasks,indent=2))
    start=time.time(); last=0; results=[]
    with ProcessPoolExecutor(max_workers=8) as ex:
        fut={ex.submit(baseline if t['mode']=='baseline_W' else lane,t,str(out)):t for t in tasks}
        while fut:
            done=[]
            for f,t in list(fut.items()):
                if f.done(): results.append(f.result()); done.append(f)
            for f in done: fut.pop(f,None)
            if time.time()-last>=600:
                cps=[]
                for p in out.glob('checkpoint_*.json'):
                    try: cps.append(json.loads(p.read_text()))
                    except Exception: pass
                d=max([c.get('depth_best',0) for c in cps]+[r.get('depth_best',r.get('depth',0)) for r in results]+[0]); w=min([c.get('W',10**9) for c in cps]+[r.get('W',10**9) for r in results]+[10**9])
                print(f'ROWHEALTH d={d}/84 W={w if w<10**9 else "-"} live={len(fut)} done={len(results)}',flush=True); last=time.time()
            if fut: time.sleep(2)
    summary={'version':VERSION,'elapsed_s':time.time()-start,'results':results}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))

def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('preflight'); p.add_argument('config')
    r=sp.add_parser('run'); r.add_argument('config'); r.add_argument('outdir')
    a=ap.parse_args()
    if a.cmd=='preflight':
        cfg=json.loads(Path(a.config).read_text()); print(json.dumps(dict(zip(('sources','errors'),preflight(cfg))),indent=2))
    else: run(a.config,a.outdir)
if __name__=='__main__': main()
