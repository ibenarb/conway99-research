"""Fresh pinned C3 proof build and sandboxed comparators in the prepared RAM tree."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
WORKSPACE = BASE.parents[2]
READY = json.loads((BASE / 'ram_prepare_result_v2.json').read_text())
ROOT = Path(READY['root'])
assert READY['status'] == 'RAM_BUILD_TREE_READY'
assert ROOT == Path('/dev/shm/conway99_c3_assurance_20261122_v2')
BIN = BASE / 'toolchain/lean-4.35.0-rc2-linux/bin'
os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
ENV = os.environ.copy()
ENV['PATH'] = str(BIN) + os.pathsep + ENV['PATH']
ENV['LEAN_NUM_THREADS'] = '1'
ENV['OMP_NUM_THREADS'] = '1'
ENV['MATHLIB_CACHE_DIR'] = str(BASE / 'mathlib_cache')
ENV['COMPARATOR_BWRAP'] = str(BASE.parent / 'math_env_v1/root/usr/bin/bwrap')
temporary = ROOT / 'temporary'
temporary.mkdir(exist_ok=True)
ENV['TMPDIR'] = str(temporary)
MANIFEST = json.loads((WORKSPACE / 'work/C3_Statuspruefung_20261122/source_manifest_v1.json').read_text())
PINNED = [x for x in MANIFEST if x['path'].startswith('c3formal/')]

def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()

def source_check():
    for record in PINNED:
        assert sha(ROOT / record['path'][len('c3formal/'):]) == record['sha256']

def execute(label, arguments):
    source_check()
    started = time.time()
    command = [str(BIN / 'lake')] + arguments
    print(json.dumps(dict(label=label, command=command, started=started)), flush=True)
    result = subprocess.run(command, cwd=ROOT, env=ENV)
    record = dict(label=label, arguments=arguments, exit_code=result.returncode,
                  started=started, elapsed_seconds=time.time() - started)
    source_check()
    return record

phase = sys.argv[1]
with (BASE / ('ram_' + phase + '_started_v2.json')).open('x') as stream:
    json.dump(dict(pid=os.getpid(), phase=phase, root=str(ROOT), started=time.time(),
                   own_affinity=sorted(os.sched_getaffinity(0)), threads=1), stream, indent=4)
records = []
if phase == 'build':
    assert not (ROOT / '.lake/build').exists(), 'Fresh project build required'
    modules = {}
    for record in PINNED:
        name = record['path'][len('c3formal/'):]
        if name.endswith('.lean'):
            module = name[:-5].replace('/', '.')
            text = (ROOT / name).read_text()
            modules[module] = re.findall(r'^\s*(?:public\s+)?import\s+([A-Za-z0-9_.]+)', text, re.M)
    seen = set()
    ordered = []
    visiting = set()
    def visit(module):
        if module in seen:
            return
        assert module not in visiting, 'Import cycle'
        visiting.add(module)
        for dependency in modules[module]:
            if dependency in modules:
                visit(dependency)
        visiting.remove(module)
        seen.add(module)
        ordered.append(module)
    for module in sorted(modules):
        visit(module)
    (BASE / 'ram_build_module_order_v2.json').write_text(json.dumps(
        dict(imports=modules, topological_order=ordered), indent=4))
    for index, module in enumerate(ordered):
        record = execute(module, ['--no-cache', 'build', '+' + module])
        records.append(record)
        (BASE / 'ram_build_progress_v2.json').write_text(json.dumps(
            dict(completed=index + 1, planned=len(ordered), records=records), indent=4))
        if record['exit_code'] != 0:
            break
    if len(records) == len(ordered) and all(x['exit_code'] == 0 for x in records):
        records.append(execute('all_project_targets', ['--no-cache', 'build', 'C3formal', 'Challenge', 'Solution']))
elif phase == 'axioms':
    records.append(execute('axioms', ['env', 'lean', 'C3formal/Check.lean']))
elif phase == 'comparator':
    records.append(execute('comparator', ['comparator']))
elif phase == 'paranoid':
    records.append(execute('paranoid', ['comparator', '--paranoid']))
else:
    raise ValueError(phase)
success = bool(records) and all(x['exit_code'] == 0 for x in records)
report = dict(phase=phase, status='COMMANDS_PASSED' if success else 'COMMAND_FAILURE_NOT_A_PROOF_VERDICT',
              records=records, pinned_source_hashes_unchanged=True,
              security_settings_changed=False, root=str(ROOT))
(BASE / ('ram_' + phase + '_result_v2.json')).write_text(json.dumps(report, indent=4))
print(json.dumps(report), flush=True)
sys.exit(0 if success else 1)
