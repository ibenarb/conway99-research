"""Compile an independent census-isomorphism checker, run controls and audit all records."""
import argparse
import hashlib
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def encode(edges):
    bit = 0
    code = 0
    for i in range(7):
        for j in range(7):
            if i != j:
                code |= int((i, j) in edges) << bit
                bit += 1
    return code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--census-tsv', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    source = Path(__file__).with_name('audit_isomorphism.cpp')
    input_path = Path(args.census_tsv)
    output = Path(args.output)
    expected_sha = 'd003dd431ce506b0bbf936441b970cf80d99027e7d35219b26763312bffbb538'
    before = sha(input_path)
    assert before == expected_sha
    header = 'code\taut\tmutual_edges\tdegrees\tstratum\n'
    with tempfile.TemporaryDirectory(prefix='c2_iso_audit_') as temp:
        root = Path(temp)
        binary = root / 'checker'
        flags = ['-O2', '-std=c++17']
        subprocess.run(['g++', *flags, str(source), '-o', str(binary)], check=True, capture_output=True, text=True)
        compiler = subprocess.run(['g++', '--version'], check=True, capture_output=True, text=True).stdout.splitlines()[0]
        controls = [
            (set(), 5040),
            ({(i, j) for i in range(7) for j in range(7) if i != j}, 5040),
            ({(i, (i + 1) % 7) for i in range(7)}, 7),
            ({(i, j) for i in range(7) for j in range(7) if i < j}, 1),
            ({(i, (i + k) % 7) for i in range(7) for k in (1, 6)}, 14)
        ]
        positive = root / 'positive.tsv'
        positive.write_text(header + ''.join(f'{encode(edges)}\t{aut}\t0\tcontrol\tcontrol\n' for edges, aut in controls))
        cp = subprocess.run([str(binary), str(positive)], capture_output=True, text=True)
        assert cp.returncode == 0, cp.stderr
        assert json.loads(cp.stdout)['automorphism_histogram'] == {'5040': 2, '7': 1, '1': 1, '14': 1}
        wrong = root / 'wrong_aut.tsv'
        wrong.write_text(header + '0\t1\t0\tcontrol\tcontrol\n')
        cw = subprocess.run([str(binary), str(wrong)], capture_output=True, text=True)
        assert cw.returncode != 0 and 'Automorphism order mismatch' in cw.stderr
        duplicate = root / 'isomorphic_duplicate.tsv'
        forward = {(i, (i + 1) % 7) for i in range(7)}
        backward = {(i, (i - 1) % 7) for i in range(7)}
        assert encode(forward) != encode(backward)
        duplicate.write_text(header + ''.join(f'{encode(edges)}\t7\t0\tcontrol\tcontrol\n' for edges in (forward, backward)))
        cd = subprocess.run([str(binary), str(duplicate)], capture_output=True, text=True)
        assert cd.returncode != 0 and 'Isomorphic duplicate' in cd.stderr
        result = subprocess.run([str(binary), str(input_path)], capture_output=True, text=True)
        output.with_suffix('.log').write_text(result.stderr + result.stdout)
        assert result.returncode == 0, result.stderr
        audit = json.loads(result.stdout)
        assert audit['mode'] == 'full' and audit['status'] == 'PASS'
        assert audit['records'] == 7388648 and audit['labelled_orbit_sum'] == 37030041152
        after = sha(input_path)
        assert after == before
        audit.update({
            'checked_at': datetime.now(ZoneInfo('Europe/Berlin')).isoformat(),
            'input_sha256_before': before, 'input_sha256_after': after,
            'source_sha256': sha(source), 'runner_sha256': sha(__file__),
            'compiler': compiler, 'compiler_flags': flags,
            'all_stored_automorphism_orders_independently_confirmed': True,
            'no_isomorphic_duplicate_among_all_records': True,
            'canonicalization_colors': ['outdegree', 'indegree'],
            'controls': {'known_graphs': 5, 'wrong_aut_rejected': True, 'nonidentical_isomorphic_codes_rejected': True},
            'limits': ['No fresh exhaustive generation of all admissible digraphs.',
                       'No new proof that the mathematical filters preserve all relevant C2 cases.',
                       'No SAT or UNSAT certificate checking.']
        })
    output.write_text(json.dumps(audit, indent=2, sort_keys=True) + '\n')
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
