# C2 model contract — public summary, 1 November 2026

This summarizes the project's 21 October model contract and its 31 October slice amendment. It defines the exact problem and safe necessary constraints; it is not a C2 exclusion theorem or a complete release of the underlying proof package.

## Fixed-point input and coordinates

We use the published one-fixed-point result for an involution sigma of an SRG(99,14,1,2): Makhnev–Minakova, Diskretnaya Matematika 16(1), 2004, pp. 95–104, Theorem 1, p. 96 ([original source](https://www.mathnet.ru/php/getFT.phtml?jrnid=dm&option_lang=eng&paperid=144&what=fullt)). This is a cited mathematical input, not a theorem newly proved by our SAT certificates.

Write h for the fixed point. Its 14 neighbours form seven matched pairs P_i, each exchanged by sigma. Each of the remaining 84 vertices is uniquely labelled by a pair of anchors from different P_i. An outer vertex is not adjacent to its sigma-image.

There are 42 outer orbit lines, two for each cell {i,j}, 0 <= i < j < 7. Choose columns n = e_i+e_j and e_i-e_j for N_minus, and e_i+e_j for both corresponding columns of N_plus. Both matrices have size 7 by 42.

## Exact quotient and sign variables

On the 42 lines require:

- Q symmetric and binary, diagonal zero, every row sum 10.
- T symmetric and binary, diagonal zero, every row sum 1.
- Q and T disjoint entrywise.
- D symmetric, entries in {-1,0,1}, with |D| = Q.
- H = Q + 2T.

All four equations are required:

    N_minus D = 0
    D² + D = 12 I - N_minusᵀ N_minus
    N_plus H = 4 J - 2 N_plus
    H² + H = 12 I + 4 J - N_plusᵀ N_plus

Here I and J have the dimensions dictated by the equation. Reconstruct the outer adjacency blocks by B=(H+D)/2 and C=(H-D)/2, and the 84 by 84 outer matrix by [[B,C],[C,B]]. The disjointness and absolute-value conditions make these blocks binary. With the fixed h/anchor frame, the full equations are equivalent to the SRG conditions in the one-fixed-point model. A partial row or unsigned quotient alone is not a graph.

The full 99-vertex SAT models independently enforce symmetry, zero diagonal, involution invariance, degree 14 and, for every distinct i,j,

    sum_k A[i,k] A[j,k] + A[i,j] = 2.

Product and counting auxiliaries are defined in both directions. The semantic audit must account for every actual CNF clause and the complete vertex/pair cover.

## Symmetry and safe partial states

The frame group is C2 wr S7. If a signed coordinate permutation sends n_u to s_u n_pi(u), then Q and T are jointly permuted, whereas

    D'[pi(r),pi(u)] = s_r s_u D[r,u].

Both signs are necessary. A partial-state reduction may use only transformations preserving all existing markings, decisions and boundary data, while transporting the entire continuation. Independently normalizing a matching pair and then fixing an arbitrary boundary representative is not automatically justified.

The partner types disjoint, shared and same_cell all remain allowed. We do not impose a universal same_cell prohibition.

## Confirmed slice amendment

For a rooted anchor pair there is a 12-row by 60-column binary slice matrix X. The involution acts on its 60 columns; write P for that column permutation. The fixed anchor pairing F and the two slice matchings M,E determine its necessary incidence and Gram identities. If their union has c connected components, our exact audit gives nullity 1+c for the corresponding 36 by 36 Gram matrix on the 3,308 classes with nonnegative K.

For a component containing k anchor pairs, each column c satisfies, in the 99-vertex case,

    sum_(i in component) (X[i,c] + X[i,g(c)])
        = k - number of endpoints of c in the component.

A Type-I block is a common pair of F, M and E. Its two-row sum Y has degree four at every outside anchor, is zero on columns incident to its own block and selects one column from every remaining involution pair. Distinct such block sums have inner product four. For three blocks 0,1,2 on anchor pairs (0,1),(2,3),(4,5), let S be their three pairwise inner products. Direct calculation over F2 gives

    S + d_0(3)+d_0(5)+d_1(1)+d_1(5)+d_2(1)+d_2(3) = 1 (mod 2).

Every term on the left would be even. Hence a slice has at most two Type-I blocks. The [independent parity checker and certificate](../../verification/c2_slice/README.md) make this finite identity inspectable.

Let s_ij be the T entry joining the two lines of cell {i,j}. Through B=(H+D)/2 and C=(H-D)/2, s_ij=1 is exactly the Type-I block j in slice i, and conversely the Type-I block i in slice j. Therefore

    sum_(j != i) s_ij <= 2 for each i,
    sum_(i < j) s_ij <= 7.

These are necessary conditions only. They do not imply degree at most one or the existence of a Type-I-free slice. The numerical constants are specific to the 99-vertex case; they must not be copied unchanged to the 9- or 243-vertex positive controls.

Notation: our H corresponds to the external slice project's global quotient B, and our T to its partner matching P_pi. Our reconstruction block B is a different object. T16/T18/T20 denote eigenfunction squared norms, not this matching T.

## Review amendment of 3 November 2026

The [reply audit](MIZOPL_REPLY_REVIEW_2026-11-03.md) confirms the following conditional reduction. Let S be the simple graph on the seven anchor indices with edge ij exactly when the same-cell T entry s_ij equals one. Its degree k_i is the Type-I count of slice i.

If every slice with k_i >= 2 has been validly excluded, S is a matching. Therefore sum_i k_i = 2|E(S)| <= 6, |E(S)| <= 3, and at least one k_i equals zero. This is an existential choice of a Type-I-free root slice. It does not exclude individual slices with k_i=1 and does not prove s_ij=0 for every pair.

**The degree-two exclusions supplied in the external reply have not been independently certified here. The active unconditional bound in this contract remains k_i <= 2 and sum_(i<j) s_ij <= 7.** A seven-cycle demonstrates why the old bound does not already imply a zero-degree root. Such auxiliary graphs are logical controls, not full SRG witnesses.

After the prerequisite is discharged, selecting a particular zero-degree root must transport the entire marked state under the frame group, including Q, T, D and any fixed support. Independent normalization of the root and support is not licensed by the existential statement. The reduction also leaves the Type-I-free search space to be completed.

For necessary slice searches, a safe general pruning rule is residual column capacity. If p(c) is the current number of ones in a column whose final sum is two, and a(c) counts distinct remaining row domains containing at least one candidate with a one there, then p(c)+a(c)>=2 is necessary. Failure excludes the partial assignment; success does not certify a joint completion. This rule requires complete candidate domains and correct domain updates. The [small independent checker](../../verification/c2_slice/audit_reply_20261103.py) validates its arithmetic and finite control cases, not a full external solver.

For a connected component with 2k rows, the already confirmed slice identities give XX^T=9I+J-M, row sum ten, and full column sum two. Because M stays inside the component, its column-sum counts satisfy n0+n1+n2=60, n1+2n2=20k and n1+4n2=4k(k+4). Hence (n2,n1,n0)=(2k(k-1),4k(6-k),2(6-k)(5-k)). These formulas do not remove the coupling between components.

No running solver, CNF, proof, or queue was changed by this documentation amendment.
