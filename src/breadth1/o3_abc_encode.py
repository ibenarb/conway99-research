#!/usr/bin/env python3
"""A/B/C encoder helpers for O3-BREADTH-1.

A = base core + C3 exact-one (Lemma B)
B = A + generic cycle-local pair-budget inequalities for every C_m, m>=5
C = B + redundant first/second moment equalities for every C_m, m>=5

Layer C is deliberately redundant:
- M1 is the sum of the S-degree equations over vertices of the component.
- M2 is the sum of the normalized pair equations over all unordered pairs
  inside the component.

Large moment equalities are encoded with a non-recursive Wallace/carry-save
binary adder. This avoids the recursion-depth and state-space risks of the
historical recursive BDD encoder on very large weighted sums.

No solver is invoked here.
"""
from __future__ import annotations


def upair(a, b):
    return (a, b) if a < b else (b, a)


def cycle_components(core):
    out = []
    p = len(core["T"])
    for length in core["cycle_type"]:
        out.append(tuple(range(p, p + length)))
        p += length
    return out


def add_triangle_exactly_one(cnf, core, sv):
    groups = 0
    for comp in cycle_components(core):
        if len(comp) != 3:
            continue
        inside = set(comp)
        for v in range(core["n"]):
            if v in inside:
                continue
            xs = [sv[upair(v, t)] for t in comp]
            cnf.add(xs[0], xs[1], xs[2])
            cnf.add(-xs[0], -xs[1])
            cnf.add(-xs[0], -xs[2])
            cnf.add(-xs[1], -xs[2])
            groups += 1
    return groups


def product_variable_maps(core, cnf):
    offset = len(core["candidate_edges"])
    by_factors = {}
    by_id = {}

    for item in core["products"]:
        pid = item["id"]
        var = offset + 1 + pid
        expected = "p_%d" % pid
        if cnf.names[var - 1] != expected:
            raise AssertionError(
                "product variable numbering changed: %s != %s"
                % (cnf.names[var - 1], expected)
            )
        a, b = map(tuple, item["factors"])
        key = (a, b) if a < b else (b, a)
        by_factors[key] = var
        by_id[pid] = var

    return by_factors, by_id


def weighted_le(cnf, items, rhs, label):
    """Historical small BDD encoder, retained only for the B-layer inequalities."""
    if rhs < 0:
        cnf.add()
        return 1

    max_sum = sum(weight for _, weight in items)
    if max_sum <= rhs:
        return 0

    slack = [(cnf.var("%s_slack" % label), 1) for _ in range(rhs)]
    cnf.weighted_eq(items + slack, rhs)
    return 1


def _xor2(cnf, a, b, name):
    if a is False:
        return b
    if b is False:
        return a
    if a is True:
        raise AssertionError("unexpected constant True in xor input")
    if b is True:
        raise AssertionError("unexpected constant True in xor input")
    if a == b:
        return False

    z = cnf.var(name)
    cnf.add(a, b, -z)
    cnf.add(-a, -b, -z)
    cnf.add(a, -b, z)
    cnf.add(-a, b, z)
    return z


def _and2(cnf, a, b, name):
    if a is False or b is False:
        return False
    if a is True:
        return b
    if b is True:
        return a
    if a == b:
        return a

    z = cnf.var(name)
    cnf.add(-z, a)
    cnf.add(-z, b)
    cnf.add(z, -a, -b)
    return z


def _or2(cnf, a, b, name):
    if a is False:
        return b
    if b is False:
        return a
    if a is True or b is True:
        return True
    if a == b:
        return a

    z = cnf.var(name)
    cnf.add(z, -a)
    cnf.add(z, -b)
    cnf.add(-z, a, b)
    return z


def _full_adder(cnf, a, b, carry_in, name):
    """Return (sum_bit, carry_out) with Tseitin-equivalent gates."""
    t = _xor2(cnf, a, b, name + "_x1")
    sum_bit = _xor2(cnf, t, carry_in, name + "_x2")
    ab = _and2(cnf, a, b, name + "_a1")
    tc = _and2(cnf, t, carry_in, name + "_a2")
    carry_out = _or2(cnf, ab, tc, name + "_o")
    return sum_bit, carry_out


def _force_bit(cnf, bit, value):
    if bit is False:
        if value:
            cnf.add()
        return
    if bit is True:
        if not value:
            cnf.add()
        return
    cnf.add(bit if value else -bit)


def weighted_eq_wallace(cnf, items, rhs, label):
    """Encode sum(weight * bool_var) == rhs without recursion.

    Positive integer weights only. Repeated variables are combined first.
    The weighted input bits are reduced column-wise with carry-save full
    adders (Wallace style), then the final two rows are ripple-added once.
    """

    combined = {}
    for var, weight in items:
        if weight <= 0:
            raise ValueError("weights must be positive")
        combined[var] = combined.get(var, 0) + weight

    max_sum = sum(combined.values())
    if rhs < 0 or rhs > max_sum:
        cnf.add()
        return {
            "inputs": len(combined),
            "max_sum": max_sum,
            "reducers": 0,
            "final_width": 0,
        }

    if not combined:
        if rhs != 0:
            cnf.add()
        return {
            "inputs": 0,
            "max_sum": 0,
            "reducers": 0,
            "final_width": 1,
        }

    width = max(1, max_sum.bit_length() + 1)
    columns = [[] for _ in range(width)]

    for var, weight in sorted(combined.items()):
        bit = 0
        w = weight
        while w:
            if w & 1:
                columns[bit].append(var)
            bit += 1
            w >>= 1

    reducers = 0

    # Carry-save reduction: every 3 bits in a column become one sum bit in
    # the same column and one carry bit in the next column.
    for bit in range(len(columns) - 1):
        while len(columns[bit]) >= 3:
            a = columns[bit].pop()
            b = columns[bit].pop()
            c = columns[bit].pop()
            s, carry = _full_adder(
                cnf,
                a,
                b,
                c,
                "%s_cs_%d_%d" % (label, bit, reducers),
            )
            reducers += 1
            if s is not False:
                columns[bit].append(s)
            if carry is not False:
                columns[bit + 1].append(carry)

    # One final ripple addition of the at-most-two remaining rows.
    final_bits = []
    carry = False

    for bit in range(len(columns)):
        if len(columns[bit]) > 2:
            raise AssertionError("carry-save reduction incomplete")
        a = columns[bit][0] if columns[bit] else False
        b = columns[bit][1] if len(columns[bit]) == 2 else False
        s, carry = _full_adder(
            cnf,
            a,
            b,
            carry,
            "%s_final_%d" % (label, bit),
        )
        final_bits.append(s)

    if carry is not False:
        final_bits.append(carry)

    for bit_index, bit in enumerate(final_bits):
        expected = bool((rhs >> bit_index) & 1)
        _force_bit(cnf, bit, expected)

    # Any target bit above the represented circuit must be zero; rhs<=max_sum
    # already guarantees this arithmetically.
    if rhs >> len(final_bits):
        cnf.add()

    return {
        "inputs": len(combined),
        "max_sum": max_sum,
        "reducers": reducers,
        "final_width": len(final_bits),
    }


def add_cycle_local_layer(cnf, core, sv):
    product_vars, _ = product_variable_maps(core, cnf)
    candidate_set = set(map(tuple, core["candidate_edges"]))
    lset = set(map(tuple, core["L"]))

    nbr = {i: set() for i in range(core["n"])}
    for a, b in lset:
        nbr[a].add(b)
        nbr[b].add(a)

    components = 0
    constraints = 0
    by_length = {}

    for comp_index, comp in enumerate(cycle_components(core)):
        m = len(comp)
        if m < 5:
            continue

        components += 1
        by_length[m] = by_length.get(m, 0) + 1
        inside = set(comp)

        for ii in range(m):
            i = comp[ii]
            for jj in range(ii + 1, m):
                j = comp[jj]
                ell = int(upair(i, j) in lset)
                common_l = len(nbr[i] & nbr[j])
                rhs = 6 - 4 * common_l - 2 * ell
                items = []

                for k in inside:
                    if k in (i, j):
                        continue
                    a = upair(i, k)
                    b = upair(k, j)
                    if a in candidate_set and b in candidate_set:
                        key = (a, b) if a < b else (b, a)
                        items.append((product_vars[key], 1))

                for k in nbr[j]:
                    if k != i:
                        edge = upair(i, k)
                        if edge in candidate_set:
                            items.append((sv[edge], 2))

                for k in nbr[i]:
                    if k != j:
                        edge = upair(k, j)
                        if edge in candidate_set:
                            items.append((sv[edge], 2))

                edge = upair(i, j)
                if not ell:
                    items.append((sv[edge], 1))

                constraints += weighted_le(
                    cnf,
                    items,
                    rhs,
                    "cm_%d_%d_%d" % (comp_index, i, j),
                )

    return {
        "components": components,
        "constraints": constraints,
        "by_length": dict(sorted(by_length.items())),
    }


def moment_items(core, cnf, sv, comp):
    """Return exact redundant M1 and M2 PB equalities for one component."""
    inside = set(comp)
    m = len(comp)
    candidate_set = set(map(tuple, core["candidate_edges"]))
    product_vars, _ = product_variable_maps(core, cnf)

    # M1: outside incidences + 2*internal chords = 10m.
    m1 = []
    for edge, var in sv.items():
        a, b = edge
        ina = a in inside
        inb = b in inside
        if ina and inb:
            m1.append((var, 2))
        elif ina or inb:
            m1.append((var, 1))

    # M2: sum_{i<j in C}(S^2)_ij + 9e = 3m(m-3).
    m2 = []
    vertices = list(comp)
    for ii in range(m):
        i = vertices[ii]
        for jj in range(ii + 1, m):
            j = vertices[jj]
            for k in range(core["n"]):
                if k in (i, j):
                    continue
                a = upair(i, k)
                b = upair(k, j)
                if a in candidate_set and b in candidate_set:
                    key = (a, b) if a < b else (b, a)
                    m2.append((product_vars[key], 1))

    for edge, var in sv.items():
        a, b = edge
        if a in inside and b in inside:
            m2.append((var, 9))

    return m1, 10 * m, m2, 3 * m * (m - 3)


def add_moment_layer(cnf, core, sv):
    components = 0
    equalities = 0
    by_length = {}
    adder_stats = []

    for comp_index, comp in enumerate(cycle_components(core)):
        m = len(comp)
        if m < 5:
            continue

        m1, rhs1, m2, rhs2 = moment_items(core, cnf, sv, comp)

        stat1 = weighted_eq_wallace(
            cnf,
            m1,
            rhs1,
            "moment_%d_m1" % comp_index,
        )
        stat2 = weighted_eq_wallace(
            cnf,
            m2,
            rhs2,
            "moment_%d_m2" % comp_index,
        )

        components += 1
        equalities += 2
        by_length[m] = by_length.get(m, 0) + 1
        adder_stats.append({
            "component_index": comp_index,
            "m": m,
            "m1": stat1,
            "m2": stat2,
        })

    return {
        "components": components,
        "equalities": equalities,
        "by_length": dict(sorted(by_length.items())),
        "adder_stats": adder_stats,
    }


def build_cnf(core, legacy_encode, layer):
    if layer not in ("A", "B", "C"):
        raise ValueError("layer must be A, B or C")

    cnf, sv = legacy_encode.cnf_from_core(
        core,
        lemma_triangle_eo=False,
    )

    eo_groups = add_triangle_exactly_one(cnf, core, sv)

    meta = {
        "layer": layer,
        "eo_groups": eo_groups,
        "cycle_local": {
            "components": 0,
            "constraints": 0,
            "by_length": {},
        },
        "moment": {
            "components": 0,
            "equalities": 0,
            "by_length": {},
            "adder_stats": [],
        },
    }

    a_variables = cnf.n
    a_clauses = len(cnf.cl)
    meta["A_variables"] = a_variables
    meta["A_clauses"] = a_clauses

    if layer in ("B", "C"):
        meta["cycle_local"] = add_cycle_local_layer(cnf, core, sv)

    b_variables = cnf.n
    b_clauses = len(cnf.cl)
    meta["B_variables"] = b_variables
    meta["B_clauses"] = b_clauses

    if layer == "C":
        meta["moment"] = add_moment_layer(cnf, core, sv)

    meta["variables"] = cnf.n
    meta["clauses"] = len(cnf.cl)
    meta["added_over_A_variables"] = cnf.n - a_variables
    meta["added_over_A_clauses"] = len(cnf.cl) - a_clauses
    meta["added_over_B_variables"] = cnf.n - b_variables
    meta["added_over_B_clauses"] = len(cnf.cl) - b_clauses
    return cnf, sv, meta
