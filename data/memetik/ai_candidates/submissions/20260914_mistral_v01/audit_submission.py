"""Reproduce the bounded audit of Mistral/Vibe submission v01; Python 3 stdlib."""
import collections
import hashlib
import json
import math
import pathlib
import sys


def audit(path):
    raw = path.read_bytes()
    text = raw.decode('utf-8')
    tail = text.split('```json', 1)[1].lstrip()
    submission, end = json.JSONDecoder().raw_decode(tail)
    records = []
    for candidate in submission['candidates']:
        graph6 = candidate['graph6']
        values = [ord(char) - 63 for char in graph6]
        if not values or any(value < 0 or value > 63 for value in values):
            raise ValueError('Unexpected graph6 alphabet in this submission')
        if values[0] == 63:
            raise ValueError('This bounded audit expects the observed short header')
        order = values[0]
        expected = 1 + math.ceil(order * (order - 1) / 12)
        records.append({
            'candidate_id': candidate['candidate_id'],
            'arm': candidate['arm'],
            'status': 'FAIL',
            'encoded_order': order,
            'graph6_characters': len(graph6),
            'expected_characters_for_encoded_order': expected,
            'errors': ['ORDER_NOT_99', 'GRAPH6_LENGTH_MISMATCH'],
            'reported_order_99': candidate['hard_checks']['order_99'],
            'runtime_is_required_object': isinstance(candidate['runtime'], dict),
        })
    # Independent reconstruction of the explicitly stated F03 recipe,
    # not decoding or repairing Mistral's malformed graph6 data.
    adjacency = [
        {(vertex + step) % 99 for step in list(range(1, 8)) + list(range(-7, 0))}
        for vertex in range(99)
    ]
    residuals = collections.Counter()
    edge_common = collections.Counter()
    for left in range(99):
        for right in range(left + 1, 99):
            common = len(adjacency[left] & adjacency[right])
            edge = right in adjacency[left]
            residuals[common + int(edge) - 2] += 1
            if edge:
                edge_common[common] += 1
    result = {
        'audit_scope': 'Specific received Mistral v01; no general admission or isomorphism test',
        'source_bytes': len(raw),
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'closed_json_fence': tail[end:].strip().startswith('```'),
        'json_recovered_without_value_changes': True,
        'received_candidates': len(records),
        'accepted_candidates': 0,
        'records': records,
        'graph6_order_99': {
            'header': '~?@b',
            'characters_without_newline': 4 + math.ceil(99 * 98 / 12),
        },
        'F01': {
            'minimum_common_neighbors_for_internal_edge': 7,
            'internal_edges_violating_lambda': 11 * math.comb(9, 2),
        },
        'F02': {
            'johnson_base_degree': 2 * (14 - 2),
            'old_vertex_degree_after_adding_8_universal_vertices': 32,
            'new_universal_vertex_degree': 98,
        },
        'F03_reconstructed_recipe': {
            'order': 99,
            'degrees': sorted({len(neighbors) for neighbors in adjacency}),
            'edges': sum(edge_common.values()),
            'edge_common_neighbor_histogram': dict(sorted(edge_common.items())),
            'lambda_bad_edges': sum(count for common, count in edge_common.items() if common != 1),
            'W': sum(count for residual, count in residuals.items() if residual),
            'L1': sum(abs(residual) * count for residual, count in residuals.items()),
            'F': sum(residual ** 2 * count for residual, count in residuals.items()),
            'Linf': max(map(abs, residuals)),
            'residual_histogram': dict(sorted(residuals.items())),
        },
    }
    return submission, result


if __name__ == '__main__':
    source = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).with_name('original.md')
    submitted, result = audit(source)
    print(json.dumps(result, ensure_ascii=False, indent=4))
