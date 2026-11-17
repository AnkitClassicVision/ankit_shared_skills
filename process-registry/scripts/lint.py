#!/usr/bin/env python3
"""Lint the process registry and, with --qa, its QA registry.

  python lint.py <registry> [--qa <qa registry>] [--summary] [--strict]

  python lint.py <registry> --qa <qa> --against <main checkout> --against-qa <qa main checkout>

Errors make the exit code 1. Warnings and review flags do not, unless --strict is set.
What it protects:
  - the folder shape every harness relies on
  - stage order: a stage only needs stages with a lower number
  - blind QA: no criteria, golden sets or copies of them in the main registry
  - honest status: 'verified' and 'portable' have to be earned
  - the bar: with --against, any change that lowers it is flagged for a human

The leak checks catch files in the wrong place and copied text. They cannot
catch a paraphrase. Blind QA still rests on repo access, not on this script.
"""
import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("lint needs PyYAML. Install it with: pip install pyyaml")

STAGE_RE = re.compile(r"^(\d{2})([a-z]?)-([a-z0-9]+(?:-[a-z0-9]+)*)$")
GATE_RE = re.compile(r"^(\d{2})([a-z]?)\.1-qa$")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STATUSES = ("draft", "adopted", "verified", "portable", "retired")
EARNED = ("verified", "portable")
REQUIRED_KEYS = ("id", "owner", "version", "status", "human_gate", "runs_on",
                 "requires", "depends_on", "bounce_cap", "stages")
SKIP_DIRS = {".git", "runs", "__pycache__", "node_modules"}
GATE_STUB_MAX_LINES = 25
MIN_SECRET_CHARS = 30
MAX_TEXT_BYTES = 1_000_000
RANK = {"draft": 0, "adopted": 0, "verified": 1, "portable": 2}


class UniqueKeyLoader(yaml.SafeLoader):
    """YAML that refuses a key written twice. Plain YAML silently keeps the last one,
    which lets a second 'human_gate:' or 'status:' line override the first unseen."""


def _unique_mapping(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        try:
            key = loader.construct_object(key_node, deep=deep)
            dup = key in seen
            seen.add(key)
        except TypeError:
            continue
        if dup:
            raise yaml.constructor.ConstructorError(
                None, None, f"key '{key}' is written twice", key_node.start_mark)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)


def load_yaml(text):
    return yaml.load(text, Loader=UniqueKeyLoader)


def walk(root, skip=SKIP_DIRS):
    """Walk without following symlinks. Yields (folder, dir names, file names)."""
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in skip)
        yield Path(dirpath), dirnames, sorted(filenames)


def read_text(path):
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return None
        return path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def norm(line):
    line = re.sub(r"^\s*(?:[-*>]|\d+[.)])\s+", "", line)
    return re.sub(r"\s+", " ", line).strip().lower()


class Report:
    def __init__(self):
        self.errors, self.warnings, self.reviews = [], [], []

    def review(self, where, msg):
        self.reviews.append(f"{where}: {msg}")

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


def frontmatter(path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\s*(?:\n|$)", text, re.S)
    if not m:
        return None, text
    try:
        data = load_yaml(m.group(1))
    except yaml.YAMLError:
        return None, text
    return (data if isinstance(data, dict) else None), text[m.end():]


def check_skill_md(path, folder, rel, rep):
    """A SKILL.md must be a valid Agent Skills entry whose name matches its folder."""
    if not path.is_file():
        rep.err(rel, "SKILL.md is missing")
        return ""
    fm, body = frontmatter(path)
    if fm is None:
        rep.err(rel, "SKILL.md has no valid YAML frontmatter")
        return body
    name, desc = fm.get("name"), fm.get("description")
    if name != folder:
        rep.err(rel, f"SKILL.md name is {name!r}; it must match the folder name {folder!r}")
    if not isinstance(desc, str) or not desc.strip():
        rep.err(rel, "SKILL.md description is empty; routing depends on it")
    else:
        if len(desc) > 1024:
            rep.err(rel, "SKILL.md description is over 1024 characters")
        if "TODO" in desc:
            rep.err(rel, "SKILL.md description still says TODO")
    return body


def prefix_of(name):
    m = STAGE_RE.match(name) or GATE_RE.match(name)
    return m.group(1) + m.group(2)


def check_runbook(rb, registry, qa, rep):
    rid = rb.name
    rel = f"runbooks/{rid}"
    info = {"id": rid, "status": "?", "version": "?", "stages": 0, "gates": 0, "runs_on": 0}
    if not ID_RE.match(rid):
        rep.err(rel, "folder name must be lowercase letters, digits and hyphens")

    body = check_skill_md(rb / "SKILL.md", rid, rel, rep)

    proc = rb / "process.yaml"
    if not proc.is_file():
        rep.err(rel, "process.yaml is missing")
        return info
    try:
        data = load_yaml(proc.read_text())
    except yaml.YAMLError as exc:
        rep.err(rel, "process.yaml does not parse: " + " ".join(str(exc).split()))
        return info
    if not isinstance(data, dict):
        rep.err(rel, "process.yaml must be a mapping")
        return info

    for key in REQUIRED_KEYS:
        if key not in data:
            rep.err(rel, f"process.yaml is missing '{key}'")
    if "description" in data:
        rep.err(rel, "process.yaml has a 'description'. It belongs in SKILL.md only, so the two cannot drift")
    if data.get("id") != rid:
        rep.err(rel, f"process.yaml id is {data.get('id')!r}; it must match the folder name")
    if not str(data.get("owner") or "").strip():
        rep.err(rel, "process.yaml has no owner")

    status = data.get("status")
    info["status"], info["version"] = str(status), str(data.get("version"))
    if status not in STATUSES:
        rep.err(rel, f"status {status!r} is not one of {', '.join(STATUSES)}")
    runs_on = data.get("runs_on") or []
    if not isinstance(runs_on, list):
        rep.err(rel, "runs_on must be a list")
        runs_on = []
    info["runs_on"] = len(runs_on)
    if status == "verified" and len(runs_on) < 1:
        rep.err(rel, "status is 'verified' but runs_on is empty; name the harness it passed on")
    if status == "portable" and len(runs_on) < 2:
        rep.err(rel, "status is 'portable' but runs_on lists fewer than two harnesses")
    if status == "adopted" and not str(data.get("source") or "").strip():
        rep.warn(rel, "status is 'adopted' but 'source' is empty; say where it lives today")
    cap = data.get("bounce_cap")
    if "bounce_cap" in data and (not isinstance(cap, int) or isinstance(cap, bool) or cap < 1):
        rep.err(rel, "bounce_cap must be a whole number, 1 or more")

    # Folders on disk
    stage_dirs, gate_dirs = set(), set()
    for d in sorted(p for p in rb.iterdir() if p.is_dir()):
        if STAGE_RE.match(d.name):
            stage_dirs.add(d.name)
        elif GATE_RE.match(d.name):
            gate_dirs.add(d.name)
        elif d.name[:1].isdigit():
            rep.err(rel, f"folder '{d.name}' is not a valid stage (NN-name) or gate (NN.1-qa) name")

    # Stages in process.yaml
    stages = data.get("stages")
    if not isinstance(stages, list) or not stages:
        rep.err(rel, "process.yaml 'stages' must be a non-empty list")
        stages = []
    ids, gated = [], set()
    for s in stages:
        if not isinstance(s, dict) or "id" not in s:
            rep.err(rel, "every stage needs an 'id'")
            continue
        sid = str(s["id"])
        if not STAGE_RE.match(sid):
            rep.err(rel, f"stage id '{sid}' must look like 01-name or 02a-name")
            continue
        if sid in ids:
            rep.err(rel, f"stage '{sid}' is listed twice")
            continue
        ids.append(sid)
        if not isinstance(s.get("needs"), list):
            rep.err(rel, f"stage '{sid}' must have a 'needs' list ([] if it needs nothing)")
        if not isinstance(s.get("gate"), bool):
            rep.err(rel, f"stage '{sid}' must have 'gate: true' or 'gate: false'")
        elif s["gate"]:
            gated.add(sid)
    info["stages"], info["gates"] = len(ids), len(gated)

    prefixes = {}
    for sid in ids:
        pre = prefix_of(sid)
        if pre in prefixes:
            rep.err(rel, f"stages '{prefixes[pre]}' and '{sid}' share the prefix '{pre}'; "
                         "side-by-side stages need different letters")
        prefixes[pre] = sid

    for sid in ids:
        if sid not in stage_dirs:
            rep.err(rel, f"stage '{sid}' is in process.yaml but has no folder")
    for d in sorted(stage_dirs - set(ids)):
        rep.err(rel, f"folder '{d}' is not listed under stages in process.yaml")

    # Order: needs point backwards only, which also rules out cycles.
    for s in stages:
        if not isinstance(s, dict) or str(s.get("id")) not in ids:
            continue
        sid = str(s["id"])
        num = STAGE_RE.match(sid).group(1)
        for need in s.get("needs") or []:
            need = str(need)
            if need not in ids:
                rep.err(rel, f"stage '{sid}' needs '{need}', which is not a stage here")
            elif STAGE_RE.match(need).group(1) >= num:
                rep.err(rel, f"stage '{sid}' needs '{need}'. A stage may only need stages with a lower "
                             "number. Stages that share a number run side by side and cannot depend on each other")

    # Stage files
    todo_files = 0
    if "TODO" in body:
        todo_files += 1
    for sid in sorted(set(ids) & stage_dirs):
        for fname in ("STAGE.md", "deliverable.md"):
            f = rb / sid / fname
            if not f.is_file():
                rep.err(f"{rel}/{sid}", f"{fname} is missing")
            elif "TODO" in f.read_text():
                todo_files += 1
        if (rb / sid / "SKILL.md").exists():
            rep.err(f"{rel}/{sid}", "a stage must not contain SKILL.md. One SKILL.md per runbook, "
                                    "or harnesses list every stage as its own skill. Use STAGE.md")

    # Gates: a folder exists exactly when gate is true
    for sid in ids:
        gid = f"{prefix_of(sid)}.1-qa"
        has = gid in gate_dirs
        if sid in gated and not has:
            rep.err(rel, f"stage '{sid}' has gate: true but there is no '{gid}' folder")
        if has and sid not in gated:
            rep.err(rel, f"folder '{gid}' exists but stage '{sid}' has gate: false")
    for gid in sorted(gate_dirs):
        grel = f"{rel}/{gid}"
        if prefix_of(gid) not in prefixes:
            rep.err(grel, "gate has no matching stage")
        stub = rb / gid / "GATE.md"
        if not stub.is_file():
            rep.err(grel, "GATE.md is missing")
        else:
            lines = [ln for ln in stub.read_text().splitlines() if ln.strip()]
            if len(lines) > GATE_STUB_MAX_LINES:
                rep.warn(grel, f"GATE.md has {len(lines)} lines. A gate stub is a handoff only; "
                               "check that no criteria crept in")
        extra = sorted(p.name for p in (rb / gid).iterdir() if p.name != "GATE.md")
        if extra:
            rep.err(grel, f"a gate folder may hold only GATE.md; found {', '.join(extra)}")

    # Human yes points: decided, or openly undecided
    if "human_gate" in data:
        hg = data["human_gate"]
        if hg == "undecided":
            msg = "human_gate is 'undecided'. Someone has to decide: [] for none, or a list of stage ids"
            (rep.err if status in EARNED else rep.warn)(rel, msg)
        elif isinstance(hg, list):
            for sid in hg:
                if str(sid) not in ids:
                    rep.err(rel, f"human_gate names '{sid}', which is not a stage here")
        else:
            rep.err(rel, "human_gate must be a list of stage ids, [] or 'undecided'")

    # Dependencies
    deps = data.get("depends_on") or []
    if not isinstance(deps, list):
        rep.err(rel, "depends_on must be a list")
        deps = []
    for dep in deps:
        dep = str(dep)
        if not re.match(r"^(skills|runbooks)/[a-z0-9-]+$", dep):
            rep.err(rel, f"depends_on entry '{dep}' must look like skills/<id> or runbooks/<id>")
        elif not (registry / dep).is_dir():
            rep.err(rel, f"depends_on entry '{dep}' does not exist")

    if todo_files:
        msg = f"{todo_files} file(s) still contain TODO"
        (rep.err if status in EARNED else rep.warn)(rel, msg)

    # QA registry side
    if qa is not None:
        qrb = qa / "runbooks" / rid
        for sid in sorted(gated):
            gid = f"{prefix_of(sid)}.1-qa"
            qfile = qrb / gid / "qa.md"
            qrel = f"{qa.name}/runbooks/{rid}/{gid}"
            if not qfile.is_file():
                msg = "qa.md is missing; this gate has nothing to grade against"
                (rep.err if status in EARNED else rep.warn)(qrel, msg)
            elif "TODO" in qfile.read_text():
                msg = "qa.md still contains TODO"
                (rep.err if status in EARNED else rep.warn)(qrel, msg)
            if status in EARNED:
                gdir = qrb / gid / "golden"
                names = [p.name.lower() for p in gdir.iterdir()] if gdir.is_dir() else []
                if not any(n.startswith("good") for n in names):
                    rep.err(qrel, "no known-good example in golden/ (name it good-<case>). "
                                  "A gate is only proven when it passes one")
                if not any(n.startswith("bad") for n in names):
                    rep.err(qrel, "no known-bad example in golden/ (name it bad-<case>). "
                                  "A gate that has never failed anything is not proven")
        if qrb.is_dir():
            for d in sorted(p for p in qrb.iterdir() if p.is_dir()):
                if d.name not in gate_dirs:
                    rep.warn(f"{qa.name}/runbooks/{rid}/{d.name}",
                             "criteria folder has no matching gate in the main registry")
    return info


def check_leaks(registry, qa, rep):
    """Blind QA depends on this: criteria and golden sets never sit in the main registry.

    Three tripwires: files in the wrong place, symlinks that point out of the repo,
    and (with --qa) text or files copied from the QA registry.
    """
    files = []
    for folder, dirnames, filenames in walk(registry):
        rel_dir = folder.relative_to(registry)
        for name in dirnames + filenames:
            p = folder / name
            rel = str(rel_dir / name)
            if p.is_symlink():
                target = p.resolve()
                if target != registry and registry not in target.parents:
                    rep.err(rel, "symlink points outside the registry. Nothing in the main registry "
                                 "may link to the QA registry or anywhere else")
                continue
            if name in dirnames:
                if name.lower() == "golden":
                    rep.err(rel, "a golden set found in the main registry. Move it to the QA registry")
            else:
                if name.lower() == "qa.md":
                    rep.err(rel, "QA criteria found in the main registry. Move the file to the QA registry")
                files.append(p)
    if qa is None or not (qa / "runbooks").is_dir():
        return

    secrets, golden_hashes = {}, {}
    for folder, _, filenames in walk(qa / "runbooks"):
        in_golden = "golden" in (part.lower() for part in folder.relative_to(qa).parts)
        for name in filenames:
            p = folder / name
            if p.is_symlink():
                continue
            src = str(p.relative_to(qa))
            if in_golden:
                try:
                    data = p.read_bytes()
                except OSError:
                    continue
                if data.strip():
                    golden_hashes.setdefault(hashlib.sha256(data).hexdigest(), src)
                continue
            text = read_text(p)
            if text is None:
                continue
            for line in text.splitlines():
                n = norm(line)
                if len(n) >= MIN_SECRET_CHARS and not n.startswith("#") and "todo" not in n:
                    secrets.setdefault(n, src)
    if not secrets and not golden_hashes:
        return

    templates = registry / "tools" / "templates"
    for p in files:
        if templates in p.parents:
            continue
        rel = str(p.relative_to(registry))
        if golden_hashes:
            try:
                digest = hashlib.sha256(p.read_bytes()).hexdigest()
            except OSError:
                digest = None
            if digest in golden_hashes:
                rep.err(rel, f"this file is a copy of a golden example ({qa.name}/{golden_hashes[digest]})")
                continue
        text = read_text(p)
        if text is None or not secrets:
            continue
        lines = [norm(ln) for ln in text.splitlines()]
        lines = [ln for ln in lines if len(ln) >= MIN_SECRET_CHARS]
        reported = set()
        for secret, src in secrets.items():
            if src in reported:
                continue
            if any(secret in ln for ln in lines):
                reported.add(src)
                rep.err(rel, f"contains the same text as {qa.name}/{src}: \"{secret[:60]}...\". "
                             "If the maker is meant to know it, keep it here and reword the check so it "
                             "says how this is verified. If not, remove it from the main registry")


def snapshot(registry, qa):
    """What the change guard compares: one record per runbook."""
    snap = {}
    root = registry / "runbooks"
    if not root.is_dir():
        return snap
    for rb in sorted(p for p in root.iterdir() if p.is_dir()):
        try:
            data = yaml.safe_load((rb / "process.yaml").read_text()) or {}
        except (OSError, yaml.YAMLError):
            data = {}
        if not isinstance(data, dict):
            data = {}
        gated = set()
        for st in data.get("stages") or []:
            if isinstance(st, dict) and st.get("gate") is True:
                gated.add(str(st.get("id")))
        h = hashlib.sha256()
        for folder, _, filenames in walk(rb):
            for name in filenames:
                p = folder / name
                if p.name == "process.yaml" or p.is_symlink():
                    continue
                h.update(str(p.relative_to(rb)).encode())
                h.update(p.read_bytes())
        qh = None
        if qa is not None:
            q = hashlib.sha256()
            qrb = qa / "runbooks" / rb.name
            if qrb.is_dir():
                for folder, _, filenames in walk(qrb):
                    for name in filenames:
                        p = folder / name
                        if not p.is_symlink():
                            q.update(str(p.relative_to(qrb)).encode())
                            q.update(p.read_bytes())
            qh = q.hexdigest()
        snap[rb.name] = {
            "gated": gated, "human_gate": data.get("human_gate"), "status": str(data.get("status")),
            "version": str(data.get("version")), "bounce_cap": data.get("bounce_cap"),
            "content": h.hexdigest(), "qa": qh,
        }
    return snap


def change_guard(now, base, rep):
    """Flag every change that could lower the bar, so a person looks at it.

    Lint cannot tell a good reason from a bad one. It can make sure the change is seen.
    """
    for rid, old in sorted(base.items()):
        rel = f"runbooks/{rid}"
        new = now.get(rid)
        if new is None:
            rep.review(rel, "runbook folder removed. Retire a process (status: retired) instead of deleting it")
            continue
        for sid in sorted(old["gated"] - new["gated"]):
            rep.review(rel, f"gate removed from stage '{sid}'")
        if old["human_gate"] != new["human_gate"]:
            rep.review(rel, f"human_gate changed from {old['human_gate']!r} to {new['human_gate']!r}. "
                            "Only the owner decides this")
        if RANK.get(new["status"], 0) > RANK.get(old["status"], 0):
            rep.review(rel, f"status promoted from {old['status']} to {new['status']}. Check the passing verdicts")
        try:
            if int(new["bounce_cap"]) > int(old["bounce_cap"]):
                rep.review(rel, f"bounce_cap raised from {old['bounce_cap']} to {new['bounce_cap']}")
        except (TypeError, ValueError):
            pass
        changed = old["content"] != new["content"]
        if changed and old["version"] == new["version"]:
            rep.review(rel, f"instructions or deliverables changed but version is still {new['version']}")
        if changed and old["qa"] is not None and new["qa"] is not None and old["qa"] != new["qa"]:
            rep.review(rel, "a stage and its criteria changed together. This is the one move that can "
                            "quietly lower the bar, so look at both")


def print_summary(infos):
    if not infos:
        return
    print("\nRunbooks")
    print(f"  {'id':<32} {'status':<9} {'version':<8} {'stages':>6} {'gates':>5} {'harnesses':>9}")
    for i in infos:
        print(f"  {i['id']:<32} {i['status']:<9} {i['version']:<8} {i['stages']:>6} {i['gates']:>5} {i['runs_on']:>9}")
    live = [i for i in infos if i["status"] != "retired"]
    if live:
        portable = sum(i["status"] == "portable" for i in live)
        earned = sum(i["status"] in EARNED for i in live)
        print(f"\n  live: {len(live)}   verified or better: {earned} ({100 * earned // len(live)}%)   "
              f"portable: {portable} ({100 * portable // len(live)}%)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("registry", help="path to the main registry")
    ap.add_argument("--qa", help="path to the QA registry; adds the criteria checks")
    ap.add_argument("--against", help="path to a checkout of the main branch; flags changes that lower the bar")
    ap.add_argument("--against-qa", help="path to a checkout of the QA registry's main branch")
    ap.add_argument("--summary", action="store_true", help="print the runbook scoreboard")
    ap.add_argument("--strict", action="store_true", help="treat warnings and review flags as failures")
    args = ap.parse_args()

    registry = Path(args.registry).resolve()
    qa = Path(args.qa).resolve() if args.qa else None
    rep = Report()

    if not registry.is_dir():
        sys.exit(f"error: {registry} is not a folder")
    for name in ("CLAUDE.md", "AGENTS.md", "ROUTE.md"):
        if not (registry / name).is_file():
            rep.err(name, "missing at the registry root")
    if qa is not None:
        if not qa.is_dir():
            sys.exit(f"error: {qa} is not a folder")
        if not (qa / "AGENTS.md").is_file():
            rep.err(f"{qa.name}/AGENTS.md", "missing; the QA agent has no grading rules")

    infos = []
    rb_root = registry / "runbooks"
    if not rb_root.is_dir():
        rep.err("runbooks", "folder is missing")
    else:
        for rb in sorted(p for p in rb_root.iterdir() if p.is_dir()):
            infos.append(check_runbook(rb, registry, qa, rep))

    skills_root = registry / "skills"
    if skills_root.is_dir():
        for sk in sorted(p for p in skills_root.iterdir() if p.is_dir()):
            check_skill_md(sk / "SKILL.md", sk.name, f"skills/{sk.name}", rep)

    check_leaks(registry, qa, rep)

    if args.against:
        base_reg = Path(args.against).resolve()
        if not base_reg.is_dir():
            sys.exit(f"error: {base_reg} is not a folder")
        base_qa = Path(args.against_qa).resolve() if args.against_qa else None
        change_guard(snapshot(registry, qa if base_qa else None), snapshot(base_reg, base_qa), rep)

    route = registry / "ROUTE.md"
    if route.is_file():
        text = route.read_text()
        for i in infos:
            listed = f"runbooks/{i['id']}`" in text or f"runbooks/{i['id']} " in text
            if i["status"] != "retired" and not listed:
                rep.warn("ROUTE.md", f"no row for runbooks/{i['id']}; nothing can route to it")
            if i["status"] == "retired" and listed:
                rep.warn("ROUTE.md", f"still routes to retired runbook {i['id']}")

    if qa is not None and (qa / "runbooks").is_dir():
        known = {i["id"] for i in infos}
        for d in sorted(p for p in (qa / "runbooks").iterdir() if p.is_dir()):
            if d.name not in known:
                rep.warn(f"{qa.name}/runbooks/{d.name}", "criteria exist for a runbook that is not in the main registry")

    for w in rep.warnings:
        print(f"warning  {w}")
    for r in rep.reviews:
        print(f"review   {r}")
    for e in rep.errors:
        print(f"ERROR    {e}")
    if args.summary:
        print_summary(infos)
    print(f"\n{len(infos)} runbook(s), {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)"
          + (f", {len(rep.reviews)} change(s) need a human look" if args.against else "")
          + ("" if qa else "  (QA registry not checked; pass --qa)"))
    sys.exit(1 if rep.errors or (args.strict and (rep.warnings or rep.reviews)) else 0)


if __name__ == "__main__":
    main()
