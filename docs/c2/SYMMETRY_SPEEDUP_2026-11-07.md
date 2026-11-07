# C2 exclusion research: verified symmetry reductions and cheaper replay

7 November 2026. Research result; no new global exclusion is claimed.

## Measured result

Sixteen paired boundary tasks, eight each from cases 20 and 77, were run against the actual binaries and input hashes in the sealed production contracts. The sample includes the first and last boundary and six pseudorandom boundaries per case (seed 20261107). Execution order alternated. Search, independent replay, and gzip level-1 compression/decompression/hash verification were timed together.

| Variant | Production total | Candidate total | Ratio |
|---|---:|---:|---:|
| S1: row swap, lazy replay, reusable storage | 289.056 s | 131.367 s | 2.200 |
| S2: additionally coupled column symmetry | 288.036 s | 90.341 s | 3.188 |

S2 saved 68.64% of measured time. Its maximum observed process RSS was 33136 KiB. Both experiments ran alongside the unchanged production campaign, so these are bounded pilot measurements under live load, not confidence intervals or whole-case guarantees. Ratios from different experiments must not be multiplied to manufacture a performance claim.

The earlier 6 November prototype builds omitted the production -mpopcnt flag. Their ratios only describe those builds. The comparisons above use actual sealed production binaries, and candidates compiled with -O3 -mpopcnt -std=c++17.

## Mathematical coverage

Use zero-based row indices. Rows 0 and 1 form the fixed boundary.

S1 exchanges rows 2 and 3. The verifier requires identical complete domains, invariance of both complete target matrices G and K under that exchange, and G[2,2] > G[2,3]. Consequently the rows cannot coincide and every solution orbit has an orientation X2 < X3. Column capacities and the fixed boundary are preserved. The condition is checked in both assignment orders, including dynamic row selection.

S2 uses a common column involution tau, applied to ALL rows. The verifier requires tau to commute with P, preserve each complete row domain, and fix both boundary masks. It therefore preserves ordinary and twisted scalar products and column capacities. It commutes with the row exchange. Restrict (a,b)=(X2,X3) to the lexicographic minimum of

    (a,b), (b,a), (tau(a),tau(b)), (tau(b),tau(a)).

Every full solution orbit has such a representative. Fixpoints and smaller orbits are retained; uniqueness of the entire representative is unnecessary. The necessary unary condition a <= tau(a) is safe. Independently imposing b <= tau(b) would be unsound and is NOT done. The searcher uses explicit inequalities; the independent verifier computes the minimum of the four pairs.

For the 62 current algebraic records, tau is induced by interchanging vertices 0 and 1 in the 60-column edge representation. All degree targets are invariant under that interchange, and the first two rows have zero incidence at both vertices. Thus every permitted first-two-row mask is fixed. The induced action commutes with P. These algebraic checks passed for all 62 records. Each future case still requires its own independently complete domains and input binding; this is not a transfer of another case's exclusion.

## Cheaper independent replay

An empty-domain leaf names the domain whose emptiness must be proved. The verifier reconstructs that entire domain, then checks emptiness. It need not reconstruct unrelated domains at that leaf. At branching nodes all required domains are reconstructed. Invalid codes, assigned-row leaves, false emptiness claims and truncation reject. Proof files must remain immutable during replay.

Separate vector storage is reused at each recursion depth. Parent and child depths differ, and sibling storage is reused only after return. This supports one recursive search per process; it is not shared-thread storage.

## Validation

- Lazy replay: 96 small models and 288 differential proof mutations.
- Reusable storage: 96 models and exact C2R1 proof-byte comparisons.
- S1: 64 exhaustive symmetric models (28 SAT, 36 UNSAT), both assignment orders, invalid symmetry contracts, false/truncated proofs and incompatible format tests.
- S2: closed-domain tests in both assignment orders; nonclosed domains and invalid actions rejected.
- S2 edge cases: 64 identity-action comparisons reduce byte-for-byte to S1 after the format header; exchanged SAT pairs with a nonminimal second element; nontrivial fixpoint SAT; noncommuting action and malformed proofs rejected.
- 38 S2 SAT witnesses independently checked against full ordinary/twisted matrices, all domain memberships, fixed boundaries and exact column sums.
- Every measured UNSAT candidate independently replayed. UNKNOWN, SAT and failed symmetry checks never count as exclusions.

An authorised independent internal reviewer examined coverage, frame lifetimes and independent replay. This is algorithmic verification and source review, not a proof-assistant formalisation or an external peer-review claim.

## Status and integration gate

The running case 77 and all T20 settings remain unchanged. Eleven global cases are counted closed; 51 remain, including case 77. Neither L62 nor C2 is closed. No heartbeat automation was created.

C2S1 and C2S2 have explicit new proof headers. Before production, new case-specific pilots, immutable model/source/binary/action hashes, checkpoint binding and a corresponding final archive audit are required. Existing sealed C2R1 cases must not be relabelled or silently accepted by a tolerant header check. Isolated integration templates are research work pending end-to-end validation.

The complete local research snapshot includes pilot proofs and production input/binary bindings. Public source and small-model controls accompany this report; the timing records alone are not a global C2 proof.

## Optional symmetry-image cache

Precomputing each domain element's tau-image preserves the C2S2 format and proof bytes. Ninety-eight small comparisons, both assignment orders and crossed independent replays passed. Six paired real tasks gave 31.188 s without the cache and 29.826 s with it (ratio 1.046). Maximum observed RSS increased from 33116 to 48424 KiB. This small additional gain needs broader measurement; it is not included in the 3.188 production ratio. The uncached S2 implementation remains the performance-evidenced integration baseline.

The standalone public_smoke.py regenerates small complete models and compares the cached candidate against exhaustive enumeration; it requires Python3 and g++ on Linux. No production input is needed for that regression check.

## Serial prefix reuse

The complete model and symmetry action are parsed and checked once per serial batch. Ordered candidate lists filtered against the first boundary row A are reused while A is unchanged. Conditions involving B, including saturated columns A&B, are applied separately for every task. A change clears the prefix cache. Each task has its own C2S2 proof and independent replay. SAT or UNKNOWN stops the batch; unprocessed tasks remain open.

Four paired batches used twelve task executions per variant, covering eight distinct boundaries across cases 20 and 77. Orders AAA and ABA exercised reuse and invalidation. Direct comparison with the actual sealed production binaries, including independent replay and gzip, gave 193.971080 s versus 48.587427 s: factor 3.992207, or 74.95% less wall time in this pilot. Maximum observed RSS was 34180 KiB. This is not a whole-case runtime forecast, and repeated boundaries are not independent samples.

A separate comparison against the S2 single-task programs gave factor 1.268211 (62.383221 s versus 49.189957 s). This ratio must not be multiplied with ratios from other samples. Individual batch proofs matched the S2 single-task proofs byte for byte and were replayed by both checkers. Small controls covered 32 batches, SAT and UNKNOWN stops, ABA and reverse order, invalid requests and existing-output rejection.

Production status: no batch deployment. The next integration candidate remains the uncached S2 single-task program, subject to complete case validation, six actual pilots, binary-bound native controls, a sealed Git contract, and one regular task through the real controller before the full run. Batch deployment additionally requires per-boundary replay receipts and a tested controller/final-audit path. The running case 77 and T20 remain unchanged; no new exclusion is inferred from these experiments.
