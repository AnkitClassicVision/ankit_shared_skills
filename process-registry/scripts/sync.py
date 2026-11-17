#!/usr/bin/env python3
"""Put the registry's runbooks and shared skills in front of a harness.

  python sync.py <registry> --target ~/.claude/skills --target ~/.hermes/skills
                 [--mode symlink|copy] [--include-draft] [--force] [--dry-run]

Each runbook folder holds exactly one SKILL.md, so a harness that reads the open
Agent Skills format sees one skill per runbook. Retired runbooks are never synced.
Drafts are skipped unless --include-draft is set. Only the main registry is
synced. The QA registry is never synced to a maker's harness.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path


def status_of(rb):
    proc = rb / "process.yaml"
    if not proc.is_file():
        return None
    m = re.search(r"^status:\s*([a-z]+)", proc.read_text(), re.M)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("registry")
    ap.add_argument("--target", action="append", required=True, help="a harness skills folder; repeatable")
    ap.add_argument("--mode", choices=("symlink", "copy"), default="symlink")
    ap.add_argument("--include-draft", action="store_true")
    ap.add_argument("--force", action="store_true", help="replace entries that already exist")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    registry = Path(args.registry).expanduser().resolve()
    if not (registry / "runbooks").is_dir():
        sys.exit(f"error: {registry} has no runbooks/ folder")

    sources = []
    for rb in sorted(p for p in (registry / "runbooks").iterdir() if p.is_dir()):
        st = status_of(rb)
        if st == "retired" or (st == "draft" and not args.include_draft):
            print(f"skip    {rb.name} ({st})")
            continue
        if (rb / "SKILL.md").is_file():
            sources.append(rb)
    skills = registry / "skills"
    if skills.is_dir():
        sources += [p for p in sorted(skills.iterdir()) if (p / "SKILL.md").is_file()]

    for target in args.target:
        tdir = Path(target).expanduser()
        print(f"\n{tdir}")
        if not args.dry_run:
            tdir.mkdir(parents=True, exist_ok=True)
        for src in sources:
            dst = tdir / src.name
            if dst.is_symlink() and dst.resolve() == src:
                print(f"  ok      {src.name}")
                continue
            if dst.exists() or dst.is_symlink():
                if not args.force:
                    print(f"  keep    {src.name} (already there; use --force to replace)")
                    continue
                if not args.dry_run:
                    if dst.is_symlink() or dst.is_file():
                        dst.unlink()
                    else:
                        shutil.rmtree(dst)
            print(f"  {'link' if args.mode == 'symlink' else 'copy'}    {src.name}")
            if args.dry_run:
                continue
            if args.mode == "symlink":
                dst.symlink_to(src, target_is_directory=True)
            else:
                shutil.copytree(src, dst)


if __name__ == "__main__":
    main()
