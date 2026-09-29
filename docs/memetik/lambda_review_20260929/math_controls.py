import itertools,json,math
# Exact exhaustive sanity check of packing bound and edge-deletion closure on n<=6.
counts={}
for n in range(2,7):
 pairs=list(itertools.combinations(range(n),2));valid=0;maxedges=0
 for mask in range(1<<len(pairs)):
  rows=[0]*n
  for k,(u,v) in enumerate(pairs):
   if mask>>k&1:rows[u]|=1<<v;rows[v]|=1<<u
  def ok(r):return all((r[u]&r[v]).bit_count()<=2-((r[u]>>v)&1) for u,v in pairs)
  if not ok(rows):continue
  valid+=1;m=mask.bit_count();maxedges=max(maxedges,m)
  assert sum(r.bit_count()**2 for r in rows)<=2*n*(n-1)
  for k,(u,v) in enumerate(pairs):
   if mask>>k&1:
    rr=rows.copy();rr[u]^=1<<v;rr[v]^=1<<u;assert ok(rr)
 counts[n]={'valid':valid,'max_edges':maxedges}
print(json.dumps({'packing_small_graph_checks':counts,'n99_equality':99*19404==1386**2,'edge_count':99*14//2,'single_edge_defect_triangle_moduli':[(693-1)%3,(693+1)%3]},indent=2))
