# C2 pilot diagnosis and exhaustive partition preparation, 2026-09-14

## Evidence and conclusion
The original user archive is preserved byte-for-byte in this commit. diagnosis.json records its SHA256 and a summary of all eleven full solver logs. No solver log contains a terminal SAT/UNSAT status. Neither summary.json nor per-seed result.json exists. Treat the historical RUNNING fields as stale, not live process evidence. The last controller reports 21718 monotonic seconds, 223.868 GiB proof output, 115.2 GiB disk free and 39.4 GiB RAM available. No recorded resource-floor stop exists.

Seeds 1 and 2 have fewer remaining variables (196914 and 202240 versus roughly 254000-256000), but neither this nor conflict count ranks their probability of finishing. There is no justified completion ETA or proved exclusion.

Correction of prior chat interpretation: converting monotonic elapsed time into an absolute clock timestamp was unjustified. ZIP timestamps (timezone not encoded) record driver.log at 2026-09-14 03:38:54 and status.json at 03:40:40. Sleep, clock discontinuities, VM termination and host crash cannot be distinguished from these logs. The reported Windows crash occurred around 08:04 local time; its causal relationship to termination of this run remains unresolved. Post-reboot proof sizes reported separately by the user are slightly below the last recorded sizes. Partial files must not be represented as verified or resumable solver checkpoints.

## New experiment, not a new theorem
Keep the pinned complete C2 reference CNF and its scope. Split on variables 22, 36, 685, respectively B[0,22], B[0,36], B[22,36]. Their outer labels are {0,2}, {4,6}, {8,10}. These are the three edges of one chosen triple, together with their involution images through the B encoding. This choice is an experimental heuristic, not a claim of balanced or difficult cubes. All eight bit patterns are retained, including any later found equivalent or immediately impossible.

For every full assignment a, the restriction to these three variables is exactly one b in {0,1}^3. Thus F is satisfiable iff one F AND cube_b is satisfiable. Each cube CNF retains the original clause body byte-for-byte and adds exactly three unit clauses. No orbit reduction or unproved symmetry breaker is used. The preparer checks all eight restrictions for unique coverage.

Next benchmark design: eight cubes at seed 0 plus three unsplit baseline controls (seeds 0,1,2), eleven concurrent workers, identical LRAT settings and a bounded calibration budget. A budget here compares configurations; it is not a limit on a future proof campaign. Decide after this measurement whether deeper/adaptive splitting is warranted. Do not interpret a timeout as an exclusion. Any SAT result requires the independent graph checker. Every UNSAT leaf requires checking against its own augmented CNF; all eight certified leaves plus the coverage argument imply baseline UNSAT. The preparer runs no solver and provides no production certificates.

## Reproduction
prepare_partition.py reads the existing baseline.cnf and variables.json on the Ryzen, verifies pinned SHA256 hashes, creates a fresh timestamped output, and writes a baseline copy, eight cube CNFs, variables.json and partition.json. Requires only Python standard library, approximately 0.4 GiB disk. No existing file is changed. CPU and proof resources of the next benchmark are not consumed by preparation.

Local check: regenerated the pinned CNF using the source from the received archive; all pinned input hashes matched; generated and reread all eight augmented CNFs; verified exact prefix and eight-way coverage. local_check.json and partition_checked.json report preparation only. Existing proof data on the Ryzen and its NAS archive are untouched.

Literature scope: Thakkar's arXiv:2608.11211 provides no general involution exclusion. Full C2 exclusion remains the target, conditional on the separately documented fixed-frame completeness and encoder proof. This diagnostic/preparation commit claims no new mathematical exclusion and no global Conway99 nonexistence result.
