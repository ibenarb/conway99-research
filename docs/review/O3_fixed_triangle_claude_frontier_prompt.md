# Claude review prompt — O3 fixed-K3 hard frontier after structural V3

You are reviewing the Conway_99 project branch `o3-review-reconciled-20260907` in repository `ibenarb/conway99-research`.

Please treat the project-owned mathematics and exact solver/certificate standards as fixed unless you find a concrete error. Your task is not to re-summarize the project but to attack one sharply defined remaining bottleneck: the hard frontier of the order-3 automorphism fixed-K3 quotient exclusion.

## Canonical sources to read first

1. `docs/breadth1/O3_fixed_triangle_internal_model.md`
2. `src/reconciliation/o3_fixed_triangle_certify.py`
3. `docs/breadth1/O3_fixed_triangle_structural_v3.md`
4. `src/reconciliation/o3_fixed_triangle_structural_v3.py`
5. `docs/breadth1/O3_fixed_triangle_v3_frontier_analysis.md`

Do not assume that a SAT-hard case is feasible. The only accepted exclusion standard is project-owned WLOG coverage plus LRAT verification and Cake positive `s VERIFIED UNSAT` for every terminal CNF.

## Settled fixed-K3 reduction

A nontrivial order-3 automorphism has either no fixed vertices or exactly a fixed K3. In the fixed-K3 branch the remaining 96 vertices form 32 three-orbits. Exactly two of these are triangular; they are canonically T={12,13}. There are three attachment groups A0,A1,A2 of four three-orbits each, attached to the three fixed vertices. The 32x32 three-orbit block is

    P = 2 D_T + S + 2 L

with S,L disjoint simple graphs. Degrees are:

- attached: deg_S=11, deg_L=1
- T: deg_S=12, deg_L=0
- ordinary unattached: deg_S=10, deg_L=2

For each attachment group G and any three-orbit v,

    sum_{u in G} P_uv = 1 if v is attached,
                         2 if v is unattached.

The full quotient equations are exact and encoded in the root CNF whose SHA256 is

    b55a21481c2514770af5103a000e4a18bb16723a2d61224ca6afc87c0eeabdd0

## Structural V3 result

The two T-neighbourhoods meet each attachment group in two vertices. Under the matching-preserving D8 action there are seven ordered local types. After S3 permutation of the three groups, T-swap, and S18 canonicalization of the ordinary T-neighbourhood pair, there are exactly 72 WLOG T-skeleton cases: 62 with s=S(12,13)=0 and 10 with s=1.

V3.1 certified 29/72 structural roots with LRAT+Cake, representing 7.579303% of all labelled T-skeletons. It left 43 hard cases, representing 92.420697%.

The frontier audit reveals an exact empirical classifier on the s=0 branch:

- all 22 certified s=0 roots contain local type 2;
- all 40 hard s=0 roots contain no local type 2.

Type 2 is represented, relative to the canonical internal matching {01,23}, by

    N12={0,1}, N13={2,3}.

The s=1 branch has only three hard cases:

    225, 256, 566

with total labelled weight 0.268792%.

The dominant hard mass is a=3 and a=4, where a is the number of attached vertices common to the two T-neighbourhoods. These two values alone carry about 81.82% of the entire labelled T-skeleton space.

## Critical diagnosis of V3 cubing

After the T-skeleton was fixed, every dynamic split used only

    S(10,14), S(10,15), S(10,16), S(10,17).

No hard structural case was completed after up to four such split levels.

This appears to be symmetry-redundant branching. For s=0, among the 18 ordinary vertices the four T-adjacency cells have sizes

    O11=6-a, O10=a, O01=a, O00=12-a.

Therefore the residual stabilizer contains at least

    S_(6-a) x S_a x S_a x S_(12-a).

For the dominant cases:

    a=3: S3 x S3 x S3 x S9
    a=4: S2 x S4 x S4 x S8.

So raw splitting on individual ordinary labels is likely exploring huge families of equivalent descendants.

## Additional exact deductions now available

Please check these carefully and use them if correct.

### L structure

For attached v and every attachment group G, the weighted sum into G is 1. Since P=S+2L, an attached vertex has no L-edge to any attached vertex and exactly one S-neighbour in each attachment group. Its unique L-neighbour is therefore ordinary.

For an ordinary vertex and each attachment group, weighted degree 2 means exactly either one L-edge or two S-edges into that group.

Hence on the 30 non-T vertices L has:

- 12 attached vertices of degree 1;
- 18 ordinary vertices of degree 2;
- no attached-attached edges;
- exactly 12 attached-ordinary and 12 ordinary-ordinary L-edges.

Its components are six paths with attached endpoints plus zero or more cycles entirely among ordinary vertices.

### Four-cell aggregate equations for s=0

Let A=C11, B=C10, C=C01, D=C00 among the 30 non-T vertices according to S adjacency to T=12,13. The total cell sizes are always

    |A|=6, |B|=6, |C|=6, |D|=12,

independent of a.

For any v with x=S(12,v), y=S(13,v), the T equations imply weighted P-degree from N12 to v equal to 6-3x, and from N13 equal to 6-3y.

If W_XY is total P-weight between cells, with W_XX counting each undirected edge once, all aggregate weights are determined by a and one even integer p=W_AB=W_AC:

    W_AA=W_BB=W_CC=(18-p)/2
    W_AB=W_AC=p
    W_BC=36-p
    W_AD=54-a-p
    W_BD=W_CD=18+a+p
    W_DD=39-a-p/2

with p in {0,2,...,18}.

### Four-cell aggregate equations for s=1

The total cells are

    |A|=1, |B|=10, |C|=10, |D|=9.

The analogous equations force p=W_AB=W_AC=2 because |A|=1 implies W_AA=0. Thus the coarse P-weight table is fixed by a alone.

## Questions for you

Please focus on proving or exploiting further structure, not on generic solver tuning.

1. Verify the new L-structure and four-cell aggregate derivations independently. If anything is wrong, identify the exact step.

2. Can the s=0 no-type-2 condition be turned into a stronger algebraic/combinatorial description? In particular, is there a useful characterization of local types {0,1,3,4,5,6} that explains why type 2 cases collapse quickly and the complementary sector survives?

3. Find the strongest sound second-layer WLOG reduction under the residual stabilizer. A preferred coordinate is the full S/L neighbourhood of one attached vertex relative to the four ordinary T-cells. Because the stabilizer permutes each cell, raw subsets should reduce to count vectors plus the cell containing the unique L-neighbour. Derive the exact admissible count equations if possible.

4. Alternatively or additionally, exploit the L graph as six attached-to-attached paths plus possible ordinary cycles, decorated by the three attachment-group modes. Can this classify or exclude some of the 40 s=0 hard structural cases without large SAT search?

5. For the three s=1 hard cases 225,256,566, use the fact that the coarse four-cell P table is already fixed. Can you derive a direct contradiction, or reduce them to a very small exact finite case list suitable for LRAT+Cake certification?

6. Propose a concrete V4 case decomposition. It must come with an explicit group action / WLOG coverage argument. Estimate case counts before SAT. Prefer a decomposition that removes factorial label symmetry before any binary cubing.

7. Look for a genuine analytic exclusion first. If you can prove that some feature of all 40 s=0 hard classes contradicts the quotient equations, state a formal lemma and proof. Do not infer impossibility merely from solver hardness.

## Desired output

Return a technical review in five sections:

A. Validation/corrections of the deductions above.
B. New lemmas, with proofs or proof sketches precise enough to implement/check.
C. Recommended V4 decomposition, including the exact residual symmetry group and canonical representatives.
D. Separate treatment of the three s=1 hard cases.
E. Go/no-go ranking of the next computational experiments, with expected case counts and why each is informative.

Be explicit about which statements are theorems, which are conjectures, and which are computational heuristics.
