"""One hash-bound historical deviation; never a general budget exemption."""
from common import digest

LEGACY_RECEIPT_SHA256 = '1a782d93367ef987bc114b227678a8f68cb1716497441f3b522db16fcd4ab370'


def historical_overrun(run, token, receipt):
    return (str(token) == '13'
            and digest(run / 'receipts' / (str(token) + '.json')) == LEGACY_RECEIPT_SHA256
            and receipt['category'] == '2076_01_s60_defect')
