"""Independent finite orbit proof: inverse-closed S, lambda=1 imply S/2=S."""
import collections
import itertools
import json

results={}
for name,mods in [('Z99',(99,)),('Z3xZ3xZ11',(3,3,11))]:
    elements=list(itertools.product(*(range(m) for m in mods)))
    zero=(0,)*len(mods)
    unseen=set(elements)-{zero};orbits=[]
    while unseen:
        x=min(unseen);orbit=[]
        while x not in orbit:
            orbit.append(x);x=tuple(2*a%m for a,m in zip(x,mods))
        unseen.difference_update(orbit);orbits.append(orbit)
    candidates=[];hits=[]
    for mask in range(1<<len(orbits)):
        if sum(len(o) for i,o in enumerate(orbits) if mask>>i&1)!=14:continue
        S={x for i,o in enumerate(orbits) if mask>>i&1 for x in o}
        assert all(tuple(-a%m for a,m in zip(x,mods)) in S for x in S)
        counts={s:sum(tuple((a-b)%m for a,b,m in zip(x,s,mods)) in S for x in S) for s in S}
        candidates.append(mask)
        if all(c==1 for c in counts.values()):hits.append(mask)
    results[name]={'moduli':mods,'doubling_orbits':orbits,'orbit_lengths':list(map(len,orbits)),
                   'size14_inverse_closed_orbit_unions':len(candidates),'lambda1_solutions':hits}
print(json.dumps(results,indent=4))
