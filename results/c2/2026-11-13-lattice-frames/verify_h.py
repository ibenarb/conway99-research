import gzip
"""Standalone verifier for h-stage cover certificates; does not call the producer."""
import json,math,pathlib,sys,time
import numpy as np
import flint

def require(value,message):
    if not value: raise ValueError(message)

def bits(items):
    return sum(1<<int(i) for i in items)

def canonical(row):
    value=tuple(map(int,row)); opposite=tuple(-x for x in value)
    return max(value,opposite)

def verify_tree(node,candidates,pending,need,neighbors,through,covers):
    if 'leaf' in node:
        reason=node['leaf']
        if reason=='cardinality': require(candidates.bit_count()<need,'false cardinality leaf')
        elif reason=='uncovered': require(need==0 and pending!=0,'false uncovered leaf')
        elif reason=='no_cover':
            p=node['point']; require(0<=p<len(through) and pending>>p&1 and not(candidates&through[p]),'false missing cover')
        else: raise ValueError('unknown leaf')
        return 1
    require(need>0,'nonterminal at depth seven')
    branches=node['branches']; seen=[v for v,child in branches]
    require(len(seen)==len(set(seen)),'duplicate branch')
    total=1
    if 'point' in node:
        p=node['point']; require(0<=p<len(through) and pending>>p&1,'invalid pivot')
        expected=candidates&through[p]
        require(bits(seen)==expected,'branch omission or addition')
        for v,child in branches:
            total+=verify_tree(child,candidates&neighbors[v],pending&~covers[v],need-1,neighbors,through,covers)
    else:
        require(node.get('ordered') is True and pending==0,'invalid unordered branch')
        for v,child in branches:
            require(candidates>>v&1,'invalid candidate')
            require(v==(candidates&-candidates).bit_length()-1,'wrong ordered branch')
            candidates&=~(1<<v)
            total+=verify_tree(child,candidates&neighbors[v],0,need-1,neighbors,through,covers)
        require(candidates.bit_count()<need,'ordered tail omitted')
    return total

def controls():
    require(verify_tree({'leaf':'cardinality'},3,0,3,[0,0],[],[0,0])==1,'control failure')
    bad=[({'leaf':'cardinality'},7,0,3),({'point':0,'branches':[]},1,1,1)]
    for node,C,P,k in bad:
        try: verify_tree(node,C,P,k,[0,0,0],[1],[1,0,0])
        except ValueError: continue
        raise ValueError('corrupt proof accepted')

if __name__=='__main__':
    controls(); root=pathlib.Path(__file__).resolve().parent; lid=sys.argv[1]; old=root.parent/'C2_Strategiewechsel_20261113'; folder=root/lid
    shells=[json.loads(line) for line in gzip.open(folder/'exact_short.jsonl.gz','rt',encoding='utf-8').read().splitlines()]
    H0=np.array([v for norm,v in shells if norm==4],dtype=np.int64)
    W0=np.array([v for norm,v in shells if norm==3],dtype=np.int64)
    reports=[]
    for path in sorted(folder.glob('pair_*.npz')):
        if len(sys.argv)>2 and path.stem!='pair_'+sys.argv[2]:continue
        start=time.time(); data=np.load(path,allow_pickle=False)
        for key in ['gram','h','words','shadow','y1','y2']: require(data[key].dtype.kind=='i','noninteger array')
        G=data['gram']; H=data['h']; W=data['words']; Z=data['shadow']; N=np.array([data['y1'],data['y2']])
        require(G.shape==(24,24) and np.array_equal(G,G.T),'bad Gram')
        maximum=max(int(np.abs(x).max()) for x in [H0,W0,Z,N]); grammax=int(np.abs(G).max())
        require(24*24*maximum*maximum*grammax<2**62,'unsafe fixed-width arithmetic')
        basis=json.loads((folder/'basis.json').read_text()); source=json.loads((folder/'lattice.json').read_text())['gens']
        B=flint.fmpq_mat([[flint.fmpq(x) for x in row] for row in basis]); B0=flint.fmpq_mat([[flint.fmpq(str(x)) for x in row] for row in source]); T=B*B0.inv()
        require(all(T[i,j].q==1 for i in range(24) for j in range(24)) and abs(T.det())==1,'basis mismatch')
        exactG=B*B.transpose(); require(all(exactG[i,j]==int(G[i,j]) for i in range(24) for j in range(24)),'wrong Gram basis')
        require(np.array_equal(N@G@N.T,7*np.eye(2,dtype=np.int64)),'wrong normals')
        require(np.all(np.einsum('ij,jk,ik->i',Z,G,Z)==8) and np.all((Z@G-np.diag(G))%2==0),'wrong characteristic vectors')
        hit=np.any(np.abs(Z@G@N.T)==3,axis=1)
        Hexpected=H0[np.all(H0@G@N.T==0,axis=1)&np.all(np.abs(H0@G@Z.T)<=2,axis=1)]
        Wexpected=W0[np.all(W0@G@N.T==0,axis=1)&np.all(np.abs(W0@G@Z.T)<=3,axis=1)&np.all(np.abs(W0@G@Z[hit].T)<=1,axis=1)]
        require(len(H)==len(Hexpected) and {canonical(v) for v in H}=={canonical(v) for v in Hexpected},'h coverage mismatch')
        require(len(W)==len(Wexpected) and {canonical(v) for v in W}=={canonical(v) for v in Wexpected},'word coverage mismatch')
        footprints=np.abs(H@G@Z[hit].T)==2
        neighbors=[]; through=[bits(np.flatnonzero(column)) for column in footprints.T]; covers=[bits(np.flatnonzero(row)) for row in footprints]
        products=W@G@H.T
        plus=[bits(np.flatnonzero(column==1)) for column in products.T]; minus=[bits(np.flatnonzero(column==-1)) for column in products.T]
        orthogonal=H@G@H.T==0
        for i,row in enumerate(orthogonal):
            mask=0
            for j in np.flatnonzero(row):
                j=int(j)
                if covers[i]&covers[j]:continue
                if not ((plus[i]&plus[j])|(minus[i]&minus[j])):continue
                if not ((plus[i]&minus[j])|(minus[i]&plus[j])):continue
                mask|=1<<j
            neighbors.append(mask)
        stored_graph=data['compatibility']
        require(all(neighbors[i]==bits(np.flatnonzero(stored_graph[i])) for i in range(len(H))),'compatibility mismatch')
        proof=json.load(gzip.open(folder/(path.stem+'_certificate.json.gz'),'rt',encoding='utf-8'))
        nodes=verify_tree(proof['proof'],(1<<len(H))-1,(1<<len(through))-1,7,neighbors,through,covers)
        report=dict(pair=path.stem,status='EXACT_COVER_CERTIFICATE_PASS',nodes=nodes,seconds=round(time.time()-start,3),shells='independent exact rational enumeration',overflow_bound=24*24*maximum*maximum*grammax,transfer_used=False)
        reports.append(report); print(json.dumps(report),flush=True)
    (folder/('independent_check_'+sys.argv[2]+'.json' if len(sys.argv)>2 else 'independent_check.json')).write_text(json.dumps(dict(lattice=lid,status='PASS',results=reports,controls='one positive, two corrupted proofs rejected'),indent=4))

