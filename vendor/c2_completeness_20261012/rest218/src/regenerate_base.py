"""Independent deterministic regeneration from supplied model sources."""
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'legacy'))
from model import build_base
from anchor_profile import build
from common import sha, require
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
build_base(out)
build(out / 'base.cnf', out / 'profile_346.cnf', profile=[3, 4, 6])
require(sha(out / 'profile_346.cnf') == '33fc424d5e0ce00179a5abbde52c56b40e4e1fcbc272c36d595ef29354e3b030', 'REGENERATION_HASH_MISMATCH')
print('PROFILE_REGENERATION_PASS')
