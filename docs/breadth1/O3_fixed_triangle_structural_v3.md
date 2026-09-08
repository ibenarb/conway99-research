# Fixed-K3 structural V3 certification

## Goal

Replace generic frequency-based cubing of the fixed-K3 quotient CNF by a project-owned structural WLOG reduction before any dynamic SAT splitting.

The root model is unchanged and remains pinned to

`b55a21481c2514770af5103a000e4a18bb16723a2d61224ca6afc87c0eeabdd0`.

The proof target is still: the exact 35-orbit fixed-K3 quotient model is UNSAT.

## 1. Why V2 stalled

V2 started from eight high-frequency primary variables. The first five were

- `S(11,12)`
- `S(11,13)`
- `S(10,12)`
- `S(10,13)`
- `S(12,13)`.

The only two initial 5-bit prefixes that certified quickly were `00001` and `11111`. These are explained structurally: in attachment group `A2={8,9,10,11}`, both T vertices then have the same two neighbours when `S(12,13)=1`. But the T-pair quotient equation permits only one common S-neighbour outside the pair in that case. Hence both prefixes contain an immediate local contradiction. The remaining generic binary splits did not exploit the residual orbit symmetry.

## 2. T-neighbourhood equations

The two triangular 3-orbits are `T={12,13}`. Each has S-degree 12 and L-degree 0.

For each attachment group `A_r` of size four, equation (13) in `O3_fixed_triangle_internal_model.md` gives

`sum_{u in A_r} P_{u,t}=2` for `t in T`.

Since T has no L-edges, each T vertex therefore chooses exactly two of the four vertices in each attachment group.

Let `s=S(12,13)`. The quotient equation for the pair 12,13 is

`sum_{k != 12,13} S(12,k)S(k,13) + 5s = 6`.

Hence their number of common S-neighbours outside the pair is

`6-5s`.

Each T vertex already has six S-neighbours in the three attachment groups, so it has exactly `6-s` ordinary unattached S-neighbours among vertices 14..31.

## 3. Seven local attachment types

Inside an attachment group the canonical internal S-matching is `{01,23}`. Its stabilizer on the four labels has order eight (the matching-preserving `D8`/wreath action).

An ordered pair `(N_12,N_13)` of two-subsets has 36 labelled possibilities. Under this residual group there are exactly seven orbits. Canonical representatives are:

| type | N12 | N13 | intersection |
|---|---|---|---:|
| 0 | 01 | 01 | 2 |
| 1 | 01 | 02 | 1 |
| 2 | 01 | 23 | 0 |
| 3 | 02 | 01 | 1 |
| 4 | 02 | 02 | 2 |
| 5 | 02 | 03 | 1 |
| 6 | 02 | 13 | 0 |

Swapping T vertices maps type 1 to 3 and 3 to 1; the other five types are invariant up to the local matching-preserving group.

The V3 generator reconstructs these seven orbits from all 36 labelled pairs and aborts unless the partition is exact.

## 4. Global WLOG reduction

The three fixed vertices, hence their three attachment groups, may be permuted by `S3`. Therefore a triple of local types may be sorted. The two T vertices may be exchanged, so the sorted triple is further identified with the sorted triple after the global type swap `1 <-> 3`.

For a type triple let `a` be the sum of its three local intersection sizes.

The 18 ordinary unattached vertices are still freely permutable by `S18`. Each T vertex has ordinary degree `d=6-s`, while their ordinary common-neighbour count is forced to

`c = 6-5s-a`.

For fixed `(d,c)`, every ordered pair of d-subsets of an 18-set having intersection c lies in one `S18` orbit. Hence it has a canonical representative.

Admissibility requires `0 <= c <= d`.

Exhaustive enumeration gives exactly

- 62 WLOG classes with `s=0`;
- 10 WLOG classes with `s=1`;
- 72 structural classes in total.

No SAT assumption is used in this orbit count beyond the project-owned local equations above.

## 5. Exact structural coverage accounting

Before quotienting by symmetry, the number of labelled ordinary-neighbourhood pairs with sizes d,d and intersection c is

`C(18,d) C(d,c) C(18-d,d-c)`.

V3 enumerates all `36^3` labelled attachment patterns for each `s`, filters by `0<=c<=d`, maps each to its structural WLOG class, and multiplies by the ordinary-neighbourhood count.

The resulting exact labelled T-skeleton universe has

`3,544,507,983,744`

patterns.

The script aborts unless this total, the seven local types, and the 62+10 class count are reproduced. A case is counted as covered only when every dynamic descendant of that structural case is LRAT+Cake certified UNSAT. Therefore `structural_coverage` is an exact weighted fraction of this labelled T-skeleton universe, not a solver-activity proxy.

## 6. SAT and UNSAT standards

For each structural representative V3 adds only unit assumptions to the unchanged root CNF. It also writes the implied absence of all L-edges incident with T explicitly as units for propagation.

- SAT is accepted only through the independent 35x35 quotient reconstruction inherited from V2.
- UNSAT leaves are accepted only after `lrat-check` exit 0 and Cake exit 0 with the positive marker `s VERIFIED UNSAT`.
- Proofs above the configured size cap and timed-out leaves are not accepted; the corresponding structural case is split further on a remaining primary variable.
- Solver and checker concurrency is capped at 21+1 compute lanes.
- State is resumable and pinned to both the root-CNF hash and the structural-manifest hash.

The V2 6.25% certificates remain valid diagnostic evidence but are not required by the V3 proof chain. V3 is an independent WLOG cover of the entire fixed-K3 quotient search space.
