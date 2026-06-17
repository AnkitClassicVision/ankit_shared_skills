# /deepen Pipeline Reference — Annotated Agent Roles, Gates, and Metrics

Full reference for the 7-phase deepening pipeline absorbed from the former `codebase-deepen` skill into `codebase-organizer`.

## Agent Roles

| Agent | Role | Superpower | When |
|-------|------|------------|------|
| **Gemini** | Deep Scanner | 1M context analysis | Phase 1: Discover |
| **Hermes** | Orchestrator | Skill dispatch, grilling, context persistence | Phases 1-5 |
| **Claude Code** | Validator | Code review, test verification | Phase 1 validation |
| **Claude Code** | Implementer | Refactor execution | Phase 6 |
| **SEEIT** | Visualizer | Architecture mapping | Phase 7 |

## Human Gates

| Gate | Purpose | Decision |
|------|---------|----------|
| **Grill** | Strategic prioritization | Which modules to deepen |
| **Shape** | Interface design approval | What the boundary looks like |
| **Spec Review** | Behavioral contract | Does the spec capture intent? |
| **Merge** | Code integration | Approve the refactor PR |

## Invocation Patterns

### Full Pipeline
```
User: "/deepen ~/projects/myapp"
```
Runs all 7 phases with human gates at Grill and Shape.

### Quick Scan
```
User: "/deepen --scan-only ~/projects/myapp"
```
Phase 1 only. Returns ranked candidate list.

### Resume
```
User: "/deepen --resume <session-id>"
```
Continues from last human gate.

### Periodic Maintenance
```bash
hermes cron create "0 9 * * 1" \
  --prompt "/deepen --scan-only ~/projects/myapp"
```
Weekly scan for new deepening opportunities.

## Integration with Existing Skills

| Skill | Integration Point | How to Invoke |
|-------|-------------------|---------------|
| `repo-architect` | Phase 1: Module detection | Call its `detect_modules.py` |
| `agent-spec-writer` | Phase 4: Spec generation | Delegate with shaped context |
| `context-layer-generator` | Phase 5: Context layers | Delegate with spec + repo path |
| `seeit` | Phase 7: Visualization | Delegate with before/after repo state |
| `claude-code` | Phase 6: Implementation | Print-mode with `--allowedTools` |
| `codex` | Phase 6: Alternative implement | Use when Claude unavailable |
| `gemini` | Phase 1: Large context scan | `--skip-trust` for headless runs |

## Notes

- The organizer's `scripts/discover-rank.py` and `scripts/grill-presentation.py` are the canonical bridge utilities for Phase 1.
- The organizer's `references/grilling-guide.md` drives the human gate at Phase 2.
- The organizer's `references/interface-patterns.md` provides common patterns for Phase 3 (Shape).
