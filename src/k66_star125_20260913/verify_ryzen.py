"""Verify packaged LRAT proofs against the user's original 125 star CNFs."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from strict_rup import verify as strict_verify


def require(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def save(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2)+'\n')
    os.replace(temp, path)


def memory_gib():
    for row in Path('/proc/meminfo').read_text().splitlines():
        if row.startswith('MemAvailable:'):
            return int(row.split()[1])/1024**2
    raise RuntimeError('MemAvailable unavailable')


def run_check(tool, cnf, proof, prefix, marker, progress):
    start = time.monotonic()
    last = start
    with open(str(prefix)+'.out', 'wb') as out, open(str(prefix)+'.err', 'wb') as err:
        process = subprocess.Popen([str(tool), str(cnf), str(proof)], stdout=out, stderr=err)
        try:
            while process.poll() is None:
                time.sleep(0.2)
                require(memory_gib() >= 1.0, 'Resource stop: less than 1 GiB available RAM')
                require(shutil.disk_usage(prefix.parent).free >= 5*1024**3,
                        'Resource stop: less than 5 GiB free disk')
                if time.monotonic()-last >= 600:
                    progress()
                    last = time.monotonic()
        except BaseException:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise
    stdout = Path(str(prefix)+'.out').read_bytes()
    stderr = Path(str(prefix)+'.err').read_bytes()
    return dict(exit=process.returncode, positive_marker=marker in stdout.splitlines(),
                stderr_empty=not stderr, diagnostic_free=not any(word in stdout.upper()+stderr.upper() for word in [b'WARNING', b'ERROR']), seconds=time.monotonic()-start)


def main():
    home = Path.home()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=home/'conway99_workspace/o3_reconciliation_runs/k66_v4_cert_20260908_231256_132359/neighbor_star_preflight_20260909')
    parser.add_argument('--lrat', type=Path, default=home/'.local/bin/lrat-check')
    parser.add_argument('--cake', type=Path, default=home/'conway99_workspace/conway99_o3_qsat_preflight_0.1.12/dependencies/bin/cake_lpr')
    args = parser.parse_args()
    expected = {
        'lrat': '49f0bf5b418fec38dad3a199a9ae7eb52a4617269a6d360d49d3f580a9b98dfa',
        'cake': 'e63d772e463265d26ace5f52125506024126b36c4a34901e2ed61c4378742d0a',
    }
    for key in expected:
        require(sha(getattr(args, key)) == expected[key], key+' binary hash mismatch')
    require(args.base.is_dir(), 'Original star directory missing')
    archive = zipfile.ZipFile(Path(sys.argv[0]).resolve())
    manifest = json.loads(archive.read('proof_manifest.json'))
    records = manifest['records']
    require(len(records) == 125, 'Expected 125 proofs')
    for rec in records:
        relative = Path(rec['cnf'])
        require(not relative.is_absolute() and '..' not in relative.parts, 'Invalid path')
        require(sha(args.base/relative) == rec['cnf_sha256'], 'CNF hash mismatch: '+rec['cnf'])
        require(hashlib.sha256(archive.read(rec['proof'])).hexdigest() == rec['proof_sha256'], 'Proof hash mismatch')
    outdir = args.base/'certify_star125_20260913'/time.strftime('%Y%m%d_%H%M%S')
    outdir.mkdir(parents=True, exist_ok=False)
    state = dict(format='CONWAY99-STAR125-CHECK-1', status='RUNNING', records=[], tool_hashes=expected,
                 scope='125 original star CNFs only; full K66 model necessity and coverage remain separate.',
                 package_sha256=sha(Path(sys.argv[0]).resolve()))
    started = time.monotonic()
    def progress():
        elapsed = time.monotonic()-started
        done = len(state['records'])
        eta = round(elapsed/done*(125-done), 1) if done else 'unknown'
        print('STATUS',done,'/125 elapsed_seconds',round(elapsed,1),'ETA_seconds',eta,flush=True)
    try:
        controls = outdir/'controls'
        controls.mkdir()
        positive = controls/'unsat.cnf'
        negative = controls/'sat.cnf'
        proof = controls/'proof.lrat'
        positive.write_text('p cnf 1 2\n1 0\n-1 0\n')
        negative.write_text('p cnf 1 2\n1 0\n1 0\n')
        proof.write_text('3 0 1 2 0\n')
        require(strict_verify(positive, proof) == 1, 'Strict positive control failed')
        try:
            strict_verify(negative, proof)
        except ValueError:
            pass
        else:
            raise RuntimeError('Strict negative control accepted')
        state['controls'] = {'strict_rup': 'positive_and_negative_pass'}
        for name, marker in [('lrat', b'c VERIFIED'), ('cake', b's VERIFIED UNSAT')]:
            for label, cnf in [('positive', positive), ('negative', negative)]:
                result = run_check(getattr(args, name), cnf, proof, controls/(name+'_'+label), marker, progress)
                accepted = result['exit'] == 0 and result['positive_marker'] and result['stderr_empty'] and result['diagnostic_free']
                require(accepted == (label == 'positive'), name+' control failed: '+label)
                state['controls'][name+'_'+label] = result
        print('CONTROLS_PASS; verifying 125 supplied proofs; solver not needed',flush=True)
        for rec in records:
            cnf = args.base/rec['cnf']
            folder = outdir/Path(rec['cnf']).with_suffix('')
            folder.mkdir(parents=True)
            proof = folder/'proof.lrat'
            proof.write_bytes(archive.read(rec['proof']))
            row = dict(rec)
            row['strict_rup_additions'] = strict_verify(cnf, proof)
            for name, marker in [('lrat', b'c VERIFIED'), ('cake', b's VERIFIED UNSAT')]:
                result = run_check(getattr(args, name), cnf, proof, folder/name, marker, progress)
                row[name] = result
                require(result['exit'] == 0 and result['positive_marker'] and result['stderr_empty'] and result['diagnostic_free'],
                        name+' verification failed: '+rec['cnf'])
            require(sha(cnf) == rec['cnf_sha256'] and sha(proof) == rec['proof_sha256'], 'Post-check hash mismatch')
            row['status'] = 'LRAT_AND_CAKE_CERTIFIED'
            state['records'].append(row)
            save(outdir/'state.json', state)
            if len(state['records']) % 10 == 0:
                progress()
        state['status'] = 'ALL_125_LRAT_AND_CAKE_CERTIFIED'
    except BaseException as exc:
        state['status'] = 'STOPPED_ERROR'
        state['error'] = repr(exc)
        raise
    finally:
        state['seconds'] = time.monotonic()-started
        save(outdir/'state.json', state)
        report = outdir/'STAR125_ERGEBNIS.json'
        save(report, state)
        handoff = outdir/'k66_star125_checker_handoff.zip'
        with zipfile.ZipFile(handoff, 'w', zipfile.ZIP_DEFLATED) as z:
            for path in sorted(outdir.rglob('*')):
                if path.is_file() and path != handoff:
                    z.write(path, str(path.relative_to(outdir)))
        downloads = Path('/mnt/c/Users/rb/Downloads')
        if downloads.is_dir():
            destination = downloads/('k66_star125_checker_handoff_'+outdir.name+'.zip')
            shutil.copy2(handoff, destination)
            print('HANDOFF_WINDOWS',destination,flush=True)
            print('HANDOFF_SHA256',sha(destination),flush=True)
        print('RESULT',state['status'],report,flush=True)


if __name__ == '__main__':
    main()
