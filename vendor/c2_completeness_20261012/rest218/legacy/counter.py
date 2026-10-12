"""Balanced, truncated, bidirectional totalizer for E3 exact sums <= 2."""
from collections import Counter
from math import gcd
from c2_reference import CNF, negate


class CounterCNF(CNF):
    def __init__(self, retain=False):
        super().__init__(retain)
        self.small = False
        self.small_equalities = set()

    def exact(self, terms, target):
        if not self.small:
            return super().exact(terms, target)
        weights = Counter()
        for term in terms:
            if term is True:
                target -= 1
            elif term is not False:
                if not isinstance(term, int) or not 0 < term <= self.variables:
                    raise ValueError('Expected positive variable or Boolean constant')
                weights[term] += 1
        divisor = 0
        for w in weights.values():
            divisor = gcd(divisor, w)
        if divisor > 1:
            if target % divisor:
                self.clause(False)
                return
            weights = Counter({v: w // divisor for v, w in weights.items()})
            target //= divisor
        items = tuple(sorted(weights.items()))
        key = (items, target)
        if key in self.small_equalities:
            return
        self.small_equalities.add(key)
        if target < 0 or target > sum(weights.values()):
            self.clause(False)
            return
        if target > 2:
            raise ValueError('Specialized encoder only accepts normalized targets <= 2')
        if target == 0:
            for v, _ in items:
                self.clause(-v)
            return
        # Any variable whose weight exceeds the target must be false.
        leaves = []
        for v, w in items:
            if w > target:
                self.clause(-v)
            else:
                leaves.append([v] * w)
        if sum(map(len, leaves)) < target:
            self.clause(False)
            return
        cap = target + 1

        def merge(left, right):
            result = [self.variable() for _ in range(min(cap, len(left) + len(right)))]
            a, b = [True] + left + [False], [True] + right + [False]
            for i in range(len(left) + 1):
                for j in range(len(right) + 1):
                    t = i + j
                    if 1 <= t <= len(result):
                        self.clause(negate(a[i]), negate(b[j]), result[t - 1])
                    if t + 1 <= len(result):
                        self.clause(a[i + 1], b[j + 1], -result[t])
            return result

        def tree(start, end):
            if end - start == 1:
                return leaves[start]
            mid = (start + end) // 2
            return merge(tree(start, mid), tree(mid, end))

        outputs = tree(0, len(leaves))
        self.clause(outputs[target - 1])
        if len(outputs) > target:
            self.clause(-outputs[target])


def encode_variant(cnf, frame):
    """Identical E1/E2; only E3 sum encoder differs from encode_base."""
    k, labels = frame.k, frame.labels
    n = len(labels)
    phases = []
    for phase in ('E1_DEGREES', 'E2_MIXED', 'E3_COMMON_NEIGHBORS'):
        before = cnf.variables, cnf.clauses
        cnf.small = phase == 'E3_COMMON_NEIGHBORS'
        for x in range(n):
            if phase == 'E1_DEGREES':
                cnf.exact([frame.edge(x, z) for z in range(n)], k - 2)
            elif phase == 'E2_MIXED':
                for a in range(k):
                    cnf.exact([frame.edge(x, z) for z in range(n) if a in labels[z]],
                              2 - int(a in labels[x]) - int((a ^ 1) in labels[x]))
            else:
                for y in range(x + 1, n):
                    terms = [cnf.conjunction(frame.edge(x, z), frame.edge(z, y)) for z in range(n)]
                    terms.append(frame.edge(x, y))
                    cnf.exact(terms, 2 - len(set(labels[x]) & set(labels[y])))
        phases.append({'phase': phase, 'added_variables': cnf.variables - before[0],
                       'added_clauses': cnf.clauses - before[1]})
    return phases
