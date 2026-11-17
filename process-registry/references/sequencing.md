# Order, parallel work and human yes points

## The rule

`process.yaml` decides order. Two definitions do all the work:

- A stage is **ready** when every stage in its `needs` list is complete.
- A stage is **complete** when its output is handed in and its gate, if it has one, has passed.

So "go to step 2 after step 1 is complete" means after step 1 has passed QA. A stage that is finished but still failing its gate holds everything that needs it.

Whoever orchestrates the run, a lead agent or a person, starts every ready stage.

## Sequential by default

Each step needs the step before it:

```yaml
stages:
  - id: 01-collect
    needs: []
    gate: true
  - id: 02-build
    needs: [01-collect]
    gate: true
  - id: 03-send
    needs: [02-build]
    gate: false
```

Here `02-build` carries the gate, because what it builds is about to be sent. `03-send` has none: a check after the send cannot stop a bad one.

Write each stage as three lines, as above. The scaffolder writes this layout and its `gate` command edits it.

## Side by side

Stages that share a number run at the same time. In the scaffolder, a pipe makes them:

`--stages "collect, build-table | draft-email, assemble, send"`

```yaml
stages:
  - id: 01-collect
    needs: []
    gate: true
  - id: 02a-build-table
    needs: [01-collect]
    gate: false
  - id: 02b-draft-email
    needs: [01-collect]
    gate: false
  - id: 03-assemble
    needs: [02a-build-table, 02b-draft-email]
    gate: true
  - id: 04-send
    needs: [03-assemble]
    gate: false
```

A stage is safe to run side by side with another when all of these hold:

- Neither reads the other's output.
- Each writes only to its own `output/` folder.
- Neither changes something outside the run that the other relies on, such as the same record in an outside system.

If any of these fails, they are not parallel. Put one after the other.

Each side-by-side stage is its own job with its own task record. That keeps receipts, gates and rework separate.

## Fan-in

A stage with several needs waits for all of them. `03-assemble` above starts only when both `02a` and `02b` are complete. If either had a gate, complete would include passing it.

One branch failing its gate does not cancel the other. The sibling finishes and waits. If the failing branch hits its bounce cap, the run stops at the fan-in until the steward resolves it.

## Skipping ahead

A stage may need any earlier step, not just the one before it. `needs` may only point at lower numbers, so folder order always equals a valid run order and a cycle cannot be written. Lint enforces this.

Do not use `needs` for "nice to have" context. If a stage reads another stage's output, it needs it. If it does not, it does not.

## Human yes points

`human_gate` lists stages that wait for a named person to say yes before they start. The orchestrator opens a request on the task record, with what is being approved and the evidence, and starts the stage only after the answer.

- `human_gate: []` means the owner decided no stage needs a human yes.
- `human_gate: [04-send]` means stage 04 waits.
- `human_gate: undecided` means nobody has decided. It is a warning while the runbook is a draft and an error once it claims `verified`.

There are no blanket rules about which kinds of work need a human. The owner decides per process. The author's job is to ask, record the answer, and never fill it in on a guess.

A human yes is different from a QA gate. QA checks that the deliverable is right. The human yes is permission to take the next action. When both apply, the gate comes first, so the person approves something that has already been checked.

## When this shape is not enough

Folders and `needs` handle straight lines, side-by-side branches and joins. They do not express loops over unknown-length lists, long waits for outside events, or branching on run-time conditions.

Often those are better handled inside one stage: a stage whose process says "for each item" is still one stage with one deliverable. If a process truly needs engine-style control flow, say so to the owner and treat adding a workflow definition as its own decision.
