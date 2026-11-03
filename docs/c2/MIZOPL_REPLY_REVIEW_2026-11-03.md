# Mizopls Antwort und Konsequenzen für unser C2-Projekt

Stand: 3. November 2026. Geprüfter Fremdcommit: [5bae03c494ee69501a6b5c7024a4b86c31c8bec8](https://github.com/mizopl/conway-99-graph/tree/5bae03c494ee69501a6b5c7024a4b86c31c8bec8). Die Antwort wurde am 2. November um 23:49:54 UTC veröffentlicht und am 3. November um 00:50:21 Berliner Zeit im Outlook-Posteingang empfangen. Die Nachricht verweist auf denselben [öffentlichen Kommentar](https://github.com/mizopl/conway-99-graph/issues/1#issuecomment-6591473434).

**Unser Einwand gegen die gleichzeitige Normalisierung von Matching und Randdaten ist bestätigt. Die vorgeschlagene globale Reduktion ist unter zusätzlichen Voraussetzungen korrekt, schließt aber nicht jeden einzelnen Slice mit genau einem Type-I-Block aus. Ein vollständiger C2-Ausschluss folgt aus dem geprüften Stand weiterhin nicht.**

## Was sich durch die Antwort geändert hat

Mizopl erkennt die ungesicherte Fixierung des Randpaares im alten 299-Fälle-Programm an. Dessen Ergebnis gilt nur für die ausgewählte Randkonfiguration. Er führt neue komponentenbasierte Suchprogramme und eine globale Paritätsreduktion an. Die grundsätzliche Reaktion ist fachlich sinnvoll: Eine andere, vollständig begründete Projektion kann einen fehlerhaft normalisierten Suchzweig ersetzen, ohne dessen gesamten Suchraum nachträglich abzuarbeiten.

Die [neue Falltabelle](https://github.com/mizopl/conway-99-graph/blob/5bae03c494ee69501a6b5c7024a4b86c31c8bec8/SIGN_OFF_TABLE.md) unterscheidet den alten bedingten Lauf von der neuen globalen Argumentation. Der [Programmtext des alten Laufs](https://github.com/mizopl/conway-99-graph/blob/5bae03c494ee69501a6b5c7024a4b86c31c8bec8/verify-it-yourself/run_all_299_nullity3_k1.py#L366) fixiert weiterhin `h0 = all_H0[0]` und danach den ersten passenden Partner. Die neue Kennzeichnung repariert seine ursprüngliche Fallüberdeckung nicht.

## Der entscheidende Unterschied zwischen Mail und Lean-Satz

In unserem Modell bezeichnet `s_ij=1` die T-Verbindung der beiden Orbitlinien derselben Zelle `{i,j}`. Diese Einträge bilden einen einfachen ungerichteten Hilfsgraphen auf den sieben Ankerindizes. Sein Grad `k_i=sum(j!=i,s_ij)` ist die Zahl der Type-I-Blöcke in Slice i. Diese Zuordnung war bereits Teil unseres [Modellvertrags](MODEL_CONTRACT.md).

Der tatsächlich vorhandene [Lean-Satz, Zeilen 381–393](https://github.com/mizopl/conway-99-graph/blob/5bae03c494ee69501a6b5c7024a4b86c31c8bec8/verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L381-L393) hat die arithmetische Form:

```text
Für alle i: 0 <= k_i <= 1
und sum_i k_i = 2m
=>
sum_i k_i <= 6 und es gibt mindestens ein i mit k_i = 0.
```

Seine Variablen haben den Typ `Int`. Die Verbindung zwischen diesen Zahlen und konkreten Graph-Slices ist eine zusätzliche mathematische Anwendungsvoraussetzung. Der Satz ist korrekt: Ein Matching auf sieben Punkten lässt mindestens einen Punkt unbedeckt.

Er beweist weder `k_i != 1` für jeden Slice noch `k_i = 0` für alle Slices. Bereits eine einzelne Kante hat die Gradfolge `(1,1,0,0,0,0,0)` und erfüllt seine Voraussetzungen. Das ist ein Gegenbeispiel zur stärkeren **arithmetischen Schlussfolgerung**, kein behaupteter Conway99-Graph und kein Beleg für einen fortsetzbaren fremden Slice.

Auch die Paritätsrechnung in der Mail ist falsch: Sechs ungerade Zahlen plus eine gerade Zahl ergeben eine **gerade** Summe. Der gültige Widerspruch betrifft die Annahme, dass **alle sieben** Grade eins wären.

Die korrekte Nutzung ist eine globale Wurzelwahl: Nach einem belastbaren Ausschluss aller Slices mit mindestens zwei Type-I-Blöcken muss jeder hypothetische C2-Graph einen Slice mit null Type-I-Blöcken besitzen. Eine vollständige Suche über solche Wurzelslices genügt dann für den globalen Ausschluss. Der lokale 299-Orbit-Zweig kann so umgangen werden; seine individuelle Unerfüllbarkeit ist damit nicht bewiesen.

## Welche Voraussetzungen noch geprüft werden müssen

Unser bestätigter Filter erlaubt bisher `k_i <= 2` und höchstens sieben same-cell-T-Kanten. Daraus folgt keine isolierte Wurzel: Ein Siebenerzyklus hat überall Grad zwei.

Für die Verschärfung auf `k_i <= 1`, höchstens drei same-cell-Kanten und mindestens einen Type-I-freien Slice müssen insbesondere die 6 Klassen der Partition `1+1+2+2` und die 56 Klassen von `1+1+4` vollständig ausgeschlossen werden. Dabei sind die wirklichen Projektionsabbildungen, sämtliche zulässigen Zeilen, die verwendeten Stabilisatoren und die überprüfbaren Suchabschlüsse zu verbinden.

Die [neuen Zusammenfassungen](https://github.com/mizopl/conway-99-graph/blob/5bae03c494ee69501a6b5c7024a4b86c31c8bec8/verify-it-yourself/null_ktype1_ge1_unconditional_lego_summary.json) bestehen folgende kleine Konsistenzprüfungen:

- Sechs Einzelprotokolle summieren sich auf 18.259.722 erste und 227.789 zweite Teilbelegungen, jeweils ohne vollständige Lösung.
- Alle 45 Subkegel-IDs und elf unterschiedlichen Zusatzklassen sind vorhanden. Die verzeichneten Klassenlabels decken gemeinsam 0 bis 55 ab; die Summenzähler stimmen.
- Die drei neuen Programme enthalten keine Fixierung `all_H0[0]`.

Das bestätigt die interne Buchführung, nicht die geometrische Vollständigkeit oder die gemeldeten UNSAT-Ergebnisse. Die großen Enumerationen wurden hier nicht wiederholt; auch die neue Lean-Datei wurde nicht kompiliert. Der Satz wurde in seinem tatsächlichen Wortlaut geprüft und seine elementare Aussage unabhängig nachgerechnet.

Die [formale Projektionsregel](https://github.com/mizopl/conway-99-graph/blob/5bae03c494ee69501a6b5c7024a4b86c31c8bec8/verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L1040-L1057) verlangt die Abbildung gültiger Gesamtzustände auf gültige Teilzustände und deren vollständige Kanonisierung ausdrücklich als Voraussetzungen. Ebenso nimmt der [große Schluss-Satz](https://github.com/mizopl/conway-99-graph/blob/5bae03c494ee69501a6b5c7024a4b86c31c8bec8/verify-it-yourself/ChiralNullspaceAndHandshaking.lean#L1464-L1478) weiterhin unter anderem einen separaten Ausschluss der 1+5-Schicht entgegen. Das neue Existenzargument liefert diesen lokalen Allsatz nicht direkt; für seinen Gebrauch muss die Gesamtübertragung die geeignete Wurzel ausdrücklich auswählen.

## Weitere Korrekturen an den Statusangaben

**Unsere Prüfleistung wird zu weit dargestellt.** Die Falltabelle bezeichnet die vollständigen 4+2- und 2+2+2-Ergebnisse als von `@ibenarb` unabhängig reproduziert. Unser [veröffentlichter Bericht vom 1. November](https://github.com/ibenarb/conway99-research/blob/86d3ff8b237894592751451cf44a246ee4ea44cc/docs/c2/SLICE_REVIEW_2026-11-01.md) besagt ausdrücklich, dass diese neuen Suchen nicht vollständig nachgerechnet oder auditiert wurden. Bestätigt sind unter anderem die 3.580 Orbitklassen, notwendige Slice-Identitäten und die Dreifach-Type-I-Paritätsobstruktion. Die weitergehende Zuschreibung ist keine von uns erteilte Bestätigung.

**Die 2.903 Type-I-freien Orbitklassen sind nicht vollständig abgeschlossen.** Die abschließende Beschreibung im neuen JSON behauptet dies, während das gleichzeitig veröffentlichte [Class-6-Ledger](https://github.com/mizopl/conway-99-graph/blob/5bae03c494ee69501a6b5c7024a4b86c31c8bec8/docs/CLASS6_BUNDLE_INDEX_AND_LEDGER.md) nur 270 von 2.670 Class-6-Orbits als erledigt ausweist. Damit bleiben nach dieser Fremdmeldung 2.400 offen. Die 2.903 ergeben sich aus `2670+55+168+10`; die globale Wurzelwahl allein erledigt diese Suchen nicht.

Die als erschöpfend bezeichnete Falltabelle summiert die getrennten lokalen Klassen auf 3.308. Die übrigen 272 Klassen mit negativem K-Eintrag gehören zur bereits bekannten elementaren Nichtnegativitätsprüfung und sollten als eigene Zeile erscheinen. Das ist eine Lücke der Buchführung, kein Nachweis von 272 neuen mathematisch offenen Fällen. Die globale Reduktion der Tabellenzeile C99-09b darf nicht als zusätzliche disjunkte Klasse mitgezählt werden.

Die in der Mail verlinkte Datei unter `lean/Conway99/` war am geprüften Commit nicht vorhanden. Der tatsächliche Beleg liegt unter `verify-it-yourself/`; die Links dieses Berichts benutzen diesen Pfad.

## Was wir belastbar übernehmen können

### Globale Reduktion als bedingtes Lemma

Die Matching-Parität ist bestätigt und als **bedingter** Zusatz im Modellvertrag dokumentiert. Sie eröffnet einen sinnvollen alternativen Abschlussweg, sobald der Ausschluss aller Grad-zwei-Slices unabhängig abgesichert ist. Bis dahin bleibt unser wirksamer Filter unverändert.

Eine spätere Festlegung der isolierten Wurzel auf einen bestimmten Index muss den gesamten Zustand mittransportieren: Q, T, D, Supportmarkierungen und übrige Randdaten. Die Existenz einer geeigneten Wurzel allein erlaubt keine zweite unabhängige Normalisierung bereits festgelegter T20-Supports.

### Komponenten und Restkapazitäten

Die standardisierten Schnittbedingungen zwischen Komponenten und die Verteilung ihrer Spaltensummen waren bereits in unserem Audit vom 27. Oktober enthalten. Sie sind kein neuer zusätzlicher Ausschluss. Komponenten teilen dieselben Spalten und Kapazitäten; isolierte erfüllbare Komponenten müssen weiterhin gemeinsam kompatibel sein.

Aus `XXᵀ=9I+J-M`, Zeilensumme zehn und voller Spaltensumme zwei folgt für eine Komponente mit 2k Zeilen:

```text
n0+n1+n2 = 60
n1+2n2 = 20k
n1+4n2 = 4k(k+4)

n2 = 2k(k-1), n1 = 4k(6-k), n0 = 2(6-k)(5-k).
```

Für k=4 ergibt dies `(n2,n1,n0)=(24,32,4)`. Die Rechnung ist eine überprüfte Folgerung der notwendigen Slice-Gleichungen.

Der neue [Restkapazitätsfilter](https://github.com/mizopl/conway-99-graph/blob/5bae03c494ee69501a6b5c7024a4b86c31c8bec8/verify-it-yourself/run_rem11_nullity4_k2_114_8dom_cpu.py#L43-L82) ist als allgemeine Suchmethode sinnvoll: Jede Spalte muss nach den bisher gesetzten Einsen noch ausreichend viele **verschiedene verbleibende Zeilenbereiche** haben, die dort eine Eins liefern könnten. Kandidaten derselben Zeile dürfen dabei nicht als mehrere unabhängige Beiträge gezählt werden.

Formal sei p(c) die aktuelle Belegung und a(c) die Zahl verbleibender Zeilenbereiche, die Spalte c überhaupt erreichen. Eine echte Fortsetzung zur Spaltensumme zwei erfordert `p(c)+a(c)>=2`. Die Masken `av1` und `av2` codieren Erreichbarkeit aus mindestens einem beziehungsweise zwei verschiedenen Bereichen. Der Filter überschätzt mögliche gemeinsame Fortsetzungen, was für einen notwendigen Abschneidetest sicher ist. Er beweist bei Bestehen keine Fortsetzbarkeit.

Die eigenständige Prüfung erfasst 2.304 Zwei-Spalten-/Zwei-Bereich-Instanzen und 196.608 Ein-Spalten-/Acht-Bereich-Instanzen ohne falschen Ausschluss. Sie prüft dieses Prinzip, nicht sämtliche Datenstrukturen oder Symmetriereduktionen des fremden Programms. Eine Beschleunigung unserer SAT-Pipeline ist damit nicht gemessen.

### Fallbuchführung und Beweiskette

Für jede übernommene Aussage müssen Modell, Quantoren, zusätzliche Voraussetzungen, abgedeckter Fallraum, konkrete Übertragung und Prüfergebnis zusammenstehen. Bei gemeinsamen Daten zählt die diagonale Gruppenwirkung; nach Fixierung eines Objekts darf nur dessen tatsächlicher Stabilisator für die Fortsetzung verwendet werden.

Statusmeldungen sollten aus überprüften Resultaten entstehen. In zwei neuen [Programmen](https://github.com/mizopl/conway-99-graph/blob/5bae03c494ee69501a6b5c7024a4b86c31c8bec8/verify-it-yourself/run_all_6_nullity5_k2_1122_cpu.py#L254-L263) wird die abschließende PASS-/UNSAT-Zeile unabhängig vom ausgegebenen Lösungszähler gedruckt; dies ist auch im [Subkegelprogramm](https://github.com/mizopl/conway-99-graph/blob/5bae03c494ee69501a6b5c7024a4b86c31c8bec8/verify-it-yourself/run_all_56_nullity4_k2_114_subcones_cpu.py#L954-L957) der Fall. Das widerlegt die gespeicherten Nullresultate nicht, macht aber deutlich, warum eine Erfolgsmeldung allein kein Zertifikat ist.

## Bedeutung für unsere Forschung und nächste Priorität

Der konkrete Wert unseres Reviews ist durch die öffentliche Korrektur dokumentiert. Unsere vollständigen 99-Knoten-Modelle, semantischen CNF-Audits und unabhängig geprüften Ausschlusszertifikate bleiben eine eigenständige Kontrolllinie. Ihre Neuheit gegenüber fremden Teilresultaten muss über eine tatsächliche Fallabbildung beurteilt werden; Slice-Orbitzahlen und T16/T18/T20-Supportzahlen lassen sich nicht direkt vergleichen.

Der lokale Status vom 3. November, 07:14:35 UTC, weist T20-Typen 1/1 und 0/0 als laufend und sechs weitere Typen als wartend aus. Typ 1/0 bleibt zertifiziert ausgeschlossen. Der allgemeine C2-Abschluss und die vollständige mathematische Übertragung bleiben offen. Laufende Berechnungen wurden für diesen Review nicht verändert.

Priorität vor einer stärkeren Filterübernahme hat ein gezielter Audit der 62 Grad-zwei-Slice-Klassen samt Projektion und Stabilisatoren. Erst danach lässt sich eine gemeinsame Wurzel-/Supportnormalisierung und deren tatsächlicher Nutzen für unsere Restfälle messen. Gegenwärtig rechtfertigt die Antwort **keinen weiteren T20-Fallausschluss**. Diese Dokumentation sendet keine neue Antwort an Mizopl.

## Nachrechenbare Belege

- [Eigenständiger kleiner Prüfer](../../verification/c2_slice/audit_reply_20261103.py), Python-Standardbibliothek.
- [Ergebnisse einschließlich Konsistenzprüfung des fremden JSON](../../results/c2/2026-11-03/reply_audit.json).
- [Unveränderliche Quellen und SHA-256-Prüfsummen](../../results/c2/2026-11-03/source_manifest.json).
- [Prüfanleitung](../../verification/c2_slice/REPLY_AUDIT_2026-11-03.md).

Private Mailheader, Antworttokens und Benachrichtigungslinks sind nicht Bestandteil dieser Veröffentlichung.
