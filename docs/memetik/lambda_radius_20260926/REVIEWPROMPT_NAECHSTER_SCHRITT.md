# Reviewauftrag: konkreter nächster Schritt nach der λ-Radiusprüfung

Stand: 26.09.2026. Projekt `ibenarb/conway99-research`, ausschließlich **λ-Memetik auf dem Ryzen**.

Bitte prüfe die nachstehenden Befunde kritisch und empfehle **einen konkreten nächsten Schritt**. Gesucht ist eine begründete Forschungsentscheidung, keine allgemeine Sammlung möglicher Heuristiken. Eine begrenzte Diagnose, ein kontrollierter Pilot, eine Pause oder ein Abschluss dieses Ansatzes sind zulässige Empfehlungen. **Noch keinen neuen Suchlauf programmieren oder starten.** Kleine lokale Auswertungen zur Prüfung sind erwünscht und als solche zu dokumentieren.

## 1. Ziel und bisherige Methode

Gesucht ist ein srg(99,14,1,2). Unsere λ-Kandidaten haben 99 Knoten, Grad 14 und genau einen gemeinsamen Nachbarn je Kante. Für ungeordnete Paare gilt

`r_uv = |N(u) ∩ N(v)| + A_uv − 2`.

W zählt die von null verschiedenen Residuen, L1 summiert ihre Beträge, F ihre Quadrate, Linf ist der maximale Betrag, Nmax dessen Häufigkeit. Optimiert wurde lexikographisch nach (W,L1).

Der bisherige stochastische Operator P verwendet Apex-/Pivot-Perturbationen der Längen 2–4, 5–12 und 13–32 mit Gewichten 4:3:2, anschließend lokale Verbesserung nach (W,L1). Population: 16 Isomorphieklassen je Job. Kein Crossover, keine Migration und keine zusätzliche Sprungmutation. Die jüngste deterministische Radiusprüfung untersucht dagegen alle erreichbaren beschrifteten Zustände bis vier elementare Apex-/Pivot-Züge; sie ist kein weiterer stochastischer P-Lauf.

## 2. Verbindliche Daten und Lesereihenfolge

Alle Links sind auf feste Commits gepinnt. Eigene Projektbewertungen sind Diskussionsgrundlagen, keine unabhängigen externen Bestätigungen.

1. **Jüngster Ergebnisbericht mit Prüfgrenzen:**
   https://github.com/ibenarb/conway99-research/blob/4850aa096c788ea3a25f803d69af1f9b994c7a5a/docs/memetik/lambda_radius_20260926/ERGEBNIS.md
2. **Radius-Prüfartefakte:** `RESULT.json`, `DEPTH3_VERIFIED.json`, `CALIBRATION.json`, `AUDIT.json`, Ledger, Fingerprint und `audit.py`:
   https://github.com/ibenarb/conway99-research/tree/4850aa096c788ea3a25f803d69af1f9b994c7a5a/docs/memetik/lambda_radius_20260926
3. **Originales kompaktes Radius-Rückgabearchiv**, einschließlich Aufgaben, Receipts, Einzelergebnissen, Protokollen und eingefrorenem Programm; **ohne SQLite-Dateien**:
   https://raw.githubusercontent.com/ibenarb/conway99-research/4850aa096c788ea3a25f803d69af1f9b994c7a5a/releases/memetik/ryzen_lambda_radius_100_20260926_audit.tar.gz
   SHA256: `7d35c369e010252c02d5ed2ccf44af3e993618d6b3d134d65c40d6f409f35989`.
4. **Radius-Quellcode, exakte Startgraphen und Tests:** insbesondere `STARTS.json`, `enumeration.py`, `worker.py`, `controller.py`, `SOURCE_PINS.json` und `README.md`:
   https://github.com/ibenarb/conway99-research/tree/8ec085cdb8402a6e33dc186ae0302fea4dd542ec/experiments/memetik/lambda_radius_1_0_0
   Eigenständig ausführbares Quellpaket:
   https://raw.githubusercontent.com/ibenarb/conway99-research/8ec085cdb8402a6e33dc186ae0302fea4dd542ec/releases/memetik/lambda_radius_1_0_0.zip
   SHA256: `af297f07f1e20158b5748279c05e54c4bc456aad8153677f6b11e332b429e767`.
   Dieses Paket dient hier der Codeprüfung, nicht als Aufforderung zum Start.
5. **Früheres flaches Datenpaket D/F/O:** alle 30 Jobs, Originalresultate, Gründer, Graph6-Daten, Bestwertkurven, Messpunkte, Histogramme und Standard-Python-Prüfer. Beginne dort mit `00_REVIEWERPROMPT.md` und `01_DATENUEBERSICHT.md`:
   https://raw.githubusercontent.com/ibenarb/conway99-research/c3197a2cad41d9b6e9f72ba9b90e63fb98a30b14/releases/memetik/Lambda_Review_20260926.zip
   SHA256: `85604ac1218a55f6601a76e589360611886e99ffd518ba571886629b2cba15d7`.
6. **Vorheriges Revieweroriginal und Prüfsatz**, getrennt von unserer Bewertung archiviert:
   https://github.com/ibenarb/conway99-research/tree/7a00a6a93227eb7eb09980355b4d3129975489fc/docs/reviews/20260926_lambda
   **Eigener Abgleich mit strukturellen Auswertungen und Reproduktionsartefakten:**
   https://github.com/ibenarb/conway99-research/tree/d7e3a83aab28dddee9ab02faf0e98f6d3a66e330/docs/memetik/lambda_review_20260926
   Dessen damaliger Tiefe-4-Vorschlag ist inzwischen ausgeführt; seine offenen Tiefe-3/4-Fragen sind durch den jüngsten Bericht aktualisiert.

Diese verlinkten Pakete enthalten die benötigten kleinen Ausgangsdaten. Große Ryzen-SQLite-Dateien sind erhalten, aber nicht beigefügt. Falls sie für eine konkrete entscheidungsrelevante Prüfung erforderlich sind, benenne die benötigten Tabellen/Auszüge und die damit beantwortbare Frage. Fordere nicht pauschal sämtliche Roharchive an.

## 3. Bisherige Kampagnen und Strukturdiagnose

- Vorprüfungen: PCesc ermöglichte mit cycle3 Fluchten aus lokalen Minima, zeigte aber keinen belastbaren Endwertvorteil gegenüber P. Nicht-HoG-Gründer waren in den geprüften Ansätzen schwächer. Das beweist keinen allgemeinen Operator- oder Gründerfamilienausschluss.
- Entscheidungslauf D: sechs V2-Frontier-Jobs à zwei CPU-Stunden, bestes W2096, Median 2102. Acht V3-Jobs von zwei auf acht CPU-Stunden fortgesetzt: bestes W2177, Median 2214; vorab festgelegtes Kriterium W<2150 verfehlt. Zusatzbudget knapp 60 CPU-h.
- Frontier-Lauf F: je vier neue Seeds aus Banken W2096 und W2101, je vier CPU-Stunden. Endwerte 2088/2081/2091/2081 bzw. viermal derselbe beschriftete W2092-Graph; vier Endklassen, knapp 32 CPU-h.
- Übernachtlauf O: sechs Seeds aus einer W2081-Bank und zwei aus einer W2092-Bank, je sieben CPU-Stunden. Endwerte 2079/2076/2076/2079/2076/2078 bzw. 2077/2084; sieben Erfolge W<2081 in vier erfolgreichen Endklassen. Alle drei W2076-Treffer sind derselbe beschriftete Graph. Verbrauch 55,989 Such-CPU-h.
- O hatte nach vier CPU-Stunden je Job bereits sieben Erfolge und zwei W2076-Treffer. Ein dritter W2076-Treffer kam bei 4,75 h; späte L1-Verbesserungen und weitere Klassen traten auf, aber kein neuer kampagnenweiter W-Rekord. Der durchgehende Sieben-Stunden-Lauf war ausdrücklich vorab autorisiert, keine Protokollverletzung.

| Kandidat | W | L1 | F | Linf | Nmax |
| --- | ---: | ---: | ---: | ---: | ---: |
| W-Rekord | 2076 | 2488 | 3352 | 3 | 20 |
| Alternative | 2077 | 2436 | 3180 | 3 | 13 |

Beide Graphen sind asymmetrisch. Die strukturelle Untersuchung ist inzwischen erfolgt: Residuenhistogramme, Knotenlasten, Automorphismen und die empirische (W,F)-Paretofront liegen im eigenen Abgleich. Die Paretopunkte des geprüften Pakets sind (2076,3352), (2077,3180), (2078,3172), (2097,3088), (2143,3084). Das ist kein projektweiter F-Rekordnachweis.

Im λ-Raum gelten `sum_nonedge r = 0` und `F = 4(Q−2079)` für die Zahl Q nichtorientierter Vierkreise. W=0 und F=0 charakterisieren beide das Ziel; ihre Größe ist kein nachgewiesener Zugabstand zur Lösungsmenge. Ein F-Wechsel braucht deshalb eine eigene Begründung.

## 4. Jüngster Befund: Radius vier abgeschlossen

Zwei exakte Einzelstarts, keine Gründerbank:

- W2076: state `8169eba8e1f2bf78eb655d99b94844a1eb5056df828e8c610a3778d537a7d0fe`.
- W2077: state `136bad89e063ba84bbc4201cfa5be21db6d511852602ad861a4d2c0e0ef8e49c`.

Unveränderter Apex-/Pivot-Katalog, keine fitnessabhängige Auslassung und kein Isomorphie-Pruning. Erfolg: strikt lexikographisch besseres (W,L1) als der jeweilige Start; W<2076 wäre separat ein globaler W-Rekord.

| Arm | Tiefe-3-Kindübergänge | Verschiedene beschriftete Zustände in exakter Tiefe 3 | Tiefe-4-Kindübergänge | Vollständige Tiefe-4-Jobs | Tiefe-4-CPU-h |
| --- | ---: | ---: | ---: | ---: | ---: |
| W2076 | 526476 | 195508 | 19873151 | 1528/1528 | 18,17643 |
| W2077 | 459185 | 169048 | 16408393 | 1321/1321 | 15,57459 |

Beide Arme melden `COMPLETE_NO_IMPROVEMENT_DEPTH4`. Keine Verbesserung bis Tiefe 3 oder 4, kein Ressourcenabbruch. Die insgesamt 36.281.544 Tiefe-4-Kindübergänge sind **keine Zahl verschiedener Endgraphen**.

Gesamtabrechnung einschließlich Hilfsarbeiten 34,78827 CPU-h; darin 20 konservativ reservierte CPU-Sekunden für Vorbereitung/Start. Host-Walltime 3 h 6 min 26 s; beendet 26.09.2026 um 16:48:47 MESZ. Grenzen 2 CPU-h Hilfsarbeit und 20 CPU-h je Arm eingehalten.

**Prüfstand:** Rückgabearchivhash bestätigt; 67 Quelldateien plus Manifest byteidentisch zum Startpaket; 2934 Jobs mit passenden Task-/Ergebnishashes, DONE und Exitcode 0; gemeldete ID-Intervalle lückenlos/disjunkt, Zähler und CPU-Abrechnung konsistent. Drei Eingabegraphen unabhängig bewertet und kanonisiert, positiver Vier-Zug-Kontrollpfad W2079→W2076 vollständig nachgespielt.

**Prüfgrenze:** Der Cloud-Audit hat weder die ausgelassenen SQLite-Zustandsmengen geprüft noch die 36,28 Millionen Übergänge unabhängig erneut enumeriert. Integrität und innere Konsistenz des kleinen Pakets plus Kontrollreplay sind bestätigt; eine unabhängige Vollreproduktion des negativen Radiusbefunds liegt nicht vor. Gemeinsamer Operatorcode bleibt eine mögliche gemeinsame Fehlerquelle.

Gemäß der vollständigen Ryzen-Rechnung existiert für diese beiden Starts keine strikt (W,L1)-bessere Konfiguration in höchstens vier zulässigen Zügen. Falls eine solche überhaupt erreichbar ist, braucht sie mindestens fünf Züge. Das ist keine Aussage über die notwendige zwischenzeitliche Fitnessverschlechterung, andere Starts, andere Operatoren oder eine Erschöpfung des λ-Raums.

## 5. Deine Fragen und gewünschte Rückgabe

1. **Befundprüfung:** Welche zentralen Aussagen kannst du reproduzieren? Welche bleiben Interpretation oder offene Frage? Prüfe insbesondere Abdeckung, Bedeutung des Radiusbegriffs, Operatorvollständigkeit und die Reichweite des Audits. Gib konkrete Quellenstellen und tatsächlich ausgeführte Rechnungen an; behaupte keine nicht ausgeführten Prüfungen.
2. **Entscheidungswert:** Was ändert der negative Radius-4-Befund gegenüber dem vorherigen Review tatsächlich? Rechtfertigt er weitere Suche, eine andere begrenzte Diagnose oder eine Pause? Begründe dies ohne globale Erschöpfung zu behaupten.
3. **Ein priorisierter nächster Schritt:** Welche präzise Frage soll als Nächstes beantwortet werden und welche Entscheidung hängt von der Antwort ab? Vergleiche knapp höchstens drei plausible Optionen und wähle eine. Denkbar, aber nicht vorgegeben, sind eine zusätzliche Absicherung der Radiusrechnung, eine strukturelle/Operator-Diagnose oder ein kontrollierter Zielfunktions-/Startpopulationspilot. Tiefe 5, F-Wechsel und erneuter P-Lauf sind keine automatischen Folgerungen.
4. **Ausführbarer Versuchsplan:** Benenne exakte Startgraphen oder eine deterministische Auswahlregel samt Pool; Kontroll- und Vergleichsarme; Operatoren und zulässige Zwischenzustände; Zielfunktion und sekundäre Messgrößen; Anzahl Replikate/Seeds oder Vollständigkeitskriterium; CPU-Budget je Arm und Hilfsbudget; Parallelität, RAM/Disk und realistische Walltime. Falls ein Punkt nicht anwendbar ist, erkläre das kurz. Trenne lokale Verbesserung, neuen globalen Rekord und diagnostischen Erkenntnisgewinn.
5. **Vorabentscheidung:** Lege Erfolg, negatives Ergebnis, Unvollständigkeit sowie Abbruch-/Pausenkriterien vorab fest. Welche Ergebnisse führen zu welcher nächsten Entscheidung? Kein automatisches Hochskalieren. Schätzungen müssen Annahmen und eine kleine Kalibrierung nennen; gemessene Tiefe-4-Kosten sind keine belastbare Tiefe-5-Prognose.
6. **Falls Pause/Abschluss empfohlen:** Benenne den konkreten Abschluss- oder Sicherungsschritt und die neue Evidenz, die eine Wiederaufnahme rechtfertigen würde. Eine Pause ist eine Ressourcenentscheidung, kein mathematischer Ausschluss.

Erwartete Rückgabe: zuerst eine klare Empfehlung, dann eine kurze Tabelle „reproduzierter Befund / Interpretation / offene Frage“, anschließend der konkrete Plan mit Entscheidungskriterien. Lege bei eigenen Auswertungen Skripte, Ergebnisse und Quellenhashes bei.

## 6. Grenzen und Umgebung

Adaptive Bankauswahl und ungleiche Wiederholungszahlen erlauben keinen kausalen Familienvergleich. Wiederholtes Erreichen derselben Klasse beweist keine Vielfalt; unterschiedliche Klassen beweisen keine unabhängigen Suchbecken. Kürzeste Zugabstände sind keine rekonstruierten Produktionspfade, nächste Gründer keine Abstammungsnachweise. Verändere in einem Vergleich nicht zugleich mehrere Methodenbestandteile ohne dafür passende Kontrollen.

Nur Ryzen, WSL2 Ubuntu; Python `$HOME/conway99_workspace/venvs/memetik/bin/python`. Originalverzeichnis `$HOME/conway99_workspace/ryzen_lambda_radius_100_20260926` einschließlich SQLite erhalten. Laufende oder eingefrorene Umgebungen nicht ändern. WSL-Monotonzeit driftet: Windows-Host-Monotonzeit und CPU-Abrechnung über wait4; Status alle zehn Minuten mit vorsichtiger ETA. Bisheriger Rahmen: höchstens 12 Worker, 8 GiB Prozessgruppen-RAM, 10 GiB neue Ausgaben; Pause bei weniger als 6 GiB verfügbarem RAM oder 25 GiB freiem Linux-/Windows-Datenträgerplatz. Ein anderer Rahmen muss ausdrücklich begründet werden.

Cloud-Audits mit pynauty über den isolierten Helfer `tools/memetik/audit_python.py` (pynauty 2.8.8.1), nicht über eine zufällige Benutzerinstallation:
https://github.com/ibenarb/conway99-research/blob/4850aa096c788ea3a25f803d69af1f9b994c7a5a/tools/memetik/audit_python.py

Deutsch, präzise, keine überzogenen Schlussfolgerungen. Softwareanweisungen an den Nutzer immer nur einen Schritt pro Antwort, Shellbefehle als Einzeiler. Vor Git-Aktionen `AGENTS.md` und `docs/CONWAY99_COLLABORATION.md` lesen. Ein eingehendes Review wird später byteidentisch auf eigenem Reviewbranch archiviert; unsere Bewertung bleibt separat. Dieser Auftrag autorisiert ausschließlich Review und kleine Prüfungen, keinen neuen Produktionslauf.
