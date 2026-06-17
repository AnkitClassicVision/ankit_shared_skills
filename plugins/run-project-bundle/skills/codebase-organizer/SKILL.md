---
name: codebase-organizer
description: >
  Universal codebase operations: analyze, organize, and architecturally deepen any repo.
  Two commands: /organize for read-only analysis and /deepen for multi-agent refactoring.
  Use when the user wants a codebase scan, deep module scoring, dependency mapping,
  architectural improvement, or code-to-skill conversion.
  Triggers: "organize this repo", "/organize", "deepen this codebase", "/deepen",
  "improve architecture", "brownfield rescue", "codebase audit", "create a skill from my code".
version: 3.0.0
author: Public Maintainer
category: software-development
surfaces: [hermes, claude-code, codex]
tags: [organize, analyze, brownfield, deepen, deep-modules, context-layer, spec-diagram, refactoring, architecture]
---

# codebase-organizer

## One-line pitch

Point it at any repo. Get a structured, skill-like decomposition with deep module scoring, dependency graph, circular dependency detection, orphaned file surfacing, and three-layer context extraction — all saved to `.run-project/` for automatic consumption by `/run-project`, SEEIT, and agent-spec phases.

## Invocation

```
/organize [path]
```

- `path`: Repo path (defaults to `.`).
- Zero flags. All behavior auto-detected:
  - **Repo size** < 1000 LOC → lightweight scan only
  - **Repo size** >= 1000 LOC → deep analysis enabled
  - **Existing** `.run-project/` → bind to existing pipeline context
  - **Clean** repo → produce standalone analysis

## When to use it

| Situation | Tool | Why |
|-----------|------|-----|
| Starting `/run-project` on brownfield | `/organize` | Establish baseline architecture before grilling |
| During spec diagramming | `/organize` | Inject organized structure into SEEIT |
| Post-refactor audit | `/organize` | See what changed, find new hotspots |
| Onboarding new AI agent | `/skillify` | Give it `.skill-pack/PROJECT.md` — a consumable skill manifest |
| Exploring inherited code | `/organize` | Quick orientation — deep modules, seams, orphaned files |
| Any time you feel lost in a repo | `/skillify` | Re-run. `.skill-pack/` stays fresh. |
| Want repo to be consumable by agents | `/skillify` | Produces persistent `.skill-pack/` that travels with repo |

## Pipeline integration (automatic binding)

When `.run-project/` exists, the organizer auto-writes to:

```
.run-project/
  context/
    structural.json      -- module map, import graph, circular deps, orphans
    semantic.json        -- interfaces, contracts, complexity scores
    philosophical.json   -- deep modules, hotspots, recommendations
  seeit/
    modules.json         -- spec-diagram injection data
    interfaces.json      -- entry points + contracts
    data-flow.json       -- producer → consumer pairs
  skill-structure.json   -- candidate skill layout (see Part 2b above)
  organizer-report.json  -- summary for resume-read by /run-project phases
```

`/run-project` auto-discovers these files and feeds them forward:
- **Grill phase**: Uses deep module scores and hotspot list
- **Context Layer phase**: Reads structural/semantic/philosophical layers
- **SEEIT phase**: Consumes modules.json, interfaces.json, data-flow.json
- **Skill Creation phase**: If user or downstream phase decides to promote repo to formal skill, `skill-structure.json` provides the initial layout

**`/skillify` integration**: The organizer's output is the primary input for `/skillify`. When `/skillify [path]` runs, it invokes `/organize` internally, then transforms the analysis into a persistent `.skill-pack/` directory containing:
- `PROJECT.md` — human-readable, agent-consumable repo manifest
- `context/{structural,semantic,philosophical}.json` — machine-readable context layers
- `interfaces/{module}.md` — annotated public APIs
- `adrs/adr-{NNN}.md` — inferred architectural decisions

Use `/organize` when you want analysis only. Use `/skillify` when you want the repo to become a consumable skill for agents.

See `references/run-project-integration.md` for the full binding protocol, append-only snapshot behavior, and re-run triggers.

When `.run-project/` does not exist, the organizer runs standalone and prints to stdout.

## What it produces

### Part 1: Surface Scan (always)

```
repo/
  src/
    core/                -- 3 modules, 12 deps, 2 circular
    api/                 -- REST surface, 4 routes, phi: true
    db/                  -- migration files, schema drift detected
  tests/                 -- coverage 34%, orphaned tests: 3
  docs/                  -- outdated (last edit 8 months ago)

Dominant language: Python
Test-to-source ratio: 0.34
Doc freshness: 8 months stale
```

### Part 2: Deep Module Scoring (auto-enabled for repos >= 1000 LOC)

For each module, calculates **deep module score** using the deep modules philosophy:

| Dimension | Measures | Weight |
|-----------|----------|--------|
| **Stability** | How often it changes (git log 6-month window) | 0.25 |
| **Depth** | Complexity hidden behind interface (AST function/class count) | 0.35 |
| **Interface Surface** | Lines of public API vs private logic | 0.20 |
| **Clarity** | Docstrings, type hints, naming quality | 0.20 |

**Deep Score Formula**:
```
deep_score = (stability * 0.25 + depth * 0.35 + interface_surface * 0.20 + clarity * 0.20) / (coupling + 1)
```

High score = deep module. Protect it. Low score = shallow. Candidate for deepening.

Top deep modules are surfaced for the user and recorded in philosophical.json.

### Part 2b: Skill-Format Structure (new — auto-suggests how to turn this repo into a skill)

After analysis, the organizer emits a `skill-structure.json` that maps repo contents to the standard skill directory layout:

```json
{
  "skill_name": "inventory-system",
  "SKILL.md_suggested_sections": ["inventory analysis", "frame catalog", "aging protocol"],
  "references/": ["docs/inventory-model.md", "README.md#methodology"],
  "scripts/": ["scripts/pull-inventory-data.py", "scripts/generate-po-sheet.py"],
  "templates/": ["templates/method-config.yml"],
  "reused_code_blocks": [
    {"file": "src/abc.py", "function": "classify_frame", "use": "scoring method"}
  ]
}
```

This serves two purposes:
1. **Classify repo as candidate for skill creation** — if the repo solves a reusable class of problems, suggest `skill-creator`
2. **Extract reusable methods** — when a specific function/class is a candidate for standalone reuse, flag it for `scripts/` or `templates/`

The skill-format output is always written but never auto-acts on. The user (or a downstream phase) decides whether to promote the repo into a formal skill.

### Part 3: Dependency Graph

- Static import analysis (AST for Python/JS/Go; regex fallback for other languages)
- Circular dependency detection with cycle paths
- Orphaned file detection (imports nothing, imported by nothing)
- Cross-module coupling matrix

### Part 4: Three-Layer Context (machine-readable)

| Layer | File | Contents |
|-------|------|----------|
| **Structural** | `.run-project/context/structural.json` | Module map, import graph, circular deps, orphans, file tree |
| **Semantic** | `.run-project/context/semantic.json` | Type signatures, docstrings, test contracts, complexity scores per module |
| **Philosophical** | `.run-project/context/philosophical.json` | Deep module rankings, hotspot list, recommendations, architectural smells |

These three layers are the **canonical input format** for the Context Layer Generator skill.

### Part 5: SEEIT Injection Data (for spec diagramming)

| File | Contents |
|------|----------|
| `.run-project/seeit/modules.json` | Module list with depth scores, color-coded by tier |
| `.run-project/seeit/interfaces.json` | Entry points and their contracts |
| `.run-project/seeit/data-flow.json` | Producer → consumer directed edges |
| `.run-project/seeit/state-surface.json` | Where state lives, who mutates it |
| `.run-project/seeit/hotspots.json` | Files with highest churn or deepest coupling |

SEEIT consumes these directly to produce interactive architecture diagrams.

## Deep module philosophy

This organizer applies the deep module philosophy consistently:

- **Module**: anything with an interface and implementation (function, class, package, slice)
- **Interface**: everything a caller must know — types, invariants, error modes, ordering, config
- **Depth**: a lot of behavior behind a small interface. High leverage = deep.
- **Shallow**: interface nearly as complex as implementation. Low leverage = shallow.
- **Seam**: where an interface lives; a place behavior can be altered without editing in place
- **Deletion test**: imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.

The organizer surfaces candidates where the deletion test would concentrate complexity — these are the modules worth deepening.

## /deepen — Multi-Agent Architectural Deepening Pipeline

When the user wants to **improve** the codebase (not just analyze it), run the `/deepen` pipeline.
It is a 7-phase, multi-agent refactoring pipeline with human gates at Grill and Shape.

### When to use /deepen vs /organize

| User intent | Command | Why |
|-------------|---------|-----|
| Understand current state | `/organize` | Read-only. Surfaces deep modules, circular deps, orphans. |
| Improve architecture | `/deepen` | Read+write. Refactors shallow modules into deep ones. |
| Onboarding new agent | `/organize` | Consumable context without touching code. |
| Brownfield rescue | `/deepen` | Starts with `/organize` scan, then applies deepening. |

### Philosophy

- **Deep module**: simple interface + complex implementation
- **Shallow module**: complex interface + little implementation
- **Filesystem must match mental model** — code should be discoverable
- **Progressive disclosure** via interfaces — hide complexity behind seams
- **Test harness before legacy changes** — never refactor without safety net

### The 7-phase pipeline

| Phase | Name | Agent(s) | Human Gate? | Output |
|-------|------|----------|-------------|--------|
| 1 | **Discover** | Gemini 1M scan + Hermes ranking + Claude Code validation | No | Ranked candidate list |
| 2 | **Grill** | Human gate | Yes | Approved module + success criteria |
| 3 | **Shape** | Hermes + human | Yes | Interface contract + test plan |
| 4 | **Spec** | `agent-spec-writer` | No | Behavioral spec document |
| 5 | **Context** | `context-layer-generator` | No | 3-layer context snapshot |
| 6 | **Implement** | `claude-code` or `codex` | No | Working diff + test results |
| 7 | **Verify** | `seeit` | No | Before/after architecture map |

### Deep module score reference

The same scoring algorithm used by `/organize` drives candidate selection:

```
deep_score = (stability * 0.25 + depth * 0.35 + interface_surface * 0.20 + clarity * 0.20) / (coupling + 1)
```

High score = already deep (protect). Low score = shallow (candidate for deepening).

### Integration — /organize feeds /deepen

`/deepen` begins by invoking `/organize` to establish baseline architecture. The organizer's
output ( structural / semantic / philosophical layers, dependency graph, deep module scores )
is the canonical input for Phase 1 (Discover). Re-run `/organize` before each new deepen
session so the baseline is current.

### Risk mitigation

| Risk | Mitigation |
|------|------------|
| AI makes wrong architectural call | Human gates at Grill and Shape |
| Refactor breaks production | Git worktree + comprehensive tests |
| Context gets stale | Re-run `/organize` baseline before each deepen |
| Over-engineering | "Deepen 1–3 modules per session" rule |

### Success metrics

| Metric | Target |
|--------|--------|
| Modules deepened per session | 1–3 (quality over quantity) |
| Public API surface reduction | 50%+ simpler |
| Test coverage at new seams | 90%+ |
| Time to comprehension (new agent) | < 5 minutes |

### Reserved support files for /deepen

- `references/deepen-pipeline-reference.md` — annotated pipeline with agent roles, gates, metrics
- `references/deep-modules-theory.md` — the companion deep module philosophy summary
- `references/grilling-guide.md` — How to evaluate deepening candidates
- `references/interface-patterns.md` — Common adapter and seam patterns
- `scripts/discover-rank.py` — Candidate scoring from 1M-token analysis output
- `scripts/grill-presentation.py` — Format candidate list for human review

## Cross-surface behavior

| Surface | How |
|---------|-----|
| **Hermes** | Runs `scripts/organize.py` directly. Full Python AST analysis. Git history extraction. |
| **Claude Code** | Invokes Claude's built-in codebase analysis. Feeds into Claude's agentic context. |
| **Codex** | Same as Claude (shares skills). Python script execution if available. |
| **All** | Output format is identical. `.run-project/` binding is automatic. |

## Re-running for freshness

Context drifts. Re-run `/organize` when:
- Major refactor completed
- New modules added (3+ files or 1 new directory)
- New dependencies introduced
- Before starting a new feature branch on brownfield
- Any time an AI agent says "I need more context about this repo"

The organizer does not overwrite existing context files destructively — it appends with timestamps so history is preserved.

## Pitfalls

- **Orphaned files are not always bad** — some are entry points, CLI scripts, or config. Verify before deleting.
- **Circular deps in tests are common** — do not flag `test_*.py` circulars as critical.
- **Low deep score does not mean delete** — it means investigate. Some shallow modules are intentional adapters.
- **The organizer does not refactor** — it only surfaces. Deepening is a separate human+agent decision.
- **Do not treat output as immutable architecture** — it is a snapshot for the current context window. Re-run monthly on active repos.
- **Skill-format output is recommendatory** — not every repo should become a formal skill. Only promote when the repo solves a reusable class of problems with clear boundaries. The skill-structure.json signals *candidate* status; a human or downstream phase makes the promotion call.
- **Never auto-create SKILL.md** — the organizer emits suggestions only. Creating a skill requires explicit `skill-creator` invocation with user confirmation.
- **Re-running for freshness does not invalidate prior pipeline phases** — `/run-project` phases consume the latest organizer output but only when explicitly re-triggered. Re-running `/organize` standalone does not automatically restart the pipeline.

## Version history

- v3.0.0 (2026-05-28): Absorbed `codebase-deepen` into umbrella. Now covers /organize (analysis) and /deepen (refactoring) under one class-level skill.
- v2.0.0 (2026-05-28): Surface-agnostic always-on organizer. Deep module philosophy. Auto-binding to `.run-project/`. Three-layer context + SEEIT injection. Zero flags. Auto-detection by repo size.
