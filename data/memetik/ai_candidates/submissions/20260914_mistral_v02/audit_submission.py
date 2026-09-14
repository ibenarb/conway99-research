"""Bounded reproduction of the literal Mistral v02 construction; stdlib only."""
import collections
import hashlib
import itertools
import json
import pathlib
import sys


def audit(source):
    raw = source.read_bytes()
    text = raw.decode('utf-8')
    pairs = [pair for pair in itertools.combinations(range(14), 2)
             if pair[1] != (pair[0] + 7) % 14]
    subsets = list(map(set, pairs))
    partners = [{a, a + 7} for a in range(7)]
    neighbors = [
        {j for j, right in enumerate(subsets)
         if len(left & right) == 1
         and sum(pair <= left | right for pair in partners) == 1}
        for left in subsets
    ]
    violations = []
    for a in range(14):
        for j, pair in enumerate(pairs):
            actual = sum(a in pairs[k] for k in neighbors[j])
            expected = 2 - int(a in pair) - int((a + 7) % 14 in pair)
            if actual != expected:
                violations.append({'row': a, 'outer_pair': pair,
                                   'actual': actual, 'expected': expected})
    result = {
        'scope': 'Own reconstruction of the literal H iff-rule; not execution of supplied code (none present)',
        'source_bytes': len(raw),
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'end_marker_present': text.rstrip().endswith('ENDE DER ABGABE'),
        'fenced_code_block_openers': sum(line.lstrip().startswith('```') for line in text.splitlines()),
        'submitted_graphs': 0,
        'supplied_generators': 0,
        'accepted_candidates': 0,
        'omega': {
            'outer_vertices': len(pairs),
            'H_degree_histogram': dict(collections.Counter(map(len, neighbors))),
            'full_A_degree_histogram': {'14': 15, '4': 84},
            'PH_equations': 14 * len(pairs),
            'PH_violations': len(violations),
            'first_violation': violations[0],
        },
        'triangle_counts': {
            'disjoint_33_triangles_vertex_degree': 2,
            'triangles_per_vertex_required_for_degree14_and_lambda1': 7,
            'total_triangles_required': 99 * 7 // 3,
            'full_STS99_blocks_per_vertex': 49,
            'full_STS99_shadow_degree': 98,
        },
        'first_edge_in_empty_graph_common_neighbors': 0,
    }
    return result


if __name__ == '__main__':
    source = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).with_name('original.md')
    print(json.dumps(audit(source), ensure_ascii=False, indent=4))
