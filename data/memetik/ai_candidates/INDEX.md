# Eingangskatalog der KI-Kandidaten

| Eingang | Einreichung | Eingereicht | Aufgenommen | Entscheidung | Festes Archiv |
| --- | --- | ---: | ---: | --- | --- |
| 2026-09-14 | Mistral; Selbstangabe Vibe / Mistral Medium 3.5; v01 | 6 | 0 | REJECTED_AS_SUBMITTED | [dc08364](https://github.com/ibenarb/conway99-research/tree/dc0836414dbeefc6da4460f21dcd1ab4aa5e9eb7/data/memetik/ai_candidates/submissions/20260914_mistral_v01) |

[Original](submissions/20260914_mistral_v01/original.md) · [Prüfbericht](submissions/20260914_mistral_v01/REVIEW.md) · [Prüfdaten](submissions/20260914_mistral_v01/audit.json)

Die Modellkennung ist eine Selbstangabe, keine externe Verifikation. Die empfangene Datei endet nach dem JSON; mögliche Übertragungsverkürzung ungeklärt. Mathematische und Datenformatfehler sind unabhängig davon belegt.

## Mistral v02 — gekürzter Auftrag

| Eingang | Ansätze | Graphdaten | Generatoren | Aufgenommen | Entscheidung | Festes Archiv |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| 2026-09-14, Vibe v02 | 3 | 0 | 0 | 0 | REJECTED_AS_SUBMITTED | [9bbbbfe](https://github.com/ibenarb/conway99-research/tree/9bbbbfece7511c96cdc9103c42318b89c3a64f08/data/memetik/ai_candidates/submissions/20260914_mistral_v02/) |

[Original](submissions/20260914_mistral_v02/original.md) · [Prüfbericht](submissions/20260914_mistral_v02/REVIEW.md) · [Prüfdaten](submissions/20260914_mistral_v02/audit.json)

Schlussmarker vorhanden; angekündigter Code fehlt. Eigene Rekonstruktion der Ω-Regel: H-Grad 2 statt 12 und 840 verletzte PH-Gleichungen. Keine Kandidaten übernommen.

## Korrektur zu v02: Code-Nachtrag

Die Oberfläche hatte Code angezeigt; er wurde beim Kopieren nicht übernommen. Drei nachgereichte Generatoren tatsächlich ausgeführt: jeweils Grad-AssertionError. Metrikfunktion auf allen drei Zwischenständen unabhängig bestätigt. Null Aufnahme; fehlenden Code nicht mehr Mistral zuschreiben. [Nachtrag und Ausführungsbericht](https://github.com/ibenarb/conway99-research/tree/d58dbccb3dce418f57bfb05325cc8cfaec782e65/data/memetik/ai_candidates/submissions/20260914_mistral_v02/code_supplement/) (Archivzweig `reviews/20260914-mistral-v02-code-supplement`).

## Mistral v03

Zwei Generatoren im Chat empfangen und nach dokumentierter Kopierkorrektur ausgeführt. Beide melden NO_CANDIDATE_FOUND; null Aufnahme. D tatsächlich Sidon, aber 594 Kanten verletzen λ. Ω-H hat Grad 22. Eigene Herleitung: keine 14-regulären zirkulären λ-Gründer auf Z99. [Archiv und Prüfbericht](https://github.com/ibenarb/conway99-research/tree/8e8769a39b9b66b12247378a9d7ed5280ec2e95c/data/memetik/ai_candidates/submissions/20260914_mistral_v03/).

## Mistral v04 — letzter Korrekturversuch

Original mit Code erhalten und archiviert. Ω-Backtracking: mit Limit 20 ausschließlich 21 Wiederholungen derselben Zelle; beim Standardlimit RecursionError. Header korrigiert, graph6-Bitreihenfolge nicht. Null Aufnahme. [Archiv und Prüfbericht](https://github.com/ibenarb/conway99-research/tree/cb3687eb3a1e544717f633e11533e6454d9d574f/data/memetik/ai_candidates/submissions/20260914_mistral_v04/).

## Gemini v01 — gültiger Ω-Kandidat

Ein bereitgestellter CP-SAT-Generator, keine von Gemini vorgetäuschte Ausführung. Eigener Probelauf Seed 42, ein Worker: Lösung nach etwa 2,47 s. Alle harten Bedingungen und Scores unabhängig geprüft. W=3107, L1=5310, F=11504, Linf=8. Ein Graph aufgenommen; Isomorphie-/Einzugsgebietsneuheit offen. [Archiv und Prüfbericht](https://github.com/ibenarb/conway99-research/tree/007fa996be815756e83aa129807e1603dab06d2d/data/memetik/ai_candidates/submissions/20260914_gemini_v01/). [Validierter Graph](accepted/omega/gemini_v01_seed42.g6).

## Claude v01 — drei gültige Kandidaten

Zwei Ω-Kandidaten (A/B), ein λ-Kandidat (C); alle Scores unabhängig bestätigt, paarweise Nichtisomorphie belegt. final/cayley byteidentisch reproduziert. Cayley-Ausschluss über alle Gruppen der Ordnung 99 zusätzlich unabhängig geprüft. Herkunft A→B beachten; Fluchtlängenschwelle nicht belegt. [Archiv und Prüfbericht](https://github.com/ibenarb/conway99-research/tree/bfb4f623ad66a8e52373c6ba972b5c5f9e60adb6/data/memetik/ai_candidates/submissions/20260915_claude_v01/).

Validierte Graphen: [Claude-A](accepted/omega/claude_v01_a.g6), [Claude-B](accepted/omega/claude_v01_b.g6), [Claude-C](accepted/lambda/claude_v01_c.g6). Gesamtbestand der neuen KI-Sammlung: vier gültige Graphen einschließlich Gemini; kein Nachweis vier unabhängiger Familien.

## Codex v01 — zehn gültige, reproduzierte Kandidaten

C01–C05 im Ω-Arm, C06–C10 im λ-Arm. Alle harten Bedingungen und Kennzahlen unabhängig bestätigt; zehn byteidentische Wiedererzeugungen. Untereinander und zu 18 benannten Referenzgraphen nichtisomorph. C02 verbessert die dokumentierten Office-Ω-Bestwerte W/L1/F auf 2074/2506/3472. F02 liefert fünf asymmetrische Graphen; die λ-Lifts benötigen Suchbewegungen außerhalb ihrer festen Dreiteilung. Familienvielfalt und Einzugsgebiete bleiben gesondert zu untersuchen. [Archiv und Prüfbericht](https://github.com/ibenarb/conway99-research/tree/c10038a3baa23145b666d5e5251e81c139877f83/data/memetik/ai_candidates/submissions/20260915_codex_v01/).

Aktueller Bestand: **14 validierte KI-Kandidaten (8 Ω, 6 λ)**. Aufnahme ist keine automatische Pilot-Auswahl und kein Nachweis von 14 unabhängigen Familien.
