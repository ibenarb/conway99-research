# O3-BREADTH-1 matched-seed A/B scout — final report

Date: 2026-09-05
Status: **COMPLETE / SCOUT ONLY**
Certification: **no new certified exclusion**

## Provenance

- Raw campaign: `/home/rb/conway99_workspace/o3_breadth1_runs/ab_matched_main_20260904`
- Immutable freeze: `/home/rb/conway99_workspace/conway99_freezes/O3_BREADTH1_AB_MATCHED_20260905`
- Git branch before final report: `o3-breadth1-scout`
- Git HEAD before final report: `77d07ec8e883cf32e1cb8c034e416c571bdb9ed8`
- Runner SHA256: `451ac951efa307cefc2fd258dba9a119cfe78edc352d4e16675531ba3342e29e`
- SMT panel SHA256: `c7ea3d618c056120dfeea303017e261485952887729c7057f1c989e9c2650839`
- Workers: **20**
- Timeout: **5760 s**
- Layers: **A, B**
- A/B seed scope: **matched per type**
- A/B execution: **same logical CPU, A then B**

## Final audit

- Types complete: **139/139**
- Instances complete: **278/278**
- A/B seed matches: **139/139**
- A/B CPU matches: **139/139**
- `TIMEOUT`: **275**
- `UNSAT_UNCERTIFIED`: **3**
- Audit errors: **0**

Layer totals:

- A: **138 TIMEOUT + 1 UNSAT_UNCERTIFIED**
- B: **137 TIMEOUT + 2 UNSAT_UNCERTIFIED**

## Main scientific result

The only `UNSAT_UNCERTIFIED` outcomes belong to the two pre-existing control/excluded types:

- `(3^9)`
- `(6,3^7)`

For the **137 remaining open O3 types**:

- A: **137/137 TIMEOUT**
- B: **137/137 TIMEOUT**
- new UNSAT candidates: **0**

`UNSAT_UNCERTIFIED` is a scout-level CaDiCaL outcome, not an LRAT/Cake-certified mathematical exclusion.

## Control `(3^9)`

A and B are byte-identical because B adds no generic `C_m` constraint here.

- CNF SHA256 A/B: `fc43530b5673eff07a2335fdfaac3a75bc813cbbc1442dc79381cf4b8ef83a08`
- matched seed: `1844336176`
- matched CPU: `15`
- A solve wall: **2431.996 s**
- B solve wall: **2442.533 s**
- conflicts A/B: **4578525 / 4578525**
- decisions A/B: **9939866 / 9939866**
- propagations A/B: **5264704731 / 5264704731**

The logical solver statistics are exactly identical, validating the matched-seed control.

## Control `(6,3^7)`

This type was already fully certified in the earlier FULLCERT milestone (656/656 terminal A obligations certified). The present result is only a performance/control observation.

- matched seed: **1100167974**
- matched CPU: **3**
- A: **TIMEOUT**, solve wall **5880.227 s**
- B: **UNSAT_UNCERTIFIED**, solve wall **1612.709 s**
- conflicts A/B: **8872079 / 3835253**
- decisions A/B: **22516987 / 9386658**
- propagations A/B: **10674670114 / 3173723633**
- B added clauses: **1313**
- B added variables: **424**
- B cycle-local constraints: **15**

B therefore has a real algorithmic effect on this known control, but that effect produced no new solved type among the 137 open cases.

## Aggregate solver work

A:

- conflicts: **1079401216**
- decisions: **5276300137**
- propagations: **1534084055787**
- summed solve wall: **226:05:31**

B:

- conflicts: **1049124949**
- decisions: **5176922248**
- propagations: **1523462328110**
- summed solve wall: **224:54:41**

## Interpretation

The generic `C_m` B-layer is valid and demonstrably helpful on the known `(6,3^7)` control, but under this matched-seed monolithic budget it did **not** convert any of the 137 open O3 types from TIMEOUT to UNSAT.

The next research phase should therefore prioritize **structured decomposition / cubing**, using Task03 as the successful model, rather than simply extending the same monolithic A/B timeout.

## Integrity

- Freeze files hashed: **424**
- `SHA256SUMS.txt` SHA256: `bbf3dcacca7602a9cf01cf98bf1dca682d88b0bff778b702fea662751bcf2eba`

Raw campaign artifacts remain outside Git in the project freeze. Git receives this report, the machine-readable summary, the per-type table, and the exact source used for the campaign.
