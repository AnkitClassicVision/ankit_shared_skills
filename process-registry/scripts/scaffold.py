#!/usr/bin/env python3
"""Scaffold the process registry and its QA registry.

Commands
  init     create both repo skeletons, process zero and the repo-local tools
  runbook  add a runbook with stages, gate stubs and QA placeholders
  adopt    wrap an existing process as a runbook, captured as-is
  gate     add a QA gate to an existing stage

Nothing is ever overwritten. A file that already exists is kept and reported.
Standard library only.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE_RE = re.compile(r"^(\d{2})([a-z]?)-([a-z0-9]+(?:-[a-z0-9]+)*)$")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TOOLS = ("scaffold.py", "lint.py", "graph.py", "sync.py", "compare.py")


def die(msg):
    sys.exit(f"error: {msg}")


def templates_dir():
    for cand in (HERE / "templates", HERE.parent / "assets" / "templates"):
        if (cand / "parts").is_dir():
            return cand
    die("templates folder not found next to scaffold.py")


def render(text, values):
    """Fill {{tokens}} in one pass, so a token inside an inserted value stays literal."""
    return re.sub(r"\{\{(\w+)\}\}",
                  lambda m: str(values[m.group(1)]) if m.group(1) in values else m.group(0), text)


def one_line(text):
    return " ".join(str(text).split())


def write(path, text, created):
    path = Path(path)
    if path.exists():
        print(f"  keep    {path}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    created.append(path)
    print(f"  create  {path}")
    return True


def out_name(name):
    if name == "gitignore.tmpl":
        return ".gitignore"
    return name[:-5] if name.endswith(".tmpl") else name


def copy_tree(src, dst, values, created):
    for p in sorted(src.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(src)
        write(dst / rel.parent / out_name(p.name), render(p.read_text(), values), created)


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")
    if not s:
        die(f"cannot make a folder name from {text!r}")
    return s


def yaml_scalar(text):
    """Plain scalar when safe, otherwise a double-quoted string (valid YAML)."""
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./@ -]*", text) and text.lower() not in (
        "true", "false", "yes", "no", "null", "on", "off"
    ):
        return text
    return json.dumps(text)


def stage_prefix(stage_id):
    m = STAGE_RE.match(stage_id)
    return m.group(1) + m.group(2)


def gate_id_for(stage_id):
    return f"{stage_prefix(stage_id)}.1-qa"


def parse_stages(spec):
    """'collect, build-table | draft-email, send' -> ordered stages.

    A comma starts the next step. A pipe puts stages side by side: they get the
    same number and a letter, and they can run at the same time.
    """
    groups = []
    for chunk in spec.split(","):
        names = [slug(n) for n in chunk.split("|") if n.strip()]
        if names:
            groups.append(names)
    if not groups:
        die("--stages is empty")
    if len(groups) > 99:
        die("more than 99 steps; split this into several runbooks")
    stages, prev = [], []
    for i, names in enumerate(groups, 1):
        if len(names) > 26:
            die("more than 26 parallel stages in one step")
        if len(set(names)) != len(names):
            die(f"duplicate stage name in step {i}")
        ids = []
        for j, name in enumerate(names):
            letter = chr(ord("a") + j) if len(names) > 1 else ""
            sid = f"{i:02d}{letter}-{name}"
            ids.append(sid)
            stages.append({"id": sid, "needs": list(prev), "gate": False})
        prev = ids
    return stages


def match_stages(tokens, stages, flag):
    """Resolve names or ids given on the command line to stage ids."""
    found = []
    for tok in tokens:
        t = tok.strip()
        if not t:
            continue
        hits = [s["id"] for s in stages if s["id"] == t or STAGE_RE.match(s["id"]).group(3) == slug(t)]
        if len(hits) != 1:
            die(f"{flag}: {t!r} matches {len(hits)} stages; use the full stage id")
        found.append(hits[0])
    return found


def resolve_gates(spec, stages):
    spec = spec.strip().lower()
    if spec == "none":
        return set()
    if spec == "all":
        return {s["id"] for s in stages}
    if spec == "last":
        last = max(STAGE_RE.match(s["id"]).group(1) for s in stages)
        return {s["id"] for s in stages if STAGE_RE.match(s["id"]).group(1) == last}
    return set(match_stages(spec.split(","), stages, "--gates"))


def resolve_human_gate(spec, stages):
    s = spec.strip().lower()
    if s == "undecided":
        return "undecided"
    if s == "none":
        return "[]"
    return "[" + ", ".join(match_stages(spec.split(","), stages, "--human-gate")) + "]"


def process_yaml(rb_id, owner, status, source, human_gate, stages, bounce_cap):
    lines = [
        f"id: {rb_id}",
        f"owner: {yaml_scalar(owner)}",
        "version: 0.1.0",
        f"status: {status}",
        "# Stage ids that wait for a human yes before they start. [] means decided: none.",
        "# 'undecided' means nobody has decided yet. Lint keeps flagging it.",
        f"human_gate: {human_gate}",
        f"source: {json.dumps(source)}",
        "runs_on: []       # harnesses this has passed its gates on",
        "requires: []      # tools, logins and connections a run needs",
        "depends_on: []    # skills/<id> or runbooks/<id> this process uses",
        f"bounce_cap: {bounce_cap}",
        "stages:",
    ]
    for s in stages:
        lines += [
            f"  - id: {s['id']}",
            f"    needs: [{', '.join(s['needs'])}]",
            f"    gate: {'true' if s['gate'] else 'false'}",
        ]
    return "\n".join(lines) + "\n"


def stage_table(stages):
    rows = ["| Stage | Does | Needs | Gate |", "|---|---|---|---|"]
    for s in stages:
        needs = ", ".join(f"`{n}`" for n in s["needs"]) or "none"
        rows.append(f"| `{s['id']}` | TODO | {needs} | {'yes' if s['gate'] else 'no'} |")
    return "\n".join(rows)


def inputs_rows(stage):
    if not stage["needs"]:
        return "| TODO: the request or source data | TODO | TODO |"
    return "\n".join(f"| `{n}` | `<run folder>/{n}/output/` | TODO |" for n in stage["needs"])


def check_roots(registry, qa):
    if not (registry / "AGENTS.md").is_file() or not (registry / "runbooks").is_dir():
        die(f"{registry} is not a registry (no AGENTS.md or runbooks/). Run init first.")
    if not (qa / "AGENTS.md").is_file():
        die(f"{qa} is not a QA registry (no AGENTS.md). Run init first.")


def add_route_row(registry, rb_id, when, created):
    route = registry / "ROUTE.md"
    if not route.is_file():
        print("  note    ROUTE.md is missing; add the route row by hand")
        return
    text = route.read_text()
    if f"runbooks/{rb_id}`" in text:
        return
    cell = " ".join(when.split()).replace("|", "/")
    if not text.endswith("\n"):
        text += "\n"
    route.write_text(text + f"| {cell} | `runbooks/{rb_id}` |\n")
    print(f"  update  {route}")


def make_gate(registry, qa, rb_id, stage_id, created):
    parts = templates_dir() / "parts"
    gid = gate_id_for(stage_id)
    values = {"id": rb_id, "stage_id": stage_id, "gate_id": gid, "qa_name": qa.name}
    write(registry / "runbooks" / rb_id / gid / "GATE.md",
          render((parts / "GATE.md.tmpl").read_text(), values), created)
    qdir = qa / "runbooks" / rb_id / gid
    write(qdir / "qa.md", render((parts / "qa.md.tmpl").read_text(), values), created)
    write(qdir / "golden" / ".gitkeep", "", created)


def build_runbook(args, stages, status, source, adopted):
    registry, qa = Path(args.registry).resolve(), Path(args.qa).resolve()
    check_roots(registry, qa)
    rb_id = args.id
    if not ID_RE.match(rb_id) or len(rb_id) > 64:
        die("--id must be lowercase letters, digits and hyphens, 64 characters at most")
    rb = registry / "runbooks" / rb_id
    if rb.exists():
        die(f"{rb} already exists. Edit it, or use the gate command to add a gate.")
    description = " ".join(args.description.split())
    if len(description) > 1024:
        die("--description is over 1024 characters")
    parts = templates_dir() / "parts"
    created = []
    human_gate = resolve_human_gate(args.human_gate, stages)
    title = one_line(args.title) if args.title else rb_id.replace("-", " ").capitalize()

    write(rb / "SKILL.md", render((parts / "entry.md.tmpl").read_text(), {
        "id": rb_id, "description_yaml": json.dumps(description), "title": title,
        "stage_table": stage_table(stages),
    }), created)
    write(rb / "process.yaml",
          process_yaml(rb_id, one_line(args.owner), status, one_line(source), human_gate, stages,
                       args.bounce_cap), created)

    stage_tmpl = "STAGE-adopted.md.tmpl" if adopted else "STAGE.md.tmpl"
    for s in stages:
        values = {"id": rb_id, "stage_id": s["id"], "inputs_rows": inputs_rows(s)}
        write(rb / s["id"] / "STAGE.md", render((parts / stage_tmpl).read_text(), values), created)
        write(rb / s["id"] / "deliverable.md",
              render((parts / "deliverable.md.tmpl").read_text(), values), created)
        if s["gate"]:
            make_gate(registry, qa, rb_id, s["id"], created)
    add_route_row(registry, rb_id, args.when or description, created)

    print(f"\n{rb_id}: {len(stages)} stage(s), {sum(s['gate'] for s in stages)} gate(s), status {status}.")
    print("Next: replace every TODO, then run lint.py with --qa.")


def cmd_init(args):
    tdir = templates_dir()
    if not (tdir / "registry").is_dir():
        die("init needs the full template set. Run it from the process-registry skill, "
            "not from a repo's tools/ folder.")
    registry, qa = Path(args.registry).resolve(), Path(args.qa).resolve()
    if registry == qa or registry in qa.parents or qa in registry.parents:
        die("the registry and the QA registry must be separate folders, neither inside the other")
    values = {
        "registry_name": registry.name, "qa_name": qa.name,
        "runs_root": one_line(args.runs_root), "record": one_line(args.record),
        "owner": yaml_scalar(one_line(args.owner)),
    }
    created = []
    print(f"registry: {registry}")
    copy_tree(tdir / "registry", registry, values, created)
    copy_tree(tdir / "zero" / "registry", registry, values, created)
    for name in TOOLS:
        src = HERE / name
        if src.is_file():
            dst = registry / "tools" / name
            if dst.exists():
                print(f"  keep    {dst}")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                created.append(dst)
                print(f"  create  {dst}")
    # Only the blank forms go into the repo, unrendered, so tools/scaffold.py can
    # reuse them. Process-zero criteria stay out of the main registry.
    for src in sorted((tdir / "parts").glob("*.tmpl")):
        dst = registry / "tools" / "templates" / "parts" / src.name
        if dst.exists():
            print(f"  keep    {dst}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        created.append(dst)
        print(f"  create  {dst}")
    print(f"qa registry: {qa}")
    copy_tree(tdir / "qa", qa, values, created)
    copy_tree(tdir / "zero" / "qa", qa, values, created)
    print(f"\nCreated {len(created)} file(s).")
    print("Next:")
    print("  1. git init each folder and push them to two separate repos.")
    print(f"  2. Give read access to {qa.name} only to the QA agent's own user or machine, plus the steward.")
    print("  3. Decide human_gate in runbooks/registry-steward/process.yaml.")
    print(f"  4. python {registry.name}/tools/lint.py {registry} --qa {qa}")


def cmd_runbook(args):
    stages = parse_stages(args.stages)
    gated = resolve_gates(args.gates, stages)
    for s in stages:
        s["gate"] = s["id"] in gated
    build_runbook(args, stages, "draft", "", adopted=False)


def cmd_adopt(args):
    stages = parse_stages(args.stages)
    gated = resolve_gates(args.gates, stages)
    for s in stages:
        s["gate"] = s["id"] in gated
    build_runbook(args, stages, "adopted", args.source, adopted=True)


def cmd_gate(args):
    registry, qa = Path(args.registry).resolve(), Path(args.qa).resolve()
    check_roots(registry, qa)
    rb = registry / "runbooks" / args.id
    proc = rb / "process.yaml"
    if not proc.is_file():
        die(f"{proc} not found")
    stage_id = args.stage
    if not STAGE_RE.match(stage_id) or not (rb / stage_id).is_dir():
        die(f"stage {stage_id!r} not found in {rb}")
    text = proc.read_text()
    block = re.search(
        r"^\s*- id: %s[ \t]*\n((?:(?!\s*- id:).*\n?)*)" % re.escape(stage_id), text, re.M)
    hint = ("Write the stage as three lines ('- id:', 'needs:', 'gate:'), the way the scaffolder does, "
            "or set gate: true by hand and add the folders yourself. Nothing was changed.")
    if not block:
        die(f"cannot find a '- id: {stage_id}' line in process.yaml. {hint}")
    m = re.search(r"^(\s*gate:\s*)(true|false)\b", block.group(1), re.M)
    if not m:
        die(f"stage {stage_id} has no 'gate:' line of its own in process.yaml. {hint}")
    created = []
    if m.group(2) == "false":
        start = block.start(1) + m.start(2)
        text = text[:start] + "true" + text[start + len("false"):]
        proc.write_text(text)
        print(f"  update  {proc}")
    make_gate(registry, qa, args.id, stage_id, created)
    print(f"\nGate {gate_id_for(stage_id)} is in place for {stage_id}. "
          "Fill qa.md in the QA registry, and bump version in process.yaml.")


def add_runbook_args(p, default_stages=None):
    p.add_argument("--registry", required=True, help="path to the main registry")
    p.add_argument("--qa", required=True, help="path to the QA registry")
    p.add_argument("--id", required=True, help="runbook id, lowercase-with-hyphens")
    p.add_argument("--description", required=True,
                   help="what the process does and when to use it (routing depends on this)")
    p.add_argument("--title", help="heading for the runbook; defaults to the id")
    p.add_argument("--when", help="'Use when' text for ROUTE.md; defaults to the description")
    p.add_argument("--owner", default="registry-steward", help="who answers for this process")
    p.add_argument("--stages", required=default_stages is None, default=default_stages,
                   help="comma = next step, pipe = side by side. "
                        "Example: 'collect, build-table | draft-email, send'")
    p.add_argument("--human-gate", default="undecided",
                   help="'undecided' (default), 'none', or stages that wait for a human yes")
    p.add_argument("--bounce-cap", type=int, default=3, help="fix rounds before escalation")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="create the registry and the QA registry")
    p.add_argument("--registry", required=True)
    p.add_argument("--qa", required=True)
    p.add_argument("--runs-root", default="../runs",
                   help="where run folders live, as written into AGENTS.md")
    p.add_argument("--record", default="the team task board",
                   help="where receipts go, as written into AGENTS.md")
    p.add_argument("--owner", default="registry-steward", help="owner of process zero")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("runbook", help="add a new runbook")
    add_runbook_args(p)
    p.add_argument("--gates", default="all", help="'all' (default), 'last', 'none', or a list of stages")
    p.set_defaults(func=cmd_runbook)

    p = sub.add_parser("adopt", help="wrap an existing process, as-is")
    add_runbook_args(p, default_stages="run")
    p.add_argument("--source", required=True, help="where the process lives today")
    p.add_argument("--gates", default="none", help="'none' (default), 'all', 'last', or a list of stages")
    p.set_defaults(func=cmd_adopt)

    p = sub.add_parser("gate", help="add a QA gate to an existing stage")
    p.add_argument("--registry", required=True)
    p.add_argument("--qa", required=True)
    p.add_argument("--id", required=True, help="runbook id")
    p.add_argument("--stage", required=True, help="full stage id, for example 02a-build-table")
    p.set_defaults(func=cmd_gate)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
