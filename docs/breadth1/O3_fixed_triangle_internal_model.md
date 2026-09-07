# Order-3 fixed-triangle branch — project-owned reduction and certified quotient model

**Purpose:** remove the dependence on the historical computer result that every order-3 automorphism is fixed-point-free.

The argument has two parts:

1. a self-contained SRG proof that a nontrivial order-3 automorphism has either no fixed vertices or exactly a fixed `K3`;
2. an exact quotient CNF for the remaining fixed-`K3` case. If this CNF is certified UNSAT, fixed-point-freeness becomes an internal project consequence rather than an imported computer theorem.

## 1. Fixed-set dichotomy from the SRG equations

Let `g` have order 3 and let `F=Fix(g)`. Assume `F` is nonempty. For `v in F`, all neighbors outside `F` occur in 3-cycles of `g`, so

`deg_F(v) ≡ 14 ≡ 2 (mod 3)`.                                     (1)

For two fixed vertices `u,v`, their common neighbors outside `F` also occur in 3-cycles. The total number of common neighbors is 1 if `u~v` and 2 otherwise, both smaller than 3. Hence **all** common neighbors of a fixed pair are fixed. Therefore the induced graph on `F` has

- exactly one common neighbor for adjacent pairs;
- exactly two common neighbors for nonadjacent pairs.              (2)

It is connected: vertices in different components would be a nonadjacent pair with zero common neighbors. It contains a triangle because every edge has a common neighbor, and (1) gives positive fixed degree.

Write `d_v=deg_F(v)`. Counting length-2 walks from a fixed vertex `v` gives

`sum_{x~v} (d_x-1) = d_v + 2(|F|-1-d_v)`,

hence

`sum_{x~v} d_x = 2|F|-2`.                                        (3)

With adjacency matrix `A_F` and degree vector `d=A_F 1`, equation (3) is

`A_F d = (2|F|-2) 1`,

so

`A_F^2 1 = (2|F|-2) 1`.                                          (4)

Because `F` is connected and non-bipartite, `A_F^2` is irreducible on the Perron component and `-rho(A_F)` is not an eigenvalue of `A_F`. Equation (4) therefore forces `1` to be the Perron eigenvector of `A_F`; the fixed graph is regular. Let its degree be `k`.

Thus `F` is an `srg(f,k,1,2)` with `f=|F|`. The standard parameter identity gives

`k^2 = 2(f-1)`.                                                   (5)

By (1), `k ≡ 2 (mod 3)`, and `k<=14`. Equation (5) makes `k` even, so the only candidates are

`k in {2,8,14}`, giving `f in {3,33,99}`.

`f=99` would make `g` the identity. For `f=33,k=8`, the nontrivial eigenvalues of an `srg(33,8,1,2)` would be `2` and `-3`; their multiplicities would require

`8 + 2m - 3(32-m)=0`, i.e. `5m=88`, impossible.

Hence a nontrivial order-3 automorphism has

`Fix(g)=empty` or `Fix(g)=K3`.                                    (6)

No external fixed-point classification is used in (1)–(6).

## 2. Orbit structure in the fixed-`K3` case

Assume now `Fix(g)=K3`. The other 96 vertices form 32 orbits of length 3.

Each fixed vertex has two fixed neighbors and twelve outside neighbors, hence is adjacent to exactly four whole 3-orbits. Adjacent fixed vertices have no common outside neighbor because their unique common neighbor is the third fixed vertex. Therefore the three four-orbit attachment sets are pairwise disjoint: there are exactly 12 attached 3-orbits, four for each fixed vertex.

An attached 3-orbit cannot itself induce a triangle: otherwise an edge from its fixed vertex to one orbit vertex would have the other two orbit vertices as two common neighbors, contradicting `lambda=1`.

## 3. The number of triangle 3-orbits is exactly two

Let `tau` be the number of the 32 length-3 orbits that induce triangles.

The equitable quotient has dimension 35. Its eigenvalues are among `14,3,-4`; write the nonprincipal multiplicities in the quotient as `a,b`. Then

`a+b=34`,

and the quotient trace is `2tau`, so

`2tau = 14 + 3a - 4b = 7a - 122`.

Thus

`tau ≡ 2 (mod 7)`.                                                (7)

The full graph has 231 triangles. Under `g`, a setwise fixed triangle is either the fixed `K3` itself or one of the `tau` triangular 3-orbits. Hence

`231 ≡ 1+tau (mod 3)`,

so

`tau ≡ 2 (mod 3)`.                                                (8)

The 12 attached orbits are non-triangular, so `tau<=20`. Combining (7), (8) gives

`tau = 2`.                                                        (9)

This is a project-owned analytic reduction.

## 4. Canonical labels

Label the three fixed vertices `f0,f1,f2`. Label the 32 length-3 orbits `0..31` so that

- `A0={0,1,2,3}` is attached to `f0`;
- `A1={4,5,6,7}` is attached to `f1`;
- `A2={8,9,10,11}` is attached to `f2`;
- `12..31` are unattached.

By (9), the two triangular 3-orbits may WLOG be `12,13`.

Let `P` be the 32x32 quotient submatrix between length-3 orbits. Its diagonal is 2 on `12,13` and zero elsewhere.

For an orbit `u`, let `f_u=1` if it is attached and zero otherwise. Let `d=P_uu` and let `n_r` count offdiagonal entries in row `u` equal to `r`, `r=1,2,3`. The row-degree and diagonal quotient equations imply

`d^2 + 2 n_2 + 6 n_3 + 2 f_u = 4`.                              (10)

Consequently:

- attached: `d=0`, `n_1=11`, `n_2=1`, `n_3=0`;
- triangular unattached: `d=2`, `n_1=12`, `n_2=n_3=0`;
- ordinary unattached: `d=0`, `n_1=10`, `n_2=2`, `n_3=0`.

Therefore no offdiagonal quotient entry equals 3. Write

`P = 2D_T + S + 2L`,                                             (11)

with disjoint simple graphs `S,L`.

Their degrees are

- attached: `deg_S=11`, `deg_L=1`;
- T (`12,13`): `deg_S=12`, `deg_L=0`;
- ordinary unattached: `deg_S=10`, `deg_L=2`.                    (12)

## 5. Equations involving the fixed vertices

For every attachment group `A_r` and every length-3 orbit `v`, the fixed-to-orbit quotient equation is

`sum_{u in A_r} P_uv = 1` if `v` is attached,

`sum_{u in A_r} P_uv = 2` if `v` is unattached.                   (13)

In particular each induced `P[A_r]` has weighted degree one, so it is a simple perfect matching. Relabelling independently within each four-set is legitimate; the CNF fixes these three matchings to canonical representatives.

For two length-3 orbits `i!=j`, the contribution through fixed vertices is 3 exactly when `i,j` lie in the same attachment group, and zero otherwise. Therefore

`(P^2+P)_ij = 3` for `i,j` in the same `A_r`,

`(P^2+P)_ij = 6` otherwise.                                      (14)

Equations (11)–(14), together with the degree equations, are exactly the nontrivial part of the 35-orbit quotient identity

`Q^2+Q = 12I + 2 1 s^T`,                                        (15)

where `s=(1,1,1,3,...,3)` is the orbit-size vector. The fixed-fixed equations are automatic from the disjoint four-orbit attachment sets.

## 6. CNF and proof standard

`src/reconciliation/o3_fixed_triangle_certify.py` encodes (11)–(14) exactly.

- S/L edges are Boolean and disjoint.
- Degree and attachment equations use an exact reduced-BDD weighted-equality encoding.
- Every two-step product is a Tseitin equivalence.
- The three internal attachment matchings are the only symmetry breaking; each is justified by independent relabelling inside its four-set.

A solver SAT result is accepted only if an independent reconstruction of the full 35x35 quotient verifies (15) entry by entry.

An UNSAT result is accepted only if:

1. CaDiCaL produces LRAT;
2. `lrat-check` returns zero;
3. Cake returns zero **and** prints `s VERIFIED UNSAT`.

If this CNF is certified UNSAT, equations (6) and the certificate imply:

**Every order-3 automorphism of a Conway `srg(99,14,1,2)` is fixed-point-free.**

This removes the project's dependence on the older computer orbit-matrix assertion of fixed-point-freeness.