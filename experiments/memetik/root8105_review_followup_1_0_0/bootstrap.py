"""Reference imports; the preserved reference package is never modified."""
import sys
from pathlib import Path
REFERENCE = Path(__file__).resolve().parent / 'reference'
if str(REFERENCE) not in sys.path:
    sys.path.append(str(REFERENCE))
