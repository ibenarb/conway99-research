# Involutionen in Conway99: Zwischenbericht und Suchstrategie

Stand: 19. September 2026. Gegenstand ausschließlich C2 auf dem Ryzen.
Belegstand: Git-Commit `1dc3d773254cb914f49a067d298178a720ff6f72`.

## 1. Ergebnis und Reichweite

**Wir haben ein kontrolliertes vollständiges Involutionsmodell und eine
reproduzierbare Suchinfrastruktur, aber noch keinen der elf Produktionsfälle
entschieden und keinen neuen Involutionsausschluss bewiesen.** Ein Timeout
belegt weder Existenz noch Nichtexistenz. Auch ein C2-Ausschluss wäre für sich
noch kein vollständiger Symmetrieausschluss und kein Nichtexistenzbeweis.

Die Vollständigkeit verwendet den im Literaturabgleich vom 13. September
zitierten Satz über genau einen Fixpunkt jeder Involution. Dessen Originalbeweis
wurde hier nicht neu auditiert. Der damalige Abgleich erkennt bei Thakkar die
84-Knoten-Modellierung und Automorphismenmodellierung als Vorarbeiten an; er
belegt keinen vollständigen C2-Ausschluss bei 99 Knoten. Das ist eine datierte
Projektbewertung, keine erneute Literaturrecherche oder pauschale Bewertung des
fremden Manuskripts. Neuheit der Grundmodellierung wird ausdrücklich nicht beansprucht.

## 2. Mathematische Grundlage

Der eindeutige Fixpunkt o hat 14 Nachbarn, die sieben disjunkte Kanten bilden.
Die 84 Außenknoten sind durch die nichtgematchten Paare dieser Nachbarn eindeutig
bezeichnet. Die Involution vertauscht die Endpunkte jeder Rahmenkante und wirkt
damit fest auf den Außenlabels. Kein Außenknoten ist zu seinem Partner benachbart.

Für die Außenadjazenz M, die Labelinzidenz R und das Rahmenmatching K gelten:

    E1: M 1 = 12 1
    E2: M R = 2 J - R(K + I)
    E3: M² + M = 12 I + 2 J - R Rᵀ.

Mit Symmetrie, Binärität, Nulldiagonale und vorgeschriebener Involution sind diese
Bedingungen nach der dokumentierten Herleitung notwendig und hinreichend.
Die Paarordnung liefert M=[[B,C],[C,B]], also 1722 primäre Kantenbits.

Zwei verschiedene Matchings dürfen nicht verwechselt werden:

- **F auf 42 Involutionspaaren:** Doppelverbindungen B_ij=C_ij=1 bilden ein
  perfektes Matching. Der übrige Träger H ist 10-regulär. Mit Q=B+C und D=B−C
  gelten Q=H+2F und die exakte Kopplung
  (Q_ij,D_ij)∈{(0,0),(1,1),(1,−1),(2,0)}. Q allein genügt nicht.
- **L auf zwölf Außenknoten einer Rahmennachbarschaft:** Relativ zum dort festen
  Paarmatching P klassifizieren die alternierenden Komponenten von P∪L die
  elf verwendeten Fälle durch Partitionen von 6. Alle 10395 beschrifteten
  Matchings wurden mit expliziten Transportern gegen diese Orbitabdeckung geprüft.
  Die Fälle sind keine gleich großen Anteile des gesamten Lösungsraums.

Die F-Bedingung ist keine ungenutzte Entdeckung: Ihre Ergänzung in der bisherigen
Referenzproduktion lieferte eine byteidentische CNF. Bloßes erneutes Hinzufügen
dieser Bedingung ist daher kein sinnvoller neuer Versuch.

## 3. Was implementiert und gemessen wurde

Der Referenzencoder besitzt schriftliche Induktionsargumente und kleine
unabhängige Projektions-/Graphkontrollen. Sie ersetzen keine Produktionsbeweise.
Die Referenz-CNF hat 570171 Variablen und 1990821 Klauseln. Eine Variante ersetzt
nur die E3-Zähler durch einen Totalizer: 534135 Variablen, 1921773 Klauseln.
Primärvariablen und elf Fallbedingungen bleiben vergleichbar.

| Experiment | Umfang | Ergebnis |
|---|---|---|
| Referenz, Matching-Fälle | 11 × 8 Stunden, etwa 88 CPU-h | Alle offen |
| Referenz/Totalizer A/B | 22 × 20 Minuten, etwa 7.34 CPU-h | Alle offen |
| Totalizer, ursprünglicher Langlauf | Abbruch nach 12 h 32 min | Guard-Schreibfehler; kein abgeschlossener Fall |
| Totalizer, korrigierter Langlauf | 11 × 34 Stunden, 373.979 CPU-h | Alle offen, regulär beendet |

Im kurzen A/B-Vergleich sank der mediane Spitzen-RAM von 746.62 auf 558.40 MiB,
also um etwa 25 %. Ein Geschwindigkeitsvorteil ist damit nicht bewiesen: alle
Laufzeiten sind durch das Budget zensiert, nur ein Seed und feste Wellenreihenfolge.
Der 34h-Lauf ist kein gleich budgetierter Vergleich zum 8h-Referenzlauf.

Im 34h-Lauf: 634325720 Konflikte, median 96.95 % Suchzeit; CPU-Zeit nahezu gleich
Solver-Wallzeit, 596–797 MiB RSS je Prozess. Keine unterbrochenen Jobs oder
Beweisdateien. Acht Fälle reduzierten ihre Restvariablen in den letzten zehn
Stunden um weniger als 2 %, drei stärker. Das zeigt Vereinfachung, aber keine
messbare Beweisnähe. Viele Restvariablen sind Hilfsvariablen; Konfliktzahlen
zählen weder ausgeschlossene Graphen noch vergleichbare Arbeit verschiedener Encoder.

Die Betriebsprobleme sind getrennt zu bewerten: Unbegrenzte LRAT-Ausgabe führte
früher zum vollen Windows-Datenträger; Scouts erzeugen jetzt keine Beweisdateien.
Der Guard wurde nach mehreren Dateizugriffsfehlern korrigiert und unter echten
Windows-Sperren getestet. Der 34h-Lauf besteht als Betriebserfahrung, nicht als
allgemeine Zuverlässigkeitsgarantie. Es gibt keinen Solver-Checkpoint zum Fortsetzen.

## 4. Verfeinerte Strategie: erst Strukturwirkung, dann lange Suche

### A — Kurze Folgeklauseln auf Kantenvariablen (erste Priorität)

Für verschiedene Außenknoten x,y mit genau einem gemeinsamen Rahmenlabel ist
M_xy + Σ_z M_xz M_yz = 1. Daraus folgt für jeden weiteren Außenknoten z:

    ¬M_xy ∨ ¬M_xz ∨ ¬M_yz.

Zwei verschiedene äußere gemeinsame Nachbarn liefern entsprechende vierstellige
Verbotsklauseln. Gewichte und identische Literale durch die Involution müssen
korrekt normalisiert werden. Diese Klauseln sind logische Folgerungen; ihr
explizites Auftreten könnte kürzere Propagationswege schaffen oder nur Ballast sein.

**Gate:** Zählen, normalisieren, Duplikate und Subsumption gegen vorhandene
Klauseln prüfen. An vorab festgelegten gleichen Primärbelegungen die vollständige
Unit-Propagation vergleichen: zusätzliche Primärfixierungen, Widersprüche,
Zeit und Speicher. Kein Schluss aus der bloßen Klauselanzahl. Erst bei plausibler
Wirkung ein A/B-Pilot mit elf Fällen je Variante und je 20 Minuten; insgesamt
etwa 40 Minuten Suche. Einen Vorteil danach an zurückgehaltenen Belegungen bzw.
weiteren Seeds und umgekehrter Wellenreihenfolge prüfen. Vorbereitung: grob einige
Arbeitsstunden, abhängig vom Klauselumfang. Kein neuer Graphsatz beansprucht.

### B — Gekoppelte Nachbarschaften statt isolierter Matching-Typen

Das bisherige L fixiert nur eine Nachbarschaft. Zweites Matching oder kompatible
Zeilenmuster einer weiteren Rahmennachbarschaft könnten stärkere Kopplungen
sichtbar machen. Zuerst lokale Musterzahlen und Widersprüche unter E1/E2/E3
ermitteln; anschließend erst Teilprobleme erzeugen.

**Pflicht:** Überdeckung aller Lösungen beweisen. Weitere Orbitreduktion nur
unter dem Stabilisator des bereits fixierten Rahmens UND des ersten Matchings.
Keine unabhängige Standardisierung zweier Matchings ohne gemeinsamen Transporter.
**Risiko:** kombinatorische Explosion. Zunächst auf 15–30 Minuten Zählzeit begrenzen;
anschließend höchstens eine Stunde Scout. Implementierung voraussichtlich ein bis
zwei Arbeitstage; keine Schätzung der Gesamtlösezeit möglich.

### C — Lookahead und vollständiges Cubing auf Primärvariablen

Variablen anhand gemessener beidseitiger Propagation wählen, nicht anhand von
Nummern oder Hilfsvariablenzählungen. Kleine Teilbäume aufbauen, beide Zweige
x=0 und x=1 erhalten und nachweisbar vollständig buchen. Bereits entschiedene
Blätter separat zur Zertifizierung vormerken. Die elf Fälle bleiben die Wurzeln.

**Gate:** Vorheriges Spine-Problem aus K66 gezielt vermeiden: Verhältnis von
Seitenastabschlüssen, Tiefe des dominanten Astes, Größe der offenen Frontier und
CPU-Verbrauch messen. Ausgewogene unmittelbare Propagation garantiert keine
balancierte Schwierigkeit. Ein 30–60-Minuten-Pilot muss mehr zeigen als viele
triviale Seitenäste; sonst Splitkriterium ändern. Aufwand grob ein Arbeitstag.
Keine Timeouts als geschlossene Blätter zählen; kein gelerntes Wissen unkontrolliert
zwischen unterschiedlich angenommenen Fällen übertragen.

### D — Exakte Paar-/Vorzeichenformulierung als alternativer Forschungsweg

Die Spezifikation liefert neben Q auch D mit DV=0,
D²+D=12I−VVᵀ und Spektrum {0^7,3^20,(−4)^15}. Untersuchen, ob die lokale
Vorzeichenkompatibilität und die gemeinsame Realisierbarkeit von H,F,D eine
bessere Variablenwahl, lokale Obstruktionen oder einen eigenen Constraint-Ansatz
ermöglichen. Ein Spektrum allein ist keine hinreichende Ersatzbedingung.

**Pflicht:** feste W,V-Labels und exakte Q/D-Kopplung erhalten; keine willkürliche
S42-Umbenennung zur Normierung von F. Eine notwendige Relaxation darf nur bei
bewiesener UNSAT zum Ausschluss dienen; ihre SAT-Ausgabe muss ins volle Modell
gehoben werden. Vor Vollimplementierung ein bis zwei Arbeitstage algebraische
und kleine kombinatorische Vorprüfung. Suchzeit und Gewinn derzeit unbekannt.

**Reihenfolge:** A zuerst; bei geringem Nutzen B oder C nach lokalen Messungen.
D als eigenständige Alternative vom Reviewer bewerten lassen. Keine automatische
erneute 34h-Kampagne. Lange Läufe erst bei einem begründeten Vorteil; auch dann
keine Erfolgsgarantie. Scout und Zertifizierung bleiben getrennt: UNSAT-Meldungen
werden erst mit passendem CNF-Beweis, unabhängiger Prüfung und vollständiger
Fallabdeckung zu einem Ausschluss. Proof-Erzeugung bekommt ein eigenes, explizites
Speicherbudget auf Windows und Linux.

## 5. Prüfbarkeit

Alle nachfolgenden Pfade sind am genannten Belegcommit eingefroren:

- `docs/c2_spec_20260913/{SPEZIFIKATION,LITERATURABGLEICH}.md`
- `src/c2_matching_20260915/THEOREM.md`, `results/c2_matching_20260915/cover.json`
- `docs/c2_reference_20260913/README.md`, `results/c2_reference_20260913/controls.json`
- `src/c2_counter_ab_20260916/THEOREM.md`
- `results/c2_matching_20260916/eight_hour/`
- `results/c2_counter_ab_20260917/`
- `results/c2_totalizer_34h_20260919/` (Original-ZIP, Auswerteskript, Kennzahlen, Bericht)
- `src/c2_guard_fix_20260917/` und `src/c2_totalizer_34h_20260917/`

Die Ergebnisarchive enthalten Logs und Metadaten, nicht die Produktions-CNFs oder
Solver-Binärdateien. Gespeicherte Hashfelder sind keine hier erneut ausgeführten
Byteprüfungen dieser fehlenden Dateien. Die 34h-Archivkonsistenz wurde unabhängig
gegen elf Logs/Einzelergebnisse geprüft; ein formaler UNSAT-Nachweis liegt nicht vor.
