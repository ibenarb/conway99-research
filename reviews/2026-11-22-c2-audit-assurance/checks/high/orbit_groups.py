# Own construction of the chart automorphisms acting on 12-word star assignments (own geometry, own GL(4,2) lifts).
import itertools, json
exec(open('geometry.py').read().split("# induced action of GL(4,2)")[0])   # circuits, cosets, stars, vert, edge (own code)
def gl():
    for b in itertools.permutations(range(1, 16), 4):
        f = [0]; ok = True
        for x in b:
            if x in f: ok = False; break
            f += [y ^ x for y in f]
        if ok: yield f
lift = {}
for f in gl():
    im = lambda m: sum(1 << (f[i + 1] - 1) for i in range(15) if m >> i & 1)
    img = {a: min(im(cos[a][0]) ^ s for s in simplex) for a in keys}
    p = tuple(stars.index(frozenset(img[a] for a in s)) for s in stars)
    if p[0] == 0 and p[1] == 1:
        lift[p[2:]] = [f[i + 1] - 1 for i in range(15)]        # coordinate i -> coordinate
assert len(lift) == 360
L = [list(map(int, s.split())) for s in open('/home/claude/pk/Conway99_NoInvolution_EvenAxis_Exact/even-simplex-packet/dualplanes/unary5-packet/layouts.tsv')]
charts = [int(s) for s in open('/home/claude/replay/orbitaudit/pkt/unsigned15/strong_charts.txt')]
out = open('orbit_groups.txt', 'w')
for cid in charts:
    P = L[cid][1:13]; N = L[cid][13:25]
    for par, order in ((0, [2, 3, 4, 5, 6, 7]), (1, [2, 3, 4, 5, 7, 6])):
        elems = []
        for q in itertools.permutations(range(6)):
            vp = [0] * 8
            for j in range(6): vp[order[j]] = order[q[j]]
            key = tuple(vp[2:])
            if key not in lift: continue           # odd permutation: not induced by the coordinate group
            for h in range(64):
                p = [2 * q[i // 2] + ((i % 2) ^ ((h >> (i // 2)) & 1)) for i in range(12)]
                if all(p[P[i]] == P[p[i]] and p[N[i]] == N[p[i]] for i in range(12)):
                    elems.append((tuple(p), tuple(lift[key])))
        # small generating set by closure on the label permutations
        gens = []; closure = {tuple(range(12))}
        for p, s in elems:
            if p in closure: continue
            gens.append((p, s))
            frontier = list(closure)
            gp = [g for g, _ in gens]
            changed = True
            while changed:
                changed = False
                for a in list(closure):
                    for g in gp:
                        c = tuple(g[a[i]] for i in range(12))
                        if c not in closure: closure.add(c); changed = True
            if len(closure) == len(elems): break
        assert len(closure) == len(elems)
        out.write(f'{cid} {par} {len(elems)} {len(gens)}\n')
        for p, s in gens: out.write(' '.join(map(str, p)) + ' ' + ' '.join(map(str, s)) + '\n')
out.close()
print('wrote groups for', len(charts), 'charts')
