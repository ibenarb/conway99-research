"""Small independent RUP checker. No solver imports; RAT-only steps rejected.

Deletion lines may be ignored: every retained lemma was already proved implied.
An empty clause must itself pass reverse unit propagation before UNSAT is accepted.
"""
import argparse
import hashlib
import json
from pathlib import Path


def conflict(clauses, assumptions):
    assigned = set()
    for literal in assumptions:
        if -literal in assigned:
            return True
        assigned.add(literal)
    changed = True
    while changed:
        changed = False
        for clause in clauses:
            if any(literal in assigned for literal in clause):
                continue
            remaining = [literal for literal in clause if -literal not in assigned]
            if not remaining:
                return True
            if len(remaining) == 1:
                literal = remaining[0]
                if -literal in assigned:
                    return True
                if literal not in assigned:
                    assigned.add(literal)
                    changed = True
    return False


def verify(cnf_path, proof_path):
    clauses = []
    pending = []
    declared = None
    for line in cnf_path.read_text().splitlines():
        if not line or line.startswith('c'):
            continue
        if line.startswith('p'):
            _, kind, variables, count = line.split()
            assert kind == 'cnf'
            declared = (int(variables), int(count))
            continue
        for literal in map(int, line.split()):
            if literal == 0:
                clauses.append(tuple(set(pending)))
                pending = []
            else:
                pending.append(literal)
    assert declared and not pending and len(clauses) == declared[1]
    assert all(abs(lit) <= declared[0] for clause in clauses for lit in clause)
    additions = deletions = 0
    empty = False
    for number, line in enumerate(proof_path.read_text().splitlines(), 1):
        tokens = line.split()
        if not tokens or tokens[0] == 'c':
            continue
        if tokens[0] == 'd':
            deletions += 1
            continue
        values = list(map(int, tokens))
        assert values[-1] == 0 and 0 not in values[:-1], ('proof syntax', number)
        clause = tuple(set(values[:-1]))
        if not conflict(clauses, [-lit for lit in clause]):
            raise ValueError('non-RUP addition at line ' + str(number))
        clauses.append(clause)
        additions += 1
        if not clause:
            empty = True
    if not empty:
        raise ValueError('missing verified empty clause')
    return {'status': 'RUP_VERIFIED_UNSAT', 'additions': additions,
            'ignored_deletions': deletions,
            'cnf_sha256': hashlib.sha256(cnf_path.read_bytes()).hexdigest(),
            'proof_sha256': hashlib.sha256(proof_path.read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cnf', type=Path)
    parser.add_argument('proof', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.cnf, args.proof)))
