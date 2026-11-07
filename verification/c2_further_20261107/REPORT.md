# C2 optimisation follow-up: reviewed invariants and discriminating experiments

7 November 2026. Research only; case78 production remains sealed and unchanged. Twelve of62 cases certified,50 pending. Neither L62 nor C2 is closed. No heartbeat restored.

## Independent review

The full reviewer request is REVIEWER_AUFTRAG.md. The authorised independent reviewer confirmed S1/S2 and checked 4,032 distinct ordered mask pairs. Recovery/scaling findings retain their documented limits. Crucial precision: the portable and reference pure-row screens independently construct D/G/K but share their exhaustive enumeration algorithm. Independent proof replay does not establish domain completeness by itself.

## Fixed-boundary coupled symmetries

The existing coupled vertex group was augmented by validated pure row swaps (0 1),(2 3). Group closure, normalisation, exact D/G/K covariance, commuting column action and faithful column representation were checked. An independent reviewer confirmed the stabiliser formula 2 times the number of coupled elements preserving the unordered distinct boundary pair.

| Case | Boundaries | Stabiliser order4 | Stabiliser order8 |
|---|---:|---:|---:|
|20|36288|36096|192|
|77|18144|18048|96|
|78|9072|9024|48|

Only0.5291% have additional symmetry in this particular group. This is neither a runtime saving estimate nor a classification of every possible row/column action. Further canonicalisation would need a common canonical ordering for the combined group or proof that it preserves S2's canonical domain.

## Four bounded native comparisons

All four comparisons use the same unchanged baseline; percentages are not incremental gains over the preceding variant. Each comparison uses the same eight real boundaries:0,1,2,12 from cases20 and77. Baseline/variant execution order alternates by index. One execution per task per variant: an exploratory screen, not a confidence interval or whole-case forecast. All final builds use -O3 -mpopcnt -std=c++17. Existing host/WSL resource monitor,512MiB address-space cap,180CPU seconds,128MiB file cap and watchdog guard each stage; each task search has30seconds. One research pilot at a time.

Times below include monitored native search and unchanged sealed single-verifier replay; they exclude full-case orchestration, final audit and final archive. Search visit counts are not complete proof-node counts. Speedup means baseline divided by variant; factors must not be multiplied with earlier experiments.

| Variant | Baseline seconds | Variant seconds | Speedup | Time saved |
|---|---:|---:|---:|---:|
| pair | 40.324 | 44.127 | 0.9138 | -9.43% |
| cheap | 40.596 | 39.295 | 1.0331 | +3.21% |
| prefix | 40.060 | 40.084 | 0.9994 | -0.06% |
| order | 39.881 | 39.217 | 1.0169 | +1.66% |

**pair:** Test up to four small remaining-row pairs, product at most256, at most1024 compatibility calls per visit. Only a completely incompatible pair yields an existing-format branch followed by empty-domain leaves. All proofs passed unchanged replay.715,261 cuts reduce visits by only574 and increase raw proofbytes from4,828,934 to4,832,759. Do not adopt this tested policy. Larger or differently scheduled pair filters remain untested.

**cheap:** Move capacity and Gram/twist checks before costly symmetry computations. Same side-effect-free conjunction, no changed candidate ordering. All eight completed proofs were byte-identical to baseline and independently replayed.

**prefix:** Additionally perform the unary row2 condition x<=tau(x) only in the mandatory row0 prefix. Every later row2 domain is a subset of that checked prefix. First-task, same-A, ABA, changed-A and row3-first paths preserve the invariant; the coupled canonical_pair test stays unchanged. The reviewer checked this argument. All eight completed proofs were byte-identical and passed independent replay. This optimisation is not automatically valid for a future entry from unchecked rest domains.

**order:** On top of prefix, filter the remaining child rows in ascending current domain size, tie-breaking by row index. MRV and candidate order remain unchanged; each row filter is independent of the other filters. Any empty domain supplies a valid existing-format leaf; otherwise every child domain is complete. Reviewer approved this invariant. All eight completed tasks retained identical visit counts and proof lengths and passed unchanged replay; leaf bytes differed.

## Exact-state repetition diagnostic

No pruning or proof reuse. Keys contain remaining rows,once,twice and each complete ordered remaining domain; model/action/index semantics stay fixed per process. Only completed UNSAT states enter an exact string-equality map. Partially built children are never cached. Limits:50,000 entries,64MiB keybytes,16KiB per key; process-memory limit additionally applies.

Case20:158,277 eligible-key probes,0hits. Case77:965,468probes,1hit for a one-visit subtree. Each process reached the50,000entry cap. This is a limited sample against retained earlier states, not proof of global uniqueness. Skipped probes/insertions are reported. All eight diagnostic proofs were byte-identical and independently replayed. No evidence here justifies a new DAG proof format. Diagnostic overhead is not an acceleration measurement; repeated-node sums could double-count overlapping subtrees.

## Measurement correction and preservation

Initial new builds accidentally omitted -mpopcnt although baseline used it. Their timing comparisons are invalid as algorithm comparisons; the initially reported18% pair slowdown is superseded by the corrected table. Original logs and proofs are preserved. Their correctness/byte-equality evidence remains valid. No production conclusion or counted exclusion used these timings.

REVIEW_RECORD.md records independent reviews. JSON records bind inputs, binaries, proofhashes, search and replay. Local complete evidence archive is separately byte-verified. Scripts are workspace research helpers requiring the existing model files and previous bounded-controller/resource-sensor modules; they are not a self-contained global exclusion certificate.

Next production gates remain: representative repeated measurements including actual production transactions, positive/negative controls, newly sealed case contract and complete final-audit/archive integration. No change to live case78, T20, shared checkout or exclusion ledger.

## Next structural diagnostic, not yet implemented

The independent reviewer prioritises explanation-based small conflicts rather than complete-state memoisation. At a bounded sample of empty-domain leaves, reconstruct exclusions from the full original row domain: Gram/twist incompatibility with an assigned row; third-column occupancy caused by two assigned rows; and explicit S2 reasons. Find a small sufficient subset of assignments, independently recheck that it eliminates every original candidate, and measure whether the same conflict occurs elsewhere. No pruning or new proof format until this diagnostic demonstrates recurring small explanations. Sparse exact-state matches do not imply sparse small conflicts.
