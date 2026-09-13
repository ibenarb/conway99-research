#!/usr/bin/env python3
"""Independent metadata/tree/log audit. No SAT solver or proof checker is invoked."""
import argparse
import collections
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile
import gzip
import os
import shutil
import subprocess
import sys
import threading
import time
import tempfile
import fcntl
import platform

ROOTS = ['v4_09316', 'v4_09317', 'v4_09322', 'v4_09323', 'v4_09331', 'v4_09332', 'v4_09333']
EXPECTED = 'ae44c1274c5c3c646f964475e3c6a6057bb11525105144e2f41126ad54f0ebbb'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def audit(main, star):
    errors = []
    def check(value, label):
        if not value:
            errors.append(label)
    inventory = []
    def read_zip(path):
        with zipfile.ZipFile(path) as z:
            check(z.testzip() is None, 'CRC:' + str(path))
            names = z.namelist()
            check(len(names) == len(set(names)), 'duplicate ZIP names')
            check(all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names), 'unsafe names')
            data = {n: z.read(n) for n in names}
        for n, b in data.items():
            inventory.append({'archive': path.name, 'path': n, 'bytes': len(b), 'sha256': sha(b)})
        return data
    if sha(main.read_bytes()) != EXPECTED:
        raise ValueError('Originalarchiv: falsche SHA256; Abbruch vor Auswertung')
    data = read_zip(main)
    state, manifest, summary, policy, harvest = [json.loads(data[n + '.json']) for n in ['state', 'manifest', 'summary', 'policy_changes', 'harvest_manifest']]
    check(sha(data['manifest.json']) == policy['base_manifest_sha256'], 'policy base manifest')
    check(manifest['old_tree_state_sha256'] == harvest['old_tree_state_sha256'], 'old scout hash agreement')
    check(set(manifest['roots']) == set(ROOTS) == set(manifest['root_hashes']) == set(summary['roots']), 'root sets')
    nodes = state['cubes']
    children = collections.defaultdict(list)
    for key, c in nodes.items():
        check(key == c['id'], 'id:' + key)
        check(c['root_id'] in ROOTS, 'root:' + key)
        check(c['depth'] == len(c['lits']), 'depth:' + key)
        check(all(type(v) is int and v != 0 for v in c['lits']), 'literal type:' + key)
        check(len({abs(v) for v in c['lits']}) == len(c['lits']), 'repeated variable:' + key)
        if c['parent'] is None:
            check(key in ROOTS and c['root_id'] == key and c['lits'] == [], 'root shape:' + key)
        else:
            children[c['parent']].append(key)
            check(c['parent'] in nodes, 'missing parent:' + key)
        check(c['status'] in ['SPLIT', 'CERTIFIED'], 'open status:' + key)
    visited = set()
    counts = {}
    warnings = []
    leaf_rows = []
    for root in ROOTS:
        stack = [root]
        rc = collections.Counter()
        while stack:
            key = stack.pop()
            check(key not in visited, 'cycle or repeated node:' + key)
            if key in visited:
                continue
            visited.add(key)
            c = nodes[key]
            check(c['root_id'] == root, 'cross-root:' + key)
            rc[c['status']] += 1
            if c['status'] == 'SPLIT':
                kids = children[key]
                check(set(kids) == {key + '0', key + '1'}, 'children:' + key)
                v = c['split_var']
                check(type(v) is int and v > 0 and v not in {abs(x) for x in c['lits']}, 'split variable:' + key)
                for suffix, lit in [('0', -v), ('1', v)]:
                    child = nodes.get(key + suffix, {})
                    check(child.get('lits') == c['lits'] + [lit], 'complementary extension:' + key + suffix)
                    check(child.get('parent') == key, 'parent:' + key + suffix)
                stack.extend(kids)
            else:
                check(not children[key], 'leaf with children:' + key)
                sol, ck = c['solver'], c['checker']
                check(sol['exit'] == 20 and ck['lrat_exit'] == ck['cake_exit'] == 0, 'exit:' + key)
                check(ck['lrat_marker'] is True and ck['cake_marker'] is True, 'stored marker:' + key)
                check(ck['status'] == 'CERTIFIED' and sol['status'] == 'UNSAT_READY', 'nested status:' + key)
                check(sol['proof_sha256'] == ck['proof_raw_sha256'], 'raw hash link:' + key)
                check(sol['proof_bytes'] == ck['proof_raw_bytes'], 'raw length link:' + key)
                for h in [sol['leaf_cnf_sha256'], sol['proof_sha256'], ck['proof_gz_sha256']]:
                    check(re.fullmatch('[0-9a-f]{64}', h) is not None, 'hash syntax:' + key)
                check(ck['proof_gz_bytes'] > 0 and ck['proof_raw_bytes'] > 0, 'proof sizes:' + key)
                logs = {}
                for tool in ['cadical', 'lrat', 'cake']:
                    for ext in ['out', 'err']:
                        name = key + '/' + tool + '.' + ext
                        check(name in data, 'missing log:' + name)
                        logs[tool + '.' + ext] = data.get(name, b'').decode('utf-8')
                        for line_no, line in enumerate(logs[tool + '.' + ext].splitlines(), 1):
                            if re.search(r'warn|error|invalid|fail|incorrect', line, re.I):
                                warnings.append({'leaf': key, 'file': tool + '.' + ext, 'line': line_no, 'text': line})
                        check(ext != 'err' or logs[tool + '.' + ext] == '', 'nonempty stderr:' + name)
                check('c VERIFIED' in logs['lrat.out'].splitlines(), 'LRAT marker:' + key)
                check(logs['cake.out'] == 's VERIFIED UNSAT\n', 'Cake marker:' + key)
                check('c exit 20' in logs['cadical.out'].splitlines(), 'solver exit log:' + key)
                parsed = re.search(r'parsed a formula with (\d+) variables and (\d+) clauses', logs['lrat.out'])
                check(parsed is not None, 'LRAT formula header:' + key)
                leaf_rows.append({'leaf': key, 'root': root, 'depth': c['depth'], 'cnf_sha256': sol['leaf_cnf_sha256'], 'raw_sha256': ck['proof_raw_sha256'], 'gz_sha256': ck['proof_gz_sha256'], 'raw_bytes': ck['proof_raw_bytes'], 'gz_bytes': ck['proof_gz_bytes'], 'parsed': list(map(int, parsed.groups())) if parsed else None})
        counts[root] = dict(rc)
        check(rc['CERTIFIED'] == rc['SPLIT'] + 1, 'full tree count:' + root)
        check(sum(rc.values()) == state['coverage_audit'][root] == summary['coverage_audit'][root], 'coverage count:' + root)
    check(visited == set(nodes), 'unreachable nodes')
    check(sum(c['SPLIT'] for c in counts.values()) == state['splits'] == summary['splits'] == 890, 'split totals')
    check(len(leaf_rows) == summary['certified_leaves'] == 897, 'leaf totals')
    check(state['status'] == 'COMPLETE', 'state completion')
    expected_names = {x + '.json' for x in ['state', 'manifest', 'summary', 'policy_changes', 'harvest_manifest']}
    expected_names.update(row['leaf'] + '/' + t + '.' + e for row in leaf_rows for t in ['cadical', 'lrat', 'cake'] for e in ['out', 'err'])
    check(set(data) == expected_names, 'exact archive log coverage')
    sd = read_zip(star)
    sm = json.loads(sd['EXPORT_MANIFEST.json'])
    check(set(sm) == set(sd) - {'EXPORT_MANIFEST.json'}, 'star manifest coverage')
    for name, entry in sm.items():
        check(len(sd[name]) == entry['bytes'] and sha(sd[name]) == entry['sha256'], 'star manifest:' + name)
    ss = json.loads(sd['summary.json'])
    star_counts = collections.Counter()
    for name, b in sd.items():
        if not name.endswith('.cnf'):
            continue
        parts = name.split('/')
        star_counts[(parts[0], parts[1])] += 1
        header = None
        tokens = []
        for line in b.decode('ascii').splitlines():
            if line.startswith('c') or not line.strip():
                continue
            if line.startswith('p'):
                check(header is None, 'duplicate CNF header:' + name)
                header = line.split()
            else:
                tokens.extend(map(int, line.split()))
        check(header is not None and header[:2] == ['p', 'cnf'], 'CNF header:' + name)
        nv, nc = map(int, header[2:])
        check(tokens[-1] == 0 and tokens.count(0) == nc and max(map(abs, tokens)) <= nv, 'CNF syntax:' + name)
    for r in [1, 2, 3]:
        rd = json.loads(sd[f'star_round_{r}_summary.json'])
        for root in ROOTS:
            check(star_counts[(f'star_round_{r}', root)] == rd[root]['removed_this_round'], 'star count:' + str((r, root)))
    for result in ss['global_results']:
        if result['id'] in ROOTS:
            root = result['id']
            check(result['cnf_sha256'] == manifest['root_hashes'][root], 'cross archive root hash:' + root)
            for row in leaf_rows:
                if row['root'] == root:
                    check(row['parsed'] == [result['vars'], result['clauses'] + row['depth']], 'leaf formula dimensions:' + row['leaf'])
    result = {'scope': 'metadata_tree_archived_logs_only', 'proofs_rechecked': 0, 'solver_s_UNSATISFIABLE_markers': sum(b's UNSATISFIABLE' in b for n, b in data.items() if n.endswith('/cadical.out')),  'errors': errors, 'counts': counts, 'nodes': len(nodes), 'leaves': len(leaf_rows), 'splits': state['splits'], 'warning_lines': len(warnings), 'warning_leaves': len({x['leaf'] for x in warnings}), 'warnings_by_file': dict(collections.Counter(x['file'] for x in warnings)), 'star_counts': {a + '/' + b: n for (a, b), n in star_counts.items()}, 'total_raw_proof_bytes_recorded': sum(x['raw_bytes'] for x in leaf_rows), 'total_gz_proof_bytes_recorded': sum(x['gz_bytes'] for x in leaf_rows), 'archives': [{'name': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())} for p in [main, star]]}
    return result, inventory, warnings, leaf_rows


VERSION = 'K66-RYZEN-AUDIT-1.0.1'
STAR_SHA = '11287fffa90e6700c7fea159d8c9e948e92418ca3b875c3a3e9556ff45bc3be0'


def atomic_json(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    temp.replace(path)


class Progress:
    def __init__(self):
        self.phase = 'Start'
        self.done = 0
        self.total = 0
        self.started = time.monotonic()
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def set(self, phase, total=0):
        self.phase, self.done, self.total = phase, 0, total
        self.started = time.monotonic()
        self.report()

    def report(self):
        elapsed = time.monotonic() - self.started
        eta = ((self.total - self.done) * elapsed / self.done) if self.done and self.total else None
        print(json.dumps({'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'phase': self.phase, 'completed': self.done, 'total': self.total, 'elapsed_seconds': round(elapsed), 'eta_seconds': round(eta) if eta is not None else None, 'eta_basis': 'completed items; proof sizes vary'}), flush=True)

    def loop(self):
        while not self.stop.wait(600):
            self.report()


def file_signature(path):
    s = path.stat()
    return [str(path.resolve()), s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def stream_hash(path, compressed=False):
    h = hashlib.sha256()
    length = 0
    opener = gzip.open if compressed else open
    with opener(path, 'rb') as f:
        while True:
            block = f.read(4 * 1024 * 1024)
            if not block:
                break
            h.update(block)
            length += len(block)
    return {'bytes': length, 'sha256': h.hexdigest()}


def locate_archive(downloads, stem, expected):
    candidates = sorted(downloads.glob(stem + '*.zip'))
    for path in candidates:
        if stream_hash(path)['sha256'] == expected:
            return path
    raise FileNotFoundError('Kein Archiv mit erwarteter SHA256: ' + str(downloads / (stem + '*.zip')))


def checker_controls(output, manifest):
    tests = [
        ('positive_units', 'p cnf 1 2\n1 0\n-1 0\n', '3 0 1 2 0\n', True),
        ('positive_chain', 'p cnf 2 3\n1 0\n-1 2 0\n-2 0\n', '4 0 1 2 3 0\n', True),
        ('negative_user', 'p cnf 1 2\n1 0\n1 0\n', '3 0 1 2 0\n', False),
        ('negative_missing_conflict', 'p cnf 1 2\n1 0\n-1 0\n', '3 0 1 0\n', False),
        ('negative_empty', 'p cnf 1 2\n1 0\n-1 0\n', '', False),
    ]
    results = []
    for tool, names in [('lrat-check', ['lrat-check']), ('cake', ['cake_lpr', 'cake'])]:
        candidates = []
        for name in names:
            for p in [Path.home() / '.local/bin' / name, Path(shutil.which(name)) if shutil.which(name) else None]:
                if p is not None and p.is_file() and p not in candidates:
                    candidates.append(p)
        chosen = next((p for p in candidates if stream_hash(p)['sha256'] == manifest['tool_hashes'][tool]), None)
        if chosen is None:
            results.append({'tool': tool, 'status': 'MISSING_EXACT_ARCHIVED_BINARY', 'expected_sha256': manifest['tool_hashes'][tool], 'candidates': [{'path': str(p), 'sha256': stream_hash(p)['sha256']} for p in candidates]})
            continue
        tool_results = []
        for name, cnf, proof, valid in tests:
            case = output / 'controls' / tool / name
            case.mkdir(parents=True, exist_ok=True)
            (case / 'input.cnf').write_text(cnf)
            (case / 'proof.lrat').write_text(proof)
            try:
                run = subprocess.run([str(chosen), str(case / 'input.cnf'), str(case / 'proof.lrat')], capture_output=True, text=True, timeout=30)
                (case / 'stdout.txt').write_text(run.stdout)
                (case / 'stderr.txt').write_text(run.stderr)
                marker = bool(re.search(r'^(?:c VERIFIED|s VERIFIED UNSAT)\s*$', run.stdout, re.M))
                diagnostic = bool(re.search(r'warn|error|invalid|fail|incorrect|empty clause not derived at end of proof', run.stdout + run.stderr, re.I))
                clean_accept = run.returncode == 0 and marker and not diagnostic and not run.stderr.strip()
                explicit_reject = not marker and (run.returncode != 0 or diagnostic)
                passed = clean_accept if valid else explicit_reject
                tool_results.append({'case': name, 'expected_valid': valid, 'exit': run.returncode, 'positive_marker': marker, 'warning_or_error': diagnostic, 'pass': passed})
            except subprocess.TimeoutExpired:
                tool_results.append({'case': name, 'pass': False, 'error': 'CONTROL_TIMEOUT'})
        results.append({'tool': tool, 'path': str(chosen), 'sha256': stream_hash(chosen)['sha256'], 'status': 'PASS' if all(r['pass'] for r in tool_results) else 'FAIL', 'cases': tool_results})
    atomic_json(output / 'checker_controls.json', results)
    return results


def local_files(output, state, manifest, checkpoint, progress):
    tasks = []
    for root, path in manifest['roots'].items():
        tasks.append((root + ':root', Path(path), False, manifest['root_hashes'][root], None))
    for key, node in state['cubes'].items():
        if node['status'] != 'CERTIFIED':
            continue
        ck, sol = node['checker'], node['solver']
        tasks.append((key + ':cnf', Path(node['work']) / 'leaf.cnf', False, sol['leaf_cnf_sha256'], None))
        tasks.append((key + ':gzip', Path(ck['proof_gz']), False, ck['proof_gz_sha256'], ck['proof_gz_bytes']))
        tasks.append((key + ':raw', Path(ck['proof_gz']), True, ck['proof_raw_sha256'], ck['proof_raw_bytes']))
    progress.set('Lokale CNF- und Beweishashes; keine Beweischecker-Neupruefung', len(tasks))
    records = checkpoint.setdefault('local_files', {})
    for key, path, compressed, expected, size in tasks:
        if not path.is_file():
            records[key] = {'status': 'MISSING', 'path': str(path)}
        else:
            signature = file_signature(path)
            prior = records.get(key, {})
            if prior.get('signature') != signature or prior.get('expected_sha256') != expected or prior.get('status') != 'PASS':
                try:
                    actual = stream_hash(path, compressed)
                    unchanged = signature == file_signature(path)
                    passed = unchanged and actual['sha256'] == expected and (size is None or size == actual['bytes'])
                    records[key] = {'status': 'PASS' if passed else 'FAIL', 'signature': signature, 'expected_sha256': expected, 'actual': actual, 'unchanged_during_read': unchanged}
                except (OSError, EOFError) as e:
                    records[key] = {'status': 'FAIL', 'path': str(path), 'error': str(e)}
            atomic_json(output / 'checkpoint.json', checkpoint)
        progress.done += 1
    atomic_json(output / 'checkpoint.json', checkpoint)
    atomic_json(output / 'local_file_hashes.json', records)
    progress.report()
    return dict(collections.Counter(v['status'] for v in records.values()))


def write_report(output, metadata, controls, local_counts):
    lines = [
        '# K66: neuer lokaler Audit',
        '',
        'Dieser Bericht ersetzt keine fehlenden mathematischen Nachweise. Frühere abgeleitete Auswertungen dieses Vorgangs wurden nicht als Beweise übernommen.',
        '',
        f"Metadatenfehler: {len(metadata['errors'])}; Knoten: {metadata['nodes']}; Blätter: {metadata['leaves']}; Verzweigungen: {metadata['splits']}.",
        f"Archivierte LRAT-Warnungen: {metadata['warning_lines']} in {metadata['warning_leaves']} Blättern. Einzelheiten: warnings.json.",
        f"Lokale Dateihashes: {local_counts}. Checkpoint-Wiederverwendung nur bei identischer Programmversion, Eingabehashes und Dateisignatur (Pfad, Länge, mtime, ctime).",
        f"Kontrollen der hashidentischen Checker: {[(c['tool'], c['status']) for c in controls]}.",
        '',
        '## Getrennte Aussageebenen',
        '',
        '1. Metadaten/Bäume: audit.json prüft Eltern, Wurzeln, komplementäre Literale, Erreichbarkeit, Überdeckung, Abschlusszahlen und gespeicherte Hashverknüpfungen.',
        '2. Archivprotokolle: Exitcodes im Zustand, positive LRAT/Cake-Marker, stderr und Warnungen wurden gesondert ausgewertet. CaDiCaL enthält c exit 20; fehlende s UNSATISFIABLE-Marker werden ausgewiesen. Protokolle sind keine erneute Beweisprüfung.',
        '3. Vorhandene Dateien: root/leaf-CNF sowie gzip und dekomprimierte LRAT-Bytes wurden, soweit vorhanden, gegen gespeicherte Hashes geprüft. Die gzip-Dekompression prüft zusätzlich CRC. Hier wurden KEINE der 897 Produktionsbeweise erneut durch einen Beweischecker geprüft. Die kleinen Kontrollen betreffen nur das Checker-Verhalten.',
        '4. Mathematische Notwendigkeit und vollständige K66-Abdeckung bleiben eigene offene Beweispflichten. Aus dem Abschluss reduzierter Wurzeln folgt allein kein vollständiger K66-Ausschluss.',
        '',
        '## Offene Beweispflichten und benötigte Quellen',
        '',
        '- 125 Profilentfernungen: 124 in Runde 1, eine in Runde 2 bei v4_09317/profile_3520.cnf. CNFs sind im Star-ZIP vorhanden; gültige Beweise/Checkerprotokolle fehlen dort. Zusätzlich benötigt: exakte aktive Profillisten vor/nach jeder Runde, Profil-ID-Zuordnung, Encoder samt Quelldaten und Notwendigkeitsbeweis. Die Runde-2-Entfernung muss auf bereits gerechtfertigten Runde-1-Entfernungen beruhen.',
        '- Rekonstruktion der sieben reduzierten Wurzeln: die sieben in manifest.json bezeichneten global/*/model.cnf sowie deren Encoder-Eingaben. Hashübereinstimmung verbindet Dateien, beweist aber nicht die mathematische Richtigkeit des Encoders.',
        '- Vollständige K66-Fallabdeckung: übergeordnetes manifest.json und state.json aus k66_v4_cert_20260908_231256_132359, vollständige V4-Fallliste und alle Ausschlussnachweise außerhalb der sieben Wurzeln. Die Star-Zusammenfassung führt zusätzlich v4_09232 und 12 weitere Entfernungen; deren Abschluss ist mit diesen beiden ZIPs nicht bewiesen.',
        '- Produktionschecker: bei fehlendem oder nicht bestandenen Kontrolltest zuerst exakte Checker-Version/Build und Verhalten klären. Warnung plus VERIFIED wird nicht als saubere unabhängige LRAT-Bestätigung gewertet. Cake bleibt separat zu beurteilen.',
        '- Für echte erneute Beweisprüfung: leaf.cnf und proof.lrat.gz jedes Blattes, hashidentischer kontrollierter Checker und ein ressourcenbewusster Replay-Lauf. Dieser Audit startet keinen solchen Replay und keinen Solverlauf.',
        '- Historische Rekonstruktion: die in harvest_manifest.json und manifest.json referenzierten alten Zustände und Runner fehlen im Archiv. Die aktuelle Baumüberdeckung wurde davon unabhängig geprüft; die Historie nicht.',
        '',
        '## Reproduzieren und Fortsetzen',
        '',
        'Denselben Programmaufruf erneut ausführen. Bereits geprüfte unveränderte lokale Dateien werden übersprungen. --fresh verwirft nur Audit-Checkpoints; Originaldaten werden nie verändert.',
        'compact_report.json und REPORT.md sind die hier zurückzugebenden kleinen Ergebnisse. Große Archive/Beweise verbleiben auf dem Ryzen. Dieses Programm führt keine Git-Uploads aus.',
    ]
    (output / 'REPORT.md').write_text('\n'.join(lines) + '\n')


def main():
    parser = argparse.ArgumentParser(description=VERSION)
    parser.add_argument('--downloads', type=Path, default=Path('/mnt/c/Users/rb/Downloads'))
    parser.add_argument('--main-zip', type=Path)
    parser.add_argument('--star-zip', type=Path)
    parser.add_argument('--output', type=Path, default=Path.home() / 'conway99_workspace/k66_restart_audit_v1')
    parser.add_argument('--fresh', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    lock = (output / '.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    progress = Progress()
    try:
        progress.set('Archive lokalisieren und SHA256 pruefen')
        main_zip = args.main_zip or locate_archive(args.downloads, 'k66_deep7_coarsecert_handoff_20260913_080728', EXPECTED)
        star_zip = args.star_zip or locate_archive(args.downloads, 'k66_star125_export_20260913', STAR_SHA)
        if stream_hash(star_zip)['sha256'] != STAR_SHA:
            raise ValueError('Star-ZIP SHA256 stimmt nicht')
        identity = {'version': VERSION, 'script_sha256': stream_hash(Path(__file__))['sha256'], 'main_sha256': EXPECTED, 'star_sha256': STAR_SHA}
        checkpoint_path = output / 'checkpoint.json'
        checkpoint = json.loads(checkpoint_path.read_text()) if checkpoint_path.exists() and not args.fresh else {}
        if checkpoint.get('identity') != identity:
            checkpoint = {'identity': identity}
        progress.set('ZIP-Inventar, Baeume, Metadaten und archivierte Protokolle')
        metadata, inventory, warnings, links = audit(main_zip, star_zip)
        for name, result in [('audit.json', metadata), ('inventory.json', inventory), ('warnings.json', warnings), ('leaf_hash_links.json', links)]:
            atomic_json(output / name, result)
        with zipfile.ZipFile(main_zip) as z:
            manifest, state = [json.loads(z.read(n + '.json')) for n in ['manifest', 'state']]
        if metadata['errors']:
            raise ValueError('Metadatenfehler: siehe audit.json; keine automatische Fortsetzung')
        progress.set('Positive und negative Checker-Kontrollen')
        controls = checker_controls(output, manifest)
        counts = local_files(output, state, manifest, checkpoint, progress)
        write_report(output, metadata, controls, counts)
        compact = {'version': VERSION, 'status': 'LOCAL_AUDIT_COMPLETE_WITH_OPEN_PROOF_OBLIGATIONS', 'identity': identity, 'metadata_errors': metadata['errors'], 'counts': metadata['counts'], 'lrat_warning_lines': metadata['warning_lines'], 'lrat_warning_leaves': metadata['warning_leaves'], 'local_file_hashes': counts, 'checker_controls': controls, 'production_proofs_rechecked': 0, 'star_profile_cnfs': sum(metadata['star_counts'].values()), 'output': str(output)}
        atomic_json(output / 'compact_report.json', compact)
        print('K66_COMPACT_REPORT ' + json.dumps(compact), flush=True)
        print('FERTIG. Bitte nur compact_report.json bzw. diese kompakte Konsolenausgabe zurueckgeben.', flush=True)
        return 0 if not counts.get('FAIL') else 2
    finally:
        progress.stop.set()
        lock.close()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print('Unterbrochen. Derselbe Befehl setzt anhand der Checkpoints fort.', flush=True)
        raise SystemExit(130)
