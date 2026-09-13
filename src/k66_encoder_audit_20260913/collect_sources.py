#!/usr/bin/env python3
"""Collect bounded K66 source evidence on Ryzen; optionally publish verified text."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

VERSION = "1.0.0"
REPO = "ibenarb/conway99-research"
BRANCH = "research/algebra-memetic-20260912"
ANCHOR = "fba694b50357fdd795601a6b17c97036f06af101"
RUN_NAME = "k66_v4_cert_20260908_231256_132359"
FILE_LIMIT = 512 * 1024
TOTAL_LIMIT = 8 * 1024 * 1024
ARCHIVE_LIMIT = 32 * 1024 * 1024
PRUNE = {".git", ".venv", "venv", "node_modules", "__pycache__", "site-packages",
         "jobs", "cubes", "proofs", "proof", "dependencies", "git_worktree"}
MARKERS = (b"def build_star_cnf", b"def encode_global", b"NEIGHBOR_STAR",
           b"neighbor_star_deep7", b"profile_conflict_cnf_scout")


def hashes(data):
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "git_blob_sha1": hashlib.sha1(header + data).hexdigest()}


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def command(args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, stderr=subprocess.PIPE, timeout=300)


def api(endpoint, raw=False):
    args = ["gh", "api", "repos/" + REPO + "/" + endpoint]
    if raw:
        args += ["-H", "Accept: application/vnd.github.raw+json"]
    result = command(args)
    return result if raw else json.loads(result)


class Collector:
    def __init__(self, workspace, output):
        self.workspace = workspace
        self.output = output
        self.payload = output / "payload"
        self.payload.mkdir(parents=True, exist_ok=True)
        self.records = {}
        self.issues = []
        self.archives = []
        self.last_status = time.monotonic()
        self.scanned = 0

    def status(self, force=False):
        if force or time.monotonic() - self.last_status >= 600:
            print("STATUS", json.dumps({"phase": "SOURCE_COLLECTION", "scanned": self.scanned,
                  "collected": len(self.records), "ETA": "unknown during bounded discovery"}), flush=True)
            self.last_status = time.monotonic()

    def issue(self, path, reason):
        self.issues.append({"path": str(path), "reason": str(reason)})

    def add(self, origin, data, suffix, category):
        if len(data) > FILE_LIMIT:
            self.issue(origin, "FILE_SIZE_LIMIT")
            return
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            self.issue(origin, "NOT_UTF8")
            return
        if sum(r["bytes"] for r in self.records.values()) + len(data) > TOTAL_LIMIT:
            raise RuntimeError("text collection limit exceeded; local checkpoint retained")
        key = hashlib.sha256(origin.encode("utf-8")).hexdigest()[:16] + suffix
        destination = self.payload / key
        if destination.exists() and destination.read_bytes() != data:
            raise RuntimeError("source changed since checkpoint: " + origin)
        destination.write_bytes(data)
        self.records[key] = dict(origin=origin, category=category, **hashes(data))
        self.checkpoint()

    def checkpoint(self):
        save_json(self.output / "collection_checkpoint.json", {
            "version": VERSION, "files": self.records, "issues": self.issues,
            "archives": self.archives, "status": "SOURCE_EVIDENCE_ONLY"})

    def collect_archive(self, path):
        if path.stat().st_size > ARCHIVE_LIMIT:
            self.issue(path, "ARCHIVE_SIZE_LIMIT_NOT_OPENED")
            return
        try:
            with zipfile.ZipFile(path) as archive:
                members = archive.infolist()
                chosen = [m for m in members if m.filename.endswith(".py")
                          and not any(x in PRUNE for x in Path(m.filename).parts)]
                if not chosen:
                    return
                descriptor = dict(path=str(path), **hashes(path.read_bytes()))
                descriptor["python_members"] = len(chosen)
                self.archives.append(descriptor)
                for member in chosen:
                    if member.file_size > FILE_LIMIT:
                        self.issue(str(path) + "!" + member.filename, "MEMBER_SIZE_LIMIT")
                        continue
                    self.add(str(path) + "!" + member.filename, archive.read(member), ".py", "archive_source")
        except (OSError, zipfile.BadZipFile) as error:
            self.issue(path, type(error).__name__ + ": " + str(error))

    def discover(self):
        roots = [self.workspace, Path.home() / "Downloads", Path("/mnt/c/Users/rb/Downloads")]
        for root in roots:
            if not root.is_dir():
                continue
            def walk_error(error):
                self.issue(root, error)
            for directory, names, files in os.walk(root, onerror=walk_error, followlinks=False):
                parent = Path(directory)
                depth = len(parent.relative_to(root).parts)
                names[:] = sorted(n for n in names if n not in PRUNE and not n.startswith(".")
                                  and not (parent / n).is_symlink()
                                  and not (parent / n).resolve().is_relative_to(self.output.resolve()))
                if depth >= (9 if root == self.workspace else 1):
                    names[:] = []
                for name in sorted(files):
                    path = parent / name
                    if path.is_symlink():
                        continue
                    self.scanned += 1
                    self.status()
                    lower = name.lower()
                    try:
                        if path.suffix == ".py" and path.stat().st_size <= FILE_LIMIT:
                            data = path.read_bytes()
                            selected = ("k66" in lower or "neighbor_star" in lower
                                        or "profile_conflict" in lower or any(m in data for m in MARKERS))
                            reference = RUN_NAME in str(path) and ("/source/" in str(path) or "/reference/" in str(path))
                            if selected or reference:
                                self.add(str(path), data, ".py", "local_source")
                        elif path.suffix in (".zip", ".pyz") and any(s in lower for s in ("k66", "neighbor_star", "profile_conflict")):
                            self.collect_archive(path)
                    except OSError as error:
                        self.issue(path, error)
        self.checkpoint()

    def metadata(self):
        run = self.workspace / "o3_reconciliation_runs" / RUN_NAME
        subdirs = [run, run / "neighbor_star_preflight_20260909",
                   run / "neighbor_star_deep7_autonomous_20260909",
                   run / "profile_conflict_cnf_scout_20260909_r2"]
        for directory in subdirs:
            if not directory.is_dir():
                self.issue(directory, "MISSING_DIRECTORY")
                continue
            for path in sorted(directory.glob("*.json")):
                if path.stat().st_size <= FILE_LIMIT:
                    self.add(str(path), path.read_bytes(), ".json", "run_metadata")
                else:
                    self.issue(path, "METADATA_SIZE_LIMIT")
        reference = run / "reference/docs/breadth1/O3_fixed_triangle_internal_model.md"
        if reference.is_file():
            self.add(str(reference), reference.read_bytes(), ".md", "reference_document")
        inventory = []
        for directory in subdirs[1:3]:
            for path in sorted(directory.rglob("*.cnf")):
                inventory.append({"path": str(path), "bytes": path.stat().st_size})
        inventory_data = (json.dumps(inventory, indent=2) + "\n").encode("utf-8")
        self.add("generated:star_and_global_cnf_locations", inventory_data, ".json", "paths_only_no_cnf_read")
        self.checkpoint()
        save_json(self.payload / "SOURCE_INDEX.json", {
            "version": VERSION, "anchor": ANCHOR, "files": self.records,
            "issues": self.issues, "source_archives": self.archives,
            "claim": "Collected bytes and provenance candidates; no mathematical or CNF reproduction verdict."})
        extras = {p.name for p in self.payload.iterdir()} - set(self.records) - {"SOURCE_INDEX.json"}
        if extras:
            raise RuntimeError("unindexed checkpoint files: " + repr(sorted(extras)))
        self.status(force=True)


def publish(workspace, output):
    receipt_path = output / "GIT_SOURCE_RECEIPT.json"
    state_path = output / "publish_state.json"
    backup = workspace / "k66_restart_git_backup"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    worktree = output / "git_worktree"
    relative = "data/k66_encoder_audit_20260913/source_evidence"
    if "commit" not in state:
        origin = command(["git", "remote", "get-url", "origin"], backup).decode().strip()
        if origin.rstrip("/").removesuffix(".git") not in (
                "https://github.com/" + REPO, "git@github.com:" + REPO):
            raise RuntimeError("unexpected backup origin; publication stopped")
        if not worktree.exists():
            command(["git", "fetch", "origin", BRANCH], backup)
            command(["git", "merge-base", "--is-ancestor", ANCHOR, "FETCH_HEAD"], backup)
            command(["git", "worktree", "add", "--detach", str(worktree), "FETCH_HEAD"], backup)
        destination = worktree / relative
        destination.mkdir(parents=True, exist_ok=True)
        for path in sorted((output / "payload").iterdir()):
            target = destination / path.name
            if target.exists() and target.read_bytes() != path.read_bytes():
                raise RuntimeError("refusing to overwrite different published evidence: " + str(target))
            shutil.copyfile(path, target)
        command(["git", "add", "--", relative], worktree)
        staged = command(["git", "diff", "--cached", "--name-only"], worktree).decode().splitlines()
        if any(not name.startswith(relative + "/") for name in staged):
            raise RuntimeError("unexpected staged files in audit worktree")
        if staged:
            command(["git", "commit", "-m", "Collect K66 encoder sources and local reduction metadata"], worktree)
        state = {"commit": command(["git", "rev-parse", "HEAD"], worktree).decode().strip(), "path": relative}
        save_json(state_path, state)
    command(["git", "push", "origin", state["commit"] + ":refs/heads/" + BRANCH], worktree)
    tree_sha = command(["git", "rev-parse", state["commit"] + ":" + relative], worktree).decode().strip()
    tree = api("git/trees/" + tree_sha)
    remote = {entry["path"]: entry for entry in tree["tree"]}
    verified = []
    for path in sorted((output / "payload").iterdir()):
        expected = hashes(path.read_bytes())
        entry = remote[path.name]
        if entry["sha"] != expected["git_blob_sha1"] or entry["size"] != expected["bytes"]:
            raise RuntimeError("remote blob mismatch: " + path.name)
        data = api("contents/" + relative + "/" + path.name + "?ref=" + state["commit"], raw=True)
        if hashes(data) != expected or data != path.read_bytes():
            raise RuntimeError("full return download mismatch: " + path.name)
        verified.append(dict(file=path.name, **expected))
        save_json(receipt_path, dict(state, status="VERIFYING", verified=verified))
    receipt = dict(state, status="GIT_SOURCE_BACKUP_VERIFIED", files=len(verified), verified=verified)
    save_json(receipt_path, receipt)
    print("GIT_SOURCE_BACKUP_VERIFIED", json.dumps({k: v for k, v in receipt.items() if k != "verified"}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.home() / "conway99_workspace")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    output = args.workspace / "k66_encoder_source_audit_v1"
    output.mkdir(parents=True, exist_ok=True)
    if not (output / "publish_state.json").exists():
        collector = Collector(args.workspace, output)
        collector.discover()
        collector.metadata()
    if args.publish:
        publish(args.workspace, output)
    print("SOURCE_COLLECTION_COMPLETE", str(output / "payload/SOURCE_INDEX.json"), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("SOURCE_COLLECTION_FAILED", type(error).__name__, str(error), file=sys.stderr, flush=True)
        if isinstance(error, subprocess.CalledProcessError):
            print(error.stderr.decode("utf-8", errors="replace"), file=sys.stderr)
        raise SystemExit(1)
