# Small independent C2 slice checks

These are copies of our independent 27 October checkers, released with the 1 November public status. They do not import the external project's solver code.

- `audit_boundary.py`: Python 3 and NumPy; enumerates the ten-vertex boundary configurations and their B5 orbits. Writes `boundary_audit.json` beside the script.
- `audit_parity.py`: Python 3 standard library only; verifies the affine F2 identity excluding three Type-I blocks under the slice equations. Writes `triple_parity_certificate.json` beside the script.

The corresponding stored outputs are included. To reproduce, use a disposable copy of this directory and run either script with Python. They regenerate their own output files. They do not read or control any solver process.

The scripts were rerun in an isolated temporary publication-check directory on 1 November; their parsed JSON outputs matched the stored records. The boundary result concerns local necessary data, not global extendability. The parity result is conditional on the explicitly stated necessary slice identities; see [the model contract](../../docs/c2/MODEL_CONTRACT.md).

The large matching enumeration, global graph certificates and complete lattice transfer audit are outside this small checker package.
