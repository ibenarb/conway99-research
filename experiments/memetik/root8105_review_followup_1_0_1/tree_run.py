"""Explicit tree-plan entry; same audited controller with a separate model identity."""
import os
import sys

for flag, variable in [('--draws-per-cell', 'ROOT8105_TREE_DRAWS'), ('--depth', 'ROOT8105_TREE_DEPTH')]:
    if flag in sys.argv:
        index = sys.argv.index(flag)
        os.environ[variable] = sys.argv[index + 1]
        del sys.argv[index:index + 2]
import tree_plan
sys.modules['plan'] = tree_plan
from census import main

if __name__ == '__main__':
    main()
