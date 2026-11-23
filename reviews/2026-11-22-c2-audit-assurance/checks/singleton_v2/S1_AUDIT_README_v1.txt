Separate Singleton evidence audit, version 1
22 November 2026

Run from this directory with standard Python 3.12 or newer:
python -B audit_singleton_evidence_v1.py --output new_audit.json
python -B test_singleton_auditor_v1.py --output-dir new_control_directory
Output files/directories must not exist. The caller must first check CPU,
RAM and disk admission. These commands start no research solver.

The auditor imports no solver, setup, NumPy or PARI code. It reconstructs
all 3580 literal base graphs and the 272 nonphysical cases. For every
completed result it recomputes all 924 candidate balanced root signs with
exact Fraction arithmetic, including range and Schur conditions. It builds
the full coloured matching automorphism group by forced-image backtracking,
then independently checks each complete root orbit and overall negation.
This differs from the setup's enumeration of all 46080 signed permutations.
All input matrices, recorded determinants and attachment encodings are
checked; every gzip input is fully decompressed and hashed. Every ROOT
completion must occur exactly once in order, followed by a unique FINAL
with open=0 and natural exhaustion. All source and evidence hashes match.

This is an evidence and coverage auditor, not a third search solver.
Attachment completeness and mathematical validity of search predicates
remain dependencies on the disclosed implementation and separate review.
The first/second-layer counters are retained. The original second-layer
cases 183 and 3377 close by stronger exact first-layer conditions here;
that does not reproduce the original second-layer survivor ledger.

The controls include raw and gzip inputs and the successful resource-retry
cases. Eight corrupted fixtures update affected hashes before testing:
wrong chart, OPEN, omitted orbit member, duplicated orbit member, wrong
input root list, missing ROOT row, missing FINAL and nonempty error stream.
Every original input is rehashed after the tests. Unchanged fixture files
and newly included completed-job evidence may be immutable hardlinks.
Do not edit them in place. Hardlinks are not independent backups; committed
Git objects and the remote private repository provide separate copies.

Only completed per-job records count. Main-controller historical admission
failures for charts 12 and 202 do not override their subsequent separately
verified retry results. Partial snapshots explicitly enumerate every
remaining case; a partial PASS is not full S1 completion. The catalogue's
177842 raw-root total is a pinned preliminary-ledger total until every
physical chart has also passed this auditor's exact unary recomputation.
