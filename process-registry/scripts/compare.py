#!/usr/bin/env python3
"""Compare how several agents built the same runbook from the same brief.

  python compare.py <registry A> <registry B> [<registry C> ...] --id <runbook-id>

Each registry is one attempt: a different agent, harness or session given the
same request. This reports where the structure agrees and where it does not.

What must match for a consistent result: the shape (steps and how many stages
run side by side in each), where the gates sit, where a human yes is needed,
and what each step depends on. Stage names are labels; different names with the
same shape are reported but do not count as a mismatch.

Exit code 0 when every attempt is consistent with the first, otherwise 1.
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("compare needs PyYAML. Install it with: pip install pyyaml")

STAGE_RE = re.compile(r"^(\d{2})([a-z]?)-(.+)$")


def signature(registry, rid):
    proc = Path(registry) / "runbooks" / rid / "process.yaml"
    if not proc.is_file():
        sys.exit(f"error: {proc} not found")
    data = yaml.safe_load(proc.read_text()) or {}
    steps = {}
    for s in data.get("stages") or []:
        m = STAGE_RE.match(str(s.get("id", "")))
        if not m:
            sys.exit(f"error: bad stage id {s.get('id')!r} in {proc}")
        num = int(m.group(1))
        needs = sorted({int(STAGE_RE.match(str(n)).group(1)) for n in (s.get("needs") or []) if STAGE_RE.match(str(n))})
        steps.setdefault(num, []).append({"id": str(s["id"]), "name": m.group(3), "gate": s.get("gate") is True, "needs": needs})
    order = sorted(steps)
    index = {num: i + 1 for i, num in enumerate(order)}  # compare by position, not by the digits used
    hg = data.get("human_gate")
    if isinstance(hg, list):
        human = sorted({index[int(STAGE_RE.match(str(x)).group(1))] for x in hg if STAGE_RE.match(str(x))})
        human = ", ".join(map(str, human)) or "none"
    else:
        human = str(hg)
    return {
        "stages": str(sum(len(steps[n]) for n in order)),
        "shape": " | ".join(str(len(steps[n])) for n in order),
        "gates": " | ".join(str(sum(st["gate"] for st in steps[n])) for n in order),
        "human": human,
        "needs": " | ".join(
            "+".join(sorted({",".join(str(index[x]) for x in st["needs"]) or "-" for st in steps[n]})) for n in order),
        "names": "; ".join(", ".join(sorted(st["name"] for st in steps[n])) for n in order),
        "cap": str(data.get("bounce_cap")),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("registries", nargs="+", help="two or more registry folders")
    ap.add_argument("--id", required=True, help="the runbook id to compare")
    args = ap.parse_args()
    if len(args.registries) < 2:
        sys.exit("error: give at least two registries to compare")

    sigs = [signature(r, args.id) for r in args.registries]
    labels = [chr(ord("A") + i) for i in range(len(sigs))]
    rows = [
        ("stages", "stages", True), ("steps (stages side by side)", "shape", True),
        ("gates per step", "gates", True), ("human yes before step", "human", True),
        ("each step needs steps", "needs", True), ("bounce cap", "cap", True),
        ("stage names", "names", False),
    ]
    print(f"Runbook: {args.id}")
    for lab, reg in zip(labels, args.registries):
        print(f"  {lab} = {reg}")
    print()
    width = max(len(r[0]) for r in rows) + 2
    for title, key, _ in rows:
        print(f"{title:<{width}}" + "   ".join(f"{lab}: {sig[key]}" for lab, sig in zip(labels, sigs)))
    print()

    consistent = True
    checks = [("shape", ("stages", "shape")), ("gates", ("gates",)), ("human yes", ("human",)),
              ("dependencies", ("needs",)), ("bounce cap", ("cap",))]
    for title, keys in checks:
        same = all(all(sig[k] == sigs[0][k] for k in keys) for sig in sigs)
        consistent &= same
        print(f"{title}: {'match' if same else 'DIFFER'}")
    names_same = all(sig["names"] == sigs[0]["names"] for sig in sigs)
    print(f"names: {'match' if names_same else 'differ (labels only; not counted)'}")
    print(f"\nRESULT: {'consistent' if consistent else 'NOT consistent'}")
    sys.exit(0 if consistent else 1)


if __name__ == "__main__":
    main()
