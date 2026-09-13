"""Produce single-step RUP/LRAT proofs where root unit propagation suffices."""
import collections
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def parse(path):
    clauses = []
    pending = []
    header = None
    for line in path.read_text().splitlines():
        if not line or line.startswith('c'):
            continue
        if line.startswith('p'):
            assert header is None and not clauses and not pending
            tag, fmt, nv, nc = line.split()
            assert fmt == 'cnf'
            header = int(nv), int(nc)
            continue
        assert header is not None
        for token in line.split():
            literal = int(token)
            if literal:
                assert abs(literal) <= header[0]
                pending.append(literal)
            else:
                assert len(set(pending)) == len(pending)
                assert not any(-x in pending for x in pending)
                clauses.append(pending)
                pending = []
    assert header is not None and not pending and len(clauses) == header[1]
    return header, clauses


def unit_hints(clauses):
    occurrences = collections.defaultdict(list)
    remaining = [len(c) for c in clauses]
    satisfied = set()
    values = {}
    queue = collections.deque(i for i, c in enumerate(clauses) if len(c) <= 1)
    for i, c in enumerate(clauses):
        for x in c:
            occurrences[x].append(i)
    hints = []
    while queue:
        i = queue.popleft()
        if i in satisfied:
            continue
        free = [x for x in clauses[i] if abs(x) not in values]
        assert len(free) <= 1
        hints.append(i + 1)
        if not free:
            return hints
        x = free[0]
        values[abs(x)] = x > 0
        satisfied.update(occurrences[x])
        for j in occurrences[-x]:
            remaining[j] -= 1
            if remaining[j] <= 1 and j not in satisfied:
                queue.append(j)
    return None


def main():
    base, output, checker = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    records = []
    for path in sorted(base.rglob('*.cnf')):
        header, clauses = parse(path)
        hints = unit_hints(clauses)
        rec = dict(path=str(path.relative_to(base)), variables=header[0], clauses=header[1],
                   cnf_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        if hints:
            target = output / path.relative_to(base).with_suffix('.lrat')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(str(header[1]+1)+' 0 '+' '.join(map(str,hints))+' 0\n')
            check = subprocess.run([checker, str(path), str(target)], capture_output=True)
            target.with_suffix('.check.out').write_bytes(check.stdout)
            target.with_suffix('.check.err').write_bytes(check.stderr)
            assert check.returncode == 0 and b'c VERIFIED' in check.stdout.splitlines()
            rec.update(status='ROOT_RUP_LRAT_CHECKED', hints=len(hints),
                       proof_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
        else:
            rec['status'] = 'NOT_ROOT_UP'
        records.append(rec)
    output.mkdir(parents=True, exist_ok=True)
    result = dict(records=records, counts=dict(collections.Counter(r['status'] for r in records)),
                  scope='CNF syntax and single-step root RUP checked. Cake not run here.')
    (output/'unit_audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result['counts']), flush=True)


if __name__ == '__main__':
    main()
