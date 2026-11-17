# Mapping the loop onto a task board

The registry does not care which board records the work. It needs five things from one:

| Need | What the board must give |
|---|---|
| One record per job | A task per stage per run. Side-by-side stages get separate tasks |
| A way to hand off | Reassigning or re-queuing a task so the next agent picks it up |
| States | At least: to do, working, in review, done, blocked |
| A receipt trail | Comments or a log that keep verdicts and receipts in order |
| A way to ask a human | For `human_gate` stages and real decisions |

## The loop in board terms

1. The orchestrator creates one task per ready stage, naming the runbook, the stage and the run.
2. The maker claims it, works, posts a receipt and moves it to review.
3. If the stage has a gate, the task passes to the QA agent.
4. `QA REVIEW: PASS` closes the stage. `QA REVIEW: FIX n/cap` returns the task to the maker.
5. At the bounce cap the task is marked blocked and passed to the registry steward.
6. A `human_gate` stage gets a request to the named human first. The stage's task is created only after the yes.

Receipts carry the runbook id, the stage id, `process@<commit>`, and for gated stages `qa@<commit>`.

Keep criteria off the board. A maker reads its task. Verdicts follow the fix-note rules, so they are safe to post.

## Adapting an existing board

Use the board’s existing task format, permissions and human approval workflow. Map its states before creating a task. The following table shows one possible mapping.

| Registry | On the board |
|---|---|
| One job per stage | One issue per stage per run |
| Handing off | Assignment. Assigning to an agent starts its run, so finish the card body first, then assign |
| Stage is being worked | `in_progress` |
| Handed in, waiting for the gate | `in_review`, assigned to the QA agent |
| Gate passed | `done` |
| Bounce cap reached | `blocked`, assigned to the steward |
| Verdict comment | First line `QA REVIEW: PASS` or `QA REVIEW: FIX n/cap`, which fits the existing comment taxonomy |
| Human yes point | The human-action lifecycle from the board skill |

Points that are easy to get wrong:

- A comment's first line never starts with the approval words reserved for the human owner.
- The human-action label is for things only the human can do. A failing gate is not one of them. At the bounce cap the card goes to the steward, and reaches the human only if a real decision is left.
- Side-by-side stages are separate cards. Do not burst-assign many cards to one agent at once; space them out.
- The board can hold skills as well. Treat the registry as the source and the board's copy as a pointer to it. Never edit a process on the board.

## Other boards

The same mapping works on any board with assignment and comments. Write the board's name and any format rules into the "Record of work" line of `AGENTS.md`, and add a short `adapters/` note if a harness needs board-specific commands.
