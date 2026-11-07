from pathlib import Path
import json
import hashlib
import sys
import time
import batch_recovery as b

P = Path(__file__).resolve().parent
RESEARCH = P.parent / 'C2_ProofReplay_20261107'
CASES = P.parent / 'C2_Rest55_20261104'
O = P / 'real_pilot'
O.mkdir(exist_ok=False)
results = []
try:
    for case in (20, 77):
        folder = CASES / f'case_{case:04d}'
        original = json.loads((folder / 'execution_contract.json').read_text())
        assert b.digest(folder / 'row_input.txt') == original['files']['row_input.txt']
        tokens = list(map(int, (folder / 'row_input.txt').read_text().split()))
        n, c = tokens[:2]
        cursor = 2 + c + 2*n*n
        for _ in range(n):
            cursor += 1 + tokens[cursor]
        total = tokens[cursor]
        pairs = list(zip(tokens[cursor+1::2], tokens[cursor+2::2]))
        assert total == len(pairs) == original['boundaries']
        first = pairs[0][0]
        same = [i for i, (a, _) in enumerate(pairs) if a == first][:3]
        different = next(i for i, (a, _) in enumerate(pairs) if a != first)
        for pattern, tasks in [('AAA', same), ('ABA', [same[0], different, same[1]])]:
            variants = [('single', 1), ('batch', 3)] if pattern == 'AAA' else [('batch', 3), ('single', 1)]
            hashes = {}
            for variant, size in variants:
                root = O / f'c{case}_{pattern}_{variant}'
                sources = dict(zip(b.NAMES, [folder/'row_input.txt', RESEARCH/'column_action.txt',
                                            P/'batch-engine', P/'batch-verify']))
                b.initialise(root, f'case{case}_{pattern}_{variant}', total, tasks, sources)
                begin = time.monotonic()
                state = b.run(root, chunk_size=size)
                wall = time.monotonic() - begin
                assert state['state'] == 'RESEARCH_SUBSET_VERIFIED', state
                records = [b.read(root/'receipts'/f'{i:05d}.json') for i in tasks]
                hashes[variant] = [r['proof_sha256'] for r in records]
                phases = [b.read(path) for path in (root/'attempts').glob('*/search_closed.json')]
                replays = [b.read(path) for path in (root/'attempts').glob('*/checked.json')]
                result = dict(case=case, pattern=pattern, tasks=tasks, variant=variant, total_wall=wall,
                              search_wall=sum(r['result']['seconds'] for r in phases),
                              replay_wall=sum(r['seconds'] for r in replays), receipts=len(records),
                              proof_sha256=hashes[variant], context=b.sha(b.canonical(b.read(root/'contract.json'))),
                              original_input_sha256=original['files']['row_input.txt'], status='PASS')
                results.append(result)
                (P/'REAL_RESULTS.json').write_text(json.dumps(results,indent=4)+'\n')
                print(json.dumps(result),flush=True)
            assert hashes['single'] == hashes['batch'], 'Changed proof bytes'
    totals = {v:sum(r['total_wall'] for r in results if r['variant']==v) for v in ('single','batch')}
    summary = dict(status='PASS', totals=totals, speedup=totals['single']/totals['batch'],
                   paired_groups=4, task_executions_per_variant=12, distinct_boundaries=8,
                   scope='S2 single versus batch using identical durable controller and native receipt checker; includes resource checks, replay, compression, snapshot and receipt transactions; excludes bundle initialisation and whole-case final audit',
                   global_exclusion=False)
    (P/'REAL_COMPARISON.json').write_text(json.dumps(summary,indent=4)+'\n')
    print(json.dumps(summary),flush=True)
except Exception as error:
    (P/'REAL_STOP.json').write_text(json.dumps(dict(error=repr(error)),indent=4))
    raise
