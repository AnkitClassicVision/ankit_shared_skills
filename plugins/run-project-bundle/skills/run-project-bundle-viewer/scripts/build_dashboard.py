#!/usr/bin/env python3
"""Build a static dashboard for the run-project skill bundle.

The script intentionally has no mandatory third-party dependencies. If PyYAML is
available it is used for frontmatter parsing; otherwise a small fallback parser
handles the viewer metadata fields used by this repository.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # Optional: available in many agent runtimes, but not required.
    import yaml  # type: ignore
except Exception:  # pragma: no cover - exercised only in minimal runtimes
    yaml = None

PHASE_ORDER = ["sense", "shape", "spec", "execute", "transfer"]
PHASE_LABELS = {
    "sense": "Sense",
    "shape": "Shape",
    "spec": "Spec",
    "execute": "Execute",
    "transfer": "Transfer",
}
PHASE_DESCRIPTIONS = {
    "sense": "Triage, clarify, challenge, or route messy context.",
    "shape": "Visualize or analyze code and project structure.",
    "spec": "Turn intent into behavioral requirements or readiness criteria.",
    "execute": "Create implementation plans, issue sets, or project runs.",
    "transfer": "Preserve or improve context for future agents.",
}
CATEGORY_VOCAB = {
    "conductor",
    "interrogate",
    "sensemaking",
    "triage",
    "visualize",
    "repo",
    "spec",
    "plan",
    "agent-safety",
    "transfer",
}
RISK_LEVELS = {"low", "medium", "high"}
SIDE_EFFECTS = {"none", "draft-only", "can-write-files"}
REQUIRED_FIELDS = [
    "name",
    "display_name",
    "viewer_summary",
    "bundle",
    "phase",
    "category",
    "artifact_type",
    "primary_command",
    "triggers",
    "inputs",
    "outputs",
    "dependencies",
    "risk_level",
    "side_effects",
    "requires_repo",
    "requires_network",
]
SKIP_DIRS = {
    ".git",
    ".agents",
    ".github",
    "docs",
    "plugins",
    "scripts",
    "node_modules",
    "__pycache__",
}


def split_frontmatter(text: str, path: Path) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    try:
        _, frontmatter, body = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError(f"{path}: frontmatter is not closed") from exc
    return frontmatter, body


def parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw == "":
        return ""
    if raw in {"true", "True"}:
        return True
    if raw in {"false", "False"}:
        return False
    if raw in {"null", "None", "~"}:
        return None
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",")]
    if (raw.startswith("'") and raw.endswith("'")) or (raw.startswith('"') and raw.endswith('"')):
        return raw[1:-1]
    return raw


def parse_frontmatter_fallback(frontmatter: str) -> dict[str, Any]:
    """Minimal YAML parser for the simple metadata shape used here."""
    data: dict[str, Any] = {}
    lines = frontmatter.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if not line.startswith(" ") and ":" in line:
            key, raw = line.split(":", 1)
            key = key.strip()
            raw = raw.strip()
            if raw in {">", ">-", "|", "|-"}:
                block: list[str] = []
                i += 1
                while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                    block.append(lines[i][2:] if lines[i].startswith("  ") else "")
                    i += 1
                data[key] = "\n".join(block).strip()
                continue
            if raw:
                data[key] = parse_scalar(raw)
                i += 1
                continue
            # Nested list or dict.
            i += 1
            if i < len(lines) and lines[i].startswith("  - "):
                items: list[Any] = []
                while i < len(lines) and lines[i].startswith("  - "):
                    items.append(parse_scalar(lines[i][4:]))
                    i += 1
                data[key] = items
                continue
            nested: dict[str, Any] = {}
            while i < len(lines) and lines[i].startswith("  "):
                nested_line = lines[i][2:]
                if not nested_line.strip():
                    i += 1
                    continue
                if ":" not in nested_line:
                    i += 1
                    continue
                subkey, subraw = nested_line.split(":", 1)
                subkey = subkey.strip()
                subraw = subraw.strip()
                if subraw:
                    nested[subkey] = parse_scalar(subraw)
                    i += 1
                    continue
                i += 1
                subitems: list[Any] = []
                while i < len(lines) and lines[i].startswith("    - "):
                    subitems.append(parse_scalar(lines[i][6:]))
                    i += 1
                nested[subkey] = subitems
            data[key] = nested
            continue
        i += 1
    return data


def load_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    frontmatter, body = split_frontmatter(path.read_text(encoding="utf-8"), path)
    if yaml is not None:
        loaded = yaml.safe_load(frontmatter) or {}
    else:
        loaded = parse_frontmatter_fallback(frontmatter)
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: frontmatter must parse to a mapping")
    return loaded, body


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def normalize_dependencies(value: Any) -> dict[str, list[str]]:
    if isinstance(value, dict):
        return {
            "before": as_list(value.get("before")),
            "after": as_list(value.get("after")),
        }
    return {"before": [], "after": []}


def extract_sections(body: str) -> list[dict[str, str]]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", body, re.MULTILINE))
    sections: list[dict[str, str]] = []
    for idx, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        content = body[start:end].strip()
        # Compact preview: first non-heading paragraph, stripped of markdown bullets.
        preview = ""
        for para in re.split(r"\n\s*\n", content):
            cleaned = re.sub(r"^[-*]\s+", "", para.strip())
            cleaned = re.sub(r"\s+", " ", cleaned)
            if cleaned and not cleaned.startswith("###"):
                preview = cleaned[:220]
                break
        sections.append({"title": title, "preview": preview})
    return sections


def discover_skills(repo: Path, bundle: str) -> list[dict[str, Any]]:
    skills: list[dict[str, Any]] = []
    for child in sorted(repo.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir() or child.name in SKIP_DIRS or child.name.startswith("."):
            continue
        skill_md = child / "SKILL.md"
        if not skill_md.is_file():
            continue
        meta, body = load_frontmatter(skill_md)
        if meta.get("bundle", bundle) != bundle:
            continue
        name = str(meta.get("name") or child.name)
        display_name = str(meta.get("display_name") or name.replace("-", " ").title())
        dependencies = normalize_dependencies(meta.get("dependencies"))
        missing = [field for field in REQUIRED_FIELDS if field not in meta or meta.get(field) in (None, "")]
        warnings: list[str] = []
        phase = str(meta.get("phase") or "")
        category = str(meta.get("category") or "")
        risk = str(meta.get("risk_level") or "")
        side_effects = str(meta.get("side_effects") or "")
        if phase and phase not in PHASE_ORDER:
            warnings.append(f"phase '{phase}' is outside recommended vocabulary")
        if category and category not in CATEGORY_VOCAB:
            warnings.append(f"category '{category}' is outside recommended vocabulary")
        if risk and risk not in RISK_LEVELS:
            warnings.append(f"risk_level '{risk}' is outside recommended vocabulary")
        if side_effects and side_effects not in SIDE_EFFECTS:
            warnings.append(f"side_effects '{side_effects}' is outside recommended vocabulary")
        skills.append(
            {
                "name": name,
                "display_name": display_name,
                "viewer_summary": str(meta.get("viewer_summary") or meta.get("description") or ""),
                "description": str(meta.get("description") or ""),
                "bundle": str(meta.get("bundle") or bundle),
                "phase": phase or "sense",
                "phase_label": PHASE_LABELS.get(phase, phase.title() if phase else "Sense"),
                "category": category or "sensemaking",
                "artifact_type": str(meta.get("artifact_type") or "markdown-artifact"),
                "primary_command": str(meta.get("primary_command") or f"/{name}"),
                "triggers": as_list(meta.get("triggers")),
                "inputs": as_list(meta.get("inputs")),
                "outputs": as_list(meta.get("outputs")),
                "dependencies": dependencies,
                "risk_level": risk or "medium",
                "side_effects": side_effects or "draft-only",
                "requires_repo": bool(meta.get("requires_repo")),
                "requires_network": bool(meta.get("requires_network")),
                "path": str(skill_md.relative_to(repo)),
                "sections": extract_sections(body),
                "missing_fields": missing,
                "warnings": warnings,
            }
        )
    return sorted(skills, key=lambda s: (PHASE_ORDER.index(s["phase"]) if s["phase"] in PHASE_ORDER else 99, s["display_name"]))


def build_edges(skills: list[dict[str, Any]]) -> list[dict[str, str]]:
    names = {skill["name"] for skill in skills}
    edges: set[tuple[str, str]] = set()
    for skill in skills:
        for before in skill["dependencies"].get("before", []):
            if before in names:
                edges.add((before, skill["name"]))
        for after in skill["dependencies"].get("after", []):
            if after in names:
                edges.add((skill["name"], after))
    return [{"from": src, "to": dst} for src, dst in sorted(edges)]


def canonical_repo_name(repo: Path) -> str:
    config_path = repo / ".git" / "config"
    if config_path.is_file():
        text = config_path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"url\s*=\s*.+/([^/\s]+?)(?:\.git)?\s*$", text, re.MULTILINE)
        if match:
            return match.group(1)
    return repo.name


def summarize(skills: list[dict[str, Any]], repo: Path, bundle: str) -> dict[str, Any]:
    phase_counts = {phase: 0 for phase in PHASE_ORDER}
    category_counts: dict[str, int] = {}
    risks: dict[str, int] = {}
    side_effect_counts: dict[str, int] = {}
    for skill in skills:
        phase_counts[skill["phase"]] = phase_counts.get(skill["phase"], 0) + 1
        category_counts[skill["category"]] = category_counts.get(skill["category"], 0) + 1
        risks[skill["risk_level"]] = risks.get(skill["risk_level"], 0) + 1
        side_effect_counts[skill["side_effects"]] = side_effect_counts.get(skill["side_effects"], 0) + 1
    return {
        "bundle": bundle,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_name": canonical_repo_name(repo),
        "skill_count": len(skills),
        "phase_counts": phase_counts,
        "category_counts": category_counts,
        "risk_counts": risks,
        "side_effect_counts": side_effect_counts,
        "missing_field_count": sum(len(skill["missing_fields"]) for skill in skills),
        "warning_count": sum(len(skill["warnings"]) for skill in skills),
    }


def render_html(payload: dict[str, Any]) -> str:
    json_payload = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    title = html.escape(str(payload["summary"]["bundle"]).replace("-", " ").title())
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{title} Dashboard</title>
  <style>
    :root {{
      --ink: #16201b;
      --muted: #66746f;
      --paper: #f8f2e8;
      --paper-2: #fffaf1;
      --line: rgba(22, 32, 27, .14);
      --teal: #0f766e;
      --moss: #4d7c0f;
      --gold: #c98924;
      --rose: #b45353;
      --blue: #2563eb;
      --shadow: 0 24px 80px rgba(34, 28, 18, .12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at 14% -10%, rgba(15, 118, 110, .18), transparent 34rem),
        radial-gradient(circle at 90% 0%, rgba(201, 137, 36, .16), transparent 30rem),
        linear-gradient(135deg, #fbf6ed 0%, #f4efe5 45%, #eef4f0 100%);
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    .shell {{ max-width: 1480px; margin: 0 auto; padding: 38px 24px 72px; }}
    .hero {{
      position: relative;
      overflow: hidden;
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(320px, .8fr);
      gap: 28px;
      padding: 34px;
      border: 1px solid var(--line);
      border-radius: 32px;
      background: rgba(255, 250, 241, .78);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
    }}
    .hero:after {{
      content: "";
      position: absolute;
      inset: auto -15% -55% 35%;
      height: 320px;
      border-radius: 999px;
      background: linear-gradient(90deg, rgba(15, 118, 110, .15), rgba(37, 99, 235, .08), rgba(201, 137, 36, .14));
      transform: rotate(-8deg);
    }}
    .eyebrow {{
      display: inline-flex;
      gap: 10px;
      align-items: center;
      padding: 7px 11px;
      border: 1px solid rgba(15, 118, 110, .24);
      border-radius: 999px;
      color: #075f59;
      background: rgba(15, 118, 110, .08);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .12em;
      text-transform: uppercase;
    }}
    h1 {{
      max-width: 850px;
      margin: 18px 0 16px;
      font-family: ui-serif, Georgia, Cambria, "Times New Roman", serif;
      font-size: clamp(46px, 7vw, 92px);
      line-height: .9;
      letter-spacing: -.06em;
    }}
    .lede {{ max-width: 760px; color: var(--muted); font-size: 18px; }}
    .hero-panel {{
      position: relative;
      z-index: 1;
      align-self: stretch;
      display: grid;
      gap: 12px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: linear-gradient(180deg, rgba(255,255,255,.7), rgba(255,255,255,.35));
    }}
    .metric-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    .metric {{ padding: 16px; border: 1px solid var(--line); border-radius: 20px; background: rgba(255, 250, 241, .8); }}
    .metric strong {{ display: block; font-size: 31px; line-height: 1; letter-spacing: -.04em; }}
    .metric span {{ display: block; margin-top: 7px; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; font-weight: 800; }}
    .toolbar {{
      position: sticky;
      top: 0;
      z-index: 5;
      display: grid;
      grid-template-columns: minmax(220px, 1fr) repeat(3, minmax(160px, 220px));
      gap: 10px;
      margin: 24px 0;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 22px;
      background: rgba(248, 242, 232, .86);
      backdrop-filter: blur(18px);
    }}
    input, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 15px;
      padding: 12px 13px;
      color: var(--ink);
      background: rgba(255,255,255,.74);
      font: inherit;
      outline: none;
    }}
    input:focus, select:focus {{ border-color: rgba(15,118,110,.55); box-shadow: 0 0 0 4px rgba(15,118,110,.11); }}
    .section-title {{ display: flex; align-items: end; justify-content: space-between; gap: 20px; margin: 34px 0 14px; }}
    .section-title h2 {{ margin: 0; font-family: ui-serif, Georgia, serif; font-size: clamp(28px, 4vw, 48px); letter-spacing: -.04em; }}
    .section-title p {{ margin: 0; color: var(--muted); max-width: 620px; }}
    .lanes {{ display: grid; gap: 18px; }}
    .lane {{
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: 18px;
      background: rgba(255, 250, 241, .66);
      box-shadow: 0 12px 34px rgba(34, 28, 18, .06);
    }}
    .lane-head {{ display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 4px 6px 16px; }}
    .lane-head h3 {{ margin: 0; font-size: 20px; letter-spacing: -.02em; }}
    .lane-head .desc {{ color: var(--muted); font-size: 14px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 14px; }}
    .card {{
      display: flex;
      flex-direction: column;
      gap: 13px;
      min-height: 300px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: rgba(255, 255, 255, .62);
      transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
    }}
    .card:hover {{ transform: translateY(-3px); border-color: rgba(15,118,110,.34); box-shadow: 0 18px 46px rgba(34, 28, 18, .10); }}
    .card-top {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; }}
    .card h4 {{ margin: 0; font-size: 21px; letter-spacing: -.03em; }}
    .summary {{ margin: 0; color: var(--muted); }}
    .chip-row {{ display: flex; gap: 7px; flex-wrap: wrap; }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid rgba(22,32,27,.12);
      border-radius: 999px;
      padding: 5px 9px;
      background: rgba(248,242,232,.72);
      color: #33423d;
      font-size: 12px;
      font-weight: 750;
    }}
    .chip.command {{ color: #064e48; background: rgba(15,118,110,.10); border-color: rgba(15,118,110,.22); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .chip.high {{ color: #8b2727; background: rgba(180,83,83,.10); border-color: rgba(180,83,83,.22); }}
    .chip.medium {{ color: #7a4d00; background: rgba(201,137,36,.12); border-color: rgba(201,137,36,.24); }}
    .chip.low {{ color: #275c13; background: rgba(77,124,15,.10); border-color: rgba(77,124,15,.22); }}
    .list-pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: auto; }}
    .mini {{ padding: 11px; border: 1px solid var(--line); border-radius: 16px; background: rgba(248,242,232,.52); }}
    .mini b {{ display: block; margin-bottom: 6px; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; }}
    .mini ul {{ margin: 0; padding-left: 17px; color: var(--muted); font-size: 13px; }}
    details {{ border-top: 1px solid var(--line); padding-top: 10px; }}
    summary {{ cursor: pointer; color: var(--teal); font-weight: 800; }}
    .deps {{ display: grid; gap: 7px; margin-top: 8px; color: var(--muted); font-size: 13px; }}
    .graph-wrap {{ overflow: auto; border: 1px solid var(--line); border-radius: 28px; background: rgba(255,255,255,.52); box-shadow: 0 12px 34px rgba(34, 28, 18, .06); }}
    svg {{ min-width: 1120px; width: 100%; display: block; }}
    .node rect {{ fill: rgba(255,250,241,.94); stroke: rgba(22,32,27,.18); stroke-width: 1; rx: 16; }}
    .node text {{ font: 700 13px ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: var(--ink); }}
    .node .phase-text {{ font: 800 10px ui-sans-serif, sans-serif; fill: #0f766e; letter-spacing: .08em; text-transform: uppercase; }}
    .edge {{ fill: none; stroke: rgba(15,118,110,.35); stroke-width: 1.6; }}
    .empty {{ padding: 28px; color: var(--muted); text-align: center; border: 1px dashed var(--line); border-radius: 24px; }}
    .footer {{ margin-top: 34px; color: var(--muted); font-size: 13px; }}
    @media (max-width: 900px) {{
      .hero {{ grid-template-columns: 1fr; padding: 24px; }}
      .toolbar {{ grid-template-columns: 1fr; position: static; }}
      .list-pair {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main class=\"shell\">
    <section class=\"hero\">
      <div>
        <span class=\"eyebrow\">Brain Viewer Ready · Static Artifact</span>
        <h1>Run Project Bundle Dashboard</h1>
        <p class=\"lede\">A generated map of the shared skill bundle: phase lanes, invocation chips, risk and side-effect badges, inputs, outputs, and dependency flow. Built directly from each <code>SKILL.md</code> frontmatter file.</p>
      </div>
      <aside class=\"hero-panel\">
        <div class=\"metric-grid\" id=\"metrics\"></div>
        <div class=\"chip-row\" id=\"phaseChips\"></div>
      </aside>
    </section>

    <section class=\"toolbar\" aria-label=\"Dashboard filters\">
      <input id=\"search\" type=\"search\" placeholder=\"Search skills, commands, triggers, outputs…\" />
      <select id=\"phaseFilter\"><option value=\"\">All phases</option></select>
      <select id=\"categoryFilter\"><option value=\"\">All categories</option></select>
      <select id=\"riskFilter\"><option value=\"\">All risk levels</option></select>
    </section>

    <section class=\"section-title\">
      <div>
        <h2>Workflow rails</h2>
        <p>Each lane uses the controlled phase vocabulary from the recipe so Brain Viewer can group cards without guessing from prose.</p>
      </div>
      <span class=\"chip\" id=\"visibleCount\"></span>
    </section>
    <section class=\"lanes\" id=\"lanes\"></section>

    <section class=\"section-title\">
      <div>
        <h2>Dependency graph</h2>
        <p>Edges are derived from <code>dependencies.before</code> and <code>dependencies.after</code>. The graph is intentionally static and docs-site friendly.</p>
      </div>
    </section>
    <section class=\"graph-wrap\" id=\"graph\"></section>

    <p class=\"footer\" id=\"footer\"></p>
  </main>
  <script>
    const DATA = {json_payload};
    const phaseOrder = {json.dumps(PHASE_ORDER)};
    const phaseLabels = {json.dumps(PHASE_LABELS)};
    const phaseDescriptions = {json.dumps(PHASE_DESCRIPTIONS)};
    const skills = DATA.skills;
    const edges = DATA.edges;

    function unique(values) {{ return [...new Set(values.filter(Boolean))].sort(); }}
    function esc(value) {{ return String(value ?? '').replace(/[&<>\"]/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}}[ch])); }}
    function list(items, max=3) {{
      const visible = (items || []).slice(0, max);
      const extra = (items || []).length - visible.length;
      return `<ul>${{visible.map(item => `<li>${{esc(item)}}</li>`).join('')}}${{extra > 0 ? `<li>+${{extra}} more</li>` : ''}}</ul>`;
    }}
    function skillText(skill) {{
      return [skill.name, skill.display_name, skill.viewer_summary, skill.description, skill.primary_command, skill.phase, skill.category, skill.artifact_type, ...(skill.triggers||[]), ...(skill.inputs||[]), ...(skill.outputs||[])].join(' ').toLowerCase();
    }}
    function currentFilters() {{
      return {{
        q: document.getElementById('search').value.trim().toLowerCase(),
        phase: document.getElementById('phaseFilter').value,
        category: document.getElementById('categoryFilter').value,
        risk: document.getElementById('riskFilter').value,
      }};
    }}
    function filteredSkills() {{
      const f = currentFilters();
      return skills.filter(skill =>
        (!f.q || skillText(skill).includes(f.q)) &&
        (!f.phase || skill.phase === f.phase) &&
        (!f.category || skill.category === f.category) &&
        (!f.risk || skill.risk_level === f.risk)
      );
    }}
    function renderMetrics() {{
      const s = DATA.summary;
      document.getElementById('metrics').innerHTML = [
        ['Skills', s.skill_count],
        ['Phases', Object.values(s.phase_counts).filter(Boolean).length],
        ['Write-capable', s.side_effect_counts['can-write-files'] || 0],
        ['Warnings', s.warning_count + s.missing_field_count],
      ].map(([label, value]) => `<div class=\"metric\"><strong>${{value}}</strong><span>${{label}}</span></div>`).join('');
      document.getElementById('phaseChips').innerHTML = phaseOrder.map(phase => `<span class=\"chip\">${{phaseLabels[phase]}} · ${{s.phase_counts[phase] || 0}}</span>`).join('');
      document.getElementById('footer').textContent = `Generated ${{s.generated_at}} from ${{s.repo_name}}. Missing-field count: ${{s.missing_field_count}}. Vocabulary warnings: ${{s.warning_count}}.`;
    }}
    function populateFilters() {{
      const phaseSel = document.getElementById('phaseFilter');
      phaseOrder.forEach(phase => phaseSel.insertAdjacentHTML('beforeend', `<option value=\"${{phase}}\">${{phaseLabels[phase]}}</option>`));
      const catSel = document.getElementById('categoryFilter');
      unique(skills.map(s => s.category)).forEach(cat => catSel.insertAdjacentHTML('beforeend', `<option value=\"${{cat}}\">${{cat}}</option>`));
      const riskSel = document.getElementById('riskFilter');
      unique(skills.map(s => s.risk_level)).forEach(risk => riskSel.insertAdjacentHTML('beforeend', `<option value=\"${{risk}}\">${{risk}}</option>`));
    }}
    function renderCard(skill) {{
      const riskClass = ['low','medium','high'].includes(skill.risk_level) ? skill.risk_level : '';
      const depsBefore = (skill.dependencies?.before || []).join(', ') || 'none';
      const depsAfter = (skill.dependencies?.after || []).join(', ') || 'none';
      const warnings = [...(skill.missing_fields || []).map(f => `missing: ${{f}}`), ...(skill.warnings || [])];
      return `<article class=\"card\" data-name=\"${{esc(skill.name)}}\">
        <div class=\"card-top\"><h4>${{esc(skill.display_name)}}</h4><span class=\"chip command\">${{esc(skill.primary_command)}}</span></div>
        <p class=\"summary\">${{esc(skill.viewer_summary)}}</p>
        <div class=\"chip-row\">
          <span class=\"chip\">${{esc(skill.category)}}</span>
          <span class=\"chip\">${{esc(skill.artifact_type)}}</span>
          <span class=\"chip ${{riskClass}}\">risk: ${{esc(skill.risk_level)}}</span>
          <span class=\"chip\">${{esc(skill.side_effects)}}</span>
          ${{skill.requires_repo ? '<span class=\"chip\">repo</span>' : ''}}
          ${{skill.requires_network ? '<span class=\"chip\">network</span>' : ''}}
        </div>
        <div class=\"list-pair\">
          <div class=\"mini\"><b>Inputs</b>${{list(skill.inputs)}}</div>
          <div class=\"mini\"><b>Outputs</b>${{list(skill.outputs)}}</div>
        </div>
        <details>
          <summary>Routing + dependencies</summary>
          <div class=\"deps\">
            <div><b>Triggers:</b> ${{esc((skill.triggers || []).join(', ') || 'not listed')}}</div>
            <div><b>Before:</b> ${{esc(depsBefore)}}</div>
            <div><b>After:</b> ${{esc(depsAfter)}}</div>
            <div><b>Source:</b> <code>${{esc(skill.path)}}</code></div>
            ${{warnings.length ? `<div><b>Metadata notes:</b> ${{esc(warnings.join('; '))}}</div>` : ''}}
          </div>
        </details>
      </article>`;
    }}
    function renderLanes() {{
      const visible = filteredSkills();
      document.getElementById('visibleCount').textContent = `${{visible.length}} visible / ${{skills.length}} total`;
      const lanes = phaseOrder.map(phase => {{
        const laneSkills = visible.filter(skill => skill.phase === phase);
        if (!laneSkills.length) return '';
        return `<div class=\"lane\">
          <div class=\"lane-head\"><h3>${{phaseLabels[phase]}}</h3><span class=\"desc\">${{phaseDescriptions[phase]}}</span></div>
          <div class=\"cards\">${{laneSkills.map(renderCard).join('')}}</div>
        </div>`;
      }}).join('');
      document.getElementById('lanes').innerHTML = lanes || '<div class=\"empty\">No skills match the current filters.</div>';
      renderGraph(visible);
    }}
    function renderGraph(visible) {{
      const visibleNames = new Set(visible.map(s => s.name));
      const byPhase = Object.fromEntries(phaseOrder.map(p => [p, visible.filter(s => s.phase === p)]));
      const width = 1220;
      const colW = 220;
      const left = 42;
      const top = 70;
      const rowH = 82;
      const maxRows = Math.max(1, ...Object.values(byPhase).map(arr => arr.length));
      const height = top + maxRows * rowH + 70;
      const coords = new Map();
      phaseOrder.forEach((phase, pi) => {{
        (byPhase[phase] || []).forEach((skill, si) => coords.set(skill.name, {{x: left + pi * (colW + 20), y: top + si * rowH, phase}}));
      }});
      const visibleEdges = edges.filter(e => visibleNames.has(e.from) && visibleNames.has(e.to) && coords.has(e.from) && coords.has(e.to));
      const paths = visibleEdges.map(e => {{
        const a = coords.get(e.from); const b = coords.get(e.to);
        const x1 = a.x + 180, y1 = a.y + 25, x2 = b.x, y2 = b.y + 25;
        const mid = Math.max(28, Math.abs(x2 - x1) / 2);
        return `<path class=\"edge\" marker-end=\"url(#arrow)\" d=\"M ${{x1}} ${{y1}} C ${{x1 + mid}} ${{y1}}, ${{x2 - mid}} ${{y2}}, ${{x2}} ${{y2}}\"><title>${{esc(e.from)}} → ${{esc(e.to)}}</title></path>`;
      }}).join('');
      const phaseHeaders = phaseOrder.map((phase, pi) => `<text x=\"${{left + pi * (colW + 20)}}\" y=\"32\" class=\"phase-text\">${{phaseLabels[phase]}}</text>`).join('');
      const nodes = [...coords.entries()].map(([name, c]) => {{
        const skill = visible.find(s => s.name === name);
        const label = (skill?.display_name || name).length > 23 ? (skill?.display_name || name).slice(0, 21) + '…' : (skill?.display_name || name);
        return `<g class=\"node\" transform=\"translate(${{c.x}},${{c.y}})\"><rect width=\"180\" height=\"54\"></rect><text x=\"14\" y=\"23\">${{esc(label)}}</text><text x=\"14\" y=\"40\" class=\"phase-text\">${{esc(skill?.primary_command || '')}}</text></g>`;
      }}).join('');
      document.getElementById('graph').innerHTML = `<svg viewBox=\"0 0 ${{width}} ${{height}}\" role=\"img\" aria-label=\"Run project bundle dependency graph\">
        <defs><marker id=\"arrow\" viewBox=\"0 0 10 10\" refX=\"8\" refY=\"5\" markerWidth=\"6\" markerHeight=\"6\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" fill=\"rgba(15,118,110,.55)\"></path></marker></defs>
        ${{phaseHeaders}}${{paths}}${{nodes}}
      </svg>`;
    }}
    renderMetrics();
    populateFilters();
    ['search','phaseFilter','categoryFilter','riskFilter'].forEach(id => document.getElementById(id).addEventListener('input', renderLanes));
    renderLanes();
  </script>
</body>
</html>
"""


def write_outputs(repo: Path, out_dir: Path, bundle: str, strict: bool) -> int:
    skills = discover_skills(repo, bundle)
    if not skills:
        raise SystemExit(f"No skills found for bundle '{bundle}' under {repo}")
    payload = {
        "summary": summarize(skills, repo, bundle),
        "phases": [{"name": p, "label": PHASE_LABELS[p], "description": PHASE_DESCRIPTIONS[p]} for p in PHASE_ORDER],
        "skills": skills,
        "edges": build_edges(skills),
        "required_fields": REQUIRED_FIELDS,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    data_path = out_dir / "run-project-bundle-data.json"
    html_path = out_dir / "run-project-bundle-dashboard.html"
    data_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    html_path.write_text(render_html(payload), encoding="utf-8")

    missing = [(skill["name"], skill["missing_fields"]) for skill in skills if skill["missing_fields"]]
    warnings = [(skill["name"], skill["warnings"]) for skill in skills if skill["warnings"]]
    print(f"wrote {data_path.relative_to(repo) if data_path.is_relative_to(repo) else data_path}")
    print(f"wrote {html_path.relative_to(repo) if html_path.is_relative_to(repo) else html_path}")
    print(f"skills={len(skills)} edges={len(payload['edges'])} missing_fields={sum(len(x[1]) for x in missing)} warnings={sum(len(x[1]) for x in warnings)}")
    if missing:
        for name, fields in missing:
            print(f"missing {name}: {', '.join(fields)}", file=sys.stderr)
    if warnings:
        for name, notes in warnings:
            print(f"warning {name}: {'; '.join(notes)}", file=sys.stderr)
    if strict and (missing or warnings):
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Run Project Bundle dashboard from SKILL.md frontmatter.")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root containing skill folders. Defaults to cwd.")
    parser.add_argument("--out-dir", type=Path, default=None, help="Output directory. Defaults to <repo>/docs.")
    parser.add_argument("--bundle", default="run-project", help="Bundle metadata value to include.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if required viewer fields or vocabulary checks fail.")
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    out_dir = (args.out_dir or repo / "docs").resolve()
    return write_outputs(repo=repo, out_dir=out_dir, bundle=args.bundle, strict=args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
