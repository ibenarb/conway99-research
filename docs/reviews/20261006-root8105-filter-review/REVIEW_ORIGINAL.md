Ich habe die vier Dateien sowie `MATHEMATIK.md` und `filters.py` gelesen und nichts nachgerechnet. Meine Herleitungen setzen diese Lesart des Modells voraus: H ist die zweite Subkonstituente eines Knotens x₀. Jedes Label S(v) ist eines der 84 Nicht-Matching-Paare der 14 Nachbarn von x₀. L(c) bezeichnet die zwölf H-Knoten mit c im Label, c′ den Matchingpartner von c. N(a) steht für die H-Nachbarschaft, und w(p), w(q) sind die beiden H-Nachbarn der Wurzel a, die einen Labelpunkt mit a teilen. Eure Klassenzahlen sind genau 24 × (51, 20, 10, 2). Das sagen die Randmargen unter dieser Lesart vorher, was sie stützt.

#### 1. Eure Schlussfolgerungen

**Gesichert.** Der Nullbefund ist sauber erhoben: identische Zustände, keine Nachselektion. Die BVLS-Positivkontrolle ist gut gewählt, weil λ und μ dieselben sind.

Das LD-Lemma ist korrekt. Ein verbotenes Paar in N(u) kann nur über die andere gebaute Zeile feststehen, also nur in einem H-Dreieck a, b, w. Bei e = 0 gibt es kein solches Dreieck, und bei (1,1) schließt F es ebenfalls aus.

Das Gegenbeispiel ist ein echtes F-gültiges, nicht fortsetzbares Präfix. Sein eigentliches Zertifikat ist der Zweizeiler: 29 und 32 sind benachbart und haben die gemeinsamen Nachbarn 0 und Randpunkt 2, was λ = 1 verletzt. Die UNSAT_UNCERTIFIED-Läufe bestätigen das nur zusätzlich. Dass es über Quoten nichts aussagt, schreibt Ihr richtig.

**Zu schwach bzw. unvollständig.**

- Auch der CAP-Nullbefund ist strukturell erzwungen (siehe 2). „Für CAP folgt noch keine Redundanz“ ist formal richtig, verdeckt aber, dass der Pilot für keine Variante überhaupt eine Wirkung messen konnte, sondern nur Kosten.
- Die Lücke war vorhersehbar. Die beiden (1,1)-Ziele sind w(p) und w(q), also strukturelle Extremfälle der Breite. Der Median fällt bei 51 von 83 Zielen praktisch sicher in (0,0). Die Lehre daraus: zuerst nach Relationstyp schichten, dann nach Breite.
- Nach Eurem eigenen Lemma ist LD auf (0,1) wirkungslos. Der (0,1)-Arm des Ergänzungspiloten kann also nur CAP zeigen.
- Die in `MATHEMATIK.md` angekündigte Überadditivität von LD+CAP kann bei Tiefe 2 nicht auftreten (siehe 2).

#### 2. Eigene Folgerungen

**Gesichert (aus `filters.py` hergeleitet, unter obiger Lesart).** Bei zwei gebauten Zeilen greifen CAP-Obergrenzen nie. Jede Gleichung behält mindestens fünf offene Positionen, und die Zielwerte sind höchstens 2 (Paar, Rand) bzw. 12 von 84 (Grad). Eine Untergrenzenverletzung braucht einen offenen Knoten w, der zu beiden gebauten Zeilen benachbart ist. F erzwingt in (1,0) und (0,1) genau ein solches w. Daraus folgt vollständig:

| Klasse                   | LD                | CAP              | verworfen genau dann, wenn |
| ------------------------ | ----------------- | ---------------- | -------------------------- |
| (0,0), (1,1)             | nie               | nie              | –                          |
| (1,0)                    | identisch mit CAP | identisch mit LD | S(w) ∩ (S(a) ∪ S(b)) ≠ ∅   |
| (0,1), S(a) ∩ S(b) = {c} | nie               | ja               | S(w) ∩ {c, c′} ≠ ∅         |

Bei Tiefe 2 gilt also F+LD+CAP = F+LD ∪ F+CAP. Auf (1,0) leistet LD dasselbe wie CAP zu einem Hundertstel der Kosten. Euer Gegenbeispiel ist der Fall S(w) ∩ S(b) = {2}.

Die (0,1)-Widersprüche sind elementar. Bei c ∈ S(w) hätte die Kante c–w die zwei gemeinsamen Nachbarn a und b. Bei c′ ∈ S(w) hätten die Nichtnachbarn c und w drei gemeinsame Nachbarn (c′, a, b).

Schlechte Kandidaten für w gibt es in (1,0) zwei bis vier unter den elf übrigen Nachbarn von a, in (0,1) genau zwei von zwölf. Inhaltlich prüfen beide Filter bei Tiefe 2 nur die lokale λ-Struktur:

- N(a) ohne w(p), w(q) trägt ein perfektes Matching aus fünf labeldisjunkten Paaren.
- Jedes L(c) induziert ein perfektes Matching.

**Plausibel.**

- Bei nicht zu schiefer Verteilung von w liegen die Verwerfungsquoten grob bei 2/11 bis 4/11 bzw. 2/12. Schätzen muss man sie aber nicht. Sie sind exakt die Summe der F-Breiten mit erzwungenem Bit w über die schlechten w, berechenbar mit Euren vorhandenen Rekursionsgewichten.
- (e,s) ist zu grob. Unter Z₂≀S₇ zerfallen Labelpaare weiter nach Partnerbeziehungen, etwa t = Anzahl der x ∈ S(b) mit x′ ∈ S(a). Dieses t bestimmt die Zahl schlechter Kandidaten. Die deutlich kleineren (1,0)-Breiten bei drei Typ-0-Roots (rund 1,5 Mio. statt 3,5 Mio.) deuten möglicherweise auf eine solche verdeckte Schicht.
- Strategisch bringen solche lokalen Filter nur konstante Faktoren pro Ebene. Bei Breiten von 10⁶–10⁷ je Zeile entscheiden sie nicht über die Machbarkeit.

**Offen.**

- Ab welcher Tiefe greifen Obergrenzen? Sie brauchen fast vollständig bekannte L(c) oder N(u), das hängt also an der Aufbaureihenfolge.
- Geht LD-verengte CAP ab dort über die Vereinigung hinaus?
- Wie verhält sich die Breite ab Tiefe 3?

#### 3. Ergänzungspilot

Nicht in der vorgeschlagenen Form, aus drei Gründen:

- Er schätzt stichprobenartig eine exakt berechenbare Rate.
- Die Hälfte seiner Zustände testet LD dort, wo LD beweisbar nichts tun kann.
- Die Frage nach dem Mehrwert der Kombination ist für Tiefe 2 schon mit Nein beantwortet.

Da Manifest und Lauf billig sind, würde ich ihn umwidmen. Für jeden der 3072 Zustände schreibt Ihr vorab das vorhergesagte Ergebnis je Variante aus der Tabelle fest. Kriterium ist 100 % Übereinstimmung; jede Abweichung ist ein Implementierungs- oder Lemmafehler. Das ist ein scharfer Falsifikationstest statt einer Quotenschätzung. Priorität hat aber Punkt 4.

Zu anderen Wegen: Symmetrische Fälle sind stark eingegrenzt. Nach Cesarz und Woldar sind die Ordnungen 9 und 11 ausgeschlossen, eine gerade Gruppenordnung muss 6 teilen, und Teilbarkeit durch 7 erzwingt die zyklische Gruppe der Ordnung 7. Ein vollständiger Ausschluss folgt daraus nicht, solange die triviale Gruppe offen ist. Zudem lieferte ein CP-SAT-Modell selbst für den Z₇-Fall nach 48 Stunden auf 14 Kernen kein Ergebnis. Eine symmetriefreie Suche wie Eure bleibt also nötig, braucht aber eine belastbare Machbarkeitsgrundlage. [arxivsvgarxivsvg](https://arxiv.org/pdf/2608.11211)

#### 4. Bevorzugter nächster Schritt

**Fragestellung:** Schrumpft eine an der lokalen Matchingstruktur ausgerichtete Aufbaureihenfolge mit Vorwärtsprüfung im Generator den Baum bis zum Abschluss der Wurzelnachbarschaft um Größenordnungen?

**Methode in drei Teilen:**

1. **Generator statt Filter.** LD, die CAP-Untergrenzen und die μ-Prüfung aus (0,1) werden als erzwungene Nullen direkt im Sampler gesetzt. Dazu kommt eine Matchingprüfung (Hall/Tutte) auf jeder vollständig bekannten Nachbarschaft, also N(u) gebauter Zeilen und jedes L(c). Diese Prüfung ist strikt stärker als LD und kostet bei höchstens zwölf Knoten praktisch nichts.
2. **Nachbarschaft zuerst.** Nach a werden die zulässigen perfekten Matchings M auf N(a) ∖ {w(p), w(q)} exakt aufgezählt, bis auf Stab(a). Das sind höchstens 945, nur aus labeldisjunkten Paaren. Das Paar (a, M) ist das neue Wurzelobjekt. Danach folgen die zehn gematchten Zeilen, dann w(p) und w(q). Jede Root ohne zulässiges M wäre sofort elementar ausgeschlossen, falls es solche gibt.
3. **Knuth-Schätzung.** Auf den 24 Pilot-Roots schätzt Ihr die Baumgröße bis Tiefe 13 im 2×2-Design: alte gegen neue Reihenfolge, F gegen F+Propagation. Mit festen Seeds und mindestens 10⁴ Abstiegen je Zelle meldet Ihr log₁₀(Knoten) mit Bootstrap-Intervall und die Absterberate je Tiefe. Bei schweren Rändern geschichtete Schätzer verwenden.

**Entscheidungskriterium (vorab festgelegt):**

- Die neue Konfiguration wird Standard, wenn sie bei Tiefe 13 mindestens zwei Größenordnungen niedriger liegt und die Intervalle sich nicht überlappen.
- Für die Machbarkeit rechnet Ihr die Knoten über alle 8105 Roots hoch, multipliziert mit den gemessenen Kosten pro Knoten, und vergleicht mit Eurem realistischen Gesamtbudget. Liegt die obere Schranke darunter, folgt eine vollständige Kampagne mit Zertifikaten.
- Liegt sie mehr als drei Größenordnungen darüber, wird die zeilenweise Erschöpfung in dieser Form eingestellt. Stattdessen stellt Ihr auf zertifizierte Teilausschlüsse einzelner (a, M)-Klassen um.
