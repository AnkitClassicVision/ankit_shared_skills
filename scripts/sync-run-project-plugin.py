#!/usr/bin/env python3
"""Rebuild the repo-local Codex plugin wrapper for the public run-project bundle."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "run-project-bundle"
PLUGIN_ROOT = REPO / "plugins" / PLUGIN_NAME
SKILLS_ROOT = PLUGIN_ROOT / "skills"
MARKETPLACE_PATH = REPO / ".agents" / "plugins" / "marketplace.json"

SKILL_NAMES = [
    "make-it-make-sense",
    "scout",
    "aac-process-design",
    "agent-spec-writer",
    "agenttwin",
    "to-prd",
    "to-issues",
    "improve-codebase-architecture",
    "handoff",
    "grill-me",
    "codebase-organizer",
    "context-layer-generator",
    "run-project",
    "seeit",
    "skillify",
    "writing-plans",
]

PLUGIN_JSON = {
    "name": PLUGIN_NAME,
    "version": "0.1.0",
    "description": "Portable Codex plugin packaging for the public run-project skill bundle.",
    "author": {
        "name": "Ankit Classic Vision",
        "url": "https://github.com/AnkitClassicVision",
    },
    "homepage": "https://github.com/AnkitClassicVision/ankit_shared_skills",
    "repository": "https://github.com/AnkitClassicVision/ankit_shared_skills",
    "license": "MIT",
    "keywords": [
        "skills",
        "run-project",
        "project-planning",
        "codex-plugin",
        "agent-workflow",
    ],
    "skills": "./skills/",
    "interface": {
        "displayName": "Run Project Bundle",
        "shortDescription": "Install the public run-project skill stack as one plugin.",
        "longDescription": (
            "A public-safe Codex plugin bundle containing run-project and its companion skills for "
            "project grilling, PRDs, specs, context layers, issues, writing plans, handoffs, "
            "architecture review, and acceptance checks."
        ),
        "developerName": "Ankit Classic Vision",
        "category": "Productivity",
        "capabilities": ["Project planning", "Implementation planning", "Review and handoff"],
        "defaultPrompt": [
            "Use run-project to plan this build from prompt to acceptance.",
            "Grill this project idea, then produce a PRD and issues.",
            "Create a handoff packet for this project.",
        ],
        "brandColor": "#2563EB",
    },
}

MARKETPLACE_JSON = {
    "name": "ankit-shared-skills",
    "interface": {
        "displayName": "Ankit Shared Skills",
    },
    "plugins": [
        {
            "name": PLUGIN_NAME,
            "source": {
                "source": "local",
                "path": f"./plugins/{PLUGIN_NAME}",
            },
            "policy": {
                "installation": "AVAILABLE",
                "authentication": "ON_INSTALL",
            },
            "category": "Productivity",
        }
    ],
}

PLUGIN_README = """# Run Project Bundle Plugin

This is a public-safe Codex plugin wrapper for the shared `run-project` skill stack.

## What it includes

The plugin copies the public skill bundle under `skills/` so the plugin is self-contained:

{skills_list}

## Install from a local clone

From a clone of this repo:

```bash
codex plugin marketplace add .
codex plugin add run-project-bundle@ankit-shared-skills
```

Start a new Codex thread after installing so the plugin skills are loaded into the next session.

## Public-safety rule

Do not add private names, internal system names, local machine paths, emails, phone numbers, credentials, client data, patient data, or account identifiers to this plugin.
"""


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    missing = [name for name in SKILL_NAMES if not (REPO / name / "SKILL.md").is_file()]
    if missing:
        raise SystemExit(f"Missing source skill folders: {', '.join(missing)}")

    if PLUGIN_ROOT.exists():
        shutil.rmtree(PLUGIN_ROOT)
    (PLUGIN_ROOT / ".codex-plugin").mkdir(parents=True, exist_ok=True)
    SKILLS_ROOT.mkdir(parents=True, exist_ok=True)

    for name in SKILL_NAMES:
        shutil.copytree(REPO / name, SKILLS_ROOT / name)

    write_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json", PLUGIN_JSON)
    write_json(MARKETPLACE_PATH, MARKETPLACE_JSON)

    skills_list = "\n".join(f"- `{name}`" for name in SKILL_NAMES)
    (PLUGIN_ROOT / "README.md").write_text(
        PLUGIN_README.format(skills_list=skills_list),
        encoding="utf-8",
    )

    print(f"rebuilt {PLUGIN_ROOT.relative_to(REPO)} with {len(SKILL_NAMES)} skills")
    print(f"wrote {MARKETPLACE_PATH.relative_to(REPO)}")


if __name__ == "__main__":
    main()
