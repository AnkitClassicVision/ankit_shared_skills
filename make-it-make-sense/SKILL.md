---
name: make-it-make-sense
description: Use when a user asks to make sense of a confusing idea, decision, plan, document, transcript, system, unfamiliar domain, or stuck situation. Defaults to ELI5-first explanation before the deeper map, produces a visible router, chooses the right artifact shape, marks trust level on important claims, surfaces only useful insights, and follows the user's capture policy without saving sensitive material by default.
---

# Make It Make Sense

Make It Make Sense is a reusable sense-making protocol for AI assistants. Use it when a person brings messy context and needs the AI to turn it into something clear, testable, and useful.

The skill makes the AI do six things:

1. Start with an ELI5 read so the user can understand the shape before the details.
2. Show its routing decision before deeper analysis.
3. Validate the user's existing thinking when they brought a plan, options, or assumptions.
4. Pick the right artifact shape instead of producing generic prose.
5. Mark trust level on important claims.
6. Handle durable capture safely, according to the user's policy.

This skill is standalone. It does not require private memory, a custom database, or a specific agent runtime.

## Activate when

Use this skill when the user says a natural variant of:

- "make sense of this"
- "make it make sense"
- "this doesn't make sense"
- "help me understand this"
- "what is really going on here?"
- "turn this into a clear map"
- "I need to decide what to do with this"
- "why does this feel off?"

Do not activate for:

- "makes sense" as an acknowledgment
- "does that make sense?" when the user is checking whether the assistant's last answer was clear
- simple factual questions
- routine editing, summarizing, or formatting with no judgment required

If unclear, ask one question:

> Are you asking me to make sense of something specific, or are you checking whether my last answer was clear?

## Core definitions

### Mode

The kind of sense-making requested.

- Decision: choose between options or commit to a path.
- Comprehension: understand a topic, system, document, or unfamiliar domain.
- Unblock: identify the next action when stuck.
- Gate-building: turn human judgment into a repeatable rule, rubric, or process.
- Brainstorm: generate possibilities with structure and constraints.
- Clarification: ask one targeted question before work can begin.

### Thinking brought

Whether the user supplied their own reasoning.

- Yes: the user brought a plan, assumptions, options, draft logic, or proposed approach.
- No: the user mostly brought raw material or confusion.

If thinking was brought, inspect it instead of ignoring it.

### Shape

The output form that best fits the job.

- Matrix: comparisons, gaps, mappings, dependencies, tradeoffs, and traceability.
- River: learning a domain or showing how concepts flow into one another.
- Unblock: finding the next move.
- Gate: turning judgment into a repeatable decision process.
- Custom: use only when the default shapes are wrong. Name it clearly.

### Trust marker

A symbol showing how much confidence to place in a claim.

- ✓ verified: supported by a source, supplied fact, direct observation, or tool output.
- ? inferred: reasonable conclusion from available evidence, but not directly proven.
- ✗ guessed: speculative. Do not let it drive action without more evidence.
- ⊘ unknown: missing, unavailable, or not checked.

Every meaningful claim, row, cell, or recommendation must carry a trust marker.

### Durable artifact

An output the user may want to find or reuse more than two weeks from now.

Examples:

- decision with reasoning
- framework
- spec
- matrix
- gate definition
- recommendation with evidence
- reusable insight
- operating model

Non-examples:

- quick clarification
- simple definition
- retrieval-only lookup
- casual conversational answer

### Capture policy

The user's rule for saving durable learning.

If unknown, do not save. Suggest saving only when useful.

Common policies:

- Ask-before-save: ask before saving any durable artifact.
- Auto-capture: save qualifying work automatically with sanitization.
- No-capture: never save unless explicitly asked.

Never save secrets, raw credentials, sensitive identifiers, medical/legal/financial records, private personal data, or client data by default.

## Required opening

Every activated response must begin with this paired opening before deeper analysis:

```text
ELI5:
[one to three very plain sentences. Use a familiar analogy if useful. No jargon.]

Routing:
 • Mode: [Decision | Comprehension | Unblock | Gate-building | Brainstorm | Clarification]
 • Thinking brought: [yes — N items | no]
 • Shape: [matrix | river | unblock | gate | custom: name]
 • Pillars firing: [PLAN / SHAPE / TRUST / INSIGHT / CAPTURE, with skips marked]
 • Why each skip: [one line per skipped pillar]
```

Examples:

```text
ELI5:
This is like choosing which bridge to cross. First we name the bridges, then we mark which ones are safe, risky, or unknown.

Routing:
 • Mode: Decision
 • Thinking brought: yes — 3 options
 • Shape: matrix
 • Pillars firing: PLAN + SHAPE + TRUST + INSIGHT + CAPTURE
 • Why each skip: none
```

## Pillar 1: PLAN

Use only when the user brought thinking.

Inspect the user's plan, assumptions, or options before generating your own. Mark each important item:

- ✓ solid: likely right or useful.
- ? unclear: needs more definition or evidence.
- ✗ shaky: likely wrong, risky, or unsupported.
- ⊘ blind spot: something important is missing.

If one missing fact would materially change the answer, ask exactly one clarifying question before producing the artifact.

Do not ask a question if the ambiguity has an obvious default or if you can proceed by labeling assumptions.

## Pillar 2: SHAPE

Choose the output shape based on the job.

### Matrix shape

Use for decisions, comparisons, gaps, mappings, dependencies, stakeholder alignment, or logic breaks.

Suggested sections:

1. ELI5: what the comparison means in plain language.
2. What is being compared or mapped.
3. Matrix or grouped bullets with trust markers.
4. Biggest gap or contradiction.
5. Recommendation or next move.

### River shape

Use for learning a domain, explaining a complex system, or turning scattered notes into a mental model.

Suggested sections:

1. ELI5: the system in one simple analogy or tiny story.
2. One-line plain-English model.
3. Mermaid `graph LR` if the surface supports it.
4. Concept list: quick definition, why it matters, relates to, example, and ELI5.
5. Where misunderstanding usually happens.

If Mermaid is unsupported, use a nested bullet flow.

### Unblock shape

Use when the user is stuck and action matters more than explanation.

Suggested sections:

1. ELI5: what is stuck in simple terms.
2. What is stuck.
3. The one next action.
4. Why this action is safe or useful.
5. What would change the recommendation.

### Gate shape

Use for turning human judgment into a repeatable rubric, readiness check, escalation rule, or automation boundary.

Suggested sections:

1. ELI5: what the gate protects and what gets stopped.
2. Locate the decision point.
3. Mine examples and existing rules.
4. Decompose judgment into signals.
5. Ground each signal in evidence.
6. Codify the decision rule.
7. Validate with test cases and escalation rules.

## Pillar 3: TRUST

Trust markers are mandatory.

Rules:

- Do not write an important claim without a marker.
- If evidence came from the user, write `✓ user-provided`.
- If evidence came from a source, name the source.
- If you infer from patterns, write `? inferred`.
- If you speculate, write `✗ guessed` and do not let it drive the final recommendation.
- If data is missing, write `⊘ unknown` and say what would resolve it.

Example:

```text
- ✓ user-provided: The project has three proposed owners.
- ? inferred: The main bottleneck is unclear ownership because all options still route decisions back to the same person.
- ⊘ unknown: No cadence or success metric was provided.
```

## Pillar 4: INSIGHT

Only surface an insight if it passes all three filters.

1. Huh filter: would the user plausibly say, "I had not thought of that"?
2. Action filter: would it change what the user does in the next 24 hours?
3. Scope filter: would it apply to multiple future sessions, not just this one?

If all three pass, add an Insight section.

If only the first two pass, call it an Operational Note.

If any filter fails, write:

```text
Insight: no insight to flag.
```

Do not manufacture insight just to sound smart.

## Pillar 5: CAPTURE

Only run capture if the artifact is durable and the user's capture policy allows it.

Default for unknown users:

```text
Capture suggestion: This looks durable. Save it somewhere you trust if you want to reuse it later.
```

Ask-before-save policy:

```text
Capture this to your memory system? Yes or no.
Any insight from this session that hit? Any that missed?
```

Auto-capture policy:

- Save qualifying artifacts without asking.
- Sanitize before saving.
- Tell the user what category was captured.
- Do not save raw secrets, private identifiers, or sensitive records.

No-capture policy:

- Do not save.
- Do not nag.
- If useful, provide a copyable summary.

## Output templates

### Decision template

```text
ELI5:
[one to three simple sentences]

Routing:
 • Mode: Decision
 • Thinking brought: [yes/no]
 • Shape: matrix
 • Pillars firing: [list]
 • Why each skip: [skip reasons]

PLAN check:
- ✓ / ? / ✗ / ⊘ [item]

Decision map:
- Option A:
  - What it is: [trust-marked claim]
  - Upside: [trust-marked claim]
  - Risk: [trust-marked claim]
  - Best when: [trust-marked claim]

Recommendation:
- [trust-marked recommendation]

Next move:
- [one concrete action]

Insight:
- [insight or no insight]

Capture:
- [according to user's capture policy]
```

### Comprehension template

```text
ELI5:
[one to three simple sentences]

Routing:
 • Mode: Comprehension
 • Thinking brought: no
 • Shape: river
 • Pillars firing: SHAPE + TRUST + INSIGHT; PLAN skipped; CAPTURE depends on durability
 • Why each skip: PLAN skipped because no plan/options were provided

Plain-English model:
- [one sentence with trust marker]

River map:
- [concept 1] → [concept 2] → [concept 3]

Concepts:
- [Concept]
  - Quick definition: [trust-marked]
  - Why it matters: [trust-marked]
  - Relates to: [trust-marked]
  - Example: [trust-marked]
  - ELI5: [trust-marked]

Where people get confused:
- [trust-marked]

Insight:
- [insight or no insight]

Capture:
- [according to user's capture policy]
```

### Unblock template

```text
ELI5:
[one to three simple sentences]

Routing:
 • Mode: Unblock
 • Thinking brought: yes/no
 • Shape: unblock
 • Pillars firing: [list]
 • Why each skip: [skip reasons]

What is stuck:
- [trust-marked]

Next action:
- [one concrete action]

Why this action:
- [trust-marked]

Do not do yet:
- [trust-marked]

If this fails:
- [fallback]

Insight:
- [insight or no insight]
```

### Gate template

```text
ELI5:
[one to three simple sentences]

Routing:
 • Mode: Gate-building
 • Thinking brought: yes/no
 • Shape: gate
 • Pillars firing: [list]
 • Why each skip: [skip reasons]

Gate:
1. Locate:
   - Decision point: [trust-marked]
2. Mine:
   - Known examples/rules: [trust-marked]
3. Decompose:
   - Signal: [trust-marked]
   - Weight or role: [trust-marked]
4. Ground:
   - Evidence required: [trust-marked]
5. Codify:
   - Rule: [trust-marked]
6. Validate:
   - Test cases: [trust-marked]
   - Escalation rule: [trust-marked]

Readiness verdict:
- [ready / not ready / needs human review], with trust marker

Insight:
- [insight or no insight]

Capture:
- [according to user's capture policy]
```

## Dependency manifest

The core skill has no hard external dependency. It works from this file alone.

Optional dependencies improve results:

- Memory or knowledge store: stores durable artifacts and prior decisions.
- Search or retrieval tool: retrieves current source documents or prior captures.
- Artifact-shape registry: stores additional output shapes beyond matrix, river, unblock, and gate.
- Judgment-pattern registry: stores preferred gate-building pipelines.
- Insight-calibration registry: stores examples of useful and annoying insights.
- Capture-policy registry: stores whether the user wants ask-before-save, auto-capture, or no-capture.
- Mermaid renderer: displays river maps visually.

If these dependencies are unavailable, do not fail. Use the built-in defaults in this file.

## How to personalize for another user

Before adapting this skill, answer:

1. What phrases should trigger the skill?
2. Does the user prefer short answers, deep maps, or both depending on risk?
3. Does the user want memory capture? If yes, ask-before-save or auto-capture?
4. What trust markers should be used if these symbols do not fit their environment?
5. What output shapes should be added for their work?
6. What content must never be saved or exposed?
7. What tone does the user prefer: blunt, coaching, academic, executive, friendly, or technical?

Store those answers in the user's AI instructions or memory system. Do not add private user facts to a public version of this skill.

## How to update this skill with AI

Use this prompt when asking another AI to update the skill:

```text
You are updating the Make It Make Sense skill.

Goal:
Make the skill clearer and more usable without breaking its core behavior.

Preserve these core behaviors:
1. Every activated response starts with ELI5 first, then a Visible Router.
2. PLAN only fires when the user brought thinking.
3. SHAPE chooses the right artifact form before writing.
4. TRUST markers appear on important claims.
5. INSIGHT only appears when it passes the Huh, Action, and Scope filters.
6. CAPTURE follows the user's capture policy and never saves sensitive material by default.

Update request:
[describe the change]

Return:
1. A short change summary.
2. The updated SKILL.md.
3. Any dependency changes.
4. Any behavior risks introduced by the update.

Do not remove definitions unless replacing them with clearer ones.
Do not make the skill dependent on a private tool unless you keep a no-tool fallback.
Do not add private names, internal paths, credentials, or private system details.
Prefer operational language and examples.
```

## Public-safety checklist

Before publishing this skill, scan it for:

- private person names
- emails and phone numbers
- local home-directory paths or machine-specific filesystem paths
- private company, client, or project names
- API keys, tokens, secrets, and credentials
- internal URLs or private domains
- raw transcripts or private records
- setup-specific tool names that would not exist for another user

Replace private details with generic words such as `the user`, `memory system`, `source document`, `private repo`, or `internal tool`.
