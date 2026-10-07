# N1: Katalogbindung der beiden archivierten Klasse-0-Eingaben

Abgeschlossen am 07.10.2026. Basiscommit: `bd0e5f301e02de2fe6180a88bb00d5259caaedb6`.

## Ergebnis und Geltungsbereich

Root 210 und Root 6682 wurden direkt gegen den hashfixierten ursprünglichen
8105-Rootkatalog geprüft. Die Klasse-0-Repräsentanten stammen aus den ebenfalls
hashfixierten Matching-Coverage-Dateien des alten CLASSES.tar.xz. Selektionsdaten,
Rootzeilen, Klassenkennungen und historische Abschlussbelege stimmen überein.
Beide CNFs wurden mit dem unveränderten Encoder neu erzeugt und byteweise mit
den archivierten CNFs verglichen. Kantenabbildungen und Metadaten stimmen exakt.
Sechs Manipulationen (Rootnummer, Klassennummer, Matching je Root) wurden abgewiesen.

Keine SAT-Suche, keine gelöste Klasse, kein Rootausschluss. Die alte erschöpfende
Matching-Coverage wurde als fixierter Vorbeleg übernommen; ihre Orbitrechnung
wurde nicht wiederholt. Die Bindungen gehören ausschließlich zu Klasse 0.

Die v0.3-Bindungen behalten `catalog_identity_checked: false`: dieser generische
Binder prüft selbst keinen Katalog. Der getrennte CATALOG_RECEIPT.json bestätigt
die hier zusätzlich geprüfte Katalogidentität und bindet jede Binding-Datei per
SHA256. Der Runtime-Code wurde nicht verändert und erzwingt diesen Zusatzbeleg
noch nicht automatisch. Daraus folgt keine Produktionsfreigabe.

## Reproduktion

Im Repository am Basiscommit plus diesem Paket:

```sh
python3 tools/memetik/audit_python.py
# Den ausgegebenen Interpreter verwenden; python-sat==1.9.dev15 erforderlich.
/path/to/audit/python tools/memetik/verify_n1_catalog.py . /tmp/n1-catalog-new
```

Das Ziel muss neu sein. Das Skript importiert ausschließlich den Binder/Encoder,
keinen Solverstarter. Alte Eingaben werden nur gelesen. CNFs entstehen temporär;
die dauerhaften Bindungen verweisen per SHA256 auf die vorhandenen CNFs im Archiv
`docs/augmentation/root8105_n1_20261006/CLASSES.tar.xz`.
Das ZIP enthält Prüfer, Binder, unabhängigen Checker, Encoder und diese Ergebnisse;
der Rootkatalog und die archivierten Eingaben werden aus dem fixierten Repository
benötigt und nicht erneut dupliziert. Kein eigenständiges Produktionspaket.

## Verbrauch und offene Punkte

Cloud-Prüfung erfolgreich, python-sat 1.9.dev15. Prozess-CPU bis zur
Receipt-Serialisierung: 3,622566 Sekunden; Peak-RSS: 190192 KiB. Diese Messung
umfasst weder den gesamten Chat noch eine Host-/Supervisor-Endabrechnung.
Regeln GC-08/16/20/22/23; Regelquellen am oben genannten Basiscommit.
Keine alten CPU-Lücken geschlossen. Vollständige Runtime-/Hostabrechnung,
Ressourcenüberwachung und echte Zielhardwareprüfungen bleiben offen.

Nächstes begrenztes Arbeitspaket: vollständige Runtime-Verbrauchsabrechnung
konzipieren und implementieren; weiterhin kein Ryzen- oder Suchstart.
