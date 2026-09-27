"""Aggregate the per-job episode histograms already contained in the flat D/F/O package:
fraction of P episodes (perturbation + exact steepest descent) that end exactly at the parent
labelled state ('returned'), or in the parent's isomorphism class, per campaign and job."""
import json,glob,collections,re
out={}
for pref in ('F','O'):
    files=sorted(glob.glob(f'{pref}__runs__comparison__tasks__*__result.json'))
    agg=collections.Counter(); rows=[]
    for f in files:
        r=json.load(open(f)); h=r['histogram']; job=re.search(r'tasks__(.*)__result',f).group(1)
        ret=h['returned']; iso=h['isomorphic_return']; n=sum(ret.values())
        pl=h['perturb_length']; short=sum(v for k,v in pl.items() if int(k)<=4); mid=sum(v for k,v in pl.items() if 5<=int(k)<=12); lng=sum(v for k,v in pl.items() if int(k)>=13)
        stops=h['stop']
        rows.append(dict(job=job,episodes=n,returned=ret.get('True',0),returned_frac=round(ret.get('True',0)/n,4),
                         iso_return=iso.get('True',0),iso_return_frac=round(iso.get('True',0)/n,4),
                         perturb_2_4=short,perturb_5_12=mid,perturb_13_32=lng,stops=stops,
                         median_descent=sorted([int(k) for k,v in h['descent_length'].items() for _ in range(v)])[n//2],
                         best_W=r['best']['scores']['W'],best_L1=r['best']['scores']['L1']))
        agg['episodes']+=n; agg['returned']+=ret.get('True',0); agg['iso']+=iso.get('True',0); agg['short']+=short; agg['mid']+=mid; agg['long']+=lng
    out[pref]=dict(jobs=rows,total=dict(agg),returned_frac=round(agg['returned']/agg['episodes'],4),iso_return_frac=round(agg['iso']/agg['episodes'],4))
    print(pref,'episodes',agg['episodes'],'returned exactly to parent',agg['returned'],round(agg['returned']/agg['episodes'],3),'isomorphic return',agg['iso'],round(agg['iso']/agg['episodes'],3),'perturb 2-4/5-12/13-32',agg['short'],agg['mid'],agg['long'])
    for r in rows: print('  ',r['job'],'n',r['episodes'],'ret',r['returned_frac'],'iso',r['iso_return_frac'],'medDesc',r['median_descent'],'best',(r['best_W'],r['best_L1']),r['stops'])
json.dump(out,open('/home/claude/review/episode_histograms.json','w'),indent=1)
