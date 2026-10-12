"""Necessary marking-domain Hall test; no global completion claim or SAT run."""
import collections
import itertools
import json
from pathlib import Path
import sys


def perfect_matching(domains):
    owner = [-1] * len(domains)

    def augment(u, seen):
        for v in domains[u]:
            if v in seen:
                continue
            seen.add(v)
            if owner[v] == -1 or augment(owner[v], seen):
                owner[v] = u
                return True
        return False

    return all(augment(u, set()) for u in sorted(range(len(domains)), key=lambda x: len(domains[x])))


def main(source, destination):
    labels = [(c, d) for c, d in itertools.combinations(range(12), 2) if d != (c ^ 1)]
    assert len(labels) == 60
    rows = []
    strata = collections.defaultdict(list)
    for line in Path(source).read_text().splitlines():
        r = json.loads(line)
        if r['d_plus'] > 2 or not r['passes_local_filter']:
            continue
        l, n = r['L'], r['N']
        nonedges = [(u, v) for u, v in itertools.combinations(range(12), 2) if l[u] != v]
        demands = [[2 - (c == i) - (c == (i ^ 1)) - (c == l[i]) - (c == (n[i] ^ 1)) for c in range(12)] for i in range(12)]
        assert all(min(row) >= 0 and sum(row) == 20 for row in demands)
        # If z has anchor label {c,d} and is adjacent to x_i, both residual
        # incidence demands must be positive. This is only a necessary test.
        domains = [[j for j, pair in enumerate(nonedges) if all(demands[i][c] > 0 and demands[i][d] > 0 for i in pair)] for c, d in labels]
        hall = perfect_matching(domains)
        entry = {'partition': r['partition'], 'L': l, 'N': n,
                 'hall_pass': hall, 'allowed_assignments': sum(map(len, domains)),
                 'smallest_domain': min(map(len, domains)), 'automorphisms': r['automorphisms']}
        rows.append(entry)
        strata[tuple(r['partition'])].append(entry)
    result = {'scope': 'Necessary marking assignment relaxation; passing is not feasibility of the marking equations.',
              'tested': len(rows), 'excluded_by_Hall': sum(not r['hall_pass'] for r in rows),
              'strata': [{'partition': p, 'count': len(rr), 'Hall_excluded': sum(not r['hall_pass'] for r in rr),
                          'allowed_assignments_range': [min(r['allowed_assignments'] for r in rr), max(r['allowed_assignments'] for r in rr)],
                          'smallest_domain_range': [min(r['smallest_domain'] for r in rr), max(r['smallest_domain'] for r in rr)],
                          'stabilizer_orders': dict(sorted(collections.Counter(r['automorphisms'] for r in rr).items()))}
                         for p, rr in sorted(strata.items())]}
    Path(destination).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main(*sys.argv[1:])
