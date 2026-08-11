---
name: make-it-make-sense
description: Use when the user asks to "make sense," "make sense of this," "make it make sense," "this doesn't make sense," or otherwise requests structured comprehension of a confusing idea, decision, plan, document, system, unfamiliar domain, or stuck situation. Produces a visible router, a declared artifact shape, trust-marked claims, filtered insights, and a forward PATH when work remains. Do not use for rhetorical acknowledgments such as "makes sense" or "does that make sense?", simple factual questions, retrieval-only lookups, or routine editing, summarizing, and formatting that require no judgment.
---

# Make It Make Sense v3.7

Turn messy context into one coherent comprehension artifact and, when work remains, one aligned forward plan.

This skill is standalone. It does not require a particular memory product, agent runtime, or integration.

## Search current context

At the start of an activated response:

1. Search the user's available memory or knowledge system for `make-sense-protocol` and topics named in the request.
2. Prefer the highest version number, newest decision date, or explicit `supersedes` statement.
3. If the top result has a version number, search once more to confirm that no newer version exists.
4. Search relevant shape, judgment, and insight-calibration records when they exist.
5. If no memory or knowledge system is available, use this file without failing.

Treat retrieved context as evidence, not unquestioned truth. Do not reveal private records, secrets, credentials, or sensitive identifiers.

## Trigger rule

Activate on direct sense-making requests such as:

- "make sense"
- "make sense of this"
- "make it make sense"
- "this doesn't make sense"
- "help me make sense of this"

Do not activate on:

- "makes sense" as an acknowledgment
- "does that make sense?" as a check on the assistant's prior answer
- simple factual questions
- retrieval-only lookups
- routine editing, summarizing, or formatting with no judgment

If intent is ambiguous, ask exactly one question before the router:

> Are you asking me to make sense of something specific, or checking whether my last answer was clear?

## Core definitions

### Mode

- `Decision`: choose between options or commit to a path.
- `Comprehension`: understand a topic, system, document, or unfamiliar domain.
- `Unblock`: identify the next action when stuck.
- `Gate-building`: turn human judgment into a repeatable rule, rubric, or process.
- `Brainstorm`: generate possibilities with structure and constraints.
- `Clarification`: resolve one ambiguity before deeper work.

### Thinking brought

- `yes`: the user supplied a plan, assumptions, options, draft logic, or proposed approach.
- `no`: the user supplied raw material or confusion without a proposed approach.

When thinking was brought, inspect it before adding new reasoning.

### Shape

- `matrix`: comparisons, gaps, mappings, dependencies, tradeoffs, and traceability
- `river`: concepts and causal flow in a new domain or complex system
- `unblock`: one next action or a two-option choice
- `gate`: repeatable judgment, readiness, escalation, or automation boundary
- `custom`: only when the default shapes do not fit; name it

### Durable artifact

Treat an output as durable when the user may want to find or reuse it more than two weeks later.

Durable examples include a decision with reasoning, framework, specification, matrix, gate definition, evidence-backed recommendation, or confirmed reusable insight.

Clarifications, definitions, retrieval-only answers, and casual replies are not durable.

## Visible Router

The router is the first block of every activated response. Do not place an ELI5, preface, summary, or recommendation before it.

Use this exact structure:

```text
Routing:
 • Mode: [Decision | Comprehension | Unblock | Gate-building | Brainstorm | Clarification]
 • Thinking brought: [yes - N items | no]
 • Shape: [matrix | river | unblock | gate | custom: name it]
 • Pillars firing: [PLAN / SHAPE / TRUST / INSIGHT / PATH / Compound Capture, marking each fire or skip]
 • Why each skip: [one line per skipped pillar or ritual]
```

If the mode cannot be determined, ask the one disambiguating question first. Produce the router after the user answers.

## Pillar 1: PLAN

Fire PLAN when the user:

- proposes an approach;
- names two or more options; or
- requests help with strategic or architectural thinking.

Tag each important part of the user's thinking:

- `✓ solid`: likely correct or useful, with named support
- `? unclear`: needs definition or evidence
- `✗ shaky`: likely wrong, risky, or unsupported
- `⊘ blind spot`: an important missing consideration

Challenge the shakiest item. If one missing fact would materially change the artifact, ask exactly one clarifying question before producing the artifact. Proceed without asking when an explicit, trust-marked assumption is sufficient.

Skip PLAN when the user brought no thinking to validate. State the skip in the router.

## Pillar 2: SHAPE

Declare the shape in the router before writing the artifact.

### Matrix

Use for mapping, gaps, integration, comparisons, dependencies, or decisions. Prefer a traceability table with:

- what is being compared or mapped;
- trust-marked rows and cells;
- the largest gap or contradiction; and
- the recommendation or next move.

### River

Use for comprehension or a new domain. Include:

1. an ELI5 explanation in one to three plain sentences;
2. a one-line plain-English model;
3. a Mermaid `graph LR` when supported, otherwise a nested bullet flow; and
4. a concept table with `Quick definition`, `Why`, `Relates`, `Deep dive`, `Example`, and `ELI5`.

### Unblock

Use when action matters more than explanation. Include:

1. what is stuck;
2. one next action or an A/B choice;
3. why that move is justified;
4. what not to do yet; and
5. what result would change the recommendation.

### Gate

Use when replacing or supporting human judgment with a repeatable process. Follow:

1. `LOCATE`: identify the decision point.
2. `MINE`: collect examples and existing rules.
3. `DECOMPOSE`: separate signals, weights, conflicts, and missing inputs.
4. `GROUND`: connect each signal to named evidence.
5. `CODIFY`: write the decision rule and escalation boundary.
6. `VALIDATE`: test normal cases, edge cases, disagreements, and failures.

### Custom

Use a custom shape only when the four defaults fail. Name the shape and explain that choice with a trust marker.

## Pillar 3: TRUST

Mark every meaningful claim, table row, table cell, and recommendation:

- `✓ verified`: supported by a named source, user-provided fact, direct observation, or tool output
- `? inferred`: a reasonable conclusion not directly proven
- `✗ guessed`: speculation that must not drive action
- `⊘ unknown`: missing or unchecked; state what would resolve it

Name the source whenever using `✓ verified`.

Examples:

```text
- ✓ user-provided: Three owners were proposed.
- ? inferred: Ownership is the bottleneck because all three options route final decisions to one person.
- ⊘ unknown: No completion target was supplied. A numbered success condition would resolve this.
```

Never leave a meaningful cell unmarked. Empty information is `⊘ unknown`, not blank and not zero.

## Pillar 4: INSIGHT

Surface an insight only when it passes all three filters:

1. `HUH`: Would the user plausibly say, "I had not thought of that"?
2. `ACTION`: Would it change what the user does in the next 24 hours?
3. `SCOPE`: Would it apply to multiple future sessions on different topics?

Before surfacing an insight, check available insight-calibration records for prior hits and misses.

- All three pass: add `Insight` and propose capturing it as a reusable insight.
- HUH and ACTION pass, but SCOPE fails: add `Operational note`; do not propose reusable insight capture.
- Any other result: write `Insight: no insight to flag.`

Do not manufacture insight to make the response sound clever.

## Pillar 5: PATH

Fire PATH when the artifact ends with work still to do. Skip PATH for pure comprehension, retrieval, or clarification with no forward work.

PATH folds ATLAS concept structure and Judge verdicts into the same response. An ATLAS node is a claim under TRUST and a decision subject under Judge. The PATH state carries both confidence and progress. Its proof slot supplies the evidence that can change a verdict.

### SPINE

Write one falsifiable line stating what changes and what counts as won.

```text
SPINE: [who or what changes] so that [observable outcome]; won when [numbered binary condition].
```

If the work requires two unrelated ladders, rewrite the SPINE. One SPINE supports one ladder.

### One ladder, one rung equals one goal

Render the ladder as a table.

- One rung must deliver one user-visible goal.
- Fold scaffolding that delivers no goal into the next rung.
- Split a goal that spans two rungs into two goals.
- Do not create parallel unaligned task lists.
- If one ladder cannot hold the plan, the SPINE is wrong.

### Six required fields

Every rung contains:

| Field | Required content |
|---|---|
| GOAL | What changes for the user, in the user's language rather than the system's |
| DONE | The binary completion condition, with a number |
| TEST | The exact executable command |
| RED | The poisoned input or condition that makes the test fail |
| STATE | `✓ proven`, `~ building`, `✗ broken`, or `⊘ unknown` |
| WHO | `GO`, `HOLD`, `ASK`, or `GATE`, plus the owner |

Use one state vocabulary:

- `✓ proven`: evidence has passed the stated TEST and RED check
- `~ building`: work is underway but is not proven
- `✗ broken`: the stated test currently fails
- `⊘ unknown`: the test has not run or the value is unmeasured

Do not use separate confidence, status, and trust fields inside PATH. Unmeasured is `⊘ unknown` and is never assumed zero.

Use one verdict vocabulary:

- `GO`: the agent may act now; maps to Judge `allow`
- `HOLD`: blocked on a named condition; maps to Judge `block`
- `ASK`: the human must decide before work continues; maps to Judge `escalate`
- `GATE`: an external effect requires human approval at the moment of action; maps to Judge `escalate-at-action`

Approval for `GATE` happens when the external action is ready, not in advance.

### RED is mandatory

Every acceptance test must include a poisoned input or failure condition that has been observed to fail. A check that has never been watched fail is not a check.

For a machine-tested rung, provide:

1. the exact success command in TEST;
2. the exact poisoned input or setup in RED; and
3. the failure signal, such as a nonzero exit, rejected fixture, or named assertion.

Do not mark the rung `✓ proven` until both the success path passes and the poisoned path produces the expected failure.

For a human gate with no machine test, write exactly:

```text
TEST: None - human gate
RED: None - human gate
```

Do not invent a machine test for a judgment only a human can make.

### Worked PATH ladder

```text
SPINE: The user can produce a complete weekly report without sending an incomplete one; won when 10 required fields pass validation and a fixture missing 1 required field is rejected.
```

| Rung | GOAL | DONE | TEST | RED | STATE | WHO |
|---|---|---|---|---|---|---|
| 1 | ? proposed: The user can detect an incomplete report before review. | ? proposed: 10 of 10 required fields pass and 1 missing-field fixture is rejected. | ? proposed command: `python scripts/check_report.py examples/report-complete.md` exits 0. | ? proposed poison: `python scripts/check_report.py examples/report-missing-owner.md` must exit nonzero and name `owner`. | `⊘ unknown`: neither command has run. | ? proposed: `GO`, agent runs both commands. |
| 2 | ? proposed: The user can approve one complete report for external delivery. | ? proposed: 1 report receives an explicit approve or reject decision. | `None - human gate` | `None - human gate` | `⊘ unknown`: approval has not occurred. | ? proposed: `GATE`, user approves at the moment of delivery. |

The example remains `⊘ unknown` because illustrative commands are not evidence that the commands ran.

### Decision blocks

Write every open decision in this exact order:

1. `WHAT IT MEANS`: explain the question's vocabulary in two or three plain sentences. Assume the vocabulary may be the missing context.
2. `RECOMMEND`: state the choice directly.
3. `JUDGE`: name the judge that fired (`Router`, `Recall`, `Proposal`, `Gate`, `Release`, or `Learning`) and its verdict.
4. `WHY`: cite named data, measurements, sources, or file and line evidence. Never use preference alone.
5. `IF WRONG`: state the concrete cost if the recommendation is wrong.

Never place a recommendation before `WHAT IT MEANS`.

### PLAN THIS NEXT

When a rung is too large or uncertain to specify honestly:

1. write `PLAN THIS NEXT`;
2. state that the rung is not yet specifiable; and
3. name the single question whose answer would size it.

Do not fake a detailed plan for work that is not visible.

## Output order

For every activated response:

1. Visible Router, first.
2. PLAN check, when activated.
3. Artifact in the declared SHAPE, with TRUST markers.
4. PATH, when activated: SPINE, one ladder table, decision blocks, and PLAN THIS NEXT when needed.
5. Insight, Operational note, or `Insight: no insight to flag.`
6. Compound Capture ritual, last, when the artifact is durable.

Do not add a next-action menu after the capture ritual.

## Manual shape overrides

When the user says `matrix`, `river`, `unblock`, or `gate`, switch to that shape immediately.

The router still comes first. TRUST and INSIGHT still apply. PLAN fires when the user brought thinking. PATH still fires when forward work remains. Compound Capture still depends on durability.

## Compound Capture ritual

Run this ritual whenever the response produces a durable artifact. It is mandatory and must be the final output:

```text
Capture this to your memory or knowledge system? Yes or no.
Any insight from this session that hit? Any that missed?
```

Do not replace the ritual with a next-action menu, an offer to continue, or a different capture question. Wait for the user's answer before saving or proposing further actions.

Skip the ritual only when:

- the response produced no durable artifact;
- the user explicitly said to skip the capture ritual;
- the response was retrieval-only with no analysis; or
- the user ended the session.

Never save before the user answers yes. Sanitize approved captures. Do not save secrets, credentials, private identifiers, sensitive records, or unnecessary personal data.

## Style

- Use no em dashes.
- Do not use stock corporate filler; prefer direct verbs.
- Prefer specific numbers over vague quantities.
- Prefer tables when they make relationships faster to read.
- Challenge weak reasoning instead of flattering it.
- Keep every line behavior-changing; remove padding.

## Public-safety check

Before publishing or sharing an artifact produced with this skill, scan it for:

- private person names;
- emails and phone numbers;
- absolute home paths and machine-specific filesystem paths;
- private company, client, project, or memory-product names;
- API keys, tokens, secrets, and credentials;
- internal URLs or private domains;
- raw transcripts, private records, and sensitive identifiers; and
- setup-specific integrations that do not exist for other users.

Replace private details with generic terms such as `the user`, `memory or knowledge system`, `source document`, `private repository`, or `internal tool`.
