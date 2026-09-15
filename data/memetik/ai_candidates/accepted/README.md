# Unabhängig geprüfte Kandidaten

Ein Ω-Kandidat aus eigener Ausführung des Gemini-Generators aufgenommen: [gemini_v01_seed42.g6](omega/gemini_v01_seed42.g6), [Abnahmemetadaten](omega/gemini_v01_seed42.json). Zulässigkeit unabhängig bestätigt; Isomorphie- und Einzugsgebietsneuheit nicht festgestellt.

Bei Aufnahme je Graph:
- `lambda/<id>.g6` bzw. `omega/<id>.g6`;
- daneben `<id>.json` mit Originaleinreichung und festem Archivcommit, SHA256, vollständigen Scores, harten Prüfungen, Prüferskript-/Versionsreferenz, Ω-Rahmen falls erforderlich sowie gesondertem Isomorphie-/Neuheitsstatus.

Nur vollständig geprüfte, zulässige Graphen erhalten diese Ablage. Ein PASS für Zulässigkeit beweist keine neue Isomorphieklasse oder neues Einzugsgebiet. Aufnahme ins Archiv und Auswahl für einen konkreten Piloten sind getrennte Entscheidungen.

Fehlgeschlagene oder noch ungeprüfte Daten bleiben unverändert im zugehörigen submissions-Vorgang.

## Aufnahme Claude v01

[Claude-A](omega/claude_v01_a.g6), [Claude-B](omega/claude_v01_b.g6) und [Claude-C](lambda/claude_v01_c.g6) unabhängig validiert; Metadaten jeweils in gleichnamiger JSON-Datei. A/B im Ω-Arm, C im λ-Arm. Untereinander nachweislich nichtisomorph, kein vollständiger Altbestandsvergleich. B ist ein Nachfahre von A. Aktuell vier validierte Graphen einschließlich Gemini.

## Aufnahme Codex v01

Zehn weitere Graphen unter `omega/codex_v01_c01.g6` bis `omega/codex_v01_c05.g6` und `lambda/codex_v01_c06.g6` bis `lambda/codex_v01_c10.g6`; vollständige Abnahmemetadaten jeweils daneben. [Festes Archiv](https://github.com/ibenarb/conway99-research/tree/c10038a3baa23145b666d5e5251e81c139877f83/data/memetik/ai_candidates/submissions/20260915_codex_v01/). Alle zehn byteidentisch reproduziert und gegen 18 benannte Referenzgraphen auf Isomorphie geprüft. Aktueller Gesamtbestand: **14 Graphen (8 Ω, 6 λ)**. C02: W=2074, L1=2506, F=3472, Linf=4. Struktur-/Familienabhängigkeiten siehe REVIEW.md; Einzugsgebietsneuheit nicht belegt.
