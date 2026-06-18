---
name: run-project-bundle-viewer
display_name: Run Project Bundle Viewer
viewer_summary: Build a static Brain Viewer dashboard from run-project bundle skill metadata.
description: Build and refresh a static dashboard for the public run-project skill bundle by reading SKILL.md frontmatter, validating viewer metadata, and writing docs/run-project-bundle-dashboard.html plus docs/run-project-bundle-data.json. Use when a user asks to visualize the shared skills repo, make a Brain Viewer dashboard, inspect workflow lanes, or verify run-project bundle metadata.
bundle: run-project
phase: shape
category: visualize
artifact_type: html-dashboard
primary_command: /run-project-bundle-viewer
triggers:
  - run project dashboard
  - Brain Viewer dashboard
  - visualize shared skills
  - render skill bundle
inputs:
  - Clone of the shared skills repository
  - SKILL.md files with viewer-friendly YAML frontmatter
  - Optional output directory
outputs:
  - docs/run-project-bundle-dashboard.html
  - docs/run-project-bundle-data.json
  - Metadata validation summary
dependencies:
  before:
    - codebase-organizer
  after:
    - seeit
risk_level: low
side_effects: can-write-files
requires_repo: true
requires_network: false
---

# Run Project Bundle Viewer

## One-line Pitch

Turn the shared skills repository into a static dashboard that Brain Viewer, docs sites, or an agent can open without custom backend code.

## When To Use

Use this skill when the user asks to:

- visualize the Run Project Bundle or `ankit_shared_skills` repository;
- make skill cards, phase lanes, filters, or dependency graphs from `SKILL.md` files;
- validate whether bundle skills have the viewer-friendly metadata recipe fields;
- refresh the generated dashboard after editing skill frontmatter.

## Do Not Use For

- Running the `/run-project` delivery pipeline itself.
- Editing private skills or non-public skill repositories unless explicitly scoped.
- Publishing, deploying, pushing, or merging the dashboard without separate approval.

## Inputs

- Repository root containing one folder per skill and a `SKILL.md` inside each folder.
- Viewer metadata in each skill frontmatter: `display_name`, `viewer_summary`, `bundle`, `phase`, `category`, `artifact_type`, `primary_command`, `triggers`, `inputs`, `outputs`, `dependencies`, `risk_level`, `side_effects`, `requires_repo`, and `requires_network`.
- Optional output path. Default: `docs/` under the repository root.

## Outputs

- `docs/run-project-bundle-data.json` — normalized metadata for Brain Viewer and other renderers.
- `docs/run-project-bundle-dashboard.html` — a self-contained static dashboard with search, filters, phase lanes, risk chips, inputs/outputs, and a dependency graph.
- Console validation summary listing missing fields or vocabulary warnings.

## Workflow

1. Work from the repository root.
2. Make sure each public bundle skill has viewer-friendly frontmatter using the recommended vocabulary:
   - `phase`: `sense`, `shape`, `spec`, `execute`, or `transfer`.
   - `category`: `conductor`, `interrogate`, `sensemaking`, `triage`, `visualize`, `repo`, `spec`, `plan`, `agent-safety`, or `transfer`.
   - `side_effects`: `none`, `draft-only`, or `can-write-files`.
3. Run the dashboard builder:

   ```bash
   python3 scripts/build-run-project-bundle-dashboard.py --strict
   ```

   Equivalent direct invocation:

   ```bash
   python3 run-project-bundle-viewer/scripts/build_dashboard.py --repo . --out-dir docs --strict
   ```

4. Open `docs/run-project-bundle-dashboard.html` in a browser and verify the lanes, cards, and graph render.
5. If plugin packaging is part of the change, run:

   ```bash
   python3 scripts/sync-run-project-plugin.py
   ```

6. Re-run the dashboard builder after syncing if the skill set changed.

## Output Format

The JSON artifact uses this shape:

```json
{
  "summary": {"bundle": "run-project", "skill_count": 17},
  "phases": [{"name": "sense", "label": "Sense"}],
  "skills": [
    {
      "name": "agent-spec-writer",
      "display_name": "Agent Spec Writer",
      "phase": "spec",
      "category": "spec",
      "primary_command": "/agent-spec-writer",
      "dependencies": {"before": ["grill-me"], "after": ["writing-plans"]}
    }
  ],
  "edges": [{"from": "grill-me", "to": "agent-spec-writer"}]
}
```

## Guardrails

- Keep the repo public-safe. Do not add private names, emails, phone numbers, account identifiers, credentials, client data, patient data, internal URLs, or local machine paths.
- The builder is file-writing only. It may create or overwrite dashboard artifacts under the selected output directory; it must not publish or deploy them.
- Preserve closed YAML frontmatter before any markdown examples using `---`.
- Prefer explicit arrays in YAML over prose lists so downstream renderers do not need brittle parsing.

## Self-Verification

Before reporting completion, verify:

- [ ] `python3 scripts/build-run-project-bundle-dashboard.py --strict` exits 0.
- [ ] `docs/run-project-bundle-dashboard.html` exists and is non-empty.
- [ ] `docs/run-project-bundle-data.json` exists and includes every intended bundle skill.
- [ ] A browser can load the HTML without JavaScript console errors.
- [ ] `git diff` contains no secrets, private identifiers, or local filesystem paths.
