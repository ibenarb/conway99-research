"""Recompute exact historical complements using the source-reviewed matcher."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main(root):
    root = Path(root).resolve()
    w = root / 'c2_coverage_work'
    w.mkdir(parents=True, exist_ok=True)
    inputs = root / 'c2_coverage_inputs'
    result = {}
    vendor = root / 'c2_publication_git/vendor/c2_coverage_audit_20261012'
    subprocess.run(['g++', '-O3', '-std=c++17', str(vendor / 'coverage.cpp'), '-o', str(w / 'coverage')], check=True)
    controls = subprocess.run([sys.executable, str(vendor / 'test_coverage.py'), str(w / 'coverage')], check=True, capture_output=True, text=True)
    result['controls'] = controls.stdout.strip()
    with (w / 'generalize.json').open('w') as out:
        subprocess.run([str(w / 'coverage'), '7', str(inputs / 'generalize/work/coverage/patterns.txt'), str(root / 'c2_census_check/representatives.tsv'), str(w / 'after_generalize.tsv')], stdout=out, check=True)
    assert sha(root / 'c2_census_check/representatives.tsv') == 'd003dd431ce506b0bbf936441b970cf80d99027e7d35219b26763312bffbb538'
    for pattern, receipt in [(inputs / 'generalize/work/coverage/patterns.txt', inputs / 'generalize/work/coverage/coverage.json'), (inputs / 'handoff/g2__work__coverage__patterns.txt', inputs / 'handoff/g2__work__coverage__coverage.json')]:
        assert sha(pattern) == json.loads(receipt.read_text())['patterns_sha256']
    old = json.loads((inputs / 'generalize/work/coverage/coverage.json').read_text())
    new = json.loads((w / 'generalize.json').read_text())
    assert all(new[k] == old[k] for k in new)
    assert sha(w / 'after_generalize.tsv') == old['uncovered_sha256']
    result['generalize'] = dict(new, output_sha256=sha(w / 'after_generalize.tsv'))
    print('GENERALIZE_EXACT_COMPLEMENT_PASS', flush=True)
    with (w / 'after_generalize.tsv').open() as src, (w / 'after_one3.tsv').open('w') as rest, (w / 'one3.tsv').open('w') as ones:
        header = next(src)
        rest.write(header)
        ones.write(header)
        for line in src:
            (ones if line.split('\t')[3].split(',').count('3') == 1 else rest).write(line)
    assert sha(w / 'one3.tsv') == sha(inputs / 'one3/work/prepare/remaining.tsv')
    old2 = json.loads((inputs / 'handoff/g2__work__coverage__coverage.json').read_text())
    assert sha(w / 'after_one3.tsv') == old2['population_sha256']
    result['one3'] = {'removed': 1032, 'remaining': 2700983, 'removed_sha256': sha(w / 'one3.tsv'), 'remaining_sha256': sha(w / 'after_one3.tsv')}
    print('ONE3_EXACT_COMPLEMENT_PASS', flush=True)
    start = time.monotonic()
    with (w / 'generalize2.json').open('w') as out:
        subprocess.run([str(w / 'coverage'), '7', str(inputs / 'handoff/g2__work__coverage__patterns.txt'), str(w / 'after_one3.tsv'), str(w / 'after_generalize2.tsv')], stdout=out, check=True)
    new2 = json.loads((w / 'generalize2.json').read_text())
    assert all(new2[k] == old2[k] for k in new2)
    assert sha(w / 'after_generalize2.tsv') == old2['uncovered_sha256']
    result['generalize2'] = dict(new2, output_sha256=sha(w / 'after_generalize2.tsv'), elapsed_seconds=time.monotonic() - start)
    print('GENERALIZE2_EXACT_COMPLEMENT_PASS', flush=True)
    with (w / 'after_generalize2.tsv').open() as src, (w / 'remaining_234691.tsv').open('w') as rest, (w / 'two3.tsv').open('w') as twos:
        header = next(src)
        rest.write(header)
        twos.write(header)
        for line in src:
            (twos if line.split('\t')[3].split(',').count('3') == 2 else rest).write(line)
    assert sha(w / 'two3.tsv') == sha(inputs / 'handoff/two3__work__prepare__remaining.tsv')
    assert sha(w / 'remaining_234691.tsv') == sha(inputs / 'handoff/remaining_234691.tsv')
    result['two3'] = {'removed': 7, 'remaining': 234691, 'removed_sha256': sha(w / 'two3.tsv'), 'remaining_sha256': sha(w / 'remaining_234691.tsv')}
    for name, path in [('one3', inputs / 'one3/work/certify/certificates.json'), ('two3', inputs / 'handoff/two3__work__certify__certificates.json')]:
        codes = {int(line.split('\t')[0]) for line in (w / (name + '.tsv')).read_text().splitlines()[1:]}
        cases = json.loads(path.read_text())['cases']
        assert codes == {item['code'] for item in cases.values()} and len(codes) == len(cases)
    result['certificate_case_sets_exact'] = True
    result['pattern_files_match_bound_lemmas'] = True
    for prefix in ['generalize/work/coverage/', 'handoff/g2__work__coverage__']:
        rows = json.loads((inputs / (prefix + 'lemmas.json')).read_text())
        assert [tuple(map(int, line.split())) for line in (inputs / (prefix + 'patterns.txt')).read_text().splitlines()] == [(row['positive_mask'], row['negative_mask']) for row in rows]
    result['status'] = 'PASS'
    result['limits'] = ['Matcher is the historical source, newly reviewed and controlled, not an independent reimplementation.', 'Set equalities alone do not prove UNSAT; certificate binding is separate.']
    output = root / 'c2_publication_git/results/c2_coverage_audit_20261012/set_audit.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print('ALL_EXACT_COMPLEMENTS_PASS', flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
