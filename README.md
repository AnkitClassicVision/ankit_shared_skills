# Shared AI Skills

A small public collection of portable AI skills.

## Skills

- `make-it-make-sense/` — a self-contained sense-making protocol for turning messy ideas, plans, documents, or decisions into clear artifacts with visible routing, trust markers, and safe capture behavior.
- `scout/` — a generic triage protocol for deciding whether a new idea, link, tool, repo, framework, or opportunity deserves GO-now, PARK, or KILL.
- `aac-process-design/` — guide AI workflow/process design with gates, owners, risks, and evaluation checkpoints.
- `agent-spec-writer/` — turn product intent into agent-ready behavioral specs with Given/When/Then boundaries.
- `agenttwin/` — produce public-safe agent evaluation packets and readiness reviews without exposing private rubrics.
- `to-prd/` — turn understood context into a PRD artifact for an issue tracker.
- `to-issues/` — break PRDs/specs into vertical-slice implementation issues.
- `improve-codebase-architecture/` — surface deep-module refactoring opportunities and architecture reports.
- `handoff/` — compact current project state into a redacted continuation packet for another agent or session.
- `grill-me/` — run the dependency-first interrogation phase before writing a PRD or implementation plan.
- `codebase-organizer/` — analyze a repository, map modules, detect coupling/orphans, and feed brownfield context into `run-project`.
- `context-layer-generator/` — build structural, semantic, and philosophical context layers for a repo or project.
- `run-project/` — orchestrate a full spec-backed project pipeline from grill to PRD, spec, context, issues, plans, execution, and acceptance.
- `seeit/` — create lightweight visual maps and review artifacts for project understanding.
- `skillify/` — turn a repository into a reusable agent-readable skill pack and project manifest.
- `writing-plans/` — convert specs and issues into small, execution-ready implementation tasks.

## Install or use

### Use as a native skill

Copy a skill folder into your AI tool's skills directory, then ask the tool to use the skill by name.

### Install the full run-project bundle

For `/run-project`, copy every folder in this repository into the target skills directory, not just `run-project/`. The conductor expects its companion skills to be installed alongside it. The bundle includes the planning, PRD, issue, context, SEEIT, handoff, codebase organizer, and acceptance-review skills. The only non-bundled dependency is the user's execution runtime: a coding agent, shell/test runner, or human operator.

### Install as a Codex plugin

This repo also includes a repo-local Codex marketplace and a self-contained plugin copy of the bundle:

```bash
git clone https://github.com/AnkitClassicVision/ankit_shared_skills.git
cd ankit_shared_skills
codex plugin marketplace add .
codex plugin add run-project-bundle@ankit-shared-skills
```

Start a new Codex thread after installing so the plugin skills are loaded into the next session.

Plugin files live at:

- `.agents/plugins/marketplace.json`
- `plugins/run-project-bundle/`

### Use as a standalone prompt

Open the skill's `SKILL.md`, paste it into an AI assistant, and add:

```text
Use this skill on the material below.
[material]
```

## Public-safety rule

This repo is intended to be public. Do not add private names, internal system names, local machine paths, emails, phone numbers, credentials, client data, patient data, or account identifiers.

Before publishing updates, scan changed files for:

- personal names
- emails and phone numbers
- local home-directory paths or machine-specific filesystem paths
- private org or client names
- API keys, tokens, and secrets
- internal URLs and private domains
- raw transcripts or records from private conversations

## License

MIT. See `LICENSE`.
