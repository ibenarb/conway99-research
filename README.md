# Conway 99 Research

Reproduzierbare Forschungsdokumentation zum Conway-99-Problem.

## Stand vom 11. November 2026

**14 von 62 L62-Fällen sind vollständig geprüft und abgeschlossen; 48 bleiben offen. L62 und C2 bleiben offen.** Fall 1005 ist mit der gekoppelten Blocktausch-Optimierung und Präfixbündelung ausgeschlossen: vollständige Randüberdeckung, 9.072 frische unabhängige C2B1-Beweisprüfungen, vollständiges bytegeprüftes Archiv und unabhängiger Schlussreview bestanden. Der Rechen- und Archivlauf endete am 10. November um 00:19 Uhr Berlin; die formale Abschlussdokumentation folgte am 11. November. Gesamtdauer 4 Stunden 22 Minuten; daraus folgt kein kontrollierter Beschleunigungsfaktor gegenüber anderen Fällen. [Abschlussbericht und Nachweishashes](docs/c2/CASE1005_CLOSURE_2026-11-11.md). Keine weitere Fallkampagne wurde mit diesem Abschluss gestartet. Heartbeat bleibt aus.

## Historischer Zwischenstand vom 7. November 2026

Geprüfte gekoppelte Symmetrien und sparsamerer unabhängiger Replay erreichen in 16 gepaarten Teilaufgaben **Faktor 3,19** gegenüber den versiegelten Produktionsprogrammen, einschließlich Komprimierungsprüfung. [Begründung, Messdaten, Kontrolltests und offene Integrationsgates](docs/c2/SYMMETRY_SPEEDUP_2026-11-07.md). **12 von 62 L62-Fällen sind abgeschlossen; 50 bleiben offen.** [Fall 77 ist vollständig geprüft und archiviert](docs/c2/CASE77_CLOSURE_2026-11-07.md). Fall 78 läuft erstmals mit dem geprüften S2-Verfahren. Zusätzliche Präfixbündelung erreicht im begrenzten Forschungspiloten Faktor 3,99, ist aber noch nicht produktiv. Keine Vollfall-Laufzeitgarantie; L62 und C2 bleiben offen. Heartbeat abgeschaltet.

Der [Überdeckungsbefund vom 6. November](docs/c2/BOUNDARY_COVERAGE_AUDIT_2026-11-06.md) betrifft die geprüfte externe Prefixauswahl; er ist kein SAT-Zeuge.

## Reviewupdate vom 3. November 2026

Mizopl bestätigt die von uns identifizierte Überdeckungslücke. Die neue globale Reduktion ist bedingt nutzbar; ihr Lean-Satz behauptet weniger als die Mail. [Antwort, unabhängige Gegenprüfung und Konsequenzen für C2](docs/c2/MIZOPL_REPLY_REVIEW_2026-11-03.md), mit kleinem Prüfer und ergänztem Modellvertrag. Kein neuer T20-Ausschluss und kein vollständiger C2-Abschluss.

## Forschungsstand vom 1. November 2026

**C2 und das Conway99-Problem bleiben offen.** Unser aktueller Schwerpunkt ist die Involutionsanalyse mit vollständigen 99-Knoten-Modellen und unabhängig geprüften Ausschlusszertifikaten.

- **T16 und T18:** unter den dokumentierten Voraussetzungen computerunterstützt abgeschlossen.
- **T20:** Typ `1/0` zertifiziert ausgeschlossen; acht Typen noch offen. Momentaufnahme vom 01.11.2026, keine Live-Anzeige.
- [C2-Status, genaue Reichweite und Belegverfügbarkeit (English)](docs/c2/STATUS_2026-11-01.md).
- [Öffentlicher Modellvertrag (English)](docs/c2/MODEL_CONTRACT.md).
- [Unabhängiger Slice-Abgleich und offene Überdeckungsfrage (English)](docs/c2/SLICE_REVIEW_2026-11-01.md).

Die kleinen Abschlussbelege und zwei nachrechenbare Slice-Prüfer sind öffentlich beigefügt. Diese Aktualisierung ist keine vollständige Veröffentlichung aller großen C2-Beweisdateien. Der historische O3-Stand und die damaligen Reviewaufträge folgen unten.

## Kanonischer Stand

Der Branch `main` ist der kanonische Forschungsstand. Historische Meilenstein-Tags bleiben unverändert.

Wichtige Meilensteine:

- `o3-task03-fullcert-1.1` — vollständig zertifizierter Ausschluss des FPF-Ordnung-3-Quotiententyps `(6,3^7)` bei `tau=6`.
- `o3-breadth1-ab-matched-20260905` — historischer matched-seed A/B-Breadth-Scout über 139 C4-freie Ordnung-3-Typen.

## Historischer O3-Stand vom 6. September 2026

1. `docs/breadth1/O3_LAYER_A_MODEL_SPEC.md` beschreibt jetzt explizit die vollständige Semantik des Grundmodells A. A ist ein 33-Knoten-Quotientenmodell, kein 99-Knoten-Liftmodell.
2. Der historische FULLCERT-`qsat`-Quellbaum ist content-exakt unter `vendor/O3_TASK03_FULLCERT_1.1_20260902/qsat/` eingecheckt; Hashprovenienz steht in `PROVENANCE.json`.
3. `docs/breadth1/O3_tau_mod3_theorem.md` beweist im fixpunktfreien Ordnung-3-Fall `tau ≡ 0 (mod 3)`, also zusammen mit der Spurrestriktion `tau in {6,27}`.
4. Nach diesem Stand sind von den historischen 139 C4-freien Typen nur 105 mathematisch live; nach zwei bereits ausgeschlossenen tau=6-Typen bleiben **103 offene O3-Typen**. Maschinenlesbare Zusammenfassung: `results/breadth1/O3_post_tau_coverage_20260906.json`.
5. Layer B ist als **redundante Propagationsschicht** zu interpretieren, nicht als mathematisch stärkeres Modell als A. Der A/B-Scout bleibt als historisches Performanceexperiment erhalten; seine frühere strategische Folgerung wurde entsprechend korrigiert.

## Historischer Strategie-Review vom September — Version 2

Der damalige gemeinsame Auftrag an ChatGPT, Claude und GPT Astra steht in:

`docs/reviews/STRATEGY_REVIEW_PROMPT_2026-09-06_v2.md`

Bitte **Version 2** zuerst lesen und anschließend die dort angegebene Pflichtlektüre im Repository prüfen. Die erste Analyse soll unabhängig erfolgen; frühere Entwürfe oder Antworten anderer Modelle sind nicht als Evidenz zu behandeln. Die Berichte werden erst danach synthetisiert.

Die frühere Datei `STRATEGY_REVIEW_PROMPT_2026-09-06.md` bleibt ausschließlich als historische Version 1 erhalten.
