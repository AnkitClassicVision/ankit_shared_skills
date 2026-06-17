#!/usr/bin/env python3
"""
Codebase Organizer — Universal Repo Analyzer v2.1.0

Usage:
    python organize.py [path]

Zero flags. All behavior auto-detected by repo size and state.
Produces structured analysis and context layers for /run-project integration.
Version 2.1.0 adds skill-format structure output (recommendatory only).
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEEP_ANALYSIS_LOC_THRESHOLD = 1000
CIRCULAR_DEP_IGNORE_PATTERNS = {"test", "tests", "spec", "__pycache__", ".git", "node_modules", "venv", ".venv"}
IGNORED_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".run-project", ".skill-pack", "dist", "build"}


class CodebaseOrganizer:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()
        self.module_map: dict[str, list[str]] = {}
        self.import_graph: dict[str, list[str]] = defaultdict(list)
        self.deep_scores: dict[str, dict[str, Any]] = {}
        self.orphans: list[str] = []
        self.circular: list[tuple[str, ...]] = []
        self.report: dict[str, Any] = {}
        self.total_loc = 0
        self.has_run_project = (self.repo_path / ".run-project").exists()

    # -----------------------------------------------------------------------
    # Step 1: Surface Scan
    # -----------------------------------------------------------------------
    def surface_scan(self) -> None:
        files = [f for f in self.repo_path.rglob("*") if f.is_file() and not self._is_ignored(f)]
        src_files = [f for f in files if not f.name.startswith(".")]

        exts: dict[str, int] = defaultdict(int)
        for f in src_files:
            exts[f.suffix] += 1
        dominant = max(exts, key=exts.get) if exts else ".txt"

        test_files = [f for f in src_files if self._is_test_file(f)]
        coverage_ratio = len(test_files) / max(len(src_files), 1)

        docs = [f for f in src_files if f.name.lower().startswith("readme") or f.suffix == ".md"]
        doc_fresh = self._doc_freshness(docs)

        # LOC count
        self.total_loc = sum(self._file_loc(f) for f in src_files)

        self.report["surface"] = {
            "total_files": len(src_files),
            "dominant_language": dominant,
            "test_ratio": round(coverage_ratio, 2),
            "doc_fresh_months": doc_fresh,
            "total_loc": self.total_loc,
            "deep_analysis_enabled": self.total_loc >= DEEP_ANALYSIS_LOC_THRESHOLD,
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.module_map = self._build_module_map(src_files)

    def _is_ignored(self, f: Path) -> bool:
        return any(p in IGNORED_DIRS for p in f.parts)

    def _is_test_file(self, f: Path) -> bool:
        parts = [p.lower() for p in f.parts]
        return any("test" in p or "spec" in p for p in parts) or f.name.lower().startswith("test_")

    def _doc_freshness(self, docs: list[Path]) -> float | None:
        if not docs:
            return None
        now = datetime.now(timezone.utc).timestamp()
        ages: list[float] = []
        for d in docs:
            try:
                mtime = d.stat().st_mtime
                ages.append((now - mtime) / (30 * 24 * 3600))
            except Exception:
                continue
        return round(min(ages), 1) if ages else None

    def _file_loc(self, f: Path) -> int:
        try:
            return len(f.read_text(encoding="utf-8", errors="ignore").splitlines())
        except Exception:
            return 0

    def _build_module_map(self, files: list[Path]) -> dict[str, list[str]]:
        modules: dict[str, list[str]] = defaultdict(list)
        for f in files:
            rel = f.relative_to(self.repo_path)
            module = rel.parts[0] if len(rel.parts) > 1 else "root"
            modules[module].append(str(rel))
        return dict(modules)

    # -----------------------------------------------------------------------
    # Step 2: Deep Analysis
    # -----------------------------------------------------------------------
    def deep_analysis(self) -> None:
        if self.total_loc < DEEP_ANALYSIS_LOC_THRESHOLD:
            self.report["deep"] = {"skipped": True, "reason": f"LOC {self.total_loc} < threshold {DEEP_ANALYSIS_LOC_THRESHOLD}"}
            return

        for module, files in self.module_map.items():
            self._score_module(module, files)
        self._build_dependency_graph()
        self._find_circular_dependencies()
        self._find_orphans()

    def _score_module(self, module: str, files: list[str]) -> None:
        loc = 0
        complexity = 0
        docstrings = 0
        type_hints = 0
        public_api_lines = 0

        for f in files:
            fp = self.repo_path / f
            try:
                text = fp.read_text(encoding="utf-8", errors="ignore")
                lines = text.splitlines()
                loc += len(lines)

                if fp.suffix == ".py":
                    tree = ast.parse(text)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                            complexity += 1
                            # Simple public API detection: top-level definitions
                            if isinstance(node, ast.ClassDef) or (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.col_offset == 0):
                                public_api_lines += node.end_lineno - node.lineno if node.end_lineno else 1
                            # Docstring detection
                            body = node.body
                            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                                docstrings += 1
                            # Type hint detection (very simple)
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                if node.returns or any(a.annotation for a in node.args.args):
                                    type_hints += 1
            except Exception:
                continue

        stability = self._git_stability(files)
        coupling = len(self.import_graph.get(module, []))
        clarity = (docstrings + type_hints) / max(complexity, 1)
        interface_surface = public_api_lines / max(loc, 1)
        depth = complexity / max(loc, 1)

        # Deep score: weighted sum normalized by coupling
        score = (
            stability * 0.25 +
            depth * 0.35 +
            interface_surface * 0.20 +
            clarity * 0.20
        ) / (coupling + 1)

        self.deep_scores[module] = {
            "loc": loc,
            "complexity": complexity,
            "public_api_lines": public_api_lines,
            "docstrings": docstrings,
            "type_hints": type_hints,
            "stability": round(stability, 2),
            "coupling": coupling,
            "clarity": round(clarity, 3),
            "interface_surface": round(interface_surface, 3),
            "depth": round(depth, 3),
            "deep_score": round(score, 2),
        }

    def _git_stability(self, files: list[str]) -> float:
        try:
            stdout = subprocess.check_output(
                ["git", "-C", str(self.repo_path), "log", "--since=6.months", "--oneline"] +
                [str(f) for f in files],
                text=True, stderr=subprocess.DEVNULL, timeout=10,
            )
            lines = stdout.strip().splitlines()
            return max(0.0, 5.0 - len(lines) / 5.0)
        except Exception:
            return 2.5

    def _build_dependency_graph(self) -> None:
        for module, files in self.module_map.items():
            for f in files:
                fp = self.repo_path / f
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                    if fp.suffix == ".py":
                        for match in re.finditer(r"^\s*import\s+(\S+)|^\s*from\s+(\S+)", text, re.M):
                            dep = match.group(1) or match.group(2)
                            dep_module = dep.split(".")[0]
                            if dep_module != module and dep_module in self.module_map:
                                self.import_graph[module].append(dep_module)
                    elif fp.suffix in (".js", ".ts", ".jsx", ".tsx"):
                        for match in re.finditer(r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]|require\(['\"]([^'\"]+)['\"]\)", text):
                            dep = match.group(1) or match.group(2)
                            if dep.startswith("."):
                                continue  # relative imports skipped for simplicity
                            dep_module = dep.split("/")[0]
                            if dep_module != module and dep_module in self.module_map:
                                self.import_graph[module].append(dep_module)
                    elif fp.suffix == ".go":
                        for match in re.finditer(r'import\s+\(?\s*["\']([^"\']+)["\']', text):
                            dep = match.group(1)
                            dep_module = dep.split("/")[-1]
                            if dep_module != module and dep_module in self.module_map:
                                self.import_graph[module].append(dep_module)
                except Exception:
                    continue
        self.import_graph = {k: list(set(v)) for k, v in self.import_graph.items()}

    def _find_circular_dependencies(self) -> None:
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            for dep in self.import_graph.get(node, []):
                if dep not in visited:
                    dfs(dep, path + [dep])
                elif dep in rec_stack:
                    cycle = path[path.index(dep):] + [dep]
                    self.circular.append(tuple(cycle))
            rec_stack.remove(node)

        for mod in self.import_graph:
            if mod not in visited:
                dfs(mod, [mod])
        self.circular = list(set(self.circular))

    def _find_orphans(self) -> None:
        all_imported: set[str] = set()
        for deps in self.import_graph.values():
            all_imported.update(deps)
        for mod in self.module_map:
            if mod not in all_imported and mod not in ("root",):
                if not any(mod.lower().startswith(x) for x in ("test", "docs", "scripts", "bin", "cmd")):
                    self.orphans.append(mod)

    # -----------------------------------------------------------------------
    # Step 3: Three-Layer Context
    # -----------------------------------------------------------------------
    def context_layer(self) -> None:
        structural = {
            "modules": self.module_map,
            "import_graph": dict(self.import_graph),
            "circular_dependencies": [list(c) for c in self.circular],
            "orphans": self.orphans,
            "dominant_language": self.report["surface"]["dominant_language"],
            "total_loc": self.report["surface"]["total_loc"],
        }

        semantic: dict[str, Any] = {}
        for module, score in self.deep_scores.items():
            semantic[module] = {
                "complexity": score["complexity"],
                "public_api_lines": score["public_api_lines"],
                "interface_surface": score["interface_surface"],
                "depth": score["depth"],
                "clarity": score["clarity"],
                "contracts": "inferred from tests/types" if score["type_hints"] > 0 else "no type hints detected",
            }

        top_deep = sorted(
            self.deep_scores,
            key=lambda m: self.deep_scores[m]["deep_score"],
            reverse=True,
        )[:5]

        hotspots = [m for m, s in self.deep_scores.items() if s["coupling"] > 5]

        philosophical = {
            "top_deep_modules": top_deep,
            "hotspots": hotspots,
            "recommendations": self._generate_recommendations(),
            "deep_module_count": len([m for m, s in self.deep_scores.items() if s["deep_score"] > 1.0]),
            "shallow_module_count": len([m for m, s in self.deep_scores.items() if s["deep_score"] <= 0.5]),
        }

        self.report["context"] = {
            "structural": structural,
            "semantic": semantic,
            "philosophical": philosophical,
        }

    def _generate_recommendations(self) -> list[str]:
        recs: list[str] = []
        if self.circular:
            recs.append(f"Break circular dependencies: {self.circular[0]}")
        if self.orphans:
            recs.append(f"Review orphaned modules: {', '.join(self.orphans[:3])}")
        shallow = [m for m, s in self.deep_scores.items() if s["deep_score"] <= 0.5]
        if shallow:
            recs.append(f"Investigate shallow modules (score <= 0.5): {', '.join(shallow[:3])}")
        if not recs:
            recs.append("Structure looks healthy. Continue deepening high-score modules.")
        return recs

    # -----------------------------------------------------------------------
    # Step 4: SEEIT Injection Data
    # -----------------------------------------------------------------------
    def spec_diagram_output(self) -> dict[str, Any]:
        return {
            "modules": [
                {
                    "name": m,
                    "deep_score": self.deep_scores.get(m, {}).get("deep_score", 0),
                    "tier": "deep" if self.deep_scores.get(m, {}).get("deep_score", 0) > 1.0 else "mid" if self.deep_scores.get(m, {}).get("deep_score", 0) > 0.5 else "shallow",
                    "loc": self.deep_scores.get(m, {}).get("loc", 0),
                }
                for m in self.module_map
            ],
            "interfaces": {
                m: {
                    "file_count": len(fs),
                    "public_api_lines": self.deep_scores.get(m, {}).get("public_api_lines", 0),
                }
                for m, fs in self.module_map.items()
            },
            "data_flow": [
                {"from": k, "to": v}
                for k, deps in self.import_graph.items()
                for v in deps
            ],
            "state_surface": {
                m: self.deep_scores.get(m, {}).get("loc", 0)
                for m in self.module_map
            },
            "hotspots": self.report["context"]["philosophical"]["hotspots"] if "context" in self.report else [],
        }

    # -----------------------------------------------------------------------
    # Step 6: Skill-Format Structure (candidate skill layout)
    # -----------------------------------------------------------------------
    def skill_format_structure(self) -> dict[str, Any]:
        """Map the analyzed repo into a proposed skill directory layout.
        This is recommendatory — NOT an auto-creation signal."""
        deep_modules = sorted(
            self.deep_scores,
            key=lambda m: self.deep_scores[m]["deep_score"],
            reverse=True,
        )[:5]

        reusable_blocks: list[dict[str, str]] = []
        for mod in deep_modules:
            # Suggest top public functions/classes from deep modules as reusable
            info = self.deep_scores.get(mod, {})
            if info.get("public_api_lines", 0) > 0:
                reusable_blocks.append(
                    {
                        "module": mod,
                        "suggested_use": "scoring method / core logic",
                        "reason": f"deep_score={info['deep_score']}, stability={info['stability']}",
                    }
                )

        return {
            "skill_name": self.repo_path.name or "unnamed-repo",
            "repo_path": str(self.repo_path),
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "SKILL.md_suggested_sections": [
                "system overview",
                "core methods",
                "configuration",
                "testing strategy",
            ],
            "references/": {
                "purpose": "Documentation, design decisions, external API references",
                "candidates": [
                    f for f in self.module_map.get("docs", [])
                    + self.module_map.get("doc", [])
                    + [str(p) for p in self.repo_path.glob("README*")]
                    + [str(p) for p in self.repo_path.glob("*.md")]
                    if Path(f).exists()
                ][:10],
            },
            "scripts/": {
                "purpose": "Automation, data ingestion, CLI tools",
                "candidates": self.module_map.get("scripts", [])
                + self.module_map.get("bin", [])
                + self.module_map.get("cli", []),
            },
            "templates/": {
                "purpose": "Starter configs, scaffolding, known-good examples",
                "candidates": self.module_map.get("templates", [])
                + self.module_map.get("scaffold", [])
                + self.module_map.get("examples", []),
            },
            "reused_code_blocks": reusable_blocks[:5],
            "candidate_for_skill": len(deep_modules) >= 2 and self.total_loc >= 500,
            "promotion_recommendation": (
                "This repo has clear deep modules and enough code to be a reusable skill. "
                "Consider invoking `skill-creator` if the problem domain is generalizable."
                if len(deep_modules) >= 2 and self.total_loc >= 500
                else "Repo is too small or too shallow to promote as a standalone skill. "
                "Continue as a project, not a skill."
            ),
        }

    # -----------------------------------------------------------------------
    # Step 7: Output
    # -----------------------------------------------------------------------
    def _write_json(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Append with timestamp if file exists
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(existing, dict):
                existing[f"_snapshot_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"] = data
                data = existing
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def run(self) -> None:
        print(f"🔍 Organizing: {self.repo_path}")
        self.surface_scan()
        self.deep_analysis()
        self.context_layer()

        if self.has_run_project:
            # Bind to .run-project/
            base = self.repo_path / ".run-project"
            self._write_json(base / "organizer-report.json", self.report)
            self._write_json(base / "context" / "structural.json", self.report["context"]["structural"])
            self._write_json(base / "context" / "semantic.json", self.report["context"]["semantic"])
            self._write_json(base / "context" / "philosophical.json", self.report["context"]["philosophical"])

            spec_data = self.spec_diagram_output()
            self._write_json(base / "seeit" / "modules.json", spec_data["modules"])
            self._write_json(base / "seeit" / "interfaces.json", spec_data["interfaces"])
            self._write_json(base / "seeit" / "data-flow.json", spec_data["data_flow"])
            self._write_json(base / "seeit" / "state-surface.json", spec_data["state_surface"])
            self._write_json(base / "seeit" / "hotspots.json", spec_data["hotspots"])

            # Skill-format structure (recommendatory)
            skill_struct = self.skill_format_structure()
            self._write_json(base / "skill-structure.json", skill_struct)

            print(f"✅ Bound to {base}")
            print(f"   organizer-report.json")
            print(f"   context/{{structural,semantic,philosophical}}.json")
            print(f"   seeit/{{modules,interfaces,data-flow,state-surface,hotspots}}.json")
            print(f"   skill-structure.json  (recommendatory — see SKILL.md Part 2b)")
        else:
            # Standalone: print summary
            print("\n--- Surface Scan ---")
            for k, v in self.report["surface"].items():
                print(f"  {k}: {v}")

            if "deep" in self.report and self.report["deep"].get("skipped"):
                print(f"\n⚠️  {self.report['deep']['reason']}")
            else:
                print("\n--- Deep Module Scores (top 5) ---")
                top = sorted(self.deep_scores, key=lambda m: self.deep_scores[m]["deep_score"], reverse=True)[:5]
                for m in top:
                    s = self.deep_scores[m]
                    print(f"  {m}: deep_score={s['deep_score']}, stability={s['stability']}, coupling={s['coupling']}, loc={s['loc']}")

                print("\n--- Circular Dependencies ---")
                print(f"  Found: {len(self.circular)}")
                for c in self.circular[:3]:
                    print(f"    {' → '.join(c)}")

                print("\n--- Orphans ---")
                print(f"  {self.orphans or 'None'}")

                print("\n--- Recommendations ---")
                for r in self.report["context"]["philosophical"]["recommendations"]:
                    print(f"  • {r}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Universal Codebase Organizer")
    parser.add_argument("path", nargs="?", default=".", help="Repo path")
    args = parser.parse_args()

    organizer = CodebaseOrganizer(repo_path=Path(args.path))
    organizer.run()


if __name__ == "__main__":
    main()
