---
name: caliber
description: Route prompts by task-demand surface before spending tokens. Use when deciding which model, tool lane, verifier, or human gate a task needs; when a task involves local/private models, small/cheap models, coding, agents, long context, media, compliance, or high-stakes verification.
license: MIT
metadata:
  version: 0.3.0-public
---

# CALIBER

CALIBER is a model-routing skill. It turns a request into a **task-surface demand
vector**, compares that vector against a **model capability matrix**, and returns
the cheapest constructor that can clear the task with the right defender.

A constructor is:

```text
model + deployment path + context + retrieval + tools + verifier + human gate
```

## Core rule

Do not ask “what is the best model?” Ask:

> What is the cheapest allowed constructor whose proven capabilities clear this
> task's required surfaces and whose defender can verify the result?

## Demand levels

| Level | Name | Meaning |
|---:|---|---|
| -1 | deterministic | No model; use SQL/rules/regex/script/API directly. |
| 0 | tiny | Simple classify/extract/rewrite/routing. |
| 1 | small | Simple reasoning, short summaries, low-stakes drafts. |
| 2 | workhorse | Normal professional work, routine code/specs, common RAG. |
| 3 | strong specialist | Harder domain work, repo work, complex synthesis, multimodal reasoning. |
| 4 | frontier | Expensive-to-fail planning, novel architecture, high-reliability synthesis. |
| 5 | orchestrated frontier | Decomposition + tools + defenders + human gates. |
| 6 | reserved future | Future super-frontier/research-grade tier. |

## Workflow

1. Gate the deployment pool: regulated/private data, local-only requirements,
   secrets, production writes, or external sends may restrict allowed models.
2. Break the task into surfaces such as reasoning, coding, long context, tool use,
   media, structured output, local/private, or compliance.
3. Assign required level per surface.
4. Filter candidate models/deployments from `references/model-capability-matrix.yaml`.
5. Attach defenders from `references/defender-registry.md`.
6. Pick the cheapest viable constructor.
7. If the defender fails, escalate one tier or switch specialist lane.

## Output shape

```text
Task surfaces:
- <surface>: required level <n> — <why>

Gate pool:
- allowed deployments:
- excluded deployments:

Candidate comparison:
- cheapest viable:
- strongest reliable:
- local/private option:
- specialist option:

Defenders:
- required verifier(s):
- human gate:

Recommendation:
- primary constructor:
- fallback constructor:
- escalation rule:
- evidence confidence:
```

## References

- `references/surface-taxonomy.md`
- `references/model-capability-matrix.yaml`
- `references/model-capability-schema.json`
- `references/benchmark-source-ledger.md`
- `references/defender-registry.md`
- `references/routing-policy-v0.3.md`
- `references/model-registry.md`
- `references/demand-card.md`
