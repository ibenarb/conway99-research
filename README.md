# Conway 99 Research

Reproduzierbare Forschungsdokumentation zum Conway-99-Problem.

## Kanonischer Stand

Der Branch `main` ist der kanonische Forschungsstand. Historische Meilenstein-Tags bleiben unverändert.

Wichtige Meilensteine:

- `o3-task03-fullcert-1.1` — vollständig zertifizierter Ausschluss des FPF-Ordnung-3-Quotiententyps `(6,3^7)` bei `tau=6`.
- `o3-breadth1-ab-matched-20260905` — historischer matched-seed A/B-Breadth-Scout über 139 C4-freie Ordnung-3-Typen.

## Korrekturen vom 6. September 2026

1. `docs/breadth1/O3_LAYER_A_MODEL_SPEC.md` beschreibt jetzt explizit die vollständige Semantik des Grundmodells A. A ist ein 33-Knoten-Quotientenmodell, kein 99-Knoten-Liftmodell.
2. Der historische FULLCERT-`qsat`-Quellbaum ist content-exakt unter `vendor/O3_TASK03_FULLCERT_1.1_20260902/qsat/` eingecheckt; Hashprovenienz steht in `PROVENANCE.json`.
3. `docs/breadth1/O3_tau_mod3_theorem.md` beweist im fixpunktfreien Ordnung-3-Fall `tau ≡ 0 (mod 3)`, also zusammen mit der Spurrestriktion `tau in {6,27}`.
4. Damit sind von den historischen 139 C4-freien Typen nur 105 mathematisch live; nach zwei bereits ausgeschlossenen tau=6-Typen bleiben **103 offene O3-Typen**. Maschinenlesbare Zusammenfassung: `results/breadth1/O3_post_tau_coverage_20260906.json`.
5. Layer B ist als **redundante Propagationsschicht** zu interpretieren, nicht als mathematisch stärkeres Modell als A. Der A/B-Scout bleibt als historisches Performanceexperiment erhalten; seine frühere strategische Folgerung wurde entsprechend korrigiert.

## Externer Strategie-Review — Version 2

Der aktuelle gemeinsame Auftrag an ChatGPT, Claude und GPT Astra steht in:

`docs/reviews/STRATEGY_REVIEW_PROMPT_2026-09-06_v2.md`

Bitte **Version 2** zuerst lesen und anschließend die dort angegebene Pflichtlektüre im Repository prüfen. Die erste Analyse soll unabhängig erfolgen; frühere Entwürfe oder Antworten anderer Modelle sind nicht als Evidenz zu behandeln. Die Berichte werden erst danach synthetisiert.

Die frühere Datei `STRATEGY_REVIEW_PROMPT_2026-09-06.md` bleibt ausschließlich als historische Version 1 erhalten.
