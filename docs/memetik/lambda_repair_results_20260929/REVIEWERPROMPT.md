# Auftrag: Drei unabhängige Perspektiven für die Fortsetzung der λ-Memetik

Bitte prüfe das beigefügte flache Datenpaket und entwickle eine Fortsetzung mit dem Fernziel srg(99,14,1,2), W=0. Organisiere drei zunächst unabhängig arbeitende Agenten bzw. getrennte Analysedurchgänge:

1. **Optimierer:** Verbessere das vorhandene Verfahren. Welche präzise Änderung an Fensterwahl, Solvermodell, Operatoren, Budgetverteilung oder Wiederverwendung verspricht messbaren Fortschritt? Identifiziere zuerst den tatsächlichen Engpass.
2. **Hubschrauber:** Betrachte die gesamte bisherige Suchgeschichte und relevante externe Forschung. Welche erfolgversprechende neue Kombination ergibt sich daraus? Unterscheide publizierte Resultate, unsere Messungen und Hypothesen; belege externe Aussagen mit Primärquellen.
3. **Maverick:** Stelle Grundannahmen in Frage, einschließlich harter λ-Bedingung, Suchraum, Zielmaßen, Gründerverteilung und lokaler Reparatur. Entwickle alternative überprüfbare Wege und erläutere Rückführung auf einen gültigen Zielgraphen.

Lass jede Perspektive zunächst selbst urteilen. Eigene Agentenberichte des Absenders stehen im Paket unter AGENT_*; lies diese möglichst erst nach dem unabhängigen Entwurf, um Verankerung zu vermeiden.

Jeder Bericht soll enthalten: Diagnose; bis zu drei Optionen; Mechanismus; Gegenargumente; messbare Hypothese; kleinster aussagekräftiger Vergleich; benötigte Gründer/Operatoren; großzügiges, begründetes Ressourcenbudget; Erfolgs- und Widerlegungskriterien. Trenne Rekordverbesserung, neue Graphklassen, Mechanismusnachweis und zertifizierte Aussagen. Keine Zeitlimits als Unmöglichkeitsbeweis. Keine erfundene Walltimegarantie.

Führe anschließend die Perspektiven zusammen: Wo widersprechen sie sich? Welche Annahme lässt sich am günstigsten entscheiden? Empfiehl einen konkreten nächsten Versuch, ohne einen weiteren Suchlauf vorauszusetzen. Falls Du einen memetischen Hauptlauf empfiehlst, definiere Population und Gründerfamilien, Vielfalt/Isomorphiefilter, Selektion, Mutation, Crossover, Sprungmutation, lokale Optimierung und Ersatzregeln vollständig.

Primärbefund: 24 Gründer,144 feste Fensteraufgaben; 1.2.0 mit7200 CPU s je Aufgabe gegenüber3600 in1.1.0. BesterW2076 unverändert; eine Gründerverbesserung2139→2127 erneut, keine neue Klasse gegenüber1.1.0.88 lokale Solveroptima ohne Ausschlusszertifikat,5 starre Fenster,51 Zeitlimits einschließlich sämtlicher48 großer Fenster. Zwei zusätzliche lokale Optimalitätsmeldungen.1.1.0 hatte zudem einen Kalibrierungsabschlussfehler,1.2.0 behebt ihn. Kein reiner exakter Zeitpräfixvergleich.

Priorität: lokale Rechenzeit ist günstig, manuelle Schleifen teuer. Ryzen mit12 Solverarbeitern, etwa47GiB RAM; laufende Office-C2-Arbeit bleibt unberührt. Regeln und GC-02/08/10/11 beachten. Bitte antworte als drei getrennte Berichte plus kurze strittige Gesamtempfehlung. Neue Software oder Läufe sind mit diesem Reviewauftrag nicht verlangt.

Einstieg: BERICHT.md, SUMMARY.json, TASKS_120.csv, CANDIDATES_25.json, historische HISTORY_* und RULES_*. RUN120__* und RUN110__* sind entpackte Originaldateien mit im FILE_INDEX.json abgebildetem Originalpfad. Keine verschachtelten Archive. analyze.py benötigt die anhand FILE_INDEX.json rekonstruierten Laufverzeichnisse. SOURCE_SHA256SUMS.txt sichert jedes enthaltene Nutzdatenfile.
