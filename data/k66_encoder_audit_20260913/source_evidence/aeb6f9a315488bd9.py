"""Strict independent checker for the positive-hint RUP subset used here.

No RAT, binary syntax, or extension-variable proof steps are accepted.
A satisfied hint is rejected; an actual conflict must be reached.
"""
import json
import sys
from pathlib import Path
from unit_audit import parse


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def verify(cnf, proof):
    (nv, nc), clauses = parse(cnf)
    database = {i+1: tuple(c) for i, c in enumerate(clauses)}
    last = nc
    proved_empty = False
    additions = 0
    for line in proof.read_text().splitlines():
        tokens = line.split()
        need(len(tokens) >= 3, 'Short record')
        if tokens[1] == 'd':
            need(tokens[-1] == '0', 'Unterminated deletion')
            for token in tokens[2:-1]:
                need(int(token) > 0, 'Invalid deletion identifier')
                database.pop(int(token), None)
            continue
        numbers = list(map(int, tokens))
        cid = numbers[0]
        need(cid > last and not proved_empty, 'Invalid addition order')
        cut = numbers.index(0, 1)
        clause = numbers[1:cut]
        hints = numbers[cut+1:-1]
        need(numbers[-1] == 0 and all(h > 0 for h in hints), 'Non-RUP hints')
        need(all(0 < abs(x) <= nv for x in clause), 'Invalid literal')
        need(not any(-x in clause for x in clause), 'Tautological addition unsupported')
        values = {abs(x): x < 0 for x in clause}
        conflict = False
        for index, hint in enumerate(hints):
            need(hint in database, 'Missing or deleted hint')
            body = database[hint]
            need(not any(abs(x) in values and values[abs(x)] == (x > 0) for x in body), 'Satisfied hint')
            free = {x for x in body if abs(x) not in values}
            need(len(free) <= 1, 'Hint not unit or conflicting')
            if not free:
                need(index == len(hints)-1, 'Hints after conflict unsupported')
                conflict = True
                break
            x = next(iter(free))
            values[abs(x)] = x > 0
        need(conflict, 'No actual conflict reached')
        database[cid] = tuple(clause)
        last = cid
        additions += 1
        proved_empty = not clause
    need(proved_empty, 'No empty clause proved')
    return additions


if __name__ == '__main__':
    base, proofs = map(Path, sys.argv[1:3])
    records = []
    for cnf in sorted(base.rglob('*.cnf')):
        relative = cnf.relative_to(base)
        count = verify(cnf, proofs/relative.with_suffix('.lrat'))
        records.append(dict(path=str(relative), additions=count))
    need(len(records) == 125, 'Expected 125 instances')
    result = dict(status='ALL_125_STRICT_RUP_VERIFIED', records=records)
    (proofs/'strict_rup.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], flush=True)
