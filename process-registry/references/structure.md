# Structure reference

Contents: repos, root files, runbook folder, naming, process.yaml, status ladder, shared skills, run folders, versioning.

## Repos

| Repo | Holds | Who reads it |
|---|---|---|
| registry | Process definitions | Everyone: makers, orchestrators, QA, steward |
| registry-qa | Criteria and golden sets | QA agent and steward only |
| run folders (not a definition repo) | Output and verdicts of each run | Makers write their own stage; QA reads output |

The two definition repos use the same paths, so the main registry never needs a pointer into the test.

## Root files of the registry

| File | Job | Keep it |
|---|---|---|
| `CLAUDE.md` | One line that says to read `AGENTS.md` | One line |
| `AGENTS.md` | How to use, route, run, hand off to QA, change | The only rule file |
| `ROUTE.md` | A table: "Use when" to runbook | Routing only, no process detail |
| `GRAPH.md` | Generated Mermaid map | Never edited by hand |

`CLAUDE.md` exists because some harnesses load that name first. `AGENTS.md` is the name most others load. Keeping all rules in one of them avoids two rule files that drift.

Each file describes only its own level. A runbook's detail lives in the runbook, never copied up into `ROUTE.md` or `AGENTS.md`.

## Runbook folder

```
runbooks/<id>/
  SKILL.md          required. Frontmatter name (= folder name) and description. Outcome, stage map.
  process.yaml      required. Governance and stage order.
  NN-name/          a stage
    STAGE.md        required. Purpose, Inputs table, Process, Output, Uses.
    deliverable.md  required. Definition of done for the maker.
    references/     optional. Stable material this stage reads.
    scripts/        optional. Code this stage runs.
  NN.1-qa/          a gate for stage NN
    GATE.md         required, and the only file allowed here.
  adapters/         optional. One file per harness for quirks: adapters/<harness>.md
```

In the QA registry:

```
runbooks/<id>/NN.1-qa/
  qa.md             criteria
  golden/
    good-<case>/    a deliverable known to be right
    bad-<case>/     one known to be wrong, with why.md
```

## Naming

| Thing | Pattern | Example |
|---|---|---|
| Runbook id | lowercase, digits, hyphens, max 64 | `champions-leaderboard` |
| Stage | two digits, optional letter, hyphen, name | `01-collect`, `02a-build-table` |
| Gate | the stage's number and letter, then `.1-qa` | `01.1-qa`, `02a.1-qa` |

- The number is the step. Steps run in number order.
- A letter marks stages that share a step and may run side by side.
- A gate folder sorts directly after its stage, so the folder listing reads as the process.

## process.yaml

```yaml
id: champions-leaderboard      # must equal the folder name
owner: registry-steward        # a real role or person
version: 0.1.0
status: draft                  # draft | adopted | verified | portable | retired
human_gate: undecided          # [] | [stage ids] | undecided
source: ""                     # adopted only: where it lives today
runs_on: []                    # harnesses it has passed its gates on
requires: []                   # tools, logins, connections a run needs
depends_on: []                 # skills/<id> or runbooks/<id>
bounce_cap: 3                  # fix rounds before escalation
stages:
  - id: 01-collect
    needs: []
    gate: true
  - id: 02a-build-table
    needs: [01-collect]
    gate: false
```

Rules lint enforces:

- All keys above are present. There is no `description` key; the description lives in `SKILL.md` only.
- Every stage has `needs` (a list, `[]` for none) and `gate` (true or false).
- `needs` only names stages with a lower number.
- `gate: true` exactly when the `NN.1-qa` folder exists.
- `human_gate` is a list of valid stage ids, `[]`, or `undecided`.
- `depends_on` entries exist in the registry.
- No key is written twice. Plain YAML silently keeps the last one, which would let a second `human_gate:` line override the first.

`requires` is where harness-neutral requirements go. Steps port between harnesses. Logins and tool connections do not, so name them here and let each harness satisfy them its own way.

## Status ladder

| Status | Means | Lint requires |
|---|---|---|
| `draft` | Being written | Shape is valid. TODOs and `undecided` are warnings |
| `adopted` | An existing process captured as it runs today, not yet tested | `source` should be set |
| `verified` | Every gate has passed on one harness | One entry in `runs_on`, no TODOs, criteria present, `human_gate` decided, a good and a bad golden example per gate |
| `portable` | The same definition has passed on two or more harnesses | Two entries in `runs_on` |
| `retired` | No longer run | Row removed from `ROUTE.md` |

Promotion is a claim about evidence. Only promote when the task record shows the passing verdicts. Lint can check that the fields are filled; it cannot check that the run happened. With `--against`, every promotion is flagged so a person confirms the evidence.

## Tools

| Tool | Does |
|---|---|
| `scaffold.py` | `init`, `runbook`, `adopt`, `gate`. Never overwrites a file |
| `lint.py` | Checks shape, order, leaks and status. `--against` flags changes that lower the bar |
| `graph.py` | Writes `GRAPH.md` from every `process.yaml` |
| `sync.py` | Links runbooks and shared skills into a harness skills folder |
| `compare.py` | Compares how several agents built the same runbook |
| `selftest.py` | Attacks throwaway registries to prove the tools hold. Skill only, not copied into the repo |

## Shared skills

`skills/<id>/SKILL.md` follows the open Agent Skills format: frontmatter with `name` (equal to the folder name) and `description`, then instructions, with optional `scripts/`, `references/` and `assets/`.

A stage names what it uses under "Uses" in `STAGE.md`. The runbook lists the same in `depends_on`. That list is what `tools/graph.py` draws, and it is how you find every runbook a shared skill change could break.

## Run folders

```
<runs root>/<runbook-id>/<run-id>/
  run.yaml               registry commit, start time, harness
  01-collect/output/     the deliverable
  01.1-qa/verdict-1.md   first verdict; verdict-2.md after a resubmit
  02a-build-table/output/
```

- `output/` is the only handoff channel. The next stage and the grader read it and nothing else.
- The count of fix verdicts for a gate is the bounce count.
- The runs root must be somewhere both the maker and the QA agent can reach. See `qa-loop.md`.

## Versioning

Git is the version control. Every receipt stamps `process@<commit>` and, for gated stages, `qa@<commit>`, so any run can be traced to the exact instructions and the exact test.

`version` in `process.yaml` is for people: patch for wording, minor for a change in steps or deliverable, major for a change in stage structure.
