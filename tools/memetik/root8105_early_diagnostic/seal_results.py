"""Seal a completed diagnostic; compact only redundant equation evaluations."""
import argparse
import gzip
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--interruption', type=Path)
    args = parser.parse_args()
    source, destination = args.source, args.destination
    receipt = json.loads((source / 'FINAL_RECEIPT.json').read_text())
    assert receipt['complete'] and receipt['paths'] == 960
    for name, digest in receipt['files'].items():
        assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='root8105-seal-') as directory:
        stage = Path(directory)
        counts = {'paths': 0, 'SAT_witnesses': 0, 'UNSAT_certificates': 0}
        negatives = []
        with gzip.GzipFile(filename=str(stage / 'WITNESSES.jsonl.gz'), mode='wb', mtime=0) as stream:
            for path in sorted(source.glob('r*.json')):
                data = json.loads(path.read_text())
                counts['paths'] += 1
                assert data['complete'] and len(data['states']) == 2
                for state in data['states']:
                    for mode, results in state['results'].items():
                        assert len({r['target'] for r in results}) == len(results)
                        if state['Q'][mode]:
                            assert len(results) == 84 - state['depth']
                        for result in results:
                            if result['status'] == 'SAT_DIRECT_VERIFIED':
                                counts['SAT_witnesses'] += 1
                                assert result['check']['status'] == 'DIRECT_INTEGER_CHECK_PASS'
                                # All integer witnesses remain. The removed
                                # evaluated margins/codegrees are recomputable.
                                result.pop('check')
                            else:
                                assert result['status'] == 'RUP_VERIFIED_UNSAT'
                                counts['UNSAT_certificates'] += 1
                                negatives.append({'root_id': data['root_id'], 'index': data['index'],
                                                  'depth': state['depth'], 'mode': mode, **result})
                stream.write((json.dumps(data, separators=(',', ':')) + '\n').encode())
        for path in source.iterdir():
            if path.suffix in ('.cnf', '.rup'):
                shutil.copyfile(path, stage / path.name)
        shutil.copyfile(source / 'FINAL_RECEIPT.json', stage / 'RAW_RECEIPT.json')
        if args.interruption:
            shutil.copyfile(args.interruption, stage / 'TECHNICAL_INTERRUPTION.json')
        summary = {k: v for k, v in receipt.items() if k != 'files'}
        summary.update(counts=counts, negatives=negatives,
                       representation='all row witnesses retained; redundant evaluated equation values omitted',
                       raw_receipt_scope='hashes refer to original raw JSON; compact representation has separate hashes')
        (stage / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
        final = {'complete': True, 'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.iterdir())}}
        (stage / 'FINAL_RECEIPT.json').write_text(json.dumps(final, indent=2) + '\n')
        with zipfile.ZipFile(destination / 'EVIDENCE_960.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(stage.iterdir()):
                archive.write(path, path.name)
        shutil.copyfile(stage / 'SUMMARY.json', destination / 'SUMMARY.json')
        with zipfile.ZipFile(destination / 'EVIDENCE_960.zip') as archive:
            assert all(hashlib.sha256(archive.read(n)).hexdigest() == h for n, h in final['files'].items())
        print(json.dumps({'counts': counts, 'archive_bytes': (destination / 'EVIDENCE_960.zip').stat().st_size,
                          'archive_sha256': hashlib.sha256((destination / 'EVIDENCE_960.zip').read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
