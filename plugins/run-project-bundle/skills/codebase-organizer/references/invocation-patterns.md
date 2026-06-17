# Detailed Invocation Patterns

## `/deepen` Slash Command

### Full Pipeline (default)
```
/deepen <repo-path> [--output-dir <dir>]
```
Runs all 7 phases. Human gates pause at Grill and Shape.

### Quick Scan Mode
```
/deepen --scan-only <repo-path>
```
Phase 1 only. Returns ranked JSON. No human gates.

### Resume Mode
```
/deepen --resume <session-id>
```
Reads prior session state from `--output-dir`. Continues from last completed phase.

### Dry Run
```
/deepen --dry-run <repo-path>
```
Runs all phases but no file modifications. Useful for estimating scope.

## Cron Scheduling

Weekly maintenance scan:
```bash
hermes cron create "0 9 * * 1" \
  --name "weekly-deepen-scan" \
  --prompt "/deepen --scan-only ~/projects/myapp" \
  --output-dir ~/.agent/deepen-snapshots/myapp
```

## Multi-Agent Orchestration

The skill internally delegates to other skills:

| Phase | Delegation Target | Key Params |
|-------|-------------------|------------|
| 1 (Discover) | `gemini` | `--skip-trust`, read-only preamble |
| 4 (Spec) | `agent-spec-writer` | behavioral context from Shape |
| 5 (Context) | `context-layer-generator` | repo path + spec output |
| 6 (Implement) | `claude-code` | `--allowedTools`, git worktree |
| 7 (Verify) | `seeit` | before/after repo snapshots |

## Output Directory Structure

```
<output-dir>/
├── session-<id>/
│   ├── 01-discover/
│   │   ├── candidates.json          # raw Gemini output
│   │   └── ranked-candidates.json   # scored + sorted
│   ├── 02-grill/
│   │   └── decision.md              # human decision record
│   ├── 03-shape/
│   │   └── interface-contract.md    # proposed API
│   ├── 04-spec/
│   │   └── behavioral-spec.md       # agent-spec-writer output
│   ├── 05-context/
│   │   ├── structural-layer.md
│   │   ├── semantic-layer.md
│   │   └── philosophical-layer.md
│   ├── 06-implement/
│   │   ├── diff.patch               # proposed changes
│   │   └── test-results.json
│   └── 07-verify/
│       └── seeit-visualization.html
```
