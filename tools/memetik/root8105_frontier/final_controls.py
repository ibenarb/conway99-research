"""Certificate controls and proofs for the three rejected F proposals."""
import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from certify_dead import encode as independent_row_encode
from rup_check import verify
from widths import save
from pysat.solvers import Glucose4


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output
    receipt = json.loads((output / 'FINAL_RECEIPT.json').read_text())
    payload_sha = receipt.pop('payload_sha256')
    assert hashlib.sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest() == payload_sha
    assert all(hashlib.sha256((output/n).read_bytes()).hexdigest()==h for n,h in receipt['artifact_sha256'].items())
    source = args.repo / 'experiments/memetik/root8105_review_followup_1_0_1'
    sys.path.insert(0, str(source))
    import bootstrap
    import historical_core as core
    from kernel import Geo
    from row_sampler import RowProposal
    prefix_dir = args.repo / 'docs/augmentation/root8105_prefix_audit_20261006'
    positives = []
    negative_proofs = []
    for item in receipt['F_counts']:
        data = json.loads((prefix_dir / (item['prefix'] + '.json')).read_text())
        # Concrete positive candidate: full row fixed, not an ungrounded SAT control.
        row_result = next(r for r in item['results'] if r['accepted'])
        candidate = row_result['accepted'][0]['neighbors']
        cnf, equations = independent_row_encode(data, row_result['target'])
        assert all(sum(v in candidate for v in vertices) == rhs for vertices,rhs in equations)
        with Glucose4(bootstrap_with=cnf.clauses) as solver:
            assert solver.solve(assumptions=[v+1 if v in candidate else -(v+1) for v in range(84)])
        positives.append({'prefix':item['prefix'],'target':row_result['target'],'status':'FIXED_KNOWN_ROW_SAT'})
        for result in item['results']:
            if not result['rejected_ranks']:
                continue
            rows = {int(u):sum(1<<v for v in vs) for u,vs in data['rows'].items()}
            assigned = {(u,v):bit for u,v,bit in data['assignments']}
            target = result['target']
            proposal = RowProposal(Geo(), rows, target, assigned)
            assert proposal.total == result['proposal_width']
            for rank in result['rejected_ranks']:
                row = proposal.unrank(rank)
                cnf, variables = core.encode(core.Geometry(), rows, target)
                _, free = core.projection(core.Geometry(), rows, target, variables)
                units = [lit if row >> v & 1 else -lit for v,lit in free]
                units += [lit if assigned[p] else -lit for p,lit in variables.items() if p in assigned]
                cnf.extend([[lit] for lit in units])
                stem = item['prefix']+'_t%02d_rank%d_F_rejection' % (target,rank)
                cnf_path, proof_path = output/(stem+'.cnf'), output/(stem+'.rup')
                with Glucose4(bootstrap_with=cnf.clauses, with_proof=True) as solver:
                    assert not solver.solve()
                    proof = solver.get_proof()
                cnf.to_file(str(cnf_path))
                explicit_empty_added = '0' not in [line.strip() for line in proof]
                proof_path.write_text('\n'.join(proof + (['0'] if explicit_empty_added else []))+'\n')
                verified = verify(cnf_path,proof_path)
                negative_proofs.append({'prefix':item['prefix'],'target':target,'rank':rank,
                                        'cnf':cnf_path.name,'proof':proof_path.name,'verification':verified,
                                        'explicit_empty_added_and_RUP_checked':explicit_empty_added,
                                        'solver_proof_lines':len(proof)})
            proposal.rec.cache_clear()
    assert len(positives)==17 and len(negative_proofs)==3
    controls = []
    temp = Path(tempfile.mkdtemp(prefix='root8105-rup-controls-'))
    def case(name, cnf, proof, expected):
        cp, pp = temp/(name+'.cnf'), temp/(name+'.rup')
        cp.write_text(cnf)
        pp.write_text(proof)
        try:
            verify(cp,pp)
            accepted = True
        except (ValueError,AssertionError):
            accepted = False
        assert accepted == expected, name
        controls.append({'name':name,'accepted':accepted,'expected':expected})
    case('unit_contradiction','p cnf 1 2\n1 0\n-1 0\n','0\n',True)
    case('SAT_false_empty_clause','p cnf 2 1\n1 2 0\n','0\n',False)
    case('non_implied_lemma','p cnf 2 2\n1 2 0\n-1 2 0\n','1 0\n0\n',False)
    case('missing_empty_clause','p cnf 1 2\n1 0\n-1 0\n','1 0\n',False)
    case('deletions_ignored_soundly','p cnf 1 2\n1 0\n-1 0\n','d 1 0\n0\n',True)
    case('malformed_proof','p cnf 1 2\n1 0\n-1 0\n','1\n',False)
    report={'status':'PASS','sealed_receipt_payload_sha256':payload_sha,
            'original_receipt_artifact_hashes_checked':True,
            'fixed_row_positive_controls':positives,'F_rejection_certificates':negative_proofs,
            'RUP_checker_controls':controls,
            'RUP_checker_sha256':hashlib.sha256(Path(__file__).with_name('rup_check.py').read_bytes()).hexdigest()}
    save(output/'CONTROLS.json',report)
    print(json.dumps({'status':'PASS','positive_controls':len(positives),'F_rejection_certificates':3,'RUP_controls':len(controls)}),flush=True)


if __name__ == '__main__':
    main()
