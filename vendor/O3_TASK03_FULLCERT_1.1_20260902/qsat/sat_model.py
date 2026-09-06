"""Strict CaDiCaL model handling for production CNFs.

Only ``-w <sol>`` is used for witness output: it is advertised by the local
CaDiCaL 2.2.1 ``--help`` output.  A projected primary assignment is never
accepted until the caller's independent verifier has checked it.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


class ModelError(RuntimeError):
    """A solver witness cannot safely be used as a primary model."""


def primary_edge_map(core, edge_variables):
    """Return the canonical, complete edge-to-variable map for a core."""
    expected = {tuple(edge) for edge in core["candidate_edges"]}
    if set(edge_variables) != expected:
        raise ModelError("primary variable map is incomplete or has foreign edges")
    return {edge: edge_variables[edge] for edge in sorted(expected)}


def parse_dimacs_witness(text):
    """Parse a complete DIMACS witness, rejecting ambiguity and truncation."""
    values = {}
    terminated = False
    saw_value_line = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("c") or line.startswith("s"):
            continue
        fields = line.split()
        if fields[0] != "v":
            raise ModelError("unexpected witness record")
        if terminated:
            raise ModelError("literals occur after terminating 0")
        saw_value_line = True
        if len(fields) == 1:
            continue
        for pos, token in enumerate(fields[1:]):
            try:
                literal = int(token)
            except ValueError as exc:
                raise ModelError("non-integer witness literal") from exc
            if literal == 0:
                if pos != len(fields[1:]) - 1:
                    raise ModelError("literals occur after terminating 0")
                terminated = True
                continue
            if terminated:
                raise ModelError("literals occur after terminating 0")
            variable, value = abs(literal), literal > 0
            if variable == 0:
                raise ModelError("zero is only a line terminator")
            if variable in values and values[variable] != value:
                raise ModelError("contradictory witness literal")
            values[variable] = value
    if not saw_value_line or not terminated:
        raise ModelError("missing final witness 0")
    return values


def project_primary_model(text, primary_map):
    """Return selected primary edges, requiring every primary literal."""
    values = parse_dimacs_witness(text)
    missing = [edge for edge, variable in primary_map.items() if variable not in values]
    if missing:
        raise ModelError("incomplete primary model: %r" % (missing,))
    return [edge for edge, variable in primary_map.items() if values[variable]]


def solve_sat_and_project(cnf_path, primary_map, verifier, *, cadical="cadical"):
    """Solve a production CNF and verify its strictly projected model.

    ``verifier`` is intentionally injected, keeping this layer independent of
    the encoder and allowing the Rook matrix verifier to remain independent.
    """
    cnf_path = Path(cnf_path)
    witness = cnf_path.with_suffix(".witness")
    result = subprocess.run(
        [cadical, "-w", str(witness), str(cnf_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 10:
        raise ModelError("CaDiCaL did not return SAT (exit %d)" % result.returncode)
    if not witness.is_file():
        raise ModelError("CaDiCaL did not create requested witness")
    selected = project_primary_model(witness.read_text(), primary_map)
    try:
        verifier(selected)
    except Exception as exc:
        raise ModelError("independent model verification failed") from exc
    return selected, result, witness.read_text()
