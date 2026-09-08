#!/usr/bin/env python3
"""Read-only diagnostic for the fixed-K3 structural V3 frontier.

Consumes structural_manifest.json + state.json from a stopped/resumable V3 run.
It does not solve, certify, mutate state, or delete artifacts.
"""
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path

N=32
PAIRS=[(i,j) for i in range(N) for j in range(i+1,N)]

def vname(v:int)->str:
    if 1 <= v <= 496:
        i,j=PAIRS[v-1]; return f"S({i},{j})"
    if 497 <= v <= 992:
        i,j=PAIRS[v-497]; return f"L({i},{j})"
    return f"aux({v})"

def leaves_for(st,cid):
    return [c for c in st['cubes'].values() if c['case_id']==cid and c['status']!='SPLIT']

def case_done(st,cid):
    q=leaves_for(st,cid)
    return bool(q) and all(c['status']=='CERTIFIED' for c in q)

def pct(x,den): return 100.0*x/den if den else 0.0

def feature_report(cases,done,total_weight):
    print('=== FEATURE DISTRIBUTIONS ===')
    for feature,fn in [
        ('s12_13',lambda c:c['s12_13']),
        ('attached_common',lambda c:c['attached_common']),
        ('ordinary_common',lambda c:c['ordinary_common']),
        ('n_type0',lambda c:c['local_types'].count(0)),
        ('n_type1',lambda c:c['local_types'].count(1)),
        ('n_type2',lambda c:c['local_types'].count(2)),
        ('n_type3',lambda c:c['local_types'].count(3)),
        ('n_type4',lambda c:c['local_types'].count(4)),
        ('n_type5',lambda c:c['local_types'].count(5)),
        ('n_type6',lambda c:c['local_types'].count(6)),
    ]:
        vals=defaultdict(lambda:[0,0,0,0]) # easy_n,hard_n,easy_w,hard_w
        for c in cases:
            e=done[c['id']];v=fn(c);w=c['raw_weight']
            z=vals[v]
            if e:z[0]+=1;z[2]+=w
            else:z[1]+=1;z[3]+=w
        print(f'FEATURE {feature}')
        for v,z in sorted(vals.items(),key=lambda kv:str(kv[0])):
            print(f'  value={v} easy={z[0]} hard={z[1]} easy_w={pct(z[2],total_weight):.6f}% hard_w={pct(z[3],total_weight):.6f}%')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run-dir',required=True)
    a=ap.parse_args(); run=Path(a.run_dir)
    mp=run/'structural_manifest.json'; sp=run/'state.json'
    if not mp.exists() or not sp.exists():
        raise SystemExit(f'missing manifest/state under {run}')
    m=json.loads(mp.read_text()); st=json.loads(sp.read_text())
    if st.get('manifest_sha256') != m.get('self_hash_sha256'):
        raise SystemExit('manifest/state hash mismatch')
    cases=m['cases']; byid={c['id']:c for c in cases}; total=m['raw_T_skeleton_total']
    done={c['id']:case_done(st,c['id']) for c in cases}
    easy=[c for c in cases if done[c['id']]]; hard=[c for c in cases if not done[c['id']]]
    ew=sum(c['raw_weight'] for c in easy); hw=sum(c['raw_weight'] for c in hard)
    print('=== V3 FRONTIER AUDIT ===')
    print('run_dir=',run)
    print('campaign_status=',st.get('status'))
    print('root_sha256=',st.get('root_sha256'))
    print('manifest_sha256=',st.get('manifest_sha256'))
    print(f'classes easy={len(easy)} hard={len(hard)} total={len(cases)}')
    print(f'weight easy={pct(ew,total):.6f}% hard={pct(hw,total):.6f}% total_raw={total}')
    print('splits=',st.get('splits'))

    print('=== LOCAL TYPES ===')
    for t in m['local_types']:
        print(f"type={t['id']} N12={t['rep_N12']} N13={t['rep_N13']} intersection={t['intersection']} orbit={t['orbit_size']} swap={t['T_swap_type']}")

    feature_report(cases,done,total)

    print('=== LOCAL TYPE OCCURRENCES ===')
    for label,arr in [('easy',easy),('hard',hard)]:
        cnt=Counter(t for c in arr for t in c['local_types'])
        wcnt=Counter()
        for c in arr:
            for t in c['local_types']:wcnt[t]+=c['raw_weight']
        print(label,'case_occurrences=',dict(sorted(cnt.items())))
        print(label,'weighted_occurrences_pct_of_total=',{t:round(pct(wcnt[t],3*total),6) for t in range(7)})

    print('=== SIMPLE PURE FEATURE VALUES ===')
    features={
        's':lambda c:c['s12_13'], 'a':lambda c:c['attached_common'], 'c':lambda c:c['ordinary_common'],
        **{f'n{t}':(lambda c,t=t:c['local_types'].count(t)) for t in range(7)}
    }
    for name,fn in features.items():
        valmap=defaultdict(list)
        for c in cases: valmap[fn(c)].append(c)
        for v,arr in sorted(valmap.items(),key=lambda kv:str(kv[0])):
            flags={done[c['id']] for c in arr}
            if len(flags)==1:
                lab='EASY_ONLY' if True in flags else 'HARD_ONLY'
                w=sum(c['raw_weight'] for c in arr)
                print(f'{name}={v} {lab} cases={len(arr)} weight={pct(w,total):.6f}%')

    print('=== HARD CASES BY RAW WEIGHT ===')
    for c in sorted(hard,key=lambda x:(-x['raw_weight'],x['id'])):
        q=leaves_for(st,c['id']); sc=Counter(x['status'] for x in q)
        maxd=max((x['depth'] for x in q),default=-1)
        root=st['cubes'].get(c['id'],{})
        lr=root.get('last_solve',{})
        print(f"{c['id']} s={c['s12_13']} types={''.join(map(str,c['local_types']))} a={c['attached_common']} c={c['ordinary_common']} raw_group={c['raw_group_patterns']} raw_weight={c['raw_weight']} pct={pct(c['raw_weight'],total):.6f}% root={root.get('status')} root_kind={lr.get('kind')} root_wall={lr.get('wall')} leaves={len(q)} maxdepth={maxd} statuses={dict(sorted(sc.items()))}")

    print('=== EASY CASES ===')
    for c in sorted(easy,key=lambda x:(x['s12_13'],x['local_types'])):
        root=st['cubes'].get(c['id'],{});lr=root.get('last_solve',{})
        print(f"{c['id']} s={c['s12_13']} types={''.join(map(str,c['local_types']))} a={c['attached_common']} c={c['ordinary_common']} raw_weight={c['raw_weight']} pct={pct(c['raw_weight'],total):.6f}% root_kind={lr.get('kind')} root_wall={lr.get('wall')}")

    print('=== SPLIT VARIABLES IN HARD FRONTIER ===')
    sv=Counter(); bycase=defaultdict(Counter)
    for x in st['cubes'].values():
        cid=x.get('case_id')
        if cid in byid and not done[cid] and x.get('status')=='SPLIT' and x.get('split_var'):
            v=x['split_var']; sv[v]+=1; bycase[cid][v]+=1
    for v,n in sv.most_common(30): print(f'{v} {vname(v)} splits={n}')
    print('unique_split_vars=',len(sv))

    print('=== HARD CASE SPLIT DEPTH SUMMARY ===')
    for c in sorted(hard,key=lambda x:x['id']):
        allc=[x for x in st['cubes'].values() if x['case_id']==c['id']]
        d=Counter(x['depth'] for x in allc if x['status']=='SPLIT')
        print(c['id'],'split_depths=',dict(sorted(d.items())))

    print('=== ANALYSIS_PASS ===')

if __name__=='__main__': main()
