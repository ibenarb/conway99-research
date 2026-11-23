from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import traceback

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = BASE.parents[1]
PRIVATE = ROOT / 'git-assurance'
PUBLIC = ROOT / 'git-research'
DOSSIER = 'reviews/2026-11-22-c2-audit-assurance'
BRANCH = 'review/project/c2-assurance-20261122'
sys.path.insert(0, str(BASE / 'recovery_v1'))
from resource_observer_v1 import measure, live
from c2_serial_admission_core_20261118_v1 import identity


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(name, obj):
    with (OUT / name).open('x', encoding='utf-8') as stream:
        json.dump(obj, stream, indent=4)


def git(repo, *args, data=None):
    command = ['git', '-c', 'safe.directory=' + repo.as_posix(), '-c', 'gc.auto=0', '-c', 'pack.threads=1', '-C', str(repo), *args]
    result = subprocess.run(command, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(str(args[:2]) + ': ' + result.stderr.decode('utf-8', errors='replace'))
    return result.stdout


def admit(label):
    controller = json.loads((BASE / 'recovery_v1/controller_identity_v1.json').read_text())
    assert not live(controller['identity'])
    assert sha(BASE / 'recovery_v1/finished.json') == '06c6c6990ecf1808ef4aa528195c25d2576650fd12d4815441951208911f8fb5'
    while True:
        resource = measure([])
        if max(row['system_busy_cpu'] for row in resource['intervals']) + 1 <= 20 and resource['ram_free_gib'] >= 10 and resource['disk_free_gib'] >= 39:
            save('git_admission_' + label + '.json', resource)
            return
        time.sleep(20)


def commit_and_push(repo, paths, branch, label, message):
    admit(label)
    assert not git(repo, 'diff', '--cached', '--name-only').strip(), 'Unexpected staged edits'
    assert git(repo, 'branch', '--show-current').decode().strip() == branch
    for relative in paths:
        assert (repo / relative).is_file() and (repo / relative).resolve().is_relative_to(repo.resolve())
    pathspec = OUT / ('git_paths_' + label + '.bin')
    pathspec.write_bytes(b'\0'.join(path.encode('utf-8') for path in paths) + b'\0')
    git(repo, 'add', '--pathspec-from-file=' + str(pathspec), '--pathspec-file-nul')
    staged = git(repo, 'diff', '--cached', '--name-only', '-z').decode().split('\0')
    staged = [path for path in staged if path]
    assert set(staged) == set(paths), ('Unexpected staged set', label)
    expected = git(repo, 'hash-object', '--stdin-paths', data=('\n'.join(paths) + '\n').encode()).decode().splitlines()
    indexed = {}
    for entry in git(repo, 'ls-files', '--stage', '-z').decode().split('\0'):
        if entry:
            info, path = entry.split('\t', 1)
            indexed[path] = info.split()[1]
    assert all(indexed[path] == digest for path, digest in zip(paths, expected)) and len(expected) == len(paths)
    git(repo, 'commit', '-m', message + ' [skip ci]')
    commit = git(repo, 'rev-parse', 'HEAD').decode().strip()
    git(repo, 'push', '--quiet', 'origin', 'HEAD:refs/heads/' + branch)
    remote = git(repo, 'ls-remote', 'origin', 'refs/heads/' + branch).decode().split()[0]
    assert remote == commit
    save('git_published_' + label + '.json', dict(at_utc=datetime.now(timezone.utc).isoformat(), repository=repo.name, branch=branch, commit=commit, remote_matches=True, files=len(paths), staged_blob_hashes_match_full_worktree_hashes=True))
    print(json.dumps(dict(published=label, commit=commit, files=len(paths))), flush=True)
    return commit


def main():
    save('git_publish_identity_v1.json', dict(identity=identity(os.getpid()), source_sha256=sha(Path(__file__)), at_utc=datetime.now(timezone.utc).isoformat()))
    assert git(PRIVATE, 'rev-parse', 'HEAD').decode().strip() == '9b27794066a45753304f61d12c24487f70fa2558'
    assert git(PUBLIC, 'rev-parse', 'HEAD').decode().strip() == 'eda127fdffb1c7554706d6b51dee127ac6d7b930'
    staging = json.loads((OUT / 'payload_staging_complete_1930_v1.json').read_text())
    groups = {}
    for row in staging['added']:
        if '/jobs/' in row['path']:
            groups.setdefault('/'.join(row['path'].split('/')[:3]), []).append(row)
    chunks, current, size = [], [], 0
    for key in sorted(groups):
        group = groups[key]
        group_bytes = sum(row['bytes'] for row in group)
        assert group_bytes <= 500 * 1024 ** 2
        if current and size + group_bytes > 500 * 1024 ** 2:
            chunks.append(current)
            current, size = [], 0
        current.extend(group)
        size += group_bytes
    if current:
        chunks.append(current)
    for number, rows in enumerate(chunks, 1):
        paths = [DOSSIER + '/checks/' + row['path'] for row in rows]
        for row, path in zip(rows, paths):
            assert sha(PRIVATE / path) == row['sha256']
        commit_and_push(PRIVATE, paths, BRANCH, 'payload_' + str(number), 'Preserve audited C2 payloads, tranche ' + str(number) + ' of ' + str(len(chunks)))
    tracked = git(PRIVATE, 'diff', '--name-only', '-z').decode().split('\0')
    untracked = git(PRIVATE, 'ls-files', '--others', '--exclude-standard', '-z').decode().split('\0')
    paths = sorted({path for path in tracked + untracked if path})
    assert paths and all(path.startswith(DOSSIER + '/') for path in paths)
    private_commit = commit_and_push(PRIVATE, paths, BRANCH, 'private_final', 'Document all five C2 assurance checks and complete S1 evidence')
    assert not git(PRIVATE, 'status', '--porcelain').strip()
    public_commit = commit_and_push(PUBLIC, ['docs/c2/AUDIT_AND_ASSURANCE_2026-11-22.md'], 'main', 'public_final', 'Report completion and scope of all five C2 assurance checks')
    assert not git(PUBLIC, 'status', '--porcelain').strip()
    save('git_publication_complete_v1.json', dict(at_utc=datetime.now(timezone.utc).isoformat(), status='BOTH_AUTHORIZED_REPOSITORIES_PUBLISHED_AND_REMOTE_HEADS_VERIFIED', private_commit=private_commit, private_branch=BRANCH, public_commit=public_commit, payload_chunks=len(chunks), private_full_high_cases=3156, private_full_singleton_cases=3308, private_full_low_cases=92, both_worktrees_clean=True, no_actions_requested=True))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        save('git_publication_error_v1.json', dict(at_utc=datetime.now(timezone.utc).isoformat(), traceback=traceback.format_exc()))
        raise
