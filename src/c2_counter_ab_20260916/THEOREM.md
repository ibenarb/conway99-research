# Equivalence of the E3 totalizer variant

The reference is c2_reference.py, SHA256
3a88f356831a4f955c79639bfe86aac5eea2a80febdd676cbd1009e86f1e9b29.
The primary numbering, fixed graph frame, AND gates and E1/E2 equations are unchanged.
Only the exact-sum implementation for E3 is replaced. This is an encoding experiment,
not a new mathematical exclusion or a claim of literature novelty.

## Normalization

A sum of positive Boolean variables and Boolean constants is normalized by removing
false constants, subtracting true constants from the target and collecting duplicate
variables as positive integer weights. Dividing all weights and the target by their
gcd preserves solutions; a nondivisible target is impossible. A negative target or a
target exceeding the sum of weights is impossible. Target zero forces every term false.
A weight above a positive target forces its variable false. If the remaining total
weight is below the target, the equation is impossible.

E3 has target 2 minus the number of common fixed-frame neighbors, hence at most 2.
Repeated conjunctions can produce weights; they are not treated as independent bits.
After normalization each surviving weighted leaf is the same variable repeated w times.
Its j-th output thus means that its contribution is at least j, for 1 <= j <= w.

## Merge induction

For child threshold vectors A,B, define A_0=B_0=true and thresholds above a child's
available vector=false. Retain at most K=target+1 outputs at each node.
For each available pair i,j impose:

- not A_i OR not B_j OR R_(i+j), when 1 <= i+j <= length(R);
- A_(i+1) OR B_(j+1) OR not R_(i+j+1), when i+j+1 <= length(R).

Induction: these clauses are equivalent to R_t iff the sum of the contributions of
the two children is at least t, for every retained t. If the sum is at least t, choose
thresholds i,j with i+j=t that both hold; the forward clause forces R_t. If the sum is
less than t, choose i,j with i+j=t-1, each at least its child's actual count, within the
available lengths; the backward clause forces not R_t. Such choices exist because
R_t is only allocated up to the sum of available lengths. Truncation at K is harmless:
when a child count is >=K, every query t<=K is already satisfied by that child; when
the parent count is <t<=K, neither child count has been truncated.

Assigning each auxiliary its actual threshold truth value satisfies all merge clauses.
Conversely the clauses force those values by induction. Correlation between children
or repeated primary variables does not change the pointwise count argument.
Forcing R_target and, if allocated, not R_(target+1) is therefore equivalent to exact
sum=target, under existential projection of auxiliary variables.

The reference encoder and variant accordingly have exactly the same primary models.
The eleven matching assumptions are appended unchanged to both formulations. The
previous matching-cover theorem transfers without a new symmetry reduction.

## Controls and limitations

34,208 exhaustive sum-assignment controls, including weights, constants, gcd rejection,
impossible targets and balanced trees up to eight independent leaves. Both encodings
are also compared with direct reconstruction and SRG verification for all four primary
assignments in the nine-vertex frame (eight encoding/assignment checks).
Independent DPLL supplies the projection oracle. These finite controls supplement,
and do not replace, the induction argument. Actual solver integration is checked on
the target host before the large comparison starts. No production UNSAT proof exists.
