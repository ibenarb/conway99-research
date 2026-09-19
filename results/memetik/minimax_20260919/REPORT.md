# Office Minimax 0.3.0 — Abschlussprüfung vom 19.09.2026

Ausschließlich Memetik/Escape, Office rb-PC; Branch memetik.

## Herkunft

Original: Ergebnisse_Minimax_030_minimax_20260917_213047_385349.zip

292828623 Bytes; SHA256 eb0b94a06ee2740d0439354146e6785f054e484816670464595ade4214444fe7.
Dateigröße und SHA256 entsprechen der Office-Exportmeldung. Sämtliche ZIP-Einträge wurden mit CRC-Prüfung entpackt. Das Original liegt als hochgeladenes Artefakt vor; dieser Git-Bericht enthält NICHT das 293-MB-Original oder die SQLite-Dateien. Der Office-Lauf bleibt als ursprünglicher Checkpoint erhalten.

Release-Referenz: 8f9fa3f7b03a631b9bb09b6f330b9c5d8a4ab7cf.

## Ergebnis

B/Ω/W: IMPROVEMENT_FOUND. 9241 entdeckte beschriftete Zustände, 37 Expansionen. Pfad W: 2082 → 2094 → 2094 → 2086 → 2090 → 2080, fünf Übergänge. Endpunkt (W,L1,F,Linf,Nmax)=(2080,3360,8980,10,34). Alle sechs Graphen unabhängig mit Mengen-Nachbarschaften geprüft: einfach, ungerichtet, 14-regulär, kanonischer Ω-Rahmen einschließlich harter Gleichungen, sämtliche Kennzahlen. Alle fünf gespeicherten Kantenänderungen reproduzieren den Folgezustand. Zusammen mit dem zuvor geschlossenen Subniveau W<2094 ergibt sich die minimale Fluchtbarriere 12 im untersuchten Katalog. Keine Behauptung kürzester Weglänge. Kein Beleg eines lokalen Minimums bei W=2080.

HoG57338/λ/F: WALLTIME_LIMIT. 2142386 entdeckte beschriftete Zustände, 76258 Expansionen. Start F=2836, minimale offene Minimax-Markierung 3028, gemeldete notwendige Barriere ≥192. Keine gefundene Verbesserung. Komponente nicht geschlossen. Die Konsistenzprüfung ersetzt keine vollständige unabhängige Neuenumeration der Nachbarschaften; ≥192 bleibt ein durch Suchcode und Checkpoint gestützter Befund, kein vollständig unabhängig reproduziertes Abschlusszertifikat.

## Prüfumfang und Grenzen

AUDIT.json dokumentiert SQLite integrity_check, vollständige Zustandszahlen, alle Vorgängerverweise und Minimax-Rekurrenzen, alle Vollständigkeitsflags geschlossener Zustände sowie deterministische Stichproben unabhängiger Graph- und Kennzahlenprüfungen. Weder alle 2,14 Millionen Graphen noch sämtliche Nachbarschaften wurden unabhängig neu berechnet. Beschriftete Zustände sind keine Isomorphieklassen.

Zur Reproduktion audit.py und verify_results.py neben die entpackten Originaldateien legen und audit.py ausführen. Der Prüfer verändert die Datenbanken nicht.

Die Laufzeitzähler sind nicht identisch: elapsed_wall_seconds_since_launch=122402, session_seconds=132601. Ursache aus dem Export nicht geklärt; deshalb nicht beide als identische 34-Stunden-Zeitmessung interpretieren. Das Programm meldet das Erreichen der absoluten UTC-Endfrist 2026-09-19T05:30:47Z.

## Nächster sinnvoller Schritt

Checkpoints bewahren. B ab dem geprüften W=2080 gezielt absteigen; neue Endpunkte jeweils mit vollständigem Kennzahlenvektor prüfen. Für HoG zunächst Schichtenwachstum und strukturelle Diversität auswerten, bevor weiteres Suchbudget vergeben wird. Keine Wiederholung abgeschlossener Zensen; Populationspilot bleibt nachgeordnet.
