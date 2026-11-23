"""Check the finite arithmetic underlying the genus mass double count."""
from pathlib import Path
from fractions import Fraction
from math import factorial, prod
import hashlib
import itertools
import json
import numpy as np
from cypari2 import Pari

BASE = Path(__file__).resolve().parent
P = Pari()
P.allocatemem(1000000000, silent=True)
data = json.loads((BASE / "unimodular15.json").read_text())
known_orders = {
    "Z15": 2 ** 15 * factorial(15),
    "Z7+E8": 2 ** 7 * factorial(7) * 696729600,
    "Z3+D12+": 2 ** 3 * factorial(3) * 2 ** 11 * factorial(12),
    "Z1+E7E7+": 4 * 2903040 ** 2,
    "A15+": 2 * factorial(16)
}
assert set(data["gram"]) == set(known_orders)
binary = np.array(list(itertools.product((0, 1), repeat=15)), dtype=np.int64)
mass = Fraction(0)
records = []
for name, gram in data["gram"].items():
    gp = P.matrix(15, 15, [int(x) for row in gram for x in row])
    assert P.matdet(gp) == 1
    assert 225 * max(abs(x) for row in gram for x in row) < 2 ** 62
    norms = np.sum((binary @ np.array(gram, dtype=np.int64)) * binary, axis=1) % 4
    counts = [int(np.sum(norms == i)) for i in range(4)]
    assert counts[0] + counts[2] == 2 ** 14
    assert counts[0] == 2 ** 13 + 2 ** 6
    order = int(P.qfauto(gp)[0])
    assert order == known_orders[name]
    mass += Fraction(1, order)
    records.append({"name": name, "aut_order": order, "norm_residues_mod4": counts})
    print(name, order, counts, flush=True)
# Ordered bases of totally singular 4-spaces in O+_14(2), divided by |GL4(2)|.
ordered = prod(2 ** d * (2 ** (7 - d) - 1) * (2 ** (6 - d) + 1) for d in range(4))
bases = prod(16 - 2 ** d for d in range(4))
singular4 = Fraction(ordered, bases)
lagrangians = prod(2 ** d + 1 for d in range(1, 5))
assert singular4 == 3876193035 and bases == 20160 and lagrangians == 2295
assert mass == Fraction(29713, 385648863215616000)
target = mass * singular4 / lagrangians
checked = json.loads((BASE / "finite_result_v2.json").read_text())
assert target == Fraction(checked["mass"])
out = {"status": "MASS_ARITHMETIC_CHECKS_PASS", "unimodular_classes": records,
       "singular_4spaces": int(singular4), "lagrangians": lagrangians,
       "unimodular_mass": str(mass), "genus_target_mass": str(target),
       "dependency": "Uses the established classification of rank-15 positive definite integral unimodular lattices into these five classes; does not reprove that classification.",
       "source_sha256": hashlib.sha256((BASE / "unimodular15.json").read_bytes()).hexdigest()}
with (BASE / "mass_result_v1.json").open("x") as file:
    json.dump(out, file, indent=4)
print(out["status"], flush=True)
