---
name: grill-me
description: Relentlessly interview the user to stress-test a plan, design, docs, or existing codebase before building. Use when the user says "grill me", "grill docs", "grill with docs", wants codebase/domain alignment, wants a CONTEXT.md or ADR-backed interrogation, or needs shared language before implementation.
---

# Grill Me

Grill the user before building. Reach shared understanding, expose contradictions, and leave durable docs or code pointers that reduce future re-explanation.

## Operating loop

1. Start by finding available grounding:
   - User-provided docs, PRDs, specs, tickets, diagrams, transcripts.
   - Existing codebase files, tests, schema/migrations, README, and package scripts.
   - Domain docs such as `CONTEXT.md`, `UBIQUITOUS_LANGUAGE.md`, `docs/`, `architecture/`, `adr/`, or `decisions/`.
2. If a question can be answered from docs or code, inspect those artifacts instead of asking.
3. Ask one question at a time.
4. For each question:
   - State the tension or unknown.
   - Give the recommended answer first.
   - Offer 2-4 concrete options only when the choice is real.
   - Name what code or docs evidence supports or contradicts the recommendation.
5. Walk dependency-first: resolve upstream concepts, relationships, ownership, lifecycle, state, permissions, failure modes, data contracts, and naming before implementation details.
6. Keep grilling until the next build step is unambiguous or the remaining blockers require human product judgment.

## Docs-aware grilling

Before or during the interview, look for a bounded-context document:

- Prefer `CONTEXT.md` if present.
- If absent, use the smallest relevant existing doc set and propose creating or updating `CONTEXT.md` when shared language emerges.
- In monorepos, identify the bounded context first. Do not force a single global glossary if contexts use different language.

During grilling:

- Challenge fuzzy terms against existing glossary/docs.
- Surface terminology collisions, such as one term being used for two concepts or two terms for one concept.
- Ground terms in code: types, schemas, route names, migrations, component names, test names, and folder boundaries.
- Convert verbose phrasing into precise domain language.
- Use concrete scenarios and edge cases to test each term.
- Capture unresolved terms as open questions, not fake definitions.

## Codebase grilling checklist

Investigate only enough code to ask sharper questions:

- Entity relationships and cardinality.
- State/status semantics and whether status is stored, derived, manual, or event-driven.
- Lifecycle transitions, deletion/archive behavior, permissions, and ownership.
- Existing naming conventions and likely file/module boundaries.
- Tests and migrations that reveal intended behavior.
- Integration boundaries and backward-compatibility constraints.

## Durable output

When the user asks to save or update docs, or when a durable decision emerges, propose or make scoped doc edits:

- `CONTEXT.md`: shared language, term definitions, relationships, invariants, examples.
- `docs/adr/YYYY-MM-DD-short-title.md` or `docs/decisions/...`: non-obvious decisions.
- Existing README/spec docs: only when that is the repo convention.

Create an ADR only when the decision is hard to reverse, surprising without context, or involves a real trade-off with downstream consequences.

Doc updates should include:

- Terms and definitions.
- Relationships/cardinality.
- Examples and non-examples.
- Invariants and constraints.
- Open questions.

Do not document every preference. Keep docs thin and useful.

## Answer style

- One question per turn.
- Be challenging but useful.
- Prefer "recommended answer: X, because Y" over neutral brainstorming.
- If code/docs already answer it, say "I found this in `<path>`" and do not ask.
- If evidence conflicts, stop and ask about the conflict.
- Do not build until the design tree is resolved or the user explicitly overrides the grilling phase.
