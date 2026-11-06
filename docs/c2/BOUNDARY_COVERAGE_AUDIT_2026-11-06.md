## Status, 6 November 2026

Our independent L62 campaign has certified **11 of 62 cases**: 3, 4, 17, 18, 20, 62, 63, 68, 74, 75 and 76. **51 remain**, including case 77 currently running. We count a case only after independent proof replay, a complete checked proof archive and versioned documentation. Neither L62 nor C2 is closed.

## Reproducible boundary-coverage finding

We are grateful to Mizopl for sharing code and detailed algorithmic ideas. An audit of [the published implementation at commit d3ac3b573e8b824609398af879b6c62b9aaceb39](https://github.com/mizopl/conway-99-graph/tree/d3ac3b573e8b824609398af879b6c62b9aaceb39/verify-it-yourself) found an inconsistency between **numerical mask order** and **unsorted pool index order**, in the nullity-4 k2 (1,1,4) boundary selection.

External class 0 maps to our independently excluded case 4. The four boundary masks, occupying full rows 8–11, are:

```
18084836003153921
4644487506690754
565424259352594
290340897587752
```

Their original zero-based pool indices are **5527, 8101, 6119, 15565**. Columns are the source's 60 endpoint pairs: b<c in 0..5, then s,t in 0..1, endpoints (2b+s,2c+t).

An independent standard-library checker verifies the boundary against D=2J-I-F-M-EF, G=9I+J-M, K=2J-F-E-ME-EM and column capacities ≤2. It also verifies all 256 declared coupled transformations against the **full** D/G/K contract, commutation with P, identity and group closure.

Every transformed boundary fails one of the first three original selection guards:
- 240 transformations: y0 is not its numerical canonical mask;
- 12: y0 is canonical, but i1≤i0;
- 4: y0 is canonical and i1>i0, but canon(y1)<y0.

These count transformations, not necessarily distinct images.

The lexicographically least image is:

```
17910082046496
13581717521039381
290408912397442
1130367247483176
```

Its original indices are **15735, 896, 9968, 14847**. The first mask is numerically smaller than the second, but its pool index is larger. Thus the declared symmetry selection rejects an entire valid boundary orbit.

The original rem34 preparation was executed verbatim up to the first solver call; its ordered pools, adjacency, canonical arrays and stabiliser lookup tables agree with the independently examined state. The finding is not based solely on sampled reviewer output.

## Scope and repair

This is a **coverage defect in the examined implementation**, not a twelve-row SAT witness, not a Conway graph, and not a disproof of the mathematical UNSAT conclusion. Our case-4 exclusion was independently established.

Sorting whole pool records numerically **before rebuilding every index-dependent adjacency, representative array and cache** repairs this particular order inconsistency. The least image then has sorted indices **241, 11737, 6136, 14061** and passes all boundary symmetry guards. Removing only one explicit index guard is insufficient while adjacency still imposes j>i.

For the checked group/domain, a lexicographic-minimum argument proves that a least orbit representative survives the sorted selection: pure pair swaps impose consistent within-pair order, and stabiliser comparisons cannot reduce a lexicographically least tuple. This does **not** certify every other pruning rule, buffer bound or all 56 class setups.

A prefix-only enumeration over all 1,482 y0 representatives accepts 188,234 prefixes in the original order and 1,792,351 after sorting/reindexing (ratio 9.52193015). These are **not full-search counts or timings**: tail-triggered early exits are absent. No several-orders-of-magnitude runtime comparison is established.

## Next work

1. Validate corrected ordering and coupled group actions across all relevant classes, with positive controls and independent coverage checks.
2. Reuse filtering for shared boundary prefixes, avoiding repeated preparation.
3. Fuse column-capacity support accumulation into existing domain filters; an earlier separate-pass prototype was slower, so correctness and measured benefit must both be demonstrated.
4. Benchmark identical complete domains, including proof generation, independent replay and memory use; report preparation/JIT separately.

Production searches and their checked proof files remain unchanged while bounded experiments proceed. A faster search will be adopted only with an independently reviewed correctness argument and verified proof replay.

Public discussion: https://github.com/ibenarb/conway99-research/issues/3
