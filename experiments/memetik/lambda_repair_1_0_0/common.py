"""Small durable I/O and Linux process helpers; no solver imports."""
import hashlib
import json
import os
import resource
import tempfile
import sys

if sys.flags.optimize:
    raise RuntimeError("Assertions are required; optimized Python mode is unsupported")
from pathlib import Path

HERE = Path(__file__).resolve().parent
GIB = 1024 ** 3
THREAD_ENV = {k: '1' for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')}


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        fd = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        try:
            os.unlink(name)
        except FileNotFoundError:
            pass


def cpu():
    u = resource.getrusage(resource.RUSAGE_SELF)
    return u.ru_utime + u.ru_stime


def process(pid):
    try:
        text = Path('/proc/self/stat' if pid == os.getpid() else f'/proc/{pid}/stat').read_text()
        fields = text[text.rfind(')') + 2:].split()
        return {'pid': pid, 'cpu': (int(fields[11]) + int(fields[12])) / os.sysconf('SC_CLK_TCK'),
                'rss': int(fields[21]) * os.sysconf('SC_PAGE_SIZE'), 'start_ticks': int(fields[19])}
    except (FileNotFoundError, ProcessLookupError):
        return {'pid': pid, 'cpu': 0, 'rss': 0, 'start_ticks': None}


def verify_package():
    manifest = read(HERE / 'PACKAGE.json')
    for name, expected in manifest['files'].items():
        if digest(HERE / name) != expected:
            raise RuntimeError('PACKAGE_HASH_MISMATCH: ' + name)
    return digest(HERE / 'PACKAGE.json')


def environment():
    import importlib.metadata
    required = read(HERE / 'DEPENDENCIES.json')
    actual = {name: importlib.metadata.version(name) for name in required}
    if actual != required:
        raise RuntimeError('Pinned dependencies differ')
    return actual
