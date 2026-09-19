# Auftrag: kritisches externes Review der Conway99-Involutionsstrategie

Bitte begutachte als unabhängiger Reviewer mit Kenntnissen in algebraischer
Graphentheorie und beweisgestütztem SAT die beigefügte Datei
`BERICHT_UND_STRATEGIE.md`. Gegenstand ist ausschließlich die Involutionssuche
für einen stark regulären Graphen mit Parametern (99,14,1,2).

Wir wünschen ausdrücklich Kritik an Modell, Interpretation und Prioritäten,
keine Bestätigung unserer bisherigen Entscheidungen. Entwickle bei Bedarf eigene,
auch grundsätzlich andere Vorschläge. Die bisherigen Suchkosten rechtfertigen
keine Fortsetzung eines ungeeigneten Ansatzes.

## Ausgangslage und Belege

Alle unten verlinkten Belege sind auf den Git-Stand
`1dc3d773254cb914f49a067d298178a720ff6f72` festgelegt. Der zu prüfende Bericht
liegt daneben unter `docs/c2_review_20260919/BERICHT_UND_STRATEGIE.md`.

- [Modellspezifikation](https://github.com/ibenarb/conway99-research/blob/1dc3d773254cb914f49a067d298178a720ff6f72/docs/c2_spec_20260913/SPEZIFIKATION.md)
- [Datierter Literaturabgleich](https://github.com/ibenarb/conway99-research/blob/1dc3d773254cb914f49a067d298178a720ff6f72/docs/c2_spec_20260913/LITERATURABGLEICH.md)
- [Referenzencoder und Reproduktion](https://github.com/ibenarb/conway99-research/blob/1dc3d773254cb914f49a067d298178a720ff6f72/docs/c2_reference_20260913/README.md)
- [Matching-Orbitsatz](https://github.com/ibenarb/conway99-research/blob/1dc3d773254cb914f49a067d298178a720ff6f72/src/c2_matching_20260915/THEOREM.md)
- [Matching-Abdeckung](https://github.com/ibenarb/conway99-research/blob/1dc3d773254cb914f49a067d298178a720ff6f72/results/c2_matching_20260915/cover.json)
- [Totalizer-Argument](https://github.com/ibenarb/conway99-research/blob/1dc3d773254cb914f49a067d298178a720ff6f72/src/c2_counter_ab_20260916/THEOREM.md)
- [8h-Referenzexperiment](https://github.com/ibenarb/conway99-research/tree/1dc3d773254cb914f49a067d298178a720ff6f72/results/c2_matching_20260916/eight_hour)
- [20min-A/B-Experiment](https://github.com/ibenarb/conway99-research/tree/1dc3d773254cb914f49a067d298178a720ff6f72/results/c2_counter_ab_20260917)
- [34h-Totalizerexperiment mit Originalarchiv und Auswerteskript](https://github.com/ibenarb/conway99-research/tree/1dc3d773254cb914f49a067d298178a720ff6f72/results/c2_totalizer_34h_20260919)

Im letzten Experiment blieben alle elf Fälle nach je 34 Stunden offen; etwa
374 CPU-Stunden wurden verbraucht. Es entstanden keine Produktionsbeweise.
Der Totalizer benötigte im kurzen A/B-Vergleich weniger Speicher. Aus diesem
Befund leiten wir keinen bewiesenen Geschwindigkeitsvorteil ab.

Hardware und Betriebsrahmen: Ryzen mit 24 logischen Threads, bisher elf
CaDiCaL-Prozesse, WSL2/Debian unter Windows, 48 GiB WSL-RAM-Limit.
Der letzte bekannte Windows-Freiraum lag bei etwa 200 GiB, nicht bei den rund
953 GiB, die das virtuelle Linux-Dateisystem meldete. Frühere unbeschränkte
LRAT-Ausgaben füllten den Hostdatenträger. Neue Scouts arbeiten ohne Proof-Logging;
Zertifizierung braucht einen gesonderten begrenzten Lauf. Bitte keine langen
Solverläufe starten und keine Änderungen am Projekt vornehmen.

## Zu prüfende Fragen

1. **Literatur und Neuheitsziel.** Was ist zum Involutionsausschluss tatsächlich
   bewiesen? Prüfe insbesondere den Satz über genau einen Fixpunkt und die
   einschlägigen Aussagen bei Thakkar anhand ihrer Beweise und Voraussetzungen.
   Übernimm unseren datierten Literaturabgleich nicht als Autorität. Nenne genaue
   Quellen, Versionen und Satz-/Abschnittsstellen. Falls bereits ein gültiger
   vollständiger Ausschluss vorliegt: Welche eigene Arbeit wäre eine sinnvolle
   unabhängige Zertifizierung, welche nur Wiederholung? Welcher Ansatz könnte
   darüber hinaus einen neuen Beitrag zum Symmetrieausschluss leisten?

2. **Vollständigkeit des Modells.** Prüfe den Rahmen 1+14+84, die vorgeschriebene
   Involution, E1/E2/E3, die 1722 Primärbits sowie die Rekonstruktion eines
   vollständigen Graphen aus einem Modell. Unterscheide schriftliche generische
   Beweise, endliche Kontrollen und tatsächlich geprüfte Produktionsartefakte.
   Reichen die notwendigen Bedingungen gemeinsam auch hin? Wo fehlen Argumente?

3. **Symmetriereduktion.** Prüfe die elf Typen als vollständige Orbitabdeckung
   der 10395 lokalen Matchings und die zulässigen gemeinsamen Transporter.
   Unterscheide das Matching F auf 42 Paaren vom lokalen Matching L auf zwölf
   Knoten. Bewerte die byteidentische CNF nach Ergänzung der F-Bedingung.
   Welche weitere Normalisierung ist wirklich zulässig, insbesondere bei zwei
   gekoppelten Nachbarschaften oder einer Q/D-Formulierung?

4. **Experimentelle Aussagekraft.** Kontrolliere die Berichte anhand der
   Originalarchive und Auswerteskripte, soweit möglich. Prüfe das Fehlen von
   Entscheidungen, Budgetzensierung, Seeds, Wellenreihenfolge und die
   Vergleichbarkeit der Kennzahlen. Was sagen Restvariablen, Konflikte und
   Speicherverbrauch tatsächlich aus? Benenne ausdrücklich unzulässige
   Fortschritts- oder Erfolgsschätzungen. Gespeicherte Hashfelder allein sind
   keine erneute Prüfung fehlender CNF- oder Binärdateien.

5. **Vorschlag A: kurze Folgeklauseln.** Sind die beschriebenen Drei-/Vierliteral-
   Klauseln korrekt, einschließlich identifizierter Kantenvariablen und Gewichte?
   Sind sie im vorhandenen Encoder bereits enthalten, subsumiert oder vollständig
   durch Unit-Propagation erschlossen? Kann explizite Ergänzung trotz gleicher
   logischer Stärke nützen? Entwirf einen aussagekräftigen kleinen Test und ein
   Abbruchkriterium. Wäre ein anderer Encoder-Eingriff besser?

6. **Vorschläge B/C: strukturelle Zerlegung und Cubing.** Welche zweite
   Nachbarschaft oder welche Primärvariablen wären begründet zu wählen?
   Wie lässt sich vollständige Abdeckung ohne unzulässige Symmetrieannahmen
   sichern? Wie verhindert oder erkennt man früh einen dominanten offenen Ast
   mit vielen trivialen Seitenblättern? Schlage messbare Auswahlkriterien vor.

7. **Vorschlag D: Paar-/Vorzeichenmodell.** Prüfe Q/D-Kopplung und Spektralargumente.
   Welche Bedingungen sind nur notwendig, welche ergeben ein exaktes Modell?
   Gibt es eine praktisch bessere algebraische oder kombinatorische Darstellung,
   lokale Obstruktionen oder ein tragfähiges Lift-Verfahren? Verhindere, dass
   eine leichter lösbare Relaxation irrtümlich als ursprüngliches Problem gilt.

8. **Eigene Alternativen und Priorisierung.** Entwickle gegebenenfalls eigene
   Vorschläge jenseits A–D, zum Beispiel stärkere Strukturlemmata, andere exakte
   Constraints, spezialisierte Enumeration oder einen begründeten Wechsel des
   Forschungsziels. Erkläre den erwarteten Wirkmechanismus und die Risiken.
   Bewerte auch, ob elf Prozesse sinnvoll sind oder ein kontrollierter Vergleich
   anderer Parallelisierungen lohnt; 24 logische Threads sind kein Beleg für
   24-fachen Durchsatz. Schätze Entwicklungsaufwand und Pilotbudget getrennt;
   eine unbekannte Gesamtlösezeit darf ausdrücklich unbekannt bleiben.

## Gewünschte Antwort

Bitte liefere einen eigenständig lesbaren Markdown-Bericht mit:

- kurzem Gesamturteil und klarer Aussage, was bewiesen, kontrolliert, nur
  angenommen oder offen ist;
- Befunden nach Schweregrad, jeweils mit konkretem Beleg, mathematischer
  Begründung oder Gegenbeispiel und betroffener Datei/Behauptung;
- begründeter Rangfolge von A–D und deinen eigenen Alternativen, einschließlich
  verworfener Vorschläge;
- einem konkreten nächsten Experiment, das binnen weniger Arbeitsstunden
  vorbereitet werden kann: Hypothese, Vergleich, Messgrößen, Budget sowie
  vorab festgelegte Kriterien für Fortsetzung, Änderung und Abbruch;
- einem Weg vom erfolgreichen Scout zur unabhängig prüfbaren vollständigen
  Zertifizierung, einschließlich Abdeckung und begrenztem Proof-Speicher;
- offenen Rückfragen und einer Liste der von dir tatsächlich gelesenen,
  reproduzierten bzw. nicht zugänglichen Belege.

Bitte fehlende Daten kenntlich machen und keine fiktiven Reproduktionen oder
Laufzeitschätzungen einsetzen. Eine begründete Empfehlung, die gegenwärtige
C2-Suche zu beenden oder grundlegend umzubauen, ist ausdrücklich willkommen.
