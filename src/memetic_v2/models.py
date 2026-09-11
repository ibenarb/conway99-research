"""Exact finite CP-SAT subproblems for starts and Omega recombination.

Only proven feasible assignments are returned. UNKNOWN is an exhausted
subproblem, never a mathematical exclusion of a search arm.
"""

from collections import defaultdict
from itertools import combinations
import random
import time

from core import OUTER, OUTER_INDEX, BudgetEnd, canonical, edge, from_edges, reconstruct, validate


def cp_api():
    from ortools.sat.python import cp_model
    return cp_model


def solver_for(seed, budget):
    cp = cp_api()
    solver = cp.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = seed % 2147483647
    solver.parameters.max_time_in_seconds = budget.remaining()
    solver.parameters.max_memory_in_mb = 768
    solver.parameters.log_search_progress = False
    solver.parameters.stop_after_first_solution = True
    return solver


def solve_once(model, seed, budget):
    budget.check()
    solver = solver_for(seed, budget)
    started = time.process_time()
    status = solver.solve(model)
    report = {"status": solver.status_name(status),
              "cpu_seconds": time.process_time() - started,
              "solver_wall_seconds": solver.wall_time,
              "conflicts": solver.num_conflicts, "branches": solver.num_branches,
              "variables": len(model.proto.variables),
              "constraints": len(model.proto.constraints)}
    return solver, status, report


def add_random_objective(model, variables, rng, reference=None):
    terms = []
    for pair, var in variables.items():
        if reference is None:
            weight = rng.choice((-3, -2, -1, 1, 2, 3))
        else:
            weight = -1 if reference.get(pair, False) else 1
        terms.append(weight * var)
    model.minimize(sum(terms))


def omega_start(method, rng, seed, budget):
    cp = cp_api()
    model = cp.CpModel()
    variables = {(u, v): model.new_bool_var(f"h{u}_{v}") for u, v in combinations(range(84), 2)}

    def h(u, v):
        return variables[edge(u, v)]

    for column, pair in enumerate(OUTER):
        budget.check()
        for label in range(14):
            target = 1 if label in pair or (label + 7) % 14 in pair else 2
            model.add(sum(h(column, row) for row, rp in enumerate(OUTER) if row != column and label in rp) == target)
    description = {"method": method, "hard_conditions": "Omega P-margins, symmetry, binary, zero diagonal"}
    if method == "algebraic":
        step = rng.choice((1, 2, 7))
        perm = [OUTER_INDEX[edge((a + step) % 14, (b + step) % 14)] for a, b in OUTER]
        for (u, v), var in variables.items():
            model.add(var == h(perm[u], perm[v]))
        description["translation_step"] = step
    reference = None
    if method == "repair":
        # A newly generated, generally invalid matrix. This is NOT a search
        # excursion that permits invalid intermediate population states.
        reference = {p: rng.random() < 12 / 83 for p in variables}
        description["proposal"] = "Independent Bernoulli outer matrix, p=12/83"
    add_random_objective(model, variables, rng, reference)
    solver, status, report = solve_once(model, seed, budget)
    description["solver"] = report
    if status not in (cp.FEASIBLE, cp.OPTIMAL):
        return None, description
    hrows = [0] * 84
    for (u, v), var in variables.items():
        if solver.value(var):
            hrows[u] |= 1 << v
            hrows[v] |= 1 << u
    result = reconstruct(tuple(hrows))
    validate(result, "omega")
    return result, description


def lambda_start(method, rng, seed, budget):
    """Degree model with exact, lazily added lambda constraints.

    Each violated edge pair is permanently constrained. A valid return is
    checked for ALL edges, including those never present in a separation.
    Model growth is bounded by the same task CPU and external RSS guards.
    """
    cp = cp_api()
    model = cp.CpModel()
    pairs = list(combinations(range(99), 2))
    variables = {p: model.new_bool_var(f"e{p[0]}_{p[1]}") for p in pairs}

    def a(u, v):
        return variables[edge(u, v)]

    for u in range(99):
        model.add(sum(a(u, v) for v in range(99) if u != v) == 14)
    description = {"method": method, "separations": [], "hard_conditions": "99 vertices, degree 14, lambda=1 on every edge"}
    if method == "algebraic":
        # One documented symmetry family, without assuming it is feasible.
        for (u, v), var in variables.items():
            model.add(var == a((u + 33) % 99, (v + 33) % 99))
        description["symmetry"] = "Translation by 33 on Z99 (order 3)"
    reference = None
    if method == "repair":
        labels = list(range(99))
        rng.shuffle(labels)
        reference_edges = {edge(labels[u], labels[(u + d) % 99]) for u in range(99) for d in range(1, 8)}
        reference = {p: p in reference_edges for p in pairs}
        description["proposal"] = "Relabeled circulant degree-14 proposal; not declared lambda-valid"
    add_random_objective(model, variables, rng, reference)
    constrained = set()
    while True:
        solver, status, report = solve_once(model, seed, budget)
        description["separations"].append(report)
        if status not in (cp.FEASIBLE, cp.OPTIMAL):
            return None, description
        candidate = from_edges(99, [p for p, var in variables.items() if solver.value(var)])
        bad = [(u, v) for u, v in pairs if candidate[u] & (1 << v) and (candidate[u] & candidate[v]).bit_count() != 1]
        if not bad:
            validate(candidate, "lambda")
            return candidate, description
        new = [p for p in bad if p not in constrained]
        if not new:
            raise RuntimeError("Lambda separation failed to enforce an existing constraint")
        for u, v in new:
            budget.check()
            common = []
            for w in range(99):
                if w in (u, v):
                    continue
                z = model.new_bool_var(f"c{u}_{v}_{w}")
                model.add(z <= a(u, w))
                model.add(z <= a(v, w))
                model.add(z >= a(u, w) + a(v, w) - 1)
                common.append(z)
            model.add(sum(common) == 1).only_enforce_if(a(u, v))
            constrained.add((u, v))
        # Hints guide the next exact solve; they do not relax any condition.
        model.clear_hints()
        for (u, v), var in variables.items():
            model.add_hint(var, int(bool(candidate[u] & (1 << v))))


def crossover(first, second, rng, seed, budget):
    cp = cp_api()
    validate(first, "omega")
    validate(second, "omega")
    differing = [(u, v) for u, v in combinations(range(84), 2) if bool(first[u + 15] & (1 << (v + 15))) != bool(second[u + 15] & (1 << (v + 15)))]
    if len(differing) < 2:
        return None, {"status": "NO_PROPER_DIFFERENCE"}
    model = cp.CpModel()
    choices = {p: model.new_bool_var(f"take{p[0]}_{p[1]}") for p in differing}
    constraints = defaultdict(list)
    for (u, v), choice in choices.items():
        sign = -1 if first[u + 15] & (1 << (v + 15)) else 1
        for label in OUTER[u]:
            constraints[(v, label)].append(sign * choice)
        for label in OUTER[v]:
            constraints[(u, label)].append(sign * choice)
    for terms in constraints.values():
        model.add(sum(terms) == 0)
    count = sum(choices.values())
    model.add(count >= 1)
    model.add(count <= len(choices) - 1)
    target = rng.choice((25, 50, 75))
    deviation = model.new_int_var(0, 100 * len(choices), "target_deviation")
    model.add_abs_equality(deviation, 100 * count - target * len(choices))
    model.minimize(deviation)
    parents = {canonical(first), canonical(second)}
    reports = []
    rejected = 0
    while True:
        solver, status, report = solve_once(model, seed, budget)
        reports.append(report)
        information = {"status": report["status"], "target_percent": target,
                       "different_undirected_pairs": len(choices),
                       "rejected_parent_isomorphs": rejected, "solver_calls": reports}
        if status not in (cp.FEASIBLE, cp.OPTIMAL):
            return None, information
        selected = {p for p, var in choices.items() if solver.value(var)}
        rows = list(first)
        for u, v in selected:
            rows[u + 15] ^= 1 << (v + 15)
            rows[v + 15] ^= 1 << (u + 15)
        rows = tuple(rows)
        validate(rows, "omega")
        if canonical(rows) not in parents:
            information.update({"status": "VALID_PROPER_RECOMBINATION", "actual_percent": 100 * len(selected) / len(choices)})
            return rows, information
        rejected += 1
        model.add(sum((1 - var) if p in selected else var for p, var in choices.items()) >= 1)
        budget.check()
