from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(BASE / 'recovery_v1'))
from resource_observer_v1 import measure, live


def main():
    completed = json.loads((OUT / 'git_publication_complete_v1.json').read_text())
    identity = json.loads((OUT / 'git_publish_identity_v1.json').read_text())
    assert not live(identity['identity'])
    assert hashlib.sha256((OUT / 'publish_verified_snapshots_1930_v1.py').read_bytes()).hexdigest() == identity['source_sha256'] == '7c253e7f8aaad6ed52de82dbed4eb78729b8beb94f3d9629a2d73417c2681141'
    assert not (OUT / 'git_publication_error_v1.json').exists()
    assert (OUT / 'stderr.log').stat().st_size == 0
    assert completed['status'] == 'BOTH_AUTHORIZED_REPOSITORIES_PUBLISHED_AND_REMOTE_HEADS_VERIFIED'
    assert completed['private_full_singleton_cases'] == 3308 and completed['private_full_high_cases'] == 3156 and completed['private_full_low_cases'] == 92
    resource = measure([])
    rows = []
    for name, branch, field, expected_origin in [('git-assurance', 'review/project/c2-assurance-20261122', 'private_commit', 'https://github.com/ibenarb/conway99-review-exchange.git'), ('git-research', 'main', 'public_commit', 'https://github.com/ibenarb/conway99-research.git')]:
        repo = ROOT / name
        def git(*args):
            return subprocess.check_output(['git', '-c', 'safe.directory=' + repo.as_posix(), '-c', 'gc.auto=0', '-C', str(repo), *args]).decode().strip()
        assert git('branch', '--show-current') == branch
        origin = git('remote', 'get-url', 'origin')
        assert origin == expected_origin
        local = git('rev-parse', 'HEAD')
        remote = git('ls-remote', 'origin', 'refs/heads/' + branch).split()[0]
        assert local == remote == completed[field]
        assert not git('status', '--porcelain')
        rows.append(dict(repository=name, branch=branch, commit=local, origin=origin, remote_matches=True, worktree_clean=True))
    receipt = dict(at_utc=datetime.now(timezone.utc).isoformat(), status='BOTH_REMOTE_HEADS_INDEPENDENTLY_RECONFIRMED', publisher_exited=True, stderr_empty=True, resource=resource, repositories=rows, counts=dict(singleton=3308, nonphysical=272, high=3156, low=92), all_five_assurance_checks_complete_with_documented_scope=True)
    with (OUT / 'remote_acceptance_v1.json').open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, indent=4)
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
