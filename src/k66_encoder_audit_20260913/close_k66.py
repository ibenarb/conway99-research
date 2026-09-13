#!/usr/bin/env python3
"""Independent K66 orbit coverage and negative-minor audit; run on Ryzen."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import shutil
import subprocess
import sys
import time
from array import array
from collections import Counter
from fractions import Fraction
from pathlib import Path

VERSION = "1.0.1"
ANCHOR = "a85aabc475116c6cb5fa39a10d281767ab6f7cf5"
REPO = "ibenarb/conway99-research"
BRANCH = "research/algebra-memetic-20260912"
MANIFEST_SHA = "63cbc21e88e4d49b58da7401577593679caec77b9444fd3b236deba0ab679075"
RUN_NAME = "k66_v4_cert_20260908_231256_132359"
PERM4 = tuple(itertools.permutations(range(4)))
PAIR12 = tuple(itertools.combinations(range(12), 2))
EDGE_INDEX = {edge: index for index, edge in enumerate(PAIR12)}
PINNED = {
    "results/k66_encoder_audit_20260913/audit_status.json": "643a4eca6323b4ac462d4223e0e4f2f6ba93c3aa350894a8179c7d60d1700847",
    "results/k66_encoder_audit_20260913/replay_linkage.json": "236cae2b03d6e8293e9c5135502f02bf92715832e9c818d4c2f67e646d496c9f",
    "results/k66_encoder_audit_20260913/reproduction/summary.json": "c2de574e4be01aa0accacab87dd55381be4154f4eeafe79da176c2b654b28048",
}


CASE_RESULT_HASHES = {'v4_09238': 'b2cceae9af1de0d4468150706b11e4f4340c91c10d854a750d3761a6a0cef53b', 'v4_09233': '20b62e1cc991b3eca2a5bb82da2f841f43a218c7d5989af3cfbfd8d0b0de2e4b', 'v4_09333': '9c91dd5300c907c385dcef8cfaf59eac4ecd3765fd65c08597a6ff315def2d55', 'v4_09323': 'd808b96cfcd3bbf4ba31ca5327f80ddeb9ca5b2793f608c35d0ca5c687391747', 'v4_09239': '8a9646e82281627f89395d58db54301221a3c992432dafefebfb9c9150239e9d', 'v4_09234': '8590a519785272cbd253d134d967b2d29d3a83b4cc3ab8c986fc864131b86b52', 'v4_09331': 'e12dc035a7dcd787e5b77f6c18d9b3a8b666248582a8bd4e2650cdd71cb16606', 'v4_09317': '956c276c2b23960011022ad17000c01cbf17203b869a0e486ddc448f56baf7a1', 'v4_09285': '410065c808c2dd9d4685e0c774f316f628353901fa4438f7b35865f497644e05', 'v4_09332': '9b392bb1ba1735f80a33b89801408c1a2e55504379ad5cff8eb2e6c60a6b8342', 'v4_09236': '3d689e8469b2157045b995306b531ef9894c7d913f3153529c887ab020fa9dc1', 'v4_09227': 'd11674df8995359ce525d3d85c16fa6dfe7aecdad57058a45970871930a7355c', 'v4_09235': '3c477876799187101a282f9326260498759a6f74761f9c6e9b83fe8c08387e8c', 'v4_09220': '7aa4dec8f4a0bd9f768800d447ca892c22674cddd86f961b61244eff51afd34d', 'v4_09232': '5fa6f22c2f8b2df3dcadda8315a0b5a87795e7d4b1c1a13737a27f73b1c37532', 'v4_09284': '91e47a347cc06ecf03403a7d33afb63b10eefe264e78f2c9e893bd2d3fbb1b28', 'v4_09275': '25cd91feb25ea60c0235889c7df7322e5d107b6ea66ca0db39f0e2ad8c843ab6', 'v4_09274': '24124c3e55a0530a4d0fc6a9ecf9ed6116e8c5a8dee95e8cf87a5db41460a2d9', 'v4_09226': '7d4915e98bdc364087b2cc65acf22679ea6aefff64bf9652e3100addec5b394c', 'v4_09322': '23d5fd827035924818c70d25e57fce5377a74db32a163bae87d066fcc01f9877', 'v4_09316': '0d3b126c977bbadbc0516097ac05e66b652046767746480220a05242d0fd5f0a', 'v4_09221': 'e94326f366a130106fe6354215f28e81b2fecbea2aae8d943f983daf52200104', 'v4_09237': '7724d760a48bb27ce9b0a4ee3b3db2d8a7599476400186ce845bf4155bfbfdfb'}

def require(value, message):
    if not value:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_bytes(encoded(value))
    temp.replace(path)


def command(args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, stderr=subprocess.PIPE, timeout=300)


class Progress:
    def __init__(self):
        self.started = self.last = time.monotonic()
        self.phase_started = self.started
        self.phase = None

    def update(self, phase, done, total, force=False):
        now = time.monotonic()
        if phase != self.phase:
            self.phase, self.phase_started = phase, now
            force = True
        if force or now - self.last >= 600:
            eta = (now - self.phase_started) * (total - done) / done if done else None
            print("STATUS", json.dumps(dict(phase=phase, done=done, total=total,
                  elapsed_seconds=round(now - self.started, 2), ETA_phase_seconds=round(eta, 2) if eta is not None else None)), flush=True)
            self.last = now


def canonical_skeleton():
    partner = (1, 0, 3, 2)
    local_group = tuple(p for p in PERM4 if all(p[partner[i]] == partner[p[i]] for i in range(4)))
    subsets = tuple(itertools.combinations(range(4), 2))
    pattern_orbits = {}
    for first, second in itertools.product(subsets, repeat=2):
        orbit = frozenset((tuple(sorted(p[i] for i in first)), tuple(sorted(p[i] for i in second)))
                          for p in local_group)
        pattern_orbits[min(orbit)] = orbit
    representatives = sorted(pattern_orbits)
    lookup = {pair: i for i, representative in enumerate(representatives) for pair in pattern_orbits[representative]}
    swap = [lookup[(b, a)] for a, b in representatives]
    counts = Counter()
    for types in itertools.product(range(len(representatives)), repeat=3):
        overlap = sum(len(set(representatives[t][0]) & set(representatives[t][1])) for t in types)
        canonical = min(tuple(sorted(types)), tuple(sorted(swap[t] for t in types)))
        multiplicity = math.prod(len(pattern_orbits[representatives[t]]) for t in types)
        for s in [0, 1]:
            degree = 6 - s
            intersection = 6 - 5 * s - overlap
            if 0 <= intersection <= degree:
                counts[s, canonical] += multiplicity
    keys = sorted(counts)
    require(len(local_group) == 8 and len(representatives) == 7 and len(lookup) == 36, "local type partition")
    require(len(keys) == 72 and keys[66] == (1, (2, 2, 5)), "canonical k66 identity")
    s, types = keys[66]
    bits = [[int(i in representatives[t][0]), int(i in representatives[t][1])] for t in types for i in range(4)]
    overlap = sum(a * b for a, b in bits)
    degree, intersection = 6 - s, 6 - 5 * s - overlap
    cells = [intersection, degree - intersection, degree - intersection, 18 - 2 * degree + intersection]
    require(cells == [0, 5, 5, 8], "derived K66 cells")
    return dict(s=s, types=list(types), attached_T_bits=bits, cell_sizes=cells,
                raw_group_patterns=counts[s, types]), local_group


def fixed_matrix(skeleton):
    matrix = [[0] * 14 for _ in range(14)]
    for group in range(3):
        for a, b in [(0, 1), (2, 3)]:
            i, j = 4 * group + a, 4 * group + b
            matrix[i][j] = matrix[j][i] = 1
    for i, bits in enumerate(skeleton["attached_T_bits"]):
        for t, bit in enumerate(bits):
            matrix[i][12 + t] = matrix[12 + t][i] = bit
    matrix[12][12] = matrix[13][13] = 2
    matrix[12][13] = matrix[13][12] = skeleton["s"]
    return matrix


def target_matrix():
    return [[12 * (i == j) + 6 - 3 * (i < 12 and j < 12 and i // 4 == j // 4)
             for j in range(14)] for i in range(14)]


def stabilizer(skeleton, local_group, progress):
    fixed, target = fixed_matrix(skeleton), target_matrix()
    group = set()
    checked = 0
    for blocks in itertools.permutations(range(3)):
        for local in itertools.product(local_group, repeat=3):
            for swap in [0, 1]:
                checked += 1
                p = tuple(4 * blocks[i // 4] + local[i // 4][i % 4] for i in range(12)) + (12 + swap, 13 - swap)
                if all(fixed[p[i]][p[j]] == fixed[i][j] for i in range(14) for j in range(14)):
                    require(all(target[p[i]][p[j]] == target[i][j] for i in range(14) for j in range(14)),
                            "target covariance")
                    group.add(p)
        progress.update("STABILIZER", checked, 6144)
    require(checked == 6144 and len(group) == 64, "exhaustive stabilizer count")
    require(tuple(range(14)) in group, "group identity")
    for p in group:
        require(tuple(p.index(i) for i in range(14)) in group, "group inverse")
        for q in group:
            require(tuple(p[q[i]] for i in range(14)) in group, "group closure")
    return sorted(group)


def decode(code):
    first, remainder = divmod(code, 24 * 24)
    second, third = divmod(remainder, 24)
    require(0 <= first < 24, "matching code range")
    return [PERM4[i] for i in [first, second, third]]


def crossmask(code):
    mask = 0
    for (a, b), permutation in zip([(0, 1), (0, 2), (1, 2)], decode(code)):
        for i, j in enumerate(permutation):
            mask |= 1 << EDGE_INDEX[(4 * a + i, 4 * b + j)]
    require(mask.bit_count() == 12, "crossmatching edge count")
    return mask


def permute_mask(mask, edge_images):
    result = 0
    while mask:
        bit = mask & -mask
        result |= edge_images[bit.bit_length() - 1]
        mask -= bit
    return result


def orbit_partition(group, progress):
    masks = [crossmask(code) for code in range(24 ** 3)]
    lookup = {mask: code for code, mask in enumerate(masks)}
    require(len(lookup) == 13824, "complete distinct labelled universe")
    actions, fixed_counts = [], []
    for i, p in enumerate(group):
        edge_images = [1 << EDGE_INDEX[tuple(sorted((p[a], p[b])))] for a, b in PAIR12]
        action = array("H", (lookup[permute_mask(mask, edge_images)] for mask in masks))
        require(len(set(action)) == 13824, "non-bijective action")
        fixed_counts.append(sum(code == image for code, image in enumerate(action)))
        actions.append(action)
        progress.update("DIRECT_GRAPH_ACTIONS", i + 1, len(group))
    require(sum(fixed_counts) % len(group) == 0, "Burnside integrality")
    owner = [-1] * len(masks)
    orbits = []
    for code in range(len(masks)):
        if owner[code] != -1:
            continue
        members = sorted({a[code] for a in actions})
        require(members[0] == code and all(owner[m] == -1 for m in members), "orbit minimality/disjointness")
        point_stabilizer = sum(a[code] == code for a in actions)
        require(len(members) * point_stabilizer == len(group), "orbit-stabilizer theorem check")
        for member in members:
            owner[member] = code
        orbits.append(dict(code=code, members=members, size=len(members), point_stabilizer=point_stabilizer))
    require(all(x >= 0 for x in owner) and sum(o["size"] for o in orbits) == 13824, "label coverage")
    require(len(orbits) == sum(fixed_counts) // len(group) == 246, "Burnside/direct orbit agreement")
    return orbits, fixed_counts


def matrices(skeleton, code):
    h = fixed_matrix(skeleton)
    for (a, b), permutation in zip([(0, 1), (0, 2), (1, 2)], decode(code)):
        for i, j in enumerate(permutation):
            u, v = 4 * a + i, 4 * b + j
            h[u][v] = h[v][u] = 1
    target = target_matrix()
    gram = [[target[i][j] - h[i][j] - sum(h[i][k] * h[k][j] for k in range(14))
             for j in range(14)] for i in range(14)]
    return h, gram


def determinant(matrix):
    """Rational Gaussian elimination with row pivoting, independent of historical Bareiss code."""
    a = [[Fraction(v) for v in row] for row in matrix]
    result = Fraction(1)
    for k in range(len(a)):
        pivot_row = next((i for i in range(k, len(a)) if a[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            result = -result
        pivot = a[k][k]
        result *= pivot
        for i in range(k + 1, len(a)):
            factor = a[i][k] / pivot
            for j in range(k + 1, len(a)):
                a[i][j] -= factor * a[k][j]
    require(result.denominator == 1, "nonintegral determinant of integer matrix")
    return result.numerator


def psd_rank(matrix):
    a = [[Fraction(v) for v in row] for row in matrix]
    rank = 0
    for k in range(len(a)):
        pivot = a[k][k]
        require(pivot >= 0, "negative residual PSD pivot")
        if pivot == 0:
            require(all(a[k][j] == 0 for j in range(k, len(a))), "zero PSD pivot with nonzero row")
            continue
        rank += 1
        for i in range(k + 1, len(a)):
            for j in range(k + 1, len(a)):
                a[i][j] -= a[i][k] * a[k][j] / pivot
    return rank


def complete_units(skeleton, h):
    pairs = list(itertools.combinations(range(32), 2))
    units = {}
    d = 6 - skeleton["s"]
    c = skeleton["cell_sizes"][0]
    neighbors = [set(range(14, 14 + d)), set(range(14, 14 + c)) | set(range(14 + d, 14 + 2 * d - c))]
    for number, (i, j) in enumerate(pairs, 1):
        if i < 12 and j < 12:
            value = h[i][j]
        elif i in [12, 13] or j in [12, 13]:
            if j < 14:
                value = h[i][j]
            else:
                value = int(j in neighbors[i - 12])
        else:
            continue
        units[number] = number if value else -number
        units[number + 496] = -(number + 496)
    require(len(units) == 254, "canonical primary unit count")
    return [units[k] for k in sorted(units)]


def small_controls():
    require(determinant([[2, 1], [1, 2]]) == 3, "positive determinant")
    require(determinant([[0, 1], [1, 0]]) == -1, "row pivot sign")
    require(determinant([[1, 2], [2, 4]]) == 0, "singular determinant")
    require(determinant([[2, 1, 0], [1, 2, 1], [0, 1, 2]]) == 4, "3x3 determinant")
    require(psd_rank([[1, 1], [1, 1]]) == 1, "singular PSD")
    for bad in [[[0, 1], [1, 0]], [[1, 2], [2, 1]]]:
        try:
            psd_rank(bad)
        except RuntimeError:
            continue
        raise RuntimeError("indefinite negative control accepted")
    skeleton, group = canonical_skeleton()
    require(skeleton["raw_group_patterns"] == 96 and len(group) == 8, "small canonical-label control")
    return {"status": "PASS", "determinant_controls": 4, "PSD_controls": 3, "canonical_label": "k66_s1_t225"}


def published_case_bytes(result):
    """Reproduce the exact published projection without changing the local report."""
    compact = dict(result)
    compact["rounds"] = [{k: v for k, v in r.items() if k not in ("before", "after")}
                         for r in result["rounds"]]
    compact["cnfs"] = [{k: v for k, v in c.items() if k != "depends_on_earlier_removed"}
                       for c in result["cnfs"]]
    return encoded(compact)


def fetch_predecessors(output):
    fetched = {}
    for relative, expected in PINNED.items():
        path = output / "predecessors" / Path(relative).name
        data = command(["gh", "api", "repos/" + REPO + "/contents/" + relative + "?ref=" + ANCHOR,
                        "-H", "Accept: application/vnd.github.raw+json"])
        require(len(data) < 1024 * 1024, "unexpected predecessor size")
        require(expected is None or sha(data) == expected, "predecessor hash")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        fetched[path.name] = (json.loads(data), dict(commit=ANCHOR, path=relative, bytes=len(data), sha256=sha(data)))
    status, _ = fetched["audit_status.json"]
    linkage, _ = fetched["replay_linkage.json"]
    reproduction, _ = fetched["summary.json"]
    require(status["status"] == "ENCODER_AND_REDUCTION_AUDIT_PASS", "predecessor encoder audit")
    require(linkage["status"] == "ALL_28_REPLAY_INPUT_LINKS_PASS" and linkage["linked_records"] == 28,
            "predecessor replay linkage")
    require(reproduction["status"] == "PASS" and reproduction["case_count"] == 23 and
            reproduction["counts"] == {"STAR": 137, "DEEP7_GLOBAL": 7, "PREFLIGHT_GLOBAL": 8, "R2_GLOBAL": 15},
            "predecessor reproduction")
    return fetched


def publish(output, workspace):
    relative = "results/k66_completion_proof_20260913"
    worktree = output / "git_worktree"
    state_path = output / "publish_state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    if "commit" not in state:
        backup = workspace / "k66_restart_git_backup"
        origin = command(["git", "remote", "get-url", "origin"], backup).decode().strip()
        require(origin.rstrip("/").removesuffix(".git") in ("https://github.com/" + REPO, "git@github.com:" + REPO),
                "unexpected origin")
        if not worktree.exists():
            command(["git", "fetch", "origin", BRANCH], backup)
            command(["git", "merge-base", "--is-ancestor", ANCHOR, "FETCH_HEAD"], backup)
            command(["git", "worktree", "add", "--detach", str(worktree), "FETCH_HEAD"], backup)
        destination = worktree / relative
        destination.mkdir(parents=True, exist_ok=True)
        for path in sorted((output / "publish").iterdir()):
            require(path.suffix == ".json" and path.stat().st_size < 1024 * 1024, "compact JSON only")
            target = destination / path.name
            require(not target.exists() or target.read_bytes() == path.read_bytes(), "different prior published result")
            shutil.copyfile(path, target)
        command(["git", "add", "--", relative], worktree)
        staged = command(["git", "diff", "--cached", "--name-only"], worktree).decode().splitlines()
        require(all(p.startswith(relative + "/") for p in staged), "unexpected staged file")
        if staged:
            command(["git", "commit", "-m", "Verify complete K66 orbit coverage and all 223 exact negative minors"], worktree)
        state = dict(commit=command(["git", "rev-parse", "HEAD"], worktree).decode().strip(), path=relative)
        save(state_path, state)
    command(["git", "push", "origin", state["commit"] + ":refs/heads/" + BRANCH], worktree)
    tree = command(["git", "rev-parse", state["commit"] + ":" + relative], worktree).decode().strip()
    entries = json.loads(command(["gh", "api", "repos/" + REPO + "/git/trees/" + tree]))["tree"]
    byname, checked = {x["path"]: x for x in entries}, []
    for path in sorted((output / "publish").iterdir()):
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(byname[path.name]["sha"] == blob and byname[path.name]["size"] == len(data), "remote blob identity")
        back = command(["gh", "api", "repos/" + REPO + "/contents/" + relative + "/" + path.name +
                        "?ref=" + state["commit"], "-H", "Accept: application/vnd.github.raw+json"])
        require(back == data and sha(back) == sha(data), "full return download")
        checked.append(dict(file=path.name, bytes=len(data), sha256=sha(data), git_blob_sha1=blob))
        save(output / "GIT_COMPLETION_RECEIPT.json", dict(state, status="VERIFYING", files=checked))
    save(output / "GIT_COMPLETION_RECEIPT.json", dict(state, status="VERIFIED", files=checked))
    print("GIT_K66_COMPLETION_VERIFIED", json.dumps(state), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.home() / "conway99_workspace")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    controls = small_controls()
    print("K66_SMALL_CONTROLS", json.dumps(controls), flush=True)
    if args.controls_only:
        return
    workspace = args.workspace
    output = workspace / "k66_completion_proof_v1_0_1"
    output.mkdir(parents=True, exist_ok=True)
    import fcntl
    lock = (output / "audit.lock").open("w")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    manifest_path = workspace / "o3_reconciliation_runs" / RUN_NAME / "manifest.json"
    raw = manifest_path.read_bytes()
    require(sha(raw) == MANIFEST_SHA, "source manifest identity")
    manifest = json.loads(raw)
    require(manifest["case_id"] == "k66_s1_t225", "case scope")
    predecessors = fetch_predecessors(output)
    identity = dict(version=VERSION, script_sha256=sha(Path(__file__).read_bytes()), manifest_sha256=sha(raw),
                    predecessors={k: v[1] for k, v in predecessors.items()})
    token = sha(encoded(identity))
    checkpoint_path = output / "checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text()) if checkpoint_path.exists() else {"identity": token, "checked": {}}
    require(checkpoint["identity"] == token, "different audit identity; retain previous directory")
    progress = Progress()
    skeleton, local_group = canonical_skeleton()
    for key in skeleton:
        require(skeleton[key] == manifest["case_summary"][key], "independent skeleton/manifest mismatch: " + key)
    group = stabilizer(skeleton, local_group, progress)
    orbits, fixed_counts = orbit_partition(group, progress)
    excluded = {x["code"]: x for x in manifest["arithmetic_exclusions"]}
    residual = {x["code"]: x for x in manifest["jobs"]}
    require(len(excluded) == len(manifest["arithmetic_exclusions"]) == 223, "distinct exclusions")
    require(len(residual) == len(manifest["jobs"]) == 23 and not set(excluded) & set(residual), "distinct residual partition")
    require(set(excluded) | set(residual) == {o["code"] for o in orbits}, "complete 223+23 orbit partition")
    proof_records, residual_records = [], []
    for number, orbit in enumerate(orbits, 1):
        code = orbit["code"]
        h, gram = matrices(skeleton, code)
        matrix_hash = sha(encoded(gram))
        case_path = output / "checked_orbits" / f"orbit_{code:05d}.json"
        if code in excluded:
            entry = excluded[code]
            require(orbit["size"] == entry["orbit_size"], "excluded orbit size")
            indices = entry["witness"]["indices"]
            require(indices and len(set(indices)) == len(indices) and
                    all(type(i) is int and 0 <= i < 14 for i in indices), "principal minor indices")
            principal = [[gram[i][j] for j in indices] for i in indices]
            cached_hash = checkpoint["checked"].get(str(code))
            if cached_hash and case_path.exists() and sha(case_path.read_bytes()) == cached_hash:
                record = json.loads(case_path.read_text())
                require(record["gram_sha256"] == matrix_hash and record["indices"] == indices and
                        record["determinant"] == entry["witness"]["determinant"] and record["determinant"] < 0,
                        "cached witness binding")
            else:
                value = determinant(principal)
                require(value < 0 and value == entry["witness"]["determinant"], "negative determinant witness: " + str(code))
                record = dict(code=code, orbit_size=orbit["size"], indices=indices, determinant=value,
                              gram_sha256=matrix_hash, status="NEGATIVE_PRINCIPAL_MINOR_VERIFIED")
                save(case_path, record)
                checkpoint["checked"][str(code)] = sha(case_path.read_bytes())
                save(checkpoint_path, checkpoint)
            proof_records.append(record)
        else:
            job = residual[code]
            require(job["id"] == f"v4_{code:05d}" and job["matching_permutations"] == [list(p) for p in decode(code)],
                    "residual matching/code identity")
            require(job["units"] == complete_units(skeleton, h), "residual canonical primary assignment")
            rank = psd_rank(gram)
            result_path = workspace / "k66_encoder_reproduction_v1/cases" / job["id"] / "result.json"
            previous = json.loads(result_path.read_text())
            published_bytes = published_case_bytes(previous)
            require(sha(published_bytes) == CASE_RESULT_HASHES[job["id"]],
                    "pinned published residual projection: " + job["id"])
            require(previous["status"] == "PASS" and previous["case"] == job["id"] and
                    previous["identity"] == "8a9ed8646d9eb8e93cd5114be2d497192eb652e974dafe2bd0e3fabe7bb2010a" and
                    previous["arithmetic"]["rank"] == rank, "residual encoder-audit connection")
            record = dict(code=code, id=job["id"], orbit_size=orbit["size"], gram_sha256=matrix_hash,
                          PSD_rank=rank, primary_units_match=True, encoder_case_result_sha256=sha(result_path.read_bytes()),
                          encoder_published_result_sha256=sha(published_bytes),
                          status="RESIDUAL_LINK_VERIFIED")
            save(case_path, record)
            residual_records.append(record)
        progress.update("PRINCIPAL_MINORS_AND_RESIDUALS", number, len(orbits))
    require(Counter(r["PSD_rank"] for r in residual_records) == {11: 4, 12: 19}, "residual exact ranks")
    save(output / "publish/stabilizer.json", dict(vertex_permutations=group, direct_fixed_counts=fixed_counts,
         candidate_transformations=6144, order=len(group), skeleton=skeleton, target_covariance=True,
         closure=True, inverses=True))
    save(output / "publish/orbit_partition.json", orbits)
    save(output / "publish/negative_minors.json", proof_records)
    save(output / "publish/residual_links.json", residual_records)
    save(output / "publish/identity.json", identity)
    result = dict(status="K66_ARITHMETIC_AND_ORBIT_COVERAGE_PASS", case="k66_s1_t225", version=VERSION,
                  labelled_crossmatchings=13824, stabilizer_order=len(group), orbit_count=len(orbits),
                  orbit_size_histogram=dict(Counter(o["size"] for o in orbits)), Burnside_sum=sum(fixed_counts),
                  negative_principal_minors=len(proof_records), encoder_linked_residuals=len(residual_records),
                  labelled_arithmetic_exclusions=sum(r["orbit_size"] for r in proof_records),
                  labelled_residuals=sum(r["orbit_size"] for r in residual_records),
                  filters_used_before_coverage=[], new_solver_runs=0, new_proof_replays=0,
                  controls=controls, wall_seconds=round(time.monotonic() - progress.started, 3),
                  proof_scope="K66 case only, combined with the pinned encoder audit and existing Cake evidence.",
                  main897_evidence="Archived Cake confirmations and verified file integrity; no new replay.",
                  requires_final_review="Read saved results and assemble the final case theorem; no global SRG claim.")
    save(output / "publish/summary.json", result)
    print("K66_COMPLETION_RESULT", json.dumps(result), flush=True)
    if args.publish:
        publish(output, workspace)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("K66_COMPLETION_FAILED", type(error).__name__, str(error), file=sys.stderr, flush=True)
        if isinstance(error, subprocess.CalledProcessError):
            print(error.stderr.decode("utf-8", errors="replace"), file=sys.stderr)
        raise SystemExit(1)
