# Independent residual-Gram low-rank solver, version 1

Source of the mathematical specification: frozen low-simplex-packet/Theorem.md
at mxym/math d73a176f942b1fd67bac3b60c07d181487d84b66.
The new search is residual_gram_v1.cpp. It does not use the author's low-rank
search implementation. Input geometry, chart construction and the attachment
generator are the referee's separate implementation, copied without changing
any running high-rank code. This is therefore an independent search relative
to the original proof, not an entirely new independent derivation of inputs.

For local rank r=8 or 9, use a nondegenerate ambient residual space of dimension
n=13-r, with determinant character det(Q). The m=11-r anchor residuals have
zero Gram matrix. A candidate supplies its pairings h with those anchors and
its residual norm. Every selected outside pair supplies its unsigned T from
the integer word product and every allowed signed L. The residual product is
-4L-z_x.z_y-f_x[I]^T Q^{-1} f_y[I], modulo seven.

A candidate is extended coherently against the selected clique: all allowed
products are enumerated in its one extended Gram matrix. Retain that matrix
if its rank is at most n, and, when its rank equals n, its nonsingular principal
minor has the determinant character of the ambient residual space.
No determinant-character rejection is made at smaller rank. Those weaker
tests are necessary conditions, not assertions that every accepted matrix
embeds in the required ambient space.

In rank eight all common h-vectors are restricted to a single one of the 57
planes of F7^3. In nonsplit rank nine they are restricted to one of the eight
lines of F7^2. Every smaller common image is contained in such a plane/line.
In split rank nine h is unrestricted in F7^2: the Gram search simultaneously
includes anchor-image dimension zero, one and two. There is no assumption of
independent residual anchors, no separate hyperbolic coordinate normalization,
and no missing low-image branch.

The reason the determinant test is necessary: a Gram matrix of rank n from
vectors in a nondegenerate n-space contains an n-vector basis; changing basis
multiplies the ambient determinant by a nonzero square. Independent columns
of a symmetric rank-n matrix give a nonsingular principal minor. These facts
also justify the implementation's column-basis minor.

The unsigned/signed exact Schur and rational range tests are enforced during
attachment generation. Each selected outside pair is also checked against the
exact rational Cauchy inequality and the literal 43-vertex graph capacities.
The Cauchy and capacity tests are only necessary conditions. Future-label
support is existential relative to the chosen clique; it cannot overprune a
true global realization. Minimum-domain choice changes order only. All 30
labels are searched, without a depth or wall-time cutoff. OPEN is never an
exclusion. No automorphism pruning is used.

Finite Gram controls compare modular column reduction against an independent
oracle enumerating principal minors with exact integer Bareiss determinants:
all 343 symmetric 2x2 matrices with multiple ambient dimension/type choices,
random larger symmetric matrices, 160 genuine ambient Gram matrices, and
explicit negative controls. 2366 cases passed (1375 accepted, 991 rejected).
These controls are evidence for the implementation, not a replacement for
the preceding mathematical necessity argument.

Before accepting a research result, require nonempty exact star coverage,
all word products checked, both chart parities, the correct rank-9 determinant
type, full natural search exhaustion, and no sanitizer/overflow/input error.
For rank eight also require exact agreement with the previously independently
recomputed viable star/plane counts. All results remain per-job until a full
coverage reconciliation has passed.
