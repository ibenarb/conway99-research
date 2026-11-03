# Independent slice review — 1 November 2026

Update, 3 November: the author has acknowledged the coverage problem. The [reply audit](MIZOPL_REPLY_REVIEW_2026-11-03.md) assesses the proposed replacement argument and corrects the attribution of complete solver replays to us. The dated findings below remain the historical 1 November record.

Scope: the central one-fixed-point involution of an SRG(99,14,1,2), compared with [mizopl/conway-99-graph at 2c5c9ab5381d95baea14816bdb8e538399642778](https://github.com/mizopl/conway-99-graph/tree/2c5c9ab5381d95baea14816bdb8e538399642778). Our initial audit used 1c219d2a4e7e036890293b19aa45ca7921fcc2a0 on 27 October. This is a partial independent audit, not an endorsement or refutation of the full program.

## What we confirmed

Our independent matching/group enumeration reproduced 10,395 matchings, 3,580 B6-orbits of ordered matching pairs, and total orbit weight 108,056,025. The stored [orbit summary](../../results/c2/2026-11-01/slice_orbit_summary.json) includes the category counts. It is a historical result record; the full orbit-enumeration package is not part of this small release.

We independently checked the necessary slice equations against our model contract, the stated exact Gram nullities using integer kernel vectors plus modular lower rank bounds, and the obstruction to three Type-I blocks. The latter is included here as a small executable check. These necessary statements are useful even while larger exclusion claims remain unverified. See the [model contract](MODEL_CONTRACT.md).

## A concrete outstanding coverage question: the 299-case runner

In [run_all_299_nullity3_k1.py, lines 366–378](https://github.com/mizopl/conway-99-graph/blob/2c5c9ab5381d95baea14816bdb8e538399642778/verify-it-yourself/run_all_299_nullity3_k1.py#L366), h0 is fixed to all_H0[0], and the first degree-valid h1 is selected. The [commit comparison](https://github.com/mizopl/conway-99-graph/compare/1c219d2a4e7e036890293b19aa45ca7921fcc2a0...2c5c9ab5381d95baea14816bdb8e538399642778) changes only this runner's output path.

Our [standalone boundary checker](../../verification/c2_slice/audit_boundary.py) generates all 22,176 legal h0 configurations on the remaining ten anchor vertices. It obtains 15 h0 orbits under B5 and 78 ordered (h0,h1) boundary orbits. The [full small output](../../verification/c2_slice/boundary_audit.json) supplies representatives.

An immediate obstruction to treating all boundary pairs as interchangeable is their cycle-type pair:

- The selected first pair has cycle types (10) and (10).
- Another legal boundary pair has cycle types (10) and (4,6).

The unordered pair of cycle types is invariant under B5, exchange of h0/h1 and involution conjugation. Therefore these boundaries are not all equivalent even under those enlarged identifications. A subgroup stabilizing already fixed matching data cannot make the vertex-permutation orbits larger.

**This is not a claim that the omitted boundary extends to a valid full slice or SRG.** It identifies a missing justification for a particular normalization. The remaining obligation is a proof that every potentially extendable joint state (M,E,h0,h1,...) is represented after both the matching and boundary normalizations, or an explicit exhaustive treatment of the necessary boundary orbits with their actual stabilizers.

A general covariance or orbit-transfer lemma is useful, but its hypotheses must be instantiated for the concrete joint data and the implemented search. If a different transformation or a theorem forces the selected boundary among extendable states, that argument and its implementation would resolve the question. Until then, we do not use the claimed 299-case exclusion as a theorem in our C2 chain.

## Improvements and current limits

The newer snapshot now includes standalone CPU searches for 4+2 and 2+2+2 and simple comparison routines. Our earlier observation that those particular programs were missing is no longer current. We have not rerun or fully audited all new searches.

The Class-6 ledger contains 270 distinct indices with sols=0 out of 2,670, including seed indices 0,1670,2118. They must not be added twice. This is the author's search record, not an independently replayed proof. It leaves 2,400 Class-6 orbits outside that reported closure.

The [Lean cascade theorem](https://github.com/mizopl/conway-99-graph/blob/2c5c9ab5381d95baea14816bdb8e538399642778/verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L1464) explicitly takes the graph-to-slice map, coverage/canonicalization obligations and reduced UNSAT statements as hypotheses. Its conclusion concerns involutions. Reading those hypotheses is essential; a theorem name containing nonexistence is not evidence that the unfinished hypotheses have been discharged.

Our own [current C2 progress](STATUS_2026-11-01.md) remains partial as well. Neither our norm-support counts nor their slice-orbit counts measure the same case space. Independent comparison requires an explicit map, not a comparison of headline totals.
