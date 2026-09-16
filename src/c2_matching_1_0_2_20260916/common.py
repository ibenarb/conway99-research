"""Shared, bounded I/O and immutable identities for C2 scouting."""
import hashlib
import json
import os
from pathlib import Path
import tempfile

VERSION = '1.0.2'
CNF_HASH = 'f9d6011c5e6eb8a0fab971fa324d159e94b8bc4526b7b17dc31ee55aee1c25ba'
MAP_HASH = 'cd78938cc0fd6c4b2239ddd2b67054e1ea754b41be4dc6eeaef6849b97e0bc0e'
REF_HASH = '3a88f356831a4f955c79639bfe86aac5eea2a80febdd676cbd1009e86f1e9b29'
SOLVER_COMMIT = '4198d817d0dcde5b1240eefbff70b555b7df2af9'
ROOT = Path.home() / 'conway99_workspace/c2_matching_v1'
GIB = 1024**3
LOG_LIMIT = 64 * 1024**2


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, obj):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(obj, stream, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def tail(path, size=16384):
    with Path(path).open('rb') as stream:
        stream.seek(max(0, stream.seek(0, 2) - size))
        return stream.read().decode(errors='replace')
