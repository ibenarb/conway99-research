from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for name in ('lambda_review_20260921', 'lambda_strategy_0_1_0', 'move_accel_0_1_0', 'ryzen_compare_0_4_0'):
    sys.path.insert(0, str(HERE.parent / name))
sys.path.insert(0, str(HERE))
