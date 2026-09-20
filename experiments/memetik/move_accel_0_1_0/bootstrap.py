"""Load the sibling baseline; frozen bundles retain its original files."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASELINE = HERE.parent / 'ryzen_compare_0_4_0'
sys.path.insert(0, str(BASELINE))
