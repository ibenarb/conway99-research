"""Verify saved explicit prefixes/witnesses, without replay or SAT calls."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from independent_check import check, equations_and_checks, verify_witness


def rejected(name, action):
    try:
        action()
    except ValueError as error:
        return {'name': name, 'rejected': True, 'reason': str(error)}
    raise AssertionError('undetected corruption: ' + name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    results = json.loads((args.directory / 'RESULTS.json').read_text())
    assert results['complete'] and len(results['results']) == 17
    checked = []
    for record in results['results']:
        path = args.directory / record['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256']
        data = json.loads(path.read_text())
        _, equations, counts = equations_and_checks(data)
        assert counts == record['counts']
        assert data['independent_result']['status'] == 'PASS_NECESSARY_PREFIX_AND_JOINT_STARS'
        verify_witness(equations, data['independent_result']['witness'])
        checked.append(data)
    # Full 3x3 rook graph, with boundary opposite pairs (0,2), (1,3).
    labels = [[0, 1], [0, 3], [1, 2], [2, 3]]
    coords = [(1, 1), (2, 1), (1, 2), (2, 2)]
    rook = {'m': 2, 'labels': labels, 'matching': [], 'assignments': [],
            'rows': {str(i): [j for j in range(4) if j != i and
                             (coords[i][0] == coords[j][0] or coords[i][1] == coords[j][1])]
                     for i in range(4)}}
    positive = check(rook)
    assert positive['status'] == 'PASS_NECESSARY_PREFIX_AND_JOINT_STARS'
    assert positive['counts']['full_vertices'] == 9
    controls = []
    sample = checked[0]
    broken = copy.deepcopy(sample)
    broken['labels'][0], broken['labels'][1] = broken['labels'][1], broken['labels'][0]
    controls.append(rejected('swapped_labels', lambda: equations_and_checks(broken)))
    broken = copy.deepcopy(sample)
    broken['rows']['0'][0] = 0
    controls.append(rejected('self_loop', lambda: equations_and_checks(broken)))
    broken = copy.deepcopy(sample)
    broken['rows']['0'].pop()
    controls.append(rejected('deleted_edge', lambda: equations_and_checks(broken)))
    broken = copy.deepcopy(sample)
    broken['rows']['0'][0] = broken['rows']['0'][1]
    controls.append(rejected('duplicate_neighbor', lambda: equations_and_checks(broken)))
    broken = copy.deepcopy(sample)
    built_neighbor = broken['rows']['0'][0]
    neighbor_row = broken['rows'][str(built_neighbor)]
    neighbor_row[neighbor_row.index(0)] = next(v for v in range(84)
                                             if v not in neighbor_row and v != built_neighbor)
    controls.append(rejected('asymmetric_edge_preserving_row_degree',
                             lambda: equations_and_checks(broken)))
    broken = copy.deepcopy(sample)
    broken['matching'][1] = broken['matching'][0]
    controls.append(rejected('duplicate_matching_pair', lambda: equations_and_checks(broken)))
    broken = copy.deepcopy(sample)
    u, v, bit = broken['assignments'][0]
    broken['assignments'].append([u, v, 1 - bit])
    controls.append(rejected('contradictory_assignment', lambda: equations_and_checks(broken)))
    _, equations, _ = equations_and_checks(sample)
    witness = copy.deepcopy(sample['independent_result']['witness'])
    assert witness
    witness[0][2] = 1 - witness[0][2]
    controls.append(rejected('flipped_SAT_witness_edge', lambda: verify_witness(equations, witness)))
    witness = copy.deepcopy(sample['independent_result']['witness'])
    witness.pop()
    controls.append(rejected('missing_SAT_witness_edge', lambda: verify_witness(equations, witness)))
    report = {'status': 'PASS', 'saved_prefixes_verified_without_replay_or_SAT': len(checked),
              'distinct_labeled_prefixes': len({json.dumps(d['rows'], sort_keys=True) for d in checked}),
              'distinct_root_ids': len({d['root_id'] for d in checked}),
              'positive_control': {'graph': 'srg(9,4,1,2), 3x3 rook', 'counts': positive['counts']},
              'negative_controls': controls,
              'independent_check_sha256': hashlib.sha256(Path(__file__).with_name('independent_check.py').read_bytes()).hexdigest()}
    (args.directory / 'CONTROLS.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
