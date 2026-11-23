# Rank 8 (charts 306, 620, 2264): number of viable (star, 2-plane of F_7^3) pairs after the unary/plane filter,
# for comparison with the "Wdomains" column of the frozen generic-low logs.  Own code.
import itertools, time
from own_local import *
import own_setup
def planes3():
    seen = set(); out = []
    def norm(v):
        f = next(x for x in v if x); iv = pow(f, -1, 7); return tuple(x * iv % 7 for x in v)
    pts = sorted({norm(v) for v in itertools.product(range(7), repeat=3) if any(v)})
    for a, b in itertools.combinations(pts, 2):
        W = frozenset(tuple((x * p + y * q) % 7 for p, q in zip(a, b)) for x in range(7) for y in range(7))
        if W not in seen: seen.add(W); out.append(W)
    return out
PL = planes3(); print('2-planes of F_7^3:', len(PL))
for cid in (306, 620, 2264):
    for par in (0, 1):
        t0 = time.time(); C = Chart(cid, par); dom = own_setup.attachments_fast(C)
        stars = C.star_assignments(); viable = 0
        for st in stars:
            Hs = []
            for y in OUTER:
                keys = C.outer_keys(st, y)
                Hs.append({a['h'] for a in dom[y] if a['key'] in keys})
            if any(not h for h in Hs): continue
            viable += sum(1 for W in PL if all(hs & W for hs in Hs))
        print('chart', cid, 'own parity', par, '(packet parity', 1 - par, ') rank', C.rank, 'nonpivots', C.nonpiv, 'stars', len(stars), 'viable (star, plane) pairs', viable, 'time', round(time.time() - t0), flush=True)
