# Reviewabgleich und umgesetzte Fortsetzung — 06.10.2026

Ausgangspunkt: abgeschlossener Census/Audit und Filterpilot unter
`671adac6b9b987d7b9eb1ed53d81780a45c47c59`. Keine Wiederholung der 672715 Censuszählungen,
der 13455 Auditgegenzählungen oder der 4608 Pilotzustände.
Originalreview: eigener Branch `reviews/20261006-root8105-filter-matching`,
Commit `e4d4d6387a71b096ae949b3cc5e629891f7ab862`.
Das Review wurde als Chattext übermittelt; Metadaten unterscheiden die archivierte
Transkription von einer nicht vorhandenen hochgeladenen Originaldatei.

## Was übernommen und korrigiert wird

Die zentrale Kritik ist richtig: Der erste Pilot konnte bei Tiefe 2 **für keine
Filtervariante** eine Verwerfung beobachten. Auch der CAP-Nullbefund war strukturell
erzwungen. Er misst Implementierungskosten, nicht den Nutzen der Filter in den
fehlenden Relationstypen. Unsere vorherige Einschränkung auf das LD-Lemma war zu schwach.
Eine Überadditivität der Kombination ist bei Tiefe 2 ausgeschlossen. Für verworfene
Mengen gilt R_LD+CAP = R_LD ∪ R_CAP; für akzeptierte Mengen gilt dagegen der Schnitt.
Die Vereinigungsnotation im Review ist nur mit der ersten Lesart richtig.

Der ursprüngliche Ergänzungspilot ist ersetzt: dieselben eingefrorenen 3072 Ränge,
aber vorher festgeschriebene Entscheidungen, anschließend 100%-Vergleich. Quoten
werden nicht aus diesen Stichproben geschätzt, sondern durch exakte konditionierte
Rekursionsgewichte berechnet. Das Manifest bleibt byteidentisch (SHA256
`946fa4f19370e5df2871bfe11a78b4afc5de95f601e5345b8f6394b7fafb8ae0`).

Der Vorschlag „Generator statt Filter“ ist umgesetzt: Bei Tiefe 2 verbietet der
RestrictedSampler die schlechten gemeinsamen Nachbarn unmittelbar. Bei größerer
Tiefe übernimmt der Zeilengenerator erzwungene Kantenwerte aus Gleichungen,
LD und Matching-Vorwärtsprüfung. Die Matchingprüfung arbeitet auf allgemeinen
Graphen mit exakter Teilmengenrekursion; ein bipartites Hall-Kriterium wäre hier
nicht ausreichend. In N_H(u) werden vor der Matchingprüfung die beiden zum Rand
gepaarten Nachbarn entfernt. L(c) wird vollständig geprüft.

## Zwei zusätzliche Korrekturen am Review

1. **Die Zahl schlechter Kandidaten ist keine Verwerfungsquote.** Bei (1,0) sind die
   beiden Wurzelnachbarn mit Labelüberlappung zur Wurzel schon im historischen F
   verboten (`kernel.constraints`). Ihre konditionierten Breiten sind null.
   Aus zwei bis vier formal schlechten unter elf Nachbarn kann deshalb nicht
   2/11 bis 4/11 als plausible F-Verwerfungsquote folgen. Auch die verbleibenden
   Kandidaten haben ungleiche Gewichte. Bei Root1/Ziel76 haben die beiden bereits
   verbotenen Kandidaten6 und17 jeweils Breite0, die Kandidaten48 und75 jeweils255267;
   insgesamt werden510534 von3493558 Zeilen verworfen (14,6136%).
2. **t allein bestimmt die Zahl schlechter Kandidaten nicht.** Bei Root5116 haben
   Ziel25 und31 beide t=0, aber vier bzw. drei formal schlechte Kandidaten. Ziele58
   und68 haben beide t=1, aber drei bzw. zwei. Nach Abzug der durch F verbotenen
   Kandidaten10 und22 bleiben entsprechend2,1,1,0. `LABEL_STRATA.json` hält alle240
   (1,0)-Beziehungen der24 Roots fest. Eine feinere Beschreibung muss auch die
   konkrete Wurzel und ihre Nachbarschaft berücksichtigen.

Die Formulierung „nur lokale λ-Struktur“ ist außerdem zu eng: Der c′-Fall der
(0,1)-Klasse verwendet ausdrücklich die Schranke μ=2 für Nichtnachbarn.
Die gemessene CAP/LD-Kostenrelation wird als konkrete Implementierungsmessung
berichtet, nicht als mathematisch festes Verhältnis.

## Begründung des Tiefe-2-Lemmas

Schreibe e=1 genau für a–b und s=|S(a)∩S(b)|. F verlangt
|N(a)∩N(b)|=2−e−s. Für ein offenes w kennt CAP nur die beiden Kanten zu a,b.
Eine Graduntergrenze kann damit nicht überschritten werden. Eine Randgleichung
kann zwei bekannte Einsen nur für s=1 und den gemeinsamen Randpunkt c enthalten.
Ihr Ziel ist1 genau wenn S(w) einen der Punkte c,c′ enthält. Das liefert (0,1).
Bei (1,1) existiert kein gemeinsamer Nachbar.

Eine Paargleichung zu a kann als bekannte Eins nur die Kante w–b enthalten,
wenn e=1. Sie verletzt das Ziel2−1−|S(a)∩S(w)| genau dann, wenn w gemeinsamer
Nachbar ist und sein Label S(a) trifft; symmetrisch für b. Das liefert (1,0)
und zugleich genau den LD-Widerspruch eines labelüberlappenden Paares im Dreieck.
Bei (0,0) gibt es zwar zwei gemeinsame Nachbarn, aber keine solche bekannte Eins
in einer Paargleichung und keine gemeinsame Randgleichung.

Auch eine CAP-Obergrenzenverletzung ist ausgeschlossen, einschließlich LD-verengter
CAP: Für ein festes offenes w verbietet LD aus einer gebauten Nachbarschaft höchstens
zwei weitere inzidente Positionen. Denn die Randmargen der zwei Labelpunkte von w
summieren sich zu höchstens4, und w selbst zählt darin zweimal. Zwei gebaute Zeilen
verbieten damit höchstens4 Positionen. Eine Rand- oder Paargleichung mit12 Positionen
behält nach Entfernung von Diagonale, beiden gebauten Stellen und diesen4 Nullen
mindestens5 offene Positionen, ihr Ziel ist höchstens2. Die Gradgleichung behält
mindestens77 offene Stellen bei Ziel12. Bekannte Einsen verbessern diese Obergrenzen.
Widersprechende feststehende LD-Kanten sind bereits LD-Verwerfungen.

Die Tabelle des Reviews folgt. Dieser Beweis gilt für zwei gebaute Zeilen des
historischen Modells und die implementierten Filter, nicht für beliebige stärkere
Propagationsabschlüsse oder größere Tiefen.

## Strategische Anpassung

Die Richtung des Reviews wird übernommen: Matchingobjekte, Nachbarschaftsreihenfolge,
Vorwärtsprüfung und eine quantitative Machbarkeitsprüfung vor Erschöpfung.
Dabei gelten vier notwendige Einschränkungen:

- Alle vier Vergleichsarme verwenden denselben Wald von (a,M)-Repräsentanten.
  Andernfalls würde Matching-Vorbelegung mit Reihenfolge vermischt. Der F-Arm ist
  daher ausdrücklich **F unter festem M**, nicht der alte unbedingte F-Baum.
- Der lokale Zeilen-DP zählt bei mehreren gebauten Zeilen zunächst eine notwendige
  Obermenge. Ein SAT-Mitgliedschaftstest prüft die historische vollständige
  Sternrelaxation. Ein abgewiesener Vorschlag liefert Gewicht0 und wird nicht
  ersetzt. Die Gewichte enthalten die exakten Vorschlagsbreiten. Das ist eine
  Importance-/Knuth-Schätzung, keine Behauptung exakt bekannter F-Verzweigungsgrade.
- Die24 Roots wurden nicht mit positiven bekannten Auswahlwahrscheinlichkeiten
  aus allen8105 gezogen. Ihre Ergebnisse erlauben keine unverzerrte Hochrechnung
  auf alle8105. Eine solche Hochrechnung braucht ein neues Root-Stichprobendesign
  oder vollständige stratumweise Erfassung; vorhandene Censuswerte bleiben nutzbar.
- Ein Bootstrapintervall ist keine garantierte obere Schranke. Ein Baum bis Tiefe13
  ist nicht der gesamte Suchbaum bis84. Selbst eine belastbare lokale Verbesserung
  reicht daher nicht zur Freigabe einer vollständigen SRG-Kampagne.

Literaturabgleich: Die vom Reviewer verlinkte Arbeit, HTML-v2 vom18.09.2026,
berichtet die genannten Automorphismenbeschränkungen sowie einen ergebnislosen
Z7-CP-SAT-Lauf über48Stunden auf14Kernen. Das stützt die Vorsicht gegenüber
Machbarkeitsannahmen, ersetzt aber keine Analyse unseres Suchraums.
Quelle: https://arxiv.org/html/2608.11211v2 ; ursprüngliche Gruppenarbeit:
https://arxiv.org/abs/2308.02978 . Kein neuer Symmetrieausschluss wird behauptet.
