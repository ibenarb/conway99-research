# O3 theorem: tau is divisible by 3

**Status:** PROJECT THEOREM  
**Date:** 6 September 2026  
**External input:** a hypothetical order-3 automorphism of a Conway-99 graph is fixed-point-free.  
**Internal conclusion:** `tau in {6,27}`.

## Statement

Let `G = srg(99,14,1,2)` and let `g` be a fixed-point-free automorphism of order 3. Let `tau` denote the number of vertex-orbits of `g` whose three vertices induce a triangle; equivalently, in the quotient notation these are the indices `i` with `q_ii = 2`.

Then

`tau ≡ 0 (mod 3)`.

Combined with the previously derived trace restriction

`tau in {6,13,20,27}`,

this gives

`tau in {6,27}`.

## Proof

Every edge of an `srg(99,14,1,2)` lies in exactly one triangle because `lambda=1`. The number of edges is

`99*14/2 = 693`,

so the number of graph triangles is

`693/3 = 231`.

The automorphism `g` acts on the set of these 231 triangles. Every orbit of triangles has length 1 or 3.

A triangle fixed setwise by `g` cannot contain a fixed vertex, because `g` is fixed-point-free. Hence `g` acts on its three vertices as a 3-cycle. Therefore its three vertices form exactly one vertex-orbit of `g`.

Conversely, a vertex-orbit of size 3 contributes a setwise fixed graph triangle exactly when its three vertices are mutually adjacent. In the quotient notation this is precisely the condition `q_ii=2`, so the number of fixed triangles is exactly `tau`.

Thus for some integer `k >= 0`,

`231 = tau + 3k`.

Therefore

`tau ≡ 231 ≡ 0 (mod 3)`.

Intersecting this with `{6,13,20,27}` leaves exactly `{6,27}`. QED.

## Search-space consequence

The historical C4-free classification contained 139 quotient cycle types:

- tau=6: 103,
- tau=13: 28,
- tau=20: 6,
- tau=27: 2.

The theorem removes all 28 tau=13 types and all 6 tau=20 types before SAT. Hence only

`103 + 2 = 105`

C4-free types remain mathematically possible in the fixed-point-free order-3 branch.

The project already has two previously excluded tau=6 control/types, `(3^9)` and `(6,3^7)`. Therefore the current working count for future O3 campaigns is

`105 - 2 = 103 open types`,

namely 101 at tau=6 and 2 at tau=27.

Historical 139-type scout artifacts are not rewritten; they remain valid records of the experiment that was run before this theorem was noticed.

## Audit note

Before external publication, the fixed-point-free input should again be checked directly against its cited primary literature. The proof above is otherwise elementary and independent of the SAT encoding.
