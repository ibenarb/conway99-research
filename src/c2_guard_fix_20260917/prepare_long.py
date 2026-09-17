"""Reuse verified totalizer inputs without regenerating or overwriting them."""
import fcntl
import json
from pathlib import Path
from common import ROOT, VERSION, sha, save
from windows_guard import host_probe


def main():
    base = Path.home() / 'conway99_workspace'
    lock = (base / 'c2_matching_v1/campaign.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    old = base / 'c2_counter_ab_v1'
    setup = json.loads((old / 'setup.json').read_text())
    manifest = json.loads((old / 'partitions/manifest.json').read_text())
    if sha(setup['solver']) != '51e256422129042b730eff10a5c0e91e70c69ddc878c65ed332dd56902a57e3c':
        raise RuntimeError('Solver identity mismatch')
    if sha(old / 'partitions/totalizer.cnf') != '7c105a67b0f7865f2ceec085ac9e5017213208e657e728381406323052acf3dd':
        raise RuntimeError('Totalizer identity mismatch')
    jobs = [j for j in manifest['jobs'] if j['group'] == 'totalizer']
    if len(jobs) != 11 or len({j['id'] for j in jobs}) != 11:
        raise RuntimeError('Expected eleven totalizer cases')
    for j in jobs:
        if sha(j['cnf']) != j['cnf_sha256'] or j['seed'] != 0:
            raise RuntimeError('Case identity mismatch')
    host = host_probe()
    if host['free_bytes'] < 55 * 1024**3:
        raise RuntimeError('Host disk reserve')
    ROOT.mkdir(parents=True, exist_ok=True)
    parts = ROOT / 'partitions'
    parts.mkdir(exist_ok=False)
    save(parts / 'manifest.json', dict(manifest, jobs=jobs))
    save(ROOT / 'setup.json', dict(setup, version=VERSION, jobs=11,
                                  source=str(Path(__file__).resolve().parent)))
    print(json.dumps({'status':'TOTALIZER_LONG_PREPARED', 'jobs':11, 'seconds_per_job':64800,
                      'proof_logging':False, 'inputs_regenerated':False,
                      'windows_free_GiB':round(host['free_bytes']/1024**3, 2)}), flush=True)


if __name__ == '__main__':
    main()
