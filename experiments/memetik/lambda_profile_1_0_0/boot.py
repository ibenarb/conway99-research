"""Explicit import paths; original source bytes are never patched."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FROZEN = ROOT / "experiments/memetik/lambda_compare_0_2_0"
sys.path.insert(0, str(FROZEN))
import bootstrap
sys.path.insert(0, str(HERE))
