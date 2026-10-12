# C4 und Profile46: Formelbindung, Vollständigkeit und übernommene Zertifikate

Stand 12.10.2026. Fortsetzung nach Forschungscommit
`7dbacd7eed56e2bf73b3aa5f2648f00e5484adfa`. Der darauf bezogene erste Reviewerauftrag
ist laut Ralph seit 14:43 Uhr in Arbeit; diese Fortsetzung verändert seinen
festgeschriebenen Ausgangsstand nicht.

## 1. Ergebnis und Prüfgrenze

Die bisher offenen **Formel-, Transport- und Censusbindungen** der beiden Filter
C4 und Profile46 sind jetzt ausgearbeitet und vollständig rechnerisch geprüft.
Die mathematische Encoderadäquanz der konkret verwendeten Basis ist separat in
[ENCODER_ADAEQUANZ.md](ENCODER_ADAEQUANZ.md) hergeleitet. Ein unabhängiges Review
dieser neuen Ausarbeitung steht aus.

Die historischen UNSAT-Prüfungen werden weiterhin als frühere Ergebnisse
übernommen. In diesem Schritt wurden weder SAT-Solver noch Beweischecker gestartet.
Die 2.170 großen Einzelbeweise lagen nicht im kompakten Export und wurden nicht
erneut gelesen. Der mitgelieferte C4-Beweis wurde dagegen vollständig dekomprimiert
und gehasht, aber nicht erneut durch drat-trim geprüft.

**Bedingte Schlussfolgerung:** Unter Anerkennung der angegebenen historischen
Checkerprüfungen und der hier ausgearbeiteten Encoderadäquanz sind C4-Freiheit und
der Ausschluss des gesamten Profile46-Zweigs als Censusfilter gerechtfertigt.
Die Filter hängen nicht zirkulär voneinander oder vom späteren Profile346-Ausschluss ab.

## 2. Neu rekonstruierte Formeln

| Formel | Exakter Aufbau | SHA-256 |
|---|---|---|
| $F_0$ | Uneingeschränkte C2-Basis | `7c105a67b0f7865f2ceec085ac9e5017213208e657e728381406323052acf3dd` |
| $F_{C4}$ | $F_0$ plus acht positive Pfeil-Units | `9c38a75f8d9495dedea857f527f2fca5a2e860732eb8e3674356755eca0e3877` |
| $F_{46}$ | $F_0$ plus 336 Gradklauseln | `5b251b4832904a3bd2ce7d804508e380794444f19c70ba8b26903cb1b4b02859` |
| $F_{346}$ | $F_0$ plus 196 Gradklauseln | `33fc424d5e0ce00179a5abbde52c56b40e4e1fcbc272c36d595ef29354e3b030` |

Die Variablenabbildung hat SHA-256
`cd78938cc0fd6c4b2239ddd2b67054e1ea754b41be4dc6eeaef6849b97e0bc0e`.
Die vier Encoderquellen des Profile46-Pakets stimmen byteidentisch mit denen der
späteren Rest218-Basis überein. Die Rekonstruktion reproduziert alle fünf Hashes.

Insbesondere enthält $F_{C4}$ **keine** Profile46- oder Profile346-Einschränkung.
Das C4-Lemma kann daher auf das vollständige C2-Modell angewandt werden, sobald
seine historische UNSAT-Prüfung und ENC0 zugrunde gelegt werden.

## 3. C4-Lemma und semantischer Transport

Die acht Units stehen für

$$0\leftrightarrow1\leftrightarrow2\leftrightarrow3\leftrightarrow0.$$

In der tatsächlich verwendeten Reihenfolge lauten sie
`1, 159, 862, 427, 1288, 672, 1020, 1533`.
Der neue Audit rekonstruiert diese Variablennummern unabhängig aus der erzeugten
Label-/Primärvariablenabbildung und vergleicht sie mit den ursprünglichen Units.

**Transportargument.** Enthielte der gegenseitige Ankergraph einer Modelllösung
einen Vierzyklus, könnte eine Paarpermutation dessen zyklisch geordnete Knoten
auf $0,1,2,3$ abbilden. Nach L5 erhält diese Umbenennung E1–E3. ENC0 würde daraus
eine erfüllende Belegung von $F_{C4}$ erzeugen. Dies widerspricht dem übernommenen
UNSAT-Zertifikat. Der gegenseitige Ankergraph ist daher C4-frei.

Es gibt $\binom74\cdot3=105$ verschiedene Vierzyklen auf sieben beschrifteten
Knoten. Die 5.040 Paarpermutationen liefern genau diese 105 negativen
Acht-Literal-Klauseln. Der Audit verglich die gesamte Menge mit `work/coverage.json`
und prüfte jede dort gespeicherte Transportpermutation. Eine syntaktische
Permutation der Totalizer-Hilfsvariablen ist für dieses Argument nicht erforderlich.

Der C4-Checkerbeleg meldet `s VERIFIED`, Rückgabecode 0. Sein kompletter Loghash
und sein Operationsergebnis passen zum Beleg. Der Proof wurde aus dem ursprünglichen
Installer gelesen und vollständig dekomprimiert:

| Gegenstand | Größe / SHA-256 |
|---|---|
| Rohbeweis | 137.404.285 Bytes |
| Komprimierter Beweis | `00c83798645d151c85ca0a6518030b716612f2171e04c58c0c60f73e8569d426` |
| Rohbeweis | `ef350125025ee174abaf627042274ec8aa84e62f8185877d501b09926617c820` |

Beide Hashes stimmen neu berechnet mit dem historischen Beleg überein.
Das Lesen und Hashen ist ausdrücklich kein erneuter Beweischecker-Lauf.

## 4. Vollständigkeit der Profile46-Fallmenge

Nach dem C4-Lemma verbleiben im Zweig $d(p)\in\{4,6\}$ genau die C4-freien
Pfeilgraphen mit diesen Ausgraden. Aus dem ursprünglichen Export wurden alle
2.170 Vertreter und ihre 42 vollständigen Pfeil-Units gelesen. Für jeden wurden
Gradbedingungen, Schleifenfreiheit, C4-Freiheit, Code und Unitzuordnung geprüft.

Der neue Isomorphieprüfer aus dem Profile346-Audit berechnete alle
Automorphismenordnungen unabhängig neu und schloss isomorphe Dubletten aus.
Er untersuchte 200.142 farbverträgliche Knotenordnungen. Die Bahngrößensumme ist
10.690.440.

Der neue Zeilenaufzähler wurde auf die acht Gradmultiplizitäten für Grade 4 und 6
angewandt. Die Rekursion ist dieselbe bereits dokumentierte vollständige
Zeilenmaskenaufzählung mit sicherer C4-Präfixverwerfung; eine Kanonisierung oder
historische Aufzählungsdateien werden nicht verwendet. Ergebnis:

| Anzahl Anker mit Grad 6 | Beschriftete C4-freie Pfeilgraphen |
|---:|---:|
| 0 | 10.448.730 |
| 1 | 241.710 |
| 2 bis 7 | jeweils 0 |
| Summe | 10.690.440 |

Wie im [Censusbeweis](../c2_completeness_20261012/CENSUS_VOLLSTAENDIGKEIT.md)
impliziert die Übereinstimmung von unabhängig gezählter Gesamtmenge und
Bahngrößensumme die vollständige Abdeckung. Genau die 2.170 vorliegenden Bahnen
müssen daher im Profile46-Zweig ausgeschlossen werden.

## 5. Alle 2.170 Formel- und Belegzuordnungen

Für jeden Index $i=0,\ldots,2169$ wurden folgende Verbindungen geprüft:

1. Vertretercode und vollständige signierte Belegung aller 42 Pfeile stimmen überein.
2. Die Formel ist exakt $F_{46}$ plus diese 42 Einheitsklauseln. Ihre rekonstruierte
   SHA-256-Summe stimmt mit `formula.json` und dem Eintrag in `work/round.json` überein.
3. Solver- und Checkerbefehle verweisen auf genau die zugehörigen Formel-/Beweispfade.
4. Beide Logs haben die angegebenen Hashes; die gesonderten `result.json`-Belege
   stimmen vollständig mit den im Rundenergebnis eingebetteten Datensätzen überein.
5. Jeder Solverbeleg enthält `s UNSATISFIABLE`, Rückgabecode 20, ohne Abbruchgrund.
   Jeder Checkerbeleg enthält `s VERIFIED`, Rückgabecode 0, ohne Abbruchgrund.
6. Solverausgabehash, gespeicherter Rohbeweishash und Rohhash des Archivbelegs stimmen
   überein. Der Archivpfad gehört zu demselben Fall.

Alle 2.170 Prüfungen waren erfolgreich. Die Hashrekonstruktion verwendet einen
SHA-256-Zustand nach der gemeinsamen angepassten DIMACS-Kopfzeile und dem
unveränderten Basisklauselkörper; für jeden Fall wird dieser Zustand kopiert und
um seine Units ergänzt. Das ist derselbe Bytehash wie bei vollständiger Erzeugung
jeder Datei, ohne die gemeinsame Basis 2.170-mal auf Platte zu schreiben.

Die [Fallzuordnung](../../results/c2_filter_audit_20261012/profile46_case_bindings.tsv)
enthält für jeden Index den Code, Formelhash, Rohbeweishash, komprimierten
Beweishash und Checkerloghash. Ihre SHA-256-Summe ist
`c106e74e6c0250ae483dcf4ed23c093af11e8172f7ce0e1c467c7e44e50c3c3b`.

**Grenze:** Die komprimierten Einzelbeweise verbleiben laut den historischen
Archivbelegen auf Office. Ihre tatsächlichen heutigen Bytes wurden hier nicht
geprüft. Die neue Prüfung bestätigt vollständige und konsistente historische
Belegverknüpfungen; sie ersetzt die frühere DRAT-Verifikation nicht.

## 6. Verbindung mit dem Profile346-Census

Das ursprüngliche `profile46_dependency.json` nennt den Abschlussexport und vier
Dateihashes. Der neue Audit bestätigte den Exporthash sowie die Hashes von
`work/round.json`, `work/preflight.json`, `work/coverage.json` und
`work/c4_certificate.json` gegen genau diesen Export.

Damit ergibt sich ohne Zirkelschluss:

- ENC0 und der übernommene C4-Beweis schließen gegenseitige Vierzyklen aus.
- Die neu bestätigte vollständige Profile46-Fallmenge und ihre übernommenen,
  jetzt vollständig zugeordneten Zertifikate schließen alle Grade ausschließlich
  aus $\{4,6\}$ aus.
- Im Zweig $F_{346}$ muss deshalb mindestens ein Anker Grad 3 haben; dessen
  gegenseitiger Ankergraph ist C4-frei.
- Genau diese Domäne wird vom bereits neu vollständig geprüften Profile346-Census
  mit 7.388.648 Vertretern erfasst.

Dies begründet die beiden Censusfilter unter den angegebenen Zertifikatsprämissen.
Es schließt noch nicht die gesamte weitere Coverage-Kette bis Rest234691/Rest218
und erst recht nicht die niedrigen Ankergrade aus.

## 7. Quellen, Wiederholung und nächste Pflicht

Prüfprogramm: [audit_filters.py](../../src/c2_filter_audit_20261012/audit_filters.py).
Gesamtergebnis: [filter_audit.json](../../results/c2_filter_audit_20261012/filter_audit.json).
Rechenprotokoll: [filter_audit.log](../../results/c2_filter_audit_20261012/filter_audit.log).
Der neue Aufzähler steht in
[count46_independent.cpp](../../src/c2_filter_audit_20261012/count46_independent.cpp).

Benötigte historische Eingaben:

- `C2_Profile46Cert_1.0.0_final_results.tar.gz`, SHA-256
  `6ca9a5c2a34d443d1a7d58e6d907a2ab42567d5dcc8ad4bfb747a82f05141b14`;
- `Conway99_C2_Profile46Cert_1.0.0.pyz`, SHA-256
  `43f20c83b6031bcdbc92401883e80dbab1ec326c109d68aeb94f7e745367a8a3`;
- die unveränderten Quellkopien und der Profile346-Abhängigkeitsbeleg im Repository.

Die Programme werden mit Python ohne deaktivierte Assertions und g++ ausgeführt;
Argumente stehen in `--help`. Es sind keine Befehle an Ryzen oder Office erforderlich.
Dauerhafte öffentliche Downloadadressen der großen historischen Eingaben und der
2.170 Beweise müssen vor dem Publikationsrelease ergänzt werden.

Die nächste eigene Beweispflicht ist die exakte Verbindung der Generalize-, One3-,
Generalize2- und Two3-Muster mit dem Profile346-Census: Unterformeln, Variablenabbildung,
semantischer Transport und vollständige Komplementmengen. Der neue Audit beansprucht
für diese späteren Stufen noch keine zusätzliche Verifikation.
