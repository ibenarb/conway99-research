"""Finite independent validity/score checks for AP and full-star catalogues."""
import argparse
import json
from pathlib import Path
import tempfile
from threading import Event
import catalog
import verify
from common import cpu, atomic, read


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pool')
    parser.add_argument('--census')
    args = parser.parse_args()
    rook = [{j for j in range(9) if j != i and (j // 3 == i // 3 or j % 3 == i % 3)}
            for i in range(9)]
    g = verify.encode(rook)
    verify.checked(g, degree=4)
    assert list(catalog.star_moves(catalog.bits(g), catalog.Guard())) == []
    for _, move in catalog.catalogue(catalog.bits(g), True):
        verify.checked(catalog.graph6(catalog.apply_move(catalog.bits(g), move)), degree=4)
    report = {'rook_no_star': True, 'checked_moves': 0, 'fixtures': []}
    if args.pool:
        pool = json.loads(Path(args.pool).read_text())
        if isinstance(pool, dict):
            pool = pool.get('candidates', pool.get('classes', pool.get('founders')))
        expected = {r['state']: r for r in json.loads(Path(args.census).read_text())} if args.census else {}
        improving_star = 0
        resume_fixture = None
        for rec in pool:
            base = verify.record(rec['graph6'])
            rows = catalog.bits(rec['graph6'])
            scorer = catalog.Scorer(rows)
            assert scorer.scores == base['scores']
            stars = list(catalog.star_moves(rows, catalog.Guard()))
            scores = []
            for move in stars:
                child, score = scorer.evaluate(move)
                full = verify.record(catalog.graph6(child))
                assert score == full['scores']
                assert catalog.apply_move(child, (move[1], move[0])) == rows
                scores.append(verify.key(score))
                improving_star += verify.key(score) < verify.key(base['scores'])
                if verify.key(score) < verify.key(base['scores']):
                    resume_fixture = rec, full
                report['checked_moves'] += 1
            if base['state'] in expected:
                target = expected[base['state']]
                assert len(stars) == target['valid_moves']
                assert list(min(scores)) == target['best']
            aps = list(catalog.catalogue(rows, False))
            extended = list(catalog.catalogue(rows, True))
            assert extended[:len(aps)] == aps
            assert len(set(m for _, m in extended)) == len(extended)
            for name, move in aps:
                child, score = scorer.evaluate(move)
                assert score == verify.record(catalog.graph6(child))['scores']
                assert catalog.apply_move(child, (move[1], move[0])) == rows
                report['checked_moves'] += 1
            report['fixtures'].append({'state': base['state'], 'ap': len(aps),
                                       'star_raw': len(stars), 'combined': len(extended)})
        assert improving_star > 0, 'Pool must contain known improving star witness'
        report['improving_star_witnesses'] = improving_star
        with tempfile.TemporaryDirectory() as directory:
            event = Event()
            event.set()
            result = catalog.run_task(pool[0], {'arm': 'AP', 'seed': 42}, directory, 10, cpu() + 10, event)
            assert result['status'] == 'STOP_REQUESTED'
            assert result['best'] == verify.record(pool[0]['graph6'])
            result = catalog.run_task(pool[0], {'arm': 'AP_STAR', 'seed': 42}, directory, 0, cpu(), Event())
            assert result['status'] == 'CPU_BUDGET'
            assert result['completed_censuses'] == 0
            assert read(Path(directory) / 'best.json') == result['best']
            assert read(Path(directory) / 'catalog_archive.json') == result['archive']
        with tempfile.TemporaryDirectory() as directory:
            parent, incumbent = resume_fixture
            atomic(Path(directory) / 'best.json', incumbent)
            paused = Event()
            paused.set()
            result = catalog.run_task(parent, {'arm': 'AP_STAR', 'seed': 91}, directory, 10, cpu() + 10, paused)
            assert result['best'] == incumbent
            assert read(Path(directory) / 'best.json') == incumbent
            assert read(Path(directory) / ('candidate_' + incumbent['state'] + '.json')) == incumbent
            result = catalog.run_task(parent, {'arm': 'AP_STAR', 'seed': 91}, directory, 0, cpu(), Event())
            assert result['best'] == incumbent
            assert incumbent in read(Path(directory) / 'catalog_archive.json')
            damaged = dict(incumbent, state='forged')
            atomic(Path(directory) / 'best.json', damaged)
            try:
                catalog.run_task(parent, {'arm': 'AP_STAR', 'seed': 91}, directory, 0, cpu(), Event())
            except ValueError:
                pass
            else:
                raise AssertionError('Forged resume incumbent accepted')
        report['durable_incumbent_resume_and_corruption_rejection'] = True
    print(json.dumps({'status': 'PASS', **report}, indent=2))


if __name__ == '__main__':
    main()
