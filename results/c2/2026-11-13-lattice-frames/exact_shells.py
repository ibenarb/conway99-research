import gzip
"""Independent exact short-vector enumeration by rational LDL decomposition."""
import hashlib, itertools, json, math, pathlib, sys, time
from fractions import Fraction as F

def enumerate_ball(gram,bound):
    n=len(gram)
    lower=[[F(i==j) for j in range(n)] for i in range(n)]
    diagonal=[]
    for i in range(n):
        pivot=F(gram[i][i])-sum(lower[i][k]**2*diagonal[k] for k in range(i))
        assert pivot>0
        diagonal.append(pivot)
        for j in range(i+1,n):
            lower[j][i]=(gram[j][i]-sum(lower[j][k]*lower[i][k]*diagonal[k] for k in range(i)))/pivot
    assert all(sum(lower[i][k]*diagonal[k]*lower[j][k] for k in range(n))==gram[i][j] for i in range(n) for j in range(n))
    denominators=[]; coefficients=[]
    for i in range(n):
        denominator=math.lcm(*(lower[j][i].denominator for j in range(i,n)))
        denominators.append(denominator)
        coefficients.append([int(lower[j][i]*denominator) for j in range(n)])
    vector=[0]*n; counts=[0]*(bound+1); nodes=[0]*(n+1); positive=[]
    def recurse(i,remaining):
        nodes[i+1]+=1
        if i<0:
            norm=F(bound)-remaining
            assert norm.denominator==1
            counts[int(norm)]+=1
            if norm and tuple(vector)>tuple(-v for v in vector):
                positive.append((int(norm),tuple(vector)))
            return
        denominator=denominators[i]
        numerator=sum(coefficients[i][j]*vector[j] for j in range(i+1,n))
        radius=remaining/diagonal[i]
        width=math.isqrt(radius.numerator//radius.denominator)
        midpoint=(-numerator)//denominator
        for value in range(midpoint-width-1,midpoint+width+2):
            shifted=value*denominator+numerator
            cost=diagonal[i]*F(shifted*shifted,denominator*denominator)
            if cost<=remaining:
                vector[i]=value
                recurse(i-1,remaining-cost)
        vector[i]=0
    recurse(n-1,F(bound))
    return positive,counts,nodes

def controls():
    for gram,bound in [([[1,0],[0,1]],4),([[2,1],[1,2]],4),([[1,1],[1,2]],4)]:
        vectors,counts,nodes=enumerate_ball(gram,bound)
        expected=set()
        for v in itertools.product(range(-5,6),repeat=2):
            norm=sum(v[i]*gram[i][j]*v[j] for i in range(2) for j in range(2))
            if 0<norm<=bound and v>tuple(-x for x in v):
                expected.add((norm,v))
        assert set(vectors)==expected
    try:
        enumerate_ball([[1,2],[2,1]],4)
    except AssertionError:
        return dict(positive_controls=3,indefinite_rejected=True)
    raise AssertionError('Indefinite input accepted')

if __name__=='__main__':
    root=pathlib.Path(__file__).resolve().parent
    old=root.parent/'C2_Strategiewechsel_20261113'
    lid=sys.argv[1]
    folder=root/lid
    folder.mkdir(exist_ok=True)
    check=controls()
    gram=json.loads((folder/'gram.json').read_text())
    start=time.time()
    vectors,counts,nodes=enumerate_ball(gram,4)
    supplied={(norm,tuple(v)) for norm,v in (json.loads(line) for line in gzip.open(folder/'exact_short.jsonl.gz','rt',encoding='utf-8'))}
    assert set(vectors)==supplied,'Exact and floating shell catalogues differ'
    with (folder/'exact_short.jsonl').open('w') as output:
        for norm,v in sorted(vectors):
            output.write(json.dumps([norm,list(v)],separators=(',',':'))+'\n')
    report=dict(id=lid,status='EXACT_EXHAUSTIVE_SHELLS_MATCH',bound=4,counts=counts,nodes=nodes,seconds=round(time.time()-start,3),controls=check,arithmetic='Python Fraction and arbitrary-precision integers only',sha256=hashlib.sha256((folder/'exact_short.jsonl').read_bytes()).hexdigest())
    (folder/'exact_shells.json').write_text(json.dumps(report,indent=4))
    print(json.dumps(report),flush=True)
