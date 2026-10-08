"""Real Windows/WSL acceptance only; never runs an N1 research class."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import uuid
import accounting
import platform_adapter as pa
import preflight
import runtime as r

CONTROL_PROCESSES = []

CFG = dict(min_available_bytes=128*1024**2, min_free_bytes=512*1024**2,
           max_rss_bytes=1024**3)


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def probe(out):
    require('microsoft' in platform.release().lower(), 'Run this probe in the intended Ryzen WSL instance')
    required = ['powershell.exe', 'wslpath', 'git', 'g++', 'gcc']
    commands = {name: shutil.which(name) for name in required}
    require(all(commands.values()), 'Missing prerequisite: ' + str(commands))
    require(hasattr(os, 'pidfd_open'), 'pidfd process handles unavailable')
    # Parse the PowerShell file on its actual interpreter before starting it.
    script = Path(__file__).with_name('host_clock.ps1').resolve()
    windows = subprocess.check_output([commands['wslpath'], '-w', str(script)], text=True).strip()
    import base64
    path64 = base64.b64encode(windows.encode('utf-16-le')).decode()
    ps = "$p=[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('" + path64 + "')); $tokens=$null; $errors=$null; [void][System.Management.Automation.Language.Parser]::ParseFile($p,[ref]$tokens,[ref]$errors); if($errors.Count){$errors|Out-String|Write-Output; exit 1}"
    command = [commands['powershell.exe'], '-NoLogo', '-NoProfile', '-NonInteractive',
               '-EncodedCommand', base64.b64encode(ps.encode('utf-16-le')).decode()]
    parsed = subprocess.run(command, capture_output=True)
    (out/'powershell-parser.log').write_bytes(parsed.stdout+parsed.stderr)
    require(parsed.returncode == 0, 'PowerShell syntax check failed; see parser log')
    session = out/'sessions'/uuid.uuid4().hex
    session.mkdir(parents=True)
    adapter = pa.Observer(out, session, CFG)
    measurements = []
    try:
        adapter.start()
        sequences = set()
        while len(sequences) < 6:
            adapter.tick()
            require(adapter.fault is None, 'Platform probe fault: ' + str(adapter.fault))
            sample = r.read(adapter.folder/'health.json')
            sequence = sample['host']['sequence']
            if sequence not in sequences:
                measurements.append(sample)
                sequences.add(sequence)
            time.sleep(0.1)
    finally:
        final = adapter.finish()
    require(final['adapter_complete'] and final['fault'] is None, 'Host final account incomplete')
    # Byte-preserving atomic exchange checked through the same filesystem.
    require(len(measurements) == 6, 'Incomplete host observations')
    r.raw_atomic(out/'atomic-control.json', {'sequence': 1})
    r.raw_atomic(out/'atomic-control.json', {'sequence': 2})
    require(r.read(out/'atomic-control.json') == {'sequence': 2}, 'Atomic round trip failed')
    result = dict(stage='PLATFORM_PROBE', status='PASS', production_approved=False,
                  windows_executed=True, prerequisites=commands, measurements=measurements,
                  end_account=final, thresholds_for_small_controls=CFG,
                  next_stage='build pinned tools, then controls; no N1 class start')
    r.raw_atomic(out/'RESULT.json', result)
    return result


def controls(out, worker, checker):
    require('microsoft' in platform.release().lower(), 'Real WSL required')
    require(worker.is_file() and checker.is_file(), 'Build pinned worker/checker first')
    rows = []
    def command(root, action, *extra, background=False):
        log = out/(root.name+'-'+action+'-'+uuid.uuid4().hex+'.log')
        with log.open('wb') as stream:
            proc = subprocess.Popen([sys.executable, r.__file__, action, str(root), *map(str, extra)],
                                    stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT,
                                    start_new_session=True)
        if background:
            CONTROL_PROCESSES.append((root, proc))
            return proc
        code = proc.wait()
        require(code == 0, 'Control CLI failed: '+str(log))
    def init(name, text, budget):
        root = out/name
        cnf = out/(name+'.cnf')
        cnf.write_text(text)
        command(root, 'init', '--cnf', cnf, '--worker', worker, '--checker', checker,
                '--budget', budget, '--platform-wsl', '--total-budget', 600,
                '--max-rss-bytes', CFG['max_rss_bytes'], '--min-free-bytes', CFG['min_free_bytes'],
                '--min-available-bytes', CFG['min_available_bytes'])
        return root
    def wait(root, process, predicate):
        last_notice = time.monotonic()
        while True:
            state = r.read(root/'state.json')
            if predicate(state):
                return state
            require(process.poll() is None, 'Control ended before expected state: '+state['status'])
            if time.monotonic()-last_notice > 30:
                print('Control still active; no automatic budget abort. State:', state['status'], flush=True)
                last_notice = time.monotonic()
            time.sleep(0.1)
    def finished(root):
        report = accounting.audit(root)
        require(not report['gaps'] and not report['active'] and report['partition_complete'], 'Control account gap')
        active_platform = [x['platform'] for x in report['sessions'] if x['platform'] is not None]
        require(active_platform and all(x['adapter_complete'] and x['fault'] is None for x in active_platform),
                'Host control not fully closed')
        r.raw_atomic(out/(root.name+'-ACCOUNTS.json'), report)
        return report
    for name, text, expected in (
        ('sat', 'p cnf 1 1\n1 0\n', 'SAT_CNF_VERIFIED'),
        ('unsat', 'p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n', 'UNSAT_CERTIFIED'),
    ):
        root = init(name, text, 60)
        command(root, 'run')
        state = r.read(root/'state.json')
        require(state['status'] == expected, 'Wrong control result')
        finished(root)
        command(root, 'resume')
        require(len(r.read(root/'state.json')['attempts']) == 1, 'Completed work repeated')
        finished(root)
        rows.append(dict(test=name+'_host_native_end_and_reuse', passed=True))
    h = 21
    var = lambda i,j: i*h+j+1
    clauses = [[var(i,j) for j in range(h)] for i in range(h+1)]
    clauses += [[-var(i,j), -var(k,j)] for j in range(h) for i in range(h+1) for k in range(i)]
    text = 'p cnf 462 '+str(len(clauses))+'\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses)
    root = init('budget_control', text, 0.01)
    proc = command(root, 'run', background=True)
    state = wait(root, proc, lambda s: s['request'] is not None)
    ident, cpu = state['child'], state['live_cpu']
    state = wait(root, proc, lambda s: s['live_cpu'] > cpu+0.15)
    require(state['child'] == ident and state['budget'] == 0.01, 'Budget paused/restarted solver')
    request = state['request']['id']
    command(root, 'reply', '--request', request, '--seconds', 1, '--answer-id', 'extend')
    command(root, 'reply', '--request', request, '--seconds', 1, '--answer-id', 'extend')
    state = wait(root, proc, lambda s: s['request'] is not None and s['request']['id'] != request)
    require(state['child'] == ident and state['budget'] == 1.01, 'Extension not exact once')
    command(root, 'reply', '--request', state['request']['id'], '--seconds', 0, '--answer-id', 'stop')
    require(proc.wait() == 0, 'Controlled stop failed')
    first = r.read(root/'state.json')
    require(first['status'] == 'STOPPED_UNRESOLVED', 'Zero falsely resolved control')
    finished(root)
    old = {str(p.relative_to(root)): r.sha(p) for p in (root/'attempts').rglob('*') if p.is_file()}
    proc = command(root, 'resume', background=True)
    state = wait(root, proc, lambda s: s['request'] is not None)
    command(root, 'reply', '--request', state['request']['id'], '--seconds', 0, '--answer-id', 'stopresume')
    require(proc.wait() == 0, 'Resume stop failed')
    final = r.read(root/'state.json')
    require(final['cpu_completed'] > first['cpu_completed'] and len(final['attempts']) == 2, 'Lost resume accounts')
    require(all(r.sha(root/p) == digest for p,digest in old.items()), 'Old attempt changed')
    finished(root)
    rows.append(dict(test='EOF_continues_extension_duplicate_zero_resume_and_host_accounts', passed=True))
    result = dict(stage='TARGET_CONTROLS', status='PASS', tests=rows, windows_executed=True,
                  production_approved=False, N1_class_searches=0,
                  next_stage='review these target receipts before separate calibration release')
    r.raw_atomic(out/'RESULT.json', result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['probe','controls'])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--worker', type=Path)
    parser.add_argument('--checker', type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=False)
    try:
        result = probe(out) if args.action == 'probe' else controls(out, args.worker.resolve(), args.checker.resolve())
    except BaseException as exc:
        # Only our finite acceptance controls; never signal unrelated work.
        for root, proc in CONTROL_PROCESSES:
            while proc.poll() is None:
                state = r.read(root / "state.json")
                if state["request"] is not None:
                    r.reply(root, state["request"]["id"], 0, "testfailure" + uuid.uuid4().hex)
                    proc.wait()
                    break
                time.sleep(0.1)
        r.raw_atomic(out/'FAILED.json', dict(error=type(exc).__name__+': '+str(exc), production_approved=False))
        raise
    print(json.dumps(dict(status=result['status'], stage=result['stage'], output=str(out), production_approved=False)))


if __name__ == '__main__':
    main()
