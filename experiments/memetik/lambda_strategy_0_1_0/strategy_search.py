"""A0/A1 episodes, population selection and bounded labelled visit memory."""
from collections import Counter
import math
import random
import time

from common import core, cpu, checked, sha
from fast_moves import MoveSource

OBSERVER = lambda rows, scores, name: None


def key(scores, target):
    return tuple(scores[k] for k in (("Linf", "Nmax", "L1") if target == "Linf" else ("W", "L1") if target == "W" else (target,)))


def identity(graph6):
    return sha(graph6.encode())


def candidate(rows, arm, family, line, parent, costs):
    from generate import structure
    started = cpu()
    graph6 = core.encode_g6(rows)
    _, scores = checked(graph6, arm)
    fixed_template = structure(rows, family)
    costs["verification"] += cpu() - started
    started = cpu()
    canonical = core.canonical(tuple(rows))
    costs["canonicalization"] += cpu() - started
    return {"graph6": graph6, "scores": scores, "family": family, "line": line,
            "parent": parent, "class": canonical, "state": identity(graph6),
            "fixed_source_template_holds": fixed_template}


def fresh_costs():
    return dict.fromkeys(("generation", "scoring", "verification", "canonicalization", "repair"), 0.0)


class End(core.BudgetEnd):
    pass


class Guard:
    def __init__(self, deadline, stop=lambda: False):
        self.deadline = deadline
        self.stop = stop
        self.generated = 0

    def check(self):
        if self.stop():
            raise End("PAUSED")
        if cpu() >= self.deadline:
            raise End("CPU_LIMIT")


def escape_allowed(value, current, anchor, target, step, level):
    if key(value, target) < key(current, target):
        return True
    if target == "Linf":
        return (value["Linf"] == anchor["Linf"]
                and value["Nmax"] <= anchor["Nmax"] + max(1, math.ceil(anchor["Nmax"] / 10))
                and value["L1"] <= anchor["L1"] * 105 // 100)
    cap = min(int(step) * (1 << level), anchor[target] // 10)
    return (value[target] <= anchor[target] + cap
            and (target != "W" or value["L1"] <= anchor["L1"] * 110 // 100))


def sampled(rows, arm, rng, guard, costs, count):
    source = MoveSource(rows, arm, rng, guard)
    for _ in range(count):
        started = cpu()
        try:
            found = source.next()
        finally:
            costs["generation"] += cpu() - started
        if found is None:
            return
        name, move = found
        guard.check()
        started = cpu()
        child = core.apply_move(rows, move)
        score = core.metrics(child)
        costs["scoring"] += cpu() - started
        OBSERVER(child, score, name)
        guard.check()
        yield child, score, name


def episode(parent, arm, target, variant, rng, config, memory, failures, deadline,
            stop=lambda: False, on_best=lambda rows, scores: None):
    costs = fresh_costs()
    rows = core.decode_g6(parent["graph6"])
    scores = dict(parent["scores"])
    maxima = dict(scores)
    adopted_names = Counter()
    anchor = dict(scores)  # Fixed for the ENTIRE episode; never cumulative drift.
    ranges = [(2, 4), (5, 12), (13, 32)]
    recipe = rng.choices(range(3), (4, 3, 2))[0]
    # No fresh/repair generator is enabled in confirmation. Its 10% is openly
    # redistributed in proportion 4:3:2, identically in A0 and A1.
    if variant == "A1" and failures >= 8:
        recipe = 2
    desired = rng.randint(*ranges[recipe])
    record = {"recipe": recipe, "requested": desired, "perturb_trades": 0,
              "descent_trades": 0, "neutral_trades": 0, "escape_trades": 0,
              "source_line": parent["line"], "minimum_reached": False,
              "costs": costs, "status": "STALLED_SAMPLED"}
    seen = list(memory[-128:])
    state_id = identity(parent["graph6"])
    if state_id not in seen:
        seen.append(state_id)
    started = cpu()

    def adopt(child, child_scores, guard):
        nonlocal rows, scores, seen
        # Check new records before adoption: independent validation is charged.
        on_best(child, child_scores)
        guard.check()
        for metric in ("W", "L1", "F", "Linf"):
            maxima[metric] = max(maxima[metric], child_scores[metric])
        rows, scores = child, child_scores
        seen.append(identity(core.encode_g6(rows)))
        seen = seen[-128:]

    perturb = Guard(min(deadline, cpu() + config["perturb_cpu"]), stop)
    try:
        for _ in range(desired):
            item = next(sampled(rows, arm, rng, perturb, costs, 1), None)
            if item is None:
                record["perturb_stop"] = "CATALOG_EXHAUSTED"
                break
            adopt(item[0], item[1], perturb)
            adopted_names[item[2]] += 1
            record["perturb_trades"] += 1
        else:
            record["perturb_stop"] = "REQUESTED_LENGTH"
    except core.BudgetEnd as error:
        record["perturb_stop"] = str(error)
    record["minimum_reached"] = record["perturb_trades"] >= ranges[recipe][0]
    record["perturb_cpu"] = cpu() - started
    descent = Guard(min(deadline, cpu() + config["descent_cpu"]), stop)
    started = cpu()
    neutral_count = 0
    escaped = False
    try:
        while True:
            descent.check()
            choices = list(sampled(rows, arm, rng, descent, costs, config["sample_size"]))
            better = [c for c in choices if key(c[1], target) < key(scores, target)]
            if better:
                child, child_scores, name = min(better, key=lambda c: key(c[1], target))
                adopt(child, child_scores, descent)
                adopted_names[name] += 1
                record["descent_trades"] += 1
                continue
            if variant == "A0":
                break
            neutral = [c for c in choices if key(c[1], target) == key(scores, target)
                       and identity(core.encode_g6(c[0])) not in seen]
            if neutral and neutral_count < config["neutral_limit"]:
                child, child_scores, _ = rng.choice(neutral)
                adopt(child, child_scores, descent)
                neutral_count += 1
                record["neutral_trades"] += 1
                continue
            if escaped:
                break
            # One anchored escape segment, then strict/neutral descent in the
            # remaining 75s. No Linf+1 experiment in the frozen initial variant.
            escaped = True
            level = min(2, failures // 4)
            step = config["thresholds"][arm].get(target, 0)
            for _ in range(min(8, desired)):
                allowed = [c for c in choices
                           if identity(core.encode_g6(c[0])) not in seen
                           and escape_allowed(c[1], scores, anchor, target, step, level)]
                if not allowed:
                    break
                child, child_scores, _ = rng.choice(allowed)
                adopt(child, child_scores, descent)
                record["escape_trades"] += 1
                choices = list(sampled(rows, arm, rng, descent, costs, config["sample_size"]))
    except core.BudgetEnd as error:
        record["status"] = str(error)
    record["descent_cpu"] = cpu() - started
    record["returned_to_parent"] = rows == core.decode_g6(parent["graph6"])
    # End verification/canonicalization belongs to the same worker CPU budget;
    # never admit a child whose validation finishes after the endpoint.
    result = candidate(rows, arm, parent["family"], parent["line"], parent["state"], costs)
    record["path_maxima"] = maxima
    record["adopted_moves"] = dict(adopted_names)
    record["target_improved"] = key(result["scores"], target) < key(parent["scores"], target)
    record["new_class_vs_parent"] = result["class"] != parent["class"]
    record["eligible_before_endpoint"] = cpu() <= deadline
    return result, record, seen


def parent_choice(population, target, rng):
    if rng.random() < 0.8:
        return min(rng.choices(population, k=3), key=lambda x: key(x["scores"], target))
    counts = Counter(p["family"] for p in population)
    least = min(counts.values())
    family = rng.choice(sorted(f for f, n in counts.items() if n == least))
    return rng.choice([p for p in population if p["family"] == family])


def select(population, children, arm, target, rng, epoch, families):
    size = len(population)
    if size != 16:
        raise ValueError("This frozen selection requires 16 real founders")
    distinct = {}
    for item in population + children:
        # For Omega preserve labelled working frames, not an uncolored quotient.
        state = item["state"] if arm == "omega" else item["class"]
        distinct.setdefault(state, item)
    ordered = sorted(distinct.values(), key=lambda x: (key(x["scores"], target), x["state"]))
    chosen = ordered[:2]
    if epoch < 5:
        for family in families:
            if not any(p["family"] == family for p in chosen):
                representative = next((p for p in ordered if p["family"] == family), None)
                if representative is None:
                    raise ValueError("Lost protected source family")
                chosen.append(representative)
    for item in ordered:
        if len(chosen) >= 12:
            break
        if item not in chosen:
            chosen.append(item)
    remaining = [p for p in ordered if p not in chosen]
    chosen.extend(rng.sample(remaining, 16 - len(chosen)))
    return chosen


def tuple_state(value):
    return tuple(tuple_state(x) for x in value) if isinstance(value, list) else value
