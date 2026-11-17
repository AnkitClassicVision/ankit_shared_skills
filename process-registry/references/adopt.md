# Adopting existing processes

The goal is to get what already runs into the registry without breaking it and without a rewrite project.

## Wrap, do not rewrite

```bash
python scripts/scaffold.py adopt --registry <registry> --qa <registry-qa> \
  --id recall-reminders \
  --description "What it does today. Use when ..." \
  --source "where it lives today: script path, skill name, schedule, bot"
```

This creates a one-stage runbook with `status: adopted`, the `source` recorded, no gate, and `human_gate: undecided`. Pass `--stages` if the process already has clear steps.

Then:

1. **Write the steps as they run today** in `STAGE.md`. Do not improve them. An adoption that changes behavior hides the change inside a move, and nobody can tell which one broke things.
2. **Move existing code untouched** into the stage's `scripts/` folder, or leave it in place and point to it from `source` and the Inputs table.
3. **Write `deliverable.md` from what the process produces now.** Describe the real output, not the output you wish it had.
4. **Put harness quirks in `adapters/<harness>.md`.** Anything true for only one harness, such as a required label or a login step, goes there. The core steps stay neutral.
5. **List `requires`.** Tools, logins and connections the run depends on.
6. **Ask the owner about `human_gate`.** Leave it `undecided` if they have not said.
7. **Lint.** Adopted runbooks pass with warnings.

## What counts as an existing process

| It lives as | Bring it in by |
|---|---|
| A skill file in one harness | Moving the instructions into `STAGE.md`. If several runbooks will reuse it, make it a shared skill under `skills/` instead |
| A script on a schedule | Recording the schedule in `SKILL.md` under "Start a run" and the script under `scripts/` |
| A standing card or pinned instructions on a board | Copying the instructions into the runbook and replacing the card body with a pointer to it |
| A bot workflow inside a vendor tool | Writing down the steps and the trigger. Note in `adapters/` what only that tool can do |
| Something a person does from memory | Interviewing them. This is a new runbook, not an adoption |

## Adopt on touch

Do not migrate everything at once. A big-bang move stalls, and half-moved processes are worse than unmoved ones.

- Seed the registry with the few processes that run most often.
- After that, a process is adopted the next time it runs or changes.
- Anything not yet adopted keeps running where it is.

## Climbing the ladder

| Step | What it takes |
|---|---|
| `adopted` to `verified` | Add gates where deliverables cross a boundary, write criteria, pass them on one harness, decide `human_gate` |
| `verified` to `portable` | Run the same definition on a second harness and pass the same gates. Fix whatever was secretly tied to the first harness by moving it to `adapters/` or `requires` |

Each step is a normal versioned change. Splitting a one-stage adoption into real stages is a major version bump.

## Common traps

- **Hidden state.** The old process relied on a file, a login session or a memory that the new stage cannot see. List it in `requires` or the Inputs table.
- **Two sources of truth.** After adoption, the old location must point to the registry or be removed. Otherwise edits keep landing in the old place.
- **Improving on the way in.** Tempting, and it removes your ability to compare before and after.
