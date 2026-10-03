# DRAT-Sonderfall in der Entwicklungskontrolle

Der Zwei-Arm-Test an Root 1 (je 120 CPU-s) ergab drei akzeptierte und zunächst
einen zurückgewiesenen lokalen Abschluss. Der vierte hatte null Projektionen,
eine bereits widersprüchliche Eingabeformel und eine leere DRAT-Ausgabe.

Das Original-Prüferlog enthält `c trivial UNSAT` und die exakte Zeile
`s VERIFIED`, der Prozess liefert jedoch Exitcode 1. Der unveränderte,
fixierte Quelltext von drat-trim erklärt dies: Bei `parseReturnValue == UNSAT`
wird die Erfolgszeile ausgegeben, die für den Rückgabewert benutzte Variable
`sts` bleibt aber auf ERROR. Die normale Verifikation setzt `sts` korrekt.

Die Adapterkorrektur verändert den Prüferquelltext nicht. Akzeptiert wird:

1. regulär: Exitcode 0 und exakt `s VERIFIED`;
2. ausschließlich für diesen fixierten Sonderfall: Exitcode 1, exakt
   `s VERIFIED`, zusätzlich `c trivial UNSAT`, **und** eine zweite, unabhängige
   Python-Unit-Propagation findet selbst einen Widerspruch in der CNF.

`NOT VERIFIED` wird nicht durch Teilstringvergleich akzeptiert. Andere
Fehlercodes und Limits bleiben unzertifiziert. Die echte auslösende partielle
Konstruktion ist als `fixtures/trivial_unsat_state.json` im Paket enthalten.
Positivtest, falscher Beweis einer erfüllbaren Formel und beschädigte
Projektionsliste werden in den Kontrollen ausgeführt.

Das erste Ergebnis bleibt unter `depth_probe_initial_summary.json`
nachvollziehbar; der spätere Sonderfall-Nachweis steht separat. Es wurden
keine ursprünglichen Fehllaufbelege still als ursprünglicher PASS umgeschrieben.
