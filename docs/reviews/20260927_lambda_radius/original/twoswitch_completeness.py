"""Independent completeness test at the 2-switch level: enumerate ALL double-edge swaps
(remove ab,cd; add ac,bd or ad,bc) of the start graph that keep it simple, 14-regular and
lambda=1 on every edge (i.e. stay inside the lambda space), and compare with the frozen
'pivot' catalogue. Uses only networkx-free bitset code written here, not the project kernel."""
import sys, json, itertools
sys.path.insert(0,'/home/claude/src/experiments/memetik/lambda_radius_1_0_0')
import boot
from support import read, core, Guard
from kernel import catalogue
starts = read(boot.HERE/'STARTS.json')
def lam_ok_local(rows, verts):
    # check lambda=1 on every edge incident to any vertex in verts, and no edge lost regularity
    for v in verts:
        r=rows[v]
        if r.bit_count()!=14: return False
        m=r
        while m:
            u=(m&-m).bit_length()-1; m&=m-1
            if (rows[v]&rows[u]).bit_count()!=1: return False
    return True
res={}
for label in ('2076','2077'):
    rows=list(core.decode_g6(starts[label]['graph6'])); n=len(rows)
    edges=[(a,b) for a in range(n) for b in range(a+1,n) if rows[a]>>b&1]
    assert len(edges)==693
    found=set()
    for (a,b),(c,d) in itertools.combinations(edges,2):
        if len({a,b,c,d})<4: continue
        for (p,q),(r,s) in (((a,c),(b,d)),((a,d),(b,c))):
            if rows[p]>>q&1 or rows[r]>>s&1: continue
            new=rows[:]  # apply
            for x,y in ((a,b),(c,d)): new[x]^=1<<y; new[y]^=1<<x
            for x,y in ((p,q),(r,s)): new[x]^=1<<y; new[y]^=1<<x
            # lambda=1 must hold on edges touching a,b,c,d (only those can change) AND
            # on edges whose common neighbour count changed: pairs (x,y) with x or y in {a,b,c,d}; plus
            # pairs (x,y) both outside but with a common neighbour in {a,b,c,d}: their CN changes only if
            # x,y adjacency to a..d changed -> impossible (only a..d rows changed). So check all edges
            # of vertices whose adjacency changed = a,b,c,d, and all edges (x,y) with x,y outside whose CN via a..d changed:
            ok=lam_ok_local(new,(a,b,c,d))
            if ok:
                # edges between outside vertices x,y: CN(x,y) counts z with z~x,z~y; z in {a,b,c,d} rows changed,
                # so CN(x,y) can change if x or y in N(z) for changed z. Check those edges fully.
                touched=0
                for z in (a,b,c,d):
                    touched|=new[z]|rows[z]
                m=touched
                while m and ok:
                    x=(m&-m).bit_length()-1; m&=m-1
                    if x in (a,b,c,d): continue
                    mm=new[x]
                    while mm:
                        y=(mm&-mm).bit_length()-1; mm&=mm-1
                        if (new[x]&new[y]).bit_count()!=1: ok=False; break
            if ok:
                mv=(tuple(sorted((core.edge(a,b),core.edge(c,d)))), tuple(sorted((core.edge(p,q),core.edge(r,s)))))
                found.add(mv)
    piv=set(mv for name,mv in catalogue(tuple(rows),False,Guard()) if name=='pivot')
    apx=set(mv for name,mv in catalogue(tuple(rows),False,Guard()) if name=='apex')
    res[label]=dict(candidate_pairs_checked=693*692//2, lambda_preserving_2switches_bruteforce=len(found),
                    pivot_catalogue=len(piv), apex_catalogue=len(apx), bruteforce_minus_pivot=len(found-piv), pivot_minus_bruteforce=len(piv-found))
    print(label,res[label],flush=True)
json.dump(res,open('twoswitch_completeness.json','w'),indent=1)
