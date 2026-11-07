# C2 prefix batches: recoverable proof transactions and scaling

7 November 2026. Bounded research result; no additional global exclusion.

## Measured result

The same S2 batch searcher and native receipt verifier were run with chunk size one and three, under the same controller. Four paired groups cover twelve executions per variant and eight distinct boundaries from cases 20 and 77, including AAA reuse and ABA invalidation. Order alternates between patterns. Input hashes were checked against the original sealed contracts. All proof bytes match between variants.

| Version | One-task chunks | Three-task chunks | Ratio |
|---|---:|---:|---:|
| Initial transactional prototype | 66.945214 s | 49.230644 s | 1.359828 |
| Incremental receipt prototype | 66.977697 s | 50.415823 s | 1.328505 |

The final prototype saved **24.73%** in this measured comparison. Timing includes independent resource sensing, search, replay, proof snapshots, compression and durable receipt publication; it excludes initial bundle copying and whole-case final audit/archive. These are small live-load experiments, not confidence intervals, a comparison with the production single-task controller, or whole-case forecasts. Do not multiply this ratio by earlier ratios from different experiments.

Every distinct real proof also passed the unchanged, sealed S2 single-task verifier from case78. Native checker receipts alone are not certificates: they are bound to the exact proof snapshot, model, action and executable hashes by the controller's checked manifest.

## What changed

A batch shares the ordered candidate filter for its first boundary row A; all conditions involving B remain task-specific. Each proof retains its own C2S2 boundary index. After the search process exits, the controller freezes proof snapshots, verifies them independently, checks hashes again, compresses and round-trip checks each proof, then publishes an immutable receipt. A failed batch replay commits no new controller receipts. Previously valid receipts survive.

Recovery never treats mere proof existence or log markers as completion. Closed search attempts can be replayed without repeating mathematical search. An unfinished search intent instead causes an explicit halt, retaining evidence; SAT/UNKNOWN cannot silently disappear into a restart. SAT is checked against the supplied full matrix/domain/column contract and is not labelled a global C2 witness.

The successor removes repeated full receipt scans: validate existing receipts once at startup, validate only new receipts during progress, and scan the whole subset at closure. A 96-boundary synthetic control required exactly 192 receipt validations: 96 incremental plus 96 final. This is a claim about receipt-file validation work, not optimality of every list operation or fixed-input hash.

## Validation and limits

- 26 integrity/state-transition checks, repeated for the incremental successor: wrong contexts, inputs/actions/binaries, damaged or missing compressed proofs, changed snapshots/native receipts/logs, duplicate indices, symlink escape, simultaneous controller, invalid second proof and post-replay mutation.
- Three genuine SIGKILL checks per version: interrupted mixed UNSAT/SAT publication before and after the first receipt, and controller death while a child is running. The child stops; unresolved search blocks automatic restart.
- Three further UNSAT/UNKNOWN/open checks in the final version, including SIGKILL before and after receipt publication. Only the first independently verified boundary counts; the third is never started.
- Linear receipt-validation and lock-opening-failure controls passed.
- All eight distinct real proof files passed a second, unchanged independent single-task verifier.

Tests use tiny synthetic models and explicitly labelled fixture resource sensors; real pilots use the independent host/WSL resource sensor. Initial test setup failures (a missing mixed fixture and a synthetic wrapper path error) were retained and corrected in fresh directories. They did not affect production. V1 normal pilots preceded the hard-kill tests; V2 hard-kill and scaling controls preceded its normal pilot. File/directory sync and process-kill checks do not establish hardware power-loss guarantees.

## Mathematical screen: additional pure row permutations

A complete backtracking screen fixes boundary rows 0 and 1 pointwise and requires exact preservation of row degree targets D and both full matrices G and K. Candidate colours retain each D-row and the two diagonal targets; every assigned pair is checked in both directions. Every possible permutation satisfying these conditions is explored and every returned action is rechecked.

Among all 62 algebraic contracts, 59 groups have order 2, cases18/63 have order8, and case68 has order32. The latter three are already closed. Thus **all 50 currently open cases have only the already-used row2/row3 swap in this precisely defined class**. This does not exclude additional coupled row/column transformations, boundary-moving actions, or other mathematical reductions. A standalone standard-library implementation matches the reference specification's complete result on all62 cases.

## Production status and remaining gate

Case78 continues unchanged with the reviewed single-task S2 implementation. Twelve of62 cases are excluded;50 remain. Neither L62 nor C2 is closed. Heartbeat remains deleted.

This is a reviewed recovery/scaling prototype, not a full-case production controller. Deployment still requires a newly sealed case-specific contract, complete coverage integration, final independent audit/archive binding, bounded scheduling and fresh case pilots. The live case78 contract is not modified. Local evidence archives retain real pilot inputs, proofs and failure-test artefacts; public scripts and reports are not a global exclusion certificate.
