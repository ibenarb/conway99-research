# ROOT8105-Abschluss und unabhängiger Review, 04.10.2026

**Status:** Dokumentiert und zur Entscheidung vorgelegt. Kein neuer Lauf gestartet; Entscheidung nach Rückgabe des Reviews.

- [Reviewerauftrag](REVIEWERPROMPT.md): unabhängig analysieren und eigenen Plan entwickeln; zunächst Rohdaten, dann die Codex-Vorschläge lesen.
- [Ergebnisse und Abgleich](ERGEBNISSE_UND_ABGLEICH.md): Pilotbefund, Evidenzgrenzen und Modellunterschied zum H-Faser-Handoff.
- [Konkreter Fortsetzungsplan](FORTSETZUNGSPLAN.md): getrennte Modellkontrollen, 32 Roots mit exakter erster Erweiterung, vier davon mit geplanter vollständiger Folgeschicht; 480 CPUh als vorgeschlagene Meldeschwelle mit Weiterarbeit bis Antwort.
- [Nachgerechnete Kennzahlen](DERIVED_METRICS.json) und [Nachrechnung](audit_results.py).
- [Unveränderter Nutzerexport](ROOT8105_Abschlussberichte.tar.gz) und [entpackte Originalberichte](raw/).
- [Quellenindex](SOURCE_INDEX.json), [Dateiprüfsummen](SHA256.json).

Wichtigste Modellpräzisierung: Ein H-linearer Zeuge garantiert Completion für XP=M und Gradbedingungen, nicht automatisch für die zusätzlichen Paar-/Sternbedingungen von ROOT8105. Die linearen Positivkontrollen bleiben sinnvoll, müssen aber vom stärkeren Suchmodell getrennt werden.

Reproduzierbarkeit der Berichtszahlen: Im Verzeichnis `python3 audit_results.py` ausführen und JSON mit DERIVED_METRICS.json vergleichen. Nur Python-Standardbibliothek erforderlich. Das liest die Daten und schreibt keine Dateien. Kein Beweis-Recheck und keine Reproduktion der extern berichteten H-Faser-Klassifikationen.

Die vollständigen 33,75GB Projektionsdaten, Einzel-CNFs, DRAT-Dateien, Checkerlogs und H-Faser-Zeugen gehören nicht zu diesem kleinen Berichtsexport. Der Reviewer soll fehlende entscheidungsrelevante Artefakte benennen. Die historischen Pakete und laufenden anderen Prozesse bleiben unverändert.
