# O3 lift theorem: analytic exclusion of `tau=27`

**Status:** project proof prepared for reconciliation milestone  
**Scope:** fixed-point-free automorphism of order 3; actual 99-vertex SRG lift, not merely quotient feasibility

## 1. Setup

For a fixed-point-free order-3 action, write the 33-orbit quotient as

`Q = [[2I+B, C], [C^T, H]]`,

where

- `T` is the set of triangle orbits, `|T|=tau`;
- `U` is the set of non-triangle orbits, `m=|U|=33-tau`;
- `B=S_TT`;
- `C=S_TU`;
- `H=2L+Z` on `U`, with `L` the fixed 2-factor and `Z=S_UU`.

The quotient equation is

`Q^2 + Q = 12 I + 6 J`.

Let

- `e=|E(Z)|`;
- `f=sum C`, the number of quotient `TU` S-edges;
- `W=tr(H^3)/6`, the weighted sum of unordered triangles in `H`.

Since every `U` vertex has S-degree 10,

`f = 10m - 2e`.                                                   (1)

## 2. Block identities

The `TT`, `TU` and `UU` blocks of the quotient equation give

`C C^T = 6I + 6J - B^2 - 5B`,                                    (2)

`B C = 6J - 3C - C H`,                                            (3)

`C^T C = 12I + 6J - H^2 - H`.                                    (4)

Define

`D = (1/2) tr(C^T B C)`.

Combinatorially, `D` is the number of quotient triangles with two vertices in `T` and one in `U`.

## 3. Lift-capacity lemma

**Lemma.** Every actual 99-vertex lift satisfies

`2D <= f`.                                                        (5)

**Proof.**

A `B`-edge joins two triangle orbits by a weight-1 matching. For such a pair the exact quotient equation gives exactly one common S-neighbor orbit. If a `U` orbit is that common neighbor and both incident `TU` quotient edges are present, the three matchings close to three concrete `TTU` triangles in the 99-vertex graph.

Each quotient `TTU` triangle therefore uses all six concrete `TU` edges belonging to its two quotient `TU` matchings. Because the target SRG has `lambda=1`, a concrete edge belongs to exactly one triangle, so different quotient `TTU` triangles cannot reuse a concrete `TU` edge. There are `3f` concrete `TU` edges in total. Hence `6D <= 3f`, i.e. (5).  QED.

This is a lift condition. It is not claimed to be a new independent constraint on quotient model A by itself.

## 4. Global capacity inequality

From (3),

`2D = tr(C^T B C) = 6f - 3 tr(C^T C) - tr(C^T C H)`.

Since `tr(C^T C)=f`, this is

`2D = 3f - tr(KH)`, where `K=C^T C`.                              (6)

Using (4),

`tr(KH) = 6 tr(JH) - tr(H^3) - tr(H^2)`.

Now

- `sum H = tr(JH) = 4m + 2e` because `L` is 2-regular with weight 2;
- `tr(H^2)=8m+2e`;
- `tr(H^3)=6W`.

Therefore

`tr(KH)=16m+10e-6W`,                                              (7)

and (1), (6), (7) give

`2D = 14m - 16e + 6W`.                                            (8)

Combining (5), (8) and `f=10m-2e` yields the necessary lift inequality

`7e >= 2m + 3W`.                                                  (9)

## 5. The case `tau=27`

Here `m=6`. Because `L` is a C4-free 2-factor on six vertices, only two cycle types are possible:

- `C6`;
- `C3 + C3`.

### 5.1 `L=C6`

Every S-edge inside `U` is a chord of the six-cycle. Let

- `a` = number of distance-2 chords;
- `b` = number of diameters.

Then `e=a+b`.

Each distance-2 chord closes two consecutive weight-2 L-edges to a weighted triangle of product `1*2*2=4`. Hence

`W >= 4a`.                                                        (10)

For the distance-2 pair `(i,i+2)`, the fixed `L^2` contribution to the pair equation is 4. The only mixed terms involving diameters are

`2 S_{i,i+3}` and `2 S_{i-1,i+2}`.

The entire remaining budget is 2, so these two diameter indicators cannot both be 1. Across the six distance-2 pairs every pair of the three diameters occurs in such a constraint. Thus

`b <= 1`.                                                         (11)

Applying (9), (10) gives

`7(a+b) >= 12 + 12a`,

or

`7b - 5a >= 12`.

By (11) the left side is at most 7. Contradiction.

Therefore no actual SRG lift exists with `tau=27, L=C6`.

### 5.2 `L=C3+C3`

Lemma B applied to either L-triangle says every exterior quotient vertex meets it in exactly one S-edge. In particular the two L-triangles are joined by a perfect S-matching, so

`e=3`.

Each L-triangle contributes weighted product `2*2*2=8` to `W`; therefore

`W >= 16`.

Inequality (9) would require

`21 = 7e >= 12 + 48 = 60`,

a contradiction.

Therefore no actual SRG lift exists with `tau=27, L=C3+C3`.

## 6. Theorem

**Theorem.** No actual `srg(99,14,1,2)` admitting a fixed-point-free automorphism of order 3 can have `tau=27`.

Together with the independently proved project congruence `tau in {6,27}`, this leaves

`tau=6`

for the fixed-point-free order-3 branch.

## 7. Exact regression

`src/reconciliation/o3_tau27_lift_check.py` checks, using integer arithmetic only:

- the algebraic reduction from (5) to (9);
- all 512 C6 chord masks against the necessary diameter budgets and capacity inequality;
- the `2C3` arithmetic contradiction.

The script is a regression for the finite/arithmetic part of this proof. The proof itself is the transfer argument above.