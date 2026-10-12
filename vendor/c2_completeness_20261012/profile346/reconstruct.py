"""Reproduce pinned formulas in this experiment's private directory."""
import sys
from pathlib import Path
from model import build_base, BASE_SHA, MAP_SHA
from anchor_profile import build
from runtime import sha

PROFILE_SHA = '33fc424d5e0ce00179a5abbde52c56b40e4e1fcbc272c36d595ef29354e3b030'


def main(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    build_base(directory)
    build(directory / 'base.cnf', directory / 'profile_346.cnf', profile=[3, 4, 6])
    for name, expected in [('base.cnf', BASE_SHA), ('variables.json', MAP_SHA),
                           ('profile_346.cnf', PROFILE_SHA)]:
        if sha(directory / name) != expected:
            raise ValueError('Reconstructed formula hash mismatch: ' + name)
    print('PROFILE346_FORMULAS_RECONSTRUCTED_PASS', flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
