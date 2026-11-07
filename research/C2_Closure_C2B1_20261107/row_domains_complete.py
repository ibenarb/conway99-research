"""Two independent complete enumerations of degree<=2 row graphs."""
from itertools import combinations

def residual(degrees, expected, pairs, flip):
    index={p:i for i,p in enumerate(pairs)}
    result=set()
    def walk(rem,mask,doubles):
        if doubles>expected:return
        todo=[i for i,d in enumerate(rem) if d]
        if not todo:
            if doubles==expected:result.add(mask)
            return
        v=todo[0]
        options=[u for u in todo[1:] if (v,u) in index]
        for chosen in combinations(options,rem[v]):
            rr=rem.copy();rr[v]=0;mm=mask;dd=doubles
            for u in chosen:
                rr[u]-=1;c=index[(v,u)]
                dd+=bool(mm&(1<<flip[c]));mm|=1<<c
            if dd<=expected:walk(rr,mm,dd)
    walk(list(degrees),0,0)
    return result

def components(degrees, expected, pairs, flip):
    index={p:i for i,p in enumerate(pairs)}
    assert all(d in (0,1,2) for d in degrees)
    answer=set()
    def edge(a,b,mask,count):
        c=index.get(tuple(sorted((a,b))))
        if c is None:return None
        count+=bool(mask&(1<<flip[c]))
        if count>expected:return None
        return mask|(1<<c),count
    def cycles(vertices,mask,count):
        if not vertices:
            if count==expected:
                assert mask not in answer
                answer.add(mask)
            return
        if len(vertices)<3:return
        a=min(vertices)
        def grow(chain,free,mm,dd):
            z=chain[-1]
            if len(chain)>=3 and chain[1]<z:
                closed=edge(z,a,mm,dd)
                if closed is not None:cycles(free,*closed)
            for v in sorted(free):
                added=edge(z,v,mm,dd)
                if added is not None:grow(chain+[v],free-{v},*added)
        grow([a],vertices-{a},mask,count)
    def paths(ends,internal,mask,count):
        if not ends:
            cycles(internal,mask,count);return
        a=min(ends)
        def grow(last,free,mm,dd):
            for b in sorted(ends-{a}):
                closed=edge(last,b,mm,dd)
                if closed is not None:paths(ends-{a,b},free,*closed)
            for v in sorted(free):
                added=edge(last,v,mm,dd)
                if added is not None:grow(v,free-{v},*added)
        grow(a,internal,mask,count)
    paths({i for i,d in enumerate(degrees) if d==1},{i for i,d in enumerate(degrees) if d==2},0,0)
    return answer
