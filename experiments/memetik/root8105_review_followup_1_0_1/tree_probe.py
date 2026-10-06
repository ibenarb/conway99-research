"""Unbiased inverse-proposal-probability tree walks, with explicit variance gates.

Each local row proposal is uniform on an EXACTLY counted superset; rejected
proposals contribute zero, not a replacement draw. Membership in historical
full-star F is checked by SAT. Therefore weights are products of proposal
widths, not falsely claimed exact F branching degrees. All four cells use the
same matching-representative forest to avoid confounding matching with order.
"""
import bootstrap
import collections
import json
import math
import random
import time
from pathlib import Path
from pysat.solvers import Glucose4
import historical_core as core
from kernel import Geo
from matching import edge_key, root_objects
from propagation import propagate
from row_sampler import RowProposal
from runtime import atomic, digest, fingerprint


def walk(root, objects, index, stop):
    rng = random.Random(root['seed'] + index * 1000000007)
    g = Geo()
    rows = {0: int(root['row'], 16)}
    choices = objects['classes']
    if not choices:
        return {'weights': [0] * root['max_depth'], 'termination': 'NO_MATCHING', 'index': index}
    chosen = rng.randrange(len(choices))
    matching = choices[chosen]['matching']
    mset = {edge_key(*p) for p in matching}
    neighbors = [v for v in range(g.n) if rows[0] >> v & 1]
    assignments = {edge_key(u, v): int(edge_key(u, v) in mset)
                   for i, u in enumerate(neighbors) for v in neighbors[i + 1:]}
    order = list(range(1, g.n)) if root['order'] == 'numeric' else (
        [v for pair in matching for v in pair] + sorted(objects['special_border_paired']))
    weight = len(choices)
    weights = [weight]
    steps = []
    terminal = 'DEPTH_REACHED'
    for target in order[:root['max_depth'] - 1]:
        if stop():
            return None
        begun = time.process_time()
        if root['propagation']:
            prop = propagate(g, rows, assignments)
            if not prop['pass']:
                terminal = 'PROPAGATION:' + prop['reason']
                break
            assignments = prop['assigned']
        proposal = RowProposal(g, rows, target, assignments)
        total = proposal.total
        build_cpu = time.process_time() - begun
        if not total:
            proposal.rec.cache_clear()
            terminal = 'EMPTY_LOCAL_PROPOSAL'
            break
        rank = rng.randrange(total)
        row = proposal.unrank(rank)
        proposal.rec.cache_clear()
        if stop():
            return None
        cnf, variables = core.encode(core.Geometry(), rows, target)
        _, free = core.projection(core.Geometry(), rows, target, variables)
        assumptions = [lit if row >> v & 1 else -lit for v, lit in free]
        assumptions += [lit if assignments[pair] else -lit for pair, lit in variables.items()
                        if pair in assignments]
        with Glucose4(bootstrap_with=cnf.clauses) as solver:
            member = solver.solve(assumptions=assumptions)
        if member is None:
            raise RuntimeError('UNKNOWN membership cannot be recorded as an extinct branch')
        steps.append({'target': target, 'proposal_width': total, 'rank': rank,
                      'sampler_cpu_s': build_cpu, 'cpu_s': time.process_time() - begun,
                      'F_projection_member': member})
        if not member:
            terminal = 'REJECTED_PROPOSAL_NOT_EMPTY_F_BRANCH'
            break
        child = rows | {target: row}
        g.verify(child)
        if root['propagation']:
            prop = propagate(g, child, assignments)
            if not prop['pass']:
                terminal = 'PROPAGATION:' + prop['reason']
                break
            assignments = prop['assigned']
        rows = child
        weight *= total
        weights.append(weight)
    reached = len(weights)
    weights += [0] * (root['max_depth'] - len(weights))
    return {'index': index, 'matching_class': chosen, 'matching_orbit_size': choices[chosen]['orbit_size'],
            'weights': weights, 'termination': terminal, 'reached_rows': reached, 'steps': steps,
            'target_depth': root['max_depth'], 'tree': 'shared matching-representative forest; no deeper symmetry quotient'}


def run_job(root, output, stop, progress):
    beginning = time.process_time()
    objects = root_objects(Geo(), int(root['row'], 16))
    assert objects['stabilizer_order'] == root['stab']
    # A root/cell checkpoint survives attempt changes; completed walks are never redrawn.
    checkpoint = Path(output).parent / ('tree-checkpoint-' + str(root['id']) + '.json')
    identity = digest({'root': root, 'code_hash': fingerprint()['code_hash']})
    saved = json.loads(checkpoint.read_text()) if checkpoint.exists() else {'identity': identity, 'records': []}
    if saved['identity'] != identity:
        raise ValueError('tree checkpoint identity mismatch')
    records = saved['records']
    assert [r['index'] for r in records] == list(range(len(records)))
    for index in range(len(records), root['walks']):
        if stop():
            return None
        rec = walk(root, objects, index, stop)
        if rec is None:
            return None
        records.append(rec)
        progress(index + 1)
        atomic(checkpoint, {'identity': identity, 'records': records})
    atomic(checkpoint, {'identity': identity, 'records': records})
    return {'width': len(records), 'cpu_s': time.process_time() - beginning, 'root_id': root['root_id'],
            'cell': root['cell'], 'order': root['order'], 'propagation': root['propagation'],
            'matching_raw_count': objects['raw_count'], 'matching_orbits': objects['orbit_count'],
            'records': records, 'status': 'COMPLETE'}


def log10_mean(values):
    total = sum(values)
    return None if not total else math.log10(total) - math.log10(len(values))


def summarize(con):
    cells = collections.defaultdict(list)
    for rec in con.execute('SELECT payload FROM results'):
        value = json.loads(rec[0])['counts']['1']
        cells[value['cell']].append(value)
    report = {}
    for cell, roots in cells.items():
        final = [sum(r['weights']) for j in roots for r in j['records']]
        terminal_positive = sum(r['weights'][-1] > 0 for j in roots for r in j['records'])
        positive = sum(v > 0 for v in final)
        total = sum(final)
        square = sum(v * v for v in final)
        ess = (total * total / square) if square else 0
        terminations = collections.Counter(r['termination'] for j in roots for r in j['records'])
        # Equal weighting of the 24 fixed roots; allocated draw counts may differ by one.
        root_means = [sum(sum(r['weights']) for r in j['records']) / len(j['records']) for j in roots]
        mean24 = sum(root_means) / len(root_means)
        resolved = len(final) >= 10000 and len(roots) == 24 and terminal_positive >= 100 and ess >= 100
        ci = None
        if resolved:
            rng = random.Random(810520261010)
            boot = []
            arrays = [[sum(r['weights']) for r in j['records']] for j in roots]
            for _ in range(1000):
                estimate = sum(sum(rng.choices(vals, k=len(vals))) / len(vals) for vals in arrays) / 24
                boot.append(estimate)
            boot.sort()
            ci = [math.log10(boot[24]) if boot[24] else None,
                  math.log10(boot[974]) if boot[974] else None]
        report[str(cell)] = {'completed_roots': len(roots), 'walks': len(final),
            'positive_terminal_weights': terminal_positive, 'importance_weight_ESS': ess,
            'max_weight_fraction': max(final) / total if total else None,
            'log10_mean_cumulative_nodes_per_selected_root': math.log10(mean24) if mean24 else None,
            'bootstrap95_log10_conditional_on_selected_roots': ci,
            'inference_status': 'EXPLORATORY_INTERVAL_NOT_BOUND' if resolved else 'INSUFFICIENT_INFORMATION',
            'termination_counts': dict(terminations),
            'depth_survival': [{'rows': d + 1, 'positive_walks': sum(r['weights'][d] > 0 for j in roots for r in j['records']),
                'log10_mean_nodes': log10_mean([r['weights'][d] for j in roots for r in j['records']])}
                for d in range(len(roots[0]['records'][0]['weights']))]}
    comparison = {'status': 'INSUFFICIENT_INFORMATION'}
    if len(report) == 4 and all(r['inference_status'] == 'EXPLORATORY_INTERVAL_NOT_BOUND' for r in report.values()):
        base = {j['root_id']: [sum(r['weights']) for r in j['records']] for j in cells[0]}
        strong = {j['root_id']: [sum(r['weights']) for r in j['records']] for j in cells[3]}
        rng = random.Random(810520261011)
        ratios = []
        for _ in range(1000):
            b, s = 0., 0.
            for rid, values in base.items():
                ids = [rng.randrange(len(values)) for _ in values]
                b += sum(values[i] for i in ids) / len(ids)
                s += sum(strong[rid][i] for i in ids) / len(ids)
            ratios.append(s / b)
        ratios.sort()
        comparison = {'status': 'EXPLORATORY_PAIRED_BOOTSTRAP', 'new_strong_over_old_F_95': [ratios[24], ratios[974]],
            'two_orders_candidate': ratios[974] <= .01, 'not_a_rigorous_bound': True}
    return {'comparison': comparison, 'status': 'TREE_PROBE_COMPLETE' if len(cells) == 4 and all(len(v) == 24 for v in cells.values()) else 'PARTIAL',
            'cells': report, 'scope': 'selected 24 roots only; depth-limited tree, NOT total SRG search',
            'global_8105_extrapolation': 'NOT_IDENTIFIED_BY_THIS_ROOT_SELECTION',
            'budget_upper_bound': None, 'time_or_resource_censored_walks_may_not_be_counted_as_zero': True}
