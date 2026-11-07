# Unabhängiger Reviewauftrag: C2-Beweiskampagne – Korrektheit und weitere Beschleunigung

Stand: 7. November 2026, 08:50 Berlin. Auftraggeber: Ralph.

Bitte prüfe die folgenden Ergebnisse kritisch und unabhängig. Bestätige nichts allein aufgrund unserer Berichte oder bisherigen internen Reviews. Suche nach Gegenbeispielen, fehlenden Voraussetzungen, unzulässigen Symmetrieübertragungen und irreführenden Laufzeitvergleichen. Entwickle anschließend konkrete weitere Verbesserungen, die die vollständige Beweisabdeckung und unabhängige Nachprüfbarkeit erhalten.

## 1. Ziel, Modell und Status

Wir untersuchen einen Teil des C2-Ausschlusses im Conway-99-Projekt, derzeit die Familie L62 mit 62 globalen Fallrepräsentanten. Zwölf Fälle sind vollständig unabhängig geprüft, archiviert und in Git gesichert: 3,4,17,18,20,62,63,68,74,75,76,77. Fünfzig bleiben offen. Fall78 läuft mit versiegeltem S2-Einzelverfahren; keine Änderung dieses laufenden Vertrags. Ein vollständiger L62-Ausschluss würde C2 noch nicht insgesamt abschließen.

Die lokale Suche verwendet zwölf binäre Zeilen mit 60 Spalten. Spalten entsprechen ungeordneten Paaren aus zwölf Grundpunkten, ausgenommen die sechs Paare der festen Involution F(i)=i xor1. P ist die dadurch induzierte Spalteninvolution. Die vollständigen Zeilendomänen werden unabhängig aus dem ursprünglichen Vertrag enumeriert; die Suche verlangt gewöhnliche und verdrehte Skalarprodukte G und K sowie Spaltensumme2. Zeilen0/1 bilden den festen Rand.

Für die Matchingmatrizen M,E und die Inzidenzmatrix W gelten im Originalvertrag:
D=2J-I-F-M-EF,
G=9I+J-M,
K=2J-F-E-ME-EM,
XW=D, XX^T=G, XPX^T=K und jede Spaltensumme=2.
Zusätzliche Komponentenbedingungen gehören zum ursprünglichen Modell; unterscheide ausdrücklich die geprüfte lokale Suchstufe von einem vollständigen C2-Zeugen. UNSAT wird erst nach vollständiger Randabdeckung, unabhängigem Beweisreplay, Abschlussaudit, vollständigem bytegeprüftem Archiv und Git-Sicherung als globaler Fallausschluss gezählt. Ein lokaler SAT-Kandidat ist zunächst am ursprünglichen Vertrag zu prüfen und kein automatischer C2-Zeuge.

## 2. Bisherige Beschleunigung

S1 nutzt die reine Vertauschung der Zeilen2/3, wenn vollständige Domänen identisch und G/K invariant sind. Wegen G22>G23 können die Zeilen nicht gleich sein. Ein Orbitvertreter erfüllt X2<X3; beide dynamischen Zuweisungsreihenfolgen werden berücksichtigt.

S2 ergänzt eine gemeinsame Spalteninvolution tau, induziert durch Vertauschung der Grundpunkte0/1. Sie wirkt auf ALLE Zeilen gemeinsam. Vor Nutzung: tau kommutiert mit P, erhält jede vollständige Domäne und fixiert beide Randmasken. Für a=X2,b=X3 behalten wir das lexikographische Minimum von
(a,b), (b,a), (tau(a),tau(b)), (tau(b),tau(a)).
Der Sucher benutzt explizite Ungleichungen; der unabhängige Prüfer bildet das Minimum der vier Paare. a<=tau(a) ist notwendig; ein unabhängig zusätzlich erzwungenes b<=tau(b) wäre unzulässig. Fixpunkte werden nicht verworfen.

Hinzu kommen wiederverwendete Speicherfelder pro Rekursionstiefe und ein sparsamerer unabhängiger Replay: An einem mit einer leeren Domäne bezeichneten Blatt muss diese Domäne vollständig rekonstruiert werden, nicht alle unbeteiligten Domänen. An Verzweigungen bleiben die erforderlichen vollständigen Prüfungen bestehen.

16 gepaarte reale Teilaufgaben gegen tatsächlich versiegelte alte Produktionsprogramme: 288,036077s gegenüber90,341079s, Faktor3,188318 einschließlich Replay und gzip-Rückprüfung. Acht Aufgaben je Fall20/77; begrenzter Pilot unter laufender Produktionslast, keine Vollfallgarantie.

## 3. Gemeinsame Präfixe und Belegtransaktionen

Der Batchprototyp liest Modell/Aktion einmal und teilt geordnete Kandidatenfilter, die nur von der ersten Randzeile A abhängen. Alle B-abhängigen Bedingungen, insbesondere bereits gesättigte Spalten A&B, bleiben aufgabenspezifisch. A-Wechsel invalidiert den Cache. Jeder Rand behält einen eigenen C2S2-Beweis.

Ein früher direkter Pilot gegen alte Produktion ergab Faktor3,992207: vier Dreiergruppen, zwölf Ausführungen je Variante, aber nur acht unterschiedliche Randaufgaben. Dieser Faktor darf nicht mit anderen Pilotfaktoren multipliziert werden.

Der neueste kontrollierte Vergleich verwendet dieselben Batchprogramme und dieselbe transaktionale Forschungssteuerung, einmal mit Einer-, einmal mit Dreierchunks: 66,977697s gegenüber50,415823s, Faktor1,328505 beziehungsweise24,7274% weniger Zeit. Eingeschlossen sind Ressourcenmessung, Suche, Replay, Snapshots, Kompression und Belegveröffentlichung. Ausgeschlossen sind anfängliche Bundlekopie und globaler Abschlussaudit/Archivierung. Dies ist KEIN direkter Vergleich mit dem produktiven Einzelcontroller.

Native randweise Entscheidungen entstehen erst nach vollständigem EOF-Replay. Der Controller bindet sie an eingefrorene Beweisbytes, Modell/Aktion/Programme, Randindex und Hashes. Beweise werden komprimiert, rückgeprüft und vor der Quittung dauerhaft veröffentlicht. Native JSON-Quittungen allein sind keine übertragbaren Zertifikate. Fehlgeschlagener Gesamtreplay erzeugt keine neuen Controllerquittungen. Geschlossene Suchversuche lassen sich ohne erneute mathematische Suche nachprüfen; ungeklärte Suchabbrüche halten an. SAT/UNKNOWN lassen ungeprüfte Restaufgaben offen.

Der inkrementelle Nachfolger prüft vorhandene Quittungen einmal beim Start, dann nur neue, abschließend die vollständige Menge. Bei96 synthetischen Rändern waren exakt192 Quittungsvalidierungen erforderlich. Das behauptet keine optimale Komplexität sämtlicher Verwaltungsoperationen.

Kontrollen:26 Integritäts-/Zustandstests,3 echte SIGKILL-Tests,3 UNSAT/UNKNOWN/offen-Tests einschließlich Abbruch, Skalierungs-/Lockfehlertest. Alle acht unterschiedlichen realen Beweise bestanden zusätzlich den unveränderten versiegelten Einzelprüfer. Frische öffentliche Reproduktion ohne private Produktionsdaten PASS. Keine Stromausfallgarantie aus Prozessabbruchtests. Batch bleibt Forschungsprototyp, noch kein vollständiger Produktionscontroller.

## 4. Weitere Symmetrien: begrenzter negativer Befund

Ein vollständiger Backtracking-Screen enumeriert reine Zeilenpermutationen, die Zeilen0/1 punktweise fixieren und exakte D-Zeilen sowie G/K erhalten. Unter62 Verträgen:59 Gruppen der Ordnung2, Fälle18/63 Ordnung8, Fall68 Ordnung32. Diese drei größeren Fälle sind bereits geschlossen. Alle50 offenen Fälle haben in dieser Klasse exakt Identität und (2 3). Referenz- und eigenständige Standardbibliotheksimplementierung stimmen vollständig überein.

Das schließt gekoppelte Zeilen-/Spaltenaktionen, randbewegende Transformationen, andere Suchzerlegungen oder mathematische Reduktionen NICHT aus.

## 5. Mizopl und Vergleichbarkeit

Mizopl ist Forschungspartner. Im geprüften externen Stand wurde eine konkrete Überdeckungslücke der Prefixauswahl nachgewiesen: vermischte Index-/Maskenordnung ließ eine zulässige Konfiguration unter allen verwendeten Vertragssymmetrien ohne akzeptierten Vertreter. Das ist kein SAT-Zeuge und widerlegt nicht unsere unabhängige Kampagne. Seine deutlich höhere berichtete Geschwindigkeit ist ohne identische Aufgaben, Symmetrievoraussetzungen, Abdeckung, Hardware und Beweis-/Replaykosten nicht unmittelbar vergleichbar. Bitte trenne einen realen algorithmischen Vorteil von anderer Problemstufe, ausgelassenem Beweisaufwand und unvollständiger Suche. Keine pauschale Bewertung seines gesamten Algorithmus aus diesem lokalen Befund.

## 6. Konkrete Fragen an Dich

1. Tragen S1/S2-Orbitargumente einschließlich Fixpunkten, dynamischer Zeilenwahl und vollständiger Domänen? Ist der Prüfer ausreichend unabhängig, oder teilen Sucher und Prüfer einen systematischen blinden Fleck?
2. Ist Präfixwiederverwendung auch bei ABA, verkürzten Restlisten und SAT/UNKNOWN sicher? Können Quittungen bei Crash, Dateifehlern oder Wiederaufnahme unzulässig als Abschluss gelten?
3. Bestätigst Du Messzahlen und ihre genaue Reichweite? Welche kleinste zusätzliche, aussagekräftige Vergleichsreihe fehlt vor einer Produktionsentscheidung?
4. Ist der Zeilenscreen innerhalb seiner definierten Klasse vollständig? Welche größeren GEKOPPELTEN Gruppen oder dynamischen Stabilisatoren können wir nutzen, ohne getrennte Kanonisierungen fälschlich zu kombinieren?
5. Wo entsteht weiterhin wiederholte Suche? Prüfe insbesondere gemeinsame Zwei-/Mehrzeilenpräfixe, kanonische Restzustände, sichere Memoisierung/Teilbeweiswiederverwendung, Bitset-Kompatibilität, Constraint-Propagation und Suchreihenfolge. Für jede Übertragung: exakter Zustands-/Vertragsschlüssel, Vollständigkeitsargument, Cacheinvalidierung und unabhängiger Replay.
6. Welche Ideen versprechen eine wesentliche Reduktion von Suchknoten oder Prüfarbeit statt nur Initialisierungskosten? Welche davon lassen sich mit einem begrenzten entscheidenden Experiment verwerfen oder bestätigen?

## 7. Gewünschtes Ergebnis und Arbeitsregeln

Bitte liefere: (a) bestätigte Befunde mit Beleg, (b) konkrete Fehler/Gegenbeispiele oder offene Voraussetzungen, (c) maximal drei priorisierte Verbesserungen mit mathematischer Begründung, Aufwand, erwarteter Wirkung als Hypothese und kleinstem entscheidendem Test, (d) klare Trennung Forschungsfreigabe/Produktionsfreigabe. Falls eine Behauptung nicht prüfbar ist, benenne genau die fehlende Evidenz. Keine neuen Ausschlüsse aus bloßen Laufzeitmessungen ableiten.

Laufenden Fall78, sämtliche T20-Prozesse/Parameter und bestehende Beweisdateien unverändert lassen. Keine parallelen Vollkampagnen, keine zweiten Controller, keine Heartbeats, keine E-Mails oder GitHub-Kommentare. Tests ausschließlich isoliert, begrenzt und ressourcengeprüft. Bei wesentlicher Verfahrensänderung unabhängiger Review vor Produktion.

## 8. Einstieg und Belege

Öffentlich:
- https://github.com/ibenarb/conway99-research/blob/main/docs/c2/SYMMETRY_SPEEDUP_2026-11-07.md
- https://github.com/ibenarb/conway99-research/blob/main/docs/c2/BATCH_RECOVERY_2026-11-07.md
- https://github.com/ibenarb/conway99-research/tree/main/verification/c2_batch_recovery_20261107
- https://github.com/ibenarb/conway99-research/blob/main/docs/c2/BOUNDARY_COVERAGE_AUDIT_2026-11-06.md

Lokaler Workspace: C:\Users\rb\.codex\.chatgpt-projects\g-p-6a834a51a9908191804a71a0d0060ea4
- work/C2_Rest55_20261104/FORTSETZUNG.md, ledger.json, case_0078/execution_contract.json
- work/C2_ProofReplay_20261107/PUBLIC_REPORT.md, JOINT_PRODUCTION_COMPARISON.json
- work/C2_BatchRecoveryIncremental_20261107/REPORT.md, batch_recovery.py, batch-engine.cpp, batch-verify.cpp, REAL_RESULTS.json, CROSS_REPLAY.json, sämtliche *_CONTROLS.json und PUBLIC_REPRODUCTION.json
- dort screen_rows.py, row_screen_inputs.json, PURE_ROW_SCREEN_PORTABLE.json und ROW_SCREEN_PROVENANCE.json
- vollständiges Archiv review/C2_Batch_Recovery_20261107.zip,197347471Bytes,SHA256 b37aecfe2f45b1896aafdf9b40284ab3b45edf7018b5adaf0763c088420882f9,2707bytegeprüfteNutzdateien.

Privater Belegstand: ibenarb/conway99-review-exchange, Branch review/c2-l62-pilot-20261103, PR3, Commit7df79683b9f6f7a74790df8301f4ae14cd625204. Öffentlicher Stand45f453659cbdc808660b1d3ebf391c591a795af7. Große reale Pilotinputs/Beweise liegen lokal; die kleinen öffentlichen Kontrollen allein reproduzieren nicht die Realmessung.


## Nachtrag: begrenzte Folgeexperimente am 7. November, 09:12 Berlin

Siehe work/C2_Further_20261107/REPORT.md und COMPARISONS.json. Bitte best�tige insbesondere auch die negativen Befunde und ihre Reichweitengrenzen:

- Erweiterter gekoppelter Randstabilisator in F�llen20/77/78: nur0,5291% der Randaufgaben haben Ordnung8 statt4 innerhalb der untersuchten Gruppe. Kein Laufzeitgewinn daraus abgeleitet.
- Beschr�nkte exakte UNSAT-Restzustandsprofilierung:0 beziehungsweise1 Treffer, letzterer ein einzelner Besuch;50.000 Eintr�ge pro Fall, Gr��en-/Kapazit�tsauslassungen. Keine globale Eindeutigkeitsaussage.
- Vier Varianten mit gleichen Compileroptionen und acht Randaufgaben pro Vergleich: Zwei-Zeilen-Widerspruchstest9,43% mehr Gesamtzeit; billige Filter zuerst3,21% weniger; zus�tzliche Pr�fixinvariante praktisch unver�ndert; Filterung kleiner Dom�nen zuerst1,66% weniger. Einmalige explorative Messungen, keine statistisch gesicherte Beschleunigung.
- Alle32 Variantenbeweise und alle Baselines bestehen den unver�nderten Einzelpr�fer. Filterumordnung/Pr�fix ergeben byteidentische Beweise; Dom�nengr��enreihenfolge beh�lt Suchbesuche und Beweisl�nge bei, �ndert teils Leerheitsbl�tter.
- Die ersten Forschungsbuilds hatten versehentlich andere Compileroptionen (-mpopcnt fehlte). Deren Laufzeitvergleiche wurden verworfen und mit gleichen Optionen wiederholt; urspr�ngliche Logs erhalten. Bitte pr�fe auch unsere Messkorrektur.

Welcher einzelne strukturelle Ansatz verspricht angesichts dieser Befunde den gr��ten Erkenntnisgewinn? Bitte trenne Einsparung von Suche, initialem Dom�nenaufbau, Replay und Archivierung; gib einen korrekten Beweisvertrag und den kleinsten entscheidenden Gegen-/Best�tigungstest an. Kein neuer Produktionslauf allein aufgrund eines kleinen positiven Messwertes.

Der interne Reviewer priorisiert inzwischen kleine erkl�rungsbasierte Konflikte: vollst�ndige Ursprungsdom�ne am Leerheitsblatt rekonstruieren, ausschlie�ende Zeilen-/Kapazit�ts-/S2-Gr�nde unterscheiden, kleine hinreichende Belegungsteilmengen unabh�ngig pr�fen und deren Wiederauftreten zun�chst ohne Pruning messen. Bitte best�tige oder widerlege auch diesen vorgeschlagenen n�chsten Schritt.
