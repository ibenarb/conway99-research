# Conway99: Reviewindex

Reviews werden im eigenen Zweig mit unverändertem Original und getrenntem Projektabgleich archiviert.

| Eingang | Zweig | Fester Archivstand | Inhalt |
| --- | --- | --- | --- |
| 2026-09-13, externes nicht-evolutionäres Review | `reviews/20260913-externes-review` | [`fbba251f1acbe49177a44ae47f77f66ab1b1de25`](https://github.com/ibenarb/conway99-research/tree/fbba251f1acbe49177a44ae47f77f66ab1b1de25/docs/reviews/20260913_extern) | Original, Eingangsidentität, Abgleich, Involutionsmodell und kleine eigene Prüfungen |

Historische Reviews vor dieser Regel verbleiben an ihren bisherigen Referenzen. Dieser Index ist kein Verzeichnis automatisch akzeptierter Sätze. Der aktuelle Abgleich befürwortet die kanonische Involution als nächste Modellaufgabe und präzisiert die unabhängige Reviewabdeckung.

## Memetische KI-Kandidaten

| Eingang | Zweig | Fester Archivstand | Befund |
| --- | --- | --- | --- |
| 2026-09-14, Mistral/Vibe v01 | `reviews/20260914-mistral-candidates-v01` | [dc0836414dbeefc6da4460f21dcd1ab4aa5e9eb7](https://github.com/ibenarb/conway99-research/tree/dc0836414dbeefc6da4460f21dcd1ab4aa5e9eb7/data/memetik/ai_candidates/submissions/20260914_mistral_v01) | Sechs eingereichte Datensätze; null akzeptiert; Original, Prüfdaten und eigener Bericht |

Laufender [Kandidatenkatalog](../../data/memetik/ai_candidates/INDEX.md).

Mistral/Vibe v02, 2026-09-14: [festes Archiv 9bbbbfe](https://github.com/ibenarb/conway99-research/tree/9bbbbfece7511c96cdc9103c42318b89c3a64f08/data/memetik/ai_candidates/submissions/20260914_mistral_v02/), Zweig `reviews/20260914-mistral-candidates-v02`. Drei Beschreibungen, kein Code/Graph, null Aufnahme. Ω-Regel unabhängig widerlegt; siehe Prüfbericht.

Korrektur Mistral v02: Code ging beim Kopieren verloren, nicht bei Mistrals Ausgabe. [Code-Nachtrag und Ausführung, d58dbcc](https://github.com/ibenarb/conway99-research/tree/d58dbccb3dce418f57bfb05325cc8cfaec782e65/data/memetik/ai_candidates/submissions/20260914_mistral_v02/code_supplement/); eigener Archivzweig `reviews/20260914-mistral-v02-code-supplement`. Drei Assertion-Abbrüche; Metrikfunktion bestätigt.

Mistral v03: [Archiv 8e8769a](https://github.com/ibenarb/conway99-research/tree/8e8769a39b9b66b12247378a9d7ed5280ec2e95c/data/memetik/ai_candidates/submissions/20260914_mistral_v03/), Zweig `reviews/20260914-mistral-candidates-v03`. Zwei Generatoren ausgeführt, null Kandidaten. Eigener begrenzter Ausschluss zirkulärer λ-Gründer dokumentiert, keine Literatur-Neuheit behauptet.

Mistral v04: [Archiv cb3687e](https://github.com/ibenarb/conway99-research/tree/cb3687eb3a1e544717f633e11533e6454d9d574f/data/memetik/ai_candidates/submissions/20260914_mistral_v04/), Zweig `reviews/20260914-mistral-candidates-v04`. Vollständiger Eingang; nicht fortschreitende Backtracking-Implementierung nachgewiesen, null Kandidaten.

Gemini v01: [Archiv 007fa99](https://github.com/ibenarb/conway99-research/tree/007fa996be815756e83aa129807e1603dab06d2d/data/memetik/ai_candidates/submissions/20260914_gemini_v01/), Zweig `reviews/20260914-gemini-candidates-v01`. Generator lokal ausgeführt; ein Ω-Graph unabhängig validiert und aufgenommen. Keine Neuheitsbehauptung.

Claude v01: [Archiv bfb4f62](https://github.com/ibenarb/conway99-research/tree/bfb4f623ad66a8e52373c6ba972b5c5f9e60adb6/data/memetik/ai_candidates/submissions/20260915_claude_v01/), Zweig `reviews/20260915-claude-candidates-v01`. Drei gültige paarweise nichtisomorphe Graphen; Cayley-Ausschluss unabhängig bestätigt. Aussagen zu Starrheit bleiben unbestätigt.

Codex v01: [Archiv c10038a](https://github.com/ibenarb/conway99-research/tree/c10038a3baa23145b666d5e5251e81c139877f83/data/memetik/ai_candidates/submissions/20260915_codex_v01/), Zweig `reviews/20260915-codex-candidates-v01`. Zehn zulässige Kandidaten, zehn byteidentische Wiedererzeugungen, Nichtisomorphie innerhalb der Einreichung und zu 18 Referenzen bestätigt. C02 verbessert die dokumentierten Office-Ω-Bestwerte W/L1/F; strukturelle Grenzen der λ-Lifts und offene Plateaufragen im Prüfbericht.

Grok v01 (Modus schnell laut Nutzer): [Archiv 0cc61d3](https://github.com/ibenarb/conway99-research/tree/0cc61d3c87f7b6ea09418023398570d5403a3290/data/memetik/ai_candidates/submissions/20260915_grok_v01), Zweig `reviews/20260915-grok-candidates-v01`. Null Kandidaten; unvollständiger Code, nachgewiesene Laufzeitfehler und mathematische Konstruktionsfehler. Keine Aufnahme.

Qwen v01, Eingang 2026-09-15 (Berichtsdatum laut Antwort 2026-09-16): [Archiv cbf364b](https://github.com/ibenarb/conway99-research/tree/cbf364b2ff9c0e92a1477581e33a6affffe261de/data/memetik/ai_candidates/submissions/20260915_qwen_v01), Zweig `reviews/20260915-qwen-candidates-v01`. Drei Datensätze, passende SHA256, null zulässig. Nichtstandard-graph6, Regularitätsfehler und falscher PASS des mitgelieferten Prüfers unabhängig dokumentiert.

## λ-Suchstrategie, 21. September 2026

Reviewerbericht: [byteidentisches Original und Eingangsmetadaten](https://github.com/ibenarb/conway99-research/tree/52ad622dfa5d04ba0a0d26dd39e4aa7fc6927ce7/docs/reviews/20260921_lambda), Zweig `reviews/20260921-lambda`. [Eigener Abgleich](../memetik/lambda_review_20260921/ABGLEICH.md) mit unabhängig geprüften Rekordgraphen, reproduzierten Pivot-Abstiegen und Abgrenzung nicht reproduzierter BFS-/Tabu-Aussagen. Der frühere 18-CPU-h-Vorschlag soll nicht unverändert gestartet werden.


## λ-Fortsetzung, 22. September 2026

Unabhängiger Reviewerbericht und ursprünglicher Prüfsatz: [festes Originalarchiv 07a8290](https://github.com/ibenarb/conway99-research/tree/07a82903e029b58d31f496a96e3464dc0798678c/docs/reviews/20260922_lambda), Zweig `reviews/20260922-lambda-next`. [Eigener Abgleich und konkreter Laufvorschlag](../memetik/lambda_synthesis_20260922/ABGLEICH_UND_LAUFVORSCHLAG.md): Reviewer-Zeuge W=2116 unabhängig bestätigt, eigener Pivot verbessert auf W=2114; Tiefe-2-Prüfungen reproduziert. Vorschlag 121 neue CPU-h, 39 Suchjobs, noch nicht gestartet. Technische und statistische Einschränkungen des Reviewerentwurfs sind ausdrücklich dokumentiert.

## λ-Folgelauf, 23.–24. September 2026

[Byteidentisches Revieweroriginal und Prüfsatz](https://github.com/ibenarb/conway99-research/tree/c7215b3d16c99169381cac3175506bd6480748d2/docs/reviews/20260923_lambda_followup), Zweig `reviews/20260923-lambda-followup`. [Eigener Abgleich und Entscheidung](../memetik/lambda_prechecks_20260924/ABGLEICH_UND_ENTSCHEIDUNG.md): Scores und Durchsatz reproduziert; Aussagen über Stillstand, vier Startgraphen, ein einziges Becken und V3-Herkunft korrigiert. Freigegebene Umsetzung: V1/V3, 24 Jobs, 34 CPU-h, kein V2 und kein Hauptlauf. [Startpaket und Dokumentation](../../experiments/memetik/lambda_prechecks_1_0_0/README.md).

## λ-Hauptlaufkritik und begrenzte Entscheidungsetappe, 24. September 2026

[Als Chattext übermittelter Review und Eingangsmetadaten](https://github.com/ibenarb/conway99-research/tree/6089dfe68fc254931c011a82931c0adb914fa879/docs/reviews/20260924_lambda_mainrun), Zweig `reviews/20260924-lambda-mainrun`. [Eigener Abgleich](../memetik/lambda_decision_20260924/ENTSCHEIDUNG.md): großer Hauptlauf zurückgezogen, Histogramme nachgerechnet, Überdehnungen begrenzt. Autorisiert: V2 (12 CPU-h) plus unveränderte V3-Fortsetzung (48 zusätzliche CPU-h), feste Kriterien, kein automatischer Folgelauf. [Geprüftes Startpaket](../../experiments/memetik/lambda_decision_1_0_0/README.md).

## λ-Frontier und Übernachtlauf, 26. September 2026

[Byteidentisches Review und Prüfsatz](https://github.com/ibenarb/conway99-research/tree/7a00a6a93227eb7eb09980355b4d3129975489fc/docs/reviews/20260926_lambda), Zweig `reviews/20260926-lambda`. [Eigener Abgleich und Fortsetzungsvorschlag](../memetik/lambda_review_20260926/ABGLEICH_UND_VORSCHLAG.md): 1465 Graphen samt Klassen nachgerechnet; Tiefe-2-Minima und zwei kürzeste Vier-Zug-Abstände reproduziert. Tiefe 3 bleibt in dieser Runde Reviewerbefund. Kausale Bankaussage, Herkunft, späte Klassen und endgültige Schließung präzisiert. Empfehlung: P-Kampagne pausieren, begrenzte Tiefe-4-Diagnose mit vorangehender Tiefe-3-Reproduktion; noch nicht implementiert oder gestartet.

## λ-Radiusprüfung, 27. September 2026

[Byteidentischer Prüfsatz und Eingang](https://github.com/ibenarb/conway99-research/tree/6d5004ce0669930ea858f04f0d4c64a01c1a6f7c/docs/reviews/20260927_lambda_radius), Zweig `reviews/20260927-lambda-radius`. Enthält Reproduktionen, aber keinen separaten strategischen Reviewtext. [Eigener Abgleich und konkreter Vorschlag](../memetik/lambda_review_20260927/ABGLEICH_UND_VORSCHLAG.md): Root-2-Switch-Vollständigkeit, cycle3-Census und Rückkehrquoten nachgerechnet; externe Tiefe-3-Nachzählung eingeordnet. Vorschlag: kontrollierter Episodenvergleich der Längenverteilungen an zwei festen Starts, 12 Such-CPU-h plus höchstens 1 CPU-h Kontrollen; noch nicht implementiert oder gestartet.

Nachtrag zum 27.09.: [Vollständige Bildschirmausgabe, unverändert archiviert](https://github.com/ibenarb/conway99-research/tree/06cdb5f4175aced5c30f6f9fe8245873211ebc09/docs/reviews/20260927_lambda_radius). [Abgleich und revidierter Plan](../memetik/lambda_review_20260927/ABGLEICH_VOLLREVIEW_UND_PLAN_V2.md): einzelne Perturbationsweglängen statt Längenmischungen; falsche Rückkehrkontrolle entfernt, positiver Mittelpunktabstieg nachgerechnet, P-Tie-Break beibehalten. Höchstens22 CPU-h inklusive Hilfsbudget; nur geplant.

## λ-Profil und strategischer Abstand, 27. September 2026

[Byteidentischer Reviewertext und Eingangsmetadaten](https://github.com/ibenarb/conway99-research/tree/79caad6434d3bdcca39d3ff7a17d653cdd55bf70/docs/reviews/20260927_lambda_profile), Zweig `reviews/20260927-lambda-profile`. Das im Text erwähnte ZIP wurde nicht mitgeliefert. [Eigener Abgleich und nächste Empfehlung](../memetik/lambda_profile_20260927/endpoints/ABGLEICH_UND_NEUAUSRICHTUNG.md): 885 nicht zurückgekehrte Graphen mit eigenem Standardbibliothek-Scorer reproduziert, Endpunkttabelle bestätigt; Vorabregel, Stichprobenlücke, Landschaftszensus und Neustartvergleich präzisiert. Unveränderte P-Linie pausieren; strukturellen Vergleich als alleinigen nächsten Hauptschritt zurückgenommen. Vorschlag: höchstens3 CPU-h für exakte gemeinsame Fensterreparatur, noch nicht implementiert oder gestartet.

## ROOT8105, 4. Oktober 2026

[Unverändertes Reviewer-Prüfpaket und Eingang](https://github.com/ibenarb/conway99-research/tree/efcf4a1f068d86f4216ccbfdf501bd8955972c80/docs/reviews/20261004_root8105), Zweig `reviews/20261004-root8105-claude`. Der separate strategische Antworttext fehlt. [Eigener Abgleich und revidierter Plan](../augmentation/root8105_review_response_20261004/ABGLEICH_UND_PLAN_V2.md): Rootzensus,332 erste Breiten, zwei eigene Vertex-DP-Zählungen, zusätzliche tiefe SAT/DP-Fälle und BvLS-Kontrollen nachgerechnet. Empfehlung: vollständiger Zählzensus aller8105 Roots vor materialisierter Frontier, danach wohldefinierte Stichproben; Wiederaufnahme und GC-19 müssen vor Produktion ergänzt werden. Kein neuer Nutzerlauf gestartet.

Nachtrag zum vollständigen Text: [Byteidentisches Revieweroriginal und Eingang](https://github.com/ibenarb/conway99-research/tree/7d456a57cc98d1c04be2dc5a60cd989ee0bf4c6b/docs/reviews/20261004_root8105_text), Zweig `reviews/20261004-root8105-claude-text`. [Vollständiger Abgleich und Fortsetzungsplan V3](../augmentation/root8105_review_response_20261004/ABGLEICH_VOLLREVIEW_UND_PLAN_V3.md): chronologische Aktualisierungen abgeglichen; feste Rootsymmetrie, Label-Disjunktheit und Kapazitätsfilter eingeordnet; zusätzlicher BvLS-Filtercheck bestanden. Praktische Entscheidung gegen sofortige Vollbaum-Materialisierung bestätigt, formaler NO-GO-Anspruch und medianbasierte Gesamtkostenschlüsse zurückgewiesen. Empfehlung zuerst P0+P1 mit 48 CPU-h als Meldeschwelle; keine neue Produktion gestartet. Die frühere Textlücke ist damit geschlossen.

## ROOT8105-Census Betriebsreview, 4./5. Oktober 2026

[Byteidentische Originale und Eingangsmetadaten](https://github.com/ibenarb/conway99-research/tree/fd0e6a72e122be0a047f792dd6d9b0c4be49132b/docs/reviews/20261005_root8105_census), Zweig `reviews/20261005-root8105-census-crosscheck`. Vollständiger Text und ZIP mit Bericht, Patch, Rohbelegen und 1.0.1-rc1. [Eigener Abgleich und konkrete Fortsetzung](../augmentation/root8105_census_crosscheck_20261005/ABGLEICH_UND_FORTSETZUNG.md): mathematische Dateien byteidentisch und RC-Fingerprint bestätigt; verwaiste RUNNING-Root nach reconcile-crash weiterhin gesperrt, selbst reproduziert. Reviewer-Nachzählungen ausdrücklich zugeschrieben. Empfehlung: RC abschließen, C2-schonende Zielhardwareabnahme, P0/P1-Zensus, anschließend begrenzter Filtervergleich. Kein neuer Nutzerlauf; keine Releasefreigabe.
