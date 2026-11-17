#!/usr/bin/env python3
"""Self-test and red team for the process-registry tools.

  python selftest.py [--scripts <dir>] [--verbose]

Builds throwaway registries in a temp folder, attacks them, and reports whether
the tools held. Every case is either a promise ("same inputs give the same
files") or an attack ("criteria copied into the main registry") that lint must
catch. Exit code 1 if any case fails.

--scripts points at another copy of the tools, to test an installed version.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
SECRET = "Row count is within 1% of the source system total after the listed drops."
DESC = "Builds the demo report. Use when the demo report is due."
RESULTS = []
VERBOSE = False


def tool(name):
    return str(SCRIPTS / name)


def sh(*args):
    r = subprocess.run([PY, *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def record(group, name, ok, detail=""):
    RESULTS.append((group, name, bool(ok), detail))
    if VERBOSE or not ok:
        print(f"  {'pass' if ok else 'FAIL'}  [{group}] {name}" + (f"\n        {detail.strip()[:400]}" if detail and not ok else ""))


def tree_hash(root):
    h = hashlib.sha256()
    for p in sorted(Path(root).rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(root)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def fill(path):
    for p in Path(path).rglob("*"):
        if p.is_file() and p.suffix in (".md", ".yaml") and "tools" not in p.parts:
            t = p.read_text()
            if "TODO" in t:
                p.write_text(t.replace("TODO", "Filled in"))


def build(root, rid="demo-report", stages="collect, build-table | draft-note, assemble, send",
          gates="collect, assemble", human="send", filled=True):
    reg, qa = Path(root) / "registry", Path(root) / "registry-qa"
    code, out = sh(tool("scaffold.py"), "init", "--registry", reg, "--qa", qa)
    assert code == 0, out
    code, out = sh(tool("scaffold.py"), "runbook", "--registry", reg, "--qa", qa, "--id", rid,
                   "--description", DESC, "--stages", stages, "--gates", gates, "--human-gate", human)
    assert code == 0, out
    if filled:
        fill(reg / "runbooks" / rid)
        fill(qa / "runbooks" / rid)
        q = qa / "runbooks" / rid / "01.1-qa" / "qa.md"
        if q.is_file():
            q.write_text(q.read_text() + f"\n- {SECRET}\n")
    return reg, qa


def lint(reg, qa=None, *extra):
    args = [tool("lint.py"), reg]
    if qa:
        args += ["--qa", qa]
    return sh(*args, *extra)


def clone(base):
    dst = Path(tempfile.mkdtemp(dir=WORK))
    shutil.copytree(base, dst / "w", symlinks=True)
    return dst / "w" / "registry", dst / "w" / "registry-qa"


def attack(group, name, base, mutate, needle, use_qa=True):
    """Mutate a clean copy, lint it, and require an ERROR that mentions the needle."""
    reg, qa = clone(base)
    mutate(reg, qa)
    code, out = lint(reg, qa if use_qa else None)
    hit = any(line.startswith("ERROR") and re.search(needle, line, re.I) for line in out.splitlines())
    record(group, name, code == 1 and hit, out)


def edit(path, old, new, count=1):
    t = Path(path).read_text()
    assert old in t, f"{old!r} not in {path}"
    Path(path).write_text(t.replace(old, new, count))


def make_verified(reg, qa, rid="demo-report"):
    proc = reg / "runbooks" / rid / "process.yaml"
    edit(proc, "status: draft", "status: verified")
    edit(proc, "runs_on: []", "runs_on: [harness-a]")
    for g in ("01.1-qa", "03.1-qa"):
        gd = qa / "runbooks" / rid / g / "golden"
        (gd / "good-basic").mkdir(parents=True, exist_ok=True)
        (gd / "good-basic" / "out.txt").write_text(f"good example for {g}\n")
        (gd / "bad-missing-day").mkdir(parents=True, exist_ok=True)
        (gd / "bad-missing-day" / "out.txt").write_text(f"bad example for {g}\n")


def main():
    global SCRIPTS, WORK, VERBOSE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scripts", default=str(HERE))
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    SCRIPTS, VERBOSE = Path(args.scripts).resolve(), args.verbose
    WORK = Path(tempfile.mkdtemp(prefix="pr-selftest-"))
    RB = "runbooks/demo-report"

    try:
        base = WORK / "base"
        reg, qa = build(base)
        code, out = lint(reg, qa)
        record("baseline", "a filled draft lints with no errors", code == 0 and "0 error(s)" in out, out)

        # ---------- A. consistency ----------
        g = "consistency"
        r2, q2 = build(WORK / "again")
        record(g, "same inputs give byte-identical files",
               tree_hash(reg) == tree_hash(r2) and tree_hash(qa) == tree_hash(q2))
        shapes = ["one", "a, b", "a | b | c", "a, b | c, d", "pull data, check | enrich | score, pack, ship it"]
        ok, detail = True, ""
        for i, spec in enumerate(shapes):
            rr, qq = build(WORK / f"shape{i}", rid=f"shape-{i}", stages=spec, gates="all", human="none")
            c, o = lint(rr, qq)
            if c != 0:
                ok, detail = False, f"{spec!r}: {o}"
        record(g, "five different stage shapes all produce a valid structure", ok, detail)
        rr, qq = clone(base)
        marker = rr / RB / "01-collect" / "STAGE.md"
        marker.write_text("EDITED BY A PERSON\n")
        sh(tool("scaffold.py"), "init", "--registry", rr, "--qa", qq)
        sh(tool("scaffold.py"), "gate", "--registry", rr, "--qa", qq, "--id", "demo-report", "--stage", "01-collect")
        record(g, "re-running the tools never overwrites edited files", marker.read_text() == "EDITED BY A PERSON\n")
        if (SCRIPTS / "compare.py").is_file():
            ra, _ = build(WORK / "cmpa", rid="cmp", stages="collect, build | draft, send", gates="collect", human="send")
            rb_, _ = build(WORK / "cmpb", rid="cmp", stages="pull, table | note, deliver", gates="pull", human="deliver")
            rc, _ = build(WORK / "cmpc", rid="cmp", stages="collect, build | draft, send", gates="send", human="none")
            c1, o1 = sh(tool("compare.py"), ra, rb_, "--id", "cmp")
            c2, o2 = sh(tool("compare.py"), ra, rc, "--id", "cmp")
            record(g, "compare: same shape with different names counts as a shape match", c1 == 0 and "shape: match" in o1, o1)
            record(g, "compare: different gate placement is reported as a mismatch", c2 == 1 and "DIFFER" in o2, o2)
        else:
            record(g, "compare.py is present", False, "compare.py not found")

        # ---------- B. hostile or sloppy inputs ----------
        g = "inputs"
        rr, qq = clone(base)

        def scaf(*a):
            return sh(tool("scaffold.py"), "runbook", "--registry", rr, "--qa", qq, *a)
        before = tree_hash(rr.parent)
        c, o = scaf("--id", "../../escape", "--description", DESC, "--stages", "a")
        record(g, "path traversal in --id is rejected", c != 0 and tree_hash(rr.parent) == before, o)
        c, o = scaf("--id", "Bad Id", "--description", DESC, "--stages", "a")
        record(g, "ids with spaces or capitals are rejected", c != 0, o)
        c, o = scaf("--id", "demo-report", "--description", DESC, "--stages", "a")
        record(g, "a duplicate runbook id is rejected and nothing changes", c != 0 and tree_hash(rr.parent) == before, o)
        c, o = scaf("--id", "slug-test", "--description", DESC, "--stages", "../../etc/passwd, a/b\\c")
        made = sorted(p.name for p in (rr / "runbooks" / "slug-test").iterdir() if p.is_dir()) if c == 0 else []
        record(g, "path characters in stage names cannot escape the runbook folder",
               c == 0 and made == ["01-etc-passwd", "01.1-qa", "02-a-b-c", "02.1-qa"]
               and not (WORK / "etc").exists(), f"{made} {o}")
        tricky = 'Has {{stage_table}} and {{id}}: "quotes" --- and a | pipe.\nSecond line. Use when testing.'
        c, o = scaf("--id", "inject-test", "--description", tricky, "--stages", "a")
        ok = False
        if c == 0:
            import yaml
            t = (rr / "runbooks" / "inject-test" / "SKILL.md").read_text()
            fm = yaml.safe_load(re.match(r"^---\n(.*?)\n---", t, re.S).group(1))
            ok = fm["description"] == " ".join(tricky.split())
        record(g, "template tokens, quotes, colons and newlines in a description stay literal", ok, o)
        if c == 0:
            row = [ln for ln in (rr / "ROUTE.md").read_text().splitlines() if "inject-test" in ln]
            record(g, "a pipe in a description cannot break the route table", len(row) == 1 and row[0].count("|") == 3, str(row))
        c, o = scaf("--id", "owner-test", "--description", DESC, "--stages", "a", "--owner", "ops: lead # x")
        ok = False
        if c == 0:
            import yaml
            ok = yaml.safe_load((rr / "runbooks" / "owner-test" / "process.yaml").read_text())["owner"] == "ops: lead # x"
        record(g, "special characters in --owner survive as data", ok, o)
        c, o = sh(tool("scaffold.py"), "init", "--registry", WORK / "same", "--qa", WORK / "same" / "qa")
        record(g, "a QA registry inside the main registry is rejected", c != 0, o)
        c, o = scaf("--id", "too-wide", "--description", DESC, "--stages", " | ".join(f"s{i}" for i in range(27)))
        record(g, "more than 26 side-by-side stages is rejected", c != 0, o)

        # ---------- C. blind QA leaks ----------
        g = "leaks"
        attack(g, "qa.md dropped into a stage folder", base,
               lambda r, q: (r / RB / "01-collect" / "qa.md").write_text("x\n"), "criteria found")
        attack(g, "a golden folder in the main registry", base,
               lambda r, q: (r / RB / "03-assemble" / "golden").mkdir(), "golden")
        attack(g, "an extra file in a gate folder", base,
               lambda r, q: (r / RB / "01.1-qa" / "notes.md").write_text("x\n"), "only GATE.md")
        attack(g, "criteria hidden under tools/", base,
               lambda r, q: (r / "tools" / "qa.md").write_text("x\n"), "criteria found")

        def leak_into(rel):
            def m(r, q):
                p = r / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text((p.read_text() if p.exists() else "") + f"\nNote: {SECRET}\n")
            return m
        attack(g, "a criteria line pasted into deliverable.md", base, leak_into(f"{RB}/01-collect/deliverable.md"), "same text")
        attack(g, "a criteria line pasted into GATE.md", base, leak_into(f"{RB}/01.1-qa/GATE.md"), "same text")
        attack(g, "a criteria line saved under another filename", base, leak_into(f"{RB}/01-collect/references/checks.md"), "same text")
        attack(g, "a criteria line pasted into AGENTS.md", base, leak_into("AGENTS.md"), "same text")

        def golden_copy(r, q):
            gd = q / RB / "01.1-qa" / "golden" / "good-basic"
            gd.mkdir(parents=True)
            (gd / "out.csv").write_text("a,b\n1,2\n")
            (r / RB / "01-collect" / "references").mkdir(parents=True, exist_ok=True)
            (r / RB / "01-collect" / "references" / "sample.csv").write_text("a,b\n1,2\n")
        attack(g, "a golden file copied into the main registry under another name", base, golden_copy, "golden")

        def symlink(r, q):
            os.symlink(q / RB / "01.1-qa", r / RB / "01-collect" / "hints")
        attack(g, "a symlink from the main registry into the QA registry", base, symlink, "symlink")

        # ---------- D. order and structure ----------
        g = "structure"
        P = f"{RB}/process.yaml"
        attack(g, "side-by-side stages that depend on each other", base,
               lambda r, q: edit(r / P, "  - id: 02b-draft-note\n    needs: [01-collect]", "  - id: 02b-draft-note\n    needs: [02a-build-table]"),
               "lower number")
        attack(g, "a stage that needs a later stage", base,
               lambda r, q: edit(r / P, "  - id: 01-collect\n    needs: []", "  - id: 01-collect\n    needs: [03-assemble]"), "lower number")
        attack(g, "gate: true with no gate folder", base,
               lambda r, q: shutil.rmtree(r / RB / "03.1-qa"), "no '03.1-qa' folder")
        attack(g, "a gate folder while gate is false", base,
               lambda r, q: edit(r / P, "  - id: 03-assemble\n    needs: [02a-build-table, 02b-draft-note]\n    gate: true",
                                 "  - id: 03-assemble\n    needs: [02a-build-table, 02b-draft-note]\n    gate: false"), "gate: false")
        attack(g, "a stage folder that process.yaml does not list", base,
               lambda r, q: (r / RB / "05-extra").mkdir(), "not listed")
        attack(g, "a SKILL.md inside a stage", base,
               lambda r, q: (r / RB / "01-collect" / "SKILL.md").write_text("x\n"), "must not contain SKILL.md")
        attack(g, "a description added to process.yaml", base,
               lambda r, q: edit(r / P, "version: 0.1.0", "version: 0.1.0\ndescription: drift"), "description")
        attack(g, "SKILL.md name that does not match the folder", base,
               lambda r, q: edit(r / RB / "SKILL.md", "name: demo-report", "name: something-else"), "must match")
        attack(g, "gate written as a string instead of true/false", base,
               lambda r, q: edit(r / P, "gate: true", 'gate: "true"'), "gate: true' or 'gate: false")
        attack(g, "a key written twice in process.yaml", base,
               lambda r, q: edit(r / P, "human_gate: [04-send]", "human_gate: undecided\nhuman_gate: []"), "duplicate|twice")

        # ---------- E. lowering the bar ----------
        g = "bar"
        vbase = WORK / "vbase"
        shutil.copytree(base, vbase)
        vreg, vqa = vbase / "registry", vbase / "registry-qa"
        make_verified(vreg, vqa)
        code, out = lint(vreg, vqa)
        record(g, "a properly earned 'verified' passes", code == 0, out)
        attack(g, "'verified' with no harness named", vbase,
               lambda r, q: edit(r / P, "runs_on: [harness-a]", "runs_on: []"), "runs_on is empty")
        attack(g, "'portable' with only one harness", vbase,
               lambda r, q: edit(r / P, "status: verified", "status: portable"), "fewer than two")
        attack(g, "'verified' with unfinished criteria", vbase,
               lambda r, q: (q / RB / "03.1-qa" / "qa.md").write_text("TODO\n"), "TODO")
        attack(g, "'verified' with criteria missing", vbase,
               lambda r, q: (q / RB / "03.1-qa" / "qa.md").unlink(), "qa.md is missing")
        attack(g, "'verified' while human_gate is undecided", vbase,
               lambda r, q: edit(r / P, "human_gate: [04-send]", "human_gate: undecided"), "undecided")
        attack(g, "'verified' with no known-bad example to prove the gate can fail", vbase,
               lambda r, q: shutil.rmtree(q / RB / "01.1-qa" / "golden" / "bad-missing-day"), "known-bad|bad-")

        def guard(name, mutate, needle):
            reg2, qa2 = clone(vbase)
            mutate(reg2, qa2)
            c, o = sh(tool("lint.py"), reg2, "--qa", qa2, "--against", vreg, "--against-qa", vqa)
            hit = any(line.startswith("review") and re.search(needle, line, re.I) for line in o.splitlines())
            record("guard", name, hit, o)

        def drop_gate(r, q):
            shutil.rmtree(r / RB / "03.1-qa")
            edit(r / P, "  - id: 03-assemble\n    needs: [02a-build-table, 02b-draft-note]\n    gate: true",
                 "  - id: 03-assemble\n    needs: [02a-build-table, 02b-draft-note]\n    gate: false")
        guard("a quietly removed gate is flagged for a human", drop_gate, "gate removed")
        guard("a changed human_gate is flagged for a human",
              lambda r, q: edit(r / P, "human_gate: [04-send]", "human_gate: []"), "human_gate changed")
        guard("a status promotion is flagged for a human",
              lambda r, q: (edit(r / P, "status: verified", "status: portable"),
                            edit(r / P, "runs_on: [harness-a]", "runs_on: [harness-a, harness-b]")), "status")
        guard("a raised bounce cap is flagged for a human",
              lambda r, q: edit(r / P, "bounce_cap: 3", "bounce_cap: 9"), "bounce_cap")
        guard("changed instructions with no version bump are flagged",
              lambda r, q: (r / RB / "01-collect" / "deliverable.md").write_text("easier now\n"), "version")
        guard("a stage and its criteria changed together are flagged",
              lambda r, q: ((r / RB / "01-collect" / "deliverable.md").write_text("easier now\n"),
                            (q / RB / "01.1-qa" / "qa.md").write_text("always pass\n")), "together")
        guard("a deleted runbook folder is flagged",
              lambda r, q: shutil.rmtree(r / RB), "removed")
        reg2, qa2 = clone(vbase)
        c, o = sh(tool("lint.py"), reg2, "--qa", qa2, "--against", vreg, "--against-qa", vqa)
        record("guard", "an unchanged registry raises no review flags",
               c == 0 and not any(l.startswith("review") for l in o.splitlines()), o)

        # ---------- F. tool safety ----------
        g = "tools"
        rr, qq = clone(vbase)
        edit(rr / "runbooks" / "registry-steward" / "process.yaml", "status: draft", "status: retired")
        target = WORK / "harness" / "skills"
        c, o = sh(tool("sync.py"), rr, "--target", target)
        names = sorted(p.name for p in target.iterdir()) if target.exists() else []
        record(g, "sync skips retired runbooks", "registry-steward" not in names and "demo-report" in names, o)
        rr2, _ = clone(base)
        target2 = WORK / "harness2" / "skills"
        sh(tool("sync.py"), rr2, "--target", target2)
        names2 = sorted(p.name for p in target2.iterdir()) if target2.exists() else []
        record(g, "sync skips drafts unless asked", names2 == [], str(names2))
        (target / "demo-report").unlink()
        (target / "demo-report").mkdir()
        (target / "demo-report" / "mine.txt").write_text("keep me\n")
        sh(tool("sync.py"), rr, "--target", target)
        record(g, "sync does not replace an existing folder without --force", (target / "demo-report" / "mine.txt").exists())
        rr, qq = clone(base)
        edit(rr / P, "  - id: 02b-draft-note\n    needs: [01-collect]\n    gate: false", "  - {id: 02b-draft-note, needs: [01-collect], gate: false}")
        before = tree_hash(rr.parent)
        c, o = sh(tool("scaffold.py"), "gate", "--registry", rr, "--qa", qq, "--id", "demo-report", "--stage", "02b-draft-note")
        record(g, "gate command refuses a layout it cannot edit safely, and changes nothing",
               c != 0 and tree_hash(rr.parent) == before, o)
        c, o = sh(tool("graph.py"), reg, "--stdout")
        record(g, "graph renders every stage", c == 0 and o.count("demo_report__0") >= 5, o)
    finally:
        shutil.rmtree(WORK, ignore_errors=True)

    groups = {}
    for grp, _, ok, _ in RESULTS:
        p, t = groups.get(grp, (0, 0))
        groups[grp] = (p + ok, t + 1)
    print("\nSelf-test")
    for grp, (p, t) in groups.items():
        print(f"  {grp:<12} {p}/{t}")
    passed = sum(ok for _, _, ok, _ in RESULTS)
    print(f"\n{passed}/{len(RESULTS)} passed")
    sys.exit(0 if passed == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
