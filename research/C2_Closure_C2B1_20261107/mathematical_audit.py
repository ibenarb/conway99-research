"""Independent C2B1 mathematical closure prerequisites, no search-generator import."""
from collections import Counter
from itertools import combinations
import gzip
import json
from row_domains_complete import components


def require(condition, message):
    if not condition:
        raise ValueError(message)


def image(x, action):
    result = 0
    while x:
        bit = (x & -x).bit_length() - 1
        result |= 1 << action[bit]
        x &= x - 1
    return result


def permutation(p, n):
    require(len(p) == n and all(type(x) is int for x in p) and sorted(p) == list(range(n)), 'Invalid permutation')


def load_model(path):
    with path.open() as f:
        require(f.readline().split() == ['12', '60'], 'Model dimensions')
        p = list(map(int, f.readline().split()))
        matrices = [[list(map(int, f.readline().split())) for _ in range(12)] for _ in range(2)]
        domains = []
        for _ in range(12):
            count = int(f.readline())
            row = list(map(int, f.readline().split()))
            require(len(row) == count and row == sorted(set(row)) and all(0 <= x < 1 << 60 for x in row), 'Domain encoding')
            domains.append(row)
        count = int(f.readline())
        boundaries = [list(map(int, f.readline().split())) for _ in range(count)]
        require(count > 0 and all(len(b) == 2 for b in boundaries) and not f.read().strip(), 'Boundary encoding')
    return p, matrices[0], matrices[1], domains, boundaries


def validate(root, progress=lambda message: None):
    record = json.loads((root / 'record.json').read_text())
    catalog = json.loads((root / 'representatives.json').read_text())['records']
    require(sum(x == record for x in catalog) == 1, 'Record not in pinned catalog')
    m, e = record['M'], record['E']
    for p in (m, e):
        permutation(p, 12)
        require(all(p[p[i]] == i and p[i] != i for i in range(12)), 'Invalid matching')
    f = [i ^ 1 for i in range(12)]
    pairs = [(i, j) for i, j in combinations(range(12), 2) if f[i] != j]
    p = [pairs.index(tuple(sorted((f[i], f[j])))) for i, j in pairs]
    d = [[2 - int(i == j) - int(f[i] == j) - int(m[i] == j) - int(f[e[i]] == j) for j in range(12)] for i in range(12)]
    g = [[9 * int(i == j) + 1 - int(m[i] == j) for j in range(12)] for i in range(12)]
    k = [[2 - int(f[i] == j) - int(e[i] == j) - int(e[m[i]] == j) - int(m[e[i]] == j) for j in range(12)] for i in range(12)]
    actual_p, actual_g, actual_k, domains, boundaries = load_model(root / 'model.txt')
    require((actual_p, actual_g, actual_k) == (p, g, k), 'Original matrix mismatch')
    expected_cache = {}
    for r in range(12):
        require(k[r][r] >= 0 and k[r][r] % 2 == 0, 'Diagonal twist')
        key = (tuple(d[r]), k[r][r] // 2)
        if key not in expected_cache:
            progress('Enumerating complete row domain ' + str(r))
            expected_cache[key] = components(*key, pairs, p)
        require(set(domains[r]) == expected_cache[key], 'Incomplete or incorrect domain ' + str(r))
        require(all(x.bit_count() == 10 for x in domains[r]), 'Row weight')
    progress('Complete domains validated')
    with gzip.open(root / 'boundaries.json.gz', 'rt') as stream:
        package = json.load(stream)
    require(package['representatives'] == boundaries, 'Boundary/model mismatch')
    require(len(set(map(tuple, boundaries))) == len(boundaries), 'Duplicate representative')
    require(domains[0] == domains[1] and domains[2] == domains[3], 'Pure swap domain mismatch')
    for a, b in [(0, 1), (2, 3)]:
        swap = list(range(12))
        swap[a], swap[b] = swap[b], swap[a]
        require(all(d[r] == d[swap[r]] for r in range(12)), 'Pure swap degree target')
        require(all(mat[r][s] == mat[swap[r]][swap[s]] for mat in (g, k) for r in range(12) for s in range(12)), 'Pure swap matrix')
        require(g[a][a] > g[a][b], 'Pure swap distinctness')
    sigma = [2, 3, 0, 1] + list(range(4, 12))
    def coupled(q):
        permutation(q, 12)
        require(all(q[f[i]] == f[q[i]] for i in range(12)), 'Coupled F commutation')
        require(all(mat[r][s] == mat[q[r]][q[s]] for mat in (d, g, k) for r in range(12) for s in range(12)), 'Coupled matrix covariance')
        cp = [pairs.index(tuple(sorted((q[a], q[b])))) for a, b in pairs]
        require(all(cp[p[c]] == p[cp[c]] for c in range(60)), 'Coupled P commutation')
        return cp
    sc = coupled(sigma)
    group = package['group']
    require(group and len(set(map(tuple, group))) == len(group), 'Empty/duplicate group')
    actions = []
    first_images = []
    for q in group:
        require(set(q[:2]) == {0, 1} and set(q[2:4]) == {2, 3}, 'Boundary pair moved by old group')
        cp = coupled(q)
        actions.append([cp[sc[c]] for c in range(60)])
        first_images.append({x: image(x, cp) for x in domains[0]})
    raw = list(map(int, (root / 'block_actions.txt').read_text().split()))
    require(raw and raw[0] == len(actions) and raw[1:] == [c for a in actions for c in a], 'Wrong composed block actions')
    # Degree covariance and P commutation preserve the exact, now complete domain definitions.
    tau = list(map(int, (root / 's2_action.txt').read_text().split()))
    permutation(tau, 60)
    require(all(tau[tau[c]] == c and tau[p[c]] == p[tau[c]] for c in range(60)), 'S2 not commuting involution')
    seen_domains = set()
    for r in range(12):
        key = (tuple(d[r]), k[r][r] // 2)
        if key not in seen_domains:
            values = expected_cache[key]
            require(all(image(x, tau) in values for x in values), 'S2 changes full domain')
            seen_domains.add(key)
    require(all(image(x, tau) == x for x in domains[0] + domains[1]), 'S2 moves possible boundary')
    progress('Coupled and pure action contracts validated')
    allowed = sum(1 << c for c, pair in enumerate(pairs) if not set(pair) & {0, 1})
    require(allowed.bit_count() == 40 and image(allowed, p) == allowed, 'Type-I support universe')
    require(all(d[r][0] == d[r][1] == 0 and k[r][r] == 0 for r in (0, 1)), 'Type-I diagonal requirements')
    require(g[0][1] == k[0][1] == 0, 'Type-I cross requirements')
    supports = {}
    for x in domains[0]:
        px = image(x, p)
        require(x.bit_count() == 10 and not x & px and not (x | px) & ~allowed, 'Invalid Type-I row')
        supports[x] = x | px
    counts = Counter(supports.values())
    total = sum(count * counts.get(allowed ^ support, 0) for support, count in counts.items())
    require(package['states'] == total == len(package['coverage']), 'Incomplete boundary coverage count')
    seen = set()
    used = set()
    for a, b, index, which in package['coverage']:
        require(a in supports and b in supports and supports[b] == allowed ^ supports[a], 'Invalid covered boundary')
        require((a, b) not in seen, 'Duplicate covered ordered pair')
        seen.add((a, b))
        require(type(index) is int and 0 <= index < len(boundaries) and type(which) is int and 0 <= which < len(group), 'Invalid transport reference')
        aa, bb = boundaries[index]
        require(aa in supports and bb in supports, 'Representative outside domains')
        table = first_images[which]
        mapped = (table[aa], table[bb])
        if group[which][0] == 1:
            mapped = mapped[::-1]
        require(mapped == (a, b), 'Incorrect coupled transport')
        used.add(index)
    require(used == set(range(len(boundaries))), 'Unused representative')
    for a, b in boundaries:
        require((a, b) in seen and a < b, 'Representative ordering/coverage')
        require((a, b) == min(tuple(sorted((table[a], table[b]))) for table in first_images), 'Nonminimal old representative')
    progress('Full ordered boundary coverage and minima validated')
    return dict(case=record['id'],boundary_count=len(boundaries),ordered_pairs=total,group_actions=len(group),complete_domains=[len(row) for row in domains],boundaries=boundaries)
