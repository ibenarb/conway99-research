"""Independent principal-minor oracle and positive embedding controls for the finite Gram test."""
from pathlib import Path
import hashlib
import itertools
import json
import random
import subprocess
import time

BASE = Path(__file__).resolve().parent

def determinant(matrix):
    if not matrix:
        return 1
    # Exact integer Bareiss elimination, with reduction modulo 7 only at the end.
    a = [row[:] for row in matrix]
    sign, old = 1, 1
    for c in range(len(a)-1):
        k = next((k for k in range(c,len(a)) if a[k][c]), None)
        if k is None:
            return 0
        if k != c:
            a[k], a[c] = a[c], a[k]
            sign = -sign
        pivot = a[c][c]
        for i in range(c+1,len(a)):
            for j in range(c+1,len(a)):
                numerator = a[i][j]*pivot-a[i][c]*a[c][j]
                assert numerator % old == 0
                a[i][j] = numerator//old
            a[i][c] = 0
        old = pivot
    return sign*a[-1][-1] % 7

def oracle(g):
    for r in range(len(g),0,-1):
        for indices in itertools.combinations(range(len(g)),r):
            value = determinant([[g[i][j] for j in indices] for i in indices])
            if value:
                return r, value in (1,2,4)
    return 0, True

def main():
    started = time.time()
    rng = random.Random(20261122)
    cases = []
    for a,b,c in itertools.product(range(7),repeat=3):
        g = [[a,b],[b,c]]
        for dim in (1,2,3):
            for det in (1,3):
                cases.append((g,dim,det,None))
    for size in range(1,8):
        for trial in range(20):
            g = [[0]*size for _ in range(size)]
            for i in range(size):
                for j in range(i,size):
                    g[i][j] = g[j][i] = rng.randrange(7)
            cases.append((g,rng.choice((4,5)),rng.choice((1,3)),None))
    # Genuine ambient Gram matrices, including dependence, must always pass.
    for dim in (4,5):
        for det in (1,3):
            metric = [1]*(dim-1)+[det]
            for trial in range(40):
                vectors = [[rng.randrange(7) for _ in range(dim)] for _ in range(rng.randrange(1,8))]
                g = [[sum(v[k]*metric[k]*w[k] for k in range(dim))%7 for w in vectors] for v in vectors]
                cases.append((g,dim,det,True))
            identity = [[(metric[i] if i == j else 0) for j in range(dim)] for i in range(dim)]
            cases.append((identity,dim,3 if det == 1 else 1,False))
    # Explicit zero, hyperbolic and over-dimension controls.
    cases += [([[0]*3 for _ in range(3)],4,3,True),
              ([[0,1],[1,0]],2,3,True), ([[0,1],[1,0]],2,1,False),
              ([[int(i==j) for j in range(6)] for i in range(6)],5,1,False)]
    text = ''.join(f'{len(g)} {dim} {det}\n'+' '.join(str(x) for row in g for x in row)+'\n' for g,dim,det,_ in cases)
    (BASE/'gram_controls_input.txt').write_text(text)
    command = ['wsl.exe','--distribution','Ubuntu-24.04','--cd',str(BASE),'--exec','./residual_gram_v1_checked','--gram-batch']
    result = subprocess.run(command, input=text, text=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    (BASE/'gram_controls.stdout').write_text(result.stdout)
    (BASE/'gram_controls.stderr').write_text(result.stderr)
    assert result.returncode == 0 and 'runtime error:' not in result.stderr
    rows = result.stdout.splitlines()
    assert len(rows) == len(cases)
    positive = negative = 0
    for (g,dim,det,known), row in zip(cases,rows):
        rank, value, allowed = map(int,row.split())
        ref_rank, ref_square = oracle(g)
        assert rank == ref_rank and (value in (1,2,4)) == ref_square
        expected = rank <= dim and (rank < dim or ref_square == (det in (1,2,4)))
        assert bool(allowed) == expected
        if known is not None:
            assert expected == known
        positive += allowed
        negative += not allowed
    report = dict(status='GRAM_CONTROLS_PASS', cases=len(cases), positive=positive,
                  negative=negative, genuine_ambient_gram_cases=160,
                  algorithm='All principal minors, exact integer Bareiss; compared to modular column-basis implementation',
                  elapsed_seconds=time.time()-started)
    report['hashes'] = {name:hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in
                       ['residual_gram_v1.cpp','residual_gram_v1_checked','gram_controls_input.txt','gram_controls.stdout','validate_gram_v1.py']}
    (BASE/'gram_controls_result.json').write_text(json.dumps(report,indent=4))
    print(json.dumps(report))

if __name__ == '__main__':
    main()
