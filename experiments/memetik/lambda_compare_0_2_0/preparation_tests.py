"""Manifest pairing, frozen-source integrity and locked snapshot controls."""
import bootstrap
from common import atomic, sha
from runtime import read
import run as campaign
from pathlib import Path
import fcntl
import json
import tempfile


def rejected(action, expected):
    try:
        action()
    except (RuntimeError,BlockingIOError) as error:
        assert expected in str(error), str(error)
    else:
        raise AssertionError('Expected rejection: '+expected)


def run():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)/'campaign'
        campaign.prepare(root)
        campaign.verify(root)
        manifest = read(root/'manifest.json')
        jobs = manifest['jobs']
        assert len(jobs)==192 and sum(t['worker_cpu_seconds'] for t in jobs)==691200
        for rep in range(12):
            group = [t for t in jobs if t['replicate']==rep]
            assert len(group)==16 and len({t['seed'] for t in group})==1
            assert {(t['variant'],t['target']) for t in group}=={(v,t) for v in campaign.VARIANTS for t in campaign.TARGETS}
        assert len({t['seed'] for t in jobs})==12
        assert len({sha(json.dumps(t['founders'],sort_keys=True).encode()) for t in jobs})==1
        assert len({f['class'] for f in jobs[0]['founders']})==16
        source = root/'bundle'/campaign.RELATIVE/'worker.py'
        original = source.read_bytes()
        source.write_bytes(original+b'\n# changed\n')
        rejected(lambda:campaign.verify(root),'Frozen source changed')
        source.write_bytes(original)
        budget = read(root/'budget.json')
        atomic(root/'budget.json',{**budget,'per_job_cpu_seconds':7200})
        rejected(lambda:campaign.verify(root),'Budget/ledger mismatch')
        atomic(root/'budget.json',budget)
        lock = campaign.unlocked(root)
        try:
            rejected(lambda:campaign.unlocked(root),'Resource temporarily unavailable')
        finally:
            lock.close()
        d = root/'tasks'/'test'
        d.mkdir(parents=True)
        atomic(d/'active.json',{'pid':99999999})
        rejected(lambda:campaign.unlocked(root),'Unclean process/CPU state')
        (d/'active.json').unlink()
        campaign.verify(root)
        fingerprints = read(root/'fingerprint.json')
    return {'status':'PREPARATION_PASS','jobs':192,'comparison_cpu_hours':192,'workers':18,
            'paired_seed_count':12,'identical_founders':True,'distinct_founder_classes':16,
            'changed_frozen_source_rejected':True,'changed_budget_without_ledger_rejected':True,
            'concurrent_lock_rejected':True,'unresolved_active_marker_rejected':True,
            'bundle_file_count':len(fingerprints['files']),'environment':fingerprints['environment']}


if __name__=='__main__':
    import sys
    result = run()
    if len(sys.argv)>1:
        atomic(Path(sys.argv[1]),result)
    print(json.dumps(result,indent=2))
