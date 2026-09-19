# Restsymmetrie und partielle Lex-Brechung, Version 1.0.0

19. September 2026. Ausgangsstand dd83aaef93dd0515e61513e3f2da2f3e29839c24.
Gegenstand ausschließlich C2. Kein Involutionsausschluss, keine neue Literaturbehauptung.
Die Fixpunkt-Literaturvoraussetzung und die Encoderargumente des bisherigen Modells
bleiben Voraussetzungen. Das externe Review wird nicht als eigene Reproduktion verwendet.

## Gruppe und Wirkung

Für jeden der elf kanonischen Matchingfälle L verwenden wir G = Stab_H(L),
H = C2 wr S6, mit den einzeln fixierten Rahmenlabels 0,1. Das Programm enumeriert
alle 46080 Elemente von H, filtert auf L-Erhaltung und bestimmt deterministisch
Erzeuger. Explizite Gruppenschließung muss exakt der gefilterten Menge entsprechen.
Zusätzlich wird die Ordnung gegen Produkt_r (2r)^(m_r) m_r! geprüft.

Jeder Erzeuger q kommutiert mit a -> a xor 1. Er wirkt auf Außenlabels durch
{a,b} -> {q(a),q(b)}. Exportiert werden q, die Außenpermutation und die induzierte
Bijektion p der 1722 Primärvariablen (alte Nummer -> neue Nummer). Geprüft werden
alle Außenkanten, verbotenen Kanten, Labelinzidenzen, gemeinsamen Labelanzahlen
und die mengenweise Erhaltung der 66 vorzeichenbehafteten Fallannahmen.

Damit wird E1 durch Zeilen- und Summandenpermutation erhalten. Für E2 werden
Außenzeile x und Rahmenlabel a gleichzeitig permutiert; Inzidenzen und a xor 1
bleiben kompatibel. Für E3 werden x,y,z gleichzeitig permutiert und die rechte
Seite bleibt wegen der erhaltenen Labelüberschneidung gleich. Dieses Argument
gilt für jede Belegung, unabhängig von einem zufälligen Beispiel. Es wird keine
syntaktische Automorphie der Zähler-Hilfsvariablen behauptet. Die semantische
Encoderäquivalenz liefert für jede umbenannte Primärlösung eine Hilfsbelegung.

## Vertretererhaltung

Globale Ordnung: x_1,...,x_1722, mit 0 < 1. Für jeden gewählten Erzeuger p
und eine Präfixlänge d wird die Bedingung

(x_1,...,x_d) <=lex (x_p(1),...,x_p(d))

hinzugefügt. Die rechte Seite ist die Pullback-Wirkung, also die inverse
Umbenennung gegenüber dem exportierten Vorwärtstransport. Auch sie liegt in G.
Alle Vergleiche verwenden Präfixe derselben globalen Ordnung; beliebig anders
geordnete Teilmengen sind durch dieses Argument NICHT gerechtfertigt.

Wähle in einer nichtleeren G-Bahn von Primärlösungen deren globales
lexikographisches Minimum b. Für jedes p in G gilt b <=lex p*b. Dies gilt auch
nach Abschneiden beider Tupel auf dasselbe Präfix. Also erfüllt b sämtliche
hinzugefügten Vergleiche gleichzeitig. Die CNF-Kodierung unten besitzt dafür
eine Erweiterung. Jede ursprüngliche Lösungsbahn behält mindestens einen
Vertreter. Die Rückrichtung folgt, weil die ursprünglichen Klauseln erhalten
bleiben. Erzeugervergleiche müssen nicht genau einen Vertreter übriglassen.
Variablen einer Bahn werden ausdrücklich NICHT gleichgesetzt.

## Lex-Kodierung

Positionen i mit p(i)=i können entfallen, weil dort identische Bits verglichen
werden. Für die verbleibenden Positionen (a,b) bezeichnet e die Gleichheit
aller vorher verglichenen Bits, anfangs true. Die Klausel

not e OR not a OR b

verbietet bei gleichem Präfix die falsche erste Abweichung (1,0). Falls eine
weitere Position folgt, wird frisch e' eingeführt mit e' iff e AND (a iff b):

- not e' OR e
- not e' OR not a OR b
- not e' OR a OR not b
- not e OR a OR b OR e'
- not e OR not a OR not b OR e'

Diese fünf Klauseln definieren e' genau. Induktion über die Positionen zeigt
Projektionsäquivalenz mit dem Lex-Vergleich. Weglassen des letzten unbenutzten
Präfixgates verändert nichts. Frische Gatebereiche beginnen strikt nach dem
Totalizerbereich; jeder Erzeuger besitzt eigene Gates.

## Dreierklauseln

Teilen zwei Außenknoten x,y ein Rahmenlabel, so ist der E3-Zielwert 1
(verschiedene Zweierlabels schneiden sich in höchstens einem Label). Daher
können M_xy und M_xz M_yz nicht gleichzeitig 1 sein. Für jedes Außendreieck,
in dem mindestens ein Paar ein Rahmenlabel teilt, folgt

not M_xy OR not M_xz OR not M_yz.

Konstante Nullkanten machen eine Klausel trivial; übrige Literale werden nach
der vorgegebenen Involution identifiziert und Klauseln dedupliziert. Ergebnis:
28980 verschiedene Dreierklauseln, ohne zusätzliche Variablen. Die Dreierklauseln
sind Folgerungen; Lex-Klauseln sind im Allgemeinen KEINE Folgerungen, sondern
zulässige Vertreterwahl. Dieser Unterschied bleibt in Zertifikaten wesentlich.

## Kontrollen und Grenzen

- 2140 erschöpfende Lex-Projektionsprüfungen: alle Permutationen bis vier Bits,
  alle Präfixlängen einschließlich null, alle Belegungen, unabhängiges kleines DPLL.
- 448 Bahnminimumprüfungen auf sechs Bits unter S6 (Ordnung 720), mit mehreren
  gleichzeitigen Erzeugervergleichen und allen Präfixlängen.
- 16 vollständige Kleinmodellprüfungen: vier Varianten mal vier Belegungen des
  k=4-Rahmens, direkt gegen die rekonstruierte SRG-Bedingung; jeweils eine Lösung.
- Alle elf großen Fallgruppen und induzierten Abbildungen sind explizit geprüft.

Der k=4-Fall hat nur eine sehr kleine, auf Primärbits wenig aussagekräftige
Restwirkung. Deshalb sind die zusätzlichen nichttrivialen S6-Kontrollen nötig.
Die Kontrollen ergänzen den allgemeinen Beweis, ersetzen ihn nicht. Der
bestehende Rahmenencoder wird wiederverwendet: kein vollständig unabhängiger
Zweitencoder. Ein späterer UNSAT-Proof der Lex-CNF muss gemeinsam mit diesem
Vertretererhaltungsargument und der Matchingabdeckung beurteilt werden.
