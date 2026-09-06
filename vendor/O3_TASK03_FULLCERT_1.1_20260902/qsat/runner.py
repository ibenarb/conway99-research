"""Persistent bounded QSAT supervisor (the production and microqueue kernel)."""
from __future__ import annotations
import fcntl, hashlib, json, os, signal, shutil, subprocess, time, uuid, sys
from pathlib import Path
from .core import canon, make_core
from .encode import cnf_from_core, write_cnf
from .sat_model import primary_edge_map, project_primary_model, ModelError
from .verify import verify

ROOT = Path(__file__).resolve().parents[1]
DONE = {"SAT_VERIFIED", "UNSAT_CERTIFIED", "TIMEOUT", "ERROR"}
GIB = 1024 ** 3

def pid_identity_alive(pid, start_ticks):
    try: return Path('/proc/%d/stat' % int(pid)).read_text().split()[21] == str(start_ticks)
    except (OSError, ValueError, IndexError): return False

def attempt_consumes_configuration(attempt):
    if attempt.get("timed_out"): return True
    if attempt.get("stop_signal"): return False
    if attempt.get("phase") == "SOLVER" and attempt.get("ended") is None: return False
    return True

def used_configurations(task):
    return {a.get("configuration") for a in task.get("attempts",[]) if a.get("configuration") and attempt_consumes_configuration(a)}

def classify_task(task, configs):
    state=task['state']; used=used_configurations(task)
    retry=state=='TIMEOUT' and any(name not in used for name,_ in configs)
    decided=state in {'SAT_VERIFIED','UNSAT_CERTIFIED'}
    open_=state in {'PENDING','RUNNING','CHECKING','STOPPED_RESUMABLE'} or retry
    return {'decided':decided,'open':open_,'retryable':retry,'exhausted':state=='TIMEOUT' and not retry,
            'terminal':decided or state=='ERROR' or (state=='TIMEOUT' and not retry),
            'running':state=='RUNNING','checking':state=='CHECKING','pending':state=='PENDING','error':state=='ERROR'}

def atomic(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")
    os.replace(tmp, path)

def sha256(path):
    digest = hashlib.sha256(); size = 0
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            size += len(block); digest.update(block)
    return size, digest.hexdigest()

def proc_group_rss_kib(pgid):
    total = 0
    for entry in Path("/proc").glob("[0-9]*"):
        try:
            # field 5 is process group; status avoids a shell/ps dependency.
            if int((entry / "stat").read_text().split()[4]) != pgid: continue
            for line in (entry / "status").read_text().splitlines():
                if line.startswith("VmRSS:"): total += int(line.split()[1]); break
        except (FileNotFoundError, PermissionError, IndexError, ValueError): pass
    return total

class Supervisor:
    """One lock-owning scheduler.  Dependencies are injectable for microqueue."""
    configs = (
        ("default", ()), ("plain", ("--plain",)), ("sat", ("--sat",)),
        ("unsat", ("--unsat",)),
    )
    proof_phases=('PROOF_HASH','LRAT_CHECK','CAKE_LPR_CHECK','CHECKING_COMPLETE')
    def __init__(self, run, types=(), *, core_factory=make_core, verifier=verify,
                 clock=time.time, poll=0.20, task_limit=7200, kill_grace=5,
                 max_jobs=12, resource_probe=None, solver_factory=None,
                 checker_limit=6*3600, phase_factory=None, disk_limit_override=None):
        self.run_dir = Path(run); self.types = list(types); self.core_factory = core_factory
        self.verifier = verifier; self.clock = clock; self.poll = poll
        self.task_limit = task_limit; self.kill_grace = kill_grace
        self.checker_limit = checker_limit
        self.max_jobs = min(12, max_jobs); self.resource_probe = resource_probe
        self.disk_limit_override = disk_limit_override
        self.solver_factory = solver_factory; self.phase_factory=phase_factory; self.children = {}; self.stop_requested = False
        self.stop_reason = None; self.pause = False; self.last_heartbeat = 0
        self.lock = None; self.stage = 8; self.started = None; self.finished = False
        self.metrics = None; self.next_resource_sample = 0; self.proof_checking = False
        self.campaign = None; self.active_base = 0

    def manifest_paths(self): return sorted((self.run_dir / "tasks").glob("*/manifest.json"))
    def load(self, path): return json.loads(Path(path).read_text())
    def save(self, path, data): atomic(path, data); self.heartbeat("state-change", force=True)

    def setup(self):
        for ordinal, typ in enumerate(self.types):
            name = "%02d-" % ordinal + ("-".join(map(str, typ)) if isinstance(typ, (tuple, list)) else str(typ))
            path = self.run_dir / "tasks" / name / "manifest.json"
            if not path.exists():
                atomic(path, {"type": typ, "ordinal": ordinal, "state": "PENDING", "attempts": []})

    def limits(self):
        if self.campaign:
            return self.campaign["ram_limit"], self.disk_limit_override if self.disk_limit_override is not None else self.campaign["disk_limit"]
        total = 0
        try:
            for line in Path("/proc/meminfo").read_text().splitlines():
                if line.startswith("MemTotal:"): total = int(line.split()[1]) * 1024; break
        except OSError: pass
        ram = min(48 * GIB, max(0, total - 8 * GIB))
        free = shutil.disk_usage(self.run_dir).free
        disk = self.disk_limit_override if self.disk_limit_override is not None else min(400 * GIB, max(0, free - 50 * GIB))
        return ram, disk

    def active_elapsed(self):
        return self.active_base + (0 if self.started is None else self.clock() - self.started)

    def persist_campaign(self):
        if not self.campaign: return
        snap=dict(self.campaign); snap['active_seconds']=self.active_elapsed(); snap['stage_hours']=self.stage
        atomic(self.run_dir/'campaign.json',snap)

    def phase_expired(self, child): return self.clock() >= child['phase_deadline']

    def resume_plan(self, task):
        if not task.get('attempts'): return ('SOLVER',None,None)
        rec=task['attempts'][-1]
        if task['state'] in {'CHECKING','STOPPED_RESUMABLE'} and rec.get('phase') in {'PROOF_HASH','LRAT_CHECK','CAKE_LPR_CHECK','PAUSED_CHECKING'}:
            phase=rec.get('resume_phase') or (rec.get('phase') if task['state']=='CHECKING' else ('CAKE_LPR_CHECK' if rec.get('checkers')==[0] else 'LRAT_CHECK'))
            return ('CHECKING',rec['id'],phase)
        return ('SOLVER',None,None)

    def resume_checking(self, path):
        data=self.load(path); _,_,phase=self.resume_plan(data); rec=data['attempts'][-1]
        proof,cnf=Path(rec['proof']),Path(rec.get('cnf',path.parent/'instance.cnf'))
        if not proof.is_file() or not proof.stat().st_size or not cnf.is_file():
            data['state']='ERROR';rec['error']='missing proof/CNF for checking resume';self.save(path,data);return False
        child={'record':rec,'proof':proof,'cnf':cnf,'phase':'RESUMING','checker_logs':rec.get('checker_logs',[])}
        if phase in {'LRAT_CHECK','CAKE_LPR_CHECK'} and rec.get('proof_sha256'):
            rec['after_hash_phase']=phase;child['after_hash_phase']=phase;phase='PROOF_HASH'
        elif phase=='PROOF_HASH' and rec.get('after_hash_phase'):child['after_hash_phase']=rec['after_hash_phase']
        self._spawn_checker(path,child,data,rec,phase);return True

    def usage(self):
        if self.resource_probe: return self.resource_probe()
        rss = sum(proc_group_rss_kib(child["proc"].pid) * 1024 for child in self.children.values())
        disk = sum(p.stat().st_size for p in self.run_dir.rglob("*") if p.is_file())
        return rss, disk, *self.limits()

    def sample_resources(self, force=False):
        now = self.clock()
        if force or self.metrics is None or now >= self.next_resource_sample:
            self.metrics = self.usage(); self.next_resource_sample = now + 30
            for child in self.children.values():
                rss=proc_group_rss_kib(child["proc"].pid);child["record"]["max_rss_kib"] = max(child["record"]["max_rss_kib"],rss)
                if child.get('phase')!='SOLVER' and child['record'].get('phases'): child['record']['phases'][-1]['max_rss_kib']=max(child['record']['phases'][-1].get('max_rss_kib',0),rss)
        return self.metrics

    def heartbeat(self, message="", force=False):
        now = self.clock()
        if not force and now - self.last_heartbeat < 60: return
        self.persist_campaign(); self.last_heartbeat = now; states = {}; verdicts = 0; errors = timeouts = 0; retryable = pending = running = checking = exhausted = 0
        completions=[];phases=[];open_count=terminal_count=0
        for path in self.manifest_paths():
            task = self.load(path); state = task["state"]; states[state] = states.get(state, 0) + 1
            verdicts += state in {"SAT_VERIFIED", "UNSAT_CERTIFIED"}; errors += state == "ERROR"; timeouts += state == "TIMEOUT"
            cls=classify_task(task,self.configs); retryable += cls['retryable'];open_count+=cls['open'];terminal_count+=cls['terminal']
            pending += state == "PENDING"; running += state == "RUNNING"; checking += state == "CHECKING"; exhausted += state == "TIMEOUT" and self._choose_config(task)[0] is None
            if task.get('attempts'):
                rec=task['attempts'][-1];phases.append({'ordinal':task['ordinal'],'state':state,'phase':rec.get('phase'),'pid':rec.get('phases',[{}])[-1].get('pid') if rec.get('phases') else None})
                ended=rec.get('certified_at',rec.get('verified_at',rec.get('ended')))
                if ended is not None: completions.append({'ordinal':task['ordinal'],'state':state,'at':ended})
        rss, disk, ram_limit, disk_limit = self.sample_resources(force=force)
        atomic(self.run_dir / "status.json", {"updated": now, "message": message, "stage_hours": self.stage,
               "runtime": self.active_elapsed(), "active": len(self.children),
               "open": open_count, "completed": terminal_count,
               "states": states, "verdicts": verdicts, "timeouts": timeouts, "errors": errors,
               "pending": pending, "running": running, "checking": checking, "retryable": retryable, "exhausted": exhausted,
               "current_phases":phases,"last_completions":sorted(completions,key=lambda x:x['at'])[-12:],
               "rss_bytes": rss, "disk_bytes": disk, "ram_limit": ram_limit, "disk_limit": disk_limit,
               "paused": self.pause, "stop_reason": self.stop_reason})

    def request_stop(self, reason="STOP_REQUESTED"):
        self.stop_reason = reason; self._collect_finished(); self.stop_requested = True
        for child in list(self.children.values()): self._signal(child, signal.SIGTERM, reason)

    def _collect_finished(self):
        changed=True
        while changed:
            changed=False
            for path,child in list(self.children.items()):
                if child['proc'].poll() is not None: self._collect(path);changed=True

    def _signal(self, child, sig, reason):
        if child['proc'].poll() is not None: return False
        if child.get("signal_at") is None:
            child["signal_at"] = self.clock(); child["reason"] = reason
            try: os.killpg(child["proc"].pid, sig)
            except ProcessLookupError: pass
            return True
        return False

    def _choose_config(self, manifest):
        used = used_configurations(manifest)
        for name, options in self.configs:
            if name not in used: return name, options
        return None, None

    def _start(self, path):
        data = self.load(path); name, options = self._choose_config(data)
        if data["state"] in {"STOPPED_RESUMABLE","CHECKING"} and data["attempts"]:
            rec = data["attempts"][-1]
            if rec.get("phase") in {"PAUSED_CHECKING","PROOF_HASH","LRAT_CHECK","CAKE_LPR_CHECK"}:
                self.resume_checking(path);return
        if name is None:
            data["state"] = "ERROR"; data["error"] = "no materially distinct portfolio configuration remains"; self.save(path, data); return
        directory = path.parent; core = self.core_factory(data["type"])
        core_path = directory / "core.json"; core_path.write_text(canon(core) + "\n")
        cnf_path = directory / "instance.cnf"; cnf, edge_vars = cnf_from_core(core); write_cnf(core, cnf_path)
        attempt_id = len(data["attempts"]) + 1; proof = directory / ("proof-%d.lrat" % attempt_id)
        witness = directory / ("witness-%d.out" % attempt_id)
        out = directory / ("solver-%d.out" % attempt_id); err = directory / ("solver-%d.err" % attempt_id)
        command = self.solver_factory(cnf_path, proof, witness, options, data) if self.solver_factory else ["cadical", *options, "--lrat", "--no-binary", "-w", str(witness), str(cnf_path), str(proof)]
        out_f, err_f = open(out, "wb"), open(err, "wb")
        proc = subprocess.Popen(command, stdout=out_f, stderr=err_f, start_new_session=True)
        cnf_size, cnf_hash = sha256(cnf_path)
        phase_started=self.clock();pgid=os.getpgid(proc.pid)
        rec = {"id": attempt_id, "configuration": name, "options": list(options), "cnf": str(cnf_path),
               "command": command, "started": self.clock(), "timeout": self.task_limit, "stdout": str(out),
               "stderr": str(err), "proof": str(proof), "witness": str(witness), "timeout_signal": None,
               "stop_signal": None, "max_rss_kib": 0, "cnf_size": cnf_size, "cnf_sha256": cnf_hash,
               "phase":"SOLVER","phases":[{"phase":"SOLVER","pid":proc.pid,"pgid":pgid,"started":phase_started,"deadline":phase_started+self.task_limit,"command":command}]}
        data["attempts"].append(rec); data["state"] = "RUNNING"; self.save(path, data)
        self.children[path] = {"proc": proc, "out": out_f, "err": err_f, "record": rec, "core": core,
                               "cnf": cnf_path, "proof": proof, "witness": witness, "edge_vars": edge_vars, "phase": "SOLVER",
                               "phase_started":phase_started,"phase_deadline":phase_started+self.task_limit}
        self.heartbeat("state-change", force=True)

    def _spawn_checker(self, path, child, data, rec, phase):
        """Persist and launch one proof/check phase; the event loop polls it."""
        directory = path.parent; proof = child["proof"]
        stream=None
        if phase == 'PROOF_HASH':
            out,err=directory/("hash-%d.out"%rec['id']),directory/("hash-%d.err"%rec['id'])
            child['proof_meta']=directory/("proof-%d.meta.json"%rec['id'])
            command=[sys.executable,'-m','qsat.proof_worker','hash-inputs',str(child['cnf']),str(proof),str(child['proof_meta'])]
        elif phase == "LRAT_CHECK":
            out, err = directory / ("lrat-%d.out" % rec["id"]), directory / ("lrat-%d.err" % rec["id"])
            command = ["lrat-check", str(child["cnf"]), str(proof)]
        else:
            out, err = directory / ("cake-lpr-%d.out" % rec["id"]), directory / ("cake-lpr-%d.err" % rec["id"])
            command = [str(ROOT / "dependencies" / "bin" / "cake_lpr"), str(child["cnf"]), str(proof)]
        if self.phase_factory:
            replacement=self.phase_factory(phase,command,path,rec)
            if replacement is not None:
                command=replacement
        out_f, err_f = open(out, "wb"), open(err, "wb")
        proc = subprocess.Popen(command, stdin=stream, stdout=out_f, stderr=err_f, start_new_session=True)
        phase_started=self.clock()
        child.update(proc=proc, out=out_f, err=err_f, stdin=stream, phase=phase, checker_started=phase_started, phase_started=phase_started, phase_deadline=phase_started+self.checker_limit, checker_logs=child.get("checker_logs", []) + [str(out), str(err)])
        child['record']=rec
        rec["phase"] = phase; rec.setdefault("phases", []).append({"phase": phase, "pid": proc.pid, "pgid": os.getpgid(proc.pid), "started": phase_started, "deadline":phase_started+self.checker_limit,"command": command})
        data["state"] = "CHECKING"; self.save(path, data); self.children[path] = child

    def _collect_checker(self, path):
        child = self.children[path]; proc = child["proc"]; proc.wait(); child["out"].close(); child["err"].close()
        if child.get("stdin"): child["stdin"].close()
        data = self.load(path); rec = data["attempts"][-1]; rec.update(child["record"])
        ended=self.clock();rec["phases"][-1].update({"ended":ended,"wall":ended-rec['phases'][-1]['started'], "exitcode": proc.returncode,"signal":(-proc.returncode if proc.returncode<0 else None),"cpu_time":None,"cpu_time_source":"not available from subprocess.Popen after reap"})
        if child.get("reason"):
            rec["stop_signal"] = child.get("reason", self.stop_reason); rec["resume_phase"]=child['phase'];rec["phase"] = "PAUSED_CHECKING"; data["state"] = "STOPPED_RESUMABLE"; self.children.pop(path); self.save(path, data); return
        if proc.returncode != 0:
            rec["phase"] = "CHECKING_FAILED"; rec["checkers"] = rec.get("checkers", []) + [proc.returncode]; data["state"] = "ERROR"; self.children.pop(path); self.save(path, data); return
        # cake_lpr reports malformed proofs on stderr but, by upstream design,
        # may still return zero.  Its documented positive verdict is required.
        if child['phase'] == 'CAKE_LPR_CHECK' and b's VERIFIED UNSAT' not in Path(child['out'].name).read_bytes():
            rec['phase']='CHECKING_FAILED'; rec['error']='cake_lpr did not print documented VERIFIED UNSAT verdict'; rec['checkers']=rec.get('checkers', [])+[proc.returncode]; data['state']='ERROR'; self.children.pop(path); self.save(path,data); return
        if child['phase']=='PROOF_HASH':
            meta=json.loads(Path(child['proof_meta']).read_text());expected_hash=rec.get('proof_sha256');expected_cnf_hash=rec.get('cnf_sha256')
            rec['cnf_size']=meta['cnf']['size'];rec['cnf_sha256']=meta['cnf']['sha256']
            rec['proof_size']=meta['lrat']['size'];rec['proof_sha256']=meta['lrat']['sha256']
            target=child.get('after_hash_phase') or rec.pop('after_hash_phase',None)
            if target:
                if ((expected_hash and expected_hash != meta['lrat']['sha256']) or
                    (expected_cnf_hash and expected_cnf_hash != meta['cnf']['sha256'])):
                    rec['phase']='CHECKING_FAILED';rec['error']='proof hash changed before resume';data['state']='ERROR';self.children.pop(path);self.save(path,data);return
                rec.pop('after_hash_phase',None);self._spawn_checker(path,child,data,rec,target);return
            self._spawn_checker(path,child,data,rec,'LRAT_CHECK');return
        if child["phase"] == "LRAT_CHECK":
            rec["checkers"] = [0]; self._spawn_checker(path, child, data, rec, "CAKE_LPR_CHECK"); return
        final_size, final_hash = sha256(child['proof']); final_cnf_size, final_cnf_hash = sha256(child['cnf'])
        if (final_size != rec['proof_size'] or final_hash != rec['proof_sha256'] or
            final_cnf_size != rec['cnf_size'] or final_cnf_hash != rec['cnf_sha256']):
            rec['phase']='CHECKING_FAILED'; rec['error']='LRAT hash changed during production checks'; data['state']='ERROR'; self.children.pop(path); self.save(path,data); return
        rec['proof_sha256_after_checks']=final_hash; rec['proof_size_after_checks']=final_size
        rec['cnf_sha256_after_checks']=final_cnf_hash; rec['cnf_size_after_checks']=final_cnf_size
        rec["checkers"] = [0, 0]; rec["phase"] = "CHECKING_COMPLETE"; rec['certified_at']=self.clock(); data["state"] = "UNSAT_CERTIFIED"; self.children.pop(path); self.save(path, data)

    def _collect(self, path):
        if self.children[path].get("phase") != "SOLVER":
            self._collect_checker(path); return
        child = self.children.pop(path); proc, runtime_rec = child["proc"], child["record"]
        child["out"].close(); child["err"].close(); proc.wait()
        data = self.load(path); rec = data["attempts"][-1]; rec.update(runtime_rec)
        rec["ended"] = self.clock(); rec["wall"] = rec["ended"] - rec["started"]; rec["exitcode"] = proc.returncode
        rec['phases'][-1].update({'ended':rec['ended'],'wall':rec['ended']-rec['phases'][-1]['started'],'exitcode':proc.returncode,'signal':(-proc.returncode if proc.returncode<0 else None),'cpu_time':None,'cpu_time_source':'not available from subprocess.Popen after reap'})
        rec["stdout_size"], rec["stdout_sha256"] = sha256(rec["stdout"])
        rec["stderr_size"], rec["stderr_sha256"] = sha256(rec["stderr"])
        rec["max_rss_kib"] = max(rec["max_rss_kib"], proc_group_rss_kib(proc.pid))
        if rec.get("timed_out"):
            data["state"] = "TIMEOUT"
            if child["proof"].exists():
                rec["incomplete_proof_size"] = child["proof"].stat().st_size
                rec["incomplete_proof_retained"] = True
        elif child.get("reason"):
            rec["stop_signal"] = child["reason"]; data["state"] = "STOPPED_RESUMABLE"
            if child["proof"].exists():
                rec["incomplete_proof_size"] = child["proof"].stat().st_size
                rec["incomplete_proof_retained"] = True
        elif proc.returncode == 10:
            try:
                selected = project_primary_model(child["witness"].read_text(), primary_edge_map(child["core"], child["edge_vars"]))
                self.verifier(child["core"], selected); data["state"] = "SAT_VERIFIED"; rec["selected_edges"] = selected;rec['verified_at']=self.clock()
            except Exception as exc:
                data["state"] = "ERROR"; rec["error"] = "SAT model projection: %s" % exc
        elif proc.returncode == 20 and child["proof"].exists():
            child["record"] = rec; child["phase"] = "SOLVER_DONE"; rec["phase"] = "PROOF_HASH"
            self._spawn_checker(path, child, data, rec, "PROOF_HASH"); return
        else: data["state"] = "ERROR"; rec["error"] = "solver exit %d" % proc.returncode
        self.save(path, data)
        if data["state"] == "SAT_VERIFIED": self.request_stop("SAT_QUOTIENT_FOUND")

    def _resource_gate(self):
        rss, disk, ram, dlim = self.sample_resources(); ratio = max(rss / ram if ram else 1, disk / dlim if dlim else 1)
        if ratio >= 1 or shutil.disk_usage(self.run_dir).free < 50 * GIB:
            self.request_stop("RESOURCE_STOP"); return
        self.pause = ratio >= .90 if not self.pause else ratio >= .80

    def _stage_gate(self):
        now = self.clock(); tasks = [self.load(p) for p in self.manifest_paths()]
        decided = sum(t["state"] in {"SAT_VERIFIED", "UNSAT_CERTIFIED"} for t in tasks)
        checking = any(self.load(p)["state"] == "CHECKING" for p in self.manifest_paths())
        verdict_times = [a.get("certified_at",a.get("verified_at",0)) for t in tasks for a in t["attempts"] if t["state"] in {"SAT_VERIFIED", "UNSAT_CERTIFIED"}]
        elapsed = self.active_elapsed()
        if self.stage == 8 and elapsed >= 8*3600:
            if decided >= 4 or any(now-x <= 2*3600 for x in verdict_times) or checking: self.stage = 24
            else: self.finished = True; self.stop_reason = "STOP_8H"
        elif self.stage == 24 and elapsed >= 24*3600:
            classes=[classify_task(t,self.configs) for t in tasks];open_types=sum(c['open'] for c in classes);retry=any(c['retryable'] for c in classes)
            if (decided >= 4 and any(now-x <= 8*3600 for x in verdict_times)) or (open_types <= 6 and retry) or checking: self.stage = 48
            else: self.finished = True; self.stop_reason = "STOP_24H"
        elif self.stage == 48 and elapsed >= 48*3600: self.finished = True; self.stop_reason = "STOP_48H"
        if decided >= 12 or (decided == len(tasks) and tasks): self.finished = True; self.stop_reason = "ALL_DECIDED"

    def _pending(self):
        pending = []
        for path in self.manifest_paths():
            data = self.load(path)
            retryable_timeout = data["state"] == "TIMEOUT" and self._choose_config(data)[0] is not None
            paused_check = data["state"] == "STOPPED_RESUMABLE" and data.get("attempts") and data["attempts"][-1].get("phase") == "PAUSED_CHECKING"
            orphan_check = data["state"] == "CHECKING" and path not in self.children
            if (data["state"] == "STOPPED_RESUMABLE" and not paused_check) or retryable_timeout or (data["state"] == "RUNNING" and path not in self.children):
                data["state"] = "PENDING"; self.save(path, data)
            if data["state"] == "PENDING" or paused_check or orphan_check: pending.append((not bool(data["attempts"]), data["ordinal"], path))
        # Frozen panel order, while every first attempt precedes any retry.
        return [p for _,_,p in sorted(pending, key=lambda item: (not item[0], item[1]))]

    def _reap_all(self):
        self._collect_finished()
        for path, child in list(self.children.items()):
            self._signal(child, signal.SIGTERM, self.stop_reason or "STOP_REQUESTED")
        deadline = time.monotonic() + self.kill_grace
        while self.children and time.monotonic() < deadline:
            for path, child in list(self.children.items()):
                if child["proc"].poll() is not None: self._collect(path)
            time.sleep(.02)
        for child in self.children.values():
            try: os.killpg(child["proc"].pid, signal.SIGKILL)
            except ProcessLookupError: pass
        for path in list(self.children): self._collect(path)

    def run(self):
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.lock = open(self.run_dir / "runner.lock", "a+")
        try: fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: self.lock.close(); raise RuntimeError("already running")
        self.setup()
        campaign_path = self.run_dir / "campaign.json"
        if campaign_path.exists():
            self.campaign = self.load(campaign_path); self.active_base = self.campaign["active_seconds"]; self.stage = self.campaign["stage_hours"]
        else:
            ram, disk = self.limits(); self.campaign = {"active_seconds": 0, "stage_hours": 8, "history": [], "ram_limit": ram, "disk_limit": disk, "disk_free_at_start": shutil.disk_usage(self.run_dir).free}
            help_text = subprocess.run(["cadical", "--help"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True).stdout
            required = ("--plain", "--sat", "--unsat", "--lrat", "--no-binary", "-w <sol>")
            if not all(option in help_text.decode(errors="replace") for option in required): raise RuntimeError("local CaDiCaL help lacks required documented options")
            self.campaign["cadical_help_sha256"] = hashlib.sha256(help_text).hexdigest()
            self.campaign["cadical_binary_sha256"] = sha256(shutil.which("cadical"))[1]
            self.campaign["portfolio"] = {name: list(options) for name, options in self.configs}
        self.started = self.clock(); self.campaign["history"].append({"resume_started": self.started}); atomic(campaign_path, self.campaign)
        atomic(self.run_dir / "runner.json", {"pid": os.getpid(), "started": self.started, "runner_instance_id": uuid.uuid4().hex,
               "proc_start_ticks": Path("/proc/self/stat").read_text().split()[21], "run_dir": str(self.run_dir)})
        previous = {s: signal.signal(s, lambda *_: self.request_stop("SIGNAL")) for s in (signal.SIGINT, signal.SIGTERM)}
        try:
            while not self.finished and not self.stop_requested:
                for path, child in list(self.children.items()):
                    if child["proc"].poll() is not None: self._collect(path)
                    elif self.phase_expired(child):
                        child["record"]["timed_out"] = child.get("phase") == "SOLVER"; child["record"]["timeout_signal"] = "SIGTERM"; self._signal(child, signal.SIGTERM, "TIMEOUT")
                    elif child.get("signal_at") and self.clock() - child["signal_at"] >= self.kill_grace: os.killpg(child["proc"].pid, signal.SIGKILL)
                self._resource_gate(); self._stage_gate()
                if self.finished or self.stop_requested: break
                if not self.pause and not self.stop_requested:
                    for path in self._pending():
                        if len(self.children) >= self.max_jobs: break
                        self._start(path)
                self.heartbeat("running")
                if not self.children and not self._pending(): self.finished = True; self.stop_reason = self.stop_reason or "QUEUE_DRAINED"
                time.sleep(self.poll)
        finally:
            self._reap_all(); self.heartbeat(self.stop_reason or "finished", force=True)
            self.campaign["active_seconds"] = self.active_elapsed(); self.campaign["stage_hours"] = self.stage
            self.campaign["history"][-1].update({"ended": self.clock(), "reason": self.stop_reason or "finished"}); atomic(self.run_dir / "campaign.json", self.campaign)
            for sig, handler in previous.items(): signal.signal(sig, handler)
            fcntl.flock(self.lock, fcntl.LOCK_UN); self.lock.close()

def main():
    from .cli import farthest_panel
    max_jobs=int(os.environ.get("QSAT_MAX_JOBS","12"))
    disk_gib=os.environ.get("QSAT_DISK_LIMIT_GIB")
    disk_limit_override=None if disk_gib is None else int(float(disk_gib)*GIB)
    Supervisor(Path(os.environ.get("QSAT_RUN_DIR", ROOT / "runs" / "preflight")), farthest_panel()["ordering"], max_jobs=max_jobs, disk_limit_override=disk_limit_override).run()
if __name__ == "__main__": main()
