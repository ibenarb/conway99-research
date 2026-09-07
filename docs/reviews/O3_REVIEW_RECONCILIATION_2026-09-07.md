# Conway 99 — reconciled O3 review baseline

**Date:** 2026-09-07  
**Base commit:** `15f6ce2550423ecfaf75847cfba824deecd563f3`  
**Working branch:** `o3-review-reconciled-20260907`

This document freezes the factual state after reconciling the independent Claude and Astra reviews and after the local provenance audit on RB-CUBE. It is intentionally a project-owned ledger: reviewer statements are not used as proof premises. New mathematical claims are promoted only through the project documents and checks referenced below.

## 1. Closed historical provenance questions

### 1.1 Task03 `(6,3^7)`

The historical FULLCERT chain is locally complete.

- 656/656 canonical terminal obligations are present.
- 656/656 have `lrat-check` exit code 0.
- 656/656 have `cake_lpr` exit code 0.
- 656/656 stored Cake outputs contain the documented positive verdict `s VERIFIED UNSAT`.
- The previously identified implementation weakness in the salvage controller is real: it checked Cake's exit code but not the positive verdict marker. The local audit shows that this weakness did **not** affect any of the 656 stored successful checks.
- Existing source-CNF, terminal-CNF and coverage hashes remain unchanged.

Project status: **MACHINE-CERTIFIED, provenance PASS**.

### 1.2 Historical control type `(3^9)`

The old preflight certificate was recovered at

`~/conway99_workspace/o3_qsat_runs/preflight_0.1.11_20260826/tasks/00-3-3-3-3-3-3-3-3-3/`.

Its manifest records

- `type = [3,3,3,3,3,3,3,3,3]`,
- `state = UNSAT_CERTIFIED`,
- CaDiCaL exit code 20,
- `lrat-check` exit code 0,
- `cake_lpr` exit code 0,
- positive Cake output `s VERIFIED UNSAT`.

The currently stored files match the historical manifest bit-for-bit:

- CNF SHA256: `a20ea115b44512cbeee014fa637e004e2c24ba4481e15e532594cf3ae1df092b`
- LRAT SHA256: `9219dbfa02ec96fda71a96d48b4f6fa43b79069379732dd34c46e4b2849a8fa8`

Project status: **MACHINE-CERTIFIED, provenance PASS**.

The earlier automated audit result `TYPE_3X9=NOT_FOUND` was a classification bug in that temporary audit script: it failed to recognize the historical manifest layout. It is not a scientific result.

## 2. Reconciled mathematical facts

### 2.1 Layer A / Layer B

Layer A is the exact 33-orbit quotient-feasibility model described in `docs/breadth1/O3_LAYER_A_MODEL_SPEC.md`. Layer B is mathematically redundant relative to A: its extra cycle inequalities follow from A by omitting nonnegative terms. A/B differences are therefore solver-encoding/propagation effects, not stronger mathematics.

### 2.2 Triangle-orbit congruence

The project theorem in `docs/breadth1/O3_tau_mod3_theorem.md` remains valid:

`tau ≡ 0 (mod 3)`.

Together with the quotient-spectrum restriction `tau in {6,13,20,27}`, this gives `tau in {6,27}` in the fixed-point-free order-3 branch.

### 2.3 Involution fixed points

The apparent review disagreement `1` versus `{1,15}` fixed points is resolved. The weaker arithmetic conditions that permit 15 do not override the stronger prime-order fixed-set theorem. For an involution the fixed set has exactly one vertex. The project must nevertheless keep later WLOG assumptions about the seven 2-orbit pairs separate from this fixed-point count.

### 2.4 T-skeleton counts

The numbers 69 and 26 refer to different filter depths and are not contradictory. For `tau=6`, with `B=S_TT` and

`M = 6J + 6I - 5B - B^2 = C C^T`,

the intended hierarchy is

`156 unlabeled six-vertex graphs -> 69 entrywise-nonnegative M -> 44 exact-PSD M -> exact binary Gram feasibility`.

The final binary-Gram stage is being reimplemented as a project-owned CNF classification with LRAT/Cake certificates for all UNSAT cases; until that run is complete, the historical number 26 is a reproducible target, not yet the canonical certified count.

### 2.5 C6 local-pattern counts

The counts 66, 54 and 34 are successive necessary-filter levels, not conflicting enumerations. The canonical documentation will state the precise assumptions used at each level.

## 3. Internalization work started by this reconciliation

Three project-owned tasks are now implemented on this branch.

1. **Analytic `tau=27` lift exclusion.**  
   `docs/breadth1/O3_tau27_lift_exclusion.md` gives a self-contained project proof; `src/reconciliation/o3_tau27_lift_check.py` is a finite exact regression.

2. **Certified T-skeleton classification.**  
   `src/reconciliation/o3_t_skeleton_certify.py` independently enumerates all 156 unlabeled six-vertex graphs, checks the 69 and 44 stages with exact integer arithmetic, then converts the remaining binary Gram problem to CNF. SAT cases require an independently checked 27-column witness; UNSAT cases require LRAT and the explicit positive Cake verdict.

3. **Removal of the external FPF computer dependency.**  
   `docs/breadth1/O3_fixed_triangle_internal_model.md` derives, from the SRG equations themselves, that a nontrivial order-3 automorphism has either no fixed vertices or a fixed `K3`. In the `K3` case it derives `tau=2` and a canonical exact 35-orbit quotient model. `src/reconciliation/o3_fixed_triangle_certify.py` encodes that quotient model and, if UNSAT is certified, removes the need to import Behbahani's computer-based fixed-point-free conclusion.

## 4. Current claim ledger before the new local suite

| Claim | Status at start of reconciliation suite |
|---|---|
| `(3^9)` excluded | MACHINE-CERTIFIED, provenance PASS |
| `(6,3^7)` excluded | MACHINE-CERTIFIED, provenance PASS |
| `tau ≡ 0 mod 3` in FPF O3 | PROJECT THEOREM |
| `tau=27` impossible for an actual FPF O3 SRG lift | PROJECT PROOF PREPARED; exact regression pending local run |
| `156 -> 69 -> 44` T-skeleton filters | PROJECT EXACT CODE PREPARED; local run pending |
| final T-skeleton binary-Gram count | CERTIFICATION PENDING |
| non-FPF O3 fixed `K3` quotient impossible | CERTIFICATION PENDING |
| order-3 automorphism is FPF without Behbahani computer input | PENDING fixed-`K3` certificate |

No new long-run result is claimed by this document.

## 5. Completion criterion for milestone `O3_REVIEW_RECONCILED_20260907`

The milestone may be frozen only after:

- the exact `tau=27` regression passes;
- all 44 T-skeleton CNFs are classified, every SAT case has a checked witness and every UNSAT case has LRAT + positive Cake verification;
- the fixed-`K3` quotient CNF is either certified UNSAT or, if SAT, its quotient witness is independently validated and the claim ledger is revised;
- small result JSONs, source hashes and tool hashes are archived in Git;
- individualized response manifests for Claude and Astra are generated from the final project-owned ledger.

Historical tags and proof archives are not modified.