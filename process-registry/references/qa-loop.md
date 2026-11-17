# Blind QA and the bounce loop

Contents: what blind means, access model, where output lives, the gate stub, writing criteria, golden sets and proving a gate, fix notes, the loop, the cap, changing criteria, what lint can and cannot catch.

## What blind means

The maker gets instructions and a definition of done. It does not get the criteria, the thresholds or the golden set.

Think of an exam. The syllabus is public: `deliverable.md` tells the maker what good looks like. The answer key is private: `qa.md` and `golden/` say how that is checked.

The point is to keep the maker aimed at the outcome. A maker that can see the test optimizes for the test, and the gate stops telling you anything.

## Access model

A rule that says "do not read the qa folder" is not blind. Any agent that can read a repo can read everything in it, and agents do read around.

Blindness comes from access:

- Criteria live in a second repo.
- Read access to that repo belongs only to the QA agent's own OS user or machine, plus the steward who writes criteria.
- Maker agents run under a different user or on a different machine, without that key.

If makers and the QA agent share one user on one box, the maker can read the test. Say this plainly to the owner. The structure is still worth building, but until the split exists the blindness is an honor system.

Knowing that a QA repo exists, and where, is not a leak. Reading it is.

## Where output lives

The maker and the grader need one place they can both reach that is not the QA repo. Pick one and write it into `AGENTS.md` as the run folder root:

| Option | Fits when |
|---|---|
| A shared directory | Both agents are on one machine or share a mount |
| A separate runs repo | Agents are on different machines; also gives a history of runs |
| Attachments on the task record | Deliverables are small and the board holds files |

## The gate stub

`NN.1-qa/GATE.md` in the main registry makes the gate visible in the folder order. It says what is graded, who grades, where the verdict goes and what happens on pass or fix.

It never says what the checks are. Lint rejects any other file in a gate folder and warns when the stub grows long.

The QA agent's routing is one rule: criteria live at the same path in the QA registry. There is no route table to maintain.

One QA agent serves every gate. "Separate" means separate from the maker, not one QA agent per process. The criteria folder is what specializes the grader, and each grading run loads only that folder.

## Writing criteria (qa.md)

Start from the outcome in `deliverable.md` and ask: how would a careful reviewer know it was met?

**Scripted checks first.** File exists, schema matches, counts reconcile with the source, links resolve, totals add up. They are cheap, exact and repeatable. Put code for them beside `qa.md`.

**Judgment checks second.** For each one, write what passes and what fails. "Tone is appropriate" grades differently every time. "No sentence blames the patient; fails if any does" grades the same way twice.

**Say how checks combine.** By default all must pass. If some are advisory, mark them.

**List sources a fix note may cite.** These are things the maker can also see: the source data, the request, `deliverable.md`.

A check that cannot be explained to the maker without revealing an expected answer is a sign that `deliverable.md` is missing an outcome. Fix the deliverable, not the note.

## Golden sets and proving a gate

`golden/` holds examples. Name them so their role is obvious:

- `golden/good-<case>/` is a deliverable known to be right.
- `golden/bad-<case>/` is one known to be wrong, with a `why.md` that says what is wrong with it.

A gate is proven only when it passes every good example and fails every bad one. A gate that has never failed anything may be passing everything. Before a gate is used on real work, the QA agent runs it on the golden set. If a bad example passes, the criteria are too weak.

Lint requires at least one good and one bad example per gate before a runbook may claim `verified`.

- Use examples to calibrate judgment, not as an answer key to diff against, unless the deliverable truly has one right answer.
- Add a case whenever a bad deliverable slips through or a good one is wrongly failed. That is how the gate improves.
- Make bad examples realistic: the mistakes a maker would actually make, not obvious garbage.
- Keep real personal data out. Use made-up or de-identified cases.

## Fix notes

```
QA REVIEW: FIX 1/3
Gate: 01.1-qa  Run: 2026-11-16-a
Fix:
1. [table, row "Dana"] closed count does not match the board. Evidence: board export, Dana, column Closed.
2. [header] report date is yesterday's. Evidence: run.yaml start time.
Keep (verified correct, do not change):
- Member list and ordering
- Column layout
```

Rules:

- **Cite the source, never the test.** Point at evidence the maker can see. Do not quote thresholds, rubric wording, check names or values taken from the golden set.
- **Be specific enough to act on.** Where it is, what is wrong, what shows it. A vague note causes another bounce.
- **Always include Keep.** It stops the maker from breaking good parts while fixing bad ones.
- **Grade it, do not fix it.** The grader never edits the deliverable.

A pass is short:

```
QA REVIEW: PASS
Gate: 01.1-qa  Run: 2026-11-16-a
process@4f2c1ab  qa@9d0e7c3
```

## The loop

1. Maker writes to `output/`, marks the task for review and passes it to the QA agent.
2. QA agent reads the criteria, then `output/` only. No working notes, no maker chat.
3. Verdict goes to `<run folder>/<gate>/verdict-N.md` and onto the task record.
4. Pass: the stage is complete. Stages that need it may start.
5. Fix: the task returns to the maker with the note.
6. On resubmit the whole deliverable is graded again.

## The cap

`bounce_cap` (default 3) limits fix rounds. "Until fixed" with no cap lets two agents trade the same note forever.

At the cap the QA agent does not send the work back. It marks the task blocked and hands it to the registry steward with every verdict and a line on which Fix items kept returning.

This goes to the steward, not straight to the owner. Three fails on the same items usually mean the instructions are unclear or the deliverable spec is wrong. The steward repairs the process through a normal change. It reaches a human only when a real decision is needed.

## Changing criteria

- Criteria change by pull request to the QA registry, written by the steward.
- The maker of a stage never writes or edits its test. With the access split in place this is enforced, not just promised.
- Never loosen a check to let a deliverable through. If the check is wrong, change it on purpose, on its own.
- A change that touches a stage and its criteria together deserves a human look, because that is the one move that can quietly lower the bar. Lint flags it when run with `--against` and `--against-qa`.

## What lint can and cannot catch

| Threat | Caught by |
|---|---|
| Criteria or a golden folder saved in the main registry | Lint, by file and folder name |
| A criteria sentence copied into any file in the main registry | Lint, by matching text (with `--qa`) |
| A golden file copied in under another name | Lint, by content hash (with `--qa`) |
| A symlink from the main registry to anywhere outside it | Lint |
| Criteria reworded and pasted in | Nothing automatic. A reviewer has to see it |
| Criteria put in a pull request, a task card or a chat a maker reads | Nothing automatic. The author must not do it |
| A maker reading the QA repo directly | Repo access. This is the real protection |
| A grader that passes everything | The known-bad examples |
| A gate, a human yes or a status quietly weakened | Lint with `--against`, then a person |

Lint narrows the ways to leak by accident. It does not make the main registry safe against someone trying. That is why the access split matters more than any check here.
