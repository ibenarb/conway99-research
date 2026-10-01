"""Pinned predecessor evidence and explicitly separate recovery accounting."""
import fcntl
import shutil
from common import *


def source_paths(old):
    return {str(p.relative_to(old)): p for p in old.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.name != 'controller.lock'}


def verify_predecessor(old, archive):
    plan = read(HERE / 'RECOVERY_PLAN.json')
    if digest(archive) != plan['archive_sha256']:
        raise RuntimeError('Predecessor archive hash differs from audited diagnosis')
    paths = source_paths(old)
    if set(paths) != set(plan['source_files']):
        raise RuntimeError('Predecessor file inventory changed; preserve and diagnose')
    for name, expected in plan['source_files'].items():
        if digest(paths[name]) != expected:
            raise RuntimeError('Predecessor file changed: ' + name)
    # Match the run path, not historic PIDs, which can be recycled after a reboot.
    for proc in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            data = proc.read_bytes()
        except (FileNotFoundError, ProcessLookupError):
            continue
        if str(old).encode() in data and int(proc.parent.name) != os.getpid():
            raise RuntimeError('A process still refers to the predecessor: ' + proc.parent.name)
    ledger = read(old / 'ledger.json')
    manifest = read(old / 'program/MANIFEST.json')
    tasks = {t['id']: t for t in manifest['tasks']}
    new = read(HERE / 'MANIFEST.json')['tasks']
    assert ledger['done'] == plan['completed']
    assert {t['id'] for t in new} == set(tasks) - set(ledger['done'])
    assert all(t == tasks[t['id']] for t in new)
    assert sorted(v['category'] for v in ledger['active'].values()) == plan['rerun_interrupted']
    return plan


def prepare_recovery(workspace, archive):
    from run import prepare
    plan = read(HERE / 'RECOVERY_PLAN.json')
    old = workspace / plan['predecessor_run']
    run = workspace / plan['new_run']
    if run.exists():
        raise FileExistsError('Recovery directory exists. Inspect it; never overwrite or rerun starter.')
    with (old / 'controller.lock').open('rb') as owner:
        fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
        verify_predecessor(old, archive)
        prepare(run)
        evidence = run / 'predecessor'
        evidence.mkdir()
        shutil.copyfile(archive, evidence / plan['archive_name'])
        if digest(evidence / plan['archive_name']) != plan['archive_sha256']:
            raise RuntimeError('Copied predecessor archive hash mismatch')
        atomic(run / 'RECOVERY.json', {
            'version': plan['version'],
            'plan_sha256': digest(HERE / 'RECOVERY_PLAN.json'),
            'archive_sha256': plan['archive_sha256'],
            'predecessor_directory': str(old),
            'predecessor_completed_tasks': len(plan['completed']),
            'new_segment_tasks': 184,
            'rerun_interrupted': plan['rerun_interrupted'],
            'first_attempt': plan['first_attempt'],
            'previous_settled_cpu_seconds': plan['previous_settled_cpu_seconds'],
            'previous_unsettled_cpu_seconds': None,
            'comparison_rule': 'For 12 interrupted cells use the new full attempt; old observations remain separate. No old incumbent hints imported.',
        })
        state = read(run / 'ledger.json')
        state['used']['aux'] += 120
        state['cli_reservations'].append({'action': 'recovery_validation_and_copy', 'cpu_seconds': 120})
        atomic(run / 'ledger.json', state)
        verify_link(run)
        if cpu() >= 119:
            raise RuntimeError('Setup exceeded reserved CPU; prepared directory retained, no launch')
    print('RECOVERY_PREPARED ' + str(run), flush=True)
    return run


def verify_link(run):
    plan = read(HERE / 'RECOVERY_PLAN.json')
    link = read(run / 'RECOVERY.json')
    assert link['plan_sha256'] == digest(HERE / 'RECOVERY_PLAN.json')
    assert link['archive_sha256'] == plan['archive_sha256']
    assert digest(run / 'predecessor' / plan['archive_name']) == plan['archive_sha256']
    assert link['previous_settled_cpu_seconds'] == plan['previous_settled_cpu_seconds']
    assert link['previous_unsettled_cpu_seconds'] is None
    assert link['rerun_interrupted'] == plan['rerun_interrupted']
    assert link['first_attempt'] == plan['first_attempt']
    assert link['predecessor_completed_tasks'] == len(plan['completed']) == 336
    assert link['new_segment_tasks'] == 184
    return plan


def summary(run, result):
    plan = verify_link(run)
    ledger = read(run / 'ledger.json')
    result['recovery'] = {
        'predecessor_completed_tasks': 336,
        'new_segment_completed_tasks': len(ledger['done']),
        'campaign_jobs_complete': 336 + len(ledger['done']),
        'campaign_jobs_total': 520,
        'previous_settled_cpu_hours': plan['previous_settled_cpu_seconds'] / 3600,
        'previous_unsettled_cpu_hours': None,
        'known_settled_combined_cpu_hours': (plan['previous_settled_cpu_seconds'] + sum(ledger['used'].values())) / 3600,
        'exact_combined_cpu_hours': None,
        'predecessor_audit_scope': 'Pinned partial audit; no closed-session CPU or host-wall certification for the interrupted predecessor.',
    }
    return result
