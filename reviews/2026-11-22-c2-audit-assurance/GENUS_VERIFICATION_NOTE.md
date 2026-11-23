# Packing-independent genus route: project verification note

22 November 2026. This note verifies finite certificates supplied by the
referee and records the double-counting argument. It is not a new claim of
priority for the C2 proof. The alternative genus construction is credited to
the referee's evidence package; Zhang's original proof retains its own
packing route.

## Finite computations reproduced

The new checker imports neither the original search nor the referee's
genus library. It uses PARI/GP 2.15.4 through cypari2 and exact integer
arithmetic (NumPy operations have explicit overflow bounds). The common
PARI backend is a dependency; this is not an independent implementation
of PARI's lattice algorithms.

For the supplied 31 Gram matrices the complete run checks positive
definiteness, determinant 256, integral 2G^-1 with even diagonal, the
rank-eight discriminant condition, independently recomputed automorphism
orders and all 465 pairwise nonisometry tests. It exhibits seven
pairwise orthogonal dual units in every class.

It reconstructs all 248 intrinsic K8 geometries and all admissible norm-five
vectors. Exactly 122 geometries have an empty required class. In the
remaining excluded 46 cases, every column of the exact constraint matrix
is tested against the supplied integer Farkas vector: yA <= 0 and yb > 0.
No floating-point LP status is accepted as proof. The other 80 geometries
are conservatively retained, all eight vertices of ten classes. Their
root counts match the supplied atlas. Retention is not a claim that a graph
or a compatible global configuration exists.

The complete finite record is finite_result_v2.json. A separate mass
arithmetic run checks the five rank-15 unimodular Gram matrices and their
automorphism orders, all 32768 norm residues per matrix, and the rational
mass identity (mass_result_v1.json).

## Why the mass identity proves coverage

Let L be any integral positive definite rank-15 lattice with determinant
2^8, elementary discriminant group, and integral norms on L*. On
D = L*/L the form b(x,y) = 2(x,y) modulo 2 is nondegenerate and alternating:
integral dual norms make b(x,x)=0. Hence D is a symplectic vector space of
dimension eight over F2.

An integral unimodular overlattice V corresponds to a Lagrangian of D.
Every Lagrangian has dimension four, so [V:L]=16 and det(V)=1.
The number of Lagrangians is
(2+1)(4+1)(8+1)(16+1) = 2295.

Conversely fix an integral unimodular rank-15 lattice V and a
four-dimensional subspace C of V/2V whose norms vanish modulo four.
Set L = {x in V : (x,c) is even for all c in C}.
Nondegeneracy modulo two gives [V:L]=16. The doubly-even condition implies
that C is self-orthogonal modulo two. Thus
L* = V + (1/2)C has integral norms and 2L* is contained in L.
It follows that det(L)=256 and L*/L is elementary of dimension eight.
These two constructions give the same isomorphism classes of pairs.

The established classification of positive definite integral unimodular
lattices of rank 15 has five classes:
Z^15, Z^7 + E8, Z^3 + D12+, Z + (E7 + E7)+, and A15+.
A precise published reference is J. H. Conway and N. J. A. Sloane,
“The Unimodular Lattices of Dimension up to 23 and the Minkowski–Siegel
Mass Constants”, European Journal of Combinatorics 3 (1982), 219–231.
Theorem 1 and Table 1 on p. 219 classify all lattices without norm-one
vectors; Section 2.2 on p. 223 gives the unique orthogonal splitting
of all norm-one directions. The reduced ranks at most 15 are exactly
0, 8, 12, 14 and 15, yielding the five rank-15 classes listed above.
Table 2 on p. 224 independently gives exactly the same m15 used below.
This is an established published classification input, not a new result
of the finite checker. The paper was consulted directly on 22 November 2026:
https://neilsloane.com/doc/Me102.pdf

For each of the five classes the even-norm hyperplane of V/2V has dimension
14. Its quadratic form q(v)=v^2/2 modulo two is nondegenerate. This follows
from the characteristic vector being outside that hyperplane in odd rank.
Direct enumeration gives 8256 zeros including zero, identifying the split
type. Thus it is O+_14(2).

The number N of totally singular four-spaces follows by counting ordered
bases. After a d-dimensional singular space is chosen, the quotient is
split of dimension 14-2d. Each nonzero singular quotient vector has 2^d
lifts. Therefore

N = product[d=0..3] {2^d (2^(7-d)-1)(2^(6-d)+1)}
    / product[d=0..3] (16-2^d)
  = 3876193035.

The reciprocal automorphism orders of the five classes sum to
m15 = 29713/385648863215616000.
Weighted counting of pairs (V,C), equivalently pairs (L,V), now gives

sum_[L] 1/|Aut(L)| = N*m15/2295
                  = 116980081/898948399104000.

Each of the 31 supplied classes is in the required family. They are
pairwise nonisometric, and the sum of their independently recomputed
reciprocal automorphism orders equals this target exactly. Every omitted
class would contribute a positive amount. Hence, conditional only on the
cited five-class unimodular classification and the standard group-action
count just explained, there is no omitted class. Random sampling of the
other unimodular lattices is not needed for this completeness argument.

## Reproduction and limitations

Install Python with numpy and cypari2 backed by PARI 2.15.4. From this
directory run the certificate checker and then the mass checker. Both
write fresh result files exclusively: use a new directory for a second
run or archive the previous results first. Do not overwrite evidence.

The finite checks and the mathematical completeness argument, including
the precise published classification citation, are now documented.
Editorial integration into a future manuscript revision remains; the
frozen reviewed version is not overwritten. No complete second
singleton-root search follows from the genus result. That is a separate
task S1.

Version 1 of the certificate checker stopped when PARI represented an
empty root set by a zero-row matrix. Version 2 handles that case, passed
positive and empty enumeration controls, and completed every class.
The failed run is retained and has no exclusion status.
