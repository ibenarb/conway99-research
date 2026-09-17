# C2 reference / totalizer: paired 20-minute scout

Run: matching_20260916_204748_316173. Source commit:
db4e1d27422c7f1ce07dc5962180f036651edf41.

## Result

All 22 jobs OPEN_BUDGET, solver exit 0, each log UNKNOWN. No SAT or UNSAT result.
2406 seconds total wall time, approximately 7.335 CPU hours. No interrupted jobs,
no guard read retries, no proof output. No new mathematical exclusion.

Original received ZIP retained byte-identically. analyze.py reproduces analysis.json:
run `python3 analyze.py` in this directory. CRC and 22 log/result/job crosschecks pass;
11 paired assumption lists, seeds and time budgets agree. This audit does not read
production CNFs (absent from the received ZIP); stored input hashes are provenance,
not an independent rehash of the user's input files.

## Diagnostics

| Quantity (median over 11 cases, except total conflicts) | Reference | Totalizer |
|---|---:|---:|
| Peak RSS MiB | 746.62 | 558.40 |
| Remaining variables, including auxiliaries | 232934 | 153672 |
| Irredundant clauses | 1220575 | 1180508 |
| Total conflicts, all cases | 4559820 | 5159081 |

Median peak RSS decreases 25.21%, median remaining variables 34.03%, median
irredundant clauses 3.28%. All paired peak RSS values are lower with totalizer.
Total conflicts increase 13.14% for essentially equal CPU budgets. Conflict counts
across different encodings do not measure equal work or progress to a decision.
The changed auxiliary numbering and clause order also change branching trajectories.
All observations are for one seed, one fixed wave order, no statistical replication.

| Case | Ref variables | Totalizer variables | Ref clauses | Totalizer clauses | Ref peak MiB | Totalizer peak MiB |
|---|---:|---:|---:|---:|---:|---:|
| 1_1_1_1_1_1 | 206744 | 138580 | 1084750 | 1058952 | 703.42 | 527.96 |
| 1_1_1_1_2 | 217782 | 142149 | 1142500 | 1094295 | 714.82 | 534.26 |
| 1_1_1_3 | 222665 | 155243 | 1166946 | 1107156 | 771.32 | 536.77 |
| 2_2_2 | 238796 | 159655 | 1251981 | 1212897 | 760.23 | 564.56 |
| 1_1_2_2 | 227645 | 125516 | 1194162 | 1196894 | 747.21 | 543.42 |
| 1_1_4 | 227965 | 153672 | 1193995 | 1176324 | 746.62 | 543.44 |
| 1_2_3 | 232934 | 166352 | 1221151 | 1177361 | 737.95 | 558.40 |
| 1_5 | 233113 | 154540 | 1220575 | 1180508 | 796.80 | 564.84 |
| 2_4 | 238327 | 131829 | 1248908 | 1247010 | 759.91 | 564.68 |
| 3_3 | 238478 | 161660 | 1250255 | 1236896 | 744.60 | 565.16 |
| 6 | 238497 | 79526 | 1249533 | 1545579 | 715.20 | 565.49 |

Type 6 is a cautionary example: variables fall from 238497 to 79526 while
irredundant clauses rise from 1249533 to 1545579 (about 24%). More elimination
can yield fewer variables and more clauses. No inference of solution proximity.

## Decision and next hypothesis

Keep the totalizer as a lower-memory experimental encoding and retain the immutable
reference for correctness and comparisons. Do not declare a speed winner from all-open
censored runtimes. Do not infer that 13% more conflicts means 13% shorter proof time.
A further blanket eight-hour run has no demonstrated advantage from this experiment.

Next priority: expose structural incompatibilities directly on primary edge variables.
For an outer pair x,y with c fixed common neighbors, E3 gives:

    M_xy + sum_z M_xz*M_yz = 2-c.

For c=1, the pairwise incompatibilities of the positive summands can be expanded
into short primary clauses (e.g. not M_xy OR not M_xz OR not M_yz). Two distinct
outer common neighbors similarly give a four-edge forbidden conjunction. These are
logical consequences, not new graph restrictions. Existing BDD/totalizer constraints
already enforce them semantically; explicit clauses might improve propagation, or
merely add overhead. Their benefit must be measured, not assumed.

Before another pilot: enumerate/deduplicate candidate clauses, remove tautologies and
fixed-zero cases, measure clause count/width and unit-propagation impact; establish
formal implication and small exhaustive controls. Select a bounded family with a
clear mathematical interpretation. Benchmark as a separate ablation on the same 11
cases. A structural split across interacting neighborhoods is an alternative if this
adds little; any new split requires complete case coverage. No new campaign launched.

This report concerns C2 only and makes no new K66 archival or global symmetry claim.
