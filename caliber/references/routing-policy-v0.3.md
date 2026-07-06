# CALIBER v0.3 — Routing Policy

## Algorithm

1. **Normalize the request.** Rewrite it as an input → output transformation with
   constraints, tolerance for error, and side effects.
2. **Gate the pool.** Apply compliance, privacy, data residency, local-only,
   external-send, production-write, and human-impacting gates before scoring.
3. **Build task surface vector.** Assign required levels (-1 to 6) for every
   material surface in `surface-taxonomy.md`.
4. **Filter candidates.** Use `model-capability-matrix.yaml` to keep only models
   and deployments that meet the required surfaces and gates.
5. **Construct route.** A route is model + deployment + context + retrieval +
   tools + defender + human gate.
6. **Choose cheapest viable.** Prefer the lowest-cost candidate expected to pass
   the defender. Do not pre-pay frontier by default.
7. **Defend.** Run or name the required verifier. High-stakes routes require a
   defender even if the model is frontier.
8. **Escalate on failure.** If the defender fails, escalate one model tier, switch
   specialist lane, add retrieval/tools, or block for missing context/human review.
9. **Log misroutes.** Cheap-tier failures and frontier-overuse are signals to tune
   the matrix.

## Pool gates

| Gate | Restriction |
|---|---|
| regulated/private data | approved compliant/private deployment only. |
| Secrets/credentials | Do not send raw secrets; use secure references or local tools. |
| Local/private-only | Local/open-weight/private endpoint candidates only. |
| External send/write | Human approval unless explicitly authorized. |
| CRM/EHR/finance write | Dry-run + audit log + rollback + approval. |
| Public upload | Explicit approval required. |
| Human-impacting labels | Human gate unless pre-approved policy exists. |

## Candidate comparison fields

Every non-trivial answer should name:

- cheapest viable constructor
- strongest reliable constructor
- local/private option, if relevant
- long-context option, if relevant
- media/specialist option, if relevant
- excluded candidates and why
- required defender and escalation rule

## Legacy compatibility

For pure text tasks, old bands map to levels: 0 → tiny, 1–2 → workhorse, 3 →
strong specialist, 4 → frontier, >4 → orchestrated/decompose. Prefer the full
surface vector whenever the task touches code, tools, media, compliance, long
context, local models, or side effects.
