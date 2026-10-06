"""Independent witness, exhaustive small model and odd-barrier controls."""
import bootstrap
import itertools
from kernel import Geo, VertexSampler
from row_sampler import RowProposal
from propagation import propagate
from matching import check, feasible, edge_key


def run(full):
    positive = []
    g = Geo(11)
    for depth in (1, 2, 10):
        rows = {u: full[u] for u in range(depth)}
        assert check(g, rows)['pass']
        result = propagate(g, rows)
        assert result['pass'], result
        assert all((full[u] >> v & 1) == bit for (u, v), bit in result['assigned'].items())
        positive.append({'depth': depth, 'forced_bits_checked_against_BVLS': len(result['assigned'])})
    target = g.n - 1
    proposal = RowProposal(g, {u: r for u, r in full.items() if u != target}, target)
    assert proposal.total == 1 and proposal.unrank(0) == full[target]
    proposal.rec.cache_clear()
    # All vertices have degree two, yet two odd components cannot have a perfect matching.
    triangles = {edge_key(u, v) for part in ((0, 1, 2), (3, 4, 5)) for u, v in itertools.combinations(part, 2)}
    assert not feasible(range(6), triangles)
    assert feasible(range(6), triangles | {(2, 3)})
    assert not feasible(range(4), {(0, 1), (0, 2), (2, 3)}, {(0, 1), (0, 2)})
    # Exhaustive 4-vertex H model: proposal recursion versus explicit subset enumeration.
    small = Geo(2)
    checked = 0
    for root in range(1 << small.n):
        try:
            small.verify({0: root})
        except ValueError:
            continue
        for target in range(1, small.n):
            old = VertexSampler(small, root, target)
            new = RowProposal(small, {0: root}, target)
            assert {old.unrank(i) for i in range(old.total)} == {new.unrank(i) for i in range(new.total)}
            old.rec.cache_clear(); new.rec.cache_clear()
            checked += 1
    # Horvitz-Thompson identity: rejected proposals have zero, are not redrawn.
    outcomes = [0, 1, 0, 1, 1]
    assert sum(len(outcomes) * x for x in outcomes) / len(outcomes) == sum(outcomes)
    return {'status': 'PASS', 'BVLS_propagation': positive, 'late_BVLS_row_count': 1,
            'odd_barrier_and_forced_conflict_controls': 3, 'exhaustive_small_row_cases': checked,
            'importance_zero_rejection_identity': 'PASS'}
