"""Uncolored endpoint automorphisms and comparisons to explicitly audited inputs."""
import argparse
import json
from pathlib import Path
from symmetry_audit import inspect


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=Path, required=True)
    args = parser.parse_args()
    prior = json.loads((args.results / 'symmetry.json').read_text())
    certificates = {}
    for group in ('candidates', 'escape_founders'):
        for name, data in prior[group].items():
            certificates.setdefault(data['canonical_certificate_hex'], []).append(name)
    result = {}
    for path in sorted((args.results / 'run').glob('*__*.json')):
        record = json.loads(path.read_text())
        if 'witness' not in record:
            continue
        data = inspect(record['witness']['path'][-1]['graph6'])
        data['isomorphic_known_graphs'] = certificates.get(data['canonical_certificate_hex'], [])
        result[path.stem] = data
    (args.results / 'endpoint_symmetry.json').write_text(json.dumps(result, indent=4) + '\n')


if __name__ == '__main__':
    main()
