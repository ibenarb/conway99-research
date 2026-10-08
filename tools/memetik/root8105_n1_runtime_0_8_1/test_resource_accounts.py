"""Replay only the newly reported real resource-stop receipts."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import platform_adapter as p
import runtime as r

ARCHIVE_SHA = 'b7c133be4e60d0bdb6481cecca74a0d4eb9cc668b2af7387ab666064bc106034'
SID = '59daf1139ae946e2880d924fc48ff556'


class ResourceAccounts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        archive = Path(__file__).with_name('STOP_DIAGNOSIS.zip')
        self.assertEqual(r.sha(archive), ARCHIVE_SHA)
        with zipfile.ZipFile(archive) as z:
            z.extractall(self.base)
        self.directory = self.base/'r210_class000.accounts'/'sessions'/SID
        self.receipt = r.read(self.directory/'receipt.json')

    def tearDown(self):
        self.temp.cleanup()

    def replace_end(self, end):
        path = self.directory/'platform'/'final.json'
        r.raw_atomic(path, end)
        self.receipt['platform'] = end
        self.receipt['platform_final_sha256'] = r.sha(path)

    def test_real_reserve_stop_has_complete_end_accounts(self):
        self.assertTrue(p.platform_account_complete(self.directory, self.receipt))
        self.assertIsNotNone(self.receipt['platform']['fault'])

    def test_missing_host_end_remains_gap(self):
        end = copy.deepcopy(self.receipt['platform'])
        end['adapter_complete'] = False
        self.replace_end(end)
        self.assertFalse(p.platform_account_complete(self.directory, self.receipt))

    def test_other_fault_not_whitelisted(self):
        end = copy.deepcopy(self.receipt['platform'])
        end['fault']['reason'] = 'ValueError: host heartbeat stopped advancing'
        self.replace_end(end)
        self.assertFalse(p.platform_account_complete(self.directory, self.receipt))

    def test_changed_final_hash_rejected(self):
        self.receipt['platform_final_sha256'] = '0'*64
        with self.assertRaises(ValueError):
            p.platform_account_complete(self.directory, self.receipt)

    def test_changed_host_cpu_rejected(self):
        end = copy.deepcopy(self.receipt['platform'])
        end['host']['sampler_cpu_end_s'] += 1
        self.replace_end(end)
        with self.assertRaises(ValueError):
            p.platform_account_complete(self.directory, self.receipt)

    def test_nonzero_exit_not_reclassified(self):
        self.receipt['returncode'] = 1
        self.assertFalse(p.platform_account_complete(self.directory, self.receipt))

    def test_open_native_registration_rejected(self):
        r.raw_atomic(self.directory/'platform'/'native.json', dict(identity={'pid':1}))
        with self.assertRaises(ValueError):
            p.platform_account_complete(self.directory, self.receipt)

    def test_missing_sampler_final_rejected(self):
        (self.directory/'platform'/'sampler-final.json').unlink()
        with self.assertRaises(OSError):
            p.platform_account_complete(self.directory, self.receipt)


if __name__ == '__main__':
    unittest.main()
