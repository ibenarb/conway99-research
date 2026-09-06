"""Integer-only, generator-independent production matrix verifier."""
from __future__ import annotations

class VerificationError(ValueError):
    pass

def verify(core, chosen):
    n = core['n']; L = {tuple(x) for x in core['L']}; S = {tuple(sorted(x)) for x in chosen}
    if S & L or not all(i < j and 0 <= i < n and j < n for i,j in S):
        raise VerificationError('invalid or forbidden S edge')
    q = [[0]*n for _ in range(n)]
    for i,j in S: q[i][j] = q[j][i] = 1
    for i,j in L: q[i][j] = q[j][i] = 2
    for i in core['T']: q[i][i] = 2
    targets = [core['degree_targets'][str(i)] for i in range(n)]
    sdeg = [sum(1 for e in S if i in e) for i in range(n)]
    if sdeg != targets: raise VerificationError(('S-degree', sdeg, targets))
    qdeg = [sum(r) for r in q]
    expected_qdeg = [2*(i in core['T']) + targets[i] + 2*sum(i in e for e in L) for i in range(n)]
    if qdeg != expected_qdeg: raise VerificationError(('Q-row-sum', qdeg, expected_qdeg))
    for i in range(n):
        for j in range(n):
            value = sum(q[i][k]*q[k][j] for k in range(n)) + q[i][j]
            expected = 18 if i == j else 6
            if value != expected: raise VerificationError(('matrix', i, j, value, expected))
    return True
