# Vertrag für neue memetische Gründer

Stand: 13. September 2026. Vorschlag für die nächste gemeinsame Kandidatensammlung.

## Auftrag

Ziel sind zunächst zehn zusätzliche geprüfte Gründer insgesamt, möglichst fünf je bestehendem Sucharm und mindestens vier nachvollziehbar verschiedene Konstruktionsprinzipien insgesamt. Dies ist ein Ziel, keine garantierte Liefermenge. Fehlende zulässige Gründer werden gemeldet; keine Auffüllung durch Umnummerierungen. Einreichungen dürfen mehr Kandidaten enthalten, aber viele Seeds einer Methode sind keine vielen Methoden.

KI-Partner sollen Generatoren und Konstruktionsrezepte liefern, nicht frei erfundene Adjazenzmatrizen. Reproduktion vorhandener HoG- oder Projektgraphen ist eine Kontrolle und muss als solche bezeichnet werden. Herkunft ohne Abstammung von den aktuellen Gründern ist erwünscht, aber noch kein Beweis eines neuen Einzugsgebiets.

## Harte Aufnahmebedingungen

Für beide Arme: vollständiger einfacher ungerichteter Graph auf 99 Knoten, Grad genau 14, binäre symmetrische Matrix, Nulldiagonale.

| Arm | Zusätzlicher Vertrag |
| --- | --- |
| λ | Für jede Kante genau ein gemeinsamer Nachbar |
| Ω | Kanonischer 1+14+84-Rahmen, Partner a↔a+7 mod 14, Außenlabels alle Nichtpartnerpaare in lexikographischer Reihenfolge, H symmetrisch binär ohne Diagonale, H-Grad 12, PH=2J−(C+I)P |

P ist die 14×84-Inzidenzmatrix der Außenlabels, C die Adjazenzmatrix der sieben Partnerkanten. Ω setzt **nicht** global λ=1 voraus. Ω und λ sind verschiedene notwendige Teilbedingungssysteme für Näherungen; kein ungeprüfter Transfer.

Kein exaktes Conway-Zielspektrum, keine globale μ=2-Bedingung und keine willkürlich geforderte kleine Fehlerzahl als Minimalbedingung: Dies würde die gesuchte Lösung oder einen unbegründet engen Qualitätsfilter voraussetzen. Qualitätsselektion erfolgt nach der Zulässigkeitsprüfung.

## Lieferumfang je Konstruktionsprinzip

1. Vollständiger Generator mit Versionen und reproduzierbarem Aufruf; Herkunft und mathematische Konstruktion.
2. Je Kandidat graph6, SHA256 über Dateibytes, Arm, Seed, Eltern/Abstammung falls vorhanden.
3. Für Ω Wurzel und vollständige Zuordnung zum kanonischen Rahmen; eine alternative Nummerierung braucht eine explizite Permutation.
4. Eigene Laufkosten, Zahl versuchter und erfolgreicher Konstruktionen; TIMEOUT/UNKNOWN nicht als Unmöglichkeit melden.
5. Vollbewertung aller 4851 ungeordneten Paare: r_ij=(A²)_ij+A_ij−2, W, L1, L2², Linf, Residuenhistogramm, λ-Fehlerzahl. Keine bloße H84-Teilbewertung.
6. Vermutete neue Struktur und bekannte Einschränkungen: etwa erzwungene Symmetrie oder Abstammung von einem Literaturgraphen.

## Zentrale unabhängige Abnahme

- Harte Bedingungen und alle Scores unabhängig nachrechnen.
- Exakte Isomorphiededuplikation gegen Altbestand und neue Einreichungen; für Ω zusätzlich arbeitsrahmenerhaltende Identität berücksichtigen.
- Residuenprofil, Defektgradprofil und gegebenenfalls Spektraldiagnostik als Strukturmerkmale, nicht als vollständigen Isomorphietest.
- Mehrere standardisierte Abstiege mit identischem Budget; Rückkehr zu denselben Endgraphen als empirisches Signal dokumentieren.
- Gleicher Score bedeutet nicht gleiches Plateau. Nichtisomorphie bedeutet nicht anderes Einzugsgebiet.
- Weniger als zehn neue Kandidaten ist ein zulässiges Ergebnis. Das verfehlte Mengenziel darf nicht durch Umbenennung derselben Familie verdeckt werden.

Im Pilot Startqualität und Strukturvielfalt getrennt auswerten. Schlechtere, aber andere Gründer dürfen im Archiv bleiben; ein Vorteil ihrer Verwendung muss im Vergleichslauf gezeigt werden.
