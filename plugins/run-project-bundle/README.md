# Run Project Bundle Plugin

This is a public-safe Codex plugin wrapper for the shared `run-project` skill stack.

## What it includes

The plugin copies the public skill bundle under `skills/` so the plugin is self-contained:

- `make-it-make-sense`
- `scout`
- `aac-process-design`
- `agent-spec-writer`
- `agenttwin`
- `to-prd`
- `to-issues`
- `improve-codebase-architecture`
- `handoff`
- `grill-me`
- `codebase-organizer`
- `context-layer-generator`
- `run-project`
- `seeit`
- `skillify`
- `writing-plans`

## Install from a local clone

From a clone of this repo:

```bash
codex plugin marketplace add .
codex plugin add run-project-bundle@ankit-shared-skills
```

Start a new Codex thread after installing so the plugin skills are loaded into the next session.

## Public-safety rule

Do not add private names, internal system names, local machine paths, emails, phone numbers, credentials, client data, patient data, or account identifiers to this plugin.
