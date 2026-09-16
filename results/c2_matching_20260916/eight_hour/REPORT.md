# C2: Achtstundenlauf vom 16. September 2026

## Nachweisstand

Alle elf Matching-Orbitfaelle: OPEN_BUDGET, exit 0, in jedem Solverlog UNKNOWN.
88 CPU-Stunden; 28803 Sekunden Gesamtlaufzeit. Kein SAT, kein UNSAT, keine Zertifizierung.
Das Original-ZIP ist byteidentisch beigefuegt; SHA256 und CRC-Pruefung stehen in analysis.json.
Alle elf result.json wurden mit summary.json abgeglichen. Die CNFs selbst sind nicht im ZIP;
ihre Identitaet wird hier nur anhand der gespeicherten Hashes berichtet, nicht neu geprueft.
Quellstand: 1a8636ea6ad2a4199f6c7ac4f02e41cbf756d945, Controller 1.0.2.

## Diagnose

Kein Hinweis auf einen Ressourcenabbruch. Jeder Prozess nutzte nahezu acht CPU-Stunden.
Rund 94 Prozent der Solverzeit entfielen auf search. Konfliktzahlen sind Suchaktivitaet,
kein Fortschrittsprozent und keine Rangfolge der Loesungsnaehe. Variablenzahlen schliessen
Hilfsvariablen ein; eliminated/fixed darf nicht als ausgeschlossener Anteil der Graphen gelesen werden.

| Fall | Konflikte | verbleibende Variablen | irredundante Klauseln | Search % |
|---|---:|---:|---:|---:|
| 1_1_1_1_1_1 | 10396564 | 205933 | 1077074 | 94.28 |
| 1_1_1_1_2 | 9480636 | 216103 | 1131053 | 94.22 |
| 1_1_1_3 | 9757727 | 221095 | 1156408 | 94.24 |
| 1_1_2_2 | 9385489 | 226142 | 1184034 | 94.15 |
| 1_1_4 | 9410698 | 226029 | 1182407 | 94.08 |
| 1_2_3 | 9257745 | 231324 | 1210604 | 94.08 |
| 1_5 | 9201061 | 231107 | 1208536 | 93.99 |
| 2_2_2 | 9123141 | 236301 | 1236927 | 94.23 |
| 2_4 | 9197094 | 236381 | 1236376 | 94.24 |
| 3_3 | 9206221 | 234742 | 1239019 | 94.42 |
| 6 | 9186706 | 236115 | 1236162 | 94.55 |

Die Typen mit mehr Einsen haben tendenziell kleinere Restformeln. Das ist ein beobachteter
Struktureffekt, kein nachgewiesener Laufzeitvorteil. Ohne parallel gleich budgetierte Baseline
kann dieser Lauf keinen Vorteil der Matching-Zerlegung gegen die Baseline quantifizieren.

## Naechster begrenzter Versuch (Vorschlag, nicht implementiert oder gestartet)

Zuerst die Kodierung verstaerken bzw. alternative Zaehler testen, bevor weitere grosse
Fallbaeume erzeugt werden. Der Referenzencoder bleibt die semantische Referenz.
E3 kodiert fuer aeussere Knoten x,y:

    M_xy + sum_z (M_xz AND M_zy) = 2 - |labels(x) intersect labels(y)|.

Die kleinen rechten Seiten 0,1,2 erlauben einen gezielten Vergleich des vorhandenen BDD
mit einer spezialisierten, projektionsaequivalenten Kardinalitaetskodierung. Gewichtete
bzw. mehrfach auftretende Literale und Konstanten muessen korrekt erhalten bleiben.
Eine kleinere CNF allein beweist keine bessere Suche.

Als getrennte Variante kommen direkte, logisch redundante Konfliktklauseln in Frage:
Ist c die schon im festen Rahmen vorhandene Zahl gemeinsamer Nachbarn von x,y und
c+M_xy+M_xz*M_yz+M_xw*M_yw>2, ist diese gemeinsame Kantenbelegung verboten.
Hier z,w verschieden und ausserhalb des festen Rahmens. Diese Klauseln folgen unmittelbar
aus der E3-Gleichung; ihre explizite Aufnahme koennte Konflikte frueher propagieren.
Nicht blind alle Kombinationen ausgeben: Umfang vorher zaehlen und auf strukturell
relevante Paare begrenzen. Wirksamkeit ist eine ungetestete Hypothese, kein neues Lemma.

Pruefung: kleine exhaustive Projektionskontrollen inklusive wiederholter/gewichteter Literale,
mathematischer Aequivalenznachweis, unveraenderte primaere Variablenzuordnung.
Dann gepaarter Vergleich Referenz/Variante auf denselben elf Faellen, gleichem Seed,
gleichen Budgets und vergleichbarer Parallelitaet (z.B. zwei Wellen a 11 Prozesse, je 20 Minuten).
Kein Proof-Logging im Scout. Falls alles offen bleibt, Statistik nur als Diagnose verwenden;
keinen Gewinner allein aus Konfliktrate oder CNF-Groesse ernennen. Weitere Zerlegung erst
mit begruendeter Variablenwahl und vollstaendiger Fallabdeckung.

## Grenzen

Kein neuer Involutionsausschluss. Keine neue Aussage ueber K66 oder globale Symmetriefreiheit.
Dieser Lauf belegt einen funktionierenden Achtstundenbetrieb der reparierten Ueberwachung,
keine Garantie fuer beliebige spaetere Laeufe. Kein automatischer Folgelauf gestartet.
