"""Independent standard-library check; no reviewer or solver imports."""
import pathlib, json, gzip, hashlib, collections
root = pathlib.Path(__file__).resolve().parent
with gzip.open(root / 'original_setup.json.gz', 'rt', encoding='utf-8') as f:
    data = json.load(f)
w = json.loads((root / 'concrete_witness.json').read_text())
N = 12
F = [[int(j == (i ^ 1)) for j in range(N)] for i in range(N)]
M = [r[:] for r in F]
E = [r[:] for r in F]
for i in range(8):
    for j in range(8):
        M[i][j] = data['M8'][i][j]
        E[i][j] = data['E8'][i][j]
def mul(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(N)) for j in range(N)] for i in range(N)]
EF, ME, EM = mul(E,F), mul(M,E), mul(E,M)
D = [[2-int(i==j)-F[i][j]-M[i][j]-EF[i][j] for j in range(N)] for i in range(N)]
G = [[9*int(i==j)+1-M[i][j] for j in range(N)] for i in range(N)]
K = [[2-F[i][j]-E[i][j]-ME[i][j]-EM[i][j] for j in range(N)] for i in range(N)]
cols = [tuple(x) for x in data['columns']]
assert cols == [(2*b+s,2*c+t) for b in range(6) for c in range(b+1,6) for s in range(2) for t in range(2)]
ci = {tuple(sorted(x)):i for i,x in enumerate(cols)}
P = [ci[tuple(sorted((u^1,v^1)))] for u,v in cols]
def image(v,p):
    return sum(1<<p[i] for i in range(60) if (v>>i)&1)
rows = w['masks']
pools = [data['pools'][0]]*2 + [data['pools'][1]]*2
lookup = [{v:i for i,v in enumerate(pool)} for pool in pools]
assert all(pools[i][w['indices'][i]] == rows[i] for i in range(4))
def valid_boundary(z):
    for a in range(4):
        assert z[a] in lookup[a]
        deg = [sum((z[a]>>c)&1 for c,(u,v) in enumerate(cols) if j in (u,v)) for j in range(N)]
        assert deg == D[a+8]
        for b in range(4):
            assert (z[a]&z[b]).bit_count() == G[a+8][b+8]
            assert (image(z[a],P)&z[b]).bit_count() == K[a+8][b+8]
    assert all(sum((v>>c)&1 for v in z)<=2 for c in range(60))
valid_boundary(rows)
group = data['group']
keys = set()
for g in group:
    r,p,c = g['rows'],g['anchors'],g['columns']
    assert sorted(r)==list(range(N)) and sorted(p)==list(range(N))
    assert c == [ci[tuple(sorted((p[u],p[v])))] for u,v in cols]
    assert all(P[c[j]]==c[P[j]] for j in range(60))
    assert all(D[i][j]==D[r[i]][p[j]] and G[i][j]==G[r[i]][r[j]] and K[i][j]==K[r[i]][r[j]] for i in range(N) for j in range(N))
    keys.add((tuple(r),tuple(p)))
assert len(keys)==len(group)==256
identity = tuple(range(N))
assert (identity,identity) in keys
for r,p in keys:
    for s,q in keys:
        assert (tuple(r[s[i]] for i in range(N)),tuple(p[q[i]] for i in range(N))) in keys
for a,b in [(8,9),(10,11)]:
    r=list(range(N)); r[a],r[b]=r[b],r[a]
    assert (tuple(r),identity) in keys

def canonical(v, slot):
    return min(image(v,g['columns']) for g in group if g['rows'][slot+8]==8)
counts=collections.Counter()
images=[]
for g in group:
    z=[0]*4
    for a in range(4):
        z[g['rows'][a+8]-8]=image(rows[a],g['columns'])
    valid_boundary(z)
    ix=[lookup[a][z[a]] for a in range(4)]
    c0=canonical(z[0],0)
    if z[0]!=c0:
        reason='y0_not_numeric_canonical'
    elif ix[1]<=ix[0]:
        reason='i1_not_greater_than_i0'
    elif canonical(z[1],1)<c0:
        reason='y1_canonical_below_y0'
    else:
        raise AssertionError('This image survives: '+str(ix))
    counts[reason]+=1
    images.append({'indices':ix,'masks':z,'reason':reason})
assert dict(counts)==w['rejection_counts']
lex = min(tuple(x['masks']) for x in images)
lex_indices=[lookup[a][lex[a]] for a in range(4)]
report={'status':'PASS','claim':'A valid boundary has no image passing the first three original guards under the full 256-element declared group. Not a SAT witness.','class':0,'own_case':4,'masks':rows,'indices':w['indices'],'matrix_contract_checked':'D=2J-I-F-M-EF, G=9I+J-M, K=2J-F-E-ME-EM; all 4 boundary rows, column capacity <=2','group_size':256,'group_closed':True,'group_preserves_full_contract':True,'all_256_images_valid':True,'rejection_counts':dict(counts),'lexicographically_least_image':lex,'original_indices_of_lex_image':lex_indices,'sorted_indices_of_lex_image':[sorted(pools[a]).index(lex[a]) for a in range(4)]}
(root/'independent_witness_receipt.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

