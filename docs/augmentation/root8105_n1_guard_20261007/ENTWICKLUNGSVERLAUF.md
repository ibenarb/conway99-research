# Prüf- und Entwicklungsverlauf

Erste Abnahme: 12 neue Guardkontrollen bestanden (controls-01). Danach wurden
Budgethistorienvalidierung und weitere Kontrollen ergänzt (controls-02:17 PASS).
Bei Quellprüfung wurde ein Endübergang erkannt: Ein Beobachter kann zwischen der
ersten Prüfung auf seinen Endbeleg und der Prozessabfrage normal enden. Die
ursprüngliche Fassung hätte dies als fehlenden Endbeleg melden können. Vor
Veröffentlichung wurde die erneute Belegprüfung ergänzt; der deterministische
Test bringt genau in diesem Fenster den Beleg ein und meldet PASS.
Kein tatsächlich aufgetretener Ressourcenfehler eines Nutzerlaufs wird behauptet.
Die Vorfassungen der Quellen und alle Zwischenabnahmen sind im Evidenzarchiv.

Finale release-0 bis release-4:18+9+16+11+11=65 PASS. Danach nur Dokumentation und
Paketierung. Explizite Testcrashes und abgewiesene manipulierte Eingaben gehören
zu diesen Kontrollen. Kein fehlgeschlagener regulärer Abnahmelauf in diesem Paket.
Die allgemeine Regel aus GC-03 gilt: Zustandsübergänge erneut lesen, tatsächliche
fehlende Endbelege oder Zugriffsfehler aber nicht als null/gesund unterdrücken.
