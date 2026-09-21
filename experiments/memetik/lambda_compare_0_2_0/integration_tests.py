"""Short subprocess tests. Host probe is replaced ONLY inside this test harness."""
import bootstrap
from common import atomic, sha
from runtime import read, process
from queueing import Queue, validate_receipt
from pathlib import Path
import copy
import json
import tempfile
import time


class TestQueue(Queue):
    def __init__(self, directory, pause=False):
        super().__init__(directory)
        self.pause_once = pause
    def check(self):
        usage = {pid:process(pid) for pid in self.active}
        if self.pause_once and any(p['cpu']>.8 for p in usage.values()):
            self.stop = True
            self.last_reason = ['TEST_REQUESTED_PAUSE']
        self.host = {'hazards':[],'test_fixture':True}
        return usage
    def status(self, *args, **kwargs):
        pass


def run():
    config = read(bootstrap.HERE/'config.json')
    founders = read(bootstrap.HERE/'founders.json')
    tests = []
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root/'tasks').mkdir()
        atomic(root/'budget.json',{'per_job_cpu_seconds':12})
        jobs = [{'id':'test-'+v,'kind':'compare','variant':v,'target':'W','arm':'lambda',
                 'seed':391,'replicate':0,'worker_cpu_seconds':12,'config':config,'founders':founders}
                for v in ('B0','P','T','TC')]
        pool = TestQueue(root,pause=True)
        try:
            pool.run(jobs,4,'test')
        except RuntimeError as error:
            assert str(error).startswith('PAUSED:')
        else:
            raise AssertionError('Pause not reached')
        finally:
            pool.lock.close()
        paused = {}
        for task in jobs:
            d = root/'tasks'/task['id']
            receipt = validate_receipt(d)
            assert receipt['status']=='PAUSED'
            assert read(d/'checkpoint.json')['state']['batch'] is not None
            paused[task['id']] = receipt['cpu_seconds']
        pool = TestQueue(root)
        try:
            pool.run(jobs,4,'test')
        finally:
            pool.lock.close()
        hashes = {}
        first = {}
        for task in jobs:
            d = root/'tasks'/task['id']
            receipt = validate_receipt(d)
            assert receipt['status']=='COMPLETE' and 7<=receipt['cpu_seconds']<=12
            assert len(receipt['sessions'])==2
            assert abs(sum(s['cpu_seconds'] for s in receipt['sessions'])-receipt['cpu_seconds'])<1e-6
            first[task['id']] = read(d/'checkpoint.json')['state']
            hashes[task['id']] = receipt['task_sha256']
        # Complete tasks really are skipped; no new CPU session appears.
        pool = TestQueue(root)
        try:
            pool.run(jobs,4,'test')
        finally:
            pool.lock.close()
        assert all(len(validate_receipt(root/'tasks'/t['id'])['sessions'])==2 for t in jobs)
        atomic(root/'budget.json',{'per_job_cpu_seconds':20})
        pool = TestQueue(root)
        try:
            pool.run(jobs,4,'test')
        finally:
            pool.lock.close()
        for task in jobs:
            d = root/'tasks'/task['id']
            receipt = validate_receipt(d)
            state = read(d/'checkpoint.json')['state']
            result = read(d/'result.json')
            assert receipt['task_sha256']==hashes[task['id']]
            assert len(receipt['sessions'])==3 and 15<=receipt['budget_cpu_seconds']<=20 and receipt['cpu_seconds']<=20
            assert result['endpoint_cpu_seconds']==20
            assert state['curves'][:len(first[task['id']]['curves'])]==first[task['id']]['curves']
            assert state['complete_batches']>=first[task['id']]['complete_batches']
            assert '12' in result['milestones'] and '20' in result['milestones']
            tests.append({'variant':task['variant'],'pause_cpu':paused[task['id']],
                          'total_cpu':receipt['cpu_seconds'],'sessions':receipt['sessions'],
                          'old_curve_prefix_and_milestone_retained':True,'task_unchanged':True})
        # Corrupt receipts and unresolved processes must block continuation.
        d = root/'tasks'/jobs[0]['id']
        result_bytes = (d/'result.json').read_bytes()
        (d/'result.json').write_bytes(result_bytes+b' ')
        try:
            validate_receipt(d)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Changed result accepted')
        (d/'result.json').write_bytes(result_bytes)
        atomic(d/'active.json',{'pid':99999999})
        pool = TestQueue(root)
        try:
            try:
                pool.run(jobs,4,'test')
            except RuntimeError as error:
                assert 'Unresolved CPU receipt' in str(error)
            else:
                raise AssertionError('Unclean task accepted')
        finally:
            pool.lock.close()
    return {'status':'INTEGRATION_PASS','tests':tests,'changed_result_rejected':True,
            'unresolved_cpu_rejected':True,'host_probe':'fixture only; actual WSL guard not exercised on this host'}


if __name__=='__main__':
    import sys
    report = run()
    if len(sys.argv)>1:
        atomic(Path(sys.argv[1]),report)
    print(json.dumps(report,indent=2))
