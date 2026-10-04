# Vollständiger Reviewertext: Abgleich und Entscheidungsvorschlag V3

04.10.2026, Nachtrag zum Abgleich des Prüfpakets. Status: Empfehlung, kein Produktionslauf freigegeben oder gestartet.

## Quellen und zeitliche Einordnung

Der nachgereichte Text ist byteidentisch unter [7d456a57cc98d1c04be2dc5a60cd989ee0bf4c6b](https://github.com/ibenarb/conway99-research/tree/7d456a57cc98d1c04be2dc5a60cd989ee0bf4c6b/docs/reviews/20261004_root8105_text) archiviert, Zweig `reviews/20261004-root8105-claude-text`. Er besteht aus Erstbericht und zwei nachfolgenden Aktualisierungen. Seine älteren Zahlen dürfen nicht gegen die spätere Auswertung ausgespielt oder mit ihr vermischt werden.

Autoritativer letzter Stand im Eingang:128 ausgewertete Roots, typgewichtete Schätzung ca.4,676Mrd. erste Kinder,33 BvLS-Präfixtests mit echter Paarverletzungs-Negativkontrolle, drei Tiefe2-Proben und gekoppelte Sternsysteme im allgemeinen DP. Das stimmt mit dem zuvor gelieferten ZIP und unserem Abgleich bei Commit4b5cebe9e6256a12f232384c5ef6509e01d02d7b überein. Insbesondere gelten die frühen Zahlen24Roots/1,4Mrd./20Kontrollen nicht mehr als letzter Ergebnisstand.

Der neue Text enthält zusätzliche strategische Argumente und Filter, die im ZIP nur teilweise oder nicht erläutert waren. Unsere bereits ausgeführten Reproduktionen bleiben in REPRODUCTION_SUMMARY.json nachweisbar; sie werden durch das Lesen des Textes nicht zu weiteren Reproduktionen.

## 1. Übereinstimmung und eigene Planänderung

Die Hauptentscheidung ist jetzt klar: Keine sofortige vollständige Ganzzeilen-Frontier und keine Entwicklung eines aufwendigen kanonischen Elternkriteriums als erster Schritt. Exakte Breitenzählung, echte Modellkontrollen und Kostenproben haben Vorrang. Der ursprüngliche32-Root/480CPUh-Plan bleibt zurückgezogen.

Der Reviewer bestätigt unseren Modellabgleich: L-Zeugen sind nur automatisch für L positiv, nicht für F. Ihre lokale Isolation spielt für die Positivgarantie keine Rolle. BvLS liefert eine größere echte SRG-Kontrolle des parametrisierten Modells, aber die Tests mit fest vorgegebenen Kanten sind keine Messung freier Completion-Leistung.

Die Erstberichtsempfehlung F_all vollständig zu verwerfen geht mir jedoch zu weit. Ein berichtetes60s-UNKNOWN eines Completers belegt nicht, dass jeder Einsatz auf ausgewählten Teilzuständen unwirtschaftlich wäre. Billige Filter zuerst; anschließend gezielter Vergleich nach nachgewiesenen Einsparungen. Nicht F_all zum Pflichtaufruf jedes Knotens machen.

## 2. Neues starkes Argument: Symmetrie innerhalb einer festen Root

Fixiert sind die Rollen x,u und eine konkrete Rootzeile r. Dann muss jede zulässige Isomorphie zwischen Teilzuständen derselben Root die Rootzeile erhalten. Sie gehört zum Stabilisator von r in G_u. Ein Orbit enthält daher höchstens |Aut(r)| Zustände. Bei6722 von8105 Roots ist dieser Stabilisator trivial.

Wenn genau eine deterministisch aus dem aktuellen Zustand gewählte Zielzeile erweitert und jede Zeilenbelegung nur einmal erzeugt wird, besitzt jeder beschriftete erreichte Zustand einen eindeutigen Baupfad: Die erste Zielwahl ist fest, ihre Zeile ist im Endzustand ablesbar, und induktiv ist auch jede weitere Wahl festgelegt. Diese Aussage setzt eine zustandsbasierte feste Regel ohne wechselnden versteckten Zufallszustand voraus.

**Folgerung:** Im bisherigen fest gerooteten Modell lässt globale Isomorphiededuplizierung bei den meisten Roots keinen großen Gewinn erwarten. Für die neue Ein-Ziel-Regel muss man nicht erneut Pfadduplikate erzeugen, um sie nachher teuer zu beseitigen. Damit verliert meine frühere Priorität vollständiger Schichtdeduplizierung zusätzlich an Gewicht.

Für konkrete Orbitreduktion von Erweiterungen einer ausgewählten Zielzeile ist deren Erhaltung zu beachten: entweder Stabilisator des Paares (Elternzustand,Zielzeile) oder eine nachgewiesen äquivariante Regel. Nicht ungeprüft den gesamten Elternstabilisator als auf der fixierten Zielprojektion wirkend annehmen.

Grenzen: Die Gruppenabschätzung gilt für diese Markierungen und diesen Zustandsraum. Sie schließt weder andere Darstellungen, andere Zerlegungen noch Umrootung aus.99×84=8316 zählt geordnete Nichtnachbarpaare in einem vollständigen SRG, nicht garantiert8316 verschiedene isomorphe Suchfälle oder einen sicher erreichbaren Speedup dieses Faktors. Der Satz „einzige große Symmetrie-Ersparnis“ ist deshalb zu absolut.

## 3. Zwei sinnvolle neue notwendige Filter

### Label-Disjunktheit

Sind v,w beide Nachbarn einer gebauten Zeile u und besitzen sie einen gemeinsamen Bordervertex c, dann darf v–w keine Kante sein: Als adjazente Vertices hätten sie mit u und c zwei verschiedene gemeinsame Nachbarn, im SRG ist für eine Kante aber genau einer erlaubt.

Das ist eine direkt bewiesene notwendige Bedingung. Der historische Encoder prüft dieses Verbot bei zwei offenen H-Zeilen nicht allgemein; er zählt dort zunächst nur die Sternbeiträge. Der Filter kann folglich echte zusätzliche Reduktion liefern. Wie groß die Reduktion auf m=7 ist, ist ungemessen.

Zusätzliche eigene Prüfung: Auf dem unabhängig verifizierten BvLS-Zeugen wurden alle41.800 Nachbarpaare innerhalb aller220 H-Sterne geprüft.3960 Paare teilen einen Bordervertex, kein einziges davon ist eine Kante. Ergebnis in FILTER_WITNESS_CHECK.json. Das bestätigt die Verträglichkeit mit diesem vollständigen Zeugen und damit seinen Präfixen, ersetzt aber weder den allgemeinen Beweis noch die Implementierungsprüfung einer neuen CNF.

### Kapazitätsbedingungen C(S)

Für jede offene Zeile und jede Border-Marge: Bereits festgelegte Einsen dürfen das Soll nicht überschreiten; bereits festgelegte Einsen plus noch verfügbare Möglichkeiten müssen das Soll erreichen können. Analog für bereits linearisierte gemeinsame-Nachbarn-Budgets zu gebauten Zeilen. Überbuchte Zustände lassen sich so ohne großen Completion-Aufruf erkennen.

Diese Bedingungen sind notwendige Filter, keine vollständige Erfüllbarkeitsprüfung. Dass sie gekoppelte Sternwidersprüche nicht sämtlich erkennen, macht sie schwach, nicht unsound. Eine Bezeichnung als „exakter Zähler“ wäre ohne gekoppelte Sternprüfung falsch; die Verwendung als billiger notwendiger Filter bleibt legitim. Beide neuen Filter verändern den zu zählenden Raum gegenüber dem historischen F. Alte F-Breiten dürfen danach nicht kommentarlos als Breiten des neuen Modells verwendet werden.

P1 soll deshalb zuerst den sauber reproduzierten F-Zensus liefern. Eine verschärfte Variante erhält eigene Modellkennung, Zähl-/SAT-Abgleich und separat berichtete Zahlen. Billige C(S)-Tests vor/nach erzeugten Zuständen sind von einer exakten Zählung nur der C(S)-überlebenden Kinder zu unterscheiden.

## 4. Wo das Review über die Evidenz hinausgeht

### „Formal NO-GO“ ist nicht bewiesen

Die Größen sind ein starkes praktisches Warnsignal für materialisierte Ganzzeilenschichten. Die Schwelle Summe(min w/|Aut|)≥10^8 ist aber eine gesetzte Entscheidungsschwelle, kein mathematischer Unmöglichkeitsbeweis für vollständige Suche auf dieser Hardware.

Die Annahme, jeder erzeugte Kindzustand benötige zwingend einen eigenen SAT-Aufruf, gilt nicht für jede vollständige Methode. Gemeinsame Widersprüche, stärkere notwendige Bedingungen, symbolische Zählung und andere Zerlegungen können große Mengen gemeinsam behandeln. Zudem werden hier Kinder einer notwendigen Relaxation gezählt; sie sind nicht alle SRG-extendierbar. Untergrenzen für diese rohe Schicht sind keine allgemeinen unteren Laufzeitgrenzen aller Ausschlussverfahren.

Die Rechnung1,4Mrd.×0,1s≈4,44CPU-Jahre stimmt als Szenario. Mit4,676Mrd. wären es etwa14,82CPU-Jahre. Der Zeitansatz und die Notwendigkeit einzelner Aufrufe sind jedoch unbewiesen. „Direkte SAT ist die einzige plausible vollständige Methodenfamilie“ ist eine strategische Meinung, kein aus den Zahlen folgender Satz.

### Drei Proben tragen keine Varianzaussage

Die drei Root1-Werte liefern den schon dokumentierten Schätzwert3.884.069.460 für die definierte nächste beschriftete Ebene. Kleine Streuung bei n=3 schließt seltene riesige Teilbäume nicht aus. Aus dieser einen Übergangsmessung folgt auch nicht, dass die Breite „pro Ebene“ allgemein um Faktor8 schrumpft.

Knuth-Schätzer verwenden für erwartete Baumgrößen arithmetische Mittel der korrekt gewichteten Pfadprodukte. Mediane, geometrische Mittel und Mittelwerte der Logarithmen dürfen diese nicht ersetzen. Ein Bootstrapintervall ist bei unentdeckten schweren Verteilungsschwänzen keine verlässliche obere Schranke. Offene/zensierte Proben dürfen nicht als Null verschwinden.

P2 muss außerdem eine feste, versionierte Kandidatenregel haben: Der frühe Text nennt höchstens4 Kandidaten; das gelieferte Probenprogramm prüft alle offenen Nachbarn der zwei gebauten Zeilen, hier22. Das sind unterschiedliche Suchbäume und Kosten. Der Abgleich verwendet die tatsächlich gelieferte R1-Regel; für eine Viererregel wären neue Daten nötig.

### Fehler im Duplikatbefund

Die Aussage, `duplicates_against_retained_sample` erfasse keine Isomorphie, ist falsch. `worker.py` verwendet `g.key(child)` und damit `pynauty.certificate` des gefärbten Teilgraphen. Der Zähler kann sowohl gleiche beschriftete Zustände als auch zulässige isomorphe Zustände im gerade behaltenen Pool erfassen. Das Problem ist seine kleine, wechselnde Referenzmenge, nicht das Fehlen von Kanonisierung.

### Wiederholungen und effektive Breite

Gleiche ordered-Root-CNF bei Neustarts ist im Code belegt; deterministische SAT-Reihenfolge ist vom Reviewer in seiner Umgebung beobachtet. Für1333 byteidentische Ryzen-Ausgaben und exakt9,6 verschwendete CPU-Stunden fehlen jedoch die `rows_sha256`-/Einzelzeitbelege. Zeitlimitfälle können verschieden lange gleiche Präfixe ausgeben. Die Zahl ist deshalb eine plausible Aufwandsschätzung, kein vollständig belegter Endbefund.

Projektionen geteilt durch Gesamtzahl der Segmente ergeben keine exakte Zahl expandierter Eltern pro Ebene. Nicht alle Segmente erreichen jede Ebene, und dynamic testet mehrere Ziele pro Elternzustand. Die Diagnose „Budget drückt effektive Breite“ ist plausibel; exakt sind erst `levels`/Checkpoints. Seriennummern4–21 von Proofartefakten sind ebenso keine direkt ablesbaren Tiefen.

## 5. Ein kleiner zusätzlicher mathematischer Schluss

Wenn die im H-Faser-Bericht bewiesene Untergrenze von8 betroffenen Vertices für zwei verschiedene vollständige L-Zustände desselben m=7-Rahmens gilt, ist eine L-Completion nach77 festgelegten vollständigen H-Zeilen höchstens eindeutig. Jede Differenz zweier Completions wäre auf die höchstens7 ungefüllten Zeilen beschränkt, im Widerspruch zur Untergrenze.

Das ist eine bedingte Eindeutigkeitsaussage, keine Existenzgarantie. Sie hilft nicht bei der derzeitigen frühen Explosion und wird nicht ohne erneuten Beleg auf m=11 übertragen.

## 6. Gemeinsame, aber gestufte Fortsetzungsempfehlung

**Jetzt vorzubereitender erster Block: P0+P1.** Weiterhin48CPUh als großzügige vorgeschlagene Meldeschwelle, keine automatische Abschaltung. Vollzensus8105×83 im historischen F; Daten und Rootwahl reproduzierbar; echte Zielhardwarekalibrierung; GC-19, Wiederaufnahme und Uniformsampler sauber implementieren. Parallel als Entwicklungsteil die beiden billigen Filter beweisen und kontrollieren, nicht still das Basismodell wechseln. Der Zensus soll Counts speichern, nicht Milliarden Zeilen.

**Danach P2, nicht automatisch gleichzeitig:** geschichtete uniforme Proben nach den neu erkannten Strukturtypen, Stabilisatoren als weitere Stratum-/Diagnosevariable. Zuerst klar begrenzte Tiefe2/3-Diagnose mit festgelegter Regel und offengelegten Auswahlkosten. Ganze Baumprognosen erst, wenn tiefere Proben und Taildiagnostik sie tragen. Gepaarte Filtervergleiche bevorzugt an denselben Elternzuständen; gleiche Zufallszahlen allein garantieren nach unterschiedlichem Pruning keine vergleichbaren Pfade. Meldeschwelle128CPUh vorläufig wie V2, nach Zielhardwarekalibrierung anzupassen.

**Direkte volle SRG-SAT/Cube-Zerlegung früher vorbereiten, aber P3 nicht als bereits freigegeben behandeln.** Zustimmung zum Reviewer, dies als ernsthafte konkurrierende Methode zu behandeln. Vor200CPUh-Härtestichprobe erst vollständige Modellsemantik, unabhängige Kontrollfälle, nachvollziehbare Cube-Coverage und Proof-/Speicherpipeline. Die Ergänzung aller offen–offen-Paarbedingungen ist ein eigener Encoder, kein kleiner Schalter des historischen F.

Für eine spätere Cubestichprobe feste Auswahlwahrscheinlichkeiten, vorab bestimmte Fälle und Behandlung langer/offener Fälle festlegen.100 zufällige Cubes je Root können schwere Ausreißer verfehlen. Die D3-Schwelle200CPUh/Root bleibt eine praktische Entscheidungsschwelle, keine beweisbare Prognose. Die Behauptung, LRAT lasse sich im geplanten Umfang innerhalb60GB einfach streamend prüfen, muss an der konkreten Pipeline gemessen werden; sequentielles Lesen bedeutet nicht konstanten Gesamtressourcenbedarf.

**P4 ist eine sinnvolle neue Kontrollstufe:** BvLS-Präfixe ohne vollständige Kantenhints lösen, etwa mit210/190/150 gebauten Zeilen. Das misst echte Suchfähigkeit für m=11 und ergänzt die bisherigen reinen Zeugenverträglichkeitstests. UNKNOWN wäre eine Leistungsgrenze des gewählten Suchers, kein Widerspruch zur bekannten Completion. Diese Tests sind nicht bereits durch33/33 SAT mit fixierten Kanten erledigt und liefern keine m=7-ETA.

Kein pauschaler Start aller380 Reviewer-CPUh oder480 früherer Codex-CPUh. Diese Gesamtzahlen verbergen noch nicht implementierte Methoden und unsichere Arbeitspakete. Zunächst den billigen, vollständigen Erkenntnisschritt abschließen und dann anhand seiner Resultate und der kontrollierten Proben entscheiden. Nearest-H muss nicht abgewartet werden; C2-Checker bleibt unangetastet.

## 7. Noch benötigte Pilotartefakte

Priorität für einen kompakten Folgeexport: `levels`/Checkpoints, tiefe `best.json`-Zustände, Metadata der512 Proofs und der Tiefe1/2-Enumerationen mit Hashes; ausgewählte CNF-/DRAT-Paare zur erneuten Prüfung. Damit werden Wiederholungen, tatsächliche Elternbesuche, Proofauswahl und C(S)-Wirkung direkt testbar. Keine pauschale Übertragung der gesamten35GB erforderlich.

cand_A/B und die H-Faser-Quellarchive sind für die eigenständige memetische Validierung relevant, blockieren den F-Zensus aber nicht. Frühere Feststellung „Reviewertext fehlt“ ist durch diesen Nachtrag erledigt; die übrigen Artefaktlücken bleiben bestehen.

## Fazit

Der vollständige Text stärkt die Empfehlung, frühe Breiten zu zählen und präzise zu beproben, statt ganze Schichten auszuschreiben. Neu übernommen werden die Priorität billiger notwendiger Filter, die eng begrenzte Symmetrieersparnis bei fester Root und die Vorbereitung einer echten konkurrierenden Voll-SAT-Methode. Nicht übernommen werden ein formaler Unmachbarkeitsanspruch, medianbasierte Gesamtbaumentscheidungen oder pauschale Übertragungen aus drei Proben. Die praktische Entscheidung gegen den unveränderten Vollbaum-Plan ist gut begründet; die mathematische Möglichkeit anderer vollständiger Verfahren bleibt offen.
