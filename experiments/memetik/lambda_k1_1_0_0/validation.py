"""Controller/audit dispatch, independent of candidate generation."""
from verify import record, task_check, key, encode


def initial_best(founder, task):
    if task['kind'] == 'packing':
        from packing import packing_record
        return packing_record(encode([set() for _ in range(99)]))
    return record(founder['graph6'])


def validate_best(value, founder, task):
    if task['kind'] == 'packing':
        from packing import packing_record
        actual = packing_record(value['graph6'])
        assert len(__import__('verify').decode(value['graph6'])) == 99
        assert value['kind'] == 'packing'
        if actual['scores']['edges'] == 693:
            assert record(value['graph6'])['scores']['W'] == 0
    else:
        actual = record(value['graph6'])
        assert key(actual['scores']) <= key(founder['scores'])
        if task['kind'] == 'cp':
            assert task_check(value['graph6'], founder['graph6'], task) == actual['scores']
        else:
            assert task['kind'] == 'catalog'
    assert actual['state'] == value['state'] and actual['scores'] == value['scores']
    return actual
