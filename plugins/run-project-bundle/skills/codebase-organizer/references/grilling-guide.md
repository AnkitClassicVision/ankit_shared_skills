# Grilling Guide: How to Evaluate Deepening Candidates

The Grill gate is the most important superpower. AI can find candidates. Only you can decide which battles are worth fighting.

## Grilling Questions (ask these for every candidate)

### Leverage Assessment
1. If this module were deepened, how many other modules would benefit?
2. Is this a bottleneck that slows down feature development?
3. Would simplifying this module make onboarding new developers faster?

### Risk Assessment
4. What's the blast radius if the refactor introduces a bug?
5. Do we have adequate test coverage for the current behavior?
6. Are there known dark corners or undocumented edge cases?

### Timing Assessment
7. Is this module actively being changed, or is it stable?
8. Are there upcoming features that would make this refactor easier or harder?
9. What's the opportunity cost — what else could we do with this time?

## Decision Matrix

| Leverage | Risk | Decision |
|----------|------|----------|
| High | Low | **DEEPEN** — obvious win |
| High | High | **SHAPE carefully** — invest in test harness first |
| Low | Low | **DEFER** — do it when convenient |
| Low | High | **REJECT** — not worth the risk |

## Common Grilling Pitfalls

| Pitfall | Why It Happens | How to Avoid |
|---------|---------------|-------------|
| Choosing the newest code | Recent work is fresh in memory | Ask: "what's the oldest code that new devs struggle with?" |
| Choosing the most annoying code | Frustration bias | Ask: "would fixing this actually make future work faster?" |
| Choosing the biggest file | Size != leverage | Ask: "if I split this file, what changes?" |
| Avoiding the scariest code | Fear of unknown | That's often exactly where the leverage is — test first |

## Success Criteria Template

Before approving a candidate, define:

- **Metric**: How will we measure success? (e.g., reduce public API surface by 50%)
- **Timebox**: Maximum time to invest before reassessing
- **Blast radius**: Which systems could break if we're wrong
- **Rollback plan**: How to revert if the refactor fails
- **Test requirement**: Minimum test coverage before starting changes
