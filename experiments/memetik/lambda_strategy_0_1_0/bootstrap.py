from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / 'move_accel_0_1_0'))
sys.path.insert(0, str(HERE.parent / 'ryzen_compare_0_4_0'))
sys.path.insert(0, str(HERE))
