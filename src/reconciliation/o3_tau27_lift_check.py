#!/usr/bin/env python3
"""Independent exact regression for the tau=27 lift-capacity exclusion.

No SAT solver and no floating point are used. This script checks the finite C6
part of the paper proof and the 2C3 arithmetic, and emits a JSON certificate.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

MARKER = "CONWAY99-O3-TAU27-LIFT-CHECK-1"

def weighted_triangle_sum(H):
    n=len(H); w=0
    for i in range(n):
        for j in range(i+1,n):
            for k in range(j+1,n):
                w += H[i][j]*H[j][k]*H[k][i]
    return w

def c6_check():
    n=6
    L=[[0]*n for _ in range(n)]
    for i in range(n):
        j=(i+1)%n
        L[i][j]=L[j][i]=1
    chords=[]
    for i in range(n):
        for j in range(i+1,n):
            if not L[i][j]:
                dist=min((j-i)%n,(i-j)%n)
                chords.append((i,j,"distance2" if dist==2 else "diameter"))
    assert len(chords)==9
    assert sum(kind=="diameter" for _,_,kind in chords)==3
    survivors_local=0
    survivors_capacity=0
    counterexamples=[]
    for mask in range(1<<len(chords)):
        Z=[[0]*n for _ in range(n)]
        selected=[]
        for b,(i,j,kind) in enumerate(chords):
            if (mask>>b)&1:
                Z[i][j]=Z[j][i]=1
                selected.append((i,j,kind))
        local_ok=True
        for i in range(n):
            j=(i+2)%n
            d1=Z[i][(i+3)%n]
            d2=Z[(i-1)%n][j]
            mandatory=4+2*(d1+d2)
            if mandatory>6:
                local_ok=False
                break
        if not local_ok:
            continue
        survivors_local += 1
        a=sum(1 for _,_,kind in selected if kind=="distance2")
        b=sum(1 for _,_,kind in selected if kind=="diameter")
        assert b<=1
        H=[[2*L[i][j]+Z[i][j] for j in range(n)] for i in range(n)]
        W=weighted_triangle_sum(H)
        assert W>=4*a
        e=a+b
        capacity_ok=(7*e >= 2*n+3*W)
        if capacity_ok:
            survivors_capacity += 1
            counterexamples.append({"mask":mask,"a":a,"b":b,"e":e,"W":W})
    assert survivors_local>0
    assert survivors_capacity==0
    return {
        "all_chord_masks":1<<len(chords),
        "locally_necessary_survivors":survivors_local,
        "capacity_survivors":survivors_capacity,
        "counterexamples":counterexamples,
    }

def two_c3_check():
    m=6; e=3; W_min=16
    lhs=7*e; rhs=2*m+3*W_min
    assert lhs<rhs
    return {"m":m,"e":e,"W_min":W_min,"lhs":lhs,"rhs":rhs,"contradiction":True}

def algebra_check():
    samples=0
    for m in range(1,34):
        for e in range(0,100):
            for W in range(0,30,7):
                f=10*m-2*e
                trkh=16*m+10*e-6*W
                twoD=3*f-trkh
                assert twoD==14*m-16*e+6*W
                assert (twoD<=f)==(7*e>=2*m+3*W)
                samples+=1
    return {"integer_symbolic_samples":samples,"pass":True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default=None)
    args=ap.parse_args()
    result={"format":MARKER,"algebra":algebra_check(),"C6":c6_check(),"2C3":two_c3_check(),"pass":True}
    text=json.dumps(result,indent=2,sort_keys=True)
    if args.out:
        p=Path(args.out); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text+"\n")
    print(text)

if __name__=="__main__":
    main()
