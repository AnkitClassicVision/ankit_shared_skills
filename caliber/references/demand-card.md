# CALIBER — Deep Demand Card

**Pull this only when the fast-path in SKILL.md was ambiguous, or when you want a
full auditable profile of a prompt (e.g. designing an automation, or explaining a
routing call to a human).** For everyday routing, the gate + 3-read fast-path is
the whole job — running this on trivial traffic is the router-overhead trap.

This is the full 12-signal read from the v2 rubric. It feeds two scoring paths,
both grounded in a number (see **Scoring** below):

- **Agent path (in-context, default):** the plain integer grounding score from
  SKILL.md — Load `L` (sum of the six band reads) and Peak `P` (the highest read).
  An agent can reproduce it. This is what routes live traffic.
- **Software path (deterministic):** if a *program* computes the score, use the
  full weighted `Q` + structural `S` + penalty math below — it's fine when code
  runs it identically every time. Never run this math in an agent's head; that's
  the false-precision trap.

## The 12 signals (score 0–5, from judgment)

Grouped by what they *do* to the route.

### Gate signals — these force a capability, not a bigger model

| # | Signal | 0 | 3 | 5 | Fires → |
|---|---|---|---|---|---|
| 1 | **Specification load** | exact output given | some ambiguity | vague/subjective objective | clarify or state assumptions first (G1) |
| 4 | **Evidence availability** | fully in prompt | several sources needed | missing/proprietary/unreachable | retrieve / ask for data / mark partial (G2) |
| 5 | **Evidence recency/conflict** | stable facts | current matters | fast-changing/disputed | live web + citations (G2) |
| 10 | **Tool/action burden** | none | search/file/code | multi-step agentic | tool-enabled surface / specialist lane (G3) |
| 11 | **Verification burden** | obvious | needs citations/tests | needs expert/formal proof | THROUGHLINE / Codex / expert (G4) |

### Band signals — these set the caliber via the grounding score (Load + Peak; see Scoring)

| # | Signal | 0 | 3 | 5 |
|---|---|---|---|---|
| 6 | **Reasoning depth** | direct transform | multi-step | long dependent / proof-like chain |
| 3 | **Knowledge rarity** | common | professional/domain | expert/frontier |
| 7 | **Context coupling** | none | several docs/entities | long-context / cross-ref / multimodal / codebase |
| 8 | **Constraint interaction** | none | a few tradeoffs | many conflicting tradeoffs |
| 9 | **Novelty** | standard task | custom synthesis | new framework / invention / open problem |
| 2 | **Output construction** | one line | structured memo/table | full artifact / model / SOP / codebase |

### The risk multiplier — read always, applied on top

| # | Signal | 0 | 3 | 5 | Effect |
|---|---|---|---|---|---|
| 12 | **Stakes/tolerance** | no consequence | business/customer impact | legal/medical/financial/irreversible | raises band + reliability threshold; at 4–5 forces verify pass + human gate. **Only raises, never lowers.** |

## Scoring — two paths

### Agent path (default, in-context)

From the six **band signals** only (stakes stays separate):

- **Load `L`** = sum of the six band reads (0–30).
- **Peak `P`** = the single highest band read (0–5).
- **Band:** `P`≤1 → 0–1 · `P`=2 → 1 · `P`=3 → 2 · `P`=4 → 3 · `P`=5 → 4; then `L`≥18 → **+1 band** (cap at >4 = decompose).
- **Stakes** (signal 12), applied on top: business/customer → +1 band; legal/medical/financial/irreversible → +1 band + verify pass + human gate.
- **Gate signals** (1, 4, 5, 10, 11) don't touch the score — they force a capability (clarify, retrieve, tool lane, verifier). A failed gate is not a bigger model.

Record it: `L=<n>, P=<n> → band <n>` plus any stakes/gate bumps. That line is the audit trail.

### Software path (deterministic — only if code computes it)

If a program scores prompts (not an agent in-context), the full v2 math is safe
because it runs identically every time. Integer-weight variant to avoid decimal drift:

```text
Q = Σ(weight_i × rating_i)          # weights: novelty 4; reasoning 4; verification 4;
                                    # evidence-availability 3; context-coupling 3; stakes 3;
                                    # knowledge 3; constraint 3; recency 2; spec 2;
                                    # output 2; tool 2   (integer weights, no 1.5 multiplier)
S = round(3.5 × log2(1 + N + E + 2H + 2C + 3K + 3A + 4M))   # structural composition
Final score = Q + S + Σ(penalties)
```

Structural counts (`N` entities, `E` dependency edges, `H` longest serial chain,
`C` hard constraints, `K` sources, `A` tool steps, `M` modalities) and the penalty
table come from the v2 rubric. **This block is for a code router only.** In an
agent, use the Agent path above — the log and the edge-counting are exactly what
an LLM can't reproduce turn to turn. Map the software score to bands by calibrating
cutoffs on real traffic, not by reusing the v2 0–240 ranges blind.

## Atomic-transformation lens (fast band prior)

A prompt is a *composition* of atomic moves. This gives a quick prior before the
full read:

| Move | Base caliber | Example |
|---|---|---|
| Restyle | 0 | rewrite this email |
| Extract | 0 | pull dates from this contract |
| Classify | 0–1 | sort leads by quality |
| Retrieve | 1–2 | find current vendor pricing |
| Compare | 1–2 | compare three CRMs |
| Integrate | 3 | synthesize 10 sources |
| Infer | 3 | diagnose why conversion dropped |
| Optimize | 3 | build a staffing model |
| Construct | 4 | new SOP / app spec / framework |
| Verify | varies | check claims / run tests |
| Act | 3+ (+stakes) | send email / update calendar / deploy |
| Discover | >4 | invent theory / prove new result |

`Prompt = Extract + Restyle` → band 0. `Prompt = Retrieve + Integrate + Infer +
Construct + Verify` → band 4 + gates. Read the composition, then confirm with the
band signals above.

## Worksheet (for a full auditable profile)

| Field | Value |
|---|---|
| Task transformation (input → output) | |
| Constraints | |
| Required verifier | |
| Reliability threshold (use case) | |
| **Gate 0 — regulated/private data?** | |
| G1 spec / G2 info / G3 tool / G4 verify — which fired | |
| Impossibility type (logical/info/operational/verification/none) | |
| Band signals (6/3/7/8/9/2) | |
| **Grounding score: Load `L` (sum) / Peak `P` (highest)** | |
| Stakes (12) → +band / verify / human gate | |
| **Caliber band (0–>4)** | |
| Specialist lanes triggered | |
| **Verdict: constructor + tools + verify pass + human gate?** | |
| Decompose first (ATLAS)? | |
| What would *reduce* the caliber | |
| Main reason it's hard (or: not hard — underspecified/missing-data/risky) | |

## Reusable scoring prompt (for scoring other prompts in bulk)

> You are CALIBER, a task-demand router. Treat the prompt as a transformation
> `T = <input → output | constraints, resources, verifier, tolerance>` and return
> the cheapest constructor that performs it reliably.
> 1. **Gate 0:** regulated/private data present? If yes, restrict pool to approved compliant/private
>    endpoints; non-compliant models are off the table.
> 2. **Fast-path:** trivial transform → band 0, cheapest. Known-hard build → band
>    4, decompose + verify. Else continue.
> 3. **Gates:** G1 spec defined? G2 evidence reachable? G3 tools needed? G4
>    checkable? Each fired gate adds a capability, not a bigger model.
> 4. **Score + band:** score the six band reads (reasoning depth, knowledge rarity,
>    context coupling, constraint interaction, novelty, output construction) 0–5.
>    Load `L` = their sum; Peak `P` = the highest. Band: `P`≤1→0–1, 2→1, 3→2, 4→3,
>    5→4; then `L`≥18 → +1 (cap >4 = decompose). Integer sums only, no weights/logs.
> 5. **Stakes:** +1 band + threshold if business/regulated/irreversible.
> 6. **Verdict:** band → model (per registry) + specialist lanes + verify pass +
>    human gate? Cascade from the band; don't pre-pay the top tier.
> Return: **model breakdown first** (Gate-0 pool, band 0/1–2/3/4/>4 ladder
> from `model-registry.md`, specialist lanes, recommended route +
> fallback) · transformation summary · Gate 0 result · gates fired · impossibility
> type · band reads · **grounding score `L=<n>, P=<n>`** · stakes effect · caliber
> band · verdict (constructor + lanes) · decompose? · what would reduce it · the
> real reason it's hard.
> Prompt to score: [INSERT]
